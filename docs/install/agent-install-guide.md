# Agent Install Guide

Legends Captions installs through the `cto-legends` router. The Python
package provides the commands; the router loads this repo's README plus the
policy pages as the module recipe. This module is never registered as its
own skill.

## Router install

```text
cto-legends install legends-captions
```

Then set up the repo:

```powershell
git clone https://github.com/avalonreset/legends-captions.git
Set-Location -LiteralPath .\legends-captions
python -m pip install -e .
python -m legends_captions.cli doctor
```

## Deterministic CLI commands

Use the built-in Python CLI subcommands directly instead of improvising shell pipelines:

```sh
legends-captions --version
legends-captions doctor
legends-captions policy-report
legends-captions normalize --uppercase "low raw teaches the model"
legends-captions normalize --manifest "L O R A."
legends-captions render-ass --uppercase "low raw teaches the model"
legends-captions render-ass --input transcript.words.json --output captions.ass --manifest-output correction_manifest.json --uppercase --overwrite
legends-captions ffmpeg-filter --ass captions.ass
```

Recommended prompt:

```text
Use Legends Captions to inspect this transcript, apply contextual correction
policy, build active-word ASS captions and correction manifests with
legends-captions render-ass, and review any flagged terms before final render.
```

Start with the `doctor` command, inspect active rules with `policy-report`, normalize or generate `.ass` subtitles and manifests with `normalize` and `render-ass`, format escaped FFmpeg filtergraph strings with `ffmpeg-filter --ass <path>`, and review any flagged ASR errors before final render.

## External ASR and Alignment Notes

`legends-captions` is a pure-stdlib offline policy and `.ass` rendering engine that requires zero environment variables or network credentials. When generating upstream word-timed JSON or CTM inputs before running `legends-captions render-ass`, the preferred ASR layer is NVIDIA NeMo Parakeet (`nvidia/parakeet-tdt-0.6b-v3`) and the preferred final word-boundary authority is NeMo Forced Aligner (NFA) CTM output.
