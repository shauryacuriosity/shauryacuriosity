#!/usr/bin/env node
import { chromium } from "playwright";
import { mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const out = "/opt/cursor/artifacts";
mkdirSync(out, { recursive: true });
const root = join(import.meta.dirname, "..");

const b64 = readFileSync(join(root, "assets/profile.svg")).toString("base64");
const sections = [
  { name: "hero", y: 0, h: 302 },
  { name: "contributions", y: 302, h: 216 },
  { name: "cities", y: 518, h: 286 },
];

const browser = await chromium.launch({ deviceScaleFactor: 2 });
for (const c of [
  { name: "desktop-dark", width: 1280, height: 2200, colorScheme: "dark" },
  { name: "desktop-light", width: 1280, height: 2200, colorScheme: "light" },
  { name: "mobile-dark", width: 390, height: 2400, colorScheme: "dark" },
]) {
  const ctx = await browser.newContext({
    viewport: { width: c.width, height: c.height },
    colorScheme: c.colorScheme,
    deviceScaleFactor: c.name.startsWith("mobile") ? 2 : 1,
  });
  const page = await ctx.newPage();
  await page.goto("https://github.com/shauryacuriosity", {
    waitUntil: "networkidle",
    timeout: 90000,
  });
  await page.waitForTimeout(3000);
  await page.screenshot({
    path: join(out, `live-${c.name}.png`),
    fullPage: true,
  });
  await ctx.close();
}

const page = await browser.newPage({ viewport: { width: 720, height: 1280 } });
await page.setContent(
  `<img src="data:image/svg+xml;base64,${b64}" width="720" style="display:block"/>`,
  { waitUntil: "load" }
);
await page.waitForTimeout(1500);
for (const s of sections) {
  await page.screenshot({
    path: join(out, `crop-2x-${s.name}.png`),
    clip: { x: 0, y: s.y, width: 720, height: s.h },
  });
}
await browser.close();
console.log("Saved live + 2x crops");