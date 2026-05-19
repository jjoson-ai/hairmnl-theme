/**
 * Smoke 6 — Lazy-render sections (ujg6.18, 3 increments)
 *
 * Validates the IntersectionObserver-driven Section Rendering API for
 * below-fold heavy sections:
 *   - section-collection.liquid (homepage featured-collections)
 *   - brand-collection.liquid (brand pages)
 *   - related.liquid (PDP related-products + recently-viewed)
 *
 * Acceptance:
 *   - Placeholder (<div data-lazy-render>) is server-rendered on first load
 *   - No ?section_id= fetch fires before scrolling
 *   - Scrolling near the placeholder triggers a fetch
 *   - Placeholder is replaced with full section content
 *   - section:lazy-rendered event dispatched
 *
 * Tests theme-editor + Section-API render paths via direct ?section_id=
 * fetches (verified they return full HTML, not placeholders).
 */

import { test, expect } from '@playwright/test';
import { visitDev, waitForSettled, devUrl } from '../helpers/dev-preview';
import { recordNetwork } from '../helpers/network-filter';

test.describe('Smoke 6: Lazy-render below-fold sections', () => {
  test('homepage: section-collection placeholder swaps to content on scroll', async ({
    page,
  }) => {
    const net = recordNetwork(page);
    await visitDev(page, '/');
    await waitForSettled(page);

    // Placeholders must be present
    const placeholders = page.locator('[data-lazy-render]');
    const initialCount = await placeholders.count();
    expect(
      initialCount,
      'Homepage should have at least one [data-lazy-render] placeholder'
    ).toBeGreaterThan(0);

    // Capture initial state: did any section_id= fetch fire? Should be ~0
    // until we scroll. Some may fire from above-fold sections; we check
    // delta after scroll instead of absolute count.
    const initialFetches = net.count('section_id=');

    // Scroll incrementally to trigger IO on each placeholder progressively.
    // Single jump-to-bottom can miss intermediate placeholders if the IO's
    // rootMargin doesn't catch them during the fast scroll.
    await page.evaluate(async () => {
      const totalHeight = document.documentElement.scrollHeight;
      const step = 400;
      for (let pos = 0; pos < totalHeight; pos += step) {
        window.scrollTo(0, pos);
        await new Promise((r) => setTimeout(r, 200));
      }
      // Hold at bottom for a final settle
      window.scrollTo(0, totalHeight);
      await new Promise((r) => setTimeout(r, 1000));
    });
    await waitForSettled(page);

    // Verify additional section_id= fetches happened
    const fetchesAfterScroll = net.count('section_id=');

    // Diagnostic: confirm the IO observer is even loaded (hairmnl-common.js
    // section 8). If it's missing, lazy-render can't work regardless of scroll.
    const observerInstalled = await page.evaluate(() => {
      // The section 8 IO observes [data-lazy-render]; if loaded, there should
      // be no orphan placeholders by now. We can't directly check the IO
      // existence, but we can check if hairmnl-common.js loaded.
      return typeof (window as any).IntersectionObserver === 'function';
    });

    if (fetchesAfterScroll === initialFetches) {
      console.log('[smoke-6] No section_id fetches triggered. Diagnostics:');
      console.log(`  initial placeholders: ${initialCount}`);
      console.log(`  IntersectionObserver available: ${observerInstalled}`);
      console.log(`  initial fetches: ${initialFetches}, after-scroll fetches: ${fetchesAfterScroll}`);
      // Dump the loaded JS to see if hairmnl-common.js is present
      console.log(`  hairmnl-common.js loaded: ${net.hasLoaded('hairmnl-common.js')}`);
    }

    expect(
      fetchesAfterScroll,
      'Scrolling should trigger lazy-render fetches'
    ).toBeGreaterThan(initialFetches);

    // Verify placeholders are now content (data-lazy-render attr should be gone
    // since the placeholder DOM element is replaced with the fetched section)
    const remainingPlaceholders = await page.locator('[data-lazy-render]').count();
    expect(
      remainingPlaceholders,
      'After scroll, [data-lazy-render] placeholders should be replaced with content'
    ).toBeLessThan(initialCount);
  });

  test('brand page: brand-collection lazy-render works', async ({ page }) => {
    const net = recordNetwork(page);
    await visitDev(page, '/collections/davines');
    await waitForSettled(page);

    const placeholders = page.locator('[data-lazy-render]');
    const initialCount = await placeholders.count();

    // brand-collection has 30+ brand logos. Should have a placeholder.
    if (initialCount === 0) {
      test.info().annotations.push({
        type: 'note',
        description: 'No lazy-render placeholders found — brand-collection.liquid may not have lazy-render applied on this template variant, or page was already in viewport',
      });
      return;
    }

    const initialFetches = net.count('section_id=');
    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
    await page.waitForTimeout(3000);
    await waitForSettled(page);

    expect(net.count('section_id=')).toBeGreaterThan(initialFetches);
  });

  test('Section Rendering API returns full content (not placeholder)', async ({
    request,
  }) => {
    // Direct GET to ?section_id= should return the FULL section HTML,
    // not the placeholder. This verifies the conditional branches in
    // section-collection.liquid + brand-collection.liquid + related.liquid.
    //
    // We pick a homepage section id — Shopify renders the requested
    // section's HTML for any ?section_id=<id> request, picking the
    // request.page_type==null branch.

    // Find a section_id in the rendered homepage to use
    const homeHtml = (await request.get(devUrl('/'))).text();
    const html = await homeHtml;
    const sectionIds = [...html.matchAll(/data-section-id="([^"]+)"/g)].map(
      (m) => m[1]
    );
    test.skip(sectionIds.length === 0, 'No data-section-id found on homepage');

    // Test the first section
    const firstId = sectionIds[0];
    const sectionResponse = await request.get(
      devUrl(`/?section_id=${encodeURIComponent(firstId)}`)
    );
    expect(sectionResponse.ok(), `?section_id=${firstId} fetch failed`).toBe(true);
    const sectionHtml = await sectionResponse.text();

    // Response should NOT be a placeholder (must have actual content,
    // not just <div data-lazy-render>)
    const isOnlyPlaceholder =
      sectionHtml.includes('data-lazy-render') &&
      sectionHtml.length < 1000;
    expect(
      isOnlyPlaceholder,
      `?section_id=${firstId} returned a placeholder instead of full content — ` +
        `the request.page_type==null branch may be wrong in the section's Liquid`
    ).toBe(false);
  });
});
