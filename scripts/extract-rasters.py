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
    # Aligned to concept_v7b.png proportions (720x1280)
    "hero-lower": (0, 76, 720, 302),
    "hero": (0, 0, 720, 302),
    "contributions": (0, 302, 720, 518),
    "cities": (0, 518, 720, 804),
    "planets": (0, 804, 720, 1006),
    "orbital": (0, 1006, 720, 1280),
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