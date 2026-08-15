---
name: typst
description: >-
  Generate, edit, review, compile, and visually verify Typst articles, books,
  and Mutt slide decks using the local templates and conventions for source
  structure, typography, layout, numbering, figures, tables, equations,
  citations, and localization. Use for creating or modifying .typ documents,
  changing shared Typst templates, and resolving Typst layout or rendering
  problems.
---

# Typst

Write Typst through the shared local templates and established source patterns.
Preserve the template system, source conventions, and rendered quality instead
of treating a `.typ` file as isolated markup.

## Required context

Read [conventions.md](references/conventions.md) before editing Typst. It is the
authoritative core style for source structure, labels, math, citations, and
localization.

Read [document-patterns.md](references/document-patterns.md) when creating or
changing an article, book, slide deck, standalone artifact, figure, table,
float, title page, or appendix.

Template sources live under
`~/git-repos/private/dotfiles/typst/packages/local`. Change the document for
one-off behavior, the corresponding template for one document type, or
`template-utils` for behavior shared by articles, books, and slides.

## Workflow

### 1. Inspect

Inspect the target source, nearby `.typ` files, bibliography files, assets, and
the relevant local package. Classify the output as article, book, Mutt slides,
or standalone artifact. Never inspect generated PDFs as a substitute for
reading their Typst source.

Identify the document entry point before compiling. When editing an included
chapter, compile the enclosing `main.typ`, not the chapter in isolation.

### 2. Choose the right layer

- Put content and one-off exceptions in the document.
- Put behavior expected in every document of one type in that template.
- Put behavior shared by article, book, and slides in `template-utils`.

Make the smallest practical change at the correct layer. Do not restyle a
document locally to work around a template defect.

### 3. Write

Start from the canonical import and template call for the selected document
type. Follow the exact patterns in the applicable references, especially for
labels, numbered equations, theorem environments, figures, tables, citations,
appendices, and slide hierarchy.

Put all cited entries in the `.bib` file and resolve every missing key. Reuse
existing images or standalone Typst artifacts where practical.

### 4. Format and compile

Format changed Typst sources:

```bash
typstyle --inplace path/to/file.typ
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
pdftoppm -png -r 150 -f FIRST -l LAST /tmp/output.pdf /tmp/output
```

Open the relevant rendered pages and check:

- first-page proportions and title matter;
- line breaks, page breaks, and overall content flow;
- float placement and unexplained blank space;
- table scale and legibility;
- equation, figure, table, theorem, and appendix numbering;
- footnote rule, marker style, and wrapping;
- citations and unresolved bibliography entries;
- slide overflow, clipping, density, and visual hierarchy; and
- missing glyphs, warnings, broken links, or unresolved references.

For numbering changes, test references from later sections or chapters back to
earlier equations, figures, subfigures, and statements. Include an appendix
boundary and verify the displayed target numbers; successful compilation does
not prove that cross-reference numbers are correct.

For long documents, inspect every affected page plus representative unaffected
pages. For slides, inspect every changed slide. Fix defects and render again.

## Guardrails

- Do not replace the local templates with a preview package or a new visual
  system.
- Do not hard-code shared typography or numbering rules in individual documents.
- Do not use raw display math when an equation must be numbered.
- Do not use ordinary text reads for bibliography sources; use bytes.
- Do not leave semantic headings unlabeled in articles or books.
- Do not force floats with repeated page breaks or large manual spacing before
  diagnosing the underlying layout.
- Do not shrink slide text until dense content fits. Edit or split the content.
- Do not declare a document finished from compiler success alone.
