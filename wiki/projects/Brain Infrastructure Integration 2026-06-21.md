---
type: project
status: active
created: 2026-06-21
updated: 2026-06-21
tags:
  - brain
  - infrastructure
  - captions
  - video-production
---

# Brain Infrastructure Integration 2026-06-21

## Mandate

Legends Ultimate Captions is a core component of the Avalon Reset / Hub Pro video production pipeline. It should be fully cloned or ingested into the brain infrastructure, not represented only by a summary note.

This project is the implementation home for caption intelligence. Brain mirrors may index it, but this checkout remains the source of truth for code, configs, tests, policies, playbooks, and QA rules.

## Integration Scope

The brain ingestion should include:

- `wiki/` policy, playbook, agent, concept, source, QA, roadmap, hot, index, and log pages;
- `src/` implementation files;
- `tests/` regression tests;
- `configs/` glossary, correction, and style configs;
- `scripts/` operational helpers;
- `skills/` agent-facing skill instructions;
- `examples/`, `docs/`, `assets/`, and `release/` artifacts that explain expected behavior;
- `.raw/` source-lineage material when needed for provenance.

## Required Brain Behavior

- A future video-production agent should know that Ultimate Captions is the default caption system for polished Shorts and YouTube deliverables.
- A future caption agent should read the local policies before rendering, especially [[Autonomous Shorts Caption Policy]], [[Caption Intelligence Policy]], [[Timing Authority Policy]], [[Render QA Policy]], and [[qa/Caption QA Checklist|Caption QA Checklist]].
- User revision feedback should be converted into durable policy/config/test changes when it is reusable.
- Avalon Reset YouTube should keep production-specific routing notes, while this project keeps reusable caption implementation truth.

## Verification Target

A successful brain integration can answer, from the brain layer:

- where the Ultimate Captions implementation checkout lives;
- which policy controls bottom caption scene resets at hard cuts;
- which policy controls upper static-yellow topic markers;
- which tests/configs encode accepted caption fixes;
- how a future autonomous Short should route into the caption package runner.
