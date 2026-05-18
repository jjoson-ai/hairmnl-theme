/**
 * Cumulative Layout Shift measurement helper.
 *
 * Uses the Layout Instability API (PerformanceObserver type='layout-shift')
 * which is the same data source web-vitals.js uses. Captures shift
 * entries with their per-shift `value` and attribution. Returns a
 * sum-style CLS once the page has been settled.
 *
 * For per-element attribution (the menu-buttons CLS test), we also
 * record the largest individual shift's sources.
 */

import { Page } from '@playwright/test';

export type LayoutShiftEntry = {
  value: number;
  hadRecentInput: boolean;
  startTime: number;
  sources: Array<{
    nodeName: string;
    nodeId: string | null;
    nodeClass: string | null;
    rect: { x: number; y: number; width: number; height: number } | null;
  }>;
};

export type CLSReport = {
  totalCLS: number;
  numShifts: number;
  largestShift: LayoutShiftEntry | null;
  allShifts: LayoutShiftEntry[];
};

/**
 * Inject a layout-shift observer BEFORE navigation. Returns a function
 * that retrieves the current CLS report.
 *
 * Usage:
 *   const getCLS = await observeCLS(page);
 *   await visitDev(page, '/');
 *   await waitForSettled(page);
 *   const cls = await getCLS();
 *   expect(cls.totalCLS).toBeLessThan(0.1);
 */
export async function observeCLS(page: Page): Promise<() => Promise<CLSReport>> {
  await page.addInitScript(() => {
    (window as any).__layoutShifts = [];
    new PerformanceObserver((list) => {
      for (const entry of list.getEntries() as any[]) {
        // ignore shifts from user input
        if (entry.hadRecentInput) continue;
        const sources = (entry.sources || []).map((s: any) => {
          const node = s.node as HTMLElement | null;
          return {
            nodeName: node?.tagName || '(unknown)',
            nodeId: node?.id || null,
            nodeClass: node?.className || null,
            rect: s.currentRect
              ? {
                  x: s.currentRect.x,
                  y: s.currentRect.y,
                  width: s.currentRect.width,
                  height: s.currentRect.height,
                }
              : null,
          };
        });
        (window as any).__layoutShifts.push({
          value: entry.value,
          hadRecentInput: entry.hadRecentInput,
          startTime: entry.startTime,
          sources,
        });
      }
    }).observe({ type: 'layout-shift', buffered: true });
  });

  return async () => {
    const allShifts: LayoutShiftEntry[] = await page.evaluate(
      () => (window as any).__layoutShifts || []
    );
    const totalCLS = allShifts.reduce((sum, s) => sum + s.value, 0);
    const largestShift = allShifts.reduce<LayoutShiftEntry | null>(
      (max, s) => (max === null || s.value > max.value ? s : max),
      null
    );
    return {
      totalCLS,
      numShifts: allShifts.length,
      largestShift,
      allShifts,
    };
  };
}

/**
 * Trigger any pending layout shifts by waiting for fonts to load + a
 * generous timeout. CLS settling on font-heavy pages can take 3-5s.
 */
export async function waitForLayoutStable(page: Page): Promise<void> {
  // Wait for document fonts to be ready (handles font-display:swap)
  await page.evaluate(() => (document as any).fonts?.ready);
  // Then wait a beat for any final reflow
  await page.waitForTimeout(1500);
}
