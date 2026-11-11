"""Command line entrypoint for Legends Captions."""

from __future__ import annotations

import argparse
from importlib import resources
import json
import math
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile

from . import __version__
from .ass_builder import (
    MAX_TIMECODE_SECONDS,
    AssEvent,
    AssStyle,
    build_ass_document,
    escape_ffmpeg_ass_filter,
    format_ffmpeg_ass_filtergraph,
    validate_style_identifier,
)
from .manifest import build_policy_manifest
from .policy import (
    PHRASE_RULES,
    CaptionToken,
    PolicyResult,
    apply_caption_policy,
    normalize_text,
)


_CANDIDATE_REPO_ROOT = Path(__file__).resolve().parents[2]
MAX_CONFIG_BYTES = 1 * 1024 * 1024
MAX_INPUT_BYTES = 25 * 1024 * 1024
_MACOS_SYSTEM_SYMLINKS = {Path("/var"), Path("/tmp"), Path("/etc")}


def resolve_project_root() -> Path:
    """Return the source checkout root if running from a repo checkout, else the active working directory."""
    if (_CANDIDATE_REPO_ROOT / ".legends-module").is_file():
        return _CANDIDATE_REPO_ROOT
    return Path.cwd().resolve()


PROJECT_ROOT = resolve_project_root()


def _reject_nonfinite(token: str) -> None:
    raise ValueError(f"Non-finite JSON number {token!r} is not allowed.")


def _check_parent_symlinks(path: Path) -> None:
    abs_path = Path(os.path.abspath(str(path)))
    for parent in abs_path.parents:
        if parent.is_symlink():
            if sys.platform == "darwin" and parent in _MACOS_SYSTEM_SYMLINKS:
                continue
            raise ValueError(f"Refusing path traversing symlinked directory: {parent}")


def _read_safe_json_file(path: Path, *, max_bytes: int, label: str) -> object:
    if path.is_symlink():
        raise ValueError(f"Refusing symlink for {label}: {path}")
    _check_parent_symlinks(path)
    try:
        st = path.lstat()
    except FileNotFoundError:
        raise
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
        raise ValueError(f"Refusing non-regular file for {label}: {path}")
    if st.st_size > max_bytes:
        raise ValueError(f"{label} exceeds maximum size of {max_bytes} bytes: {path}")
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw, parse_constant=_reject_nonfinite)


def _write_safe_file(path: Path, content: str, *, overwrite: bool, label: str) -> None:
    if path.is_symlink():
        raise ValueError(f"Refusing symlink output path for {label}: {path}")
    _check_parent_symlinks(path)
    if path.exists():
        st = path.lstat()
        if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
            raise ValueError(f"Refusing non-regular output target for {label}: {path}")
        if not overwrite:
            raise FileExistsError(f"Refusing to overwrite existing {label} without --overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    _check_parent_symlinks(path)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        if path.is_symlink():
            raise ValueError(f"Refusing symlink output path for {label}: {path}")
        os.replace(tmp_path, path)
    except Exception:
        with suppress_os_error():
            tmp_path.unlink(missing_ok=True)
        raise


class suppress_os_error:
    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return exc_type is not None and issubclass(exc_type, OSError)


def default_config_path() -> Path:
    packaged = Path(__file__).resolve().parent / "data" / "default_vertical_4k60.json"
    if packaged.is_file():
        return packaged
    repo_cfg = resolve_project_root() / "configs" / "default_vertical_4k60.json"
    return repo_cfg


DEFAULT_CONFIG = default_config_path()


def load_config(path: Path | None = None) -> dict[str, object]:
    if path is not None:
        payload = _read_safe_json_file(Path(path), max_bytes=MAX_CONFIG_BYTES, label="config file")
        if not isinstance(payload, dict):
            raise ValueError("Config file must contain a JSON object.")
        return payload

    try:
        resource = resources.files("legends_captions").joinpath("data", "default_vertical_4k60.json")
        raw = resource.read_text(encoding="utf-8")
        payload = json.loads(raw, parse_constant=_reject_nonfinite)
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass

    for candidate in (default_config_path(), _CANDIDATE_REPO_ROOT / "configs" / "default_vertical_4k60.json"):
        if candidate.is_file() and not candidate.is_symlink():
            payload = _read_safe_json_file(candidate, max_bytes=MAX_CONFIG_BYTES, label="default config file")
            if isinstance(payload, dict):
                return payload
    raise FileNotFoundError("No default caption config found (looked in package data and configs/).")


def command_doctor(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config) if args.config else None)
    root = resolve_project_root()
    raw_dir = root / ".raw" / "sources"
    raw_sources = sorted(raw_dir.glob("*")) if raw_dir.is_dir() and not raw_dir.is_symlink() else []
    report = {
        "project": "Legends Captions",
        "version": __version__,
        "root": str(root),
        "source_checkout": (root / ".legends-module").is_file(),
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


def command_ffmpeg_filter(args: argparse.Namespace) -> int:
    filter_complex = format_ffmpeg_ass_filtergraph(args.ass)
    if args.json:
        payload = {
            "ass_path": str(args.ass),
            "escaped_filename": escape_ffmpeg_ass_filter(args.ass),
            "filter_complex": filter_complex,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(filter_complex)
    return 0


def _validate_timestamp(value: object, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"Invalid {field_name} {value!r}: expected finite number.")
    parsed = float(value)
    if not math.isfinite(parsed) or parsed < 0.0 or parsed > MAX_TIMECODE_SECONDS:
        raise ValueError(f"Invalid {field_name} {value!r}: expected 0.0 <= {field_name} <= {MAX_TIMECODE_SECONDS}.")
    return parsed


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
    cursor = _validate_timestamp(default_start, "start")
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
        start_val = _validate_timestamp(item["start"], "start") if item.get("start") is not None else cursor
        end_val = (
            _validate_timestamp(item["end"], "end")
            if item.get("end") is not None
            else start_val + max(0.35, 0.35 * len(words))
        )
        if end_val < start_val:
            raise ValueError(f"Invalid token timing: end ({end_val}) precedes start ({start_val}).")
        if end_val == start_val:
            end_val = min(MAX_TIMECODE_SECONDS, start_val + max(0.35, 0.35 * len(words)))
        step = (end_val - start_val) / len(words)
        for idx, word in enumerate(words):
            w_start = start_val + idx * step
            w_end = start_val + (idx + 1) * step
            tokens.append(CaptionToken(text=word, start=w_start, end=w_end, source_text=word))
        cursor = end_val
    return tokens


def _resolve_render_policy(args: argparse.Namespace) -> PolicyResult:
    start = _validate_timestamp(args.start, "--start")
    if args.duration is not None:
        if not math.isfinite(float(args.duration)) or float(args.duration) <= 0.0 or float(args.duration) > MAX_TIMECODE_SECONDS:
            raise ValueError(f"Invalid --duration {args.duration!r}: expected positive finite number <= {MAX_TIMECODE_SECONDS}.")
    if args.input:
        input_path = Path(args.input)
        payload = _read_safe_json_file(input_path, max_bytes=MAX_INPUT_BYTES, label="input JSON file")
        tokens = _tokens_from_json_payload(payload, default_start=start)
    elif args.text:
        words = " ".join(args.text).split()
        duration = float(args.duration) if args.duration is not None else max(1.0, len(words) * 0.35)
        if start + duration > MAX_TIMECODE_SECONDS:
            raise ValueError(f"Start + duration exceeds maximum {MAX_TIMECODE_SECONDS} seconds.")
        step = duration / max(1, len(words))
        tokens = [
            CaptionToken(
                text=word,
                start=start + idx * step,
                end=start + (idx + 1) * step,
                source_text=word,
            )
            for idx, word in enumerate(words)
        ]
    else:
        raise ValueError("Provide either positional text or --input <json_path>.")
    return apply_caption_policy(tokens)


def command_render_ass(args: argparse.Namespace) -> int:
    validate_style_identifier(args.font, "--font")
    if not (16 <= args.width <= 16384):
        raise ValueError(f"Invalid --width {args.width!r}: expected integer in 16..16384.")
    if not (16 <= args.height <= 16384):
        raise ValueError(f"Invalid --height {args.height!r}: expected integer in 16..16384.")
    if not (1 <= args.font_size <= 1000):
        raise ValueError(f"Invalid --font-size {args.font_size!r}: expected integer in 1..1000.")

    result = _resolve_render_policy(args)
    events: list[AssEvent] = []
    cursor = _validate_timestamp(args.start, "--start")
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

    overwrite = bool(getattr(args, "overwrite", False))
    if args.output:
        output_path = Path(args.output)
        if output_path.is_symlink():
            raise ValueError(f"Refusing symlink output path for --output: {output_path}")
        _check_parent_symlinks(output_path)
        if output_path.exists() and not overwrite:
            raise FileExistsError(f"Refusing to overwrite existing --output file without --overwrite: {output_path}")
    if args.manifest_output:
        manifest_path = Path(args.manifest_output)
        if manifest_path.is_symlink():
            raise ValueError(f"Refusing symlink output path for --manifest-output: {manifest_path}")
        _check_parent_symlinks(manifest_path)
        if manifest_path.exists() and not overwrite:
            raise FileExistsError(
                f"Refusing to overwrite existing --manifest-output file without --overwrite: {manifest_path}"
            )

    if args.manifest_output:
        manifest_path = Path(args.manifest_output)
        manifest = build_policy_manifest(result, source=str(args.input) if args.input else "cli")
        _write_safe_file(
            manifest_path,
            json.dumps(manifest, indent=2) + "\n",
            overwrite=overwrite,
            label="--manifest-output file",
        )

    if args.output:
        output_path = Path(args.output)
        _write_safe_file(output_path, ass_doc, overwrite=overwrite, label="--output file")
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
    render_ass.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting existing --output or --manifest-output files.",
    )
    render_ass.add_argument("--mode", choices=("word", "line"), default="word", help="Emit one ASS Dialogue event per word or per line.")
    render_ass.add_argument("--start", type=float, default=0.0, help="Starting timestamp in seconds for untimed text.")
    render_ass.add_argument("--duration", type=float, default=None, help="Total duration in seconds for untimed text.")
    render_ass.add_argument("--width", type=int, default=2160, help="ASS PlayResX canvas width.")
    render_ass.add_argument("--height", type=int, default=3840, help="ASS PlayResY canvas height.")
    render_ass.add_argument("--font", default="Montserrat Black", help="ASS style font family.")
    render_ass.add_argument("--font-size", type=int, default=156, help="ASS style font size.")
    render_ass.add_argument("--uppercase", action="store_true", help="Render caption display text in uppercase.")
    render_ass.set_defaults(func=command_render_ass)

    ffmpeg_filter = subparsers.add_parser(
        "ffmpeg-filter",
        help="Format a cross-platform escaped FFmpeg libavfilter ass=filename=... filtergraph string.",
    )
    ffmpeg_filter.add_argument("--ass", required=True, help="Path to the .ass subtitle file.")
    ffmpeg_filter.add_argument("--json", action="store_true", help="Emit JSON output instead of plain filter string.")
    ffmpeg_filter.set_defaults(func=command_ffmpeg_filter)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
