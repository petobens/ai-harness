# Formatting Conventions

Preserve the workbook's established formatting and layout unless the user
requests a restyle. Apply these conventions when creating new tables, repairing
inconsistent formatting, or extending an existing table that follows them.

## Contents

- [Color palette](#color-palette-cell-backgrounds)
- [Semantic colors](#semantic-colors)
- [Text formatting](#text-formatting)
- [Period labels](#period-labels)
- [Number formatting](#number-formatting)
- [Alignment and wrapping](#alignment-and-wrapping)
- [Row hierarchy](#row-hierarchy)
- [Structure](#structure)
- [Workbook architecture](#workbook-architecture)
- [Side-by-side tables](#side-by-side-tables)
- [README tab](#readme-tab)

## Color palette (cell backgrounds)

Use the corresponding Google Sheets variants consistently.

- **Dark gray 1** (`#b7b7b7`) for top-level **table title cells** or compact
  title blocks, merged only when the structure rules below allow it.
- **Light gray 1** (`#d9d9d9`) for populated **title-row totals** beside a dark
  gray title cell or block, and for README section headers. Within consecutive
  emphasized body rows, it may also distinguish primary rows from supporting
  rows.
- **Soft gray** (`#efefef`) as the default for emphasized calculated totals,
  subtotals, reconciliation rows, and KPIs within a table body, and for README
  subsection headers.
- **Light green 2** (`#b6d7a8`) for **field-style headers** and, in wider data
  tables, typically the first column or first two columns. In compact two-column
  tables, use it only for the field/metric column header.
- **Light cornflower blue 2** (`#a4c2f4`) for **value-style headers**, **info
  subsection headers**, and most remaining header columns in wider data tables.
  In compact two-column tables, use it for the value column header.
- **Light cyan 2** (`#a2c4c9`) for **specific highlighted headers** in wider
  data tables, usually actual periods or special-purpose columns.
- **Light orange 2** (`#f9cb9c`) for full-year or terminal-total headers, and
  sparingly for other important individual cells.
- **Light red 2** (`#ea9999`) sparingly for adverse scenarios or important
  individual cells.
- Prefer soft gray for emphasized body rows. When two or more emphasized rows
  are consecutive, light gray 1 may be used sparingly on primary rows to create
  hierarchy; keep the supporting rows soft gray.
- Table body cells should have **no background fill** unless the user explicitly
  requests an exception, a specific value needs highlighting, or soft-gray
  emphasis materially improves readability.

Do not introduce colors outside this palette unless the user explicitly asks.

Write these exact hex values, since they are the Google Sheets picker variants a
user gets from the UI. Do not expect to read them back unchanged: structural
edits such as `moveDimension`, `insertDimension`, or a sheet rename make Sheets
re-quantize stored fills by up to one 8-bit step per channel, so `#b7b7b7` comes
back as `#b6b6b6` and `#d9d9d9` as `#d8d8d8`. The difference is invisible. When
auditing fills, match each color to the nearest palette entry within a tolerance
of about 2/255 per channel and treat it as correct. Only rewrite a fill when it
is genuinely a different color, not to chase this drift.

### Semantic colors

- Use light cyan 2 for actual-period headers, light cornflower blue 2 for
  forecast-period headers, and light orange 2 for full-year or terminal-total
  headers. Apply these roles consistently wherever the same periods recur.
- In scenario comparisons, use light red 2 for the adverse case, light
  cornflower blue 2 for the central case, and light green 2 for the favorable
  case.
- Use light gray 1 for populated title-row totals. Use soft gray by default for
  emphasized totals, subtotals, reconciliation rows, and KPIs within the table
  body. In a consecutive emphasized block, light gray 1 may distinguish primary
  rows from soft-gray supporting rows. Leave ordinary detail rows unfilled.

## Text formatting

- Use **10 pt font** throughout the workbook except on the README tab, which
  follows its dedicated typography rules below. Do not otherwise increase font
  size for titles, headers, totals, or emphasis unless the user explicitly asks.
- Table titles and column headers must always be **bold**.
- Column headers use human-readable **Title Case** labels such as `Foo Bar`, not
  snake_case, lower case, or sentence case.
- Choose one term for each recurring concept and use it consistently across tab
  names, table titles, headers, labels, mechanics, and documentation. Do not
  alternate between near-synonyms unless they represent different concepts.
- Where a row label or column header refers to a measurable value, include the
  unit in parentheses when practical, such as `(USD)`, `(%)`, or `(Q)`. Put the
  unit on the label that names the measured metric, not on a purely categorical
  or time-period header. Put units in a column header only when the column itself
  is the measured field, such as `Amount (USD)`, `Rate (%)`, or `Units (Q)`.
- Style manual model inputs and configuration parameters as **bold blue**
  (`#0010ff`, bold), anywhere in the workbook, not just dedicated parameter
  tables.
- Do not use bold blue for ordinary data-entry or imported records, including
  transaction amounts, dates, quantities, and row-level facts. Those are data,
  not parameters.
- Regular values: default text color, not bold. Formulas and derived values:
  default text color unless the user wants them emphasized.

### Period labels

- Write period labels without spaces: `202601`, `2026Q1`, `2026H1`, `2026FY`.
- Place interim totals immediately after their component periods, for example:
  `2026Q1`, `2026Q2`, `2026H1`, `2026Q3`, `2026Q4`, `2026H2`, `2026FY`.
- Use concise comparison headers such as `Q2 QoQ (%)`, `HoH (%)`, and `YoY (%)`.
  Do not repeat the complete periods in every comparison header.

## Number formatting

- Currency: `$` prefix with thousands separators (e.g. `$14,800,000`).
- Percentages: trailing `%` with **2 decimal places** (e.g. `12.49%`, `40.00%`).
- Show negative values with a leading minus sign, not parentheses, such as
  `-$14,800` or `-12.49%`.
- Format percentage-point changes as numbers followed by `pp`, not as
  percentages, and use a leading minus sign for negative changes.
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

## Row hierarchy

- Use indentation to show hierarchy: indent components, supporting amounts,
  adjustments, and bridge items beneath the primary metric they explain.
- Keep primary KPIs unindented. Use bold and soft-gray shading selectively to
  distinguish them from supporting calculations; do not bold every derived row.
- Treat repeated metric pairs consistently: give the primary measure the same
  emphasis and its supporting calculation the same indentation throughout.
- Format share or mix rows as indented, italic, and not bold. Use the concise
  label `Share (%)` when the parent row already supplies the context.

## Structure

- For compact two-column tables, use `Metric` (or another field label) as the
  first column header with light green 2 (`#b6d7a8`), and `Value` as the second
  with light cornflower blue 2 (`#a4c2f4`). Do not make both headers green.
- Group related tables on the same tab, each with its own dark gray title cell or
  compact title block.
- In wide tables other than the README layout, keep the title in column A. Let it
  span A:B or A:C only when needed for legibility; never extend it across the
  full table merely to match the table width. Compact tables of three columns or
  fewer may merge the title across their actual width.
- Keep cells to the right of a title blank and unfilled unless they contain
  genuine title-row totals. When totals exist, use dark gray for the title cell
  or block and light gray for populated total cells; never shade empty cells.
- Keep titles concise. Prefer a descriptive noun phrase followed by one short
  qualifier, using at most one separator.
- Whenever a table has a total row, the required row order is: title and total
  values on the same row, then column headers, then body rows. Total rows are
  always above the column headers, never below or at the bottom, unless the user
  explicitly asks otherwise.
- Do not add a `Total` label in the total row unless the user explicitly asks.
- Give every worksheet an explicit, descriptive name, such as `Params`,
  `Source Data`, `Model`, `Summary`, `README`, or `To-Dos`. Never leave a tab as
  `Sheet1`.
- Do not freeze rows or columns by default. Freeze panes only when the user
  explicitly asks.
- Leave exactly one empty spacer between distinct subtables on the same tab: one
  blank column for side-by-side, one blank row for stacked. Do not add blank rows
  inside a table, e.g. between a title or total row and its column headers.
- Source footnotes and input-basis notes are optional, including for imported or
  pasted data. Add them only when provenance, timing, or definitions provide
  useful context that is not already clear from the table. When adding one, place
  it directly below the table's last row, before the spacer: column A of the
  table, 9 pt italic, dark gray 3 (`#666666`) text, no fill, not wrapped, so it
  overflows across the empty cells to the right. Start source footnotes with
  `Source:` and include only relevant details: system or file, table or query,
  filters, snapshot date, or definitions needed to interpret the numbers.
  Keep every line within the table's own columns, never overflowing past its
  last column; break long
  notes into extra rows (measure the text against the summed column widths)
  rather than wrapping or merging. Use the same style for an optional short
  basis note under an input table whose defaults come from data.
- When the user specifies a starting row, place the table title on that row. If
  the table has totals, put the title and total values on that same row, then
  column headers on the next row and body rows below.
- Before constructing formatting from palette rules, inspect and copy the nearest
  semantically equivalent row or table through paste-formatting when practical.
  Treat informal color descriptions as contextual unless the user specifies a
  palette name or hex value; when the user cites a cell or range as the example,
  copy its exact formatting.
- Keep gridlines visible unless the user explicitly requests otherwise.

### Workbook architecture

- Organize tabs by logical responsibility, such as documentation, parameters,
  source data, operating drivers, calculations, scenarios, and outputs.
- Keep workbook-wide controls and assumptions used by multiple calculation areas
  in a dedicated `Params` tab. Co-locate narrowly scoped inputs with their
  primary model tab, and do not duplicate shared assumptions.
- Give each table one clear grain and one row per record. When data repeats,
  connect normalized tables with stable keys and store each source value once.
- Split a worksheet when it mixes distinct calculation engines, becomes hard to
  scan, or combines unrelated grains.
- Keep tightly coupled drivers and their immediate outputs together when that
  makes the causal relationship easier to audit. Order drivers before outputs.
- Within a repeated subject area, show detailed-period tables before
  summarized-period tables, and keep the same table sequence across related
  tabs.
- When presenting an aggregate and its components, show the aggregate first and
  then its components. Keep that ordering consistent across related tables.
- Avoid hidden or far-right helper tables when formulas can live directly in the
  principal table. Put substantial reusable helper logic in a clearly named
  dedicated tab.

### Side-by-side tables

- Place small, directly comparable tables side by side when they have compatible
  structures and are meant to be read together.
- Separate them with exactly one blank column; align their title and header rows;
  and match column widths, row heights, number formats, and hierarchy.
- When inserting columns for a side table, keep the spacer and unused cells below
  the table unfilled and not bold. Inspect them across every used row because
  inserted columns may inherit each existing row's formatting.
- Stack wide time-series or detail tables vertically rather than forcing them
  side by side.

## README tab

Use a single README tab for narrative context, instructions, model explanation,
and important caveats. Keep it readable and polished, but do not over-design it.

### README layout and formatting

- Use **Arial** throughout the README, sized by level so headings stand out
  from the text: **14 pt** title, **13 pt** section headers, **12 pt**
  subsection headers, and **11 pt** labels and body text.
- Keep the README content no wider than columns A:E. Size column A for the
  body-row labels (at most two wrapped lines); never widen it to fit body text.
- Put the README title in its own merged row across A:E. Use dark gray 1
  (`#b7b7b7`), bold text, horizontal and vertical centering, and wrapping.
- Start the first section immediately below the title, with no blank row between
  them. Build every section from three parts:
  1. A merged A:E section-header row with light gray 1 (`#d9d9d9`), bold text,
     left alignment, vertical centering, and wrapping. With six or more
     sections, number the headers (`1. Scope`, `2. ...`).
  2. One or more unfilled body rows directly below it. Use a single merged A:E
     row only for a short paragraph. When a section covers several
     sub-topics, items, terms, or steps, give each its own labeled row: a short
     bold label in column A and the text merged across B:E. The label column
     provides emphasis even when the text is a live formula, because formula
     cells cannot carry rich text. Body text is regular weight; labels and text
     are unfilled, left- and top-aligned, and wrapped.
  3. Exactly one blank, unfilled, non-bold spacer row after the body, including
     after the final section.
- To group closely related sections, typically the model mechanics, use one
  numbered parent header (`5. Model mechanics`) with no body of its own,
  followed directly by numbered subsections (`5.1 Revenue`, `5.2 Cost`). Each
  subsection has a merged A:E header row with soft gray (`#efefef`), bold text,
  left alignment, vertical centering, and wrapping, then its body rows. Leave no
  spacer rows inside the group; one spacer follows the whole group.
- Keep each section independently editable. Do not collapse multiple sections
  into one large rich-text narrative block.
- Sheets does not auto-fit rows with merged wrapped cells. Set every body row's
  height explicitly: count wrapped lines with real font metrics (about 18 px per
  11 pt line plus 8 px), then confirm in the render that no text is clipped.
- When inserting or moving README rows, inspect the full A:E range afterward.
  Reset inherited fill, bold, alignment, and wrapping on spacer rows, and verify
  every header, label, and body row retained its intended formatting.
- Keep the workbook map synchronized with the actual tabs and remove stale
  references. Prefer shortening the narrative before increasing its footprint.

### README prose conventions

- Abbreviate large numbers with `M` and `k` when more readable, e.g. `$14M`,
  `$850k`, `$1.15M`, instead of `$14,000,000`, `$850,000`, `$1,150,000`.
- Keep prose direct, concrete, and useful. Avoid generic AI-written framing,
  hype, filler, or content-marketing language.
- Do not write a body cell longer than about two sentences as one unbroken
  paragraph. Break it with line breaks (`CHAR(10)` inside formulas, a literal
  newline in plain text): use `•` bullets for parallel points, `1.` numbering
  for sequences or steps, and keep each item to one or two sentences. Do not
  start a bullet with `-`, `+`, or `=`, which `USER_ENTERED` parses as a
  formula.

### Suggested README content structure

Treat this as a suggestion, not a required template:

- Initial summary of what the workbook does.
- Key takeaways.
- Model mechanics, logic, assumptions, and approach, grouped into numbered
  subsections when there are several areas (revenue, capacity, cost).
- Definitions, when terms or abbreviations may not be obvious.
- How to use the sheet, including which inputs the user should change.
- Limitations, caveats, and known exclusions.
