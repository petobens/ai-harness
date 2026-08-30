---
name: python-development
description: >-
  Create, modify, or review Python code that will remain in a repository or be
  delivered to the user. Do not use for temporary agent or subagent helper
  scripts.
---

# Python Development

Follow repository instructions when they differ from these defaults. If
repository configuration conflicts with either, follow the configuration.

- Target Python 3.14+ syntax.
- Always include type hints, using built-in generics (`list`, `dict`) and
  `X | None` unions rather than `typing.List` or `Optional`.
- Prefer `pathlib` over `os.path`.
- Prefer double quotes for text and interpolation, and single quotes for short
  symbol-like strings, unless the repository formatter enforces another style.
- Write NumPy-style docstrings: a summary line, then `Parameters` and `Returns`
  sections, omitting types already present in the signature. Skip boilerplate
  docstrings for obvious one-off code.
- Before finishing a change, format and lint with Ruff and type-check with
  `zmypy`, falling back to `mypy` if `zmypy` is unavailable.
- For non-trivial changes, add or update pytest tests when the repository has a
  test suite or the behavior can be meaningfully tested.
