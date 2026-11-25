#!/usr/bin/env python3
"""Build hero, cities, planets, and orbital SVGs with embedded raster + vector animation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from b64 import webp_data_uri

ROOT = Path(__file__).resolve().parents[1]
RASTER = ROOT / "assets" / "raster"
ASSETS = ROOT / "assets"

REDUCED = """
      @media (prefers-reduced-motion: reduce) {
        .motion, .motion * { animation: none !important; }
        animate, animateTransform, animateMotion { display: none; }
      }
"""


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    kb = path.stat().st_size / 1024
    print(f"Wrote {path.name}: {kb:.1f} KB")


def build_hero() -> None:
    bg_lower = webp_data_uri(RASTER / "hero-lower.webp")
    sky_cap = webp_data_uri(RASTER / "hero-sky-cap.webp")
    w, h = 720, 486
    title_h = 92
    paint_y = 72
    img_h = h - paint_y
    exhaust_x, exhaust_y = 524, round(paint_y + 266 * (img_h / 368))
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" overflow="hidden" role="img" aria-labelledby="heroTitle">
  <title id="heroTitle">Shaurya Kansal</title>
  <defs>
    <radialGradient id="exhaust" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#fff8e8"/><stop offset="35%" stop-color="#ffcc66"/><stop offset="100%" stop-color="#ff6600" stop-opacity="0"/></radialGradient>
    <radialGradient id="plume" cx="50%" cy="0%" r="80%"><stop offset="0%" stop-color="#fff" stop-opacity="0.65"/><stop offset="50%" stop-color="#ffe0a0" stop-opacity="0.25"/><stop offset="100%" stop-color="#88c8ff" stop-opacity="0"/></radialGradient>
    <linearGradient id="aurora" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#40e8d0" stop-opacity="0"/><stop offset="50%" stop-color="#60ffd8" stop-opacity="0.22"/><stop offset="100%" stop-color="#40e8d0" stop-opacity="0"/></linearGradient>
    <linearGradient id="titleSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#141e2c"/><stop offset="100%" stop-color="#1c2a38"/></linearGradient>
    <linearGradient id="skyFeather" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#141e2c" stop-opacity="0.98"/><stop offset="45%" stop-color="#1a2838" stop-opacity="0.55"/><stop offset="100%" stop-color="#243040" stop-opacity="0"/></linearGradient>
    <filter id="skyBlur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="8"/></filter>
    <filter id="glow"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <style>
      @keyframes dash {{ to {{ stroke-dashoffset: -48; }} }}
      @keyframes pulse {{ 0%,100% {{ opacity:.35; r:3; }} 50% {{ opacity:.9; r:5; }} }}
      @keyframes exhaustFlicker {{ 0%,100% {{ opacity:.55; transform:scale(1,1); }} 45% {{ opacity:.95; transform:scale(1.08,1.15); }} }}
      @keyframes aurora {{ 0%,100% {{ opacity:.12; transform:translateX(-6%); }} 50% {{ opacity:.28; transform:translateX(6%); }} }}
      @keyframes twinkle {{ 0%,100% {{ opacity:.15; }} 50% {{ opacity:.85; }} }}
      .path-pulse {{ stroke-dasharray:6 18; animation:dash 5s linear infinite; }}
      .node-pulse {{ animation:pulse 2.8s ease-in-out infinite; }}
      .exhaust-f {{ transform-origin:{exhaust_x}px {exhaust_y}px; animation:exhaustFlicker 1.4s ease-in-out infinite; }}
      .aurora-band {{ animation:aurora 18s ease-in-out infinite; }}
      .star {{ animation:twinkle 4s ease-in-out infinite; }}
      {REDUCED}
    </style>
  </defs>
  <image href="{bg_lower}" x="0" y="{paint_y}" width="{w}" height="{img_h}" preserveAspectRatio="xMidYMid slice"/>
  <image href="{sky_cap}" x="0" y="{paint_y}" width="{w}" height="72" preserveAspectRatio="none" opacity="0.45" filter="url(#skyBlur)"/>
  <rect x="0" y="{paint_y}" width="{w}" height="88" fill="url(#skyFeather)"/>
  <rect x="0" y="0" width="{w}" height="{title_h}" fill="url(#titleSky)"/>
  <text x="360" y="38" text-anchor="middle" fill="#e8f6f4" font-family="system-ui,-apple-system,sans-serif" font-size="24" font-weight="300" letter-spacing="0.24em">SHAURYA KANSAL</text>
  <text x="360" y="60" text-anchor="middle" fill="#b8d0d8" font-family="system-ui,sans-serif" font-size="11" letter-spacing="0.06em">Founder, SCYCLE AI // building Yuga</text>
  <rect class="motion aurora-band" x="-40" y="{title_h - 6}" width="800" height="48" fill="url(#aurora)"/>
  <g fill="none" stroke="#5cf0e0" stroke-width="1.2" filter="url(#glow)" opacity=".75" class="motion" transform="translate(0,{paint_y})">
    <path class="path-pulse" d="M145 52 Q260 28 380 38 Q500 18 620 36"/>
    <path class="path-pulse" style="animation-delay:-1.6s" d="M200 62 Q320 42 450 52"/>
    <circle r="3.5" fill="#7dffd8" class="node-pulse"><animateMotion dur="5s" repeatCount="indefinite" path="M145 52 Q260 28 380 38 Q500 18 620 36"/></circle>
  </g>
  <g class="motion" fill="#6dffd0" filter="url(#glow)" transform="translate(0,{paint_y})">
    <circle class="node-pulse" cx="140" cy="48" r="3"/><circle class="node-pulse" cx="265" cy="32" r="3.5" style="animation-delay:.4s"/>
    <circle class="node-pulse" cx="385" cy="28" r="3" style="animation-delay:.8s"/><circle class="node-pulse" cx="535" cy="26" r="3" style="animation-delay:.6s"/>
  </g>
  <g class="motion star" fill="#fff">
    <circle cx="88" cy="78" r="1"/><circle cx="310" cy="72" r="1.1" style="animation-delay:.5s"/><circle cx="540" cy="68" r=".9" style="animation-delay:1.1s"/>
  </g>
  <g class="motion exhaust-f">
    <ellipse cx="{exhaust_x}" cy="{exhaust_y}" rx="20" ry="11" fill="url(#exhaust)" opacity=".88"/>
    <ellipse cx="{exhaust_x}" cy="{exhaust_y + 6}" rx="12" ry="18" fill="url(#plume)" opacity=".5"><animate attributeName="ry" values="16;22;17" dur="2.2s" repeatCount="indefinite"/></ellipse>
  </g>
</svg>"""
    write(ASSETS / "hero.svg", svg)


def monument_blueprints() -> dict[str, str]:
    return {
        "sydney": '''
  <path class="bp-line" d="M25 115 Q45 82 65 112 Q78 95 92 112 Q108 72 125 112 Q138 95 152 112 Q168 85 188 112 L188 126 L25 126 Z"/>
  <path class="bp-line" d="M118 98 Q130 78 142 98"/>
  <line class="bp-line" x1="55" y1="122" x2="165" y2="122"/>''',
        "delhi": '''
  <path class="bp-line" d="M50 120 L115 72 L180 120 Z"/>
  <rect class="bp-line" x="105" y="92" width="20" height="28"/>
  <line class="bp-line" x1="75" y1="108" x2="155" y2="108"/>''',
        "munich": '''
  <path class="bp-line" d="M55 118 L72 76 L88 118 Z"/>
  <path class="bp-line" d="M95 118 L118 62 L142 118 Z"/>
  <path class="bp-line" d="M148 118 L168 78 L188 118 Z"/>
  <ellipse class="bp-line" cx="72" cy="74" rx="7" ry="9"/><ellipse class="bp-line" cx="118" cy="58" rx="8" ry="10"/><ellipse class="bp-line" cx="168" cy="76" rx="7" ry="9"/>''',
    }


def build_cities() -> None:
    bg = webp_data_uri(RASTER / "cities.webp")
    panels = [
        ("sydney", 10, 48, 228, 124, 0),
        ("delhi", 245, 48, 231, 124, 4),
        ("munich", 486, 48, 226, 124, 8),
    ]
    bp = monument_blueprints()
    w, h = 720, 180
    dur = 12
    panel_clips = []
    panel_groups = []
    for name, px, py, pw, ph, begin in panels:
        panel_clips.append(f'<clipPath id="panel-frame-{name}"><rect width="{pw}" height="{ph}" rx="4"/></clipPath>')
        panel_groups.append(f'''
  <g transform="translate({px},{py})">
    <g clip-path="url(#panel-frame-{name})">
      <rect width="{pw}" height="{ph}" fill="#051018" opacity="0.18">
        <animate attributeName="opacity" values="0.16;0.16;0;0;0.18" keyTimes="0;0.28;0.48;0.72;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
      </rect>
      <g stroke="#4de8ff" fill="none" stroke-width="1" transform="translate(0,8)" opacity="0.85">
        {bp[name]}
        <animate attributeName="opacity" values="0.9;0.9;0.15;0;0.85" keyTimes="0;0.28;0.5;0.72;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
      </g>
      <line x1="-1" y1="0" x2="-1" y2="{ph}" stroke="url(#laserGrad)" stroke-width="1.5" stroke-linecap="round" filter="url(#laserGlow)" opacity="0">
        <animate attributeName="x1" values="-2;-2;{pw};{pw};-2" keyTimes="0;0.32;0.58;0.74;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
        <animate attributeName="x2" values="-2;-2;{pw};{pw};-2" keyTimes="0;0.32;0.58;0.74;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;0;0.55;0.55;0" keyTimes="0;0.30;0.35;0.70;0.78" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
      </line>
    </g>
  </g>''')

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" overflow="hidden" role="img" aria-labelledby="citiesTitle">
  <title id="citiesTitle">Sydney, Delhi, Munich</title>
  <defs>
    <linearGradient id="laserGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#00ffff" stop-opacity="0"/>
      <stop offset="40%" stop-color="#88ffff" stop-opacity="1"/>
      <stop offset="60%" stop-color="#88ffff" stop-opacity="1"/>
      <stop offset="100%" stop-color="#00ffff" stop-opacity="0"/>
    </linearGradient>
    <filter id="laserGlow" x="-200%" y="-20%" width="400%" height="140%"><feGaussianBlur stdDeviation="1.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    {''.join(panel_clips)}
    <style>
      @keyframes arc-dash {{ to {{ stroke-dashoffset: -80; }} }}
      .arc {{ stroke-dasharray: 8 14; animation: arc-dash 6s linear infinite; }}
      .bp-line {{ stroke-dasharray: 220; stroke-dashoffset: 220; animation: drawbp 12s ease-in-out infinite; }}
      @keyframes drawbp {{ 0%,18% {{ stroke-dashoffset: 220; }} 35%,65% {{ stroke-dashoffset: 0; }} 82%,100% {{ stroke-dashoffset: 220; }} }}
      {REDUCED}
    </style>
  </defs>
  <image href="{bg}" x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>
  <path class="motion arc" d="M 228 118 Q 360 98 492 118" fill="none" stroke="#3cc8b8" stroke-width="1" opacity="0.35"/>
  {''.join(panel_groups)}
</svg>"""
    write(ASSETS / "cities.svg", svg)


def build_planets() -> None:
    bg = webp_data_uri(RASTER / "planets.webp")
    w, h = 720, 140
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="planetsTitle">
  <title id="planetsTitle">Yuga, Cyra, Research</title>
  <defs>
    <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <style>
      @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
      @keyframes moon {{ from {{ offset-distance: 0%; }} to {{ offset-distance: 100%; }} }}
      .ring {{ transform-origin: center; animation: spin 22s linear infinite; }}
      .ring2 {{ animation-duration: 28s; animation-direction: reverse; }}
      .moon {{ offset-path: path('M -52 0 A 52 14 0 1 1 52 0 A 52 14 0 1 1 -52 0'); animation: moon 8s linear infinite; }}
      {REDUCED}
    </style>
  </defs>
  <image href="{bg}" x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>
  <g filter="url(#glow)">
    <g transform="translate(120,88)"><ellipse class="ring" cx="0" cy="0" rx="48" ry="13" fill="none" stroke="#5ce8c8" stroke-width="1" opacity=".45"/></g>
    <g transform="translate(600,90)"><ellipse class="ring ring2" cx="0" cy="0" rx="44" ry="12" fill="none" stroke="#8cff70" stroke-width="1" opacity=".4"/></g>
  </g>
</svg>"""
    write(ASSETS / "planets.svg", svg)


def build_orbital() -> None:
    bg = webp_data_uri(RASTER / "orbital.webp")
    w, h = 720, 240
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="orbitalTitle">
  <title id="orbitalTitle">Orbital garden</title>
  <defs>
    <linearGradient id="shimmer" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#80ffc0" stop-opacity="0"/>
      <stop offset="50%" stop-color="#b0ffe0" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#80ffc0" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="shimmerClip"><rect x="0" y="0" width="{w}" height="{h - 36}"/></clipPath>
    <style>
      @keyframes shimmer {{ 0% {{ transform:translateX(-100%); }} 100% {{ transform:translateX(100%); }} }}
      @keyframes drift {{ 0%,100% {{ transform:translate(0,0); }} 50% {{ transform:translate(4px,-3px); }} }}
      .shimmer-band {{ animation: shimmer 16s linear infinite; }}
      .ship {{ animation: drift 9s ease-in-out infinite; }}
      {REDUCED}
    </style>
  </defs>
  <image href="{bg}" x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>
  <g clip-path="url(#shimmerClip)">
    <rect class="motion shimmer-band" x="-180" y="36" width="360" height="140" fill="url(#shimmer)"/>
    <g class="motion ship">
      <ellipse cx="175" cy="148" rx="24" ry="7" fill="#60e8ff" opacity=".28"><animate attributeName="opacity" values=".18;.4;.2" dur="2s" repeatCount="indefinite"/></ellipse>
    </g>
  </g>
</svg>"""
    write(ASSETS / "orbital-garden.svg", svg)


def main() -> None:
    build_hero()
    build_cities()
    build_planets()
    build_orbital()


if __name__ == "__main__":
    main()