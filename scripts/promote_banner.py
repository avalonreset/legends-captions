"""Regenerate the Legends Captions banner assets in house style.

House spec (measured from cto-legends / legends-obs-kit banners):
black background, DejaVu Sans Mono, lowercase red slug title, thin gray
rule, lowercase white tagline, thin red bar on the left edge.

Outputs: assets/banner.webp, assets/banner.png (4096x1024),
assets/social-preview.png (1280x640).

Usage: ``python scripts/promote_banner.py``
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

TITLE = "legends-captions"
TAGLINE = (
    "agentic caption qa: contextual correction,",
    "forced alignment, active-word renders, proof",
)

RED = (255, 0, 0)
GRAY = (102, 102, 102)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FONT_CANDIDATES = [
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    Path("/mnt/c/Windows/Fonts/consola.ttf"),
    Path("C:/Windows/Fonts/consola.ttf"),
]


def mono(size: int) -> ImageFont.FreeTypeFont:
    for candidate in FONT_CANDIDATES:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    raise SystemExit("No monospace font found; aborting.")


def render(width: int, height: int) -> Image.Image:
    scale = width / 4096
    img = Image.new("RGB", (width, height), BLACK)
    draw = ImageDraw.Draw(img)

    bar_w = max(2, round(8 * scale))
    draw.rectangle((0, 0, bar_w - 1, height - 1), fill=RED)

    title_font = mono(round(175 * scale))
    tag_font = mono(round(106 * scale))
    margin = round(204 * scale)
    tag_x = round(303 * scale)

    draw.text((margin, round(213 * scale)), TITLE, font=title_font, fill=RED, anchor="lt")
    rule_y = round(456 * scale)
    draw.line((margin, rule_y, width - margin, rule_y), fill=GRAY, width=max(1, round(3 * scale)))
    draw.text((tag_x, round(534 * scale)), TAGLINE[0], font=tag_font, fill=WHITE, anchor="lt")
    draw.text((tag_x, round(668 * scale)), TAGLINE[1], font=tag_font, fill=WHITE, anchor="lt")
    return img


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    banner = render(4096, 1024)
    banner.save(ASSETS / "banner.webp", "WEBP", quality=90, method=6)
    banner.save(ASSETS / "banner.png", "PNG")
    social = render(1280, 640)
    social.save(ASSETS / "social-preview.png", "PNG")
    print("wrote banner.webp, banner.png, social-preview.png")


if __name__ == "__main__":
    main()
