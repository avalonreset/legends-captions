from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "art" / "banner-concepts"
TITLE = "Legends Captions"
SLOGAN = "Caption accuracy, taken way too far."
PILL = "AGENTIC VIDEO CAPTIONS"
WIDTH = 1915
HEIGHT = 821


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    roots = [
        Path("C:/Windows/Fonts"),
        Path("/mnt/c/Windows/Fonts"),
        Path("/usr/share/fonts"),
    ]
    for root in roots:
        for candidate in (root / name, root / "segoeuib.ttf", root / "arialbd.ttf"):
            if candidate.exists():
                return ImageFont.truetype(str(candidate), size)
    raise SystemExit(f"No usable font found for {name}; aborting instead of bitmap fallback.")


def cover_crop(img: Image.Image, width: int, height: int) -> Image.Image:
    img = img.convert("RGB")
    scale = max(width / img.width, height / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - width) // 2)
    top = max(0, (resized.height - height) // 2)
    return resized.crop((left, top, left + width, top + height))


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt: ImageFont.FreeTypeFont, fill: tuple[int, int, int]) -> None:
    x, y = xy
    shadow = (0, 0, 0, 190)
    for ox, oy in [(3, 3), (0, 3), (3, 0)]:
        draw.text((x + ox, y + oy), text, font=fnt, fill=shadow)
    draw.text((x, y), text, font=fnt, fill=fill)


def compose(src: Path, out: Path) -> None:
    title_font = font("segoeuib.ttf", 88)
    slogan_font = font("seguisb.ttf", 38)
    pill_font = font("seguisb.ttf", 24)
    base = cover_crop(Image.open(src), WIDTH, HEIGHT).convert("RGBA")

    shade = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    shade_draw.rectangle((0, 0, 980, HEIGHT), fill=(0, 0, 0, 156))
    shade = shade.filter(ImageFilter.GaussianBlur(18))
    base = Image.alpha_composite(base, shade)

    draw = ImageDraw.Draw(base)
    cyan = (14, 220, 245, 255)
    white = (246, 246, 242, 255)
    soft = (205, 218, 220, 255)

    x = 96
    pill_y = 116
    pill_w = round(draw.textlength(PILL, font=pill_font)) + 48
    draw.rounded_rectangle((x, pill_y, x + pill_w, pill_y + 48), radius=12, fill=cyan)
    draw.text((x + 24, pill_y + 9), PILL, font=pill_font, fill=(4, 9, 12, 255))

    draw.rectangle((x, 206, x + 4, 620), fill=cyan)
    draw_text(draw, (x + 34, 284), TITLE, title_font, white)
    draw_text(draw, (x + 38, 394), SLOGAN, slogan_font, soft)
    draw.line((x + 38, 468, x + 660, 468), fill=cyan, width=4)

    out.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out, "WEBP", quality=88, method=6)


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage banner concepts from a local source image directory.")
    parser.add_argument("--source-dir", type=Path, required=True, help="Directory containing candidate PNG images.")
    args = parser.parse_args()
    source_dir = args.source_dir.resolve()
    if not source_dir.is_dir():
        raise SystemExit(f"Source directory does not exist: {source_dir}")

    OUT.mkdir(parents=True, exist_ok=True)
    latest = sorted(source_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]
    ordered = list(reversed(latest))
    for i, src in enumerate(ordered, 1):
        source_out = OUT / f"source-{i:02d}.png"
        shutil.copy2(src, source_out)
        compose(source_out, OUT / f"banner-concept-{i:02d}.webp")

    manifest = OUT / "README.md"
    rows = [
        "# Banner Concepts",
        "",
        f"Title: `{TITLE}`",
        f"Slogan: `{SLOGAN}`",
        "",
        "These are ten different art-direction passes. Source PNGs are preserved beside final WebP composites.",
        "",
    ]
    for i in range(1, len(ordered) + 1):
        rows.append(f"- `banner-concept-{i:02d}.webp` from `source-{i:02d}.png`")
    manifest.write_text("\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
