#!/usr/bin/env node
/**
 * Regenerates assets/contributions-forest.svg from GitHub GraphQL contributionCalendar.
 * Uses GITHUB_TOKEN or GH_TOKEN when set (Actions), else unauthenticated (may fail for private).
 */

import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const LOGIN = process.env.GITHUB_USER || "shauryacuriosity";
const OUT = join(__dirname, "..", "assets", "contributions-forest.svg");

const QUERY = `
  query($login: String!) {
    user(login: $login) {
      contributionsCollection {
        contributionCalendar {
          totalContributions
          weeks {
            contributionDays {
              contributionCount
              date
            }
          }
        }
      }
    }
  }
`;

const token =
  process.env.GITHUB_TOKEN || process.env.GH_TOKEN || process.env.GH_ENTERPRISE_TOKEN;

async function fetchCalendar() {
  const res = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `bearer ${token}` } : {}),
    },
    body: JSON.stringify({ query: QUERY, variables: { login: LOGIN } }),
  });
  const json = await res.json();
  if (json.errors?.length) {
    throw new Error(json.errors.map((e) => e.message).join("; "));
  }
  return json.data.user.contributionsCollection.contributionCalendar;
}

function level(count) {
  if (count === 0) return 0;
  if (count <= 2) return 1;
  if (count <= 6) return 2;
  if (count <= 10) return 3;
  return 4;
}

const LEVEL_FILL = [
  "#0d1a14",
  "#134d2a",
  "#1a7a3f",
  "#2dcc5c",
  "#5cff8a",
];

function treePath(cx, baseY, h) {
  const w = Math.min(14, 6 + h * 2);
  return `
    M ${cx} ${baseY}
    L ${cx - w * 0.45} ${baseY - h * 0.35}
    L ${cx - w * 0.2} ${baseY - h * 0.55}
    L ${cx - w * 0.55} ${baseY - h * 0.75}
    L ${cx} ${baseY - h}
    L ${cx + w * 0.55} ${baseY - h * 0.75}
    L ${cx + w * 0.2} ${baseY - h * 0.55}
    L ${cx + w * 0.45} ${baseY - h * 0.35}
    Z`;
}

function buildSvg(calendar) {
  const W = 720;
  const H = 220;
  const weeks = calendar.weeks;
  const cols = weeks.length;
  const cell = 9;
  const gap = 3;
  const gridW = cols * (cell + gap) - gap;
  const ox = (W - gridW) / 2;
  const oy = 108;
  const dayLabels = ["M", "T", "W", "T", "F", "S", "S"];

  let cells = "";
  let trees = "";
  let sparks = "";

  for (let c = 0; c < cols; c++) {
    const week = weeks[c].contributionDays;
    for (let r = 0; r < week.length; r++) {
      const count = week[r].contributionCount;
      const x = ox + c * (cell + gap);
      const y = oy + r * (cell + gap);
      const lv = level(count);
      const fill = LEVEL_FILL[lv];
      const delay = ((c * 7 + r) % 37) * 0.08;

      cells += `
  <rect class="cell glow-cell" x="${x}" y="${y}" width="${cell}" height="${cell}" rx="2.5" fill="${fill}">
    <animate attributeName="opacity" values="0.75;1;0.85;1" dur="4s" begin="${delay}s" repeatCount="indefinite"/>
  </rect>`;

      if (count > 0) {
        const th = 8 + Math.min(count, 20) * 1.2;
        const tcx = x + cell / 2;
        const tby = y - 2;
        trees += `<path class="tree" fill="#1e6b3a" opacity="0.92" d="${treePath(tcx, tby, th).trim()}"/>`;
        if (count >= 5) {
          sparks += `
  <circle cx="${tcx}" cy="${tby - th - 4}" r="1.2" fill="#7dff9e" opacity="0.9">
    <animate attributeName="cy" values="${tby - th - 2};${tby - th - 10};${tby - th - 2}" dur="3s" begin="${delay}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.2;1;0.2" dur="3s" begin="${delay}s" repeatCount="indefinite"/>
  </circle>`;
        }
      }
    }
  }

  const dayLabelEls = dayLabels
    .map(
      (l, i) =>
        `<text x="${ox - 14}" y="${oy + i * (cell + gap) + cell * 0.75}" fill="#4a7a5c" font-family="system-ui,sans-serif" font-size="7" text-anchor="end">${l}</text>`
    )
    .join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-labelledby="contribTitle contribDesc">
  <title id="contribTitle">Contribution forest</title>
  <desc id="contribDesc">${calendar.totalContributions} contributions in the last year, visualised as a glowing forest grid.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0a1218"/>
      <stop offset="100%" stop-color="#050a0e"/>
    </linearGradient>
    <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      @media (prefers-reduced-motion: reduce) {
        .motion, .glow-cell animate, .tree animate, .spark animate { display: none; }
        .cell { opacity: 1 !important; }
      }
    </style>
  </defs>
  <rect width="100%" height="100%" fill="url(#bg)"/>
  <text x="${W / 2}" y="28" text-anchor="middle" fill="#8cb99a" font-family="system-ui,-apple-system,sans-serif" font-size="11" letter-spacing="0.35em">CONTRIBUTIONS // FOREST</text>
  <text x="${W / 2}" y="48" text-anchor="middle" fill="#5a8a6a" font-family="system-ui,sans-serif" font-size="9">${calendar.totalContributions.toLocaleString("en-AU")} contributions · last 12 months</text>
  ${dayLabelEls}
  <g filter="url(#softGlow)">${cells}</g>
  <g class="motion">${trees}${sparks}</g>
  <rect x="0" y="${H - 24}" width="${W}" height="24" fill="#050a0e"/>
</svg>`;
}

async function main() {
  let calendar;
  try {
    calendar = await fetchCalendar();
  } catch (e) {
    console.warn("Using stylised fallback grid:", e.message);
    calendar = {
      totalContributions: 0,
      weeks: Array.from({ length: 53 }, () => ({
        contributionDays: Array.from({ length: 7 }, (_, r) => ({
          contributionCount: r === 1 || r === 3 ? 3 : r === 5 ? 8 : 0,
        })),
      })),
    };
  }
  writeFileSync(OUT, buildSvg(calendar), "utf8");
  console.log("Wrote", OUT);
}

main();