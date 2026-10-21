#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = ["pillow"]
# ///
"""Flag single-line Google Sheets cells whose text is wider than its cell.

Text is measured with real font metrics (Arial or a metric-compatible font such
as Liberation Sans). Wrapped cells are skipped: rows without a fixed height grow
to fit them, so only a render shows whether they clip.
"""

import argparse
import json
import subprocess
from functools import cache
from typing import Any

# uv installs Pillow from the script metadata; the editor may use system Python
from PIL import ImageFont  # ty: ignore[unresolved-import]

PADDING_PX = 6
TOLERANCE_PX = 2


def _font_file(pattern: str) -> str:
    result = subprocess.run(
        ["fc-match", "-f", "%{file}", pattern],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


@cache
def _font(path: str, size_px: float) -> ImageFont.FreeTypeFont:
    # Load at 4x size for sub-pixel precision; widths are divided back below
    return ImageFont.truetype(path, round(size_px * 4))


def _column_name(index: int) -> str:
    name = ""
    index += 1
    while index:
        index, rest = divmod(index - 1, 26)
        name = chr(65 + rest) + name
    return name


def _fetch(spreadsheet_id: str, ranges: list[str]) -> list[dict[str, Any]]:
    fields = (
        "sheets(properties.title,merges,data(startRow,startColumn,"
        "columnMetadata.pixelSize,rowData.values(formattedValue,effectiveValue,"
        "effectiveFormat(wrapStrategy,horizontalAlignment,"
        "textFormat(fontSize,bold)))))"
    )
    params = {
        "spreadsheetId": spreadsheet_id,
        "ranges": ranges,
        "includeGridData": True,
        "fields": fields,
    }
    result = subprocess.run(
        ["gws", "sheets", "spreadsheets", "get", "--params", json.dumps(params)],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    # gws may print a status banner before the JSON body
    return json.loads(result.stdout[result.stdout.index("{") :])["sheets"]


def check(sheets: list[dict[str, Any]], regular_font: str, bold_font: str) -> list[str]:
    """Return overflow warnings from grid data using regular and bold font files."""
    flags: list[str] = []
    for sheet in sheets:
        title = sheet["properties"]["title"]
        for data in sheet.get("data", []):
            row0 = data.get("startRow", 0)
            col0 = data.get("startColumn", 0)
            widths = [c.get("pixelSize", 100) for c in data["columnMetadata"]]
            hidden: set[tuple[int, int]] = set()
            merge_ends: dict[tuple[int, int], int] = {}
            for merge in sheet.get("merges", []):
                top, left = merge["startRowIndex"], merge["startColumnIndex"]
                right = merge["endColumnIndex"]
                merge_ends[(top, left)] = right
                hidden |= {
                    (r, c)
                    for r in range(top, merge["endRowIndex"])
                    for c in range(left, right)
                } - {(top, left)}
            rows = [r.get("values", []) for r in data.get("rowData", [])]
            for i, values in enumerate(rows):
                row = row0 + i
                for j, cell in enumerate(values):
                    col = col0 + j
                    text = cell.get("formattedValue")
                    fmt = cell.get("effectiveFormat", {})
                    if (
                        not text
                        or "\n" in text
                        or (row, col) in hidden
                        or fmt.get("wrapStrategy") == "WRAP"
                    ):
                        continue
                    style = fmt.get("textFormat", {})
                    size_px = style.get("fontSize", 10) * 4 / 3
                    path = bold_font if style.get("bold") else regular_font
                    need = _font(path, size_px).getlength(text) / 4
                    # A merged cell spans up to its end column
                    k = merge_ends.get((row, col), col + 1) - col0
                    have = sum(widths[j:k]) - PADDING_PX
                    # Left-aligned text spills into empty cells to its right;
                    # numbers show ### instead of spilling
                    spills = (
                        fmt.get("wrapStrategy", "OVERFLOW_CELL") == "OVERFLOW_CELL"
                        and fmt.get("horizontalAlignment", "LEFT") == "LEFT"
                        and "stringValue" in cell.get("effectiveValue", {})
                    )
                    while spills and need > have + TOLERANCE_PX and k < len(widths):
                        if (row, col0 + k) in hidden or (
                            k < len(values) and values[k].get("formattedValue")
                        ):
                            break
                        have += widths[k]
                        k += 1
                    if need > have + TOLERANCE_PX:
                        flags.append(
                            f"{title}!{_column_name(col)}{row + 1}: needs "
                            f"{need:.0f} px, has {have:.0f} px | {text[:60]}"
                        )
    return flags


def main() -> None:
    """Parse arguments, fetch the ranges, and print flagged cells."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spreadsheet_id")
    parser.add_argument("ranges", nargs="+", help="A1 ranges, e.g. \"'Model'!A1:Z80\"")
    parser.add_argument("--regular-font", default=_font_file("Arial"))
    parser.add_argument("--bold-font", default=_font_file("Arial:bold"))
    args = parser.parse_args()
    flags = check(
        _fetch(args.spreadsheet_id, args.ranges), args.regular_font, args.bold_font
    )
    print("\n".join(flags) if flags else "No single-line overflow found.")


if __name__ == "__main__":
    main()
