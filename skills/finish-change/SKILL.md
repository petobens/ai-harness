---
name: finish-change
description: >-
    Finish an in-progress code change by refining and simplifying the initial
    implementation, validating review feedback, running relevant checks, and
    giving a clear commit-readiness verdict. Use when asked to simplify, compact,
    polish, re-review, apply another agent's review, or get a change ready to
    commit. Do not use when asked for review only or told not to modify files.
metadata:
    short-description: Refine and finish a code change
    category: git
    requires:
        bins:
            - git
---

# Finish Change

Bring the requested change to a defensible stopping point. Preserve its intended
scope and prefer the smallest practical correction over further redesign.

## Establish the final scope

Read the repository instructions, status, the complete relevant diff, and enough
surrounding code to understand the change. Preserve unrelated or concurrent work.
Use the user's stated intent as the boundary; a request to polish or finish does
not authorize unrelated cleanup.

If the user supplies a Claude or Codex session ID, locate its JSONL session under
`~/.claude/projects` or `~/.codex/sessions` and extract the relevant review
findings. If the user pastes review feedback, use that directly.

## Resolve findings

Treat every prior or external review finding as a hypothesis. Validate it against
the current code and classify it internally as accepted, rejected, or already
resolved. Implement accepted findings only when they fix a material problem or
provide a clear improvement without disproportionate complexity. Briefly explain
rejected findings when handing off the result.

Respect settled design choices unless the current code provides concrete evidence
of a material problem.

## Refine the implementation

Treat the initial implementation as a draft and review the complete changed code,
including accepted review fixes. Look for unnecessary scope, indirection,
abstractions, helpers, state, defensive branches, duplication, and special cases.
Consolidate or remove them where doing so preserves behavior and makes the result
easier to read and maintain.

Prefer fewer moving parts and less code when they make the implementation clearer.
Do not optimize for line count, compress readable control flow, or remove
structure that carries meaning. Perform one deliberate refinement pass, then move
to validation instead of continuing to search for optional polish.

## Verify and stop

Run applicable formatters, linters, tests, and focused runtime checks. Then
review the final diff once for correctness, regressions, unnecessary complexity,
and accidental changes.

The change is finished when:

- no unresolved material finding remains;
- relevant checks pass, or any unavailable check is clearly identified; and
- the final diff stays within the intended scope.

Optional ideas and cosmetic preferences do not block completion. When these
conditions hold, stop and say `Ready to commit`; do not propose another general
polish pass. If they do not hold, say `Not ready to commit` and list only the
remaining blockers.

## Handoff

Summarize the changes made, material review decisions, validation performed, and
the readiness verdict. Keep the handoff concise. Do not commit or push unless the
user explicitly requests and repository instructions permit it.
