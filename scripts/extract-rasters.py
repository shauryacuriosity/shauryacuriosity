#!/usr/bin/env python3
"""Crop optimised WebP sections from assets/source/concept_v7b.png."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "source" / "concept_v7b.png"
OUT = ROOT / "assets" / "raster"

SECTIONS = {
    # Boundaries from concept_v7b.png content scan (sums to 1280)
    "hero-lower": (0, 118, 720, 486),
    "hero": (0, 0, 720, 486),
    "contributions": (0, 486, 720, 720),
    # Skip ~12px at concept y=720: painted contrib grid row (not part of cities art).
    "cities": (0, 732, 720, 912),
    "planets": (0, 900, 720, 1040),
    "orbital": (0, 1040, 720, 1280),
}


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Missing {SRC}")
    im = Image.open(SRC)
    OUT.mkdir(parents=True, exist_ok=True)
    meta: dict = {}
    for name, box in SECTIONS.items():
        c = im.crop(box)
        path = OUT / f"{name}.webp"
        c.save(path, "WEBP", quality=85, method=6)
        meta[name] = {"box": box, "size": list(c.size), "bytes": path.stat().st_size}
    hero_lower = im.crop(SECTIONS["hero-lower"])
    cap_h = 56
    hero_lower.crop((0, 0, 720, cap_h)).save(
        OUT / "hero-sky-cap.webp", "WEBP", quality=82, method=6
    )
    meta["hero-sky-cap"] = {"size": [720, cap_h]}
    contrib_top = SECTIONS["contributions"][1]
    trees = im.crop((0, contrib_top, 720, contrib_top + 120))
    trees_path = OUT / "contributions-trees.webp"
    trees.save(trees_path, "WEBP", quality=86, method=6)
    meta["contributions-trees"] = {
        "box": (0, contrib_top, 720, contrib_top + 120),
        "size": [720, 120],
    }
    cities = im.crop(SECTIONS["cities"])
    for pname, box in {
        "sydney": (10, 58, 238, 252),
        "delhi": (245, 58, 476, 252),
        "munich": (486, 58, 712, 252),
    }.items():
        c = cities.crop(box)
        path = OUT / f"city-{pname}.webp"
        c.save(path, "WEBP", quality=88, method=6)
        meta[f"city-{pname}"] = {"box": box, "size": list(c.size), "bytes": path.stat().st_size}
    (ROOT / "scripts" / "section-meta.json").write_text(json.dumps(meta, indent=2))
    print("Extracted rasters to", OUT)


if __name__ == "__main__":
    main()