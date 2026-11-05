# Operating legends-captions

This is an on-demand module recipe, not a registered skill. The central `cto-legends` router owns discovery.

## Select knowledge first

Read [wiki/hot.md](../wiki/hot.md), [wiki/index.md](../wiki/index.md), and [Caption Intelligence Policy](../wiki/policies/Caption%20Intelligence%20Policy.md) before changing caption policy rules or style defaults (`configs/default_vertical_4k60.json`).

## Readiness

1. Run `legends-captions doctor` (or `python -m legends_captions.cli doctor`). This is offline, free, and reports the package version, default config profile (`configs/default_vertical_4k60.json`), preserved `.raw/sources` count, Python executable, and optional `ffmpeg` / `ffprobe` paths on `PATH`.
2. Inspect active contextual correction rules with `legends-captions policy-report`.
3. Preview normalization and correction manifests with `legends-captions normalize` before rendering `.ass` subtitle files with `legends-captions render-ass`.

| Goal | Command | Interpretation |
|---|---|---|
| Offline readiness & tool check | `doctor [--config PATH]` | Verifies Python 3.11+, default caption style config, and optional `ffmpeg`/`ffprobe` binaries |
| Inspect correction rules | `policy-report` | Prints JSON list of all contextual ASR phrase replacement rules, categories, and reasons |
| Normalize caption text | `normalize [--uppercase] [--manifest] TEXT...` | Applies contextual ASR correction policy and prints normalized caption text or a JSON correction manifest |
| Render active-word or line ASS | `render-ass [TEXT...] [--input JSON] [--output ASS] [--manifest-output JSON] [--mode word\|line] [--start SEC] [--duration SEC] [--width PX] [--height PX] [--font NAME] [--font-size PT] [--uppercase]` | Applies caption policy to inline text or timed word/segment JSON and emits a deterministic `.ass` subtitle document plus optional correction manifest |

## EDR and Security Guardrails

1. **Zero Hidden Console Spawning or Execution-Policy Bypass Wrappers**: Always invoke `legends-captions` or `python -m legends_captions.cli` directly with standard streams. Never spawn background shells, hidden console windows, or execution-policy bypass shell wrappers, and never ship `.ps1`, `.bat`, or `.cmd` wrapper scripts.
2. **Zero Browser Profile or External Credential Store Access**: Never read local browser profile databases, DPAPI stores, or third-party CLI credential stores. `legends-captions` is an offline caption policy and subtitle rendering engine and requires no network credentials.
3. **Zero Secret Exposure**: Never print or log secret keys or tokens to stdout, logs, or Markdown receipts.
4. **Explicit Single-File Output Writes**: `render-ass` defaults to `stdout` and writes only to the explicitly requested `--output` and `--manifest-output` paths inside the project workspace. Never run bulk uncontrolled file-overwrite loops.
