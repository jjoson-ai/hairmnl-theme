import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright config for HairMNL P8 cutover smoke tests.
 *
 * Default target: P8 dev theme on creations-gdc.myshopify.com.
 * Override post-cutover via env: BASE_URL=https://www.hairmnl.com PREVIEW_THEME_ID=
 *
 * Auth setup (one-time per operator):
 *   1. Run `npx playwright codegen $BASE_URL` interactively
 *   2. Log in to Shopify admin in the opened browser
 *   3. Click "Save storage state" → save to .auth/storageState.json
 *   4. Subsequent `npm test` runs reuse the saved cookies
 *
 * Without auth, dev preview URLs strip preview_theme_id on canonical-domain
 * redirect and serve LIVE content. Tests will fail with a clear error
 * pointing at the auth setup.
 */

const BASE_URL =
  process.env.BASE_URL || 'https://creations-gdc.myshopify.com';
const PREVIEW_THEME_ID = process.env.PREVIEW_THEME_ID || '141168312419';
const HEADLESS = process.env.HEADLESS !== 'false';

export default defineConfig({
  testDir: './tests',
  outputDir: './test-results',
  timeout: 60_000,
  expect: { timeout: 10_000 },

  // Per-cell flakiness: PSI-equivalent fresh-load can vary; allow 1 retry
  // in CI but not locally (so devs see the failure).
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : undefined,

  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: './playwright-report' }],
    ['json', { outputFile: './test-results/results.json' }],
  ],

  use: {
    baseURL: BASE_URL,
    headless: HEADLESS,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    // Storage state with Shopify admin auth cookies (run `npm run auth` once)
    storageState: process.env.SHOPIFY_AUTH || undefined,
    // Slow 4G-ish throttling for CLS sensitivity. Playwright doesn't have
    // native PSI-quality throttling; we use CDP via context init for the
    // tests that need it (smokes 1, 2). Most smokes don't.
    extraHTTPHeaders: {
      // Pass-through marker so server-side requests are identifiable
      'X-Test-Run': 'hairmnl-smoke',
    },
  },

  projects: [
    {
      name: 'desktop',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 800 },
      },
    },
    {
      name: 'mobile',
      use: {
        ...devices['iPhone 13'],
        // iPhone 13 device profile: 390x844 viewport, mobile UA, touch
      },
    },
  ],

  // Make these values available to test files via process.env
  globalSetup: undefined,
});

export { BASE_URL, PREVIEW_THEME_ID };
