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
- Do not preserve backward compatibility unless I explicitly request it.
- Do not make unrelated cleanup or refactors unless explicitly requested.
- Do not add abstractions unless they are clearly needed.
- Avoid defensive coding unless it adds clear practical value.
- Use inline code for single-use logic instead of extracting helper functions.
- Optimize for clarity and directness over extensibility.
- Add comments only when truly necessary, and keep them as short and compact as
  possible.

## Agent Memory

> [!NOTE]
> Update this section only with durable information likely to matter again.
> Include stable preferences, recurring constraints, and long-term facts.
> Exclude temporary task details, transient project state, and vague traits.

- Before code changes, find the repository root and read its AGENTS.md.
