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
legends-captions doctor
legends-captions policy-report
legends-captions normalize --uppercase "low raw teaches the model"
legends-captions normalize --manifest "L O R A."
legends-captions render-ass --uppercase "low raw teaches the model"
legends-captions render-ass --input transcript.words.json --output captions.ass --manifest-output correction_manifest.json --uppercase
```

Recommended prompt:

```text
Use Legends Captions to inspect this transcript, apply contextual correction
policy, build active-word ASS captions and correction manifests with
legends-captions render-ass, and review any flagged terms before final render.
```

Start with the `doctor` command, inspect active rules with `policy-report`, normalize or generate `.ass` subtitles and manifests with `normalize` and `render-ass`, and review any flagged ASR errors before final render.

## Full Runtime Notes

The current preferred text-quality runtime is WSL Parakeet:

```text
/home/you/.venvs/speech/bin/python
```

Set `LEGENDS_CAPTIONS_WSL_PYTHON` (see `.env.example`) to point at your own
speech environment.

The preferred final timing authority is NeMo Forced Aligner CTM output when exact
word timing matters.
