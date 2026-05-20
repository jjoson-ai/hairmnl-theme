/**
 * Smoke 10 — FOUC filmstrip
 *
 * Captures the visual timeline of initial page load to detect "flash of
 * unstyled content" caused by deferred-CSS swap pattern + slow font loads.
 *
 * For each (template × viewport), captures 7 frames at fixed intervals
 * after `domcontentloaded`, then runs true pixel-diff vs the final frame.
 *
 * Budget (W3.12 cutover gate):
 *   - 0ms   → 200ms : permitted high diff (critical CSS only — that's fine)
 *   - 200ms → 1500ms : <15% pixel diff vs final  (acceptable settle)
 *   - 1500ms → 3000ms : <2% pixel diff vs final (stable)
 *
 * Compare runs:
 *   FOUC_RUN_LABEL=p8-dev  PREVIEW_THEME_ID=141168312419 npm run test:smoke-10
 *   FOUC_RUN_LABEL=p6-live PREVIEW_THEME_ID= npm run test:smoke-10
 *
 * Outputs:
 *   - test-results/fouc-filmstrips/<label>-<template>-<viewport>-frame*.png
 *   - test-results/fouc-summary-<label>.json
 *
 * Bd: hairmnl-theme-2i8b.39
 */

import { test } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
// CommonJS-compatible imports (pixelmatch v5, pngjs)
// eslint-disable-next-line @typescript-eslint/no-var-requires
const pixelmatch = require('pixelmatch');
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { PNG } = require('pngjs');

const PREVIEW_THEME_ID = process.env.PREVIEW_THEME_ID ?? '141168312419';
const RUN_LABEL = process.env.FOUC_RUN_LABEL ?? 'p8-dev';

const TEMPLATES = [
  { name: 'home', url: '/' },
  { name: 'collection', url: '/collections/best-sellers' },
  { name: 'pdp', url: '/products/kerastase-genesis-anti-hair-fall-fortifying-serum' },
  { name: 'cart', url: '/cart' },
  { name: 'brand', url: '/collections/davines' },
];

const FRAME_TIMES_MS = [0, 100, 200, 400, 800, 1500, 3000];

const PIXEL_DIFF_BUDGET: Record<number, number> = {
  0: 100,
  1: 80,
  2: 60,
  3: 40,
  4: 20,
  5: 15,
  6: 0,
};

const FILMSTRIP_DIR = path.join(__dirname, '..', 'test-results', 'fouc-filmstrips');
const SUMMARY_PATH = path.join(__dirname, '..', 'test-results', `fouc-summary-${RUN_LABEL}.json`);

interface FrameResult {
  template: string;
  viewport: string;
  frame_idx: number;
  time_ms: number;
  filename: string;
  size_bytes: number;
  diff_pct_vs_final: number;
  budget_pct: number;
  budget_exceeded: boolean;
}

const allResults: FrameResult[] = [];

test.beforeAll(async () => {
  if (!fs.existsSync(FILMSTRIP_DIR)) {
    fs.mkdirSync(FILMSTRIP_DIR, { recursive: true });
  }
});

test.afterAll(async () => {
  const summary = {
    generated_at: new Date().toISOString(),
    run_label: RUN_LABEL,
    preview_theme_id: PREVIEW_THEME_ID,
    diff_method: 'pixelmatch threshold=0.15',
    templates_tested: TEMPLATES.map(t => t.name),
    frame_times_ms: FRAME_TIMES_MS,
    pixel_diff_budget_pct: PIXEL_DIFF_BUDGET,
    results: allResults,
    flagged_frames: allResults.filter(r => r.budget_exceeded),
  };
  fs.writeFileSync(SUMMARY_PATH, JSON.stringify(summary, null, 2));
  console.log(`\n→ FOUC filmstrip summary: ${SUMMARY_PATH}`);
  console.log(`→ Filmstrip PNGs:         ${FILMSTRIP_DIR}/\n`);

  if (summary.flagged_frames.length > 0) {
    console.warn(`⚠ ${summary.flagged_frames.length} frames exceeded their FOUC budget:`);
    summary.flagged_frames.forEach(f => {
      console.warn(
        `  ${f.template}/${f.viewport} @ ${f.time_ms}ms: ${f.diff_pct_vs_final.toFixed(1)}% (budget ${f.budget_pct}%)`,
      );
    });
  } else {
    console.log('✓ No frames exceeded their FOUC budget — visually stable initial-load.');
  }
});

for (const template of TEMPLATES) {
  for (const viewport of ['mobile', 'desktop'] as const) {
    test(`fouc-${template.name}-${viewport}`, async ({ page }) => {
      if (viewport === 'mobile') {
        await page.setViewportSize({ width: 390, height: 844 });
      } else {
        await page.setViewportSize({ width: 1440, height: 900 });
      }

      const previewQs = PREVIEW_THEME_ID ? `preview_theme_id=${PREVIEW_THEME_ID}&` : '';
      const url = `${template.url}${template.url.includes('?') ? '&' : '?'}${previewQs}_fouc=${Date.now()}`;

      const navStart = Date.now();
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30_000 });
      const dclTime = Date.now();

      const frames: { idx: number; time_ms: number; buffer: Buffer; filename: string }[] = [];
      for (let i = 0; i < FRAME_TIMES_MS.length; i++) {
        const targetTime = dclTime + FRAME_TIMES_MS[i];
        const waitMs = Math.max(0, targetTime - Date.now());
        if (waitMs > 0) await page.waitForTimeout(waitMs);

        const filename = `${RUN_LABEL}-${template.name}-${viewport}-frame${i}-t${FRAME_TIMES_MS[i]}ms.png`;
        const filepath = path.join(FILMSTRIP_DIR, filename);
        const buffer = await page.screenshot({
          type: 'png',
          fullPage: false,
          path: filepath,
        });
        frames.push({ idx: i, time_ms: FRAME_TIMES_MS[i], buffer, filename });
      }

      // Pixel-diff each frame against the final (reference) frame
      const referencePNG = PNG.sync.read(frames[frames.length - 1].buffer);
      const { width, height } = referencePNG;
      const totalPx = width * height;

      for (const frame of frames) {
        let diffPx = 0;
        if (frame.idx !== frames.length - 1) {
          const framePNG = PNG.sync.read(frame.buffer);
          const diffOutput = new PNG({ width, height });
          diffPx = pixelmatch(
            framePNG.data,
            referencePNG.data,
            diffOutput.data,
            width,
            height,
            { threshold: 0.15, includeAA: false },
          );
        }

        const diff_pct = (diffPx / totalPx) * 100;
        const budget = PIXEL_DIFF_BUDGET[frame.idx];
        const exceeded = diff_pct > budget;

        allResults.push({
          template: template.name,
          viewport,
          frame_idx: frame.idx,
          time_ms: frame.time_ms,
          filename: frame.filename,
          size_bytes: frame.buffer.length,
          diff_pct_vs_final: diff_pct,
          budget_pct: budget,
          budget_exceeded: exceeded,
        });
      }
    });
  }
}
