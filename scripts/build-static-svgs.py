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
    w, h = 720, 486
    title_h = 92
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" overflow="hidden" role="img" aria-labelledby="heroTitle">
  <title id="heroTitle">Shaurya Kansal</title>
  <defs>
    <radialGradient id="exhaust" cx="50%" cy="50%"><stop offset="0%" stop-color="#fff"/><stop offset="40%" stop-color="#ffe8a0"/><stop offset="100%" stop-color="#ff8800" stop-opacity="0"/></radialGradient>
    <linearGradient id="plume" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#fff" stop-opacity="0.5"/><stop offset="100%" stop-color="#88c8ff" stop-opacity="0"/></linearGradient>
    <linearGradient id="aurora" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#40e8d0" stop-opacity="0"/><stop offset="50%" stop-color="#60ffd8" stop-opacity="0.25"/><stop offset="100%" stop-color="#40e8d0" stop-opacity="0"/></linearGradient>
    <linearGradient id="titleSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#141e2c"/><stop offset="70%" stop-color="#1a2838"/><stop offset="100%" stop-color="#243040"/></linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <style>
      @keyframes dash {{ to {{ stroke-dashoffset: -48; }} }}
      @keyframes pulse {{ 0%,100% {{ opacity:.4; r:3; }} 50% {{ opacity:1; r:5.5; }} }}
      @keyframes rocketLift {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-6px); }} }}
      @keyframes exhaustFlicker {{ 0%,100% {{ opacity:.75; transform:scale(1,1); }} 40% {{ opacity:1; transform:scale(1.1,1.25); }} }}
      @keyframes aurora {{ 0%,100% {{ opacity:.15; transform:translateX(-8%); }} 50% {{ opacity:.35; transform:translateX(8%); }} }}
      @keyframes twinkle {{ 0%,100% {{ opacity:.2; }} 50% {{ opacity:.95; }} }}
      .path-pulse {{ stroke-dasharray:6 18; animation:dash 5s linear infinite; }}
      .node-pulse {{ animation:pulse 2.8s ease-in-out infinite; }}
      .rocket-g {{ transform-origin:600px 248px; animation:rocketLift 12s ease-in-out infinite; }}
      .exhaust-f {{ transform-origin:600px 255px; animation:exhaustFlicker 1.2s ease-in-out infinite; }}
      .aurora-band {{ animation:aurora 18s ease-in-out infinite; }}
      .star {{ animation:twinkle 4s ease-in-out infinite; }}
      {REDUCED}
    </style>
  </defs>
  <image href="{bg_lower}" x="0" y="{title_h}" width="{w}" height="{h - title_h}" preserveAspectRatio="xMidYMid slice"/>
  <rect x="0" y="0" width="{w}" height="{title_h}" fill="url(#titleSky)"/>
  <rect x="0" y="{title_h}" width="{w}" height="32" fill="url(#titleSky)" opacity="0.96"/>
  <text x="360" y="38" text-anchor="middle" fill="#e8f6f4" font-family="system-ui,-apple-system,sans-serif" font-size="24" font-weight="300" letter-spacing="0.24em">SHAURYA KANSAL</text>
  <text x="360" y="60" text-anchor="middle" fill="#b8d0d8" font-family="system-ui,sans-serif" font-size="11" letter-spacing="0.06em">Founder, SCYCLE AI // building Yuga</text>
  <rect class="motion aurora-band" x="-40" y="{title_h - 8}" width="800" height="40" fill="url(#aurora)"/>
  <!-- Flight paths -->
  <g fill="none" stroke="#5cf0e0" stroke-width="1.4" filter="url(#glow)" opacity=".85" class="motion">
    <path class="path-pulse" d="M145 171 Q260 126 380 141 Q500 111 620 134"/>
    <path class="path-pulse" style="animation-delay:-1.6s" d="M200 186 Q320 151 450 164"/>
    <path class="path-pulse" style="animation-delay:-3.2s" d="M90 181 Q220 136 340 154"/>
    <circle r="4" fill="#7dffd8" class="node-pulse"><animateMotion dur="5s" repeatCount="indefinite" path="M145 171 Q260 126 380 141 Q500 111 620 134"/></circle>
    <circle r="3" fill="#afffe8" class="node-pulse" style="animation-delay:-2s"><animateMotion dur="7s" begin="1s" repeatCount="indefinite" path="M200 186 Q320 151 450 164"/></circle>
  </g>
  <!-- Map nodes -->
  <g class="motion" fill="#6dffd0" filter="url(#glow)">
    <circle class="node-pulse" cx="140" cy="168" r="3"/><circle class="node-pulse" cx="265" cy="144" r="4" style="animation-delay:.4s"/>
    <circle class="node-pulse" cx="385" cy="138" r="3.5" style="animation-delay:.8s"/><circle class="node-pulse" cx="455" cy="154" r="3" style="animation-delay:1.2s"/>
    <circle class="node-pulse" cx="535" cy="134" r="4" style="animation-delay:.6s"/><circle class="node-pulse" cx="610" cy="148" r="3" style="animation-delay:1s"/>
  </g>
  <g class="motion star" fill="#fff">
    <circle cx="88" cy="98" r="1"/><circle cx="310" cy="92" r="1.2" style="animation-delay:.5s"/><circle cx="540" cy="86" r="1" style="animation-delay:1.1s"/>
    <circle cx="680" cy="105" r=".9" style="animation-delay:1.7s"/>
  </g>
  <g class="motion rocket-g exhaust-f">
    <ellipse cx="600" cy="246" rx="18" ry="32" fill="url(#exhaust)" opacity=".9"/>
    <ellipse cx="600" cy="262" rx="10" ry="22" fill="url(#plume)" opacity=".55"/>
    <ellipse cx="598" cy="279" rx="6" ry="14" fill="#a0c8e0" opacity=".25"><animate attributeName="opacity" values=".1;.4;.1" dur="2s" repeatCount="indefinite"/></ellipse>
    <path d="M595 278 Q590 295 585 305 Q598 290 605 305 Q602 292 595 278" fill="#c8d8e8" opacity=".2"><animate attributeName="opacity" values=".1;.35;.15;.3;.1" dur="3s" repeatCount="indefinite"/></path>
    <path d="M608 275 Q615 292 620 302 Q612 288 600 300" fill="#e0eef8" opacity=".15"><animate attributeName="d" values="M608 275 Q615 292 620 302 Q612 288 600 300;M608 273 Q618 295 625 308 Q610 290 598 305;M608 275 Q615 292 620 302 Q612 288 600 300" dur="4s" repeatCount="indefinite"/></path>
  </g>
</svg>"""
    write(ASSETS / "hero.svg", svg)


def monument_blueprints() -> dict[str, str]:
    """Vector wireframes for each city panel (230x196 viewBox)."""
    return {
        "sydney": '''
  <path class="bp-line" d="M25 145 Q45 105 65 138 Q78 118 92 138 Q108 95 125 138 Q138 118 152 138 Q168 108 188 138 L188 155 L25 155 Z"/>
  <path class="bp-line" d="M70 140 Q82 115 94 140"/><path class="bp-line" d="M118 125 Q130 100 142 125"/>
  <line class="bp-line" x1="55" y1="152" x2="165" y2="152"/>''',
        "delhi": '''
  <path class="bp-line" d="M50 150 L115 95 L180 150 Z"/>
  <rect class="bp-line" x="105" y="118" width="20" height="35"/>
  <path class="bp-line" d="M60 150 L60 90 M170 150 L170 90"/>
  <line class="bp-line" x1="75" y1="135" x2="155" y2="135"/>''',
        "munich": '''
  <path class="bp-line" d="M55 145 L72 95 L88 145 Z"/>
  <path class="bp-line" d="M95 145 L118 78 L142 145 Z"/>
  <path class="bp-line" d="M148 145 L168 98 L188 145 Z"/>
  <ellipse class="bp-line" cx="72" cy="92" rx="8" ry="10"/><ellipse class="bp-line" cx="118" cy="72" rx="9" ry="11"/><ellipse class="bp-line" cx="168" cy="94" rx="8" ry="10"/>
  <rect class="bp-line" x="48" y="145" width="145" height="12"/>''',
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
      <rect width="{pw}" height="{ph}" fill="#051018" opacity="0.45">
        <animate attributeName="opacity" values="0.42;0.42;0;0;0.4" keyTimes="0;0.28;0.48;0.72;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
      </rect>
      <g stroke="#4de8ff" fill="none" stroke-width="1.2" transform="translate(0,12)">
        {bp[name]}
        <animate attributeName="opacity" values="1;1;0.2;0;1" keyTimes="0;0.28;0.5;0.72;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
      </g>
      <rect y="0" width="14" height="{ph}" fill="url(#laserGrad)" opacity="0.85">
        <animate attributeName="x" values="-16;-16;{pw};{pw};-16" keyTimes="0;0.3;0.55;0.72;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
      </rect>
    </g>
  </g>''')

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" overflow="hidden" role="img" aria-labelledby="citiesTitle">
  <title id="citiesTitle">Sydney, Delhi, Munich</title>
  <defs>
    <linearGradient id="laserGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#00ffff" stop-opacity="0"/>
      <stop offset="45%" stop-color="#66ffff" stop-opacity="1"/>
      <stop offset="55%" stop-color="#66ffff" stop-opacity="1"/>
      <stop offset="100%" stop-color="#00ffff" stop-opacity="0"/>
    </linearGradient>
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
  <path class="motion arc" d="M 228 118 Q 360 98 492 118" fill="none" stroke="#3cc8b8" stroke-width="1.2" opacity="0.45"/>
  {''.join(panel_groups)}
  <text x="360" y="173" text-anchor="middle" fill="#6a98a8" font-size="7.5" letter-spacing="0.16em" opacity="0.85">engineered live</text>
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
      @keyframes labelGlow {{ 0%,100% {{ opacity:.85; }} 50% {{ opacity:1; }} }}
      .ring {{ transform-origin: center; animation: spin 22s linear infinite; }}
      .ring2 {{ animation-duration: 28s; animation-direction: reverse; }}
      .moon {{ offset-path: path('M -52 0 A 52 14 0 1 1 52 0 A 52 14 0 1 1 -52 0'); animation: moon 8s linear infinite; }}
      .star {{ animation: labelGlow 3s ease-in-out infinite; }}
      {REDUCED}
    </style>
  </defs>
  <image href="{bg}" x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>
  <g class="motion star" fill="#e8f4ff" opacity=".7">
    <circle cx="40" cy="30" r=".8"/><circle cx="180" cy="18" r="1"/><circle cx="620" cy="25" r=".9"/><circle cx="700" cy="55" r=".7"/>
  </g>
  <g filter="url(#glow)">
    <g transform="translate(120,118)"><ellipse class="ring" cx="0" cy="0" rx="54" ry="15" fill="none" stroke="#5ce8c8" stroke-width="1" opacity=".55"/><circle class="moon motion" r="3" fill="#c0fff0"/></g>
    <g transform="translate(600,122)"><ellipse class="ring ring2" cx="0" cy="0" rx="50" ry="13" fill="none" stroke="#8cff70" stroke-width="1" opacity=".5"/><circle class="moon motion" r="2.5" fill="#d0ffb8" style="animation-delay:-2s"/></g>
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
      <stop offset="50%" stop-color="#b0ffe0" stop-opacity="0.2"/>
      <stop offset="100%" stop-color="#80ffc0" stop-opacity="0"/>
    </linearGradient>
    <style>
      @keyframes shimmer {{ 0% {{ transform:translateX(-100%); }} 100% {{ transform:translateX(100%); }} }}
      @keyframes twinkle {{ 0%,100% {{ opacity:.3; }} 50% {{ opacity:1; }} }}
      @keyframes drift {{ 0%,100% {{ transform:translate(0,0); }} 50% {{ transform:translate(6px,-4px); }} }}
      .shimmer-band {{ animation: shimmer 14s linear infinite; }}
      .tw {{ animation: twinkle 2.5s ease-in-out infinite; }}
      .ship {{ animation: drift 9s ease-in-out infinite; }}
      {REDUCED}
    </style>
  </defs>
  <image href="{bg}" x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>
  <rect class="motion shimmer-band" x="-200" y="40" width="400" height="180" fill="url(#shimmer)"/>
  <g class="motion ship">
    <ellipse cx="175" cy="155" rx="28" ry="8" fill="#60e8ff" opacity=".35"><animate attributeName="opacity" values=".2;.5;.2" dur="1.8s" repeatCount="indefinite"/></ellipse>
  </g>
  <g class="motion tw" fill="#fff">
    <circle cx="520" cy="95" r="1.2"/><circle cx="545" cy="88" r="1" style="animation-delay:.6s"/><circle cx="568" cy="102" r=".9" style="animation-delay:1.1s"/>
    <circle cx="595" cy="92" r="1.1" style="animation-delay:1.4s"/>
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