#!/usr/bin/env node
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";
import { join } from "node:path";

const out = "/opt/cursor/artifacts";
mkdirSync(out, { recursive: true });

const configs = [
  { name: "desktop-dark", width: 1280, height: 2400, colorScheme: "dark" },
  { name: "desktop-light", width: 1280, height: 2400, colorScheme: "light" },
  { name: "mobile-dark", width: 390, height: 2800, colorScheme: "dark" },
];

const browser = await chromium.launch();
for (const c of configs) {
  const ctx = await browser.newContext({
    viewport: { width: c.width, height: c.height },
    colorScheme: c.colorScheme,
  });
  const page = await ctx.newPage();
  await page.goto("https://github.com/shauryacuriosity", {
    waitUntil: "networkidle",
    timeout: 90000,
  });
  await page.waitForTimeout(2500);
  await page.screenshot({
    path: join(out, `live-${c.name}.png`),
    fullPage: true,
  });
  await ctx.close();
}
await browser.close();
console.log("Format screenshots saved to", out);