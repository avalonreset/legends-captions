---
type: playbook
status: active
created: 2026-06-17
updated: 2026-06-17
tags:
  - captions
  - deployment
  - playbook
---

# One Revision Caption Deployment

Goal: most caption jobs should need zero or one user revision.

## Flow

1. Inspect the video and infer the subject matter.
2. Extract or receive audio from the exact final video clock.
3. Run Parakeet for high-quality text and word candidates.
4. Apply glossary and contextual ASR correction.
5. Run or ingest NFA CTM timing when exact word timing matters.
6. Build caption groups from meaning, not only word count.
7. Render ASS captions with approved visual style.
8. Generate proof frames from the final video.
9. Run ffprobe and manifest checks.
10. Review proof frames for model names, grammar, line breaks, and active highlight sanity.
11. Deliver final video plus manifests and call out any review exceptions.

## Revision Intake

When the user flags fixes:

- patch the caption text or timing;
- rerender the final;
- update the manifest;
- convert the lesson into policy or tests when reusable.

