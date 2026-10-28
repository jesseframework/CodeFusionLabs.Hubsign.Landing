#!/usr/bin/env node
/**
 * Renders static/images/og-image.png (1200x630) for the Open Graph / Twitter
 * card meta tags in templates/base.html.
 *
 * Uses the site's own stylesheet (static/css/main.css) and self-hosted fonts
 * for accurate typography and colour, driven headless through the Playwright
 * Chromium install that already lives in the sibling hubsign_by_documenso
 * repo's node_modules (this repo has no Node toolchain of its own).
 *
 * Run with: node tools/generate_og_image.mjs
 */
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const require = createRequire('E:/src/repos/codefusionlabs/hubsign_by_documenso/package.json');
const { chromium } = require('playwright');

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

const mainCss = pathToFileURL(path.join(ROOT, 'static/css/main.css')).href;
const wordmark = pathToFileURL(path.join(ROOT, 'static/images/hubsign_logo.png')).href;
const shot = pathToFileURL(path.join(ROOT, 'static/images/screens/dashboard.png')).href;

const WIDTH = 1200;
const HEIGHT = 630;

const html = `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="${mainCss}">
<style>
  html, body { margin: 0; padding: 0; }
  body {
    width: ${WIDTH}px;
    height: ${HEIGHT}px;
    background: var(--paper);
    font-family: var(--font-body);
    overflow: hidden;
  }
  .card {
    position: relative;
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    padding: 56px 64px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .wordmark { position: absolute; top: 56px; left: 64px; height: 40px; width: auto; }
  .headline {
    max-width: 620px;
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 58px;
    line-height: 1.14;
    letter-spacing: -0.02em;
    color: var(--ink);
    margin: 0;
  }
  .headline .accent { display: block; color: var(--accent); font-style: italic; }
  .tagline {
    max-width: 520px;
    margin-top: 22px;
    font-size: 20px;
    line-height: 1.5;
    color: var(--ink-2);
  }
  .shot {
    position: absolute;
    top: 128px;
    right: 64px;
    width: 480px;
    height: 344px;
    border: 1px solid var(--rule-strong);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    overflow: hidden;
    background: var(--raised);
  }
  .shot img { width: 100%; height: 100%; object-fit: cover; object-position: top left; display: block; }
  .domain {
    position: absolute;
    bottom: 56px;
    left: 64px;
    font-family: var(--font-mono);
    font-size: 14px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--ink-muted);
  }
</style>
</head>
<body>
  <div class="card">
    <img class="wordmark" src="${wordmark}" alt="">
    <h1 class="headline">Everything that happens<span class="accent">around the signature.</span></h1>
    <p class="tagline">E-signatures, and the intake, control and records work around them.</p>
    <div class="shot"><img src="${shot}" alt=""></div>
    <div class="domain">hubsign.io</div>
  </div>
</body>
</html>`;

const outHtml = path.join(ROOT, 'tools', '.og-image.tmp.html');
fs.writeFileSync(outHtml, html, 'utf-8');

const outPng = path.join(ROOT, 'static/images/og-image.png');

(async () => {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT }, deviceScaleFactor: 1 });
    await page.goto(pathToFileURL(outHtml).href);
    // Fonts are self-hosted local files; make sure they're actually painted
    // before the screenshot, not just requested.
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: outPng });
  } finally {
    await browser.close();
    fs.unlinkSync(outHtml);
  }
  console.log('Wrote', outPng);
})();
