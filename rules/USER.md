# Context for AI Agents

This file contains durable context about me, my preferences, and how I like to
work. Read it before starting work.

## About Me

- I'm Pedro.
- I live in Buenos Aires, Argentina.
- I use Arch Linux and Neovim.
- I have a background in Economics.
- I'm the Co-Founder and COO of Muttdata, a Data + AI services company.

## Work Environment

The desktop is Hyprland on Wayland. X11 tools such as `xdotool`, `xclip`, and
`scrot` are not installed.

- Sandboxing can block access to Hyprland's local control socket. If a read-only
  `hyprctl` query fails with a socket error, retry with expanded permissions
  before concluding that the running session is unavailable.
- When a package or plugin lookup reports a DNS or network failure, treat any
  subsequent "not found" output as inconclusive. Retry with network access when
  available; otherwise report that the lookup could not be verified.

### Command-Line Tools

Many command-line tools are installed. This list is not exhaustive; it only
highlights tools that are easy to overlook or that differ from common defaults.
Use them when they fit the task:

- `ast-grep` searches and rewrites code by its syntax tree. Prefer it over `rg`
  and `sed` when formatting varies, such as calls split across lines, or for
  renames across many files.
- `grim` (with `slurp` to select a region) takes screenshots, and `wl-copy` and
  `wl-paste` access the clipboard.
- `hyperfine` benchmarks commands.
- `ouch` compresses and extracts most archive formats.
- `pdftotext`, `pdfinfo` (poppler), and `qpdf` inspect PDFs.
- `rga` (ripgrep-all) searches inside PDFs, Office documents, and archives.
- `tesseract` runs OCR with English and Spanish data.
- `wdotool` automates keyboard, mouse, and window actions on Wayland with
  xdotool-compatible commands. On Hyprland it cannot read window geometry or
  the pointer position; use `hyprctl clients` and `hyprctl cursorpos` instead.
- `yq` is mikefarah's Go version with jq-like syntax, not the Python wrapper.

## General Preferences

- Ask a concise clarifying question only when requirements are unclear or a choice
  would materially affect the outcome; otherwise proceed with a sensible default.
- Explain unfamiliar mechanisms in plain language, including why they work that
  way, the practical trade-offs, and what you recommend.
- For reviews and diagnoses, verify the full relevant scope, prioritize material
  findings, and give a candid verdict. If nothing material remains, say so.
- Treat unexpected changes made during a task as concurrent user work. Preserve
  them and continue only with your own changes. If the concurrent work prevents
  you from proceeding safely, stop and ask for guidance.
- Never run `git commit` or `git push`. After completing and verifying changes,
  leave the working tree uncommitted.
- When an authorized command needs an interactive sudo password, first explain
  precisely why elevated privileges are required and what the command will do, then
  open a small Kitty or Ghostty terminal running only that exact command so I can
  authenticate, and verify completion afterward instead of asking me to run it
  manually.

## Writing Preferences

- For externally facing prose, avoid recognizably AI-written style; prefer
  direct, concrete, natural writing, and avoid hype, jargon, formulaic structure,
  teaser phrasing, and content-marketing cliches.
- Prefer straight quotes over curly quotes, and avoid em dashes except when they
  are genuinely useful.

## Response Formatting

- Never use H1 (`#`) or H2 (`##`) headings in normal conversational responses.
  If a response needs headings, start at H3 (`###`) and keep heading text short.
  This does not apply when generating or editing a Markdown artifact whose
  requested format explicitly requires H1 or H2 headings, such as slide decks.
- Write inline math with `$...$` and display math with `$$...$$`. In display
  math, do not put operators such as `=`, `+`, or `-` alone on a line because
  Markdown renderers may interpret them as headings or list markers.
  - Use fenced `latex` code blocks only when raw LaTeX source is useful.

## Coding Preferences

- Make the smallest practical code change that solves the stated problem directly.
- For bug fixes, prefer the smallest local change at the failing call site; only
  change shared helpers, APIs, or abstractions when the bug clearly belongs
  there or affects multiple callers.
- Do not preserve backward compatibility unless I explicitly request it.
- Do not make unrelated cleanup or refactors unless explicitly requested.
- Avoid defensive coding unless it adds clear practical value.
- Keep code compact and local by default. Prefer direct code over speculative
  extensibility: use inline code for single-use logic, avoid exporting helpers
  unless another file uses them, and introduce abstractions or intermediate
  variables only when they improve clarity.
- Add comments only to explain non-obvious behavior. Use simple, concrete
  language that a beginner can follow. Explain what happens and why without
  assuming knowledge of tool internals.
  - Be precise about the concrete behavior or limitation; avoid broad claims
    when only one syntax case or code path is relevant.
  - Avoid cryptic shorthand and keep comments short.
  - Place comments as close as practical to the specific code they explain. Put
    comments about an entire function or method above its definition. When syntax
    allows, keep comments about only part of a larger construct within that
    construct. Use trailing comments only when they apply narrowly to one
    statement. Single-line comments should not end with a period.
- Before changing code, find the repository root and read its `AGENTS.md`, if
  present. Do this once per repository per session.
- Before finishing a code change, review the complete diff as if it were going
  through final code review. Simplify and polish the changed code as much as
  practical: remove unnecessary complexity, indirection, duplication, and
  verbosity, and make the implementation as compact and direct as clarity allows.
  Check naming and structure, then run the relevant formatters, linters, and tests.
  Keep the review scoped to changed code.

### Scope and Precedence

Conventions for specific languages and tools apply only to code that will remain
in a repository or otherwise be delivered to the user. They do not apply to
temporary scripts used only to support agent or subagent work.

Formatting, linting, type-checking, and testing requirements follow the same
scope. Repository instructions override general preferences and skill defaults;
repository configuration overrides all three.
