# Typst document patterns

Read only the section for the selected document type or component. Consult the
corresponding template source only when the documented patterns do not expose a
needed parameter or behavior.

## Articles

- Import `@local/latex-article:0.1.0` and apply `latex-article.with(...)`.
- Let the template own page geometry, title matter, abstract width, typography,
  running heads, footnotes, floats, and section-based numbering.
- Use `#appendix[...]`; do not reset counters or type appendix numbers.

Article appendix sections remain level-two headings:

```typst
#appendix[
  == Data sources
  <sub:data_sources>
]
```

## Books

- Import `@local/latex-book:0.1.0` and apply `latex-book.with(...)`.
- Let the template own front matter, page-number phases, running heads, chapter
  openings, and chapter-based numbering.
- Split chapters with `#include` when useful.
- Use `#appendix[...]` for appendix numbering.
- Use `#chapter-bibliographies(read("references.bib", encoding: none))` for one
  bibliography per numbered chapter.

Book appendices remain inside the current chapter and use level-two headings:

```typst
#appendix[
  == Kuhn-Tucker conditions
  <sec:kuhn_tucker_conditions>
]
```

## Mutt slides

- Import `@local/mutt-slides:0.1.0` and apply `mutt-slides.with(...)`.
- Use level-one headings for agenda sections and level-two headings for slides.
- Prefer `card`, `callout`, `formula`, `small`, `theorem`, `solution`, `proof`,
  and grids over ad hoc boxes.
- Treat every slide as a hard frame. Shorten or split content before reducing
  type size; accept no overflow, clipping, collisions, or title-chip overlap.
- Supply figure captions for semantics and references even though the template
  hides them visually.

## Standalone artifacts

- Import `@local/standalone:0.1.0` and apply `standalone.with(...)`.
- Keep the source next to its assets and compile it independently.
- Import the resulting PDF so shared analytical content stays synchronized
  across document types.

## Figures and tables

- In articles and books, ordinary image and table figures float to the top by
  default so following text can use the remaining page. Omit `placement` for
  ordinary figures; an explicit `placement: auto` overrides this default. Use
  `placement: none` only when an object must remain at its source position.
  When anchored and floating objects are mixed, verify their rendered order
  and anchor a later dependent figure if needed.
- Use `latex-table` for compact Booktabs-style native tables and wrap it in a
  figure with `kind: table` when it needs a caption or reference.
- Use `subfigure-grid` when panels need individual references.
- Use the standalone template for reusable or complex figures and tables, then
  import the compiled PDF into articles, books, or slides.
- Diagnose blank space before adding page breaks or manual vertical spacing.

`latex-table` accepts one tuple for the header and one tuple per body row:

```typst
#latex-table(
  columns: (2fr, 1fr, 1fr),
  align: (left, right, right),
  header: ([Indicator], [2020], [2025]),
  rows: (
    ([Productivity], [100], [114]),
  ),
)
```

In standalone table sources, import it explicitly:

```typst
#import "@local/template-utils:0.1.0": latex-table
```
