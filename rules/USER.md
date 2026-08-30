# Context for AI Agents

This file contains durable context about me, my preferences, and how I like to
work.

Read it before starting work. Update the "Agent Memory" section only when a new
durable preference or constraint becomes clear.

## About Me

- I'm Pedro.
- I live in Buenos Aires, Argentina.
- I use Arch Linux and Neovim.
- I have a background in Economics.
- I'm the Co-Founder and COO of Muttdata, a Data + AI services company.

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
- Add comments only to explain non-obvious behavior. Write them in plain,
  human language that describes what the code does and why it matters; avoid
  cryptic shorthand. Keep them short. Put function-level comments above the
  function and use trailing comments only when they apply narrowly to one
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

## Agent Memory

> [!NOTE]
> Update this section only with durable information likely to matter again.
> Include stable preferences, recurring constraints, and long-term facts.
> Exclude temporary task details, transient project state, and vague traits.
