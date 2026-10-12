---
name: python
description: >-
  Creates, modifies, or reviews Python code that will remain in a repository or
  be delivered to the user. Do not use for temporary agent or subagent helper
  scripts.
---

# Python

Follow repository instructions when they differ from these defaults. If
repository configuration conflicts with either, follow the configuration.

- Target Python 3.14+ syntax.
- Always include type hints, using built-in generics (`list`, `dict`) and
  `X | None` unions rather than `typing.List` or `Optional`.
- Prefer `pathlib` over `os.path`.
- Prefer double quotes for text and interpolation, and single quotes for short
  symbol-like strings, unless the repository formatter enforces another style.
- Write Google-style docstrings with Markdown prose and `Args:`, `Returns:`,
  and `Raises:` sections where useful. Omit types already present in the
  signature. Use raw docstrings for LaTeX backslashes. Skip boilerplate
  docstrings for obvious one-off code.
- In Zensical projects, keep API rendering, notebook execution, and math support
  aligned with the documentation recipes. Run the strict documentation build
  after changing docstrings or documentation configuration.
- Before finishing a change, format and lint with Ruff and type-check with
  `ty check`. Run configured hooks through the repository recipe (for example,
  `just hooks`). For uv projects using prek without a recipe, use
  `uv run --no-sync prek run --all-files` after syncing dependencies.
- For non-trivial changes, add or update pytest tests when the repository has a
  test suite or the behavior can be meaningfully tested.
