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
    "hero": (0, 0, 720, 308),
    "contributions": (0, 308, 720, 505),
    "cities": (0, 505, 720, 788),
    "planets": (0, 788, 720, 1008),
    "orbital": (0, 1008, 720, 1280),
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
        "sydney": (8, 52, 238, 248),
        "delhi": (243, 52, 478, 248),
        "munich": (483, 52, 712, 248),
    }.items():
        c = cities.crop(box)
        path = OUT / f"city-{pname}.webp"
        c.save(path, "WEBP", quality=88, method=6)
        meta[f"city-{pname}"] = {"box": box, "size": list(c.size), "bytes": path.stat().st_size}
    (ROOT / "scripts" / "section-meta.json").write_text(json.dumps(meta, indent=2))
    print("Extracted rasters to", OUT)


if __name__ == "__main__":
    main()