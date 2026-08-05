# gws Recipes

<!-- markdownlint-disable MD013 -->

Use these commands and API patterns when working with Google Sheets through
`gws`.

## Contents

- [Files](#files)
- [Reading](#reading)
- [Writing](#writing)
- [Raw batchUpdate](#raw-batchupdate)

## Files

Use the `gdrive` skill to create, find, copy, rename, or trash spreadsheet
files. A spreadsheet's mimeType is
`application/vnd.google-apps.spreadsheet`; pass it when creating, and confirm
the target matches it before copy, rename, or trash.

```bash
# Create a blank spreadsheet
gws drive files create \
    --params '{"fields":"id,name,webViewLink","supportsAllDrives":true}' \
    --json '{"name":"Spreadsheet title","mimeType":"application/vnd.google-apps.spreadsheet","parents":["root"]}'
```

## Reading

Inspect structure first, then read the cells you care about. Use a `fields` mask
on `get` so the response stays small.

```bash
# Structure: worksheet titles, sheetIds, grid sizes, named ranges
gws sheets spreadsheets get --params '{"spreadsheetId":"SHEET_ID","fields":"properties.title,sheets.properties(title,sheetId,gridProperties(rowCount,columnCount)),namedRanges(name,range)"}'

# Displayed values for one range (helper; read-only)
gws sheets +read --spreadsheet SHEET_ID --range "Model!A1:H40"

# Displayed values for several ranges; prefer this over parallel +read calls
gws sheets spreadsheets values batchGet --params '{"spreadsheetId":"SHEET_ID","ranges":["README!A1:E80","Data!A1:Z120","Model!A1:Z140"],"valueRenderOption":"FORMATTED_VALUE"}'

# Existing formulas — use FORMULA render mode before editing a computed area
gws sheets spreadsheets values batchGet --params '{"spreadsheetId":"SHEET_ID","ranges":["Model!A1:H40"],"valueRenderOption":"FORMULA"}'
```

`+read` returns `FORMATTED_VALUE` (what the cell shows). When you need to
preserve or edit formulas, read the same range with `valueRenderOption:FORMULA`;
read both when you need displayed values and the formulas behind them.

Do not run multiple `gws sheets` reads in parallel: concurrent reads can race on
auth/token refresh and fail with `Sheets auth failed: Failed to get token`.
Batch several ranges into one `values.batchGet` call instead, and if `+read`
hits that auth error after another Sheets command succeeded, retry with
`batchGet` before treating it as a real auth failure.

## Writing

Each operation is a single command. `valueInputOption:USER_ENTERED` parses
strings beginning with `=` as formulas and infers number/date formats, matching
what a user typing into the cell would get.

```bash
# Set a range
gws sheets spreadsheets values update \
    --params '{"spreadsheetId":"SHEET_ID","range":"Model!A1","valueInputOption":"USER_ENTERED"}' \
    --json '{"values":[["Total","=SUM(B2:B13)"]]}'

# Append rows (helper)
gws sheets +append --spreadsheet SHEET_ID --json-values '[["2026-06-27",10,"note"]]'

# Clear values
gws sheets spreadsheets values clear --params '{"spreadsheetId":"SHEET_ID","range":"Scratch!A1:Z100"}'
```

These value commands write cell contents only. For everything they cannot
express — formatting, merges, named ranges, grid resizing, freezing, column
auto-resize, conditional formatting — use `batchUpdate`.
Group related writes into as few atomic requests as practical, rather than
issuing one network command per cell or formatting change.

Prefer the `values` endpoints for content-only edits because they preserve
existing formatting. With `updateCells` or `repeatCell`, use the narrowest
possible `fields` mask and include `userEnteredFormat` only when intentionally
changing formatting.

## Raw batchUpdate

`spreadsheets.batchUpdate` applies requests atomically: if one is invalid, none
apply. Validate layout-sensitive bodies locally first with `--dry-run`.
Structural mutations shift the coordinates used by later requests in the same
batch. Process row and column deletions from bottom to top, account for the new
coordinates in subsequent requests, and re-inspect the affected layout after
the batch applies.

Use `moveDimension` to reorder complete rows or columns instead of copying and
clearing them. It preserves formatting and lets Sheets update dependent formulas;
re-read the moved range and its dependents afterward.

```bash
gws sheets spreadsheets batchUpdate --dry-run \
    --params '{"spreadsheetId":"SHEET_ID"}' \
    --json "$(cat /tmp/requests.json)"
```

Requests address cells with zero-based, half-open `GridRange`
(`startRowIndex`, `endRowIndex`, `startColumnIndex`, `endColumnIndex`) keyed by
`sheetId` (read it from the `spreadsheets get` inspect command above). Common
request types:
`updateCells` / `repeatCell` (values, `userEnteredFormat`: backgrounds, text
format, number format, alignment, wrap), `mergeCells`, `updateSheetProperties`
(rename, grid size, frozen rows/cols), `addNamedRange`,
`autoResizeDimensions`, and `addSheet` / `deleteSheet`.

Copy, move, or format complete merged ranges rather than partially intersecting
them. For small wording changes inside an existing rich-text cell, prefer
`findReplace` over rewriting the whole cell so its text-format runs survive.

Colors are RGB floats in `0..1`, e.g. dark gray 1 `#b7b7b7` is
`{"red":0.717,"green":0.717,"blue":0.717}`.
