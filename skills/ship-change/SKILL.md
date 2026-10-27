---
name: ship-change
description: >-
  Ships a reviewed change through a pull request, passing checks, merge, and
  branch cleanup. Use only when explicitly invoked by name or after the user
  confirms using this skill; respect requests to stop at opening a PR.
---

# Ship Change

Complete the requested GitHub PR workflow for the agreed repositories. Keep
permission specific to the current change; loading this skill grants none.

If the user has neither invoked `ship-change` by name nor confirmed using it
for this change, ask and wait before starting its workflow. Automatic selection
does not count as confirmation. If the change is already prepared, combine this
question with any missing action authorization.

## Prepare and authorize

Read repository instructions and inspect the branch, working tree, and full diff.
Use [finish-change](../finish-change/SKILL.md) for unfinished review or validation;
reuse completed validation when the changes and relevant conditions are unchanged.
Resolve the intended scope before staging or committing; staged files may still
contain unrelated work. Preserve it and commit only the agreed files or hunks.

Before publishing, summarize the change, validation, repositories, target
branches, and proposed actions. Ask once for any missing authorization, limited
to the requested scope. For the full workflow, this covers committing, pushing,
opening the PR, waiting for checks, merging, deleting local and remote task
branches, and updating the local target branch. A request to open a PR does not
authorize merging it.

Once invocation is confirmed, an explicit request for the whole sequence already
supplies action authorization; do not ask again. Invocation by name alone is not
approval of unspecified changes. If a repository says never to commit or push,
explain that restriction when asking for the exception. Explicit user
authorization for this change can provide that exception; the skill itself
cannot override repository rules.

## Publish and verify

Commit the reviewed change using repository conventions, push its task branch,
and create a PR against the agreed target. Follow any PR template and describe
the resulting behavior and validation. Reuse an existing PR for the same change.
Use a GitHub client whose credentials trigger the repository's workflows.

Establish which checks and reviews apply, then wait for them on the current PR
head. Expected checks that have not run are not passing checks. Inspect failed or
missing runs before retrying; do not loop retries without new evidence. Fix
failures attributable to the change within scope, review the fixes, and wait for
checks on the updated head. Stop and report external blockers or failures
requiring materially broader changes.

Never bypass required checks, reviews, or branch protection. If the PR head
changes unexpectedly, review the new work before continuing. Use the verified
head SHA when merging and the repository's merge convention. Do not enable
unattended merging and end the turn while the requested work is still pending.

## Merge and clean up

After checks and required reviews pass, merge if authorized and verify GitHub
reports the PR as merged. If target updates and cleanup are authorized, switch
to the target branch and pull with `--ff-only`. Confirm the reviewed changes
landed and neither task branch contains additional unshipped commits before
deleting it locally or remotely. Tolerate an already deleted remote branch and
prune stale refs.

Squash merges may require forced local branch deletion after those checks.
Never discard concurrent changes or delete the target branch. If cleanup is
blocked, preserve the work and report precisely what remains.

Finish with PR links, check results, merge status, and confirmation of local
branch, remote cleanup, and working-tree status. Ask again only if the agreed
scope materially changes or a new action needs authorization.
