# Typst document patterns

Read only the section for the selected document type or component. Consult the
corresponding template source only when the documented patterns do not expose a
needed parameter or behavior.

Keep appendix bodies flush with `#appendix[` in the source. Put
`// @typstyle off` immediately before the helper so Typstyle preserves that
layout, as shown in the examples below.

## Articles

- Import `@local/latex-article:0.1.0` and apply `latex-article.with(...)`.
- Let the template own page geometry, title matter, abstract width, typography,
  running heads, footnotes, floats, and section-based numbering.
- Set omitted optional fields such as `abstract`, `keywords`, `jel`,
  `author-note`, and `short-title` to `none`.
- Use `#appendix[...]`; do not reset counters or type appendix numbers.

Article appendix sections remain level-two headings:

```typst
// @typstyle off
#appendix[
== Appendix section
<sub:appendix_section>
]
```

## Books

- Import `@local/latex-book:0.1.0` and apply `latex-book.with(...)`.
- Let the template own front matter, page-number phases, running heads, chapter
  openings, and chapter-based numbering.
- Set omitted optional fields such as `subtitle`, `institution`, `department`,
  `logo`, `copyright`, `dedication`, and `preface` to `none`.
- Put a document-specific preface in an adjacent `preface.typ` or `prefacio.typ`
  file and pass it directly, for example `preface: include "preface.typ"`.
- Pass `index: true` after `preface` to append a localized alphabetical index
  after the body. When chapter bibliographies end the body, the index follows
  them. Mark entries using the index convention in `conventions.md`.
- Split chapters with `#include` when useful.
- Import `@local/latex-book:0.1.0` in every included chapter that uses its
  helpers. Imports in the entry point do not propagate through `#include`.
- Use `#appendix[...]` for appendix numbering.
- Use `#chapter-bibliographies(read("references.yml", encoding: none))` for one
  bibliography per numbered chapter.

Book appendices remain inside the current chapter and use level-two headings:

```typst
// @typstyle off
#appendix[
== Appendix section
<sec:appendix_section>
]
```

## Mutt slides

- Import `@local/mutt-slides:0.1.0` and apply `mutt-slides.with(...)`.
- Use level-one headings for agenda sections and level-two headings for slides.
- Use `#appendix[...]` with level-one appendix headings; do not type appendix
  letters into their titles.
- Appendix agenda entries and section chips use letters, and numbered objects
  use the corresponding `A.1`, `A.2`, `B.1`, and similar forms.
- Prefer `slide-subtitle`, `card`, `callout`, `formula`, `small`, `theorem`,
  `solution`, `proof`, and grids over ad hoc styling and boxes.
- Use native overlays for progressive content: `#pause` reveals following
  content, `#uncover("2-")[...]` preserves hidden layout space, and
  `#only("2")[...]` removes hidden content from the layout. Inside `grid`,
  `table`, or another function call, pass `pause,` as an argument.
- Treat every slide as a hard frame. Shorten or split content before reducing
  type size; accept no overflow, clipping, collisions, or title-chip overlap.
- Supply figure captions for semantics and references even though the template
  hides them visually.

```typst
// @typstyle off
#appendix[
= Appendix section

== Appendix slide
]
```

## Standalone artifacts

- Import `@local/standalone:0.1.0` and apply `standalone.with(...)`.
- Store each standalone source and its compiled PDF together in the consuming
  project: use `figures/` for figures and `tables/` for tables. Give the `.typ`
  and `.pdf` matching basenames.
- Compile every standalone entry point independently and write its PDF beside
  its source. Import that PDF from articles, books, and slides; do not include
  the standalone source or embed its CeTZ canvas directly.
- Give each panel in a multi-panel CeTZ figure its own `.typ` and `.pdf` pair.
  Panels may share drawing logic; import their PDFs into `subfigure-grid`.

## Figures and tables

- Put a `#figure(...)` label on the same source line as the call's closing
  parenthesis: `) <fig:sample>`. Use the corresponding prefix for figures with
  another `kind`, such as `) <tab:sample>` for a table.
- In articles and books, ordinary image and table figures float to the top by
  default so following text can use the remaining page. Omit `placement` for
  ordinary figures; an explicit `placement: auto` overrides this default. Use
  `placement: none` only when an object must remain at its source position.
  When anchored and floating objects are mixed, verify their rendered order
  and anchor a later dependent figure if needed.
- Use `latex-table` for compact rules-only native tables and wrap it in a
  figure with `kind: table` when it needs a caption or reference.
- When figures should appear side by side but retain separate numbers, captions,
  and references, put a grid inside one floating `place`. Set each child
  figure's `placement` to `auto` so it remains in its grid cell instead of
  inheriting the template's top placement. Label each child with `fig:` and do
  not add a parent caption.
- Use `subfigure-grid` when panels need individual references.
- For mixed-size subfigures, give the grid a shared `panel-height` and use
  `width: 100%`, `height: 100%`, and `fit: "contain"` on each image. This aligns
  the image bases and subcaptions without distorting their aspect ratios.
- Default imported analytical assets to PDF. Preserve deliberate panel
  proportions with explicit `columns` rather than forcing every panel to equal
  width.
- Use the standalone template for reusable or complex figures and tables, then
  import the compiled PDF into articles, books, or slides.
- Diagnose blank space before adding page breaks or manual vertical spacing.
- When preceding prose must stay before a figure, use `placement: none` and
  verify the affected page; automatic floating may otherwise move the figure.

Use independently numbered side-by-side figures when each image is a complete
figure rather than a panel of one combined figure:

```typst
#place(top, float: true)[
  #grid(
    columns: (1fr, 1fr),
    gutter: 1em,
    [#figure(
      image("first.pdf", width: 100%),
      placement: auto,
      caption: [First figure],
    ) <fig:first_figure>],
    [#figure(
      image("second.pdf", width: 100%),
      placement: auto,
      caption: [Second figure],
    ) <fig:second_figure>],
  )
]
```

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
