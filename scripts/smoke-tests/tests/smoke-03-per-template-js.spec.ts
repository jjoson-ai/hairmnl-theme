/**
 * Smoke 3 — Per-template JS loading (ujg6.14 + 2i8b.19)
 *
 * Validates that the per-template split JS files load correctly:
 *   - hairmnl-common.js: every template
 *   - hairmnl-collection.js: collection templates only
 *   - hairmnl-product.js: product templates only
 *
 * This is the test that would have CAUGHT the missing hairmnl-product.js
 * from dev-theme that tonight's manual smoke uncovered (commit 9832966
 * staged the file to git but the corresponding shopify theme push only
 * pushed layout/theme.liquid).
 *
 * Pattern: for each template type, navigate, wait for network idle,
 * then assert presence/absence of the 3 split files.
 */

import { test, expect } from '@playwright/test';
import { visitDev, waitForSettled } from '../helpers/dev-preview';
import { recordNetwork } from '../helpers/network-filter';

type Case = { path: string; label: string; expects: string[]; absent: string[] };

const CASES: Case[] = [
  {
    path: '/',
    label: 'homepage',
    expects: ['hairmnl-common.js'],
    absent: ['hairmnl-collection.js', 'hairmnl-product.js'],
  },
  {
    path: '/collections/davines',
    label: 'collection (davines)',
    expects: ['hairmnl-common.js', 'hairmnl-collection.js'],
    absent: ['hairmnl-product.js'],
  },
  {
    path: '/products/kerastase-genesis-anti-hair-fall-fortifying-serum',
    label: 'product (kerastase-genesis)',
    expects: ['hairmnl-common.js', 'hairmnl-product.js'],
    absent: ['hairmnl-collection.js'],
  },
];

test.describe('Smoke 3: per-template JS loading', () => {
  for (const c of CASES) {
    test(`${c.label} loads correct hairmnl-*.js files`, async ({ page }) => {
      const net = recordNetwork(page);
      await visitDev(page, c.path);
      await waitForSettled(page);

      for (const filename of c.expects) {
        const loaded = net.hasLoaded(filename);
        if (!loaded) {
          console.log(`[smoke-3] ${c.label}: ${filename} NOT loaded`);
          console.log(net.describe('hairmnl-'));
        }
        expect(loaded, `${c.label} must load ${filename}`).toBe(true);
      }

      for (const filename of c.absent) {
        const loaded = net.hasLoaded(filename);
        if (loaded) {
          console.log(`[smoke-3] ${c.label}: ${filename} LOADED but shouldn't`);
        }
        expect(loaded, `${c.label} must NOT load ${filename}`).toBe(false);
      }

      // Catch the "file exists in git but not pushed to dev" failure mode:
      // a 404 status on a hairmnl-*.js request.
      const failed = net.all('hairmnl-').filter(
        (r) => r.status !== null && r.status >= 400
      );
      if (failed.length > 0) {
        throw new Error(
          `[smoke-3] hairmnl-*.js file(s) returned HTTP error:\n` +
            failed.map((r) => `  ${r.status} ${r.url}`).join('\n') +
            `\n\nThis is the failure mode that caught hairmnl-product.js missing from dev tonight. ` +
            `Fix: shopify theme push --theme=$THEME_ID --only=assets/<filename>`
        );
      }
    });
  }
});
