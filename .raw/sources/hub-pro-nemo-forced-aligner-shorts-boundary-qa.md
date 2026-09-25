---
type: source
status: active
created: 2026-06-12
updated: 2026-06-12
tags:
  - video-quest
  - clipping
  - shorts
  - forced-alignment
  - braincraft
---

# NeMo Forced Aligner for Shorts Boundary QA

## Purpose

NVIDIA NeMo Forced Aligner (NFA) is the Braincraft Shorts boundary-QA layer for final in/out points. It does not replace editorial clip selection. It runs after candidate windows are chosen and before final 4K render so the start and outpoint can be snapped around aligned first and final words.

Official references:

- [NVIDIA NeMo Forced Aligner docs](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/tools/nemo_forced_aligner.html)
- [NVIDIA NeMo Forced Aligner source README](https://github.com/NVIDIA/NeMo/tree/main/tools/nemo_forced_aligner)

## Local Setup

- Local NFA source checkout: `<hub-pro-checkout>\tmp\nemo-forced-aligner-src\tools\nemo_forced_aligner`
- WSL speech environment: `/home/you/.venvs/legends-speech`
- Confirmed stack: `nemo 2.7.3`, `nemo.collections.asr`, PyTorch with CUDA available, RTX 4090.
- Current model: `stt_en_fastconformer_hybrid_large_pc`
- Current Braincraft run output: `D:\braincraft_v6_only_production_20260609\nfa_v2_20260612`

The installed NeMo wheel did not expose the `tools/nemo_forced_aligner` command directly, so the current integration uses the sparse source checkout. The local source copy also needed a small helper patch in `utils/data_prep.py` so relative manifest audio paths resolve correctly.

## Braincraft Command Pattern

```powershell
python .\scripts\run_braincraft_v6_nfa_alignment.py `
  --candidate-json .\scripts\braincraft_v6_nfa_v2_candidates.json `
  --output-dir "D:\braincraft_v6_only_production_20260609\nfa_v2_20260612" `
  --clean-nfa-output --run

python .\scripts\refine_braincraft_v6_nfa_boundaries.py `
  --nfa-dir "D:\braincraft_v6_only_production_20260609\nfa_v2_20260612" `
  --out-json .\scripts\braincraft_v6_nfa_v2_refined_candidates.json `
  --comparison-json .\scripts\braincraft_v6_nfa_v2_comparison.json
```

## Boundary Policy

- Candidate timestamps from Parakeet or transcript search are editorial candidates only.
- NFA word CTM files are the preferred final boundary evidence when available.
- Starts should land before the first aligned spoken word, with a short guard.
- Outpoints should land after the final aligned word, with a short guard.
- Do not extend into the next aligned phrase if it changes the thought or pulls in the next clip.
- If NFA fails, record the fallback and use stricter waveform/listen/end-frame QA before shipping.
- The music pass happens only after the captioned video is locked; Braincraft music beds stay at randomized source offsets and `-30 dB`.

## Current Braincraft V2 Artifacts

- Editorial candidates: `<hub-pro-checkout>\scripts\braincraft_v6_nfa_v2_candidates.json`
- NFA-refined candidates: `<hub-pro-checkout>\scripts\braincraft_v6_nfa_v2_refined_candidates.json`
- Old-vs-new comparison JSON: `<hub-pro-checkout>\scripts\braincraft_v6_nfa_v2_comparison.json`
- NFA CTM words: `D:\braincraft_v6_only_production_20260609\nfa_v2_20260612\nfa_output\ctm\words`
- Clean captioned 4K renders: `D:\braincraft_v6_only_production_20260609\clean_av1_clips_nfa_v2_20260612`
- Final music-bed renders: `D:\braincraft_v6_only_production_20260609\final_av1_music_nfa_v2_20260612`
