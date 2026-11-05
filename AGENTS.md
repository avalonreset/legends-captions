# Legends Captions Agent Instructions

Start with [docs/AGENT-RECIPE.md](docs/AGENT-RECIPE.md), [wiki/hot.md](wiki/hot.md), and [wiki/index.md](wiki/index.md).

## Boot Sequence

1. Read [docs/AGENT-RECIPE.md](docs/AGENT-RECIPE.md) for the CLI command table and guardrails.
2. Read [wiki/hot.md](wiki/hot.md) and [wiki/index.md](wiki/index.md).
3. Read the active policy page for the task, usually [wiki/policies/Caption Intelligence Policy.md](wiki/policies/Caption%20Intelligence%20Policy.md).
4. Check `configs/default_vertical_4k60.json` before changing caption style defaults.
5. Preserve anything under `.raw/`; treat it as source evidence.

## Operating Standard

- **Single Router Skill**: Discovery belongs to `skills/cto-legends/SKILL.md`. Do not add secondary skills under `skills/`.
- Prefer real artifacts over memory: manifests, word JSON, CTM files, ASS files, proof frames, and ffprobe output.
- Parakeet is the preferred ASR text-quality layer; NeMo Forced Aligner is the preferred final word-boundary layer.
- Do not rebuild captions from stale timelines or silently flatten spoken acronyms if per-letter highlight timing is available.
- Fix obvious ASR errors using context, record the correction in a manifest, and add or update a test for every recurring caption correction.

## EDR and Security Guardrails

1. **No Hidden Spawns or Bypass Wrappers**: Never spawn background shells, hidden console windows, or execution-policy bypass shell wrappers, and never add `.ps1`, `.bat`, or `.cmd` wrapper scripts.
2. **No Browser Profile or Credential Store Probing**: Never read local browser profile databases, DPAPI stores, or third-party credential stores outside the project workspace.
3. **Zero Secret Exposure**: Never print or log secret values or tokens to stdout, logs, or Markdown receipts.
4. **Controlled File Writes**: Keep `render-ass` outputs limited to explicit `--output` and `--manifest-output` paths inside the workspace.

## QA Before Done

- Run `python scripts/check_release.py`.
- Run `python -m unittest discover -s tests -v`.
- Run `python -m legends_captions.cli doctor`.
