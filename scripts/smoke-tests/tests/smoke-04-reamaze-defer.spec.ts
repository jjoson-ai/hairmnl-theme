/**
 * Smoke 4 — Reamaze defer-on-interaction (bd fsaa)
 *
 * Validates that cdn.reamaze.com scripts do NOT load on first paint.
 * Then triggers the placeholder click + verifies the SDK loads after.
 *
 * Acceptance:
 *   - Zero cdn.reamaze.com requests before any user interaction
 *   - Placeholder element (#reamaze-defer-placeholder) is visible from
 *     first paint (server-rendered)
 *   - After clicking placeholder, SDK loads + dataLayer fires
 *     reamaze_load_path event
 *
 * Caveat: the chat opening + working depends on Reamaze CDN availability.
 * We assert the trigger fires + at least one CDN request starts. We
 * don't assert "the chat is interactive" — that requires Reamaze backend.
 */

import { test, expect } from '@playwright/test';
import { visitDev, waitForSettled } from '../helpers/dev-preview';
import { recordNetwork } from '../helpers/network-filter';

test.describe('Smoke 4: Reamaze chat defer-on-interaction', () => {
  test('cdn.reamaze.com does not load on first paint; placeholder visible', async ({
    page,
  }) => {
    const net = recordNetwork(page);
    await visitDev(page, '/');
    await waitForSettled(page);

    // Before any interaction, NO cdn.reamaze.com SCRIPT requests.
    // We allow DNS prefetch / CSS / font requests since those may fire
    // from <link rel="preconnect"> or the placeholder's own styling.
    // Only the SDK script load is the defer-guard concern.
    const preInteractionScripts = net
      .all('cdn.reamaze.com')
      .filter((r) => r.resourceType === 'script');
    if (preInteractionScripts.length > 0) {
      console.log('[smoke-4] PRE-INTERACTION reamaze SCRIPT requests:');
      preInteractionScripts.forEach((r) =>
        console.log(`  ${r.status} ${r.resourceType} ${r.url.slice(0, 100)}`)
      );
    }
    expect(
      preInteractionScripts.length,
      'cdn.reamaze.com SCRIPT should not load before user interaction (defer guard)'
    ).toBe(0);

    // Placeholder should be visible (server-rendered)
    const placeholder = page.locator('#reamaze-defer-placeholder');
    await expect(
      placeholder,
      'Reamaze defer placeholder must be visible from first paint'
    ).toBeVisible({ timeout: 5000 });
  });

  test('clicking placeholder triggers SDK load + dataLayer event', async ({
    page,
  }) => {
    const net = recordNetwork(page);
    await visitDev(page, '/');
    await waitForSettled(page);

    // Snapshot dataLayer state before interaction
    await page.evaluate(() => {
      (window as any).dataLayer = (window as any).dataLayer || [];
    });

    // Click the placeholder. LoyaltyLion / Klaviyo notifications can
    // overlay the placeholder and intercept pointer events. First try
    // to dismiss any LoyaltyLion notification; if that fails, force-click
    // through any intercepting overlay.
    const llClose = page.locator('.lion-notification__close, [aria-label*="close" i]').first();
    if ((await llClose.count()) > 0) {
      await llClose.click({ timeout: 2000 }).catch(() => {});
      await page.waitForTimeout(300);
    }
    await page
      .locator('#reamaze-defer-placeholder')
      .click({ timeout: 5000, force: true });

    // Wait briefly for the SDK fetch to begin
    await page.waitForTimeout(2000);

    // Verify cdn.reamaze.com request started
    const reamazeReqs = net.count('cdn.reamaze.com');
    expect(
      reamazeReqs,
      'After placeholder click, cdn.reamaze.com SDK fetch should begin'
    ).toBeGreaterThan(0);

    // Verify dataLayer received the load_path event
    const dlEvents = await page.evaluate(() =>
      ((window as any).dataLayer || []).filter((e: any) =>
        e.event === 'reamaze_load_path'
      )
    );
    expect(
      dlEvents.length,
      'dataLayer should have a reamaze_load_path event'
    ).toBeGreaterThan(0);
    expect(
      dlEvents[0].path,
      'load_path event should report placeholder_click'
    ).toBe('placeholder_click');
  });

  test('scroll past 50% triggers SDK load even without click', async ({ page }) => {
    const net = recordNetwork(page);
    await visitDev(page, '/');
    await waitForSettled(page);

    // Scroll to 60% of page (over the 50% trigger threshold)
    await page.evaluate(() => {
      const target = (document.documentElement.scrollHeight - window.innerHeight) * 0.6;
      window.scrollTo(0, target);
    });
    await page.waitForTimeout(2000);

    // SDK should have started loading
    const reamazeReqs = net.count('cdn.reamaze.com');
    expect(
      reamazeReqs,
      'After scrolling past 50%, cdn.reamaze.com SDK should load'
    ).toBeGreaterThan(0);

    const dlEvents = await page.evaluate(() =>
      ((window as any).dataLayer || []).filter((e: any) =>
        e.event === 'reamaze_load_path'
      )
    );
    expect(dlEvents.length).toBeGreaterThan(0);
    expect(dlEvents[0].path).toBe('scroll_50');
  });
});
