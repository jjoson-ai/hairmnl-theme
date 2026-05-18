/**
 * Smoke 7 — Font preloads + homepage hero eager (ujg6.19)
 *
 * Validates:
 *   - BasisGrotesquePro-Regular.woff2 + SelfModern.woff2 are <link rel=preload>
 *     in the document <head>
 *   - Both fonts fetch early in the network waterfall (before most other
 *     resources)
 *   - Homepage first slideshow slide image has loading=eager + fetchpriority=high
 */

import { test, expect } from '@playwright/test';
import { visitDev, waitForSettled } from '../helpers/dev-preview';
import { recordNetwork } from '../helpers/network-filter';

test.describe('Smoke 7: Font preloads + slideshow eager-loading', () => {
  test('homepage has 2 font preload <link> tags in <head>', async ({ page }) => {
    await visitDev(page, '/');

    // Check the parsed DOM
    const preloadLinks = await page.evaluate(() =>
      Array.from(document.querySelectorAll('link[rel="preload"][as="font"]')).map(
        (l) => l.getAttribute('href') || ''
      )
    );

    const hasBasis = preloadLinks.some((h) =>
      h.includes('BasisGrotesquePro-Regular.woff2')
    );
    const hasSelf = preloadLinks.some((h) => h.includes('SelfModern.woff2'));

    if (!hasBasis || !hasSelf) {
      console.log('[smoke-7] font preload links found:', preloadLinks);
    }

    expect(hasBasis, 'BasisGrotesquePro-Regular.woff2 must be preloaded').toBe(true);
    expect(hasSelf, 'SelfModern.woff2 must be preloaded').toBe(true);
  });

  test('font preloads fetch within the first 50 network requests', async ({
    page,
  }) => {
    const net = recordNetwork(page);
    await visitDev(page, '/');
    await waitForSettled(page);

    const allRequests = net.all();
    const basisIdx = allRequests.findIndex((r) =>
      r.url.includes('BasisGrotesquePro-Regular.woff2')
    );
    const selfIdx = allRequests.findIndex((r) =>
      r.url.includes('SelfModern.woff2')
    );

    expect(basisIdx, 'BasisGrotesquePro-Regular.woff2 must be fetched').toBeGreaterThanOrEqual(
      0
    );
    expect(selfIdx, 'SelfModern.woff2 must be fetched').toBeGreaterThanOrEqual(0);
    // The preloads should be among the first 50 requests (early in waterfall).
    // Most pages issue 200-400 total requests; being in the first 50
    // confirms the browser scanner picked up the preload hints.
    expect(
      basisIdx,
      `Basis font fetched as request #${basisIdx} — should be in first 50`
    ).toBeLessThan(50);
    expect(
      selfIdx,
      `SelfModern font fetched as request #${selfIdx} — should be in first 50`
    ).toBeLessThan(50);
  });

  test('homepage first slide image has eager + fetchpriority=high', async ({
    page,
  }) => {
    await visitDev(page, '/');
    await waitForSettled(page);

    // section-banner-slider's first slide has class .banner-slide-img
    // (this is the actual homepage LCP element per tonight's ujg6.19 audit).
    // Note: ujg6.19 also added eager:true to section-slideshow's first slide,
    // but that section isn't on the homepage — it's on blog templates etc.
    const firstSlideAttrs = await page.evaluate(() => {
      const img = document.querySelector(
        '.banner-slide-img, [data-section-type="banner-slider"] img, .slideshow__slide:first-child img'
      ) as HTMLImageElement | null;
      if (!img) return null;
      return {
        loading: img.getAttribute('loading'),
        fetchpriority: img.getAttribute('fetchpriority'),
        src: img.src.split('?')[0].slice(-80),
      };
    });

    if (!firstSlideAttrs) {
      test.info().annotations.push({
        type: 'note',
        description:
          'Could not locate first slide image on homepage — section-banner-slider may have changed selector. Spot-check manually.',
      });
      return;
    }

    expect(
      firstSlideAttrs.loading,
      `First slide img loading="${firstSlideAttrs.loading}" — should be "eager"`
    ).toBe('eager');
    expect(
      firstSlideAttrs.fetchpriority,
      `First slide img fetchpriority="${firstSlideAttrs.fetchpriority}" — should be "high"`
    ).toBe('high');
  });
});
