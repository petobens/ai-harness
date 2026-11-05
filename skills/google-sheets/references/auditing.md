# Workbook audits

Use `scripts/audit_sheet.py`, relative to this skill, when a workbook-wide
review or structural edit warrants repeatable before/after verification.
It runs with `uv run` (Python 3.14+, no third-party dependencies) and the
existing `gws` credentials. Both Codex and Claude can invoke the same script.
It only calls `spreadsheets.get`; it never changes a workbook.

## Usage

```bash
uv run scripts/audit_sheet.py SHEET_ID --snapshot /tmp/before.json
# After the authorized edits:
uv run scripts/audit_sheet.py SHEET_ID --snapshot /tmp/after.json \
  --compare /tmp/before.json --checks /tmp/checks.json --report /tmp/audit.json
```

The snapshot stores formulas, effective/displayed values, formatting, links,
notes, validation, merges, dimensions, row and column groups, named ranges,
tables and other sheet metadata.
The script scans actual `effectiveValue.errorValue` values, so literal error
text is not mistaken for an error. A `#REF!` within a cell formula, data
validation rule or conditional-format rule is flagged for inspection even when
`IFERROR` masks it; it may also be literal formula text.

Add `--range "'Tab'!A1:H40"` (repeatable) to read only those ranges instead of
every tab. The snapshot records the ranges as its coverage. Compare snapshots
taken with the same ranges; otherwise cells outside the smaller read appear as
added or removed.

An optional checks file declares expected effective values in bounded A1 ranges:

```json
[
  {"range": "'Checks'!B3:B8", "expected": 0, "absolute_tolerance": 0.000001},
  {"range": "'Checks'!B9", "expected": 1},
  {"range": "'Checks'!B10:C10", "expected": [[0, "OK"]]}
]
```

A scalar applies to every cell; a matrix must match the range shape. Missing
cells fail checks instead of becoming zero; use `null` to assert an empty cell
(it fails for cells outside the fetched ranges).
Merged ranges store their value in the top-left cell only, so check that cell.
A failure on an error cell reports the error as its actual value. Numeric
comparisons use absolute tolerance; strings and booleans match exactly. Choose
checks from the model's actual invariants rather than copying checks from an
unrelated workbook.

Exit codes: `0` means mechanical checks passed, `1` means formula errors,
reference warnings or failed checks need review, and `2` means the audit could
not complete. With `--compare`, errors and warnings already present in the
baseline (such as intentional `NA()`) are still listed, but only new ones, in
`new_formula_errors` and `new_reference_warnings`, fail the run.
Metadata/value differences are reported for review and do not by themselves
fail the run. Do not reuse an older report after a failed run.

## Scope and interpretation

- Without `--range`, the live read requests all tabs and grid data. Scope it
  for very large workbooks; this helper is not mandatory for each edit.
- `--input /tmp/raw-get.json` inspects an existing raw `spreadsheets.get`
  response offline. Its report explicitly marks coverage as unverified and
  does not constitute a fresh live read.
- Diffs align cells by coordinates and tabs by stable sheet ID. Changes to
  conditional-format ranges, links, validation and dimensions remain visible.
  Review benign color rounding, recalculated values and concurrent user edits;
  never feed the diff into an automatic repair pass.
- Passing checks proves only the declared reconciliations. Verify source
  definitions and model logic separately. Continue using `check_fit.py` and
  visual rendering: wrapped or merged cells can still hide text at fixed heights.
- Snapshots contain workbook data. Keep them in the task's local working area,
  not in the shared skill or repository.
