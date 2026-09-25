"""Command line entrypoint for Legends Ultimate Captions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

from . import __version__
from .manifest import build_policy_manifest
from .policy import PHRASE_RULES, apply_caption_policy, normalize_text


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def default_config_path() -> Path:
    packaged = Path(__file__).resolve().parent / "data" / "default_vertical_4k60.json"
    if packaged.is_file():
        return packaged
    return PROJECT_ROOT / "configs" / "default_vertical_4k60.json"


DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "default_vertical_4k60.json"


def load_config(path: Path | None = None) -> dict[str, object]:
    if path is not None:
        return json.loads(path.read_text(encoding="utf-8"))
    for candidate in (default_config_path(), DEFAULT_CONFIG):
        if candidate.is_file():
            return json.loads(candidate.read_text(encoding="utf-8"))
    raise FileNotFoundError("No default caption config found (looked in package data and configs/).")


def command_doctor(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config) if args.config else None)
    raw_sources = sorted((PROJECT_ROOT / ".raw" / "sources").glob("*"))
    report = {
        "project": "Legends Ultimate Captions",
        "version": __version__,
        "root": str(PROJECT_ROOT),
        "config_profile": config.get("profile"),
        "raw_source_files": len(raw_sources),
        "ffmpeg": shutil.which("ffmpeg"),
        "ffprobe": shutil.which("ffprobe"),
        "python": sys.executable,
    }
    print(json.dumps(report, indent=2))
    return 0


def command_policy_report(_: argparse.Namespace) -> int:
    report = [
        {
            "match": " ".join(rule.match),
            "replacement": " ".join(rule.replacement),
            "category": rule.category,
            "confidence": rule.confidence,
            "reason": rule.reason,
        }
        for rule in PHRASE_RULES
    ]
    print(json.dumps(report, indent=2))
    return 0


def command_normalize(args: argparse.Namespace) -> int:
    text = " ".join(args.text)
    result = apply_caption_policy(text.split())
    if args.manifest:
        print(json.dumps(build_policy_manifest(result, source="cli"), indent=2))
    else:
        print(normalize_text(text, uppercase=args.uppercase))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="legends-captions")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Report local project readiness.")
    doctor.add_argument("--config", help="Optional config JSON path.")
    doctor.set_defaults(func=command_doctor)

    policy = subparsers.add_parser("policy-report", help="Print contextual correction policy rules.")
    policy.set_defaults(func=command_policy_report)

    normalize = subparsers.add_parser("normalize", help="Normalize a text snippet through caption policy.")
    normalize.add_argument("text", nargs="+")
    normalize.add_argument("--uppercase", action="store_true", help="Print caption display text in uppercase.")
    normalize.add_argument("--manifest", action="store_true", help="Print a correction manifest instead of text.")
    normalize.set_defaults(func=command_normalize)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

