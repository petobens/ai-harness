---
name: conventional-commit
description: >-
    Generate a git commit message from a diff, matching the repository's
    existing commit style. Use when asked to write or generate a commit
    message. Analyzes recent history and defaults to Conventional Commits.
metadata:
    short-description: Generate a commit message matching the repo's style
    category: git
    requires:
        bins:
            - git
---

# Conventional Commit

Generate a single commit message for a set of changes. Output the message in a
single fenced `text` code block; do not run `git commit`.

## Scope

If the request names a repository path, run every git command in it with
`git -C <path> ...`; otherwise use the current directory.

The request names what to describe. Resolve the diff accordingly:

- Staged changes (default): `git diff --no-ext-diff --staged`
- Against a base branch `BASE`: `git diff --no-ext-diff BASE...HEAD`
- A specific commit `SHA`: `git diff --no-ext-diff SHA^!`

If the resolved diff is empty, say there is nothing to describe and stop. The
output rules below do not apply.

## Steps

1. Resolve the diff for the requested scope (see above).
2. Read the last 50 commit subjects: `git log -n 50 --pretty=format:%s`.
3. Choose the style:
   - If most recent commits follow Conventional Commits, use that style.
   - Otherwise mimic the format of the recent history.
   - If unclear or tied, default to Conventional Commits.
4. Write the message from the diff (see Rules).

## Rules

- Summary line in the imperative mood, under 72 characters if possible.
- Wrap body prose at 72 characters. Do not wrap URLs, code, command output, or
  Git trailers when wrapping would reduce readability or usability.
- Conventional Commits format is `type(scope): summary`. Use a correct type
  (feat, fix, chore, refactor, docs, test, style, perf, build, ci). The scope
  in parentheses is optional. Do not add breaking-change notation unless the
  diff clearly shows a breaking change.
- Add a body after a blank line explaining why the change was made. Scale its
  length to the change: usually a sentence or two, more when warranted. Skip
  it only for trivial, self-evident changes (rename, typo fix, one-line tweak)
  the summary already covers.
- Output only the commit message in a single fenced `text` code block, with no
  explanation or formatting outside it.

## Examples

Conventional Commits style:

```text
fix(ui): prevent session file from being saved in headless instances

Only save the session file if a UI is attached, avoiding unwanted session
writes from headless processes such as test workers.
```

Mimicking existing history:

```text
vim: include recent commit history in conventional_commit prompt

Pass the last 50 commit messages as context to improve generated commit
messages.
```
