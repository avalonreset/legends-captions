# Contributing

## Development setup

Requires Python 3.10+ and Git. No third-party packages are needed for the
core library and tests.

```sh
git clone https://github.com/avalonreset/legends-captions.git
cd legends-captions
python -m venv .venv
.venv/bin/python -m pip install -e .
```

On Windows PowerShell, run `scripts\run-tests.ps1` instead of the commands
below.

## Rules

1. Keep raw media and raw imported evidence out of commits unless the asset is
   explicitly meant to ship.
2. Add or update a regression test for every reusable caption correction.
3. Run `python -m unittest discover -s tests` before opening a PR.
4. Update the relevant wiki policy if behavior changes.
5. Do not commit model weights, private video, transcripts with private member
   data, generated render caches, credentials, or local receipts.

## Pull requests

Keep PRs small and reviewable: one behavior change, its tests, and its docs.
