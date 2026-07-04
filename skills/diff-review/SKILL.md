---
name: diff-review
description: >-
    Review a git diff and return structured, GitHub Copilot-style feedback
    (overview, reviewed changes, comments, recommendations). Use when asked to
    review changes, a diff, or a branch before merging.
metadata:
    short-description: Copilot-style structured review of a git diff
    category: git
    requires:
        bins:
            - git
---

# Diff Review

Act as a senior software engineer. Review the requested changes and give
constructive, actionable, concise feedback in the style of a GitHub Copilot
code review.

## Scope

If the request names a repository path, run every git command in it with
`git -C <path> ...`; otherwise use the current directory.

Resolve the diff from the request:

- Staged changes (default): `git diff --no-ext-diff --staged`
- Against a base branch `BASE`: `git diff --no-ext-diff BASE...HEAD`
- A specific commit `SHA`: `git diff --no-ext-diff SHA^!`

If the diff is empty, say there is nothing to review and stop.

## Output

Structure the response with these sections:

- `## 1. Overview of Changes` — briefly summarize the purpose and main effect
  of the diff.
- `## 2. Reviewed Changes` — list the key files or areas changed and what was
  updated.
- `## 3. Comments` — for each significant change, give bullet-point feedback
  covering correctness and logic errors, style and readability, likely bugs or
  realistic edge cases (only those implied by the diff or normal production
  use, not speculative ones), suggestions for improvement, performance
  concerns, and adherence to best practices. Reference specific lines or
  snippets. When suggesting an improvement, always include a concrete code
  example. Optional minor style or documentation nitpicks are fine.
- `## 4. Overall Recommendations` — summarize major issues or next steps for
  the author.

Use neutral, practical language.
