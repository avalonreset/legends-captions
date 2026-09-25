# Agent Compatibility

The goal is one core workflow with thin adapters for each agent runtime.

## Codex

Codex uses `AGENTS.md` project instructions. OpenAI's Codex documentation says
repository-level files keep Codex aware of project norms while inheriting global
defaults, and that a repository root `AGENTS.md` is the right place for basic
project setup and expectations.

Reference:

- https://developers.openai.com/codex/guides/agents-md#layer-project-instructions

## Claude

Claude Code supports skills as directories with a `SKILL.md` entrypoint. This
repo includes:

```text
.claude/skills/legends-ultimate-captions/SKILL.md
```

## Gemini CLI

Gemini CLI can load project context through `GEMINI.md` and extension metadata.
This repo includes:

```text
gemini-extension.json
GEMINI.md
```

## Portable Agent Skill

The portable Agent Skills entrypoint is:

```text
skills/legends-ultimate-captions/SKILL.md
```

All surfaces route to the same policy pages, config files, tests, and CLI.

