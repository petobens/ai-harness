# AI Harness

This repository contains reusable prompts, global rules, and agent skills.

## Skills

- Keep shared skills compatible with both Codex and Claude Code. Use portable
  Agent Skills frontmatter unless a skill requires agent-specific behavior.
- Follow the naming convention in `README.md` when adding or renaming a skill.
- Keep each skill directory name identical to the `name` in its `SKILL.md`
  frontmatter.
- Write descriptions in the third person, stating both what the skill does and
  when it should activate.
- Keep `SKILL.md` focused. Put substantial conditional guidance in linked
  references and deterministic repeated operations in scripts.
- When renaming a skill, update every cross-skill reference and preserve its
  supporting references, scripts, and assets.

## Validation

- Run `rumdl check .` after changing Markdown.
- Run an available Agent Skills validator for every changed skill.
- After renaming a skill, search the complete repository for its previous name.
- Run `git diff --check` and review the complete diff before finishing.
