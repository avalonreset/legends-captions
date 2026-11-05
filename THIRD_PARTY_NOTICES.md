# Third-Party Notices

`legends-captions` uses only the Python 3.11+ standard library at runtime and bundles no third-party runtime packages.

## Optional external tools

When used in full media workflows, `legends-captions` interoperates with external tools installed separately by the operator:

- **FFmpeg / FFprobe** (`https://ffmpeg.org`, LGPL v2.1+ or GPL v2+ depending on build) for container probing and optional subtitle burn-in.
- **faster-whisper** (`https://github.com/SYSTRAN/faster-whisper`, MIT License) and **NVIDIA NeMo / Parakeet** (`https://github.com/NVIDIA/NeMo`, Apache-2.0 / CC-BY-4.0) for upstream speech-to-text and forced alignment.
- **Montserrat** (`https://github.com/JulietaUla/Montserrat`, SIL Open Font License 1.1), referenced by family name in default `.ass` style templates; no font binaries are redistributed in this repository.

## CTO Legends router skill

The central routing skill at `skills/cto-legends/SKILL.md` is vendored unchanged from [`avalonreset/cto-legends`](https://github.com/avalonreset/cto-legends) under the MIT License. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
