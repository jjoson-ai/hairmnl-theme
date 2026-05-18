#!/usr/bin/env node
/**
 * attach-and-save.mjs — extract storageState from an already-logged-in Chrome.
 *
 * Shopify's accounts.shopify.com page rejects ANY Playwright-controlled
 * browser, even with webdriver-flag stealth patches. Their detection
 * stack is multi-layer: TLS fingerprint, HTTP/2 priority frames, behavioral.
 * No client-side patch fully cloaks it.
 *
 * Workaround: don't fight the detection — use the operator's existing,
 * already-logged-in regular Chrome. Launch Chrome with the remote-
 * debugging port open, then attach Playwright via CDP and dump the
 * cookies + localStorage to a storageState.json file.
 *
 * Operator workflow:
 *
 *   # 1. Quit Chrome FULLY first (otherwise the remote-debugging flag is ignored
 *   #    because there's already a Chrome process holding the user-data-dir)
 *   osascript -e 'tell application "Google Chrome" to quit'
 *   # … wait a beat …
 *
 *   # 2. Relaunch Chrome with remote debugging enabled.
 *   #    Uses your normal Chrome profile (default User Data dir) so all
 *   #    your existing logins carry over.
 *   open -na "Google Chrome" --args --remote-debugging-port=9222
 *
 *   # 3. In that Chrome, log in to Shopify admin if not already logged in,
 *   #    then visit the preview URL to confirm it works:
 *   #      https://creations-gdc.myshopify.com/?preview_theme_id=141168312419
 *   #    You should see the P8 dev theme. If you see a 404 or LIVE content,
 *   #    something is wrong; debug before continuing.
 *
 *   # 4. Run this script — it will attach to that Chrome and save cookies.
 *   cd scripts/smoke-tests
 *   node bin/attach-and-save.mjs
 *
 *   # 5. Use cookies for tests:
 *   SHOPIFY_AUTH=.auth/storageState.json npm test
 *
 * The captured storageState includes cookies for ALL domains in your Chrome
 * session, not just Shopify. The .auth/ dir is gitignored so cookies stay
 * local. Treat the storageState.json file like a password — anyone with it
 * can act as you in Shopify admin until the session expires.
 */

import { chromium } from '@playwright/test';
import { mkdir, writeFile } from 'fs/promises';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SMOKE_DIR = resolve(__dirname, '..');
const AUTH_PATH = resolve(SMOKE_DIR, '.auth/storageState.json');
const CDP_URL = process.env.CDP_URL || 'http://localhost:9222';

await mkdir(dirname(AUTH_PATH), { recursive: true });

console.log(`→ Attaching to Chrome at ${CDP_URL} …`);

let browser;
try {
  browser = await chromium.connectOverCDP(CDP_URL);
} catch (err) {
  console.error('');
  console.error('✗ Cannot connect to Chrome CDP.');
  console.error('');
  console.error('  Chrome needs to be running with the remote-debugging flag.');
  console.error('  Quit Chrome fully first (osascript -e \'tell application "Google Chrome" to quit\'),');
  console.error('  then relaunch with:');
  console.error('');
  console.error('    open -na "Google Chrome" --args --remote-debugging-port=9222');
  console.error('');
  console.error('  After Chrome opens, log into Shopify admin if needed, then re-run this script.');
  console.error('');
  console.error(`  Underlying error: ${err.message}`);
  process.exit(1);
}

// connectOverCDP returns the existing browser; contexts already exist
const contexts = browser.contexts();
if (contexts.length === 0) {
  console.error('✗ Chrome has no open contexts. Open at least one tab + log in to Shopify first.');
  await browser.close();
  process.exit(1);
}

console.log(`  ✓ connected. Found ${contexts.length} browser context(s) with ${contexts.reduce((sum, ctx) => sum + ctx.pages().length, 0)} total page(s).`);

// Use the default context (always index 0 for connected real Chrome)
const ctx = contexts[0];
const pages = ctx.pages();

// Spot-check: any of the open tabs Shopify-related?
const shopifyTabs = pages
  .map((p) => p.url())
  .filter((u) => u.includes('shopify') || u.includes('myshopify') || u.includes('hairmnl'));

if (shopifyTabs.length === 0) {
  console.warn('');
  console.warn('  ⚠ Warning: no Shopify-related tabs found in this Chrome session.');
  console.warn('    Cookies will still be saved but may be incomplete.');
  console.warn('    Open https://creations-gdc.myshopify.com/admin in this Chrome first,');
  console.warn('    then re-run this script.');
  console.warn('');
} else {
  console.log('  Shopify-related tabs found:');
  shopifyTabs.slice(0, 5).forEach((u) => console.log(`    - ${u.slice(0, 100)}`));
  console.log('');
}

// Extract storageState from the existing context
console.log(`→ Saving storageState to ${AUTH_PATH} …`);
const state = await ctx.storageState();

// Sanity check: did we get any cookies?
const shopifyCookies = state.cookies.filter(
  (c) =>
    c.domain.includes('shopify') ||
    c.domain.includes('myshopify') ||
    c.domain.includes('hairmnl')
);

await writeFile(AUTH_PATH, JSON.stringify(state, null, 2));

console.log('');
console.log(`  ✓ Wrote ${state.cookies.length} cookies (${shopifyCookies.length} for Shopify domains)`);
console.log(`  ✓ Wrote ${state.origins.length} localStorage origin(s)`);
console.log('');

if (shopifyCookies.length === 0) {
  console.warn('  ⚠ No Shopify cookies captured. The smoke suite will fail to access the dev preview.');
  console.warn('    Make sure you are logged into Shopify admin in this Chrome before running this script.');
  process.exit(2);
}

console.log('Next step:');
console.log(`  cd scripts/smoke-tests`);
console.log(`  SHOPIFY_AUTH=${AUTH_PATH} npm test`);

// Disconnect from the CDP session — do NOT close the browser
await browser.close();
process.exit(0);
