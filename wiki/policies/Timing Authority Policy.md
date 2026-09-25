---
type: policy
status: active
created: 2026-06-17
updated: 2026-06-21
tags:
  - captions
  - timing
  - nfa
---

# Timing Authority Policy

## Roles

Parakeet is preferred for ASR text quality and first-pass word timestamps. NeMo Forced Aligner is preferred for final word-boundary truth when exact timing matters.

## Rules

- Treat raw ASR word timestamps as planning data.
- Treat NFA CTM words as final timing evidence when available.
- Do not cut inside the first or last aligned word.
- Use highlight lead around `0.08s` to `0.10s` for 60 fps active-word captions.
- Preserve natural caption visibility through short pauses instead of blinking blanks.
- If timing is manually adjusted, record the adjustment in the manifest.
- For edited Shorts, known hard cuts are caption group boundaries. Bottom speech-caption events should not cross a hard cut unless the render manifest records a deliberate creative exception.
- For Shorts, final render tail should normally end about three frames after the final spoken word on a 60 fps timeline.

## Spoken Acronyms

When an acronym is spoken as letters, timing may be distributed or aligned per letter. Prefer actual NFA letter timing. If only a word span is available, distribute timing across virtual letters and mark the manifest as `virtual`.
