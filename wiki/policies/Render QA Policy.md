---
type: policy
status: active
created: 2026-06-17
updated: 2026-06-21
tags:
  - captions
  - qa
  - render
---

# Render QA Policy

## Required Evidence

Before a captioned video is called done, preserve:

- final video path;
- source media path;
- caption source path;
- correction manifest;
- render manifest;
- ffprobe output;
- opening proof frame;
- at least one middle proof frame;
- at least one end proof frame.
- for edited Shorts, proof frames at each known hard cut and at the final spoken word/tail.

## Reject Conditions

Rerender if:

- captions belong to the wrong spoken section;
- a proper noun or model name is visibly wrong;
- active highlight timing is clearly late or early;
- captions disappear during retained speech;
- text exceeds two lines in the approved active-word style;
- final output points at stale source media, stale transcript, or stale timing files;
- audio or video starts with unintended pre-roll.
- a bottom speech-caption event crosses a known hard cut without an explicit creative exception;
- upper editorial captions overlap each other or duplicate the bottom speech lane;
- a Shorts render hangs for a second or more after the final spoken word without a deliberate visual reason.
