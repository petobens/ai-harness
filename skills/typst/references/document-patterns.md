# Typst document patterns

Read only the section for the selected document type or component. Consult the
corresponding template source only when the documented patterns do not expose a
needed parameter or behavior.

Keep appendix bodies flush with `#appendix[` in the source. Put
`// @typstyle off` immediately before the helper so Typstyle preserves that
layout, as shown in the examples below.

## Articles

- Import `@local/latex-article:0.1.0` and apply `latex-article.with(...)`.
- The default base size is `11pt`; override it with `font-size` only when needed.
  With `10pt` and `11pt` bases, body, small, and footnote roles adjust, and
  captions use the small role. Established title and heading sizes remain fixed.
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
- The default base size is `10pt`; override it with `font-size` only when needed.
  With `10pt` and `11pt` bases, body, small, and footnote roles adjust, and
  captions use the small role. Established cover, chapter, and section sizes
  remain fixed.
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
- The default base size is `14pt`; override it with `font-size` only when needed.
  Slide typography scales proportionally with the base size, so recheck every
  slide for overflow after changing it.
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
- Use native `table` for slide tables so they retain the slide template's table
  treatment. Use `latex-table` only when a rules-only table is intentional.

```typst
// @typstyle off
#appendix[
= Appendix section

== Appendix slide
]
```

## Standalone artifacts

- Import `@local/standalone:0.1.0` and apply `standalone.with(...)`.
- Keep the content-sized defaults `width: auto`, `margin: 3pt`, and `fill: none`.
  Set an explicit width only when the artifact needs a fixed canvas.
- In articles and books, default native Typst tables to standalone `.typ`
  sources imported as compiled PDFs, even when they could be written inline,
  unless the user requests an inline table.
- Store each standalone source and its compiled PDF together in the consuming
  project: use `figures/` for figures and `tables/` for tables. Give the `.typ`
  and `.pdf` matching basenames.
- Compile every standalone entry point independently and write its PDF beside
  its source. Import that PDF from articles, books, and slides; do not include
  the standalone source or embed its CeTZ canvas directly.
- Give each panel in a multi-panel CeTZ figure its own `.typ` and `.pdf` pair.
  Panels may share drawing logic; import their PDFs into `subfigure-grid`.
- Use filled double-chevron CeTZ arrowheads with `end: ">>"` and `fill: black`.
  Use `scale: 1.5` for axes and a smaller scale when a vector should be less
  prominent. Define the mark tuple once per canvas and reuse it.

## Floats

- Use `#figure` as the shared captioned container for images and tables. Pass
  `kind: table` when its content is a table.
- Put the label on the same source line as the `#figure(...)` call's closing
  parenthesis. Use `) <fig:sample>` for an image figure and `) <tab:sample>` for
  a table figure.
- Keep a `figure(...)` call on one line only when the entire call fits. When it
  spans multiple lines, put each argument on its own line. This convention is
  specific to figures; do not expand concise statement calls such as
  `#proof(title: [Custom proof])[...]` merely because they have a content body.
- In articles and books, ordinary image and table figures float to the top by
  default so following text can use the remaining page. Omit `placement`; an
  explicit `placement: auto` overrides this default. Use `placement: none` only
  when content must remain at its source position, such as when preceding prose
  must stay before it, and verify the affected page. When anchored and floating
  objects are mixed, verify their rendered order and anchor a later dependent
  figure if needed.
- Build reusable or complex figure and table content as a standalone `.typ`
  source, compile it to a matching PDF, and import the PDF into `#figure` in the
  consuming document.
- Diagnose blank space before adding page breaks or manual vertical spacing.

### Figures and subfigures

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

### Tables

- Default rules-only native tables to `latex-table`. In articles and books,
  normally put the helper in a standalone source as described above. It owns
  the standard table styling, including the top, header, and bottom rules.
- Pass `table.cell` and `table.hline` entries through `latex-table`'s `header`
  tuple for grouped headers, spanning cells, and partial header rules. Use raw
  `table` only when the desired structure or rule treatment does not fit the
  helper.
- In `latex-table`, put each logical body row in its own tuple inside `rows`.
  The helper flattens those row tuples into the cell stream expected by native
  Typst. In raw `table`, pass cells directly; the declared column count
  determines the row boundaries.
- Use `auto` columns for content-sized standalone tables. Use `fr` columns only
  when deliberately distributing a fixed or otherwise constrained width.

`latex-table` accepts one tuple for the header and one tuple per body row:

```typst
#latex-table(
  columns: (auto, auto, auto),
  align: (left, right, right),
  header: ([Header 1], [Header 2], [Header 3]),
  rows: (
    ([Value 1], [Value 2], [Value 3]),
    ([Value 4], [Value 5], [Value 6]),
  ),
)
```

In standalone table sources, import it explicitly:

```typst
#import "@local/template-utils:0.1.0": latex-table
```
