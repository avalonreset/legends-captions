# Changelog

## v0.1.4 - 2026-11-11

- Add `legends-captions ffmpeg-filter --ass <path> [--json]` (`escape_ffmpeg_ass_filter`, `format_ffmpeg_ass_filtergraph`) to deterministically escape Windows drive colons, backslashes, quotes, and `libavfilter` metacharacters (`CWE-88`), and escape tokens with `escape_ass()` in `.raw/sources/avalon-build-vertical-active-word-captions.py`.
- Harden `cli.py` with wheel-safe `resolve_project_root()` and `importlib.resources` packaged config lookup, symlink refusal (`CWE-59`), file size caps (`<= 1 MiB` for `--config`, `<= 25 MiB` for `--input`, `CWE-400`), non-finite JSON rejection (`NaN`/`Infinity`), and fail-closed `--overwrite` atomic writes on `render-ass` (Law 2).
- Harden `ass_builder.py` (`AssStyle`, `AssEvent`, `ass_time`, `escape_ass`, `build_ass_document`) against style/font comma/newline injection (`CWE-74`), raw `\r` carriage-return splitting, and non-finite or out-of-range timestamps/canvas bounds (`CWE-20`).
- Remove private workstation session paths from `scripts/stage_*.py`, align `README.md`, `docs/install/agent-install-guide.md`, `.env.example`, and `docs/AGENT-RECIPE.md` 1:1 with actual CLI capabilities, add `MANIFEST.in` for complete sdist parity, and upgrade `scripts/check_release.py`.

## v0.1.3 - 2026-11-05

- Add `docs/AGENT-RECIPE.md` with full 1:1 CLI command parity (`doctor`, `policy-report`, `normalize`, `render-ass`) and explicit EDR and Security Guardrails.
- Add `THIRD_PARTY_NOTICES.md`, `assets/preview.png` (`1024x256`), `assets/manifest.json`, and `scripts/check_release.py` Gold Standard offline release gate.

## v0.1.2 - 2026-11-04

- Add `legends-captions render-ass` CLI subcommand to build deterministic active-word or line `.ass` subtitle documents and correction manifests directly from inline text or timed JSON word/segment inputs.
- Standardize test execution and transcript search documentation across `README.md`, `CONTRIBUTING.md`, `docs/install/agent-install-guide.md`, and `.raw/sources/` on direct cross-platform Python CLI invocations without legacy PowerShell test wrapper scripts.

## v0.1.1 - 2026-10-29

- Raise minimum supported Python runtime to Python 3.11 (`requires-python = ">=3.11"`) across package metadata, documentation, and multi-OS CI.
- Harden GitHub Actions workflows with 40-character commit SHA action pins, explicit `contents: read` permissions, and `pip>=26.2.2` before package installation.

## v0.1.0 - 2026-09-25 - Router-native reset

- Reset to the router-native generation: `cto-legends` is the only registered skill, this repo vendors a pinned copy at `skills/cto-legends/SKILL.md` (router commit `6975dcbf073e5eec7a30ce6a04a6975238c61158`).
- Removed the per-module skill surface: `skills/legends-captions/`, the `.claude/skills/` mirror, `CLAUDE.md`, `CODEX.md`, `GEMINI.md`, and `gemini-extension.json`.
- Added the contract agent block to `README.md`, `.legends-module`, and contract CI.

## v0.2.0 - Renamed to Legends Captions

- Renamed the project from Legends Ultimate Captions to Legends Captions.
- Renamed the Python package `legends_ultimate_captions` to `legends_captions` and the skill slug to `legends-captions`.
- Regenerated the promoted banner and social preview with the new title.
- Added an acknowledgments section covering provenance and third-party tools.
- The CLI command is unchanged: `legends-captions`.

## v0.1.0 - Initial Public Release

- Created the standalone Legends Ultimate Captions project.
- Added the first contextual caption policy engine.
- Added regression tests from real SoulX FlashFace caption fixes.
- Added active-word ASS helper functions.
- Added correction manifests and CLI commands.
- Added Codex, Claude, Gemini, and portable Agent Skills surfaces.
- Added Codex Obsidian brain pages for policy, QA, revision learning, and release planning.
- Added Skool release drafts, promotional copy, banner concepts, and square meme art options.

