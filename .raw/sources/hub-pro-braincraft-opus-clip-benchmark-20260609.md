---
type: benchmark
status: active
created: 2026-06-09
updated: 2026-06-09
tags:
  - braincraft
  - shorts
  - opus-clip
  - video-production
  - captioning
---

# Braincraft Opus Clip Benchmark 2026-06-09

## Scope

Benchmark the 33 Opus Clip exports downloaded from the same Braincraft v6 raw source against the internal Braincraft v6 Shorts pipeline.

Canonical local audit folder:

```text
D:\braincraft_v6_only_production_20260609\opus_clip_audit_20260609
```

Audit script:

```text
<hub-pro-checkout>\scripts\audit_braincraft_opus_exports.py
```

Opportunity shortlist:

```text
<hub-pro-checkout>\scripts\braincraft_v6_opus_opportunity_shortlist.json
```

## Findings

- Opus produced 33 MP4s totaling about 19.0 minutes.
- All 33 Opus exports were H.264 at `1080x1920`; none preserved 4K AV1 delivery.
- Opus speech starts immediately. The title card is a visual overlay, not silent pre-roll.
- The visible white headline card usually holds for about the first 4 seconds on sampled clips.
- Opus uses louder visual grammar: white headline cards, large center/bottom captions, yellow/green highlights, occasional emojis, and an Opus watermark.
- Opus identified several useful extra source sections we did not include in the first 9-clip hero batch.
- Opus also split our strongest source modules into thinner fragments.
- Three Opus clips ended hot with under `150ms` of tail padding. Opus rank 1 was one of those hot-end failures.
- Opus still made proper-noun mistakes in visual captions, including `FRANKENSTEIN` where the production correction should be `RANKENSTEIN.PRO`.

## Production Judgment

The internal pipeline is stronger for final publication quality:

- Current internal deliverables preserve vertical 4K and AV1.
- Internal captions are cleaner and less cluttered.
- Internal files have no Opus watermark.
- Internal production uses source-of-truth manifests, v6-only transcript policy, caption-gap auditing, named-entity correction, final music-bed policy, and boundary QA.

Opus is useful as a recall benchmark, not as a final editor. Its best contribution is breadth: it can reveal candidate regions worth reviewing. Its weak points are boundary discipline, visual clutter, export quality, watermarking, and unverified caption text.

## Adopted Rules

1. Treat Opus-like services as competitor recall benchmarks only. Never treat their score or clip count as final editorial truth.
2. Run a two-pass internal selection model:
   - Hero pass: 8 to 12 coherent, high-confidence clips.
   - Recall pass: 5 to 10 extra candidates from lower-confidence or competitor-discovered regions.
3. If an Opus-like clip exposes a good region, remap it to the current source timeline and rerender internally from source. Do not reuse the Opus export.
4. Optional hook cards are allowed, but they must be short, clean, and controlled:
   - target duration: `2.5s` to `4.0s`;
   - speech may play underneath;
   - card must not cover critical UI;
   - no emojis by default;
   - no watermarks;
   - no misleading clickbait claims.
5. Caption style remains minimalist unless an alternate style is explicitly approved. Preserve readability over social-template noise.
6. Reject any clip with hot endings, mid-word outpoints, stale-source captions, missing captions during speech, or unverified proper nouns.
7. Final exports remain AV1 4K unless the user explicitly asks for platform proxies. H.264 competitor output is not the standard.

## Extra Candidate Regions

High-value Opus-discovered source windows for future internal rendering:

| Opus rank | Source window | Candidate | Note |
|---:|---:|---|---|
| 17 | `161.120-244.176` | The Perfect Website Crawler Template | Strong foundational setup. |
| 31 | `712.112-757.440` | A Website Brain Future AI Agents Can Use | Strong strategic framing. |
| 32 | `1013.856-1070.976` | Scrape Brand Identity In Seconds | Useful visual/tool payoff. |
| 19 | `1107.824-1145.344` | Turn Website Screenshots Into CTAs | Good creative angle. |
| 11 | `2417.616-2448.976` | Find Your Website Design Bible | Strong design-system angle. |
| 1 | `2142.672-2159.472` | Scrape 60 Pages Instantly | Repair before use; Opus hot-ended it. |
| 33 | `2530.464-2619.664` | The New Website Strategy | Support clip, not hero clip. |

## Related

- [[Video Transcript and Clipping SOP]]
- [[YouTube and Shorts Operations]]
