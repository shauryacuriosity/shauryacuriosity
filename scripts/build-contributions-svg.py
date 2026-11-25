#!/usr/bin/env python3
"""Build contributions-forest.svg: tree raster band + opaque vector grid below."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from b64 import webp_data_uri

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "contributions-forest.svg"
LOGIN = os.environ.get("GITHUB_USER", "shauryacuriosity")

LEVEL_FILL = ["#142018", "#1d5c34", "#289450", "#3ed878", "#6cffaa"]
MONTHS = ["Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
WEEKDAYS = [(0, "Mon"), (2, "Wed"), (4, "Fri")]

TREE_H = 120
FLOOR_TOP = 112

LEVEL_ENUM = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}

QUARTILE_COUNTS = [0, 1, 4, 9, 16]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            contributionLevel
          }
        }
      }
    }
  }
}
"""

CONTRIBUTIONS_HTML = "https://github.com/users/{login}/contributions"


def _normalize_day(day: dict) -> dict:
    level = day.get("contributionLevel")
    if isinstance(level, str):
        day = {**day, "contributionLevel": LEVEL_ENUM.get(level, 0)}
    elif level is not None:
        day = {**day, "contributionLevel": int(level)}
    return day


def fetch_calendar() -> dict:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    body = json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode()
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "shauryacuriosity-profile-build",
    }
    if token:
        headers["Authorization"] = f"bearer {token}"
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as res:
        data = json.loads(res.read().decode())
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = []
    for week in cal["weeks"]:
        days = [_normalize_day(d) for d in week["contributionDays"]]
        weeks.append({"contributionDays": days[:7]})
    cal["weeks"] = weeks
    return cal


def fetch_calendar_from_html() -> dict:
    url = CONTRIBUTIONS_HTML.format(login=LOGIN)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "shauryacuriosity-profile-build"},
    )
    with urllib.request.urlopen(req, timeout=60) as res:
        html = res.read().decode()

    total = 0
    total_m = re.search(
        r'id="js-contribution-activity-description"[^>]*>\s*([\d,]+)',
        html,
        re.S,
    )
    if total_m:
        total = int(total_m.group(1).replace(",", ""))

    matrix: list[list[int | None]] = [[None] * 53 for _ in range(7)]
    td_re = re.compile(r"<td[^>]*ContributionCalendar-day[^>]*>", re.I)
    id_re = re.compile(r'id="contribution-day-component-(\d+)-(\d+)"')
    level_re = re.compile(r'data-level="(\d)"')
    max_week = -1
    for td in td_re.finditer(html):
        tag = td.group(0)
        id_m = id_re.search(tag)
        lv_m = level_re.search(tag)
        if not id_m or not lv_m:
            continue
        row, col, lv = int(id_m.group(1)), int(id_m.group(2)), int(lv_m.group(1))
        if col >= len(matrix[row]):
            for r in range(7):
                matrix[r].extend([None] * (col + 1 - len(matrix[r])))
        matrix[row][col] = lv
        max_week = max(max_week, col)
    if max_week < 0:
        raise RuntimeError("no contribution grid cells found in HTML")

    num_weeks = max_week + 1
    weeks = []
    for c in range(num_weeks):
        days = []
        for r in range(7):
            lv = matrix[r][c] if matrix[r][c] is not None else 0
            days.append(
                {
                    "contributionCount": QUARTILE_COUNTS[lv],
                    "contributionLevel": lv,
                }
            )
        weeks.append({"contributionDays": days})

    return {"totalContributions": total, "weeks": weeks}


def load_calendar() -> tuple[dict, str]:
    errors: list[str] = []
    try:
        return fetch_calendar(), "graphql"
    except Exception as e:
        errors.append(f"graphql: {e}")
    try:
        return fetch_calendar_from_html(), "html"
    except Exception as e:
        errors.append(f"html: {e}")
    raise RuntimeError("; ".join(errors))


def build(calendar: dict) -> str:
    trees = webp_data_uri(ROOT / "assets" / "raster" / "contributions-trees.webp")
    w, h = 720, 258
    weeks = calendar["weeks"]
    cols = len(weeks)
    cell, gap = 8, 2
    row_h = cell + gap
    grid_w = cols * (cell + gap) - gap
    gutter = 22
    ox = gutter + (w - gutter - grid_w) / 2
    grid_h = 7 * row_h - gap
    month_y = 136
    oy = 150
    solid_y = 132
    grid_bottom = oy + grid_h

    cells = []
    for c, week in enumerate(weeks):
        for r, day in enumerate(week["contributionDays"]):
            if r >= 7:
                continue
            count = day.get("contributionCount", 0)
            level = day.get("contributionLevel")
            if level is not None:
                lv = min(4, max(0, int(level)))
            else:
                lv = min(4, max(0, (0 if count == 0 else 1 + min(3, count // 4))))
            x = ox + c * (cell + gap)
            y = oy + r * row_h
            fill = LEVEL_FILL[lv]
            delay = (c * 7 + r) % 40 * 0.07
            cells.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="2.4" fill="{fill}"'
                f' filter="url(#cellGlow)"><animate attributeName="opacity" values="0.85;1;0.9" dur="3.5s"'
                f' begin="{delay:.2f}s" repeatCount="indefinite"/></rect>'
            )

    month_xs = [ox + i * (grid_w / (len(MONTHS) - 1)) for i in range(len(MONTHS))]
    month_labels = "".join(
        f'<text x="{x:.1f}" y="{month_y}" text-anchor="middle" fill="#7e9788" font-family="system-ui,sans-serif" font-size="9">{m}</text>'
        for m, x in zip(MONTHS, month_xs)
    )
    weekday_labels = "".join(
        f'<text x="{ox - 12:.1f}" y="{oy + r * row_h + cell - 2:.1f}" text-anchor="end" fill="#687e72" font-family="system-ui,sans-serif" font-size="8">{label}</text>'
        for r, label in WEEKDAYS
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" overflow="hidden" role="img" aria-labelledby="ct cd">
  <title id="ct">Contribution forest</title>
  <desc id="cd">{calendar["totalContributions"]} contributions in the last year.</desc>
  <defs>
    <linearGradient id="forestFloor" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1a2e22"/>
      <stop offset="100%" stop-color="#0a1210"/>
    </linearGradient>
    <linearGradient id="waveGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#c8ffd8" stop-opacity="0"/>
      <stop offset="45%" stop-color="#e8fff0" stop-opacity="0.09"/>
      <stop offset="55%" stop-color="#e8fff0" stop-opacity="0.09"/>
      <stop offset="100%" stop-color="#c8ffd8" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="gridZone"><rect x="0" y="{FLOOR_TOP}" width="{w}" height="{h - FLOOR_TOP}"/></clipPath>
    <filter id="cellGlow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="0.7" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="waveBlur" x="-50%" y="-30%" width="200%" height="160%">
      <feGaussianBlur stdDeviation="8"/>
    </filter>
    <style>
      @media (prefers-reduced-motion: reduce) {{ .light-wave, rect animate, animateTransform {{ display: none; }} }}
    </style>
  </defs>
  <rect x="0" y="0" width="{w}" height="{h}" fill="#0a1210"/>
  <image href="{trees}" x="0" y="0" width="{w}" height="{TREE_H}" preserveAspectRatio="xMidYMid slice"/>
  <rect x="0" y="{FLOOR_TOP}" width="{w}" height="{solid_y - FLOOR_TOP}" fill="url(#forestFloor)"/>
  <rect x="0" y="{solid_y}" width="{w}" height="{h - solid_y}" fill="#0a1210"/>
  {month_labels}
  {weekday_labels}
  <g clip-path="url(#gridZone)">
    {''.join(cells)}
    <g class="light-wave" opacity="0.65" filter="url(#waveBlur)">
      <rect x="-280" y="{oy}" width="360" height="{grid_h}" fill="url(#waveGrad)">
        <animateTransform attributeName="transform" type="translate" values="-720 0;720 0" dur="14s" repeatCount="indefinite"/>
      </rect>
    </g>
  </g>
</svg>"""


def main() -> None:
    cal, source = load_calendar()
    OUT.write_text(build(cal), encoding="utf-8")
    print(
        f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB) "
        f"source={source} total={cal['totalContributions']} weeks={len(cal['weeks'])}"
    )


if __name__ == "__main__":
    main()