#!/usr/bin/env node
import { chromium } from "playwright";
import { mkdirSync, readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const outDir = "/opt/cursor/artifacts";

const sections = [
  "hero.svg",
  "contributions-forest.svg",
  "cities.svg",
  "planets.svg",
  "orbital-garden.svg",
];

async function main() {
  mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 760, height: 2000 } });

  const readmeHtml = `
<!DOCTYPE html>
<html><head>
<style>
  body { margin: 0; background: #0d1117; font-family: system-ui,sans-serif; }
  .readme { max-width: 760px; margin: 0 auto; padding: 16px; }
  img { display: block; max-width: 720px; width: 100%; }
  h2 { color: #c9d1d9; font-size: 14px; font-weight: 600; }
  hr { border-color: #21262d; }
</style>
</head><body><div class="readme">
${sections
    .map((s) => {
      const data = readFileSync(join(root, "assets", s));
      const uri = `data:image/svg+xml;base64,${data.toString("base64")}`;
      return `<img src="${uri}" width="720"/>`;
    })
    .join("\n")}
<hr/><h2>Links</h2><p><a href="#">GitHub</a></p>
</div></body></html>`;

  await page.setContent(readmeHtml, { waitUntil: "load" });
  await page.screenshot({ path: join(outDir, "profile-readme-preview.png"), fullPage: true });

  for (const s of sections) {
    const svgPage = await browser.newPage({ viewport: { width: 720, height: 500 } });
    const file = `file://${join(root, "assets", s)}`;
    await svgPage.goto(file, { waitUntil: "load" });
    const delays = [0, 2000, 4000];
    const base = s.replace(".svg", "");
    for (const ms of delays) {
      await svgPage.waitForTimeout(ms);
      await svgPage.screenshot({ path: join(outDir, `${base}-t${ms}ms.png`) });
    }
    await svgPage.close();
  }

  await browser.close();
  console.log("Screenshots written to", outDir);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});