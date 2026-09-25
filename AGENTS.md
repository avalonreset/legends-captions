# Legends Captions Agent Instructions

This project is the standalone caption system for Avalon Reset and Hub Pro video production. Work from the project brain first, then the code.

## Boot Sequence

1. Read `wiki/hot.md`.
2. Read `wiki/index.md`.
3. Read the active policy page for the task, usually `wiki/policies/Caption Intelligence Policy.md`.
4. Check `configs/default_vertical_4k60.json` before changing caption style defaults.
5. Preserve anything under `.raw/`; treat it as source evidence.

## Operating Standard

- Prefer real artifacts over memory: manifests, word JSON, CTM files, ASS files, proof frames, and ffprobe output.
- Parakeet is the preferred ASR text-quality layer.
- NeMo Forced Aligner is the preferred final word-boundary layer.
- Do not rebuild captions from stale timelines.
- Do not silently flatten spoken acronyms if per-letter highlight timing is available.
- Fix obvious ASR errors using context, but record the correction.
- If the audio is genuinely ambiguous, flag it for review instead of inventing certainty.

## Code Changes

- Keep policy changes small and regression-tested.
- Add or update a test for every recurring caption correction.
- Keep renderer changes separate from policy changes when practical.
- Use manifests to explain any text correction, virtual token, grouping override, or timing fallback.

## QA Before Done

- Run the policy tests.
- Run `python -m legends_captions.cli doctor`.
- For real renders, verify ffprobe output and proof frames from the final file, not just ASS previews.

## Release Packaging

- Keep `README.md`, `CHANGELOG.md`, `docs/release-checklist.md`, `skills/cto-legends/SKILL.md`, and `AGENTS.md` aligned.
- Skool release drafts live under `release/skool/`; Hub Pro mirror drafts may live under `E:\ai-marketing-hub-pro\wiki\drafts\skool`.
- Release art lives under `release/art/`; `assets/banner.webp` is the current README banner.
- Do not publish to Skool until repo and release URLs are real and the user approves the copy/art.
