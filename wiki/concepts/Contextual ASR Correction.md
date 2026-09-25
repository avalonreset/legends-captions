---
type: concept
status: active
created: 2026-06-17
updated: 2026-06-17
tags:
  - captions
  - asr
  - correction
---

# Contextual ASR Correction

Contextual ASR correction means using the video's subject matter to repair transcript text before render.

The system should understand that a local AI avatar video is likely to mention `LoRA`, `Seedance 2.0`, `Stable Audio 3 Medium`, `RTX 4090`, `HeyGen`, and similar terms. If ASR produces phonetically plausible nonsense, the caption system should repair it when confidence is high and record the decision.

This is the difference between a generic caption generator and a production caption agent.

