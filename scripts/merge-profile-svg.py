#!/usr/bin/env python3
"""Merge section SVGs into one seamless profile.svg (720 x total height)."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

SECTIONS = [
    ("hero.svg", "hero"),
    ("contributions-forest.svg", "cf"),
    ("cities.svg", "city"),
    ("planets.svg", "planet"),
    ("orbital-garden.svg", "orb"),
]

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")


def svg_tag(name: str) -> str:
    return f"{{{SVG}}}{name}"


def local(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def prefix_ids(root: ET.Element, prefix: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for el in root.iter():
        id_val = el.attrib.get("id")
        if id_val:
            new_id = f"{prefix}-{id_val}"
            mapping[id_val] = new_id
            el.attrib["id"] = new_id
        cls = el.attrib.get("class")
        if cls and "url(#" in cls:
            el.attrib["class"] = remap_refs(cls, mapping)
    # xlink hrefs and style url refs in attributes
    for el in root.iter():
        for key, val in list(el.attrib.items()):
            if isinstance(val, str) and ("url(#" in val or 'href="#' in val):
                el.attrib[key] = remap_refs(val, mapping)
        if el.text and "url(#" in el.text:
            el.text = remap_refs(el.text, mapping)
    return mapping


def remap_refs(text: str, mapping: dict[str, str]) -> str:
    def sub(m: re.Match) -> str:
        old = m.group(1)
        return f"url(#{mapping.get(old, old)})"

    return re.sub(r"url\(#([^)]+)\)", sub, text)


def strip_root(svg: ET.Element) -> tuple[list[ET.Element], list[ET.Element], dict]:
    w = float(svg.attrib.get("width", 720))
    h = float(svg.attrib.get("height", 100))
    defs_children: list[ET.Element] = []
    body: list[ET.Element] = []
    for child in list(svg):
        tag = local(child.tag)
        if tag == "defs":
            defs_children.extend(list(child))
        elif tag in ("title", "desc", "metadata"):
            continue
        else:
            body.append(child)
    return body, defs_children, {"w": w, "h": h}


def main() -> None:
    master_defs: list[ET.Element] = []
    layers: list[ET.Element] = []
    y = 0.0
    total_h = 0.0

    for filename, prefix in SECTIONS:
        path = ASSETS / filename
        tree = ET.parse(path)
        svg = tree.getroot()
        prefix_ids(svg, prefix)
        body, defs_children, meta = strip_root(svg)
        master_defs.extend(defs_children)

        # Nested SVG slices clip reliably on GitHub (group clip-path often bleeds).
        layer = ET.Element(
            svg_tag("svg"),
            {
                "x": "0",
                "y": str(int(y)),
                "width": str(int(meta["w"])),
                "height": str(int(meta["h"])),
                "viewBox": f"0 0 {int(meta['w'])} {int(meta['h'])}",
                "overflow": "hidden",
                "aria-hidden": "true",
            },
        )
        for el in body:
            layer.append(el)
        layers.append(layer)
        y += meta["h"]
        total_h += meta["h"]

    out = ET.Element(
        svg_tag("svg"),
        {
            "viewBox": f"0 0 720 {total_h:.0f}",
            "width": "720",
            "height": str(int(total_h)),
            "role": "img",
            "aria-labelledby": "profileTitle",
            "overflow": "hidden",
            "preserveAspectRatio": "xMidYMid meet",
        },
    )
    title = ET.SubElement(out, svg_tag("title"), {"id": "profileTitle"})
    title.text = "Shaurya Kansal — profile"
    defs_el = ET.SubElement(out, svg_tag("defs"))
    for d in master_defs:
        defs_el.append(d)
    style = ET.SubElement(defs_el, svg_tag("style"))
    style.text = ""
    for layer in layers:
        out.append(layer)

    out_path = ASSETS / "profile.svg"
    ET.indent(out, space="  ")
    raw = ET.tostring(out, encoding="unicode", xml_declaration=False)
    raw = re.sub(r'\sxmlns(?::xlink)?="[^"]+"', "", raw, count=0)
    raw = re.sub(
        r"<svg\s+",
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" ',
        raw,
        count=1,
    )
    out_path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n' + raw,
        encoding="utf-8",
    )
    kb = out_path.stat().st_size / 1024
    print(f"Wrote {out_path} ({kb:.1f} KB, height={int(total_h)})")
    if kb > 1500:
        print("WARNING: profile.svg exceeds 1.5 MB", file=sys.stderr)


if __name__ == "__main__":
    main()