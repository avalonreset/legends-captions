---
type: policy
status: active
created: 2026-06-17
updated: 2026-06-17
tags:
  - captions
  - policy
  - asr
---

# Caption Intelligence Policy

## Principle

Captions should express the intended spoken meaning, not the most literal ASR guess. ASR is evidence. It is not the final editor.

## Required Intelligence Layers

1. Domain glossary correction.
2. Contextual model and product-name correction.
3. Grammar and idiom repair.
4. Spoken acronym timing.
5. Semantic grouping and line-break review.
6. Final-render proof-frame QA.
7. Correction manifest logging.

## Rules From Recent Production Feedback

### Domain Terms

Fix obvious model-training homophones when the context supports it.

- `low raw`, `low ra`, `low-ra` -> `LoRA`
- `C dance`, `sea dance` -> `Seedance`
- `Hey Gen` -> `HeyGen`
- `Soul X` -> `SoulX`
- `Flash Head` -> `FlashHead`
- `RTX4090` -> `RTX 4090`

### Contextual Phrase Repair

If a phrase only makes sense in the video's subject matter after a small repair, make the repair and record it.

- `it may not be as exacting 2.0` -> `it may not be as exciting as Seedance 2.0`
- `what is this unlock` -> `what does this unlock`
- `sticking the 30 frames a second` -> `sticking to 30 frames a second`

### Spoken Acronyms

If the speaker spells an acronym out letter by letter, preserve letter-level timing when available. Do not collapse `L O R A` into a single visual word if the active highlight can track each letter.

Acceptable render behavior:

- visual text may read `L O R A`;
- each letter can receive its own active highlight;
- the manifest records that this is spoken-acronym timing.

### Profanity And Strong Language

If the source says a strong word and the user's channel style allows it, do not sanitize it by accident. Fix joined-token or typo artifacts such as `fuckdown` -> `fuck down` when the sentence is clear. If platform policy or user intent is uncertain, flag for review rather than censoring silently.

### Grouping

Caption groups are semantic units. A legal max-width group can still be wrong if it creates misleading phrasing. Break around sentence boundaries, contrast pivots, and comedic beats. Avoid leaving a final preposition, article, or profanity fragment stranded on the wrong line.

### Confidence

Only automate repairs that are high confidence from context, glossary, or user-approved precedent. Ambiguous audio gets a review note.

