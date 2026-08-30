---
name: typst
description: >-
  Generates, edits, reviews, compiles, and visually verifies Typst academic
  articles, Muttdata articles, books, Muttdata slide decks, and standalone
  artifacts using the local templates and conventions for source structure,
  typography, layout, numbering, figures, tables, equations, citations, indexes,
  and localization.
  Use for creating or modifying .typ documents, resolving document layout or
  rendering problems, and fixing shared templates when a defect belongs there.
---

# Typst

Write Typst through the shared local templates and established source patterns.
Treat the templates as finished document infrastructure: use their semantic
APIs and conventions instead of recreating typography or layout locally.

## Required context

Read [conventions.md](references/conventions.md) before editing Typst. It is the
authoritative core style for source structure, labels, math, citations, indexes,
and localization.

Read [document-patterns.md](references/document-patterns.md) when creating or
changing an article, book, slide deck, standalone artifact, figure, table,
float, title page, or appendix.

## Workflow

### 1. Inspect

Inspect the target source, nearby `.typ` files, bibliography files, assets, and
relevant rendered output. Read the source first; use the rendered PDF for
visual verification.

Identify the document as an academic article, Muttdata article, book, Muttdata
slide deck, or standalone artifact. Identify its entry point before compiling.
When editing an included chapter, compile the enclosing `main.typ`, not the
chapter in isolation.

### 2. Use the template API

Use the canonical template call and its semantic helpers. Keep content and true
one-off exceptions in the document. Do not add local `set` or `show` rules for
behavior the template already owns.

If a shared default is genuinely defective, template sources live under
`~/git-repos/private/dotfiles/typst/packages/local`. Change the corresponding
document template for type-specific behavior or `template-utils` for behavior
shared by document families. Do not restyle one document to work around a
template defect.

### 3. Write

Start from the canonical import and template call for the selected document
type. Follow the exact patterns in the applicable references, especially for
labels, numbered equations, statement helpers, figures, tables, citations,
indexes, appendices, and slide hierarchy.

Prefer Hayagriva YAML (`.yml` or `.yaml`) for new bibliography sources. Preserve
an existing `.bib` source unless conversion is requested. Put every cited entry
in the bibliography source and resolve every missing key. Reuse existing images
or standalone Typst artifacts where practical.

### 4. Format and compile

Format changed Typst sources:

```bash
typstyle --line-width 80 --wrap-text=fill --inplace path/to/file.typ
```

Compile from the project root. Supply `--root` whenever the source imports or
reads files outside its own directory:

```bash
typst compile --root PROJECT_ROOT source.typ /tmp/output.pdf
```

Compile every affected entry point. A successful compile is necessary but not
sufficient.

### 5. Verify the render

Inspect structure and geometry:

```bash
pdfinfo /tmp/output.pdf
pdftotext -layout /tmp/output.pdf /tmp/output.txt
qpdf --json --json-key=outlines /tmp/output.pdf
pdftoppm -png -r 150 -f FIRST -l LAST /tmp/output.pdf /tmp/output
```

Open the relevant rendered pages and check:

- first-page proportions and title matter;
- semantic heading hierarchy, including intentionally unnumbered headings;
- line breaks, page breaks, and overall content flow;
- list numbering, indentation, item spacing, and surrounding separation;
- float placement and unexplained blank space;
- subfigure order, alignment, captions, and individual references;
- table scale and legibility;
- equation, figure, table, theorem, and appendix numbering;
- PDF outline completeness, hierarchy, titles, and page destinations;
- footnote rule, marker style, and wrapping;
- citations and unresolved bibliography entries;
- slide overflow, clipping, density, and visual hierarchy; and
- missing glyphs, warnings, broken links, or unresolved references.

For numbering changes, test references from later sections or chapters back to
earlier equations, figures, subfigures, and statements. Include an appendix
boundary and verify the displayed target numbers; successful compilation does
not prove that cross-reference numbers are correct.

For long documents, inspect every affected page plus representative unaffected
pages. For slides, inspect every changed slide and every overlay state; confirm
that fixed layouts and logical slide numbering remain stable. Fix defects and
render again.

## Guardrails

- Do not replace the local templates with a preview package or a new visual
  system.
- Do not hard-code shared typography or numbering rules in individual documents.
- Do not use raw display math when an equation must be numbered.
- Follow the document-family bibliography source patterns in
  `references/conventions.md`; Retrofit backreferences and book chapter
  bibliographies resolve project files differently.
- Do not leave semantic headings unlabeled in articles or books.
- Do not force floats with repeated page breaks or large manual spacing before
  diagnosing the underlying layout.
- Do not shrink slide text until dense content fits. Edit or split the content.
- Do not declare a document finished from compiler success alone.
