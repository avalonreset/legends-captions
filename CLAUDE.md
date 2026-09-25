# Claude Instructions

Claude should use the same brain and policy as Codex.

Start with:

1. `wiki/hot.md`
2. `wiki/index.md`
3. `wiki/policies/Caption Intelligence Policy.md`
4. `wiki/playbooks/One Revision Caption Deployment.md`

Do not make a Claude-only caption standard. If you discover a better rule, propose it as a policy update, add a regression example, and record the source evidence.

Raw imports under `.raw/` are read-only. Production media should remain outside this repo unless explicitly staged as examples or manifests.

Run `legends-captions doctor` before assuming the local CLI is ready.
