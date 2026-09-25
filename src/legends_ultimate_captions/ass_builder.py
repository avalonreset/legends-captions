"""Small ASS subtitle helpers for active-word caption renderers."""

from __future__ import annotations

from dataclasses import dataclass


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


@dataclass(frozen=True)
class AssEvent:
    start: float
    end: float
    text: str
    style: str = "LegendsActive"


def ass_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    centiseconds = int(round(seconds * 100))
    cs = centiseconds % 100
    total_seconds = centiseconds // 100
    sec = total_seconds % 60
    total_minutes = total_seconds // 60
    minute = total_minutes % 60
    hour = total_minutes // 60
    return f"{hour:d}:{minute:02d}:{sec:02d}.{cs:02d}"


def escape_ass(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}").replace("\n", "\\N")


def build_ass_document(
    events: list[AssEvent],
    width: int = 2160,
    height: int = 3840,
    style: AssStyle | None = None,
) -> str:
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
        lines.append(
            f"Dialogue: 0,{ass_time(event.start)},{ass_time(event.end)},{event.style},,0,0,0,,{escape_ass(event.text)}"
        )
    return "\n".join(lines) + "\n"

