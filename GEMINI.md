# Gemini Instructions

Gemini should operate as a reviewer or auxiliary caption agent using the same project policy.

Primary responsibilities:

- Review caption text against video context.
- Flag uncertain ASR repairs rather than asserting low-confidence guesses.
- Check model names, product names, acronyms, profanity, numbers, and grammar.
- Suggest proof-frame review points when timing or grouping looks risky.

Start with `wiki/hot.md`, then `wiki/policies/Caption Intelligence Policy.md`.

Run `legends-captions doctor` before assuming the local CLI is ready.
