---
name: gsheets
description: >-
    Create, read, edit, and analyze Google Sheets with gws. Use when the user
    asks to build, update, inspect, copy, rename, or trash a Google Sheet,
    write formulas, or produce a polished spreadsheet that follows the
    documented formula and visual conventions.
metadata:
    short-description: Build, read, and manage Google Sheets with gws
    category: productivity
    requires:
        bins:
            - gws
---

<!-- markdownlint-disable MD013 -->

# Google Sheets

Use `gws` to create, read, edit, and analyze Google Sheets. Own both formula
correctness and spreadsheet polish. Preserve the workbook's established
formatting and layout unless the user requests a restyle.

## Required references

- Before any `gws` operation, read
  [gws-recipes.md](references/gws-recipes.md) completely.
- Before creating, editing, formatting, or visually reviewing a spreadsheet,
  read [formatting.md](references/formatting.md) completely. Its formatting
  rules are mandatory unless the user explicitly requests an exception.

## Rules

- Treat an explicit request to create or edit a spreadsheet as authorization to
  do so. Ask only before trashing/deleting a sheet, an unrequested destructive
  rewrite, or a materially ambiguous choice.
- Do not ask for task-level permission before safe local prep, such as writing
  request JSON to `/tmp`, running `--dry-run`, or inspecting a sheet. If the
  environment requires sandbox approval for those commands, request it as a tool
  permission only, not a product confirmation.
- Google Sheets reads and writes require network access. In restricted
  sandboxes, if a `gws` command fails with a DNS, discovery, or other
  network-access error, rerun the same command with escalated tool permissions;
  do not treat it as a spreadsheet or API-shape failure.
- When reading or inspecting a sheet, keep the content in agent context and
  return only a brief confirmation with the title, ID, URL, and inspected ranges
  by default. Do not paste cell contents, a full extraction, or a summary unless
  the user explicitly asks for one.
- Inspect the target sheet before editing so you understand existing tabs, named
  ranges, table layout, and formatting. Inspect again before reporting done, and
  fix any off-by-one or shifted-cell issues introduced during the edit.
- For a small edit, validate every edited range and its surrounding table
  boundaries. Read both formulas and displayed values, scan for formula errors,
  confirm relevant totals reconcile, and inspect `effectiveFormat`
  (`backgroundColor`, `textFormat.bold`, number format, alignment, and wrap).
- For a workbook-wide review or broad structural change, perform those checks
  across every relevant table. Confirm every row's fill and bold match its role:
  no palette fill or bold on ordinary body rows, and title/total fills only on
  actual title/total rows. Compare colors with a small tolerance because values
  read back as floats (e.g. `#b7b7b7` returns `~0.717`).
- Make the smallest safe change that achieves the user's goal.
- Before editing a target area, clear lingering formatting issues there (stale
  formatting, accidental fills, wrong text color, wrong merge state) so you start
  from a clean baseline, while preserving intended structure such as existing
  tables, header rows, total rows, and merged text blocks.
- Apply formatting (colors, number formats, alignment, wrap) as part of the same
  change, not as a follow-up round.
- For destructive edits or large rewrites, prefer copying the sheet first and
  writing to the copy.
- Accept Google Sheets URLs or IDs from the user; always pass the bare
  spreadsheet ID (the segment after `/spreadsheets/d/`) to `gws`.
- Use `gws schema sheets.spreadsheets.METHOD` or `gws sheets --help` when unsure
  about params, request bodies, or supported commands.
- Report final title, ID, URL, and operations performed.

## Formula standards

- Whenever a value is the result of a computation, write it as a formula in the
  sheet. Never compute the result yourself and paste a static number when the
  value should be derived from other cells.
- Prefer native formulas like `=SUM(A1, A2)` or `=A1+A2` over manual arithmetic.
- For totals over filterable tables, prefer `SUBTOTAL`, e.g.
  `=SUBTOTAL(9, B3:B)`, so totals respond when users filter rows.
- Prefer named ranges for repeated, stable, meaningful parameters so formulas
  stay readable. Avoid magic numbers: put assumptions, constants, and thresholds
  in labeled cells or named ranges and reference them from formulas.
- Avoid `IMPORTRANGE` unless clearly needed. Prefer local source tabs,
  pasted/imported data tables, or connected data ranges when they are more
  reliable and easier to audit.

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
