"""Small ASS subtitle and FFmpeg libavfilter helpers for active-word caption renderers."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import re


_SAFE_STYLE_TOKEN_RE = re.compile(r"^[^\r\n,{}]{1,128}$")
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
MAX_TIMECODE_SECONDS = 86400.0


def validate_style_identifier(value: str, field_name: str = "style") -> str:
    if not isinstance(value, str) or not _SAFE_STYLE_TOKEN_RE.match(value) or _CONTROL_CHAR_RE.search(value):
        raise ValueError(
            f"Invalid {field_name} {value!r}: must be 1..128 printable characters without commas, braces, or newlines."
        )
    return value


@dataclass(frozen=True)
class AssStyle:
    name: str = "LegendsActive"
    font: str = "Montserrat Black"
    font_size: int = 156
    primary_color: str = "&H00FFFFFF"
    outline_color: str = "&H00000000"
    alignment: int = 5
    margin_l: int = 0
    margin_r: int = 0
    margin_v: int = 0

    def __post_init__(self) -> None:
        validate_style_identifier(self.name, "style.name")
        validate_style_identifier(self.font, "style.font")
        if not isinstance(self.font_size, int) or isinstance(self.font_size, bool) or not (1 <= self.font_size <= 1000):
            raise ValueError(f"Invalid style.font_size {self.font_size!r}: expected integer in 1..1000.")


@dataclass(frozen=True)
class AssEvent:
    start: float
    end: float
    text: str
    style: str = "LegendsActive"

    def __post_init__(self) -> None:
        validate_style_identifier(self.style, "event.style")
        if not (isinstance(self.start, (int, float)) and not isinstance(self.start, bool) and math.isfinite(float(self.start))):
            raise ValueError(f"Invalid event.start {self.start!r}: must be a finite number.")
        if not (isinstance(self.end, (int, float)) and not isinstance(self.end, bool) and math.isfinite(float(self.end))):
            raise ValueError(f"Invalid event.end {self.end!r}: must be a finite number.")
        if float(self.start) < 0.0 or float(self.end) < float(self.start) or float(self.end) > MAX_TIMECODE_SECONDS:
            raise ValueError(
                f"Invalid event time range ({self.start}, {self.end}): expected 0.0 <= start <= end <= {MAX_TIMECODE_SECONDS}."
            )


def ass_time(seconds: float) -> str:
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(float(seconds)):
        raise ValueError(f"Invalid timestamp {seconds!r}: must be a finite number.")
    clamped = float(seconds)
    if clamped < 0.0:
        clamped = 0.0
    if clamped > MAX_TIMECODE_SECONDS:
        raise ValueError(f"Timestamp {seconds!r} exceeds maximum {MAX_TIMECODE_SECONDS} seconds.")
    centiseconds = int(round(clamped * 100))
    cs = centiseconds % 100
    total_seconds = centiseconds // 100
    sec = total_seconds % 60
    total_minutes = total_seconds // 60
    minute = total_minutes % 60
    hour = total_minutes // 60
    return f"{hour:d}:{minute:02d}:{sec:02d}.{cs:02d}"


def escape_ass(text: str) -> str:
    normalized = str(text).replace("\r\n", "\n").replace("\r", "\n")
    normalized = _CONTROL_CHAR_RE.sub("", normalized)
    return (
        normalized.replace("\\", "\\\\")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace("\n", "\\N")
    )


def escape_ffmpeg_ass_filter(ass_path: str | Path) -> str:
    """Escape a subtitle file path for safe embedding inside FFmpeg libavfilter ass=filename='...'."""
    raw = str(ass_path)
    if not raw or not raw.strip():
        raise ValueError("ASS path must not be empty.")
    if "\r" in raw or "\n" in raw or "\x00" in raw or _CONTROL_CHAR_RE.search(raw):
        raise ValueError("ASS path must not contain control characters or newlines.")
    if raw.lstrip().startswith("-"):
        raise ValueError("ASS path must not start with '-'.")
    escaped = raw.replace("\\", "\\\\")
    escaped = escaped.replace(":", "\\:")
    escaped = escaped.replace("[", "\\[")
    escaped = escaped.replace("]", "\\]")
    escaped = escaped.replace(",", "\\,")
    escaped = escaped.replace(";", "\\;")
    escaped = escaped.replace("'", "'" + "\\" * 3 + "''")
    return escaped


def format_ffmpeg_ass_filtergraph(ass_path: str | Path) -> str:
    """Build a deterministic FFmpeg -filter_complex string with Windows colon and filtergraph escaping."""
    escaped = escape_ffmpeg_ass_filter(ass_path)
    return f"[0:v]setpts=PTS-STARTPTS,ass=filename='{escaped}'[v]"


def build_ass_document(
    events: list[AssEvent],
    width: int = 2160,
    height: int = 3840,
    style: AssStyle | None = None,
) -> str:
    if not isinstance(width, int) or isinstance(width, bool) or not (16 <= width <= 16384):
        raise ValueError(f"Invalid width {width!r}: expected integer in 16..16384.")
    if not isinstance(height, int) or isinstance(height, bool) or not (16 <= height <= 16384):
        raise ValueError(f"Invalid height {height!r}: expected integer in 16..16384.")
    style = style or AssStyle()
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        (
            f"Style: {style.name},{style.font},{style.font_size},{style.primary_color},&H0000FFFF,"
            f"{style.outline_color},&H7F000000,-1,0,0,0,100,100,0,0,1,6,2,"
            f"{style.alignment},{style.margin_l},{style.margin_r},{style.margin_v},1"
        ),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for event in events:
        validate_style_identifier(event.style, "event.style")
        lines.append(
            f"Dialogue: 0,{ass_time(event.start)},{ass_time(event.end)},{event.style},,0,0,0,,{escape_ass(event.text)}"
        )
    return "\n".join(lines) + "\n"
