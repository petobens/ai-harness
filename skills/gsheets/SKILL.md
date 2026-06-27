---
name: gsheets
description: >-
    Create, read, edit, and analyze Google Sheets with gws. Use when the user
    asks to build, update, inspect, copy, rename, or trash a Google Sheet,
    write formulas, or produce a polished spreadsheet that follows the formula
    and visual conventions below.
metadata:
    short-description: Build, read, and manage Google Sheets with gws
    category: productivity
    requires:
        bins:
            - gws
---

# Google Sheets

Use `gws` to create, read, edit, and analyze Google Sheets. You own both
formula correctness and spreadsheet polish: every sheet you touch should follow
the formula standards and visual conventions below.

## Rules

- Confirm only before creating a new sheet, trashing/deleting a sheet, or making
  the first substantive edit after creating one. Do not ask for extra permission
  before normal edits to an existing sheet.
- Do not ask for task-level permission before safe local prep, such as writing
  request JSON to `/tmp`, running `--dry-run`, or inspecting a sheet. If the
  environment requires sandbox approval for those commands, request it as a tool
  permission only, not a product confirmation.
- Inspect the target sheet before editing so you understand existing tabs, named
  ranges, table layout, and formatting. Inspect again before reporting done, and
  fix any off-by-one or shifted-cell issues introduced during the edit. As part
  of that final pass, read back each edited range's `effectiveFormat`
  (`backgroundColor`, `textFormat.bold`) and confirm every row's fill and bold
  match its intended role per the palette rules below — no palette fill or bold
  on ordinary body rows, and title/total fills only on actual title/total rows.
  Compare colors with a small tolerance, since values read back as floats (e.g.
  `#b7b7b7` returns `~0.7137`, not an exact match).
- Make the smallest safe change that achieves the user's goal.
- Name every worksheet descriptively. Never leave a tab as `Sheet1`.
- Ensure every worksheet has at least 1,000 rows and at least columns A:Z before
  finishing. When creating new tabs, resize them to that minimum grid
  immediately instead of leaving the default small grid.
- Do not freeze rows or columns by default. Freeze panes only when the user
  explicitly asks.
- Prefer named ranges for repeated, stable, meaningful parameters so formulas
  stay readable. Avoid magic numbers: put assumptions, constants, and thresholds
  in labeled cells or named ranges and reference them from formulas.
- Model workbook structure with relational concepts where helpful: keep tables
  small, entity-focused, and normalized so each has a clear grain and purpose.
- Before editing a target area, clear lingering formatting issues there (stale
  formatting, accidental fills, wrong text color, wrong merge state) so you start
  from a clean baseline, while preserving intended structure such as existing
  tables, header rows, total rows, and merged text blocks.
- Apply formatting (colors, number formats, alignment, wrap) as part of the same
  change, not as a follow-up round.
- For destructive edits or large rewrites, prefer copying the sheet first and
  writing to the copy.
- For rename/trash, confirm the file is a spreadsheet MIME type.
- Accept Google Sheets URLs or IDs from the user; always pass the bare
  spreadsheet ID (the segment after `/spreadsheets/d/`) to `gws`.
- Use `gws schema sheets.spreadsheets.METHOD` or `gws sheets --help` when unsure
  about params, request bodies, or supported commands.
- Report final title, ID, URL, and operations performed.

## Reading

Inspect structure first, then read the cells you care about. Use a `fields` mask
on `get` so the response stays small.

```bash
# Structure: worksheet titles, sheetIds, grid sizes, named ranges
gws sheets spreadsheets get --params '{"spreadsheetId":"SHEET_ID","fields":"properties.title,sheets.properties(title,sheetId,gridProperties(rowCount,columnCount)),namedRanges(name,range)"}'

# Displayed values for one range (helper; read-only)
gws sheets +read --spreadsheet SHEET_ID --range "P&L!A1:H40"

# Existing formulas — use FORMULA render mode before editing a computed area
gws sheets spreadsheets values batchGet --params '{"spreadsheetId":"SHEET_ID","ranges":["P&L!A1:H40"],"valueRenderOption":"FORMULA"}'
```

`+read` returns `FORMATTED_VALUE` (what the cell shows). When you need to
preserve or edit formulas, read the same range with `valueRenderOption:FORMULA`;
read both when you need displayed values and the formulas behind them.

## Writing

Each operation is a single command. `valueInputOption:USER_ENTERED` parses
strings beginning with `=` as formulas and infers number/date formats, matching
what a user typing into the cell would get.

```bash
# Set a range
gws sheets spreadsheets values update \
    --params '{"spreadsheetId":"SHEET_ID","range":"P&L!A1","valueInputOption":"USER_ENTERED"}' \
    --json '{"values":[["Revenue (USD)","=SUM(B2:B13)"]]}'

# Append rows (helper)
gws sheets +append --spreadsheet SHEET_ID --json-values '[["2026-06-27",10,"note"]]'

# Clear values
gws sheets spreadsheets values clear --params '{"spreadsheetId":"SHEET_ID","range":"Scratch!A1:Z100"}'
```

These value commands write cell contents only. For everything they cannot
express — formatting, merges, named ranges, grid resizing, freezing, column
auto-resize, conditional formatting — use `batchUpdate` (below).

## Files (create, find, copy, rename, trash)

Use the `gdrive` skill for these. A spreadsheet's mimeType is
`application/vnd.google-apps.spreadsheet`; pass it when creating, and confirm
the target matches it before copy, rename, or trash.

```bash
# Create a blank spreadsheet
gws drive files create \
    --params '{"fields":"id,name,webViewLink","supportsAllDrives":true}' \
    --json '{"name":"Spreadsheet title","mimeType":"application/vnd.google-apps.spreadsheet","parents":["root"]}'
```

## Raw batchUpdate

`spreadsheets.batchUpdate` applies requests atomically: if one is invalid, none
apply. Validate layout-sensitive bodies locally first with `--dry-run`.

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

Colors are RGB floats in `0..1`, e.g. dark gray 1 `#b7b7b7` is
`{"red":0.717,"green":0.717,"blue":0.717}`.

## Formula standards

- Whenever a value is the result of a computation, write it as a formula in the
  sheet. Never compute the result yourself and paste a static number when the
  value should be derived from other cells.
- Prefer native formulas like `=SUM(A1, A2)` or `=A1+A2` over manual arithmetic.
- For totals over filterable tables, prefer `SUBTOTAL`, e.g.
  `=SUBTOTAL(9, B3:B)`, so totals respond when users filter rows.

When you explain a formula to the user, structure it as:

**1. Assumptions:** cell references and whether they are absolute (`$A$1`) or
relative (`A1`), and why.

**2. Formula:** in an `excel` code block.

**3. Explanation:** what each part does and the logic flow.

**4. Implementation:** step-by-step application, including formatting tips.

### Use `LET` for readability

- Prefer `LET` when a formula references the same sub-expression more than once,
  or is complex enough that named intermediate values clarify the logic.
- Do not use `LET` just to look structured. Skip it for short, single-step
  formulas where it only adds noise.

### Naming conventions

- Use `snake_case` for `LET` variables.
- Prefer descriptive names like `start_date`, `end_date`, `filtered_values`,
  `daily_rate`. Avoid vague names unless brevity is necessary.

### Formula formatting

- Keep readable one-line formulas on a single line. Use multi-line formatting
  only for longer formulas where line breaks improve readability.
- Any `QUERY` with a non-trivial query string must format the query text like
  readable SQL: put `select`, `where`, `group by`, `order by`, `label`, and
  similar clauses on separate lines inside the string. Keep very short queries
  on one line only when that is genuinely clearer.
- Prefer direct cell references: prefer `=H2-L2-M2` over
  `=INDEX($H:$H, ROW()) - INDEX($L:$L, ROW()) - INDEX($M:$M, ROW())` when both
  are valid.
- Use parentheses when they clarify operation grouping, especially when mixing
  `+`, `-`, `*`, `/`. Prefer `=(B3*B4)/B6` over `=B3*B4/B6` and `=L19*(L4/L3)`
  over `=L19*L4/L3`.
- Prefer the simplest clear, auditable formula. Do not introduce `LET`, helper
  variables, `XLOOKUP`, `INDEX`/`MATCH`, `ARRAYFORMULA`, or other complex
  constructs when direct arithmetic or a short native formula is easier to read.

For multi-line formulas, indent to show nesting:

```excel
=LET(
  att, MIN(1, IFERROR(K11, 0)),
  cliff, $B$15,
  IF(att < cliff, 0, (att - cliff) / (1 - cliff))
)
```

## Visual conventions

Apply the palette and formatting consistently across every sheet you touch.

### Color palette (cell backgrounds)

Use the corresponding Google Sheets variants consistently.

- **Dark gray 1** (`#b7b7b7`) for top-level **table titles**: banner cells that
  name a table or section, merged across the table width only when the structure
  rules below allow it.
- **Light gray 1** (`#d9d9d9`) for **total rows**, which appear at the top of
  each table rather than the bottom.
- **Light green 2** (`#b6d7a8`) for **field-style headers** and, in wider data
  tables, typically the first column or first two columns. In compact two-column
  tables, use it only for the field/metric column header.
- **Light cornflower blue 2** (`#a4c2f4`) for **value-style headers**, **info
  subsection headers**, and most remaining header columns in wider data tables.
  In compact two-column tables, use it for the value column header.
- **Light cyan 2** (`#a2c4c9`) for **specific highlighted headers** in wider
  data tables, usually the last column or special-purpose columns, not as the
  default for all wide-table headers.
- **Light red 2** (`#ea9999`) or **light orange 2** (`#f9cb9c`) sparingly, to
  highlight specific important individual cells.
- A small **gradient or hierarchy of gray fills** may be used sparingly within
  table rows when it clearly improves readability, such as grouped subsection
  rows under a parent row.
- Table body cells should have **no background fill** unless the user explicitly
  requests an exception, a specific value needs highlighting, or a limited
  grayscale hierarchy materially improves readability.

Do not introduce colors outside this palette unless the user explicitly asks.

### Text formatting

- Use **10 pt font** throughout the workbook. Do not increase font size for
  titles, headers, totals, or emphasis unless the user explicitly asks.
- Table titles and column headers must always be **bold**.
- Column headers use human-readable **Title Case** labels such as `Foo Bar`, not
  snake_case, lower case, or sentence case.
- For monthly-period column headers, use compact `YYYYMM` labels such as
  `202605`, unless the user asks for another date format.
- Where a row label or column header refers to a measurable value, include the
  unit in parentheses when practical, such as `(USD)`, `(%)`, or `(Q)`. Put the
  unit on the label that names the measured metric, not on a purely categorical
  or time-period header. In a P&L with months across columns, use row labels like
  `Revenue (USD)`, `COGS (USD)`, `Gross Profit (USD)`, while month headers stay
  `202601`, `202602`. Only put units in column headers when the column itself is
  the measured field, such as `Amount (USD)`, `Margin (%)`, or `Units (Q)`.
- Style manual model inputs and configuration parameters as **bold blue**
  (`#0010ff`, bold), anywhere in the workbook, not just dedicated parameter
  tables.
- Do not use bold blue for ordinary data-entry or imported records, including
  transaction amounts, dates, quantities, and row-level facts. Those are data,
  not parameters.
- Regular values: default text color, not bold. Formulas and derived values:
  default text color unless the user wants them emphasized.

### Number formatting

- Currency: `$` prefix with thousands separators (e.g. `$14,800,000`).
- Percentages: trailing `%` with **2 decimal places** (e.g. `12.49%`, `40.00%`).
- If a displayed number is clearly an integer, do not format it with unnecessary
  decimal places.
- Never show raw decimals like `0.125` when a percentage is intended.

### Alignment and wrapping

- Table title cells and column header cells must be horizontally centered,
  vertically centered, and wrapped, so longer labels render cleanly.
- Text body columns, especially the first column of a table, should be
  left-aligned. This does not apply to column titles or header cells.
- Numeric columns and total-row values should be right-aligned.
- Body cells follow content-based alignment by default: text labels left,
  numbers right, and only special-purpose fields such as status flags centered
  when that clearly improves readability.
- Auto-resize columns so they are as narrow as possible while still fitting their
  contents, but wide enough that header words are not split awkwardly across
  lines (e.g. avoid wrapping `Transaction` as `Transactio` / `n`).

### Structure

- For compact two-column tables, use `Metric` (or another field label) as the
  first column header with light green 2 (`#b6d7a8`), and `Value` as the second
  with light cornflower blue 2 (`#a4c2f4`). Do not make both headers green.
- Group related tables on the same tab, each with its own dark gray title banner
  on top.
- Prefer compact layouts with related small tables placed side by side,
  separated by exactly one blank column, instead of stacking everything
  vertically when the sheet stays readable.
- Keep input tables minimal: only include assumptions that are directly used. Do
  not keep source snapshot or audit tables unless they are needed for formulas or
  explicitly requested.
- Table title background fill extends only across the actual width of the table,
  ending at the last populated column, never beyond it.
- If a table has a total row, place the table title in the first cell of the
  total row, not merged across the full width. Put total values on that same row,
  starting in the value columns to the right of the title cell. For example a P&L
  with the title in column A and totals across B:E on the same row.
- If a table has no total row, the title may extend across the full table width.
  The column header row must immediately follow the title row, with no blank row
  between them.
- Whenever a table has a total row, the required row order is: title and total
  values on the same row, then column headers, then body rows. Total rows are
  always above the column headers, never below or at the bottom, unless the user
  explicitly asks otherwise.
- Do not add a `Total` label in the total row unless the user explicitly asks.
- Give every worksheet an explicit, descriptive name (e.g. `Params`, `Unit Cost`,
  `Salary Bands`, `P&L`, `README`, `ToDos`).
- Prefer one table per logical concept. Split across tabs when a tab gets dense.
- Leave exactly one empty spacer between distinct subtables on the same tab: one
  blank column for side-by-side, one blank row for stacked. Do not add blank rows
  inside a table, e.g. between a title or total row and its column headers.
- When the user specifies a starting row, place the table title on that row. If
  the table has totals, put the title and total values on that same row, then
  column headers on the next row and body rows below.

## README tab

Use a single README tab for narrative context, instructions, model explanation,
and important caveats. Keep it readable and polished, but do not over-design it.

### README layout and formatting

- The README tab uses **11 pt font**. Do not increase font size for the title,
  section labels, or emphasis unless the user explicitly asks.
- It must have a separate title row and a separate narrative body block. Put the
  README title in its own merged row across the content width, styled like a
  table title: dark gray 1 (`#b7b7b7`), bold, horizontally and vertically
  centered, wrap enabled.
- The narrative usually lives directly below the title row, with no blank spacer
  row between them, in a single merged multi-column, multi-row cell containing
  the full text block, typically spanning about 3 to 5 columns and enough rows for
  the content to be fully visible without clipping.
- Format body text cleanly inside the merged block, preserving clear paragraph
  breaks, section labels, lists, and other internal structure.
- README section labels such as `Takeaways`, `How To Use`, and `Limitations`
  should be bold using rich-text styling inside the merged body block.
- Do not widen column A to fit narrative content; keep the body in the merged
  multi-column block instead of expanding A.
- When editing an existing README narrative block, preserve its structure and
  rich-text styling unless the user asks for a redesign.

### README prose conventions

- Abbreviate large numbers with `M` and `k` when more readable, e.g. `$14M`,
  `$850k`, `$1.15M`, instead of `$14,000,000`, `$850,000`, `$1,150,000`.
- Keep prose direct, concrete, and useful. Avoid generic AI-written framing,
  hype, filler, or content-marketing language.

### Suggested README content structure

Treat this as a suggestion, not a required template:

- Initial summary of what the workbook does.
- Key takeaways.
- One or more sections explaining model mechanics, logic, assumptions, and
  approach.
- Definitions, when terms or abbreviations may not be obvious.
- How to use the sheet, including which inputs the user should change.
- Limitations, caveats, and known exclusions.

## What to avoid

### Formula mistakes

- Computed values entered as hard-coded numbers instead of formulas.
- Needlessly formatting short, readable formulas across multiple lines.
- Indirect constructions such as `INDEX(column, ROW())` when a direct
  cell-reference formula such as `=H2-L2-M2` is clearer and equally valid.
- Using `IMPORTRANGE` unless clearly needed. Prefer local source tabs,
  pasted/imported data tables, or connected data ranges when more reliable and
  easier to audit.
- Hard-coding constants inside formulas when they should be labeled assumptions,
  named ranges, or table fields.

### Layout mistakes

- Leaving any tab named `Sheet1` or other auto-generated names.
- Leaving any worksheet with fewer than 1,000 rows or fewer than columns A:Z.
- Any layout that breaks the required order (title and total values on the same
  row, headers, body) when a total row exists.
- Adding a `Total` label in the total row when not needed.
- Table titles across the full width when the table has a total row.
- Title background fill extending beyond the last populated column.
- Subtables placed directly adjacent without exactly one blank separating row or
  column.
- Blank rows inside a table, especially between a title and its column headers or
  between a title and its total row.

### Visual styling mistakes

- Compact two-column tables where both `Metric` and `Value` headers are green.
- Colors outside the dark gray 1 / light gray 1 / light green 2 / light
  cornflower blue 2 / light cyan 2 / light red 2 / light orange 2 palette.
- Background fills on ordinary table body cells by default.
- Heavy or unnecessary grayscale banding in table bodies.
- Table titles not in dark gray 1 (`#b7b7b7`); total rows not in light gray 1
  (`#d9d9d9`).
- Wide-table headers colored all light cyan 2 by default instead of light green
  2 for the first one or two columns, light cornflower blue 2 for most, and light
  cyan 2 only for specific highlighted columns.
- Titles or headers without text wrap, horizontal center, or vertical center.
- Recreating formatting by hand when an existing table's style can be reused via
  copy/paste formatting.

### Text and value mistakes

- Percentages without a `%` symbol or without 2 decimal places.
- Numbers with unnecessary decimals when clearly integers.
- Currency without a `$` prefix or thousands separators.
- Manual input cells, anywhere in the workbook, shown without bold blue
  (`#0010ff`) when they are manual inputs rather than formulas, calculations, or
  imported data.
- Bold blue applied to formula cells, derived values, totals, or non-parameter
  data.
- Table titles or column headers that are not bold.
- Column headers written as snake_case, lower case, or other non-Title-Case
  labels.
- Omitting units from the metric label when values are measurable; or adding
  units to period/category headers that do not themselves name the measured
  value (e.g. `Jan 2026 (USD)`, `Q1 2026 (USD)`, `Region (USD)`).
- Text-heavy columns not left-aligned; numeric columns not right-aligned;
  total-row values not right-aligned.
- Columns left wider than necessary instead of auto-resized to fit content.
