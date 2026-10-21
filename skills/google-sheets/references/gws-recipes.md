# gws Recipes

Use these commands and API patterns when working with Google Sheets through
`gws`.

## Contents

- [Files](#files)
- [Reading](#reading)
- [Metadata inspection](#metadata-inspection)
- [Writing](#writing)
- [Raw batchUpdate](#raw-batchupdate)
- [Rendering](#rendering)

## Files

Use the `google-drive` skill to create, find, copy, rename, or trash spreadsheet
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

## Metadata inspection

Values endpoints do not expose layout metadata. Before and after structural or
formatting edits, use a range-scoped `spreadsheets.get` to compare formatting,
merges, conditional formatting, data validation, hyperlinks, rich-text runs, and
dimension sizes. Re-read workbook-level named ranges when coordinates can shift.

```bash
gws sheets spreadsheets get \
    --params '{"spreadsheetId":"SHEET_ID","ranges":["Model!A1:H40"],"includeGridData":true,"fields":"namedRanges(name,range),sheets(properties(title,sheetId),merges,conditionalFormats,data(startRow,startColumn,rowMetadata(pixelSize),columnMetadata(pixelSize),rowData.values(userEnteredValue,effectiveFormat(backgroundColor,textFormat(bold,fontSize,foregroundColor),numberFormat,horizontalAlignment,verticalAlignment,wrapStrategy),dataValidation,hyperlink,textFormatRuns)))"}'
```

For rich-text links, inspect link URIs inside `textFormatRuns`; the cell-level
`hyperlink` field may be empty. Keep ranges and field masks narrow so the response
stays reviewable.

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
existing cell formatting. They do not preserve rich text: writing a cell through
`values` replaces its `textFormatRuns`, so in-cell bold, colors, and links are
lost. Before rewriting a cell, check it for runs; if it has any, follow the
rich-text guidance in [Raw batchUpdate](#raw-batchupdate). With `updateCells`
or `repeatCell`, use the narrowest possible `fields` mask and include
`userEnteredFormat` only when intentionally changing formatting.

## Raw batchUpdate

`spreadsheets.batchUpdate` applies requests atomically: if one is invalid, none
apply. Validate layout-sensitive bodies locally first with `--dry-run`.
Structural mutations shift the coordinates used by later requests in the same
batch. Process row and column deletions from bottom to top, account for the new
coordinates in subsequent requests, and re-inspect the affected layout after
the batch applies.

For structural changes, capture the affected formulas, displayed values,
invariant outputs, and metadata before writing. After the batch applies, repeat
the same reads and compare them, including shifted dependents and metadata ranges
outside the edited table.

`insertDimension.inheritFromBefore` chooses which adjacent dimension supplies
formatting; it does not create neutral cells. When inserted rows or columns
should be blank outside a new table, add a targeted `repeatCell` request for the
unused portion and reset only the inherited format fields that should be
neutral. Validate blank cells across the full used extent, since title, header,
total, and KPI formats can otherwise repeat into the inserted dimensions.

Use `moveDimension` to reorder complete rows or columns instead of copying and
clearing them. It preserves formatting and lets Sheets update dependent formulas;
re-read the moved range and its dependents afterward.

To move a block that does not span complete rows or columns, such as one table
beside others, use `cutPaste`. Sheets updates formulas that reference the moved
cells, including from other tabs.

- When the source and destination overlap, cut the block to an empty staging
  area first, then cut it to the destination. Keep the staging area inside the
  sheet's `gridProperties.rowCount` and `columnCount`; a destination outside
  the grid fails.
- Cell addresses written inside text are not updated: notes, labels, and string
  literals in formulas such as `"(D32:F46)"`, `"(B20)"`, or `"row 52"`. After
  every move, search the workbook's text and formulas for the old addresses and
  update them.
- Row heights and column widths stay with the grid, not the moved cells. Reset
  them for the block's new rows and columns.
- When porting a formula from one tab to a parallel tab with a similar layout,
  resolve every address again on the target tab instead of reusing the source
  tab's coordinates, then read the displayed result to confirm it.

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
`findReplace` over rewriting the whole cell so its text-format runs survive. If
rewriting is necessary, preserve and restore the runs explicitly, then verify
their link URIs.

Colors are RGB floats in `0..1`, e.g. dark gray 1 `#b7b7b7` is
`{"red":0.717,"green":0.717,"blue":0.717}`.

## Rendering

Values reads do not show clipped labels, wrapped headers, or misaligned tables,
so layout edits need a visual check. Exporting and rasterizing the workbook is
slow, so use it sparingly:

- While editing, check single-line cells from metadata with
  `scripts/check_fit.py`, resolved relative to the skill's `SKILL.md`. It
  measures each text with Arial font metrics, allows left-aligned text to spill
  into empty cells to its right, and prints the cells that do not fit.
  Overshoots under about 10 px may still look fine in the render. The script
  skips wrapped cells: rows without a fixed height grow to fit, so only the
  render shows whether they clip. Include complete merges and blank columns to
  the right for overflow; the check only sees the requested ranges. Measurements
  assume Arial and do not account for rich-text runs or hidden columns.

  ```bash
  uv run scripts/check_fit.py SHEET_ID "'Model'!A1:Z80" "'Inputs'!A1:J40"
  ```

- Render once, after layout and formatting edits are complete and before
  handing off. Skip it for value-only edits. If the render shows defects, fix
  them and render again.

The export shrinks each tab to the page width, so render at about 450 dpi and
crop to the table under review. Compute the crop instead of guessing: after
trimming, scale is image width divided by the tab's used column width in
pixels, and a cell's offset is scale times the column widths to its left and
the row heights above it. Offsets drift slightly down the page, so add about
one row of margin above and below. A tab that spans several pages restarts the
row offset on each page.

```bash
render_dir=$(mktemp -d)
# gws requires the output path to stay inside its working directory
cd "$render_dir"
gws drive files export \
    --params '{"fileId":"SHEET_ID","mimeType":"application/pdf"}' \
    -o ./sheet.pdf
# Tabs export in tab order; find the tab's page by text unique to that tab,
# since tabs can share titles
pdftotext -f 3 -l 3 ./sheet.pdf - | head -1
pdftoppm -r 450 -png -f 3 -l 3 ./sheet.pdf ./p
# Output is p-3.png; pdftoppm zero-pads it (p-03.png) in 10+ page PDFs
# Trim the margins, then crop the computed WIDTHxHEIGHT+X+Y region
magick ./p-3.png -trim +repage -crop WIDTHxHEIGHT+X+Y +repage \
    -resize 1500x ./crop.png
```

Open the crop with the agent's image viewer (Codex: `view_image`; Claude: `Read`)
and inspect it before reporting the visual check complete.

The export covers every tab and needs Drive access. Re-export after fixing
defects; do not reuse an earlier PDF.
