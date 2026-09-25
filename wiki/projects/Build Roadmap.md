---
type: roadmap
status: active
created: 2026-06-17
updated: 2026-06-21
tags:
  - captions
  - roadmap
  - legends
---

# Build Roadmap

## Phase 0: Brain Infrastructure Integration

Status: required.

- Fully clone or ingest this project into the brain infrastructure.
- Preserve discoverability for `wiki`, `src`, `tests`, `configs`, `scripts`, `skills`, `examples`, `docs`, `assets`, `release`, and `.raw` source lineage.
- Keep this checkout as implementation source of truth while Avalon Reset YouTube stores production-specific routing and receipts.
- Verify that future video agents can find the autonomous Shorts caption policy, timing authority policy, render QA policy, code, and tests from the brain layer.

## Phase 1: Policy Core

Status: started.

- Build contextual correction engine.
- Add regression tests from user fixes.
- Seed glossary and phrase repair config.
- Document cross-agent behavior.

## Phase 2: Caption Package Runner

- Ingest final video and extract exact-clock audio.
- Run or import Parakeet words.
- Run or import NFA CTM.
- Apply correction policy and emit correction manifest.
- Build ASS with active-word groups.

## Phase 3: Render And QA

- Burn captions with ffmpeg.
- Preserve source resolution, fps, codec policy, and audio policy.
- Generate ffprobe JSON.
- Generate proof frames.
- Fail runs on visible text, timing, layout, or manifest errors.

## Phase 4: Agentic Review Loop

- Assign Codex implementation, Claude language review, and Gemini visual review.
- Turn each accepted correction into policy/config/tests.
- Maintain a caption memory that gets sharper after every production run.
- Track version count per Short and the failure categories that caused extra renders.
- Treat recurring failures after policy capture as regressions in the package runner or QA gates.
