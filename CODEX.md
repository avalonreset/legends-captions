# Codex Vault Guide

This workspace uses a Codex Obsidian-style brain under `wiki/`.

## Start Here

- [[hot]]
- [[index]]
- [[overview]]
- [[Caption Intelligence Policy]]
- [[Revision Learning Policy]]
- [[One Revision Caption Deployment]]

## Wiki Map

- `wiki/sources/` contains distilled source notes.
- `wiki/policies/` contains durable caption behavior rules.
- `wiki/playbooks/` contains operational procedures.
- `wiki/agents/` contains agent role cards.
- `wiki/concepts/` contains reusable ideas and definitions.
- `wiki/qa/` contains quality gates and review checklists.
- `.raw/` contains immutable imports from Avalon Reset, Hub Pro, and production runs.

## Link Policy

Use wikilinks for internal notes. Use absolute filesystem paths only when pointing to real local artifacts outside this vault.

## Update Policy

After a production correction:

1. Add the lesson to [[Revision Learning Policy]] or a dated run note.
2. Add a regression example in `tests/` when the correction can be automated.
3. Add a manifest entry when the correction affects a real render.
4. Update [[hot]] if the rule should affect the next run.

