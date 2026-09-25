---
type: overview
status: active
created: 2026-06-17
updated: 2026-06-21
tags:
  - captions
  - overview
---

# Overview

Legends Ultimate Captions is a caption deployment system, not a subtitle script. It is a core component of the Avalon Reset / Hub Pro video production pipeline, built for videos where caption text, timing, visual style, and revision behavior are part of the content product.

The system combines:

- high-quality ASR for first-pass text;
- forced alignment for final word timing;
- contextual correction for domain terms and model names;
- active-word ASS rendering;
- proof-frame and ffprobe QA;
- correction memory that becomes tests and policy.

The project starts from proven Avalon Reset and AI Marketing Hub Pro production patterns, preserved in `.raw/`.

Brain integration requirement: this project should be fully cloned or ingested into the brain infrastructure so future video-production agents can discover the implementation, tests, configs, policies, playbooks, and QA rules without relying on ad hoc path memory. See [[projects/Brain Infrastructure Integration 2026-06-21]].
