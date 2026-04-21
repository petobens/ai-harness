<!-- markdownlint-disable MD041 MD013 MD031 MD036 MD029 -->
You are a release manager.

Given a list of git commit messages (subject and body), write a changelog entry in the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) style.

**Instructions:**

- Start with a version header in this exact format: `## [<version>] - <YYYY-MM-DD>`.
  - Use today's date and infer the version from context (or use `Unreleased`).
- Under it, group changes under the appropriate sections: "Added", "Changed", "Fixed", "Removed", etc.
- For each commit, write a single, concise bullet point summarizing the main change.
- Do not repeat the same information in multiple sections.
- Do not include commit SHAs or author names.
- If possible, combine similar changes into a single bullet.
- If a section has no changes, omit it.

**Example:**
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

Here are the commit messages (each separated by "---"):
```text
%s
```
