---
name: diff-review
description: >-
    Review a git diff and return structured, GitHub Copilot-style feedback
    (overview, reviewed changes, comments, recommendations, and readiness
    verdict) without changing files. Use when asked for a review-only assessment
    of changes, a diff, or a branch before merging. Do not use when asked to
    implement findings or finish the change.
metadata:
    short-description: Copilot-style structured review of a git diff
    category: git
    requires:
        bins:
            - git
---

# Diff Review

Give constructive, actionable, concise feedback in the style of a GitHub Copilot
code review. Preserve the structured format while prioritizing material findings
over optional polish.

## Scope

If the request names a repository path, run every git command in it with
`git -C <path> ...`; otherwise use the current directory.

Resolve the diff from the request:

- Staged changes (default): `git diff --no-ext-diff --staged`
- Against a base branch `BASE`: `git diff --no-ext-diff BASE...HEAD`
- A specific commit `SHA`: `git diff --no-ext-diff SHA^!`

If the diff is empty, say there is nothing to review and stop.

Inspect enough surrounding code and repository guidance to validate the diff in
context. Treat prior review findings as hypotheses rather than facts. On a final
or repeated review, verify the current diff and whether earlier material findings
were resolved; do not reopen settled design choices without a concrete material
reason.

## Finding threshold

Report correctness problems, regressions, security or performance concerns, and
clear maintainability problems that are worth addressing before merge. Do not
invent suggestions to populate the response, and omit cosmetic or speculative
nitpicks. If there are no material findings, say so plainly.

## Output

Structure the response with these sections:

- `## 1. Overview of Changes` — briefly summarize the purpose and main effect
  of the diff.
- `## 2. Reviewed Changes` — list the key files or areas changed and what was
  updated.
- `## 3. Comments` — list material findings as bullets, covering correctness,
  regressions, realistic edge cases, performance, and clear maintainability or
  repository-convention problems. Reference specific lines or snippets and
  include a concrete code example when it materially clarifies the fix. If there
  are no findings, write `No material findings.`
- `## 4. Overall Recommendations` — summarize major issues or next steps for
  the author and end with an explicit `Ready to commit` or `Not ready to commit`
  verdict for the reviewed scope. Mention relevant validation that was not run.
  A non-blocking idea does not make the change unready.

Use neutral, practical language.
