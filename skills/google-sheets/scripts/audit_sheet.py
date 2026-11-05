#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# ///
"""Read-only Google Sheets snapshot, error scan, checks and before/after diff.

Uses gws credentials; performs only spreadsheets.get. --input accepts
an existing raw get response for offline inspection. Check JSON is a list of
{range: "'Tab'!A1:B2", expected: 0, absolute_tolerance: 1e-6} objects.
A scalar expected value applies to every cell; arrays must match the rectangle.
With --compare, only errors absent from the baseline fail the run.
"""

# Handle validation errors at the CLI boundary without extra wrapper functions
# ruff: noqa: TRY301

import argparse
import datetime as dt
import json
import math
import re
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

FIELDS = (
    "spreadsheetId,spreadsheetUrl,properties,namedRanges,"
    "sheets(properties,merges,conditionalFormats,basicFilter,filterViews,"
    "protectedRanges,bandedRanges,charts,rowGroups,columnGroups,slicers,tables,"
    "developerMetadata,data(startRow,startColumn,"
    "rowMetadata,columnMetadata,rowData(values(userEnteredValue,effectiveValue,"
    "formattedValue,userEnteredFormat,effectiveFormat,note,dataValidation,"
    "hyperlink,textFormatRuns))))"
)


def column_name(index: int) -> str:
    """Convert a zero-based column index to its A1 label."""
    result = ""
    while index >= 0:
        index, rem = divmod(index, 26)
        result = chr(65 + rem) + result
        index -= 1
    return result


def cell_name(title: str, row: int, col: int) -> str:
    """Return a quoted A1 reference for one cell."""
    return f"'{title.replace("'", "''")}'!{column_name(col)}{row + 1}"


def cells(book: dict[str, Any]) -> dict[tuple[int, int, int], dict[str, Any]]:
    """Index populated cells by sheet ID and absolute grid coordinates."""
    result = {}
    for sheet in book.get("sheets", []):
        sid = sheet["properties"]["sheetId"]
        for grid in sheet.get("data", []):
            for row, record in enumerate(
                grid.get("rowData", []), grid.get("startRow", 0)
            ):
                for col, cell in enumerate(
                    record.get("values", []), grid.get("startColumn", 0)
                ):
                    if cell:
                        result[(sid, row, col)] = cell
    return result


def canonical(book: dict[str, Any]) -> dict[str, Any]:
    """Compare cells by coordinates and tabs by stable sheet IDs."""
    result = {k: v for k, v in book.items() if k != "sheets"}
    result["sheets"] = {}
    for sheet in book.get("sheets", []):
        sid = str(sheet["properties"]["sheetId"])
        item = {k: v for k, v in sheet.items() if k != "data"}
        item["cells"] = {}
        item["rowMetadata"] = {}
        item["columnMetadata"] = {}
        for grid in sheet.get("data", []):
            for key, start in (
                ("rowMetadata", "startRow"),
                ("columnMetadata", "startColumn"),
            ):
                for i, value in enumerate(grid.get(key, []), grid.get(start, 0)):
                    if value:
                        item[key][str(i)] = value
        result["sheets"][sid] = item
    for (sid, row, col), value in cells(book).items():
        result["sheets"][str(sid)]["cells"][f"{column_name(col)}{row + 1}"] = value
    return result


def differences(
    before: object, after: object, path: str = ""
) -> Iterator[dict[str, Any]]:
    """Yield exact JSON differences, keeping list-valued metadata intact."""
    if isinstance(before, dict) and isinstance(after, dict):
        for key in sorted(before.keys() | after.keys()):
            at = f"{path}/{key}"
            if key not in before:
                yield {"path": at, "change": "added", "after": after[key]}
            elif key not in after:
                yield {"path": at, "change": "removed", "before": before[key]}
            else:
                yield from differences(before[key], after[key], at)
    elif before != after:
        yield {"path": path, "change": "changed", "before": before, "after": after}


def parse_range(value: str, book: dict[str, Any]) -> tuple[int, int, int, int, int]:
    """Resolve a bounded A1 check range to sheet ID and grid coordinates."""
    match = re.fullmatch(
        r"(?:'((?:[^']|'')+)'|([^'!]+))!([A-Z]+)([1-9][0-9]*)(?::([A-Z]+)([1-9][0-9]*))?",
        value,
    )
    if not match:
        raise ValueError(f"Use a bounded A1 rectangle with a sheet title: {value}")
    quoted, plain, left, top, right, bottom = match.groups()
    title = quoted.replace("''", "'") if quoted else plain
    sheets = [s for s in book["sheets"] if s["properties"]["title"] == title]
    if len(sheets) != 1:
        raise ValueError(f"Sheet not found: {title}")

    def col(text: str) -> int:
        n = 0
        for char in text:
            n = n * 26 + ord(char) - 64
        return n - 1

    r0, r1 = int(top) - 1, int(bottom or top)
    c0, c1 = col(left), col(right or left) + 1
    if r0 >= r1 or c0 >= c1:
        raise ValueError(f"Reversed rectangle: {value}")
    return sheets[0]["properties"]["sheetId"], r0, r1, c0, c1


def audit(book: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    """Scan effective errors and evaluate explicitly supplied cell checks."""
    grid = cells(book)
    titles = {
        s["properties"]["sheetId"]: s["properties"]["title"] for s in book["sheets"]
    }
    # Row and column metadata cover every fetched row and column, even empty ones
    fetched = [
        (
            sheet["properties"]["sheetId"],
            grid.get("startRow", 0),
            grid.get("startRow", 0) + len(grid.get("rowMetadata", [])),
            grid.get("startColumn", 0),
            grid.get("startColumn", 0) + len(grid.get("columnMetadata", [])),
        )
        for sheet in book["sheets"]
        for grid in sheet.get("data", [])
    ]
    errors, broken, results = [], [], []
    warning = "Contains #REF!; inspect for broken references or literal text"
    for (sid, row, col), cell in grid.items():
        at = cell_name(titles[sid], row, col)
        if "errorValue" in cell.get("effectiveValue", {}):
            errors.append({"cell": at, "error": cell["effectiveValue"]["errorValue"]})
        formula = cell.get("userEnteredValue", {}).get("formulaValue", "")
        if "#REF!" in formula + json.dumps(cell.get("dataValidation", {})):
            broken.append({"cell": at, "warning": warning})
    # Conditional-format rules are stored per sheet, not per cell
    for sheet in book["sheets"]:
        if "#REF!" in json.dumps(sheet.get("conditionalFormats", [])):
            title = sheet["properties"]["title"]
            broken.append(
                {"cell": f"'{title}' conditional formats", "warning": warning}
            )
    for check in checks:
        sid, r0, r1, c0, c1 = parse_range(check["range"], book)
        expected = check["expected"]
        if isinstance(expected, list) and (
            len(expected) != r1 - r0
            or any(not isinstance(row, list) or len(row) != c1 - c0 for row in expected)
        ):
            raise ValueError(f"Expected array shape differs from {check['range']}")
        tolerance = check.get("absolute_tolerance", 0)
        if (
            isinstance(tolerance, bool)
            or not isinstance(tolerance, (float, int))
            or not math.isfinite(tolerance)
            or tolerance < 0
        ):
            raise ValueError("Tolerance must be finite and nonnegative")
        failures = []
        for row in range(r0, r1):
            for col in range(c0, c1):
                want = (
                    expected[row - r0][col - c0]
                    if isinstance(expected, list)
                    else expected
                )
                effective = grid.get((sid, row, col), {}).get("effectiveValue", {})
                actual = next(
                    (
                        effective[key]
                        for key in ("numberValue", "stringValue", "boolValue")
                        if key in effective
                    ),
                    effective.get("errorValue"),
                )
                if want is None:
                    passed = not effective and any(
                        s == sid and top <= row < bottom and left <= col < right
                        for s, top, bottom, left, right in fetched
                    )
                elif type(want) in (float, int):
                    passed = (
                        isinstance(actual, (float, int))
                        and not isinstance(actual, bool)
                        and math.isfinite(actual)
                        and math.isfinite(want)
                        and abs(actual - want) <= tolerance
                    )
                else:
                    passed = (
                        actual is not None
                        and type(actual) is type(want)
                        and actual == want
                    )
                if not passed:
                    failures.append(
                        {
                            "cell": cell_name(titles[sid], row, col),
                            "expected": want,
                            "actual": actual,
                        }
                    )
        results.append(
            {"range": check["range"], "passed": not failures, "failures": failures}
        )
    return {"formula_errors": errors, "reference_warnings": broken, "checks": results}


def main() -> int:
    """Read the workbook and write a snapshot plus an optional audit report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spreadsheet_id")
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--compare")
    parser.add_argument("--checks")
    parser.add_argument("--report")
    parser.add_argument(
        "--range",
        action="append",
        dest="ranges",
        help="A1 range to read instead of every tab; repeatable",
    )
    parser.add_argument(
        "--input", help="Offline raw spreadsheets.get response; not a live-read verdict"
    )
    args = parser.parse_args()
    try:
        if args.input:
            book = json.loads(Path(args.input).read_text())
        else:
            response = subprocess.run(
                [
                    "gws",
                    "sheets",
                    "spreadsheets",
                    "get",
                    "--params",
                    json.dumps(
                        {
                            "spreadsheetId": args.spreadsheet_id,
                            "fields": FIELDS,
                            "includeGridData": True,
                        }
                        | ({"ranges": args.ranges} if args.ranges else {})
                    ),
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=600,
            )
            book = json.loads(response.stdout[response.stdout.index("{") :])
        if book.get("spreadsheetId") != args.spreadsheet_id:
            raise ValueError("Snapshot workbook ID differs from requested workbook")
        if not book.get("sheets"):
            raise ValueError("Response contains no sheets")
        snapshot = {
            "schema_version": 1,
            "read_at_utc": dt.datetime.now(dt.UTC).isoformat(),
            "live": not bool(args.input),
            "coverage": "offline input; coverage not verified"
            if args.input
            else f"ranges only: {', '.join(args.ranges)}"
            if args.ranges
            else "full grid fields requested",
            "workbook": book,
        }
        # Load the baseline first: the new snapshot may reuse its path
        before = json.loads(Path(args.compare).read_text()) if args.compare else None
        # Write before reading other inputs so a bad file does not waste the read
        Path(args.snapshot).write_text(json.dumps(snapshot, indent=2) + "\n")
        checks = json.loads(Path(args.checks).read_text()) if args.checks else []
        if not isinstance(checks, list):
            raise TypeError("Checks file must contain a JSON list")
        result = audit(book, checks)
        result["snapshot"] = {k: v for k, v in snapshot.items() if k != "workbook"}
        if before is not None:
            if (
                before.get("schema_version") != 1
                or before["workbook"].get("spreadsheetId") != args.spreadsheet_id
            ):
                raise ValueError("Comparison snapshot schema or workbook differs")
            result["changes"] = list(
                differences(canonical(before["workbook"]), canonical(book))
            )
            # Errors already in the baseline, such as intentional NA(), do not fail
            baseline = audit(before["workbook"], [])
            for key in ("formula_errors", "reference_warnings"):
                result[f"new_{key}"] = [
                    item for item in result[key] if item not in baseline[key]
                ]
        if args.report:
            Path(args.report).write_text(json.dumps(result, indent=2) + "\n")
        prefix = "new_" if args.compare else ""
        failed = bool(
            result[f"{prefix}formula_errors"]
            or result[f"{prefix}reference_warnings"]
            or any(not c["passed"] for c in result["checks"])
        )
        print(
            json.dumps(
                {
                    "live": snapshot["live"],
                    "formula_errors": len(result["formula_errors"]),
                    "reference_warnings": len(result["reference_warnings"]),
                    "new_errors_and_warnings": len(
                        result["new_formula_errors"] + result["new_reference_warnings"]
                    )
                    if args.compare
                    else None,
                    "check_ranges": len(result["checks"]),
                    "checks_failed": sum(not c["passed"] for c in result["checks"]),
                    "changes": len(result["changes"]) if "changes" in result else None,
                    "verdict": "review required"
                    if failed
                    else "mechanical checks passed; model assumptions not assessed",
                }
            )
        )
        return int(failed)
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ) as error:
        detail = (
            error.stderr.strip()
            if isinstance(error, subprocess.CalledProcessError) and error.stderr
            else str(error)
        )
        print(f"Audit incomplete: {detail}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
