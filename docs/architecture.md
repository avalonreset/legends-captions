# Legends Captions Architecture

## Layers

1. Media intake: identify the exact final video clock and preserve raw inputs.
2. ASR: use Parakeet for high-quality text and word candidates.
3. Policy correction: apply glossary, contextual phrase repair, acronym handling, and review exceptions.
4. Alignment: use NFA CTM as final timing authority when precision matters.
5. Grouping: build semantic caption chunks with a hard visual style contract.
6. Rendering: generate ASS and burn captions into the delivery file.
7. QA: produce manifests, ffprobe output, and final-render proof frames.
8. Learning: convert user fixes into policy, config, and tests.

## Package Contract

A production caption run should eventually produce:

```text
run/
  input_manifest.json
  transcript_parakeet.words.json
  alignment_nfa.ctm
  captions.ass
  correction_manifest.json
  render_manifest.json
  ffprobe_final.json
  proof-frames/
  final_captioned.mp4
```

## Current V0.1 Scope

This first scaffold implements the policy/correction layer, cross-agent brain, glossary seed, ASS document helpers, and regression tests. Full media intake, NFA orchestration, render packaging, and proof-frame automation are the next implementation phase.

