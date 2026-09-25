# Agent Install Guide

Legends Captions is designed to be installed as a repo plus an agent
surface. The Python package provides the commands. The agent files teach Codex,
Claude, or Gemini how to operate the workflow.

## Codex

Codex reads repository-level `AGENTS.md` files as project instructions. Open
Codex from the repo root and ask it to read the project instructions.

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

## Claude Code

Use the packaged Claude skill:

```text
.claude/skills/legends-captions/SKILL.md
```

Recommended prompt:

```text
Use the legends-captions skill. Start with the doctor command, then
build a caption QA plan before rendering.
```

## Gemini CLI

Use `gemini-extension.json` and `GEMINI.md` from the repo root.

Recommended prompt:

```text
Use the Legends Captions extension to review caption text, identify
likely ASR errors, and flag proof-frame checks before final render.
```

## Full Runtime Notes

The current preferred text-quality runtime is WSL Parakeet:

```text
/home/you/.venvs/speech/bin/python
```

Set `LEGENDS_CAPTIONS_WSL_PYTHON` (see `.env.example`) to point at your own
speech environment.

The preferred final timing authority is NeMo Forced Aligner CTM output when exact
word timing matters.
