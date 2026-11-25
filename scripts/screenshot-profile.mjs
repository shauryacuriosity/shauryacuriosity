#!/usr/bin/env node
import { chromium } from "playwright";

const out = "/opt/cursor/artifacts/github-profile-live.png";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 900, height: 2200 } });
await page.goto("https://github.com/shauryacuriosity", { waitUntil: "networkidle", timeout: 60000 });
await page.waitForTimeout(3000);
await page.screenshot({ path: out, fullPage: true });
const broken = await page.locator('img[alt*="Shaurya"]').count();
console.log("Screenshots:", out, "hero imgs:", broken);
await browser.close();