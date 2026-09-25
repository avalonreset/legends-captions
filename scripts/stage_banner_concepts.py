from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
GENERATED = Path.home() / ".codex" / "generated_images" / "019ed625-2185-74e3-a5e1-0a92eff0d01c"
OUT = ROOT / "release" / "art" / "banner-concepts"
TITLE = "Legends Ultimate Captions"
SLOGAN = "Caption accuracy, taken way too far."
PILL = "AGENTIC VIDEO CAPTIONS"
WIDTH = 1915
HEIGHT = 821


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts") / name,
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


TITLE_FONT = font("segoeuib.ttf", 88)
SLOGAN_FONT = font("seguisb.ttf", 38)
PILL_FONT = font("seguisb.ttf", 24)


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
    base = cover_crop(Image.open(src), WIDTH, HEIGHT).convert("RGBA")

    # Keep title readability consistent across wildly different art directions.
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
    pill_w = round(draw.textlength(PILL, font=PILL_FONT)) + 48
    draw.rounded_rectangle((x, pill_y, x + pill_w, pill_y + 48), radius=12, fill=cyan)
    draw.text((x + 24, pill_y + 9), PILL, font=PILL_FONT, fill=(4, 9, 12, 255))

    draw.rectangle((x, 206, x + 4, 620), fill=cyan)
    draw_text(draw, (x + 34, 284), TITLE, TITLE_FONT, white)
    draw_text(draw, (x + 38, 394), SLOGAN, SLOGAN_FONT, soft)
    draw.line((x + 38, 468, x + 660, 468), fill=cyan, width=4)

    out.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out, "WEBP", quality=88, method=6)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    latest = sorted(GENERATED.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]
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

