---
type: qa
status: active
created: 2026-06-17
updated: 2026-06-21
tags:
  - captions
  - qa
  - checklist
---

# Caption QA Checklist

## Text

- Proper nouns and model names are correct.
- Acronyms are displayed intentionally.
- Grammar repairs improve meaning without inventing unsupported words.
- Strong language matches user/channel intent.
- Punctuation does not clutter active-word captions.

## Timing

- First highlighted word is not late.
- Final highlighted word is not cut off.
- Spelled acronyms can highlight per letter when possible.
- Caption holds cover natural pauses without blinking.
- Edited Shorts reset bottom caption groups at known hard cuts.
- No bottom caption event crosses a hard cut unless the manifest documents a creative exception.
- Short tail ends about three frames after the final spoken word unless a deliberate hold is documented.

## Layout

- Maximum two lines.
- Text stays inside the approved safe zone.
- Bubble width fits text with consistent padding.
- Bubble backdrop uses the current default 75% opacity black fill unless the user explicitly asks for solid.
- Apparent left/right bubble padding matches the apparent bottom padding; no line feels tight against the side edges.
- Active color is visible against the footage.
- Upper editorial captions, when used, are brief static-yellow topic markers near the upper quarter.
- Upper editorial captions do not duplicate the bottom speech lane or overlap each other.

## Artifact Evidence

- Source video path recorded.
- Transcript source recorded.
- Timing source recorded.
- Correction manifest saved.
- ffprobe output saved.
- Final-render proof frames inspected.
- Known cut-boundary list saved for edited Shorts.
- Caption manifest reports cut-crossing count and invalid-event count.
