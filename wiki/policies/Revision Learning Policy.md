---
type: policy
status: active
created: 2026-06-17
updated: 2026-06-21
tags:
  - captions
  - revisions
  - learning
---

# Revision Learning Policy

Every real caption correction should improve the next run.

The goal is to decrease the number of render/revision loops required for a usable Short. Repeated user feedback is not just a conversation artifact; it is production training data.

## Classification

Classify each user fix into one of these buckets:

- `lexical`: a word or entity was wrong.
- `casing`: the word was right but the display form was wrong.
- `grammar`: the phrase was unidiomatic or missing a function word.
- `timing`: highlight, boundary, or hold behavior was wrong.
- `grouping`: line break or caption chunking hurt meaning.
- `style`: typography, color, size, bubble, or placement was wrong.
- `qa`: the issue should have been caught by proof-frame or manifest review.
- `shorts_editorial`: a Short-specific caption choice affected hook clarity, viewer attention, upper text philosophy, or scene comprehension.
- `pipeline_default`: the correction should become a default behavior, config value, or manifest gate for future runs.
- `review_exception`: the system cannot infer the answer reliably.

## Required Follow Through

For each correction:

1. Save the original bad caption text.
2. Save the corrected caption text.
3. Record why the correction is safe or why it requires human review.
4. Add a config rule when the correction is reusable.
5. Add a test when the correction is automatable.
6. Update a policy page when the correction changes operating behavior.
7. If the correction is Short-specific, update [[Autonomous Shorts Caption Policy]] or the Avalon [[Autonomous Shorts Production SOP]] routing note.
8. Add a QA gate when the failure should have been caught automatically, such as cut-crossing captions, invalid ASS events, overlapping upper captions, missing final words, or excessive tail hang.

## Version Count Reduction

After each production Short, record:

- how many rendered versions were needed before the user considered it usable;
- the top three causes of extra versions;
- which causes became policy/config/tests/QA gates;
- which causes remain human taste calls;
- what the next first-pass render should do differently.

If the same failure category recurs after it has a policy or test, treat it as a regression and fix the pipeline rather than accepting another manual correction cycle.

## Current Regression Seeds

- `low raw` -> `LoRA`
- `exacting 2.0` in AI video context -> `exciting as Seedance 2.0`
- `L O R A` remains letter timed.
- `what is this unlock` -> `what does this unlock`
- `sticking the 30` -> `sticking to 30`
- `fuckdown` -> `fuck down`
- bottom speech captions reset at hard cuts.
- upper Shorts captions default to brief static-yellow topic markers, not duplicate speech captions with active highlights.
- Shorts tail trims to about three frames after the final spoken word unless a deliberate hold is documented.

## Do Not Overfit

Do not turn one ambiguous audio moment into a global replacement. If the rule needs context, encode that context. If the system cannot prove it, mark it for review.
