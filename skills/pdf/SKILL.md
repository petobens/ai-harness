---
name: pdf
description: >-
    Read a PDF and answer questions about its contents, whether the PDF is a
    local file or lives in Google Drive. Use when the user wants to read,
    inspect, extract from, or summarize a PDF. For a Drive PDF, download it
    first (delegating discovery to the gdrive skill), then read it.
metadata:
    short-description: Read local or Google Drive PDFs
    category: productivity
    requires:
        bins:
            - gws
            - pdftotext
            - pdfinfo
            - pdftoppm
---

<!-- markdownlint-disable MD013 -->

# PDF

How you read a PDF depends on which agent is running this skill. Claude Code has
a native file reader that parses and renders PDFs directly; Codex does not, and
pointing its file read at a PDF yields raw bytes, not text. So detect the agent
first, then use the matching path. Both paths reach the same content.

## Detect the agent

You already know which agent you are; pick the path by identity:

- **Claude** (Claude Code): use the native read path.
- **Codex** or any other agent: use the CLI path.

If you are genuinely unsure, confirm from the environment: `CLAUDECODE` is set
under Claude Code, and `CODEX_*` variables are set under Codex.

```bash
if [ -n "$CLAUDECODE" ]; then
    echo claude
elif env | grep -q '^CODEX_'; then
    echo codex
else echo unknown; fi
```

When it is still unknown, use the CLI path; it works everywhere.

## Rules

- When reading a PDF, keep the content in agent context and return only a brief
  confirmation (file name/ID, page count, and where it lives) by default. Do not
  paste the full extraction or a summary unless the user explicitly asks.
- Accept Drive URLs or IDs for Drive PDFs; always pass the bare file ID to `gws`
  (the segment after `/d/`).
- Always report the page count and which pages you actually read.

## Reading a local PDF

### Claude: native read

Read the file directly with the built-in Read tool, which parses and visually
renders PDFs (including scanned/image pages, tables, and logos). Pass an
absolute path and, for anything beyond a short file, a `pages` range (e.g.
`"1-5"`); read long PDFs in windows of at most 20 pages.

### Codex (or unknown): CLI

1. Page count and validity:

   ```bash
   pdfinfo FILE.pdf | grep -E '^(Pages|Page size):'
   ```

2. Extract the text layer to stdout. `-layout` preserves columns and tables,
   which matters for invoices and reports. For long PDFs, read a page window
   with `-f` (first) and `-l` (last):

   ```bash
   pdftotext -layout FILE.pdf -            # whole file
   pdftotext -layout -f 1 -l 10 FILE.pdf - # pages 1-10
   ```

3. If `pdftotext` returns little or no text (an image-only or scanned PDF),
   render pages to PNGs at 150 DPI and view them if the agent can accept image
   input:

   ```bash
   pdftoppm -png -r 150 -f 1 -l 5 FILE.pdf ./pdf-page
   # produces ./pdf-page-1.png, ./pdf-page-2.png, ...
   ```

   If the agent cannot view images and there is no text layer, say so rather
   than guessing; no OCR tool is wired into this skill.

4. Remove any PNGs you rendered when done unless the user wants to keep them.

## Reading a Google Drive PDF

A Drive PDF is a binary blob; download the bytes, then read the local copy using
the agent-appropriate path above.

1. Find the file with the `gdrive` skill if you only have a name. Confirm its
   `mimeType` is `application/pdf`.
2. Download the bytes to the current working directory. `gws`'s `-o` must
   resolve **inside the current directory** — it rejects `/tmp` and other
   outside paths, so use a relative path:

   ```bash
   gws drive files get \
       --params '{"fileId":"FILE_ID","alt":"media","supportsAllDrives":true}' \
       -o ./FILE_NAME.pdf
   ```

   A success response is JSON with `"status":"success"` and the resolved
   `saved_file` path. In a restricted sandbox, a DNS/discovery/network error
   means rerun with escalated tool permissions, not a real failure.

3. Read the downloaded file (see _Reading a local PDF_).
4. Remove the downloaded PDF (and any rendered PNGs) when done unless the user
   wants to keep them.
