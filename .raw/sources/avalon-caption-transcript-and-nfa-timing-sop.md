---
type: sop
status: active
created: 2026-06-13
updated: 2026-06-17
tags:
  - captions
  - transcripts
  - parakeet
  - nfa
  - nemo
  - timecodes
---

# Caption Transcript and NFA Timing SOP

## Purpose

Use this for captioned YouTube videos, Shorts, accurate transcripts, phrase search, and final timing QA.

This note is adapted from the AI Marketing Hub Pro video SOP, but narrowed for Avalon Reset YouTube production.

## Preferred Stack

ASR:

- Preferred: WSL NVIDIA NeMo Parakeet `nvidia/parakeet-tdt-0.6b-v3`
- WSL Python: `/home/you/.venvs/legends-speech/bin/python`
- Use chunked transcription for long recordings.
- Avoid Windows Anaconda for this stack when Parakeet quality is required; prior runs hit OpenMP/DLL issues.

Timing:

- Preferred final boundary authority: NVIDIA NeMo Forced Aligner (NFA)
- Local NFA source checkout in Hub Pro: `<hub-pro-checkout>\tmp\nemo-forced-aligner-src\tools\nemo_forced_aligner`
- Use Parakeet word timestamps for first-pass caption groups.
- Use NFA CTM alignment when exact start/end timing matters.
- For karaoke-style highlights, keep NFA as the source of truth but lead the visible highlight slightly earlier than the aligned word start. Stable Audio 3 testing settled on roughly `0.08s` to `0.10s` for 60 fps exports.
- Do not create tiny blank flashes between nearby spoken phrases. Hold the current caption through short gaps up to roughly `0.85s`; hide captions only when speech clearly stops.

Fallback:

- faster-whisper can be used for a quick transcript or repair pass.
- If NFA is unavailable, record the fallback and use stricter proof-frame/listen QA.

## Caption Layout Policy

Always mock up the layout before burning final captions when the user asks for approval.

## Approved Bubble Caption Standard

Use this as the default Avalon Reset caption style unless the user asks for a different format:

- Max lines: `2`
- Text case: all caps
- Font: Montserrat Black
- Visible ASS text size: `\fs118`
- ASS bubble-measurement calibration: measure Montserrat Black at `85px` for bubble geometry when using ASS `\fs118`
- Text vertical correction: `-6px` from the geometric bubble center for the current Windows/libass path
- Text colors: white inactive words, cyan active word
- Contrast: rounded black per-line bubble backdrop; no heavy outline, no 3D drop shadow
- Bubble sizing: derive each bubble from the visible rendered glyph pixels, never from loose font metrics or a fixed full-width line slot
- Bubble padding: start at `24px` on all sides and verify the apparent margins on a flat-background ASS-rendered frame
- Bubble radius: start around `32px`; reduce before increasing padding if the corners feel too round
- Two-line stack: each line gets its own independent rounded bubble with proper roundness on all four corners. Do not join the two lines into one shape with square internal corners; preserving the bubble character is more important than making the internal edge perfectly linear.
- Line breaking: avoid orphan lines; rebalance phrases so a two-line caption does not leave one word alone on the second line
- Timing: use NFA CTM as timing authority and lead active-word highlight by about `0.08s` to `0.10s`
- Gap handling: hold captions across short speaking gaps up to about `0.85s`
- Production QA: render one flat-background ASS proof frame and measure actual text-to-bubble margins before rendering the full video

## Video Codec and Preservation Policy

- MP4 is allowed as a container, but do not encode production video as MPEG-4 Part 2, H.264, or generic `mp4v`.
- Avalon Reset production video exports should use the source video codec when practical; otherwise use HEVC or AV1 only.
- Always preserve the source resolution and frame rate unless the user explicitly asks for a format conversion.
- Do not add `scale`, crop, or `fps` filters unless they are required by the requested deliverable.
- Copy the source audio stream when only adding captions. Re-encode or normalize audio only when the user explicitly asks for audio changes.
- Verify the final codec, resolution, frame rate, and audio stream with `ffprobe` before handoff.

For the current square 4K Stable Audio 3 video:

- Source/output canvas: `2160x2160`
- Frame rate: preserve `60 fps`
- Caption position: lower quarter, approximately `x=1080`, `y=1620`, unless the user requests center placement
- Max lines: 2
- Style direction: bold, legible, high-contrast, not meme-chaotic
- Suggested font: Montserrat Black or Arial Black
- Suggested text: white text with cyan active word; avoid thick strokes or 3D shadows unless explicitly requested
- Bubble backdrop policy: use per-line dynamic rounded rectangles sized from the visible rendered text pixels, not loose font metrics or a fixed line slot. Center each bubble around its line with equal top, bottom, left, and right padding. Standard padding starts at `24px` on every side, and visual QA must confirm the apparent top and bottom padding match. For two-line captions, each line gets its own bubble width so narrower and wider lines are contoured independently.
- Two-line stack policy: avoid orphan lines. Do not create a second line with one word when the phrase can be rebalanced cleanly; prefer balanced splits like `THERE'S BEEN A` / `RIFT IN THE` over `THERE'S BEEN A RIFT IN` / `THE`. Draw each line as a separate fully rounded bubble, including the inner corners between the two lines. Do not use a single joined vector path with hard internal edges. If there is a minor seam tradeoff, prefer preserving the rounded bubble effect.
- ASS renderer calibration policy: do not assume PIL font pixels equal ASS `\fs` units. For the Stable Audio 3 square render, ASS `\fs118` with Montserrat Black measured closest to PIL `85px`. Use the calibrated measurement size for bubble geometry, then verify on a flat-background ASS-rendered mock-up. Current ASS vertical centering correction is about `-6px` so apparent top and bottom padding match.
- Active-word highlight is approved for the Stable Audio 3 review pass.
- Do not use heavy outline/drop-shadow styling for this square YouTube release. Use the bubble backdrop as the contrast system.

For vertical Shorts inherited from Braincraft:

- Canvas: `2160x3840`
- Caption anchor: centered at approximately `x=1080`, `y=2760`
- Style: all caps, Montserrat Black, white text, cyan active word, heavy black outline/drop shadow
- Hard maximum: 2 lines
- Approximate font size: `156` for 4K vertical

## Caption Text Policy

- Preserve Parakeet/NFA punctuation when it clearly belongs to the sentence, including sentence-ending periods.
- Preserve question marks, apostrophes, useful commas, percentage signs, and entity punctuation.
- Do not flatten contractions like `LET'S`, `WE'RE`, `I'M`, `DON'T`.
- Fix named entities with timestamp-specific overrides, not broad replacements unless universally safe.
- Use a domain glossary before rendering so near-sounding ASR errors can be corrected in context, such as `base` -> `ACE` near `1.5`.
- Run a contextual ASR correction pass before every ASS/render step. Treat Parakeet/NFA text as timing evidence, not final display copy.
- Correct high-confidence product names, model names, acronyms, GPU terms, and obvious homophones before burn-in, for example `low raw` / `low-ra` -> `LoRA`, `Soul X` -> `SoulX`, `Flash Head` -> `FlashHead`, `Hey Gen` -> `HeyGen`, `stable audio 3 media` -> `Stable Audio 3 Medium`, `RTX4090` -> `RTX 4090`, and `C dance` -> `Seedance` when the surrounding context supports it.
- When the speaker spells an acronym and NFA exposes separate letter timings, preserve those letters as separate caption tokens so the active-word highlight can move letter by letter. Example: keep `L O R A` as four timed display tokens instead of collapsing it into one `LoRA` token.
- Record every contextual spelling correction in the render manifest. If a correction is plausible but not certain, leave the ASR text alone and flag it in notes instead of silently guessing.
- Drop obvious false-start bridge words when the sentence is clearly cleaner without them and the extra word creates a visual flash; for example, `depends on what how much VRAM` should render as `depends on how much VRAM`.
- Remove low-value filler interjections from captions, especially `uh`, `um`, `uhh`, `umm`, `er`, and `ah`; keep the audio untouched, but do not spend caption space on these.
- Treat `like` as a judgment call, not a banned word. Keep meaning-bearing uses such as `sounds like`, `looks like`, `feels like`, `things like`, `something like`, or true verb use (`I like this`). Drop obvious filler or quote-padding uses such as sentence-leading `like`, `I was like,`, `it's like,`, `this is like`, and `gives you like` when the caption reads more cleanly without it.
- Record filler cleanup decisions in the render manifest so future captions can be audited when a removed word affects rhythm or meaning.
- Collapse immediate repeated words/stutters when they are visually unhelpful, such as `go, go` -> `go`; preserve useful punctuation from the collapsed repeat.
- Preserve intended signoffs and sound-effect words through contextual corrections, for example `Benjamin Owl` -> `Benjamin out` at the ending and `sounds like both` -> `sounds like boop`.
- Keep captions continuous through retained speaking sections; avoid blinking blanks at natural pauses.
- Hold the previous caption through short gaps, roughly up to `0.85s`; hide captions only when speech has clearly stopped.
- Rebuild captions from the final render clock if the video is cut or retimed.

## Export QA Rules

Before calling a captioned video upload-ready:

1. Run `ffprobe` and confirm resolution, fps, codec, audio, and stream start times.
2. Check an opening frame, mid frame, and end frame.
3. Confirm captions are legible and centered as intended.
4. Confirm captions belong to the actual spoken section.
5. Confirm no caption event creates unintended overlap, three-line text, or unreadable text.
6. Preserve a render manifest with source video path, transcript source, caption style, render settings, and output path.

## 4K60 Square HEVC Command Pattern

Use this pattern only after the mock-up is approved:

```powershell
ffmpeg -y -hide_banner `
  -i "<source.mp4>" `
  -filter_complex "[0:v]setpts=PTS-STARTPTS,ass=filename='<captions.ass>'[v]" `
  -map "[v]" -map 0:a:0 `
  -c:v hevc_nvenc -preset p5 -tune hq -rc vbr -cq 18 -b:v 45M -maxrate 80M -bufsize 160M `
  -pix_fmt yuv420p -tag:v hvc1 -fps_mode passthrough `
  -c:a copy `
  -movflags +faststart `
  "<output.mp4>"
```

For AV1 source material, use an AV1 encoder and verify the output remains AV1. Preserve source frame rate and resolution in either case.

## Related Hub Pro Notes

Source ideas were cherry-picked from:

- `<hub-pro-checkout>\wiki\sources\Video Transcript and Clipping SOP.md`
- `<hub-pro-checkout>\wiki\sources\NeMo Forced Aligner for Shorts Boundary QA.md`
