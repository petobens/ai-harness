# Context for AI Agents

This file contains durable context about me, my preferences, and how I like to
work.

Read it before starting work. Keep the "Agent Memory" section updated, but only
with information that is likely to matter again in future conversations.

## About Me

- I'm Pedro.
- I live in Buenos Aires, Argentina.
- I use Arch Linux and Neovim.
- I have a background in Economics.
- I'm the Co-Founder and COO of Muttdata, a Data + AI services company.

## General Preferences

- Ask a concise clarifying question only when requirements are unclear or a choice
  would materially affect the outcome; otherwise proceed with a sensible default.

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

## Coding Preferences

- Make the smallest practical code change that solves the stated problem directly.
- For bug fixes, prefer the smallest local change at the failing call site; only
  change shared helpers, APIs, or abstractions when the bug clearly belongs
  there or affects multiple callers.
- Do not preserve backward compatibility unless I explicitly request it.
- Do not make unrelated cleanup or refactors unless explicitly requested.
- Do not add abstractions unless they are clearly needed.
- Avoid defensive coding unless it adds clear practical value.
- Optimize for clarity and directness over extensibility.
- Keep code compact and local by default. Use inline code for single-use logic,
  avoid exporting helpers unless another file uses them, and avoid helper
  functions or intermediate variables that do not improve clarity.
- Add comments only when truly necessary, and keep them as short and compact as
  possible. Single-line code comments should not end with a period.
- Before finishing a code change, review whether the result can be simpler:
  fewer lines, fewer helpers, fewer intermediate variables, and less indirection,
  without hurting readability.

### Python

These defaults apply to Python code that will remain in a repository or be
user-facing. They do not apply to temporary scripts written only to support
agent work during a task. A repo's AGENTS.md overrides them where they conflict.

- Target Python 3.14+ syntax.
- Always include type hints, using built-in generics (`list`, `dict`) and
  `X | None` unions rather than `typing.List` or `Optional`.
- Prefer `pathlib` over `os.path`.
- Quotes: double for text and interpolation, single for short symbol-like
  strings.
- Write NumPy-style docstrings: a summary line, then `Parameters`/`Returns`
  sections, omitting types since they are in the signature. Skip boilerplate
  docstrings for obvious one-off code.
- Before finishing, format and lint with Ruff and type-check with `zmypy`
  (Zuban), falling back to `mypy` if `zmypy` is not installed.
- For non-trivial code, provide pytest tests.

## Agent Memory

> [!NOTE]
> Update this section only with durable information likely to matter again.
> Include stable preferences, recurring constraints, and long-term facts.
> Exclude temporary task details, transient project state, and vague traits.

- Before code changes in a repository, find the repository root and check for
  AGENTS.md once per repository per session. Read it if present. Recheck only
  when work moves to a different repository.
