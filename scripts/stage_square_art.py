from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "art" / "square-meme-options"

CONCEPTS = [
    ("deadpan-office-incident", "BAD CAPTIONS ARE A PRODUCTION INCIDENT"),
    ("fake-safety-label", "DO NOT SHIP RAW AUTO CAPTIONS"),
    ("tabloid-overbuilt-caption-system", "LOCAL MAN BUILDS CAPTION SYSTEM WAY TOO HARD"),
    ("museum-correct-caption", "BEHOLD: A CORRECT CAPTION"),
    ("courtroom-timing-evidence", "YOUR HONOR, THE TIMING IS CLEAN"),
    ("luxury-caption-fragrance", "EAU DE CORRECT CAPTION"),
    ("before-after-autocaption-soup", "FROM AUTOCAPTION SOUP TO CLEAN TIMING"),
    ("support-ticket-captions-wrong", "TICKET: THE CAPTIONS ARE WRONG AGAIN"),
    ("caption-war-room", "OPERATION: MAKE THE CAPTIONS NOT SUCK"),
    ("infomercial-absurd-accuracy", "JUST ADD ABSURDLY ACCURATE CAPTIONS"),
    ("fine-dining-captions", "FINALLY, CAPTIONS WITH TASTE"),
    ("impossible-caption-tools", "WE FIX CAPTIONS WITH TOOLS THAT SHOULD NOT EXIST"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage square concept art from a local source image directory.")
    parser.add_argument("--source-dir", type=Path, required=True, help="Directory containing candidate PNG images.")
    args = parser.parse_args()
    source_dir = args.source_dir.resolve()
    if not source_dir.is_dir():
        raise SystemExit(f"Source directory does not exist: {source_dir}")

    OUT.mkdir(parents=True, exist_ok=True)
    latest = sorted(source_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)[: len(CONCEPTS)]
    ordered = list(reversed(latest))
    manifest = []
    for i, (src, concept) in enumerate(zip(ordered, CONCEPTS), 1):
        slug, text = concept
        dest = OUT / f"option-{i:02d}-{slug}.png"
        shutil.copy2(src, dest)
        manifest.append(
            {
                "option": i,
                "slug": slug,
                "text_prompt": text,
                "file": dest.name,
                "source": src.name,
            }
        )

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    readme = [
        "# Square Meme Art Options",
        "",
        "Twelve distinct square concepts for Skool release/community posts.",
        "",
    ]
    for item in manifest:
        readme.append(f"- `{item['file']}` - {item['text_prompt']}")
    (OUT / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
