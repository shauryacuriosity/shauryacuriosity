#!/usr/bin/env python3
"""Build contributions-forest.svg from GitHub GraphQL + painted forest background."""

from __future__ import annotations

import json
import os
import urllib.request
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from b64 import webp_data_uri

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "contributions-forest.svg"
LOGIN = os.environ.get("GITHUB_USER", "shauryacuriosity")

LEVEL_FILL = ["#14201888", "#1d5c3488", "#289450aa", "#3ed878cc", "#6cffaad8"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { contributionCount }
        }
      }
    }
  }
}
"""


def fetch_calendar():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    body = json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"bearer {token}"
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as res:
        data = json.loads(res.read().decode())
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def fallback_calendar():
    return {
        "totalContributions": 0,
        "weeks": [
            {
                "contributionDays": [
                    {"contributionCount": (c * 3) % 11 if r % 2 == 0 else 0}
                    for r in range(7)
                ]
            }
            for c in range(53)
        ],
    }


def build(calendar: dict) -> str:
    bg = webp_data_uri(ROOT / "assets" / "raster" / "contributions.webp")
    w, h = 720, 216
    weeks = calendar["weeks"]
    cols = len(weeks)
    cell, gap = 9, 3
    grid_w = cols * (cell + gap) - gap
    ox = (w - grid_w) / 2
    oy = 132
    cells = []
    for c, week in enumerate(weeks):
        for r, day in enumerate(week["contributionDays"]):
            count = day["contributionCount"]
            x = ox + c * (cell + gap)
            y = oy + r * (cell + gap)
            if y + cell > h - 4:
                continue
            lv = min(4, max(0, (0 if count == 0 else 1 + min(3, count // 4))))
            fill = LEVEL_FILL[lv if count else 0]
            delay = (c * 7 + r) % 40 * 0.07
            cells.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="3.2" fill="{fill}"'
                f' filter="url(#cellGlow)"><animate attributeName="opacity" values="0.7;1;0.85" dur="3.5s"'
                f' begin="{delay:.2f}s" repeatCount="indefinite"/></rect>'
            )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" overflow="hidden" role="img" aria-labelledby="ct cd">
  <title id="ct">Contribution forest</title>
  <desc id="cd">{calendar["totalContributions"]} contributions in the last year.</desc>
  <defs>
    <clipPath id="gridZone"><rect x="0" y="118" width="{w}" height="98"/></clipPath>
    <filter id="cellGlow" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="1.1" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#80ffa0" stop-opacity="0"/>
      <stop offset="45%" stop-color="#b0ffc8" stop-opacity="0.3"/>
      <stop offset="55%" stop-color="#b0ffc8" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#80ffa0" stop-opacity="0"/>
    </linearGradient>
    <style>
      @keyframes sweep {{ 0% {{ transform: translateX(-720px); }} 100% {{ transform: translateX(720px); }} }}
      .sweep-bar {{ animation: sweep 7s ease-in-out infinite; }}
      @media (prefers-reduced-motion: reduce) {{ .sweep-bar, rect animate {{ display: none; }} }}
    </style>
  </defs>
  <image href="{bg}" x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>
  <g clip-path="url(#gridZone)" opacity="0.95">{''.join(cells)}</g>
  <rect class="sweep-bar" clip-path="url(#gridZone)" x="0" y="118" width="720" height="90" fill="url(#sweep)"/>
</svg>"""


def main() -> None:
    try:
        cal = fetch_calendar()
    except Exception as e:
        print("Fallback calendar:", e)
        cal = fallback_calendar()
    OUT.write_text(build(cal), encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()