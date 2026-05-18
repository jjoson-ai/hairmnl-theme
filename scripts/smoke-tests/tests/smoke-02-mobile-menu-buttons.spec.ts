/**
 * Smoke 2 — Mobile menu-buttons CLS
 *
 * Validates 2i8b.18's mobile-breakpoint fix: the brand-collection menu
 * buttons should not shift vertically as the deferred CSS applies
 * font-weight + text-transform. Pre-fix CLS contribution was 0.872
 * (out of 0.291 page total). Post-fix should be ≤ 0.05.
 *
 * Mobile-only test (relies on iPhone 13 device profile from playwright.config).
 */

import { test, expect } from '@playwright/test';
import { visitDev, waitForSettled } from '../helpers/dev-preview';
import { observeCLS, waitForLayoutStable } from '../helpers/cls';

test.describe('Smoke 2: Mobile brand menu-buttons CLS', () => {
  for (const handle of ['davines', 'kerastase']) {
    test(`brand /collections/${handle} mobile CLS ≤ 0.10`, async ({ page }, testInfo) => {
      test.skip(
        testInfo.project.name !== 'mobile',
        'Mobile-only test (uses iPhone 13 device profile)'
      );
      const getCLS = await observeCLS(page);
      await visitDev(page, `/collections/${handle}`);
      await waitForSettled(page);
      await waitForLayoutStable(page);

      const cls = await getCLS();

      // Find any shift attributed to .menu-buttons or .mb-menu-item-link
      const menuShifts = cls.allShifts.filter((s) =>
        s.sources.some((src) =>
          (src.nodeClass || '').toString().toLowerCase().includes('menu-buttons') ||
          (src.nodeClass || '').toString().toLowerCase().includes('mb-menu-item')
        )
      );
      const menuShiftTotal = menuShifts.reduce((sum, s) => sum + s.value, 0);

      if (cls.totalCLS > 0.1 || menuShiftTotal > 0.05) {
        console.log(`[smoke-2] CLS on /collections/${handle}: ${cls.totalCLS.toFixed(4)}`);
        console.log(`  menu-buttons attributed shifts total: ${menuShiftTotal.toFixed(4)}`);
        cls.allShifts
          .sort((a, b) => b.value - a.value)
          .slice(0, 3)
          .forEach((s, i) =>
            console.log(
              `  shift ${i + 1}: value=${s.value.toFixed(4)} sources=${JSON.stringify(s.sources[0] ?? {})}`
            )
          );
      }

      expect(
        cls.totalCLS,
        `Mobile brand-page CLS exceeds 0.10 threshold`
      ).toBeLessThanOrEqual(0.1);
      expect(
        menuShiftTotal,
        `Menu-buttons CLS contribution exceeds 0.05`
      ).toBeLessThanOrEqual(0.05);
    });
  }
});
