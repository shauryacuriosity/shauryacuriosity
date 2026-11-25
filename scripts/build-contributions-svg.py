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

LEVEL_FILL = ["#0c1814", "#1d5c34", "#289450", "#3ed878", "#6cffaa"]
MONTHS = ["Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]

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
    w, h = 720, 234
    weeks = calendar["weeks"]
    cols = len(weeks)
    cell, gap = 9, 3
    grid_w = cols * (cell + gap) - gap
    ox = (w - grid_w) / 2
    grid_top = 128
    oy = 142
    row_h = cell + gap
    grid_bottom = oy + 7 * row_h - gap
    label_y = grid_top + 14

    cells = []
    for c, week in enumerate(weeks):
        for r, day in enumerate(week["contributionDays"]):
            count = day["contributionCount"]
            x = ox + c * (cell + gap)
            y = oy + r * row_h
            if r >= 7:
                continue
            lv = min(4, max(0, (0 if count == 0 else 1 + min(3, count // 4))))
            fill = LEVEL_FILL[lv if count else 0]
            delay = (c * 7 + r) % 40 * 0.07
            cells.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="3.2" fill="{fill}"'
                f' filter="url(#cellGlow)"><animate attributeName="opacity" values="0.82;1;0.88" dur="3.5s"'
                f' begin="{delay:.2f}s" repeatCount="indefinite"/></rect>'
            )

    month_xs = [ox + i * (grid_w / (len(MONTHS) - 1)) for i in range(len(MONTHS))]
    month_labels = "".join(
        f'<text x="{x:.1f}" y="{label_y}" text-anchor="middle" fill="#8aaa9a" font-family="system-ui,sans-serif" font-size="7.5" letter-spacing="0.04em">{m}</text>'
        for m, x in zip(MONTHS, month_xs)
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" overflow="hidden" role="img" aria-labelledby="ct cd">
  <title id="ct">Contribution forest</title>
  <desc id="cd">{calendar["totalContributions"]} contributions in the last year.</desc>
  <defs>
    <clipPath id="gridZone"><rect x="0" y="{grid_top}" width="{w}" height="{grid_bottom - grid_top + 8}"/></clipPath>
    <linearGradient id="gridShimmer" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#a0ffc0" stop-opacity="0"/>
      <stop offset="48%" stop-color="#d0ffe8" stop-opacity="0.08"/>
      <stop offset="52%" stop-color="#d0ffe8" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="#a0ffc0" stop-opacity="0"/>
    </linearGradient>
    <filter id="cellGlow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="0.8" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      @keyframes softSweep {{ 0% {{ transform: translateX(-540px); opacity: 0; }} 30% {{ opacity: 1; }} 70% {{ opacity: 1; }} 100% {{ transform: translateX(540px); opacity: 0; }} }}
      .soft-sweep {{ animation: softSweep 11s ease-in-out infinite; }}
      @media (prefers-reduced-motion: reduce) {{ .soft-sweep, rect animate {{ display: none; }} }}
    </style>
  </defs>
  <image href="{bg}" x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>
  <rect x="0" y="{grid_top - 4}" width="{w}" height="{grid_bottom - grid_top + 28}" fill="#0a1210" opacity="0.94"/>
  {month_labels}
  <g clip-path="url(#gridZone)">{''.join(cells)}</g>
  <rect class="soft-sweep" clip-path="url(#gridZone)" x="-180" y="{oy}" width="360" height="{grid_bottom - oy}" fill="url(#gridShimmer)" opacity="0.5"/>
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