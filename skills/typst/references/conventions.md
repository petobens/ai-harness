# Typst conventions

Use these rules for all Typst work unless the target project explicitly
overrides them.

## Contents

- [Document families](#document-families)
- [Source style](#source-style)
- [Structure and labels](#structure-and-labels)
- [Paragraph indentation](#paragraph-indentation)
- [Lists](#lists)
- [Code](#code)
- [Math symbols](#math-symbols)
- [Equations](#equations)
- [Statements and proofs](#statements-and-proofs)
- [Citations and bibliography](#citations-and-bibliography)
- [Indexes](#indexes)

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

- Keep every wrappable source line at or below 80 columns and run
  `typstyle --line-width 80 --wrap-text=fill` rather than aligning or wrapping
  Typst by hand. Reflow prose by paragraph, keeping inline references and
  citations with their sentence whenever they fit. Typstyle does not always
  reflow across these content nodes, so correct awkward breaks manually.
- Use content blocks for formatted document content and strings for plain
  metadata or file paths, following the template signatures and examples.
- Pass `none` to omit an optional template field or section. Do not use an
  empty string or empty content block as the control signal, even when a
  template tolerates those values.
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

== Methods
<sub:methods>

=== Implementation details
<ssub:implementation_details>

// Book
= Chapter heading
<cha:chapter_heading>

== Section heading
<sec:section_heading>

=== Subsection heading
<sub:subsection_heading>
```

Whenever a heading has a label, always leave one blank line after it before the
following text or other content. This applies to articles, books, and slides:

```typst
= Chapter heading
<cha:chapter_heading>

The chapter text starts here.
```

Use lowercase snake case derived from the title or caption. Never use generic
labels such as `<sec:name>` or `<eq:label>` in finished work.

Use a semantic heading with `numbering: none` when a structural heading should
be unnumbered. Do not simulate it with styled paragraph text. Keep the level and
label prefix appropriate for the document family:

```typst
// Article subsubsection
#heading(level: 3, numbering: none)[Additional details]
<ssub:additional_details>

// Book subsection
#heading(level: 3, numbering: none)[Supplementary material]
<sub:supplementary_material>
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

Reference labels directly, for example `@sec:methods`, `@fig:overview`, and
`@eq:linear_relation`. Use `#ref(<sec:methods>, form: "page")` for a page
reference.

Slide-local labels may instead use a descriptive `slide-...` name, as in
`<slide-overview>`, when section-based document labels add no value.

## Paragraph indentation

Typst does not indent a paragraph immediately after a block when
`par.first-line-indent.all` is `false`, even when a blank source line makes
the following prose a new paragraph. When a display equation, anchored figure,
or other block is followed by a genuinely new paragraph, restore the template
indent before the blank line:

```typst
$
  x + y = z
$
#restore-paragraph-indent

This is a new paragraph.
```

Do not restore the indent when the following prose continues the same paragraph.
Statement and proof helpers already restore it automatically.

## Lists

Use native `+` and `-` markup for numbered and bulleted lists. Do not wrap a
list in `#block` merely to scope a set rule; the extra block changes its
surrounding vertical spacing.

Scope custom numbering in a content block so it does not affect later lists:

```typst
#[
  #set enum(numbering: "(i)", spacing: 1em)
  + First property.

  + Second property.
]
```

Change `numbering` to any Typst numbering pattern, such as `"(a)"`, `"a)"`, or
`"1."`. In markup lists, a blank line between items makes the list non-tight and
allows `spacing` to control the gap. Omit the blank lines for a compact list, and
verify the result in the rendered page.

Scope custom bullet markers in the same way:

```typst
#[
  #set list(marker: [–], spacing: 1em)
  - First property.

  - Second property.
]
```

Use `wide-enum` for a compact numbered list whose wrapped lines return to the
text margin instead of hanging under the item body:

```typst
#wide-enum(numbering: "(i)")[
  + First property with a long explanation.
  + Second property.
]
```

The helper aligns markers in a fixed-width label column. Override `label-width`,
`body-indent`, `above`, or `spacing` only when the rendered list needs it.

For named, run-in labels, use `labeled-item`. It inserts a blank line above the
item, emphasizes the label, indents only the first line, and lets continuation
lines return to the text margin:

```typst
#labeled-item[First case][
  First explanation.
]

#labeled-item[Second case][
  Second explanation.
]
```

## Code

Use native raw syntax for code. Enclose inline code in single backticks and use
a fenced block with a language tag for syntax-highlighted code:

````typst
Use `add` for a short inline reference.

```python
def add(x, y):
    return x + y
```
````

Let the document template own the font, syntax theme, border, padding, and
width. Do not add local raw-text styling. Code blocks inherit the surrounding
background and span the available content width in articles, books, and Mutt
slides. `standalone` is reserved for figures and tables, not code-block
documents.

## Math symbols

Write ordinary math punctuation and delimiters directly. Use `x, y` and
`u(x, y)`, not `x\,y` or `u\(x\,y\)`. Reserve an escape for a character that
must remain literal, such as deliberately non-scaling grouping or the
mismatched delimiters in a half-open interval: `$x in\(0, 1\]$`. Do not remove
such escapes mechanically.

Put spaces around binary operators and relations, after commas, and between
adjacent multiplicative factors. Write `$x + y$`, `$f(x) gt.eq g(x)$`,
`$nabla f(x) dot.op v$`, `$alpha (x + y)$`, and `$(1 - alpha) y$`. Keep spaces
inside set braces, as in `$min { f(x), f(y) }$`.

Group compound scripts with parentheses. A leading number may join the
following letter, as in `$x_(1i)$`. Separate adjacent letter-led symbols so
Typst does not parse them as an undefined identifier, as in `$omega_(n i)$`
and `$omega_(n 1)$`. Do not write `$omega_1i$`, which leaves `i` on the
baseline.

Do not insert a space between an unadorned function and its argument: write
`$f(x)$`, `$log(x)$`, and named functions such as `$pi(r)$`. A scripted
function is a parsing exception: write `$g_k (x)$` or `$u_i (x_(1i), x_(2i))$`.
Without the space, Typst parses the parenthesized expression as part of the
script. Conversely, write `$alpha (x)$`, not `$alpha(x)$`, when `alpha` is a
scalar multiplying a group. The latter parses as a function call and therefore
receives function syntax highlighting. The same distinction applies after a
styled or scripted factor: write `$tilde(beta)^t (1 + gamma)$` for
multiplication.

Relations followed by delimiters also need a space. Write `$x in (0, 1)$`,
`$x in [0, 1]$`, and `$x_n lt.eq (w\/p_n)$`, not `in(0, 1)`, `in[0, 1]`, or
`lt.eq(w\/p_n)`. Without the space the relation parses as a call, which can
change its rendering as well as its highlighting.

Use quoted strings for ordinary text inside math, as in `$x "para todo" y$`.
Reserve `upright(...)` for mathematical letters that need a non-italic variant,
such as `$upright(d) x$`. When a short phrase must remain unbroken, wrap it in a
box, as in `#box[$"con igualdad si"$]`. Do not box ordinary math text
unnecessarily because the box prevents line breaking.

Use `arrow.l.r.double.long` for displayed logical equivalence and `notsuccsim`
for its dedicated negated relation. For other relations without a matching
glyph, cancel only the relation and restore its math class; do not cancel the
operands.

```typst
$
  P arrow.l.r.double.long Q quad x notsuccsim y
$
```

## Equations

Raw display math is intentionally unnumbered in articles and books:

```typst
$
  f(x) = x^2 + 1
$
```

Put the opening delimiter, formula, and closing delimiter on separate source
lines for every standalone display, even when the rendered formula fits on one
line. Reserve same-line `$...$` delimiters for inline math in prose.

Within those delimiters, keep the formula on one source line when its indented
line fits within the source-width limit. Otherwise break at logical boundaries
with ordinary newlines, which do not affect the rendered equation. Never insert
`\` merely to wrap the source. Indent a source-only continuation by two spaces
relative to the first line of its rendered row. Keep nested function arguments
at their structural indentation.

Use `\` only for an intentional rendered row break, always preceded by a space.
Return the next rendered row to the base indentation. If Typstyle rewrites an
intentional source layout, put `// @typstyle off` immediately before the math
node; the directive affects formatting, not rendering.

```typst
$
  a & = b + c + d +
    e + f \
  x & = y,
    #h(2em) x > 0
$
```

Keep each formula on one rendered line unless it approaches the text width or
a multiline layout materially improves readability. Break at a meaningful
operator, keep closely related terms together, and use `&` to align the
continuation:

```typst
$
  f(x) &= a_0 + a_1 x + a_2 x^2 \
  &quad + a_3 x^3 + a_4 x^4
$
```

Use `#equation(...)` when numbering is required. Put every numbered display
equation on its own source line; never append `#equation` to a prose sentence
or list item. Do not add blank lines around it merely for separation:

```typst
The numbered relation is
#equation($
  y = a x + b
$) <eq:linear_relation>
The discussion continues here.
```

Do not type equation numbers manually. The templates handle section-aware,
chapter-aware, slide-aware, and appendix-aware numbering and cross-references.

## Statements and proofs

Use the exported semantic statement helpers:

```typst
#theorem(
  note: [Even sum],
)[
  The sum of two even integers is even.
] <thm:even_sum>

#proof[
  Let $a = 2m$ and $b = 2n$. Then $a + b = 2(m + n)$, so $a + b$ is even.
]
```

Available helpers are `theorem`, `proposition`, `lemma`, `corollary`,
`definition`, `example`, `exercise`, `remark`, `notation`, `solution`, and
`proof`. Choose numbering per occurrence: pass `numbered: false` for an
unnumbered remark, notation, or other statement instead of changing the
template default. Use `title:` only to replace the localized statement name;
use `note:` for a parenthetical statement title.

Leave one blank source line after every statement helper before the next
paragraph, statement, or proof. In particular, never place `#proof` directly
after the closing line of a theorem, proposition, lemma, or corollary. Keep the
blank line after the statement's label when it has one, as shown above.

Continue a previously numbered example without incrementing its counter:

```typst
#continued-example(<exa:sample_calculation>)[
  The same example continues here.
]
```

## Citations and bibliography

Prefer Hayagriva YAML (`.yml` or `.yaml`) for new bibliography sources. Preserve
an existing BibLaTeX or BibTeX (`.bib`) source unless conversion is requested.
Use citation keys from the project's existing bibliography source:

```typst
@doe24
#cite(<doe24>, form: "prose")
#cite(<doe24>, form: "full")
```

The templates color citations navy. When a citation has a textual supplement,
restore the normal text color explicitly so only the bibliographic citation is
highlighted. The supplement remains part of the citation link:

```typst
#cite(
  <doe24>,
  form: "prose",
  supplement: text(fill: black)[Theorem 2],
)
```

Every cited key must exist. Fix missing keys in the document's bibliography
data, not in the template.

Read bibliography sources as bytes, matching the shared template API. This
example uses Hayagriva YAML; a `.bib` source uses the same pattern:

```typst
#bibliography(
  read("references.yml", encoding: none),
  title: localized([Referencias], [References]),
)
```

## Indexes

Only add index markers when an index is requested. To include a selected term,
put an invisible index marker immediately after the visible term:

```typst
A selected term#index("selected term") appears in the text.
```

Pass a plain string as the index key. Do not put the visible term inside
`#index[...]`: the marker does not render its argument. Repeat the marker at
each page that should appear under the entry.
