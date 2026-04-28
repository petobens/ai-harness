---
name: gdocs-write
description: >-
    Create, manage, and write Google Docs with gws. Use when the user asks to
    draft or update a Google Doc, preserve or reproduce formatting, or produce
    a polished document from prose/Markdown.
metadata:
    short-description: Write and manage Google Docs with gws
    category: productivity
    requires:
        bins:
            - gws
---

# Google Docs Writer

Use `gws` to create and modify Google Docs, with care for structure,
formatting, and final polish.

## Rules

- Confirm only before creating a new doc, trashing/deleting a doc, or making
  the first substantive edit after creating a doc. Do not ask for extra
  permission before normal edits to an existing doc.
- Do not ask the user for task-level permission before safe local prep work,
  such as writing request JSON to `/tmp`, running `--dry-run`, or inspecting a
  doc. If the execution environment requires a sandbox approval for those
  commands, request it as a tool permission only; do not present it as a
  product/workflow confirmation.
- Use `--dry-run` to validate request bodies locally before sending risky or
  layout-sensitive writes (supported on `batchUpdate` and other write methods).
- Make the smallest safe change that achieves the user's goal.
- Always apply the default document format when creating or substantially
  rewriting a doc, unless the user explicitly asks for a different style.
- Preserve existing structure and rich-text styling for small edits to existing
  docs unless the user asks for a redesign.
- Inspect the doc before layout-sensitive edits, and again before reporting
  done. Fix shifted ranges, missing styles, or formatting drift.
- For destructive edits or large rewrites, prefer copying the doc first and
  writing to the copy.
- For rename/trash, confirm the file is a Google Doc MIME type.
- Accept Google Docs URLs or IDs from the user; always pass the bare ID to
  `gws`.
- Use `gws schema docs.documents.METHOD` or `gws docs --help` when unsure
  about params, request bodies, or supported commands.
- Report final title, ID, URL, and operations performed.

## Commands

```bash
# Create blank doc; content in create requests is ignored by the API
gws docs documents create --json '{"title":"Document title"}'

# Copy
gws drive files copy \
    --params '{"fileId":"DOC_ID","supportsAllDrives":true}' \
    --json '{"name":"Copied document title"}'

# Rename
gws drive files update \
    --params '{"fileId":"DOC_ID","supportsAllDrives":true}' \
    --json '{"name":"New document title"}'

# Trash
gws drive files update \
    --params '{"fileId":"DOC_ID","supportsAllDrives":true}' \
    --json '{"trashed":true}'

# Read / inspect
gws docs documents get --params '{"documentId":"DOC_ID"}'

# Plain append (text only, no formatting)
gws docs +write --document DOC_ID --text 'Text to append'
```

For non-trivial JSON bodies, write `/tmp/gdoc-requests.json` and pass it with
`--json "$(cat /tmp/gdoc-requests.json)"` to avoid shell quoting mistakes.

## Rich Document Write

Use `documents.batchUpdate` for anything beyond plain append. Requests are
validated and applied atomically: if one is invalid, none apply.

Insert all text first, then style. `insertText` shifts every downstream index,
so doing inserts and styling in the same pass is error-prone.

1. Compose one text string and `insertText` it at index `1`.
2. Track UTF-16 start/end indexes for titles, metadata, headings, paragraphs,
   and links.
3. Apply `updateParagraphStyle`, `updateTextStyle`, `createParagraphBullets`,
   and `updateTextStyle.link` over exact ranges.
4. Use narrow `fields`, e.g. `bold,fontSize,foregroundColor,weightedFontFamily`.
5. Separate consecutive body paragraphs with exactly one blank line in the
   source text. Do not insert blank lines before or after section and
   subsection headings; use paragraph spacing for those transitions.
6. Include intentional trailing newlines, but avoid styling accidental blank
   lines.

`createParagraphBullets` requires a `bulletPreset` enum, e.g.
`BULLET_DISC_CIRCLE_SQUARE` or `NUMBERED_DECIMAL_ALPHA_ROMAN`.

Minimal example — insert a heading and one bullet:

```json
{
    "requests": [
        {
            "insertText": {
                "location": {
                    "index": 1
                },
                "text": "Heading\nFirst point\n"
            }
        },
        {
            "updateParagraphStyle": {
                "range": {
                    "startIndex": 1,
                    "endIndex": 9
                },
                "paragraphStyle": {
                    "namedStyleType": "HEADING_1"
                },
                "fields": "namedStyleType"
            }
        },
        {
            "createParagraphBullets": {
                "range": {
                    "startIndex": 9,
                    "endIndex": 21
                },
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
            }
        }
    ]
}
```

```bash
gws docs documents batchUpdate \
    --params '{"documentId":"DOC_ID"}' \
    --json "$(cat /tmp/gdoc-requests.json)"
```

## Default Document Format

Default structure and styling for polished long-form documents (memos, RFCs,
internal write-ups). Always apply this format when creating a new doc from
scratch or substantially rewriting a doc, unless the user explicitly asks for a
different style. Do not impose on third-party documents or small edits to an
existing doc with its own style.

Structure:

- **Main title:** Google Docs `TITLE` named style, large blue bold title, e.g.
  `Some Big Title`. Place the subtitle on the line directly below the title
  with no blank line between them.
- **Subtitle:** blue subtitle, immediately below the title (no blank line
  separating them).
- **Metadata block:** required DM Mono lines in this exact order: date,
  authors, audience, revised date. Each field goes on its own line using these
  labels: `Date: ...`, `Authors: ...`, `Audience: ...`, `Revised date: ...`;
  never combine multiple fields on one line.
- **Section headings:** Google Docs `HEADING_2` named style, numbered, e.g.
  `1. A first section`, not bold. Do not insert a blank line between a section
  heading and the paragraph that follows it, or between the previous paragraph
  and the section heading; paragraph spacing provides the visual separation.
- **Subsection headings:** Google Docs `HEADING_3` named style, numbered, e.g.
  `1.1 A subsection`, smaller than section headings, not bold. Same rule: no
  blank line before or after the subsection heading.
- **Body text:** normal black prose, justified alignment, with generous line
  and paragraph spacing.
- **Links:** blue underlined linked text, not raw URLs when possible.
- **Appendix:** optional lettered heading, e.g. `A. An appendix`.

Only the main title uses Title Case. Subtitles, section headings, subsection
headings, and appendix headings use sentence case.

Defaults:

- Title: `TITLE` named style, 26 pt, bold, DM Sans, `#0045fb`, compact 1.0
  line spacing, with minimal paragraph spacing after.
- Subtitle: 17 pt, DM Sans, `#0045fb`. No blank line between title and
  subtitle in the source text. Use compact 1.0 line spacing with minimal
  paragraph spacing after, so there is exactly one visual line of space before
  the metadata block.
- Metadata: 11 pt, DM Mono, black. One field per line, compact spacing
  between metadata lines. Use minimal paragraph spacing after the last metadata
  line so there is exactly one visual line of space before the first section
  heading.
- Section headings: `HEADING_2` named style, 16 pt, normal weight, DM Sans,
  `#0805ac`, paragraph spacing before and after. No blank line between the
  heading and the following paragraph in the source text.
- Subsection headings: `HEADING_3` named style, 14 pt, normal weight, DM Sans,
  `#0805ac`. No blank line between the heading and the following paragraph in
  the source text.
- Body: 11 pt, DM Sans, black, normal weight, 1.25 line spacing, and
  `alignment: JUSTIFIED` on every body paragraph (set via
  `updateParagraphStyle` with `fields` including
  `alignment,lineSpacing,spaceBelow,spacingMode`). Use `spaceBelow: 0pt` for
  prose paragraphs when the source text already has one blank line between
  paragraphs.
- Links: blue, underline, with `link.url` set.
- Paragraph spacing: exactly one blank line between consecutive body
  paragraphs in source text; avoid multiple blank lines and do not add extra
  paragraph spacing on top of those blank lines. Do not place blank lines
  before or after headings, or between title and subtitle.
- Page margins: use 1.25 inch left and right margins, with Google Docs default
  1 inch top and bottom margins. This keeps body prose closer to 11-14 words
  per line without making the title block feel cramped.

When styling a new or substantially rewritten doc, set `namedStyleType` on the
paragraphs as well as the explicit visual styling: `TITLE` for the main title,
`HEADING_2` for top-level numbered sections, and `HEADING_3` for numbered
subsections. Do not use `HEADING_1` for ordinary document sections unless the
user explicitly asks for it.
