#!/usr/bin/env node
/**
 * capture-auth.mjs — bypass Shopify accounts.shopify.com bot detection.
 *
 * Shopify's login page checks `navigator.webdriver` and silently refuses
 * the form submit if it's true (which it is for any Playwright-controlled
 * browser, including codegen and `playwright open`). This script launches
 * a Playwright-controlled Chromium with that flag patched out (and a few
 * other automation tells masked), then opens the Shopify admin login.
 *
 * The operator logs in normally; when they close the browser window the
 * cookies are saved to .auth/storageState.json.
 *
 * Usage:
 *   cd scripts/smoke-tests
 *   node bin/capture-auth.mjs
 *   # browser opens; log in; close browser when done
 *   # → .auth/storageState.json written
 *
 * Then:
 *   SHOPIFY_AUTH=.auth/storageState.json npm test
 */

import { chromium } from '@playwright/test';
import { mkdir } from 'fs/promises';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SMOKE_DIR = resolve(__dirname, '..');
const AUTH_PATH = resolve(SMOKE_DIR, '.auth/storageState.json');

const STORE = process.env.STORE || 'creations-gdc.myshopify.com';
const THEME_ID = process.env.THEME_ID || '141168312419';
const ADMIN_URL = `https://${STORE}/admin`;
const PREVIEW_URL = `https://${STORE}/?preview_theme_id=${THEME_ID}`;

await mkdir(dirname(AUTH_PATH), { recursive: true });

console.log('→ Launching stealth-patched Chromium …');
console.log(`  store:   ${STORE}`);
console.log(`  preview: ${PREVIEW_URL}`);
console.log(`  output:  ${AUTH_PATH}`);
console.log('');

const browser = await chromium.launch({
  headless: false,
  args: [
    '--disable-blink-features=AutomationControlled',
    '--disable-features=IsolateOrigins,site-per-process',
  ],
});

const context = await browser.newContext({
  viewport: { width: 1280, height: 800 },
  userAgent:
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
});

// Mask automation tells before any page script runs
await context.addInitScript(() => {
  // Hide webdriver flag — the primary check Shopify uses
  Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
    configurable: true,
  });
  // Plugins fingerprint (Chrome reports at least 3; Playwright reports 0)
  Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5],
    configurable: true,
  });
  // Languages
  Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en'],
    configurable: true,
  });
  // permissions.query patch for notification quirk
  const origQuery = window.navigator.permissions && window.navigator.permissions.query;
  if (origQuery) {
    window.navigator.permissions.query = (params) =>
      params.name === 'notifications'
        ? Promise.resolve({ state: Notification.permission })
        : origQuery.call(window.navigator.permissions, params);
  }
});

const page = await context.newPage();

console.log('→ Browser opening Shopify admin login.');
console.log('');
console.log('  STEPS:');
console.log('    1. Log in with your Shopify account');
console.log(`    2. Once admin loads, visit ${PREVIEW_URL}`);
console.log('       (confirm you see the P8 dev theme, not a redirect)');
console.log('    3. Close the browser window');
console.log('');
console.log('  Cookies will save automatically on close.');
console.log('');

await page.goto(ADMIN_URL);

// Wait for browser close
await new Promise((resolve) => {
  browser.on('disconnected', () => resolve());
});

// Some race-condition protection: in case disconnected fires before
// context state is fully available, we tried saving inside `page.close`
// hook too. But chromium typically holds state in-process until exit.
try {
  await context.storageState({ path: AUTH_PATH });
  console.log(`✓ Cookies saved to ${AUTH_PATH}`);
  console.log('');
  console.log('Next step:');
  console.log(`  SHOPIFY_AUTH=${AUTH_PATH} npm test`);
} catch (err) {
  console.error('✗ Failed to save storageState:', err);
  console.error('  This usually means the browser closed before we could read state.');
  console.error('  Retry: re-run this script and close the browser via the X button (not Cmd+Q).');
  process.exit(1);
}
