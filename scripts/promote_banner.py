"""Regenerate the promoted Legends Captions banner assets.

Composites the v2 text treatment (kicker pill, two-line title, slogan)
onto the preserved AI-generated source art, then promotes the winner to
``assets/``. Replaces the ad-hoc v2 step with a reproducible script.

Usage: ``python scripts/promote_banner.py``
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "release" / "art" / "banner-v2-concepts" / "source-v2-01.png"
V2 = ROOT / "release" / "art" / "banner-v2-concepts"
ASSETS = ROOT / "assets"

LINE1 = "LEGENDS"
LINE2 = "CAPTIONS"
SLOGAN = "Caption accuracy, taken way too far."
PILL = "AGENTIC VIDEO CAPTIONS"

CYAN = (14, 200, 230, 255)
WHITE = (246, 246, 242, 255)
SOFT = (205, 218, 220, 255)
INK = (4, 9, 12, 255)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    roots = [
        Path("C:/Windows/Fonts"),
        Path("/mnt/c/Windows/Fonts"),
        Path("/usr/share/fonts"),
    ]
    for root in roots:
        candidate = root / name
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    fallback = root / "arialbd.ttf" if (root / "arialbd.ttf").exists() else None
    if fallback is not None:
        return ImageFont.truetype(str(fallback), size)
    return ImageFont.load_default()


LINE1_FONT = font("segoeui.ttf", 112)
LINE2_FONT = font("seguibl.ttf", 150)
SLOGAN_FONT = font("segoeui.ttf", 46)
PILL_FONT = font("segoeuib.ttf", 30)


def cover_crop(img: Image.Image, width: int, height: int) -> Image.Image:
    img = img.convert("RGB")
    scale = max(width / img.width, height / img.height)
    resized = img.resize(
        (round(img.width * scale), round(img.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = max(0, (resized.width - width) // 2)
    top = max(0, (resized.height - height) // 2)
    return resized.crop((left, top, left + width, top + height))


def draw_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
) -> None:
    x, y = xy
    shadow = (0, 0, 0, 190)
    for ox, oy in [(3, 3), (0, 3), (3, 0)]:
        draw.text((x + ox, y + oy), text, font=fnt, fill=shadow)
    draw.text((x, y), text, font=fnt, fill=fill)


def compose(width: int, height: int, y_off: int = 0) -> Image.Image:
    base = cover_crop(Image.open(SRC), width, height).convert("RGBA")

    shade = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    shade_draw.rectangle((0, 0, 1050, height), fill=(0, 0, 0, 150))
    shade = shade.filter(ImageFilter.GaussianBlur(24))
    base = Image.alpha_composite(base, shade)

    draw = ImageDraw.Draw(base)
    x = 96
    pill_y = 112 + y_off
    pill_w = round(draw.textlength(PILL, font=PILL_FONT)) + 48
    draw.rounded_rectangle((x - 48, pill_y, x - 48 + pill_w, pill_y + 52), radius=12, fill=CYAN)
    draw.text((x - 24, pill_y + 8), PILL, font=PILL_FONT, fill=INK)

    rule_top = pill_y
    rule_bottom = 660 + y_off
    draw.rectangle((x - 61, rule_top, x - 55, rule_bottom), fill=CYAN)

    draw_text(draw, (x + 22, 195 + y_off), LINE1, LINE1_FONT, WHITE)
    draw_text(draw, (x + 22, 325 + y_off), LINE2, LINE2_FONT, WHITE)
    draw_text(draw, (x + 22, 525 + y_off), SLOGAN, SLOGAN_FONT, SOFT)
    draw.line((x + 22, 600 + y_off, x + 592, 600 + y_off), fill=CYAN, width=5)
    return base.convert("RGB")


def main() -> None:
    wide = compose(1920, 820)
    tall = compose(1920, 1080, y_off=110)
    wide.save(V2 / "banner-v2-01-wide.webp", "WEBP", quality=88, method=6)
    tall.save(V2 / "banner-v2-01-16x9.webp", "WEBP", quality=88, method=6)
    wide.save(ASSETS / "banner.webp", "WEBP", quality=88, method=6)
    tall.save(ASSETS / "banner-16x9.webp", "WEBP", quality=88, method=6)

    social = tall.resize((1280, 720), Image.Resampling.LANCZOS)
    social.crop((0, 40, 1280, 680)).save(ASSETS / "social-preview.jpg", "JPEG", quality=90)
    print("promoted banner.webp, banner-16x9.webp, social-preview.jpg")


if __name__ == "__main__":
    main()
