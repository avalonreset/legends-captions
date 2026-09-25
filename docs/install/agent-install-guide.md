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

Recommended prompt:

```text
Use Legends Captions to inspect this video, build accurate active-word
captions, apply contextual correction policy, render proof frames, and give me
the final caption package with manifests.
```

Start with the doctor command, then build a caption QA plan before rendering.
Review caption text, identify likely ASR errors, and flag proof-frame checks
before final render.

## Full Runtime Notes

The current preferred text-quality runtime is WSL Parakeet:

```text
/home/you/.venvs/speech/bin/python
```

Set `LEGENDS_CAPTIONS_WSL_PYTHON` (see `.env.example`) to point at your own
speech environment.

The preferred final timing authority is NeMo Forced Aligner CTM output when exact
word timing matters.
