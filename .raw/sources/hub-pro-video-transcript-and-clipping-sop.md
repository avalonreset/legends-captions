---
type: runbook
status: active
created: 2026-06-08
updated: 2026-06-12
tags:
  - transcripts
  - video-quest
  - diarization
  - clipping
  - live-sessions
  - youtube
  - sop
---

# Video Transcript and Clipping SOP

## Purpose

This is the first-stop operating procedure for AI Marketing Hub Pro video transcript, timestamp, diarization, search, and clipping work.

Use this page before answering requests like:

- "Do we have transcripts for every live-session replay?"
- "Release transcripts for all replay videos."
- "Find a moment in the video archive."
- "Cut testimonial, gratitude, VSL, or phrase-search clips."
- "Make a supercut from exact words."

## Current State

Fresh local check on 2026-06-08:

| Layer | Status |
|---|---|
| Local live-session MP4 downloads | 37 |
| MP4s with JSON transcript | 37/37 |
| MP4s with TXT transcript | 37/37 |
| MP4s with SRT captions | 37/37 |
| MP4s with VTT captions | 37/37 |
| MP4s with word-level timestamps | 37/37 |
| MP4s with Parakeet release transcript sets | 37/37 |
| MP4s with SortFormer `.speakers.json` | 37/37 |
| MP4s with speaker-aligned transcript JSON | 37/37 |
| Member-facing Markdown transcript package | [[assets/transcripts/live-sessions/index|37/37 staged]] |
| Canonical classroom replay lessons in current spine | 34 |
| Canonical lessons matched to local media/transcript evidence | 33/34 |
| Known canonical lesson-only gap | [[Live Session - 2025-11-04 AI Masterclass AI Strategy]] |

Interpretation:

- If the task is "release transcripts for every local live recording we have downloaded", the local evidence set is complete at 37/37.
- If the task is "release transcripts for every lesson in the canonical Live Sessions Archive classroom spine", first resolve or explicitly exclude the 2025-11-04 AI Strategy lesson-only gap.
- The 2026-06-07 Updated Classroom Workflow Q&A replay has local media, transcript, word timestamps, and diarization artifacts, but it is newer than the 34-lesson classroom spine snapshot and should be attached during the next replay crosswalk refresh.

## Canonical Roots

| Asset | Path |
|---|---|
| Legends Skool CLI repo | `E:\legends-skool-cli` |
| Live-session videos | `E:\legends-skool-cli\.legends-skool-cli\videos\downloads` |
| Live-session transcripts | `E:\legends-skool-cli\.legends-skool-cli\transcripts` |
| Live-session Parakeet release transcripts | `E:\legends-skool-cli\.legends-skool-cli\transcripts-parakeet-live` |
| Live-session diarization | `E:\legends-skool-cli\.legends-skool-cli\diarization\archive-full` |
| Live-session clips | `E:\legends-skool-cli\.legends-skool-cli\clips` |
| Member-facing transcript package | [[assets/transcripts/live-sessions/index|Live Session Transcript Markdown Package]] |
| Current replay index | [[Current Live Sessions Replay Index]] |
| Replay/media/transcript crosswalk | [[Video Quest Replay Media Crosswalk]] |
| Transcript artifact ledger | [[Video Quest Transcript Artifact Ledger]] |
| Clip and diarization ledger | [[Video Quest Clip and Diarization Ledger]] |
| Public YouTube channel archive | [[AgriciDaniel YouTube Channel Archive]] |

## Standard Stack

### Live-Session Recordings

Use Legends Skool CLI from `E:\legends-skool-cli`.

Transcription:

- Command: `transcripts:transcribe`
- Default backend: `--backend auto`
- Auto behavior: prefers NVIDIA Parakeet through NeMo when available, then falls back to faster-whisper.
- Default models in the CLI: `nvidia/parakeet-tdt-0.6b-v3` for Parakeet, `large-v3` for faster-whisper.
- Required output set for each replay: `.json`, `.txt`, `.srt`, `.vtt`, `.words.json`.
- Current release package source: WSL NVIDIA NeMo Parakeet `nvidia/parakeet-tdt-0.6b-v3`, chunked at 900 seconds with 2 seconds of overlap, written to `E:\legends-skool-cli\.legends-skool-cli\transcripts-parakeet-live`.
- Windows default Python currently only exposes faster-whisper. If Parakeet quality is required, use the WSL `/home/you/.venvs/legends-speech/bin/python` path or fold the temporary batch helper into the CLI before rerunning.

Diarization:

- Command: `transcripts:diarize`
- Model: NVIDIA SortFormer `nvidia/diar_streaming_sortformer_4spk-v2.1`
- Preferred runtime: WSL Python `/home/you/.venvs/legends-speech/bin/python`
- Required output set for each replay: `.speakers.json` and `.speaker-transcript.json`.
- Speaker labels are anonymous and session-local. Do not name a speaker from diarization alone.

Core commands:

```powershell
Set-Location -LiteralPath "E:\legends-skool-cli"

pnpm dev -- transcripts:transcribe `
  --file ".legends-skool-cli/videos/downloads/<session>.mp4" `
  --backend auto `
  --out-base ".legends-skool-cli/transcripts/<session>" `
  --pretty

pnpm dev -- transcripts:diarize `
  --file ".legends-skool-cli/videos/downloads/<session>.mp4" `
  --transcript ".legends-skool-cli/transcripts/<session>.json" `
  --wsl `
  --python "/home/you/.venvs/legends-speech/bin/python" `
  --out-base ".legends-skool-cli/diarization/archive-full/<session>" `
  --pretty
```

### Public YouTube Channel Archive

Use Legends YT-DLP Slayer for the public AgriciDaniel channel archive. The 2026-06-08 archive is already complete and should not be redownloaded unless the goal is to refresh new uploads.

Canonical channel control page: [[AgriciDaniel YouTube Channel Archive]].

Canonical Slayer manifest:

```text
E:\legends-yt-dlp-slayer\batches\20260608-001248-agricidaniel-youtube-all-119-20260608\manifest.json
```

Current channel transcript/search state:

- 119 visible channel items archived.
- 117 searchable word-ledger transcripts.
- 241,506 timestamped word rows.
- ASR was WSL NVIDIA NeMo Parakeet `nvidia/parakeet-tdt-0.6b-v3`.
- No public-channel diarization pass has been generated yet.

Exact phrase search:

```powershell
powershell -ExecutionPolicy Bypass -File "E:\legends-yt-dlp-slayer\scripts\slayer.ps1" intelligence search `
  "E:\legends-yt-dlp-slayer\batches\20260608-001248-agricidaniel-youtube-all-119-20260608\manifest.json" `
  "best practices" `
  --limit 25 `
  --json
```

Clip planning:

```powershell
powershell -ExecutionPolicy Bypass -File "E:\legends-yt-dlp-slayer\scripts\slayer.ps1" intelligence clips plan `
  "E:\legends-yt-dlp-slayer\batches\20260608-001248-agricidaniel-youtube-all-119-20260608\manifest.json" `
  --query "best practices" `
  --pad-before 0.15 `
  --pad-after 0.45 `
  --json
```

## Coverage Check

Run this before claiming live-session transcript coverage:

```powershell
$videoDir = "E:\legends-skool-cli\.legends-skool-cli\videos\downloads"
$transDir = "E:\legends-skool-cli\.legends-skool-cli\transcripts"
$diaDir = "E:\legends-skool-cli\.legends-skool-cli\diarization\archive-full"

$videos = @(Get-ChildItem -LiteralPath $videoDir -Filter "*.mp4" -File)
$rows = foreach ($v in $videos) {
  $base = $v.BaseName
  [pscustomobject]@{
    base = $base
    json = Test-Path -LiteralPath (Join-Path $transDir "$base.json")
    txt = Test-Path -LiteralPath (Join-Path $transDir "$base.txt")
    srt = Test-Path -LiteralPath (Join-Path $transDir "$base.srt")
    vtt = Test-Path -LiteralPath (Join-Path $transDir "$base.vtt")
    words = Test-Path -LiteralPath (Join-Path $transDir "$base.words.json")
    speakers = Test-Path -LiteralPath (Join-Path $diaDir "$base.speakers.json")
    speakerTranscript = Test-Path -LiteralPath (Join-Path $diaDir "$base.speaker-transcript.json")
  }
}

[pscustomobject]@{
  mp4 = $videos.Count
  completeTranscriptSets = @($rows | Where-Object { $_.json -and $_.txt -and $_.srt -and $_.vtt -and $_.words }).Count
  completeDiarizationSets = @($rows | Where-Object { $_.speakers -and $_.speakerTranscript }).Count
  missingTranscript = @($rows | Where-Object { -not ($_.json -and $_.txt -and $_.srt -and $_.vtt -and $_.words) } | Select-Object -ExpandProperty base)
  missingDiarization = @($rows | Where-Object { -not ($_.speakers -and $_.speakerTranscript) } | Select-Object -ExpandProperty base)
} | ConvertTo-Json -Depth 4
```

Expected current result: 37 MP4s, 37 complete transcript sets, 37 complete diarization sets, and no missing transcript or diarization bases.

## Transcript Release Workflow

When asked to release transcripts for the live-session archive:

1. Confirm the target scope: local downloaded MP4s, canonical classroom replay lessons, or both.
2. Run the coverage check above.
3. Compare against [[Current Live Sessions Replay Index]] and [[Video Quest Replay Media Crosswalk]].
4. Resolve or disclose [[Live Session - 2025-11-04 AI Masterclass AI Strategy]] if the target is every canonical classroom lesson.
5. Prefer the Parakeet release transcript set under `E:\legends-skool-cli\.legends-skool-cli\transcripts-parakeet-live` when it is complete.
6. Generate public-facing transcript files from `.txt`, `.vtt`, or segment JSON, not raw JSON dumps.
7. Include replay title, source lesson, transcript generation date, timecode policy, and an "AI-generated transcript, verify before quoting" note.
8. Use readable timecode anchors, not every caption line. The current package uses two-minute anchors.
9. Keep raw `.json`, `.words.json`, `.speakers.json`, signed URLs, cookies, HAR files, and browser material out of public packages.
10. If speaker labels are included, use anonymous session-local labels unless a human verifies names.
11. Before publishing quotes or tight clips, verify the audio/video around the timestamp manually.

Recommended transcript package shape:

```text
transcripts/
  2026-05-29-live-session-recording.md
  2026-05-29-live-session-recording.txt
  index.md
  manifest.json
```

Current staged package:

```text
<hub-pro-checkout>\wiki\assets\transcripts\live-sessions
```

## Clip Quality Rules

- Word-level timestamps are good enough for search and first-pass clip planning.
- For exact phrase supercuts, inspect waveform/audio and add small tail padding when needed.
- For testimonial or VSL clips, use 5 to 10 seconds of context padding unless the user explicitly wants tight phrase cuts.
- Use diarization to filter away the dominant host speaker, but verify the speaker by listening.
- Treat generated clips as review artifacts until approved by a human.
- For final Shorts exports, do not use video stream-copy for arbitrary timeline cuts unless stream start times are verified. AV1/H.264/HEVC copy cuts can preserve pre-roll packets or edit-list offsets, creating silent/random lead-in before the intended clip.
- After every generated clip, run `ffprobe` on stream `start_time` for video and audio. Both should start at `0.000000` or within a tiny encoder priming tolerance; any visible/audio gap is a reject.
- For captioned final clips from a newly exported or time-remapped raw file, do not mathematically retime old transcript timestamps unless the new media timeline has been proven with a phrase check. Treat old timestamps as editorial candidates only. Extract or transcribe the exact rendered clip audio, build word-level captions from that same zero-based clip clock, then render the video from the same start/duration.
- Current Braincraft Shorts source of truth: raw video `D:\Dbraincraft shorts raw v6 60fps no music.mp4`; active word timestamps `D:\braincraft_v6_only_production_20260609\transcript\braincraft_v6_full_parakeet.words.json`. Any other Braincraft transcript, manifest, render folder, or timestamp list is stale unless regenerated from this v6 source and manifest-proven.
- Current verified Braincraft v6 final batch: `D:\braincraft_v6_only_production_20260609\final_av1_music_chronological`, manifest `braincraft_v6_final_music_manifest.json`. The 2026-06-09 verification pass confirmed 9 chronological AV1 clips, 9 ASS sidecars, source video/source words both v6-only, `2160x3840`, `30/1` fps, AV1 video, AAC 48 kHz audio, randomized `-30 dB` music-bed offsets, and no stale v4/v5 production references in the final output folder.
- Current Braincraft boundary-QA extension: NVIDIA NeMo Forced Aligner (NFA) is now the preferred final in/out alignment pass before render. Start from editorial candidate windows, export padded WAV chunks, run NFA to generate word CTM files, then use `scripts\refine_braincraft_v6_nfa_boundaries.py` to snap candidate starts/ends around the aligned first and final words. Official NFA reference: [NVIDIA NeMo Forced Aligner](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/tools/nemo_forced_aligner.html).
- Before final Braincraft caption export, run a caption-gap audit on the generated ASS sidecar. Any caption event gap over normal pause length inside a retained speaking section must be checked against the source audio. If the audio has speech but the word-level transcript has no words, do not ship a blank-caption span; retranscribe or manually patch that exact source timestamp range and record the correction. The 2026-06-09 clip 5 failure was a Parakeet word-file hole around `1749.6s` to `1759.5s`, fixed by a source-v6-only manual insertion for `CLAUDE SEO`, `RANKENSTEIN.PRO`, and the following website-visual phrase.
- Current Opus Clip benchmark: [[Braincraft Opus Clip Benchmark 2026-06-09]]. Treat Opus-like services as recall benchmarks only: they can reveal candidate regions, but their scores, captions, title cards, and exported files are not production truth.

## Shorts Delivery Export Rules

Use these rules when producing final vertical clips for YouTube Shorts, TikTok, Reels, or Skool proof assets:

1. Plan clips from transcript timestamps first, but treat those cuts as editorial intent, not final export truth.
2. For review-only clips, stream-copy is acceptable if speed matters and pre-roll is tolerable.
3. For final clips, use frame-accurate re-encoding when cutting at non-container boundaries, changing speed, normalizing audio, changing frame rate, or fixing any stream offset.
4. Keep vertical 4K sources at `2160x3840` unless the user asks for a platform-size proxy.
5. Keep final output at constant 30 fps when the source is 30 fps, but reset timestamps before scaling them: `setpts=(PTS-STARTPTS)/<speed>,fps=30`.
6. For a 1.1x speedup without pitch shift, prefer Rubber Band when FFmpeg has it: `rubberband=tempo=1.1:pitch=1:formant=preserved`. Reset audio timestamps with `asetpts=PTS-STARTPTS` before and after the audio chain, and follow Rubber Band with explicit `aformat` because Rubber Band/loudnorm can leave FFmpeg without a channel layout on Windows.
7. Normalize after retiming, then force delivery audio to 48 kHz stereo.
8. Verify with `ffprobe`, a short decode, and frame thumbnails/contact sheet before calling the batch done.
9. For burned captions, verify transcript origin in the render manifest: `source media path`, `clip start`, `clip duration`, `ASR input audio path`, and `caption words JSON` must all describe the same clip clock. If any field came from an older source export, run a phrase search or fresh ASR before rendering.
10. For viral Shorts burned captions, do not render sentence-final periods or exclamation points by default. Preserve question marks, apostrophes, and useful transcript commas. Use caption group boundaries and line breaks to carry completed-sentence rhythm, and enforce a hard two-line maximum by splitting groups instead of allowing a third line. Apply known transcript corrections before ASS generation and record them in the render note or layout manifest.
11. For smart gap removal, build an edit decision list from transcript comprehension, not only detected silence. Cut dead air, repeated setup, false starts, repeated emphasis words, and low-value detours when the thesis still reads cleanly, but treat semantic boundaries as candidates only. Before rendering, inspect the waveform and snap every remove/keep boundary to a low-energy valley or zero-crossing neighborhood; reject micro-cuts inside continuous speech unless there is a clean acoustic boundary. Use hard visual cuts for momentum, but protect speech audio with short `8ms` to `15ms` crossfades at joins. Rebuild burned captions from the tightened edit clock, not the pre-cut clock. Verify final video/audio stream durations with `ffprobe`, and verify join quality with either a listen pass or an audio join report that checks RMS/peak/sample-step behavior around each crossfade. If the visual stream ends before the audio after a screen-recording cut, pad the video tail before ASS burn-in so the final words and captions still render.
12. If animated backgrounds, cursor motion, screen recordings, or visible presenter posture make hard visual cuts distracting, test smart gap compression before deleting pauses. Keep speech at `1x`, compress only confirmed dead-air interiors at a fixed speed such as `4x`, and keep `30ms` to `50ms` normal-speed guards on both sides of spoken words. This preserves visual continuity but saves less time than hard removal; record the tradeoff in the render report.

## Braincraft Shorts Captioned Clip Formula

This formula is the active production baseline for Braincraft v6-only Shorts unless the user explicitly changes the style.

Boundary rule: transcript word timestamps are first-pass planning data. When NFA is available, final Braincraft clip windows must pass through NFA CTM alignment before 4K render. Never accept an outpoint that lands inside the aligned final word; extend through the final word plus a small endpoint guard, but cap before the next aligned phrase if the next phrase would change the clip's thought.

1. Start from the exact current raw export being rendered. Old timestamps from earlier raw exports are editorial candidates only, never source of truth.
2. Pick complete logical modules from transcript and editorial intent. The hook should begin on a natural phrase and the outpoint should resolve the thought cleanly.
3. Render each selected module as one continuous source window. Do not apply smart gap removal, dead-air compression, speed ramps, hard-cut micro edits, or global retiming unless the user explicitly re-enables that experiment.
4. Optimize engagement through discerning in/out points and clip selection, not internal truncation. If a module only works after many internal edits, skip it or mark it as experimental.
5. Captions must come from the current source timeline used for the render. Build caption events from current-source word timestamps, then burn them into the same start/duration window.
6. Do not reuse pre-cut caption timings without a current-source phrase check and an explicit timeline mapping. If any caption source came from a different raw export, rerun ASR or remap from the verified current raw words.
7. Captions must be continuous through natural retained silence. Word-duration-only ASS events are a reject for this style because they can create visible blanks at pauses even when the timestamps are technically synchronized.
8. Music is opt-in for the pure Braincraft clean batch. Add a bed only after the user asks for it and after speech timing and caption visibility are locked.
9. If the user re-enables gap editing, treat it as an experimental branch: inspect waveform valleys, avoid cuts inside speech, use short audio crossfades, rebuild captions on the edited clock, and run a listen/visual join QA before delivery.
10. Do not default to gap removal, dead-air compression, speed ramps, or transcript-only internal cuts for Braincraft production. Use clean in/out points first.
11. If internal edits are requested later, run them as a separate experimental branch with waveform-aware boundaries, rebuilt caption timing, and a separate manifest.
12. Preserve the source raw untouched and write a manifest with source media path, start, duration, caption source, codec, score, and editorial rationale.
13. Caption style: all caps, Montserrat Black, white text, cyan active word, heavy black outline/drop shadow, centered at `x=1080`, `y=2760` on `2160x3840`.
14. Caption layout: hard maximum of two lines, approximately `156` font size for 4K vertical, sentence rhythm carried by group boundaries and line breaks.
15. Punctuation policy: remove sentence-final periods and exclamation points; preserve question marks, useful commas, and apostrophes in contractions and possessives. Do not flatten words such as `LET'S`, `WE'RE`, `I'M`, `DON'T`, or `CHRIS'S`. Entity punctuation is allowed when it changes the meaning, such as `RANKENSTEIN.PRO` or `CLAUDE-SEO.MD`. Record manual transcript fixes in the render manifest. Caption-only cleanup is allowed for obvious ASR display artifacts, but the manifest must retain the original ASR source.
16. Delivery source should stay vertical 4K. For this Braincraft workflow, use AV1 for final deliverables when the user has prohibited H.264; create a lower-cost proxy only if explicitly requested, and record the codec choice in the render manifest.
17. When a music bed is requested, mix it only after the captioned video is locked. Keep the captioned AV1 video stream with `-c:v copy`, mix the original speech with a randomized music offset at `-30 dB`, force AAC 48 kHz stereo, and record the music source, random seed, offset, and volume in the final manifest.
18. Default deliverable is one final captioned music-bed MP4 plus its edit/music manifest. A no-music intermediate may be created only for troubleshooting, but it is not a normal deliverable and should be deleted after the final music batch verifies unless the user explicitly asks to keep it.
19. QA before calling a clip done: run `ffprobe`, inspect the opening hook frame plus at least one mid-clip frame and one end-frame, confirm burned captions are present and legible with no blinking blanks, confirm audio begins at the intended hook, verify video and audio start at `0.000000`, record any music offset only when music is mixed, and preserve the source raw untouched.
20. Reject and rerender if the visible first hook does not match the intended phrase, if the caption text belongs to a different spoken section, if captions disappear and then repeat the same text at a tightened gap, or if any render manifest field points to a different raw/export/timeline than the final video.
21. For final clip windows, validate both boundaries against word-level timestamps before rendering. Prefer NFA CTM alignment over raw ASR word timestamps for the final boundary pass. Do not cut inside the first or final aligned word; if the outpoint is close to the final word end, extend the window by a small endpoint guard unless it would pull in the next spoken phrase. Inspect an end-frame proof when a user flags a missing last word.
22. Named entities, domains, product names, and obvious ASR homophone errors should be fixed through timestamp-specific manual overrides, not broad global replacements unless the correction is universally safe. When a correction changes phrase readability, add a caption group-break override and proof it on a rendered frame. For adjacent split product names such as `Fire` + `Crawl`, override the first token to the full entity and suppress the second token at its exact timestamp, then proof a rendered frame.
23. Run a two-pass selection process for longform-to-Shorts batches. First produce 8 to 12 hero clips with complete thoughts and strong source confidence. Then run an expanded-recall pass for 5 to 10 additional candidates from secondary transcript regions, competitor/Opus-discovered regions, or lower-confidence but interesting ideas. Do not inflate the final batch to 30+ clips unless the extra clips clear the same boundary, caption, and coherence gates.
24. Optional hook cards may be tested, but they are not the default Braincraft style. If used, keep the card to roughly `2.5s` to `4.0s`, allow speech underneath, avoid watermarks and emojis, keep copy honest, and ensure the card does not cover critical UI. Prefer a restrained title card or small hook placard over noisy social-template overlays.

Current clean-module 4K AV1 command pattern for Braincraft v6-only production:

```powershell
ffmpeg -y -hide_banner `
  -ss <start_seconds> -i "<source.mp4>" -t <duration_seconds> `
  -filter_complex "[0:v]setpts=PTS-STARTPTS,fps=30,ass=filename='<captions.ass>'[v];[0:a]asetpts=PTS-STARTPTS,loudnorm=I=-14:LRA=11:TP=-1.5,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a]" `
  -map "[v]" -map "[a]" -shortest `
  -c:v libsvtav1 -preset 10 -crf 24 -pix_fmt yuv420p10le `
  -c:a aac -b:a 192k -ar 48000 `
  -movflags +faststart "<output.mp4>"
```

NFA boundary pass pattern before final render:

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

Optional 4K AV1 1.1x command pattern. Do not use this for clean-module batches unless the user asks for retiming:

```powershell
ffmpeg -y -hide_banner `
  -ss <start_seconds> -i "<source.mp4>" -t <duration_seconds> `
  -filter_complex "[0:v]setpts=(PTS-STARTPTS)/1.1,fps=30[v];[0:a]asetpts=PTS-STARTPTS,rubberband=tempo=1.1:pitch=1:formant=preserved,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,loudnorm=I=-14:LRA=11:TP=-1.5,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a]" `
  -map "[v]" -map "[a]" -shortest `
  -c:v libsvtav1 -preset 10 -crf 18 -pix_fmt yuv420p10le `
  -c:a aac -b:a 192k -ar 48000 `
  -movflags +faststart "<output.mp4>"
```

Final music-bed mix pattern after captions are burned and approved:

```powershell
ffmpeg -y -hide_banner `
  -i "<captioned-av1.mp4>" `
  -ss <random_music_offset_seconds> -i "<music-bed.mp3>" `
  -filter_complex "[0:a:0]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,volume=1.0[voice];[1:a:0]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,volume=-30dB,afade=t=in:st=0:d=0.25,afade=t=out:st=<duration_minus_0.35>:d=0.35[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=0,alimiter=limit=0.95,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[a]" `
  -map 0:v:0 -map "[a]" `
  -c:v copy `
  -c:a aac -b:a 192k -ar 48000 `
  -movflags +faststart -shortest "<final-output.mp4>"
```

Verification pattern:

```powershell
ffprobe -v error `
  -show_entries stream=codec_type,codec_name,start_time,duration,width,height,pix_fmt,sample_rate,r_frame_rate,avg_frame_rate `
  -show_entries format=duration `
  -of json "<output.mp4>"
```

Reject and rerender if:

- video starts at `0.000000` but audio starts later, because the viewer will see silent/random pre-roll;
- audio starts at `0.000000` but video starts later, because the viewer will hear audio before the intended frame;
- output frame rate is not `30/1` for a 30 fps source;
- output audio is not 48 kHz stereo for delivery;
- the first thumbnail/frame does not visually match the intended hook.

## Known Gaps and Cautions

- The 2025-11-04 AI Strategy replay exists in the canonical classroom spine but has no matched local MP4/transcript evidence in the current Video Quest crosswalk.
- The June 7 replay has complete local artifacts but should be attached to the canonical matrix during the next crosswalk refresh.
- The YouTube channel archive has timestamped transcripts and search, but no diarization pass yet.
- The local Slayer CrispASR binary was found to be CPU-only during the 2026-06-08 channel run; WSL NeMo Parakeet was used for the high-throughput channel transcript pass.
- Long live-session Parakeet transcription should use chunking and per-video process resets. Whole-file or repeated in-process NeMo timestamp transcription produced CUDA instability on long recordings during the 2026-06-08 release pass.

## Related

- [[Transcript Evidence Library]]
- [[Live Session Video Evidence and Transcript Runbook]]
- [[Video Quest Replay Media Crosswalk]]
- [[Video Quest Transcript Artifact Ledger]]
- [[Video Quest Clip and Diarization Ledger]]
- [[Live Session Transcript Release Package]]
- [[AgriciDaniel YouTube Channel Archive]]
- [[YouTube and Shorts Operations]]
