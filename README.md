# AI Harness

A collection of reusable AI assets.

## Structure

- `AGENTS.md`: repository conventions loaded by Codex and shared with Claude.
- `CLAUDE.md`: Claude Code entrypoint that imports the shared conventions.
- `prompts/`: role and task prompts used by editor integrations.
- `rules/`: global always-on instruction files that can be autoloaded into chats.
- `skills/`: reusable workflows and instructions for specialized tasks.

## Skill naming

Use lowercase kebab-case for skill directories and frontmatter names. Name broad
language, format, or product skills after their domain, such as `python`, `typst`,
or `google-docs`. Name bounded workflows with a verb and object, such as
`review-diff`, `read-pdf`, or `write-changelog`.
