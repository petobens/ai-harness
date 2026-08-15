# Typst conventions

Use these rules for all Typst work unless the target project explicitly
overrides them.

## Contents

- [Document families](#document-families)
- [Source style](#source-style)
- [Structure and labels](#structure-and-labels)
- [Equations](#equations)
- [Statements and proofs](#statements-and-proofs)
- [Citations and bibliography](#citations-and-bibliography)

## Document families

Choose one canonical local package:

```typst
#import "@local/latex-article:0.1.0": *
#import "@local/latex-book:0.1.0": *
#import "@local/mutt-slides:0.1.0": *
#import "@local/standalone:0.1.0": *
```

- `latex-article`: papers and article-like assignments.
- `latex-book`: books, notes, and long chaptered documents.
- `mutt-slides`: branded 16:9 Muttdata presentations.
- `standalone`: tightly cropped figures and tables reused as PDF assets.

Pass `language: "es"` or `language: "en"` to the template. This controls
hyphenation, localized names, dates, and theorem titles. Use
`localized([Texto], [Text])` for bilingual content.

## Source style

- Run `typstyle` rather than aligning or wrapping Typst by hand.
- Use content blocks for formatted document content and strings for plain
  metadata or file paths, following the template signatures and examples.
- Separate prose paragraphs with one blank line. Do not use manual line breaks
  to control paragraph wrapping.
- Prefer semantic template helpers over local `set` and `show` rules.
- Keep comments rare and explain only non-obvious implementation constraints.

## Structure and labels

Articles and books label every semantic heading on the following line. Their
heading levels differ:

```typst
// Article
= Introduction
<sec:introduction>

== Policy implications
<sub:policy_implications>

=== Identification assumptions
<ssub:identification_assumptions>

// Book
= Consumer theory
<cha:consumer_theory>

== Preferences
<sec:preferences>

=== Utility representations
<sub:utility_representations>
```

Use lowercase snake case derived from the title or caption. Never use generic
labels such as `<sec:name>` or `<eq:label>` in finished work.

Use a semantic heading with `numbering: none` when a structural heading should
be unnumbered. Do not simulate it with styled paragraph text. Keep the level and
label prefix appropriate for the document family:

```typst
// Article subsubsection
#heading(level: 3, numbering: none)[Identification assumptions]
<ssub:identification_assumptions>

// Book subsection
#heading(level: 3, numbering: none)[Pure exchange economy]
<sub:pure_exchange_economy>
```

Use these prefixes consistently in articles and books:

| Object        | Prefix  |
| ------------- | ------- |
| Chapter       | `cha:`  |
| Section       | `sec:`  |
| Subsection    | `sub:`  |
| Subsubsection | `ssub:` |
| Figure        | `fig:`  |
| Subfigure     | `sfig:` |
| Table         | `tab:`  |
| Equation      | `eq:`   |
| Theorem       | `thm:`  |
| Proposition   | `pro:`  |
| Lemma         | `lem:`  |
| Corollary     | `cor:`  |
| Definition    | `def:`  |
| Example       | `exa:`  |
| Exercise      | `exe:`  |
| Remark        | `rem:`  |

Reference labels directly, for example `@sec:model`, `@fig:transition`, and
`@eq:production`. Use `#ref(<sec:model>, form: "page")` for a page reference.

Slide-local labels may instead use a descriptive `slide-...` name, as in
`<slide-production>`, when section-based document labels add no value.

## Equations

Raw display math is intentionally unnumbered in articles and books. Use the
template helpers when numbering is required:

```typst
#equation(
  $
    Y_t = K_t^alpha (A_t L_t)^(1 - alpha)
  $,
) <eq:production>

#uequation(
  $
    k^* = (s / (n + g + delta))^(1 / (1 - alpha))
  $,
)
```

Do not type equation numbers manually. The templates handle section-aware,
chapter-aware, slide-aware, and appendix-aware numbering and cross-references.

## Statements and proofs

Use the exported semantic environments:

```typst
#theorem(
  note: [Conditional convergence],
)[
  The economy converges to its steady state.
] <thm:conditional_convergence>

#proof[
  Investment is concave and break-even investment is linear.
]
```

Available environments are `theorem`, `proposition`, `lemma`, `corollary`,
`definition`, `example`, `exercise`, `remark`, `notation`, `solution`, and
`proof`. Choose numbering per occurrence: pass `numbered: false` for an
unnumbered remark, notation, or other statement instead of changing the
template default. Use `title:` only to replace the localized environment name;
use `note:` for a parenthetical statement title.

## Citations and bibliography

Use citation keys from the project's `.bib` file:

```typst
@kydland82
#cite(<kydland82>, form: "prose")
#cite(<kydland82>, form: "full")
```

Every cited key must exist. Fix missing keys in the document's bibliography
data, not in the template.

Read bibliography sources as bytes, matching the shared template API:

```typst
#bibliography(
  read("references.bib", encoding: none),
  title: localized([Referencias], [References]),
)
```
