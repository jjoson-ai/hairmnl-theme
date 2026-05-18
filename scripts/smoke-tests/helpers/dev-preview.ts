/**
 * Dev-preview URL helpers.
 *
 * The Shopify preview-theme query param strips on the canonical-domain
 * redirect (e.g., `creations-gdc.myshopify.com/?preview_theme_id=X` →
 * `https://www.hairmnl.com/?preview_theme_id=X` → `https://www.hairmnl.com/`
 * without the preview_theme_id; serves LIVE content).
 *
 * Two ways to work around this:
 *   1. Authenticated Shopify admin session (storageState set in playwright.config.ts).
 *      The session cookie tells Shopify to honor preview_theme_id without redirecting.
 *   2. Hit the myshopify.com domain directly with the right cookie path.
 *
 * This helper builds URLs that maximize the chance of landing on the right
 * theme. If the test ends up on a different theme, the tests' own assertions
 * catch it (e.g., "expected hairmnl-common.js but page is bare").
 */

import { Page, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'https://creations-gdc.myshopify.com';
const PREVIEW_THEME_ID = process.env.PREVIEW_THEME_ID || '141168312419';
// Three modes:
//   1. dev-server mode: BASE_URL points at http://127.0.0.1:NNNN (the
//      `shopify theme dev` local proxy). No preview_theme_id needed.
//      This is the recommended pre-cutover testing mode.
//   2. post-cutover mode: BASE_URL points at the canonical domain
//      (www.hairmnl.com), no theme to preview — testing live.
//   3. preview-cookie mode: BASE_URL points at the myshopify.com domain
//      with a SHOPIFY_AUTH storageState containing admin cookies.
//      Most fragile; use only if dev-server mode unavailable.
const IS_DEV_SERVER = /^https?:\/\/(127\.0\.0\.1|localhost)/.test(BASE_URL);
const IS_POST_CUTOVER =
  !IS_DEV_SERVER &&
  BASE_URL.includes('hairmnl.com') &&
  !BASE_URL.includes('myshopify.com');

/**
 * Build a dev-preview URL for a given path.
 *   - dev-server mode: localhost proxy serves the theme directly
 *   - post-cutover mode: canonical domain, no preview param
 *   - preview-cookie mode: myshopify.com with ?preview_theme_id=N
 */
export function devUrl(path: string): string {
  if (IS_DEV_SERVER || IS_POST_CUTOVER) return `${BASE_URL}${path}`;
  const sep = path.includes('?') ? '&' : '?';
  return `${BASE_URL}${path}${sep}preview_theme_id=${PREVIEW_THEME_ID}`;
}

/**
 * Visit a path on the dev theme. Verifies the page actually loaded
 * (not redirected to a 404 or unrelated page).
 */
export async function visitDev(page: Page, path: string): Promise<void> {
  const url = devUrl(path);
  await page.goto(url, { waitUntil: 'load' });
  const finalUrl = page.url();
  // Soft sanity: if we landed on a different domain, warn loudly so it
  // shows up in the test report rather than failing in a confusing way later.
  if (
    !IS_DEV_SERVER &&
    !IS_POST_CUTOVER &&
    !finalUrl.includes('myshopify.com') &&
    !finalUrl.includes('hairmnl.com')
  ) {
    throw new Error(
      `Unexpected redirect: tried ${url} but landed on ${finalUrl}. ` +
        `Check Shopify admin auth (run 'npm run auth' once and set SHOPIFY_AUTH), ` +
        `or run via 'npm run smoke:dev' which uses the local proxy.`
    );
  }
  // Check we're not on a 404 page. The Shopify default body id is
  // "404-not-found" — IDs starting with a digit aren't valid CSS
  // identifiers (WebKit rejects), so use the attribute-selector form.
  const has404 = await page
    .locator('body[id="404-not-found"], body.template-404')
    .count();
  if (has404 > 0) {
    throw new Error(
      `Landed on a 404 page for ${url}. The collection/product handle may have changed.`
    );
  }
}

/**
 * Wait for the page to be visually settled (LCP-ish). Useful before
 * asserting on CLS or final DOM state.
 */
export async function waitForSettled(page: Page, ms = 3000): Promise<void> {
  await page.waitForLoadState('networkidle', { timeout: ms }).catch(() => {
    // networkidle can be flaky on third-party-heavy pages; we don't fail
    // if it doesn't reach idle — we just stop waiting.
  });
}

export const config = {
  BASE_URL,
  PREVIEW_THEME_ID,
  IS_DEV_SERVER,
  IS_POST_CUTOVER,
};
