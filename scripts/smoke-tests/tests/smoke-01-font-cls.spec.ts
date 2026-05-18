/**
 * Smoke 1 — Font CLS verification
 *
 * Validates that text doesn't shift vertically when web fonts swap in.
 * Tests ujg6.7's Arial-matched line-box overrides on
 * BasisGrotesquePro-Regular + font-display:optional on accent weights.
 *
 * Acceptance:
 *   - Total CLS on homepage ≤ 0.10 (CWV threshold)
 *   - No individual layout-shift attributed to a heading/text element
 *     contributes more than 0.05 to total CLS
 *
 * Caveat: lab measurements vary. We assert a generous ceiling that
 * tonight's dev-theme baselines pass comfortably (mobile 0.018,
 * desktop 0.009 on home).
 */

import { test, expect } from '@playwright/test';
import { visitDev, waitForSettled } from '../helpers/dev-preview';
import { observeCLS, waitForLayoutStable } from '../helpers/cls';

test.describe('Smoke 1: Font CLS — text does not shift on web-font swap', () => {
  test('homepage CLS ≤ 0.10 with no large font-attributed shifts', async ({
    page,
  }) => {
    const getCLS = await observeCLS(page);
    await visitDev(page, '/');
    await waitForSettled(page);
    await waitForLayoutStable(page);

    const cls = await getCLS();

    // Surface useful debug info on failure
    if (cls.totalCLS > 0.1 || (cls.largestShift?.value ?? 0) > 0.05) {
      console.log(
        `[smoke-1] CLS report: total=${cls.totalCLS.toFixed(4)}, n=${cls.numShifts}`
      );
      cls.allShifts
        .sort((a, b) => b.value - a.value)
        .slice(0, 5)
        .forEach((s, i) =>
          console.log(
            `  shift ${i + 1}: value=${s.value.toFixed(4)} sources=${s.sources
              .map(
                (src) =>
                  `${src.nodeName}${src.nodeId ? '#' + src.nodeId : ''}` +
                  (src.nodeClass ? '.' + String(src.nodeClass).split(' ')[0] : '')
              )
              .join(', ')}`
          )
        );
    }

    // CWV "good" threshold is 0.10
    expect(
      cls.totalCLS,
      `Homepage CLS ${cls.totalCLS.toFixed(4)} exceeds 0.10 CWV threshold`
    ).toBeLessThanOrEqual(0.1);

    // No single shift dominates (would indicate a specific element regression)
    if (cls.largestShift) {
      expect(
        cls.largestShift.value,
        `Largest single shift ${cls.largestShift.value.toFixed(4)} ` +
          `exceeds 0.05. Source: ${JSON.stringify(cls.largestShift.sources[0] ?? {})}`
      ).toBeLessThanOrEqual(0.05);
    }
  });
});
