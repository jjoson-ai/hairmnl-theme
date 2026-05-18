/**
 * Visual parity helpers.
 *
 * Uses Playwright's built-in toHaveScreenshot() snapshot matcher, which
 * manages baseline files automatically:
 *   - First run: writes baseline images to __screenshots__/
 *   - Subsequent runs: compares against baseline, fails if pixel-diff
 *     exceeds threshold
 *   - On intentional design change: `npx playwright test --update-snapshots`
 *
 * Baselines are commit-tracked in scripts/smoke-tests/__screenshots__/ so
 * the suite can run in CI without a separate baseline-management system.
 *
 * Dynamic-content masking
 * -----------------------
 * Real-world themes have inherently-dynamic regions that shouldn't fail
 * a visual-parity check:
 *   - Reamaze placeholder (position depends on admin config + viewport)
 *   - Cart count badge in header (depends on session state)
 *   - Klaviyo signup modal (timed reveal, may or may not be visible)
 *   - LoyaltyLion points display (depends on logged-in state)
 *   - Vertex/LimeSpot recommendations (personalized per session)
 *   - Date/time strings (vary per request)
 *
 * The DYNAMIC_REGIONS array below lists CSS selectors that are masked
 * (painted black) before screenshot, in both baseline + comparison.
 */

import { Page, Locator, expect } from '@playwright/test';

/**
 * CSS selectors for regions that should be masked in screenshots
 * because their content is dynamic / personalized / time-dependent.
 */
export const DYNAMIC_REGIONS = [
  '#reamaze-defer-placeholder',
  '#reamaze-widget, #reamaze-widget-content',
  '[class*="klaviyo-form"]',
  '[data-testid^="klaviyo-form"]',
  '#loyaltylion, #lion-loyalty-panel-custom-css, .lion-notification',
  '.cart-count, [data-header-cart-count]',
  '[data-vertex-recommendations], .vertex-recommendations-section',
  '[class*="limespot"], #limespotPersonalizer',
  '.recent__container, [data-recently-viewed-wrapper]',
  // Time-based marketing banners
  '[data-countdown], .timer-bar, .hextom-timer',
  // Stock/inventory text that may change between runs
  '.inventory-status, [data-inventory-quantity]',
];

/**
 * Wait for the page to be visually stable before screenshotting:
 *   1. Fonts ready (no FOUT/FOIT mid-snapshot)
 *   2. Network idle (lazy-render fetches complete)
 *   3. No active CSS animations
 *   4. All images decoded
 */
export async function waitForVisualStability(page: Page): Promise<void> {
  // Fonts
  await page.evaluate(() => (document as any).fonts?.ready);

  // Wait for any lazy-render IO to complete by scrolling through the page
  await page.evaluate(async () => {
    const distance = 800;
    const delay = 100;
    const totalHeight = document.documentElement.scrollHeight;
    for (let pos = 0; pos < totalHeight; pos += distance) {
      window.scrollTo(0, pos);
      await new Promise((r) => setTimeout(r, delay));
    }
    window.scrollTo(0, 0);
    await new Promise((r) => setTimeout(r, 500));
  });

  // Wait for network idle (lazy-render fetches)
  await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {
    // 3rd-party scripts may keep network busy; soft-fail
  });

  // Wait for all images to be decoded
  await page.evaluate(async () => {
    const imgs = Array.from(document.querySelectorAll('img'));
    await Promise.all(
      imgs.map((img) => {
        if (img.complete) return Promise.resolve();
        return new Promise((resolve) => {
          img.addEventListener('load', resolve, { once: true });
          img.addEventListener('error', resolve, { once: true });
          // Timeout fallback
          setTimeout(resolve, 2000);
        });
      })
    );
  });

  // Final settle
  await page.waitForTimeout(500);
}

/**
 * Build the mask Locator list for screenshot calls. Each selector that
 * matches an element on the page becomes a black-painted region.
 */
export function buildMasks(page: Page): Locator[] {
  return DYNAMIC_REGIONS.map((sel) => page.locator(sel));
}

/**
 * Standard screenshot options used by all visual-parity tests.
 * Captures full-page, masks dynamic regions, disables animations.
 */
export function screenshotOptions(page: Page) {
  return {
    fullPage: true,
    mask: buildMasks(page),
    animations: 'disabled' as const,
    caret: 'hide' as const,
    // Tolerance: 1% of pixels can differ. Adjust if too tight/loose.
    maxDiffPixelRatio: 0.01,
    // Per-pixel color sensitivity (0-1, default 0.2; lower = stricter)
    threshold: 0.2,
  };
}

/**
 * Take a full-page screenshot + diff against baseline (or write baseline
 * on first run). Snapshot name auto-generated from test name + project.
 */
export async function assertFullPageParity(
  page: Page,
  snapshotName: string
): Promise<void> {
  await waitForVisualStability(page);
  await expect(page).toHaveScreenshot(snapshotName, screenshotOptions(page));
}

/**
 * Region-scoped screenshot — for testing specific high-value elements
 * (header, cart drawer, brand grid) without full-page noise.
 */
export async function assertRegionParity(
  page: Page,
  selector: string,
  snapshotName: string
): Promise<void> {
  await waitForVisualStability(page);
  const region = page.locator(selector);
  await expect(region).toHaveScreenshot(snapshotName, {
    mask: buildMasks(page),
    animations: 'disabled',
    maxDiffPixelRatio: 0.01,
    threshold: 0.2,
  });
}
