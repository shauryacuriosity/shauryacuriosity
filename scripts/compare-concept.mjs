#!/usr/bin/env node
import { chromium } from "playwright";
import { readFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const out = "/opt/cursor/artifacts";
mkdirSync(out, { recursive: true });
const root = join(import.meta.dirname, "..");
const concept = readFileSync(
  "/home/ubuntu/.cursor/projects/workspace/uploads/concept_v7b_adc2.png"
).toString("base64");
const sections = [
  "hero.svg",
  "contributions-forest.svg",
  "cities.svg",
  "planets.svg",
  "orbital-garden.svg",
];

const stack = sections
  .map((s) => {
    const b64 = readFileSync(join(root, "assets", s)).toString("base64");
    return `<img src="data:image/svg+xml;base64,${b64}" width="720" style="display:block"/>`;
  })
  .join("");

const html = `<!DOCTYPE html><html><body style="margin:0;background:#111;display:flex;gap:0">
<div style="width:720px">${stack}</div>
<div style="width:720px"><img src="data:image/png;base64,${concept}" width="720"/></div>
</body></html>`;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1480, height: 1400 } });
await page.setContent(html);
await page.screenshot({ path: join(out, "concept-side-by-side.png"), fullPage: true });

for (const s of ["hero.svg", "cities.svg"]) {
  const b64 = readFileSync(join(root, "assets", s)).toString("base64");
  const p = await browser.newPage({ viewport: { width: 720, height: 400 } });
  await p.setContent(
    `<img src="data:image/svg+xml;base64,${b64}" width="720"/>`,
    { waitUntil: "load" }
  );
  for (const [i, ms] of [0, 2000, 4000, 6000, 8000].entries()) {
    await p.waitForTimeout(i === 0 ? ms : 2000);
    await p.screenshot({
      path: join(out, `${s.replace(".svg", "")}-frame-${ms}.png`),
    });
  }
  await p.close();
}

await browser.close();
console.log("Comparison saved");