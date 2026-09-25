import argparse
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PLAY_W = 2160
PLAY_H = 3840
CAPTION_X = 1080
CAPTION_Y = 2760
FONT_NAME = "Montserrat Black"
FONT_PATH = Path(r"C:\Windows\Fonts\Montserrat-Black.ttf")
FONT_SIZE = 156
MEASURE_FONT_SIZE = 112
MAX_LINE_CHARS = 21
MAX_LINE_WIDTH = 1720
MAX_TOKENS = 7
GROUP_BREAK_GAP_SECONDS = 0.50
HOLD_GAP_SECONDS = 0.85
HIGHLIGHT_LEAD_SECONDS = 0.10
REPEAT_COLLAPSE_GAP_SECONDS = 0.72
FILLER_WORDS = {"uh", "uhh", "um", "umm", "er", "ah"}
LINE_GAP = 0
BUBBLE_PADDING = 24
BUBBLE_RADIUS = 32
BUBBLE_JOIN_MODE = "per_line_rounded_all_corners"
BUBBLE_ALPHA_HEX = "56"
TEXT_RENDER_OVERSCAN = 128
TEXT_VERTICAL_ADJUST = -8
ACTIVE_COLOR = r"&H00F5F500&"
WHITE_COLOR = r"&H00FFFFFF&"


WORD_REPLACEMENTS = {
    "ai": "AI",
    "dm": "DM",
    "dms": "DMs",
    "iphone": "IPHONE",
    "youtube": "YOUTUBE",
    "tiktok": "TIKTOK",
    "codex": "CODEX",
    "github": "GITHUB",
    "hugging": "HUGGING",
    "face": "FACE",
    "stable": "STABLE",
    "audio": "AUDIO",
    "medium": "MEDIUM",
    "adapter": "ADAPTER",
    "lora": "LORA",
    "lowra": "LORA",
    "soulx": "SOULX",
    "soul": "SOUL",
    "flashhead": "FLASHHEAD",
    "flashtalk": "FLASHTALK",
    "heygen": "HEYGEN",
    "rtx": "RTX",
    "rtx4090": "RTX 4090",
    "4090": "4090",
    "vram": "VRAM",
    "gpu": "GPU",
    "gb": "GB",
    "24gb": "24 GB",
    "comfyui": "COMFYUI",
    "seedance": "SEEDANCE",
}

FONT_CACHE = None
TEXT_SIZE_CACHE = {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build vertical active-word ASS captions with contextual ASR cleanup."
    )
    parser.add_argument("--words-json", type=Path, help="Parakeet words JSON fallback/input.")
    parser.add_argument("--ctm", type=Path, help="NFA word CTM input. Preferred when available.")
    parser.add_argument("--out-ass", type=Path, required=True)
    parser.add_argument("--out-manifest", type=Path, required=True)
    parser.add_argument("--source-video", type=Path, required=True)
    parser.add_argument("--transcript-json", type=Path)
    return parser.parse_args()


def ass_time(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    centis = int(round(seconds * 100))
    h = centis // 360000
    centis %= 360000
    m = centis // 6000
    centis %= 6000
    s = centis // 100
    c = centis % 100
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"


def normalize(raw: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(raw).lower())


def terminal_punctuation(raw: str) -> str:
    match = re.search(r"([.?!,]+)$", str(raw).strip())
    return match.group(1) if match else ""


def strip_terminal_punctuation(text: str) -> str:
    return re.sub(r"[.?!,]+$", "", str(text).strip())


def caption_font() -> ImageFont.FreeTypeFont:
    global FONT_CACHE
    if FONT_CACHE is None:
        if not FONT_PATH.exists():
            raise FileNotFoundError(f"Caption font not found: {FONT_PATH}")
        FONT_CACHE = ImageFont.truetype(str(FONT_PATH), MEASURE_FONT_SIZE)
    return FONT_CACHE


def parse_ctm(path: Path) -> list[dict]:
    words = []
    for line_index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        try:
            start = float(parts[2])
            duration = float(parts[3])
        except ValueError:
            continue
        words.append(
            {
                "source_index": line_index,
                "start": start,
                "end": start + duration,
                "word": parts[4].replace("<space>", " "),
                "timing_source": "nfa_ctm",
            }
        )
    return words


def parse_words_json(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    words = []
    for idx, item in enumerate(payload):
        raw = item.get("text", item.get("word", ""))
        words.append(
            {
                "source_index": item.get("word_index", idx),
                "start": float(item["start"]),
                "end": float(item["end"]),
                "word": raw,
                "timing_source": "parakeet_words_json",
            }
        )
    return words


def carry_terminal_punctuation(target: str, source: str) -> str:
    punctuation = terminal_punctuation(source)
    if not punctuation:
        return target
    base = strip_terminal_punctuation(target)
    return f"{base}{punctuation}"


def display_word(raw: str) -> str:
    original = str(raw).strip()
    if not original:
        return ""
    punctuation = terminal_punctuation(original)
    cleaned = re.sub(r"[^A-Za-z0-9'.%+-]+", "", original).strip()
    if not cleaned:
        return ""
    key = normalize(cleaned)
    if key in WORD_REPLACEMENTS:
        text = WORD_REPLACEMENTS[key]
    elif re.fullmatch(r"\d+gb", key):
        text = f"{key[:-2]} GB"
    else:
        text = cleaned.upper()
    if punctuation and not text.endswith(punctuation):
        text = f"{strip_terminal_punctuation(text)}{punctuation}"
    return text


def make_caption_item(words: list[dict], start_index: int, end_index: int, display: str, reason: str) -> tuple[dict, dict]:
    first = words[start_index]
    last = words[end_index]
    raw = " ".join(str(words[idx]["word"]).strip() for idx in range(start_index, end_index + 1))
    display = carry_terminal_punctuation(display, last["word"])
    item = {
        "source_index": first.get("source_index", start_index),
        "start": first["start"],
        "end": last["end"],
        "word": raw,
        "text": display,
        "timing_source": first.get("timing_source", "unknown"),
    }
    change = {
        "start": round(first["start"], 3),
        "end": round(last["end"], 3),
        "from": raw,
        "to": display,
        "reason": reason,
    }
    return item, change


def make_virtual_caption_items(
    words: list[dict], start_index: int, end_index: int, displays: list[str], reason: str
) -> tuple[list[dict], dict]:
    first = words[start_index]
    last = words[end_index]
    raw = " ".join(str(words[idx]["word"]).strip() for idx in range(start_index, end_index + 1))
    start = first["start"]
    end = last["end"]
    total = max(0.08, end - start)
    weights = [max(1, len(strip_terminal_punctuation(display))) for display in displays]
    weight_total = sum(weights)
    items = []
    cursor = start
    for display_index, display in enumerate(displays):
        if display_index == len(displays) - 1:
            item_end = end
        else:
            item_end = cursor + total * weights[display_index] / weight_total
        source_word = first["word"] if display_index == 0 else last["word"]
        items.append(
            {
                "source_index": f"{first.get('source_index', start_index)}.{display_index}",
                "start": cursor,
                "end": max(cursor + 0.04, item_end),
                "word": raw if display_index == 0 else source_word,
                "text": display,
                "timing_source": first.get("timing_source", "unknown"),
                "virtual_split": True,
            }
        )
        cursor = item_end
    change = {
        "start": round(start, 3),
        "end": round(end, 3),
        "from": raw,
        "to": " ".join(displays),
        "reason": reason,
    }
    return items, change


def collapse_immediate_repeats(words: list[dict]) -> tuple[list[dict], list[dict]]:
    collapsed = []
    changes = []
    for word in words:
        key = normalize(word["word"])
        previous = collapsed[-1] if collapsed else None
        prev_key = normalize(previous["word"]) if previous else ""
        gap = word["start"] - previous["end"] if previous else 999.0
        if key and key == prev_key and gap <= REPEAT_COLLAPSE_GAP_SECONDS:
            previous["word"] = carry_terminal_punctuation(previous["word"], word["word"])
            previous["end"] = max(previous["end"], word["end"])
            changes.append(
                {
                    "start": round(word["start"], 3),
                    "dropped": word["word"],
                    "kept": previous["word"],
                    "gap": round(gap, 3),
                    "reason": "immediate repeated word collapsed",
                }
            )
            continue
        collapsed.append(dict(word))
    return collapsed, changes


def should_drop_like(words: list[dict], idx: int) -> tuple[bool, str]:
    raw = str(words[idx]["word"]).strip()
    prev_key = normalize(words[idx - 1]["word"]) if idx > 0 else ""
    next_key = normalize(words[idx + 1]["word"]) if idx + 1 < len(words) else ""
    next2_key = normalize(words[idx + 2]["word"]) if idx + 2 < len(words) else ""
    if prev_key in {"looks", "look", "sounds", "sound", "feels", "feel", "seems", "seem", "sort", "kind"}:
        return False, "meaning-bearing comparison"
    if prev_key in {"was", "were", "is", "be", "being", "been"} and raw.endswith(","):
        return True, "quote-padding or be-verb filler like"
    if next_key in {"i", "im", "i'm", "you", "we", "they", "it", "this", "that"} and raw.endswith(","):
        return True, "filler like before subject"
    if next_key == "all" and next2_key == "the":
        return False, "example phrase like all the"
    return False, "kept"


def remove_filler_words(words: list[dict]) -> tuple[list[dict], list[dict]]:
    cleaned = []
    changes = []
    for idx, word in enumerate(words):
        key = normalize(word["word"])
        if key in FILLER_WORDS:
            changes.append(
                {
                    "start": round(word["start"], 3),
                    "dropped": word["word"],
                    "reason": "spoken filler omitted from captions",
                }
            )
            continue
        if key == "like":
            drop, reason = should_drop_like(words, idx)
            if drop:
                changes.append(
                    {
                        "start": round(word["start"], 3),
                        "dropped": word["word"],
                        "reason": reason,
                    }
                )
                continue
        cleaned.append(dict(word))
    return cleaned, changes


def apply_contextual_corrections(words: list[dict]) -> tuple[list[dict], list[dict]]:
    corrected = []
    changes = []
    idx = 0
    norms = [normalize(word["word"]) for word in words]
    while idx < len(words):
        key = norms[idx]
        next_key = norms[idx + 1] if idx + 1 < len(words) else ""
        next2_key = norms[idx + 2] if idx + 2 < len(words) else ""
        next3_key = norms[idx + 3] if idx + 3 < len(words) else ""
        prev_keys = norms[max(0, idx - 4):idx]

        if key == "soul" and next_key == "x":
            item, change = make_caption_item(words, idx, idx + 1, "SOULX", "product name: SoulX")
            corrected.append(item)
            changes.append(change)
            idx += 2
            continue
        if key == "flash" and next_key == "head":
            item, change = make_caption_item(words, idx, idx + 1, "FLASHHEAD", "model name: FlashHead")
            corrected.append(item)
            changes.append(change)
            idx += 2
            continue
        if key == "flash" and next_key == "talk":
            item, change = make_caption_item(words, idx, idx + 1, "FLASHTALK", "model name: FlashTalk")
            corrected.append(item)
            changes.append(change)
            idx += 2
            continue
        if key == "hey" and next_key == "gen":
            item, change = make_caption_item(words, idx, idx + 1, "HEYGEN", "product name: HeyGen")
            corrected.append(item)
            changes.append(change)
            idx += 2
            continue
        if key == "exacting" and next_key == "20" and "as" in prev_keys:
            items, change = make_virtual_caption_items(
                words,
                idx,
                idx + 1,
                ["EXCITING", "AS", "SEEDANCE", carry_terminal_punctuation("2.0", words[idx + 1]["word"])],
                "context correction: exciting as Seedance 2.0",
            )
            corrected.extend(items)
            changes.append(change)
            idx += 2
            continue
        if key == "the" and prev_keys[-1:] == ["sticking"] and next_key == "30":
            item, change = make_caption_item(words, idx, idx, "TO", "context correction: sticking to 30 fps")
            corrected.append(item)
            changes.append(change)
            idx += 1
            continue
        if key == "is" and prev_keys[-1:] == ["what"] and next_key == "this" and next2_key == "unlock":
            item, change = make_caption_item(words, idx, idx, "DOES", "grammar correction: what does this unlock")
            corrected.append(item)
            changes.append(change)
            idx += 1
            continue
        if key == "low" and next_key == "raw":
            item, change = make_caption_item(words, idx, idx + 1, "LORA", "AI term: LoRA")
            corrected.append(item)
            changes.append(change)
            idx += 2
            continue
        if key in {"lowra", "lora"}:
            item, change = make_caption_item(words, idx, idx, "LORA", "AI term: LoRA")
            corrected.append(item)
            if display_word(words[idx]["word"]) != "LORA":
                changes.append(change)
            idx += 1
            continue
        if [key, next_key, next2_key, next3_key] == ["l", "o", "r", "a"]:
            for letter_index in range(4):
                source = dict(words[idx + letter_index])
                text = display_word(source["word"])
                source["text"] = text
                corrected.append(source)
            _, change = make_caption_item(
                words, idx, idx + 3, "L O R A", "spelled acronym preserved for letter-level highlight"
            )
            changes.append(change)
            idx += 4
            continue
        if key == "media" and {"stable", "audio"} <= set(prev_keys) and "3" in prev_keys:
            item, change = make_caption_item(words, idx, idx, "MEDIUM", "model name: Stable Audio 3 Medium")
            corrected.append(item)
            changes.append(change)
            idx += 1
            continue
        if key == "c" and next_key == "dance":
            item, change = make_caption_item(words, idx, idx + 1, "SEEDANCE", "AI video model name: Seedance")
            corrected.append(item)
            changes.append(change)
            idx += 2
            continue
        if key == "labs" and prev_keys[-3:] == ["soul", "ai", "lab"]:
            item, change = make_caption_item(words, idx, idx, "LAB", "brand name: Soul AI Lab")
            corrected.append(item)
            changes.append(change)
            idx += 1
            continue

        item = dict(words[idx])
        item["text"] = display_word(item["word"])
        corrected.append(item)
        idx += 1
    return corrected, changes


def should_force_group_break(current: list[dict], item: dict) -> bool:
    if not current:
        return False
    previous_key = normalize(current[-1]["text"])
    item_key = normalize(item["text"])
    if previous_key == "solution" and item_key == "everyone":
        return True
    if previous_key == "down" and item_key == "in":
        return True
    return False


def visible_text_size(text: str) -> tuple[int, int]:
    cached = TEXT_SIZE_CACHE.get(text)
    if cached is not None:
        return cached
    font = caption_font()
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    ascent, descent = font.getmetrics()
    width = max(1, math.ceil(probe.textlength(text, font=font) + TEXT_RENDER_OVERSCAN * 2))
    height = max(1, ascent + descent + TEXT_RENDER_OVERSCAN * 2)
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.text((TEXT_RENDER_OVERSCAN, TEXT_RENDER_OVERSCAN), text, font=font, fill=(255, 255, 255, 255))
    bbox = image.getchannel("A").getbbox()
    if not bbox:
        TEXT_SIZE_CACHE[text] = (1, 1)
        return TEXT_SIZE_CACHE[text]
    TEXT_SIZE_CACHE[text] = (bbox[2] - bbox[0], bbox[3] - bbox[1])
    return TEXT_SIZE_CACHE[text]


def can_break(group: list[dict]) -> list[list[int]] | None:
    if not group:
        return []
    all_indices = list(range(len(group)))
    all_text = " ".join(group[idx]["text"] for idx in all_indices)
    all_w, _ = visible_text_size(all_text)
    if len(all_text) <= MAX_LINE_CHARS and all_w <= MAX_LINE_WIDTH:
        return [all_indices]

    candidates = []
    for split_at in range(1, len(group)):
        left = list(range(split_at))
        right = list(range(split_at, len(group)))
        left_text = " ".join(group[idx]["text"] for idx in left)
        right_text = " ".join(group[idx]["text"] for idx in right)
        left_w, _ = visible_text_size(left_text)
        right_w, _ = visible_text_size(right_text)
        if len(left_text) > MAX_LINE_CHARS or len(right_text) > MAX_LINE_CHARS:
            continue
        if left_w > MAX_LINE_WIDTH or right_w > MAX_LINE_WIDTH:
            continue
        orphan_penalty = 10000 if len(left) == 1 or len(right) == 1 else 0
        token_balance_penalty = abs(len(left) - len(right)) * 800
        width_balance_penalty = abs(left_w - right_w)
        candidates.append((orphan_penalty + token_balance_penalty + width_balance_penalty, [left, right]))
    if not candidates:
        return None
    return min(candidates, key=lambda item: item[0])[1]


def can_group(group: list[dict]) -> bool:
    if len(group) > MAX_TOKENS:
        return False
    return can_break(group) is not None


def build_groups(words: list[dict]) -> list[list[dict]]:
    groups = []
    current = []
    for item in words:
        if not item.get("text"):
            continue
        previous = current[-1] if current else None
        gap = item["start"] - previous["end"] if previous else 0.0
        prev_sentence = bool(previous and str(previous["word"]).strip().endswith((".", "?", "!")))
        candidate = current + [item]
        should_break = False
        if current and gap >= GROUP_BREAK_GAP_SECONDS:
            should_break = True
        if current and should_force_group_break(current, item):
            should_break = True
        if current and prev_sentence and len(current) >= 3:
            should_break = True
        if current and not can_group(candidate):
            should_break = True
        if should_break:
            groups.append(current)
            current = [item]
        else:
            current = candidate
    if current:
        groups.append(current)
    return groups


def rounded_rect_path(width: int, height: int, radius: int) -> str:
    w = int(round(width))
    h = int(round(height))
    r = int(min(round(radius), w // 2, h // 2))
    k = 0.5522847498
    c = int(round(r * k))
    return " ".join(
        [
            f"m {r} 0",
            f"l {w - r} 0",
            f"b {w - r + c} 0 {w} {r - c} {w} {r}",
            f"l {w} {h - r}",
            f"b {w} {h - r + c} {w - r + c} {h} {w - r} {h}",
            f"l {r} {h}",
            f"b {r - c} {h} 0 {h - r + c} 0 {h - r}",
            f"l 0 {r}",
            f"b 0 {r - c} {r - c} 0 {r} 0",
            "c",
        ]
    )


def group_layout(group: list[dict]) -> list[dict]:
    layout = []
    line_indices = can_break(group) or []
    for indices in line_indices:
        text = " ".join(group[idx]["text"] for idx in indices)
        text_w, text_h = visible_text_size(text)
        bubble_w = text_w + BUBBLE_PADDING * 2
        bubble_h = text_h + BUBBLE_PADDING * 2
        layout.append(
            {
                "indices": indices,
                "text": text,
                "text_w": text_w,
                "text_h": text_h,
                "bubble_w": bubble_w,
                "bubble_h": bubble_h,
            }
        )
    block_h = sum(line["bubble_h"] for line in layout) + LINE_GAP * max(0, len(layout) - 1)
    y = round(CAPTION_Y - block_h / 2)
    for line in layout:
        line["bubble_left"] = round(CAPTION_X - line["bubble_w"] / 2)
        line["bubble_top"] = y
        line["text_center_y"] = round(y + line["bubble_h"] / 2 + TEXT_VERTICAL_ADJUST)
        y += line["bubble_h"] + LINE_GAP
    return layout


def bubble_event_text(line: dict) -> str:
    path = rounded_rect_path(line["bubble_w"], line["bubble_h"], BUBBLE_RADIUS)
    return (
        rf"{{\an7\pos({line['bubble_left']},{line['bubble_top']})"
        rf"\p1\c&H000000&\1a&H{BUBBLE_ALPHA_HEX}&\bord0\shad0}}"
        f"{path}"
        r"{\p0}"
    )


def line_event_text(group: list[dict], line: dict, active_idx: int) -> str:
    pieces = [
        rf"{{\an5\pos({CAPTION_X},{line['text_center_y']})\fn{FONT_NAME}\fs{FONT_SIZE}"
        rf"\bord0\shad0\c{WHITE_COLOR}}}"
    ]
    tokens = []
    for idx in line["indices"]:
        token = group[idx]["text"]
        if idx == active_idx:
            token = rf"{{\c{ACTIVE_COLOR}}}" + token + rf"{{\c{WHITE_COLOR}}}"
        tokens.append(token)
    pieces.append(" ".join(tokens))
    return "".join(pieces)


def write_ass(groups: list[list[dict]], out_ass: Path) -> dict:
    out_ass.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "[Script Info]",
        "Title: Vertical active-word captions - contextual ASR cleanup",
        "ScriptType: v4.00+",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        f"PlayResX: {PLAY_W}",
        f"PlayResY: {PLAY_H}",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,{FONT_NAME},{FONT_SIZE},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,0,0,5,80,80,0,1",
        "Style: Bubble,Arial,1,&H00000000,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    events = []
    max_lines = 0
    max_line_chars = 0
    max_line_width = 0
    for group in groups:
        line_indices = can_break(group) or []
        max_lines = max(max_lines, len(line_indices))
        for line in line_indices:
            text = " ".join(group[i]["text"] for i in line)
            text_w, _ = visible_text_size(text)
            max_line_chars = max(max_line_chars, len(text))
            max_line_width = max(max_line_width, text_w)
        for idx, item in enumerate(group):
            event_start = max(0.0, item["start"] - HIGHLIGHT_LEAD_SECONDS)
            if idx + 1 < len(group):
                event_end = max(event_start + 0.04, group[idx + 1]["start"] - HIGHLIGHT_LEAD_SECONDS)
            else:
                event_end = max(item["end"], item["start"] + 0.08)
            if event_end - event_start < 0.04:
                event_end = event_start + 0.04
            events.append(
                {
                    "start": event_start,
                    "end": event_end,
                    "source_start": item["start"],
                    "source_end": item["end"],
                    "group": group,
                    "active_idx": idx,
                }
            )

    held_gap_count = 0
    max_gap_held = 0.0
    for idx, event in enumerate(events[:-1]):
        next_start = events[idx + 1]["start"]
        gap = next_start - event["end"]
        if gap <= 0.0:
            event["end"] = next_start
        elif gap <= HOLD_GAP_SECONDS:
            event["end"] = next_start
            held_gap_count += 1
            max_gap_held = max(max_gap_held, gap)

    for event in events:
        layout = group_layout(event["group"])
        for line in layout:
            lines.append(
                f"Dialogue: 0,{ass_time(event['start'])},{ass_time(event['end'])},Bubble,,0,0,0,,{bubble_event_text(line)}"
            )
        for line in layout:
            lines.append(
                f"Dialogue: 1,{ass_time(event['start'])},{ass_time(event['end'])},Default,,0,0,0,,{line_event_text(event['group'], line, event['active_idx'])}"
            )

    out_ass.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "ass": str(out_ass),
        "groups": len(groups),
        "events": len(events),
        "max_lines": max_lines,
        "max_line_chars": max_line_chars,
        "max_line_width": max_line_width,
        "held_gap_count": held_gap_count,
        "max_gap_held": round(max_gap_held, 3),
    }


def main() -> None:
    args = parse_args()
    if args.ctm and args.ctm.exists():
        raw_words = parse_ctm(args.ctm)
        timing_source = "nfa_ctm"
    elif args.words_json and args.words_json.exists():
        raw_words = parse_words_json(args.words_json)
        timing_source = "parakeet_words_json"
    else:
        raise FileNotFoundError("Provide an existing --ctm or --words-json input.")

    words, repeat_collapses = collapse_immediate_repeats(raw_words)
    words, filler_cleanup = remove_filler_words(words)
    words, contextual_corrections = apply_contextual_corrections(words)
    groups = build_groups(words)
    ass_report = write_ass(groups, args.out_ass)

    manifest = {
        "schema": "avalonreset.vertical-active-word-captions.v1",
        "source_video": str(args.source_video),
        "timing_source": timing_source,
        "source_ctm": str(args.ctm) if args.ctm else None,
        "source_words_json": str(args.words_json) if args.words_json else None,
        "source_transcript_json": str(args.transcript_json) if args.transcript_json else None,
        "raw_words": len(raw_words),
        "caption_words": len(words),
        "repeat_collapses": repeat_collapses,
        "filler_cleanup": filler_cleanup,
        "contextual_corrections": contextual_corrections,
        "style": {
            "play_res": [PLAY_W, PLAY_H],
            "caption_anchor": [CAPTION_X, CAPTION_Y],
            "font_name": FONT_NAME,
            "font_size": FONT_SIZE,
            "measure_font_size": MEASURE_FONT_SIZE,
            "active_color": ACTIVE_COLOR,
            "white_color": WHITE_COLOR,
            "bubble_padding": BUBBLE_PADDING,
            "bubble_radius": BUBBLE_RADIUS,
            "bubble_join_mode": BUBBLE_JOIN_MODE,
            "bubble_alpha_hex": BUBBLE_ALPHA_HEX,
            "text_vertical_adjust": TEXT_VERTICAL_ADJUST,
        },
        "timing": {
            "group_break_gap_seconds": GROUP_BREAK_GAP_SECONDS,
            "hold_gap_seconds": HOLD_GAP_SECONDS,
            "highlight_lead_seconds": HIGHLIGHT_LEAD_SECONDS,
            "repeat_collapse_gap_seconds": REPEAT_COLLAPSE_GAP_SECONDS,
        },
        "ass_report": ass_report,
        "first_word": words[0] if words else None,
        "last_word": words[-1] if words else None,
    }
    args.out_manifest.parent.mkdir(parents=True, exist_ok=True)
    args.out_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
