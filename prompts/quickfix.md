# Quickfix

Fix the diagnostics from the quickfix or location list.

You will be provided with:

- A list of code diagnostics (errors and/or warnings) in the following format:

  ```text
  /path/to/file.py:line:col: tool: message
  ```

- The corresponding file(s) may be attached as context. If the file content is
  not visible, read the relevant file(s) before editing.

Instructions:

- Inspect the relevant files before editing. Use the provided context as a
  starting point, but check imports, call sites, tests, and local conventions
  when they matter.
- Treat duplicate or equivalent diagnostics from different tools as one issue.
- Make the smallest practical change that resolves the diagnostics, preserving
  behavior unless the diagnostic points to an existing bug.
- If several diagnostics share a cause, fix the cause instead of patching each
  symptom separately.
- Run the narrowest useful formatter, linter, type-checker, or test command
  available for the affected files.
- If a diagnostic is unclear, make a reasonable best guess after inspecting the
  surrounding code. Ask only when proceeding could create the wrong behavior.

Here is the list of code diagnostics:

```text
%s
```
