# Formatting Conventions

Preserve the workbook's established formatting and layout unless the user
requests a restyle. Apply these conventions when creating new tables, repairing
inconsistent formatting, or extending an existing table that follows them.

## Contents

- [Color palette](#color-palette-cell-backgrounds)
- [Text formatting](#text-formatting)
- [Number formatting](#number-formatting)
- [Alignment and wrapping](#alignment-and-wrapping)
- [Structure](#structure)
- [README tab](#readme-tab)

## Color palette (cell backgrounds)

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

Write these exact hex values, since they are the Google Sheets picker variants a
user gets from the UI. Do not expect to read them back unchanged: structural
edits such as `moveDimension`, `insertDimension`, or a sheet rename make Sheets
re-quantize stored fills by up to one 8-bit step per channel, so `#b7b7b7` comes
back as `#b6b6b6` and `#d9d9d9` as `#d8d8d8`. The difference is invisible. When
auditing fills, match each color to the nearest palette entry within a tolerance
of about 2/255 per channel and treat it as correct. Only rewrite a fill when it
is genuinely a different color, not to chase this drift.

## Text formatting

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

## Number formatting

- Currency: `$` prefix with thousands separators (e.g. `$14,800,000`).
- Percentages: trailing `%` with **2 decimal places** (e.g. `12.49%`, `40.00%`).
- If a displayed number is clearly an integer, do not format it with unnecessary
  decimal places.
- Never show raw decimals like `0.125` when a percentage is intended.

## Alignment and wrapping

- Table title cells and column header cells must be horizontally centered,
  vertically centered, and wrapped, so longer labels render cleanly.
- Text body columns, especially the first column of a table, should be
  left-aligned. This does not apply to column titles or header cells.
- Numeric columns and total-row values should be right-aligned.
- Body cells follow content-based alignment by default: text labels left,
  numbers right, and only special-purpose fields such as status flags centered
  when that clearly improves readability.
- Size columns primarily for their body contents, not for displaying headers on
  one line. Wrap every header and use the narrowest width that fits the body
  values while keeping the header to at most three lines. Prefer two lines when
  a small width increase is enough; allow three when it keeps the table
  materially more compact. Never split a word across lines. Increase the header
  row height so all text remains visible.
- Do not rely on automatic column resizing when a long header would make the
  column unnecessarily wide. Set an explicit column width in those cases.

## Structure

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
  `Salary Bands`, `P&L`, `README`, `ToDos`). Never leave a tab as `Sheet1`.
- Ensure every worksheet has at least 500 rows and at least columns A:Z before
  finishing. When creating new tabs, resize them to that minimum grid
  immediately instead of leaving the default small grid.
- Do not freeze rows or columns by default. Freeze panes only when the user
  explicitly asks.
- Model workbook structure with relational concepts where helpful: keep tables
  small, entity-focused, and normalized so each has a clear grain and purpose.
- Prefer one table per logical concept. Split across tabs when a tab gets dense.
- Leave exactly one empty spacer between distinct subtables on the same tab: one
  blank column for side-by-side, one blank row for stacked. Do not add blank rows
  inside a table, e.g. between a title or total row and its column headers.
- When the user specifies a starting row, place the table title on that row. If
  the table has totals, put the title and total values on that same row, then
  column headers on the next row and body rows below.
- Reuse an existing table's formatting through copy/paste formatting when
  practical rather than recreating it by hand.

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
