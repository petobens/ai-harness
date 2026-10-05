---
name: mutt-ops-slides-update
description: >-
    Drafts and refines Muttdata quarterly Operations recaps for leadership,
    grounding the COO narrative in period notes, prior decks, and verified
    metrics. Activates when preparing or reviewing a Muttdata Ops update,
    its storyline, or ops_area_slides.md. Covers content and evidence;
    Google Slides layout and rendering belong to the google-slides skill.
metadata:
    short-description: Draft and refine quarterly Muttdata Ops updates
    category: writing
---

# Mutt Ops Slides Update

Turn the quarter's evidence into a concise COO account of results, their causes,
and the decisions that follow. Pedro primarily owns Professional Services (PS)
delivery and retention. Lead with that remit, acknowledging shared commercial
work and dependencies on Sales, Habit, Finance, and People where relevant.

## Establish the working context

Honor the requested mode: draft, edit, or review only. A review-only request
returns findings without changing files. Use the requested quarter and destination.
Existing recaps live under
`mutt/leadership/meetings/quarterly/<year>/<year>-Q<quarter>/` in the notes repo:

- `ops_area_notes.md`: Pedro's topics, relevant links, and supporting analysis;
- `ops_area_slides.md`: the working slide content and internal storyline.

For a new draft or full review, read the quarter notes, existing draft, previous
recap, and current annual Ops plan. Follow relevant links and inspect supporting
1:1, director, and leadership meeting notes for the requested period. Use the
quarter notes to set priorities; use other sources to substantiate or challenge
them. Prior decks establish voice and strategic continuity, not current facts.
Separate quarter results from subsequent developments and next-quarter plans.

For a targeted edit, read the affected slide and enough surrounding content to
preserve the argument. Reuse documented decisions and evidence; do not restart
the full research pass or rewrite settled slides without a material reason.
When the user cites another session, use `analyze-agent-sessions` to recover its
decisions, then check them against the current files.

Read [the slide-writing prompt](../../prompts/slides_generator.md) for storyline,
titles, chips, bullet structure, and Markdown format. Resolve it relative to this
skill's real repository location if accessed through a symlink. Its instruction
to preserve supplied numbers does not override a requested validation: investigate
discrepancies and explain corrections. For a first draft or tone pass, read
[examples](references/examples.md).

## Ground the claims

Use `mutt-data-analyst` for database definitions and read-only validation, and
`google-sheets` when reconciling Finance's workbook. Validate material quantitative
claims for a first draft or requested numbers audit. During wording edits, query
again only when a claim changes or evidence is missing or inconsistent. If a
source is unavailable, continue useful drafting and identify the affected claims
as unverified; do not imply they were checked.

Keep these distinctions explicit in the analysis and clear in the slide wording:

- **Scope:** PS versus company-wide revenue, margins, and commitments. Include
  company context only when it helps explain the Ops story, and label it.
- **Ownership:** retention means renewals plus upsells; origination means new
  deals plus cross-sells. Recognize joint work without counting all account
  revenue as retention or comparing it with a retention-only target.
- **Baseline:** base budget versus stretch target, and any difference from the
  annual plan's headline goal. Compare like scopes and periods. Do not silently
  switch between uncapped budget attainment and per-account capped coverage.
- **Status:** accrued results, forecast, committed work, closed-won deals, and
  proposed commitments are different claims. Label forecasts as forecasts rather
  than achieved results; show prior-period comparators when they clarify growth.
- **Economics:** distinguish delivery margin, allocated payroll, other
  cost-of-revenue expenses, and resulting gross margin. A time-tracking view of
  non-delivery cost can overlap with allocated payroll; do not add them together.
- **Mechanism:** utilization is not a bench measure, and revenue per reported
  delivery hour is not a negotiated billing rate. Investigate apparent conflicts
  with staffing notes before attributing movements to hiring, pricing, or raises.

When drafting or updating evidence, maintain a compact `Draft Notes` section in
the notes: source or query, period, filters, definition, verification date, and
material caveats. Distinguish database results, management observations, and
inferred causes. Use confidential people notes only for audience-appropriate
operational context.

During editorial work, retain the dated financial snapshot and flag material
live-data changes. Correct known errors within the authorized editing scope;
flag them in review-only work. For a requested numbers audit or refresh, check
current sources and reconcile dependent figures, comparisons, headlines, and
notes together. Do not mix snapshots or dismiss workbook/database discrepancies
as rounding without checking their cause.

## Build the narrative

The established recap moves from outlook to account and capability achievements,
then revenue and margin challenges, next-quarter priorities, and cross-team
requests. Use that as a starting point, adapting to the evidence and requested
format. Explain how the quarter advances or falls short of the prior plan.

Keep the summary selective and use later slides to explain its headline movements.
Pair challenges with relevant follow-through without repeating the same action
across slides.

Preserve Pedro's direct, candid voice. Reuse a few recognizable phrases from
prior decks when the underlying claim still holds. Avoid formulaic "X, but Y"
or "X, not Y" framing, repetitive rhetorical hooks, and unsupported claims that
a process is systematic or repeatable. Recognize strong delivery and commercial
relationships without turning them into slogans. Frame cross-team dependencies
as shared business problems, with evidence and a concrete request.

State the problem and its mechanism before suggesting a response. Preserve the
difference between an observation, a tentative recommendation, an agreed action,
and a commitment. Add owners, dates, and decision forums only when supported by
the sources or user direction. Make unresolved choices visible instead of
inventing deadlines or upgrading "should probably" to "we will."

Keep explanations long enough to be understood. For a dense economics slide,
preserve the margin bridge, material drivers, and decision implications; move
calculations, cost-pool reconciliations, and secondary breakdowns into the notes.
Do not compress away the reason a number matters or expose query terminology in
the presentation just because it was needed to validate the claim.

## Finish the requested pass

For a final pass, check consistency across the governing answer, storyline, slide
titles, repeated figures, and notes. Confirm that summary claims receive support
later, challenges lead to relevant priorities or requests, and wording preserves
forecast status and the user's intended certainty. Review density and repetition
across the deck, including date-sensitive language.

Keep internal planning in the slides file and detailed evidence in the notes.
Avoid creating parallel circulation copies unless requested. Run the repository's
Markdown checks after edits and review the complete task diff, preserving
concurrent edits.

Report a candid readiness verdict and any material unresolved evidence. Separate
content readiness from visual fit: Markdown checks cannot establish that the
rendered slides are readable. Use `google-slides` to inspect reference decks and,
when requested, execute and visually verify the approved content in Google Slides.
A content task alone does not authorize publishing, sharing, or messaging others.
