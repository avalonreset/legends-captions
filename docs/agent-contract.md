# Cross-Agent Contract

Codex, Claude, and Gemini can all participate in caption production, but they must share the same source of truth.

## Shared Truth

- Project brain: `wiki/`
- Hot cache: `wiki/hot.md`
- Policy: `wiki/policies/`
- Config: `configs/`
- Raw lineage: `.raw/`

## Agent Boundaries

- Codex owns implementation, shell execution, render packaging, and verified artifacts.
- Claude can review language, grouping, and policy clarity.
- Gemini can review visual frames, screenshot text, and ambiguity.

## No Drift Rule

An agent can suggest a better caption rule, but it must become a shared policy/config/test update before it becomes the default.

