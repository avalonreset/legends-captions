---
type: hot-cache
status: active
created: 2026-06-17
updated: 2026-06-21
tags:
  - captions
  - hot
---

# Hot

Legends Ultimate Captions is being split out as its own project at `E:\legends-ultimate-captions`.

Current rule that should affect the next run: treat user caption fixes as policy candidates. Every repeated or obvious fix should become one of: glossary rule, contextual phrase repair, timing/grouping rule, QA checklist item, or human-review exception.

New infrastructure mandate from 2026-06-21: Legends Ultimate Captions is a core video production dependency and must be fully cloned or ingested into the brain infrastructure. The brain layer should index the full project, including `wiki`, `src`, `tests`, `configs`, `scripts`, `skills`, `examples`, `docs`, `assets`, `release`, and `.raw` source lineage. See [[projects/Brain Infrastructure Integration 2026-06-21]].

New revision-learning mandate: every Short production should reduce future revision count. Accepted user feedback must be classified and promoted into policy, config/defaults, regression tests, or QA gates when reusable. If a captured failure recurs, treat it as a regression in the caption package runner or QA gate.

New Shorts caption policy from 2026-06-21: bottom speech captions must reset at known hard cuts, final ASS events should report zero cut-boundary crossings and zero invalid events, upper editorial captions should be brief static-yellow topic markers rather than duplicate speech captions, and Shorts should end about three frames after the final spoken word unless a deliberate hold is documented.

Active defaults:

- Text quality: WSL Parakeet `nvidia/parakeet-tdt-0.6b-v3`.
- Final timing: NeMo Forced Aligner CTM when exact highlight/boundary precision matters.
- Caption style: all caps, Montserrat Black, white inactive text, cyan active word, 75% opacity black rounded backing, hard two-line maximum. Bubble QA must confirm the apparent left/right padding matches the apparent bottom padding; increase horizontal padding separately if the sides look tight.
- Shorts upper-text style: static bright yellow topic markers near the upper quarter, no default per-word highlight.
- Recent regression rules: `low raw` -> `LoRA`, `C dance 2.0`/`exacting 2.0` in AI video context -> `Seedance 2.0`, `what is this unlock` -> `what does this unlock`, `sticking the 30` -> `sticking to 30`, and spelled `L O R A` should keep independent per-letter timing when possible.

Next build priority: move from policy-only correction into a full render package runner that can ingest media, transcript words, NFA CTM, style config, proof-frame targets, and correction manifest paths.
