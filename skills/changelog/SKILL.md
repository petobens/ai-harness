---
name: changelog
description: >-
    Write a Keep a Changelog-style entry from git commit messages. Use when
    asked to generate a changelog or release notes from recent commits or a
    set of commits.
metadata:
    short-description: Generate a Keep a Changelog entry from commits
    category: git
    requires:
        bins:
            - git
---

# Changelog

Act as a release manager. Write a changelog entry in the
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) style from a set of
commit messages.

## Commits

If the request names a repository path, run every git command in it with
`git -C <path> ...`; otherwise use the current directory.

Determine which commits to summarize from the request:

- A list of commit SHAs: read each with
  `git show --no-patch --format=%B <SHA>`.
- Since the last release (default): find the latest tag with
  `git describe --tags --abbrev=0`, then list commits with
  `git log <tag>..HEAD --format=%H` and read each message as above.

If a `CHANGELOG.md` exists at the repo root, read it to infer the next version
and match its existing style. Do not edit the file; output the entry only.

## Rules

- Start with a version header in this exact format:
  `## [<version>] - <YYYY-MM-DD>`. Use today's date; infer the version from
  context, or use `Unreleased`.
- Group changes under the appropriate sections: "Added", "Changed", "Fixed",
  "Removed", etc. Omit sections with no changes.
- Write one concise bullet per commit summarizing the main change; combine
  similar changes into a single bullet where possible.
- Do not repeat the same information across sections.
- Do not include commit SHAs or author names.

## Example

```markdown
## [1.4.0] - 2026-01-14

### Added

- Introduced user authentication module.
- Added password reset functionality.

### Changed

- Updated the login page UI for better accessibility.

### Fixed

- Fixed crash on login page when credentials are missing.
```
