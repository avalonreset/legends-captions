---
name: legends-ultimate-captions
description: Agent-driven video caption QA and rendering workflow with contextual ASR correction, forced alignment policy, active-word captions, proof-frame QA, and revision learning.
---

# Legends Ultimate Captions

Use this skill when the user wants captions added to a video, caption text fixed,
caption timing checked, active-word captions rendered, or a caption run packaged
with proof evidence.

## Start Here

1. Read `README.md`.
2. Read `wiki/hot.md`.
3. Read `wiki/policies/Caption Intelligence Policy.md`.
4. Read `wiki/playbooks/One Revision Caption Deployment.md`.
5. Run `legends-captions doctor`.

## Operating Policy

- Treat ASR as evidence, not the final editor.
- Apply contextual correction before render.
- Prefer Parakeet for text quality.
- Prefer NFA CTM for final word timing when precision matters.
- Preserve spoken acronym timing when possible.
- Generate proof frames from the final render, not only an ASS preview.
- Record corrections and timing fallbacks in manifests.
- Convert reusable user fixes into policy, config, and tests.

## Commands

```powershell
legends-captions doctor
legends-captions policy-report
legends-captions normalize --uppercase "low raw teaches the model"
legends-captions normalize --manifest "L O R A."
powershell -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1
```

If `legends-captions` is not on PATH, use:

```powershell
python -m legends_ultimate_captions.cli doctor
```

## Transcript Sources

This module does not record or transcribe. Route recording and ASR outward:
`legends-ambient-intelligence` for recorded audio and offline transcription,
`hyperyap` for live dictation, `legends-yt-dlp` subtitle fetch for pulled
video. This skill starts where raw text exists.

## Current Boundary

The v0.1.0 package includes policy, tests, docs, and helper code. Full one-command
media intake, Parakeet orchestration, NFA orchestration, render packaging, and
proof-frame automation are next-phase work.
