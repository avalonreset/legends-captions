"""Command line entrypoint for Legends Captions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

from . import __version__
from .ass_builder import AssEvent, AssStyle, build_ass_document
from .manifest import build_policy_manifest
from .policy import (
    PHRASE_RULES,
    CaptionToken,
    PolicyResult,
    apply_caption_policy,
    normalize_text,
)


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
        "project": "Legends Captions",
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


def _tokens_from_json_payload(payload: object, default_start: float) -> list[CaptionToken]:
    items: list[object]
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        for key in ("tokens", "words", "events", "segments"):
            candidate = payload.get(key)
            if isinstance(candidate, list):
                items = candidate
                break
        else:
            raise ValueError("Input JSON object must contain a 'tokens', 'words', 'events', or 'segments' list.")
    else:
        raise ValueError("Input JSON must be a list of token/segment objects or a dict containing one.")

    tokens: list[CaptionToken] = []
    cursor = default_start
    for item in items:
        if isinstance(item, str):
            words = item.split()
            for word in words:
                tokens.append(CaptionToken(text=word, start=cursor, end=cursor + 0.35, source_text=word))
                cursor += 0.35
            continue
        if not isinstance(item, dict):
            continue
        raw_text = str(item.get("text") if item.get("text") is not None else item.get("word") or "").strip()
        if not raw_text:
            continue
        words = raw_text.split()
        start_val = float(item["start"]) if item.get("start") is not None else cursor
        end_val = float(item["end"]) if item.get("end") is not None else start_val + max(0.35, 0.35 * len(words))
        if end_val <= start_val:
            end_val = start_val + max(0.35, 0.35 * len(words))
        step = (end_val - start_val) / len(words)
        for idx, word in enumerate(words):
            w_start = start_val + idx * step
            w_end = start_val + (idx + 1) * step
            tokens.append(CaptionToken(text=word, start=w_start, end=w_end, source_text=word))
        cursor = end_val
    return tokens


def _resolve_render_policy(args: argparse.Namespace) -> PolicyResult:
    if args.input:
        input_path = Path(args.input)
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        tokens = _tokens_from_json_payload(payload, default_start=args.start)
    elif args.text:
        words = " ".join(args.text).split()
        duration = args.duration if args.duration is not None else max(1.0, len(words) * 0.35)
        step = duration / max(1, len(words))
        tokens = [
            CaptionToken(
                text=word,
                start=args.start + idx * step,
                end=args.start + (idx + 1) * step,
                source_text=word,
            )
            for idx, word in enumerate(words)
        ]
    else:
        raise ValueError("Provide either positional text or --input <json_path>.")
    return apply_caption_policy(tokens)


def command_render_ass(args: argparse.Namespace) -> int:
    result = _resolve_render_policy(args)
    events: list[AssEvent] = []
    cursor = args.start
    if args.mode == "line":
        if result.tokens:
            first_start = result.tokens[0].start if result.tokens[0].start is not None else cursor
            last_end = result.tokens[-1].end if result.tokens[-1].end is not None else first_start + max(1.0, len(result.tokens) * 0.35)
            events.append(
                AssEvent(
                    start=first_start,
                    end=last_end,
                    text=result.caption_text(uppercase=args.uppercase),
                )
            )
    else:
        for token in result.tokens:
            t_start = token.start if token.start is not None else cursor
            t_end = token.end if token.end is not None and token.end > t_start else t_start + 0.35
            display = token.text.upper() if args.uppercase else token.text
            events.append(AssEvent(start=t_start, end=t_end, text=display))
            cursor = t_end

    style = AssStyle(font=args.font, font_size=args.font_size)
    ass_doc = build_ass_document(events, width=args.width, height=args.height, style=style)

    if args.manifest_output:
        manifest_path = Path(args.manifest_output)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = build_policy_manifest(result, source=str(args.input) if args.input else "cli")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(ass_doc, encoding="utf-8")
        receipt = {
            "status": "ok",
            "ass_path": str(output_path),
            "manifest_path": str(Path(args.manifest_output)) if args.manifest_output else None,
            "events": len(events),
            "decisions": len(result.decisions),
            "caption_text": result.caption_text(uppercase=args.uppercase),
        }
        print(json.dumps(receipt, indent=2))
    else:
        print(ass_doc, end="")
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

    render_ass = subparsers.add_parser(
        "render-ass",
        help="Apply caption policy and build a deterministic active-word or line ASS subtitle document.",
    )
    render_ass.add_argument("text", nargs="*", help="Optional inline text when --input is not supplied.")
    render_ass.add_argument("--input", help="Path to JSON file containing timed words, tokens, or segments.")
    render_ass.add_argument("--output", help="Optional output path for the generated .ass file.")
    render_ass.add_argument("--manifest-output", help="Optional output path for the policy correction manifest JSON.")
    render_ass.add_argument("--mode", choices=("word", "line"), default="word", help="Emit one ASS Dialogue event per word or per line.")
    render_ass.add_argument("--start", type=float, default=0.0, help="Starting timestamp in seconds for untimed text.")
    render_ass.add_argument("--duration", type=float, default=None, help="Total duration in seconds for untimed text.")
    render_ass.add_argument("--width", type=int, default=2160, help="ASS PlayResX canvas width.")
    render_ass.add_argument("--height", type=int, default=3840, help="ASS PlayResY canvas height.")
    render_ass.add_argument("--font", default="Montserrat Black", help="ASS style font family.")
    render_ass.add_argument("--font-size", type=int, default=156, help="ASS style font size.")
    render_ass.add_argument("--uppercase", action="store_true", help="Render caption display text in uppercase.")
    render_ass.set_defaults(func=command_render_ass)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
