# Release Checklist

## Before Publishing

- Run unit tests.
- Run `legends-captions doctor`.
- Verify `README.md`, `LICENSE`, `CHANGELOG.md`, `AGENTS.md`, `CLAUDE.md`,
  `GEMINI.md`, and `skills/legends-ultimate-captions/SKILL.md` tell the same story.
- Confirm the release is framed as an agentic video caption system, not just a
  text normalization script.
- Confirm `.gitignore` excludes generated render folders, proof-frame folders,
  caches, and private outputs.
- Confirm no private videos, private transcripts, signed URLs, cookies, tokens,
  or Skool receipts are tracked.
- Confirm no model weights or large generated media files are tracked unless
  intentionally staged as release artwork.
- Run the correction examples from the README.
- Verify the banner and social preview paths exist.
- Verify Skool release post and promo copy are staged under `release/`.

## Private Release Assets

Include:

- source code;
- documentation;
- agent wrappers;
- example configs;
- small launch artwork;
- example manifests without private paths.

Do not include:

- raw private media;
- generated captioned videos unless explicitly approved;
- full production transcripts from private sources;
- model weights;
- browser profiles;
- credential files;
- local absolute production paths inside public examples.

