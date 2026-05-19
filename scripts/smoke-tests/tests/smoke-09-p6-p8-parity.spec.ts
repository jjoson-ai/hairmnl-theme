/**
 * Smoke 9 — P6 LIVE vs P8 DEV visual parity (triage capture)
 *
 * Captures full-page screenshots of the same 5 templates × 2 viewports
 * from BOTH themes:
 *   - P6 LIVE  (theme 131664707683 — "Pipeline 6 - Fix share image")
 *   - P8 DEV   (theme 141168312419 — current dev / cutover candidate)
 *
 * Output: PNG files under scripts/smoke-tests/parity-screenshots/{p6,p8}/
 *
 * THIS SUITE NEVER FAILS ON VISUAL DIFFERENCES. It is a CAPTURE step.
 * After running, generate the HTML report:
 *   npm run parity:report
 * Then open parity-screenshots/index.html — side-by-side P6 | P8 | diff-blend.
 * Operator eyeballs each row + flags any unintended drift before cutover.
 *
 * Why triage-only (not pass/fail):
 *   - P8 is intentionally different from P6 in many places (typography,
 *     spacing, button styling, etc). A toHaveScreenshot threshold would
 *     fail on every template regardless of correctness.
 *   - The whole *point* of the cutover is to ship those differences.
 *     What the operator needs is "is anything DIFFERENT THAT SHOULDN'T BE",
 *     which is a human-judgment call.
 *
 * Workflow:
 *   1. npm run test:parity      # captures P6 + P8 PNGs
 *   2. npm run parity:report    # generates index.html
 *   3. open parity-screenshots/index.html
 *   4. Eyeball each row. If a diff is unintentional, file a bd issue
 *      against the relevant P8 section before cutover.
 *
 * Auth: same SHOPIFY_AUTH cookie works for both theme previews (admin
 * session honors any preview_theme_id query string).
 *
 * Saves ~2-3h vs. the operator-playbook Phase 5.1 manual walkthrough.
 */

import { test } from '@playwright/test';
import { mkdir, stat } from 'fs/promises';
import { resolve } from 'path';
import { waitForVisualStability, buildMasks } from '../helpers/visual-parity';

const OUT_ROOT = resolve(__dirname, '..', 'parity-screenshots');

// Theme IDs are stable; hardcoded so a sandboxed env can't accidentally
// run against a different theme via env-var injection.
const THEME_P6 = '131664707683';
const THEME_P8 = '141168312419';
const BASE = process.env.BASE_URL || 'https://creations-gdc.myshopify.com';

const TEMPLATES = [
  { path: '/', label: 'home' },
  { path: '/collections/best-sellers', label: 'collection' },
  { path: '/collections/davines', label: 'brand' },
  { path: '/products/kerastase-genesis-anti-hair-fall-fortifying-serum', label: 'pdp' },
  { path: '/cart', label: 'cart' },
];

function previewUrl(themeId: string, path: string): string {
  const sep = path.includes('?') ? '&' : '?';
  return `${BASE}${path}${sep}preview_theme_id=${themeId}`;
}

async function captureTheme(
  page: import('@playwright/test').Page,
  themeId: string,
  themeLabel: 'p6' | 'p8',
  tplPath: string,
  tplLabel: string,
  viewport: string
): Promise<{ path: string; bytes: number; liquidErrors: string[] } | { error: string }> {
  const url = previewUrl(themeId, tplPath);
  let response;
  try {
    response = await page.goto(url, { waitUntil: 'load', timeout: 30_000 });
  } catch (e) {
    return { error: `navigation failed: ${(e as Error).message}` };
  }

  // Soft sanity-check: are we still on the preview origin? If preview was
  // stripped on canonical redirect we'd be serving LIVE under both themes
  // and the diff would be meaningless.
  const finalUrl = page.url();
  if (!finalUrl.includes(BASE.replace(/^https?:\/\//, '')) && !finalUrl.includes('hairmnl')) {
    return { error: `redirected off preview origin to ${finalUrl}` };
  }

  // Liquid-error detection (bd 2i8b.28 retrospective). A single Liquid
  // include/render call to a missing snippet emits "Liquid error
  // (layout/theme line N): Could not find asset snippets/X.liquid" as
  // plain text content in the document. When that lands inside <head>
  // the browser parser closes <head> early and pushes ~all subsequent
  // CSS/JS into <body>, cascading into:
  //   - transparent megamenu (CSS misplaced)
  //   - no product photos (lazy-load JS misplaced)
  //   - giant slider images (sizing CSS misplaced)
  // The screenshot diff alone won't reliably catch this — the broken-
  // rendering page can still look "almost right" in a thumbnail. We
  // grep the raw HTML for "Liquid error" and capture all matches.
  let liquidErrors: string[] = [];
  try {
    const raw = response ? await response.text() : '';
    const matches = raw.match(/Liquid error[^<\n]{0,200}/g) || [];
    liquidErrors = matches.map((m) => m.trim()).slice(0, 10);
  } catch {
    /* response body unavailable — skip */
  }

  await waitForVisualStability(page);

  const outDir = resolve(OUT_ROOT, themeLabel);
  await mkdir(outDir, { recursive: true });
  const outPath = resolve(outDir, `${tplLabel}-${viewport}.png`);

  await page.screenshot({
    path: outPath,
    fullPage: true,
    mask: buildMasks(page),
    animations: 'disabled',
    caret: 'hide',
    timeout: 30_000,
  });

  // Best-effort size for the report's "sanity" line
  let bytes = 0;
  try {
    bytes = (await stat(outPath)).size;
  } catch {
    /* ignore */
  }

  return { path: outPath, bytes, liquidErrors };
}

test.describe('Smoke 9: P6 LIVE vs P8 DEV visual parity capture', () => {
  // Each template emits one test — failures here mean the CAPTURE failed
  // (navigation, auth, timeout), NOT a visual difference. Visual differences
  // are reported by parity-report.mjs.
  for (const tpl of TEMPLATES) {
    test(`capture ${tpl.label} on both themes`, async ({ page }, testInfo) => {
      const viewport = testInfo.project.name;

      const p6 = await captureTheme(page, THEME_P6, 'p6', tpl.path, tpl.label, viewport);
      if ('error' in p6) {
        testInfo.annotations.push({
          type: 'capture-failed',
          description: `P6 ${tpl.label}/${viewport}: ${p6.error}`,
        });
        throw new Error(`P6 capture failed: ${p6.error}`);
      }

      const p8 = await captureTheme(page, THEME_P8, 'p8', tpl.path, tpl.label, viewport);
      if ('error' in p8) {
        testInfo.annotations.push({
          type: 'capture-failed',
          description: `P8 ${tpl.label}/${viewport}: ${p8.error}`,
        });
        throw new Error(`P8 capture failed: ${p8.error}`);
      }

      testInfo.annotations.push({
        type: 'captured',
        description: `${tpl.label}/${viewport} — P6 ${Math.round(p6.bytes / 1024)}KB, P8 ${Math.round(p8.bytes / 1024)}KB`,
      });

      // Hard fail on Liquid errors in EITHER theme — these are cutover-
      // blocker bugs. P6 errors mean live theme has rot (rare); P8 errors
      // mean migration introduced a regression. Either way the operator
      // needs to know before the PNGs become "intentional" baselines.
      // See bd hairmnl-theme-2i8b.28 for the canonical example: 4 stale
      // {% include 'limespot' %} / {% render 'mbc-bundles' %} etc. were
      // emitting plain-text Liquid errors inside <head>, breaking the
      // entire page structure but rendering in screenshots as a thin
      // strip of text the parity diff barely showed.
      if (p6.liquidErrors.length > 0) {
        testInfo.annotations.push({
          type: 'liquid-error',
          description: `P6 ${tpl.label}: ${p6.liquidErrors.join(' | ')}`,
        });
      }
      if (p8.liquidErrors.length > 0) {
        testInfo.annotations.push({
          type: 'liquid-error',
          description: `P8 ${tpl.label}: ${p8.liquidErrors.join(' | ')}`,
        });
      }
      const combined = [...p6.liquidErrors, ...p8.liquidErrors];
      if (combined.length > 0) {
        throw new Error(
          `${combined.length} Liquid error(s) detected in ${tpl.label}/${viewport}:\n  - ` +
            combined.join('\n  - ')
        );
      }
    });
  }
});
