// ujg6.42.5 Phase 1 — Extended real Chrome CSS Coverage.
//
// Goal: produce a higher-confidence "_unused" verification by:
//   1. Covering 5 ORIGINAL templates + 4 ADDITIONAL templates that the
//      Wave A pass didn't touch (article, page, blog index, 404).
//   2. Triggering MORE interactions per template — Wave A only hovered
//      the cart icon + clicked the drawer toggle. Here we hover product
//      cards, open the cart drawer fully, open the mobile-nav drawer,
//      open the search drawer, hover the desktop nav (for dropdowns),
//      click product accordions, click PDP variant swatches, and open
//      product image zoom where present.
//   3. Adding a collection-with-filters URL to capture filter-applied
//      styling that the bare /collections/davines URL didn't hit.
//
// Output: /tmp/ujg6.42/coverage-extended/<template>.json (same format
// as the Wave A coverage capture, parallel directory so we can compare).
//
// The Python verification pass (verify-unused.py) intersects the
// Wave A "_unused" bucket with this extended capture's used-byte ranges:
// rules that became "used" in the extended pass are candidates for KEEP;
// rules that remained "_unused" after the extended pass are candidates
// for REMOVAL (after also cross-checking HTML class presence + forced-
// core override list).
//
// Usage: cd hairmnl-theme && node scripts/ujg6.42/coverage-extended.js

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const BRAVE = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser';

// ujg6.42.4 hardening: owner-only tempdir (same pattern as coverage.js)
const TMP_ROOT = '/tmp/ujg6.42';
const OUT = `${TMP_ROOT}/coverage-extended`;
fs.mkdirSync(TMP_ROOT, { recursive: true, mode: 0o700 });
fs.chmodSync(TMP_ROOT, 0o700);
fs.mkdirSync(OUT, { recursive: true, mode: 0o700 });
fs.chmodSync(OUT, 0o700);

// 5 original templates + 4 new ones + 1 filter-state variant
const TEMPLATES = {
  // Original 5 (Wave A) — for cross-reference
  home: 'https://www.hairmnl.com/',
  collection: 'https://www.hairmnl.com/collections/davines',
  product: 'https://www.hairmnl.com/products/loreal-professionnel-serie-expert-absolut-repair-shampoo-300ml-oil-30ml',
  cart: 'https://www.hairmnl.com/cart',
  search: 'https://www.hairmnl.com/search?q=shampoo',

  // NEW templates — Wave A didn't cover these
  blog: 'https://www.hairmnl.com/blogs/tousled-online-magazine',
  article: 'https://www.hairmnl.com/blogs/tousled-online-magazine/the-viral-butterfly-haircut-is-here-to-stay-what-to-know-before-riding-on-this-trend',
  page: 'https://www.hairmnl.com/pages/about-us',
  notfound: 'https://www.hairmnl.com/nonexistent-page-for-404-coverage',

  // State variants
  collectionFiltered: 'https://www.hairmnl.com/collections/davines?filter.v.availability=1',
};

// After ujg6.42 Wave C live-push, the deployed CSS surface is the per-template
// chunk files instead of theme.css + custom-theme.css. We target every chunk
// so the verification can map back to whichever file owns each selector.
// Order matters: list more specific names first so substring-match resolves
// the right file when a URL contains both (e.g. 'custom-theme-core.css' URL
// would otherwise match the more general 'theme-core.css' rule).
const CSS_TARGETS = [
  'custom-theme-core.css',
  'custom-theme-home.css',
  'custom-theme-collection.css',
  'custom-theme-product.css',
  'custom-theme-cart.css',
  'custom-theme-search.css',
  'theme-core.css',
  'theme-home.css',
  'theme-collection.css',
  'theme-product.css',
  'theme-cart.css',
  'theme-search.css',
  // Originals — kept in case a non-live theme is being tested
  'custom-theme.css',
  'theme.css',
];

// ---------------------------------------------------------------------------
// Interaction harness
// ---------------------------------------------------------------------------

async function deepInteract(page, label) {
  // Helper: safely try an interaction, log warn but never throw
  async function tryDo(name, fn) {
    try { await fn(); }
    catch (e) { console.log(`  [${label}] ${name}: ${e.message.slice(0, 80)}`); }
  }

  // 1. Full-page scroll in chunks (Wave A pattern)
  await tryDo('scroll-all', async () => {
    const innerHeight = await page.evaluate(() => window.innerHeight);
    const docHeight = await page.evaluate(() => document.body.scrollHeight);
    for (let y = 0; y < docHeight; y += innerHeight * 0.6) {
      await page.evaluate((sy) => window.scrollTo(0, sy), y);
      await new Promise(r => setTimeout(r, 150));
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    await new Promise(r => setTimeout(r, 200));
  });

  // 2. Hover header navigation links (triggers dropdown menus,
  //    .header__dropdown.is-visible, .navlink:hover etc)
  await tryDo('hover-nav', async () => {
    const navLinks = await page.$$('.header__desktop__button, .navlink--toplevel, .header__menu__inner a');
    for (const link of navLinks.slice(0, 6)) {
      try { await link.hover(); await new Promise(r => setTimeout(r, 100)); } catch (e) {}
    }
  });

  // 3. Hover ALL visible product cards on the page (triggers .product-grid-item:hover,
  //    .grid__swatch__hover, .product__grid__info--hover, .product-grid-item__slide etc)
  await tryDo('hover-products', async () => {
    const cards = await page.$$('.product-grid-item, .product__grid__item, [data-product-grid-item]');
    for (const card of cards.slice(0, 12)) {
      try { await card.hover(); await new Promise(r => setTimeout(r, 80)); } catch (e) {}
    }
  });

  // 4. Open the cart drawer (click, not just hover — triggers .cart__drawer.is-open
  //    + the populated cart-line-item rendering)
  await tryDo('open-cart-drawer', async () => {
    const sel = '[data-cart-toggle], .header__cart, .cart__icon, a[href="/cart"]';
    const el = await page.$(sel);
    if (el) {
      await el.click({ delay: 30 });
      await new Promise(r => setTimeout(r, 800));
      // Close it before next interaction (esc or click outside)
      await page.keyboard.press('Escape').catch(() => {});
      await new Promise(r => setTimeout(r, 300));
    }
  });

  // 5. Open mobile hamburger / search drawer (triggers .drawer.is-open,
  //    .search-drawer, .search__predictive, .header__drawer)
  await tryDo('open-mobile-drawer', async () => {
    const sel = '[data-drawer-toggle], .header__mobile__button, [data-drawer="hamburger"]';
    const el = await page.$(sel);
    if (el) {
      await el.click({ delay: 30 });
      await new Promise(r => setTimeout(r, 600));
      await page.keyboard.press('Escape').catch(() => {});
      await new Promise(r => setTimeout(r, 300));
    }
  });

  // 6. Open search drawer (header search icon) — separate from mobile drawer
  await tryDo('open-search-drawer', async () => {
    const sel = '[data-search-toggle], .header__search, .search__icon, button[aria-label*="search" i]';
    const el = await page.$(sel);
    if (el) {
      await el.click({ delay: 30 });
      await new Promise(r => setTimeout(r, 500));
      // Type a character to trigger predictive results
      await page.keyboard.type('s', { delay: 30 }).catch(() => {});
      await new Promise(r => setTimeout(r, 600));
      await page.keyboard.press('Escape').catch(() => {});
      await new Promise(r => setTimeout(r, 300));
    }
  });

  // 7. Open product accordions / collapsibles
  await tryDo('open-accordions', async () => {
    const accs = await page.$$('.accordion__title, .sidebar__heading, [data-accordion-trigger], .product__accordion__title');
    for (const acc of accs.slice(0, 4)) {
      try { await acc.click({ delay: 20 }); await new Promise(r => setTimeout(r, 200)); } catch (e) {}
    }
  });

  // 8. Click PDP variant swatches if any present (color/size selectors)
  await tryDo('click-variant-swatches', async () => {
    const swatches = await page.$$('.swatch__list .swatch__option, [data-variant-option], .product__variant-option');
    for (const sw of swatches.slice(0, 3)) {
      try { await sw.click({ delay: 20 }); await new Promise(r => setTimeout(r, 200)); } catch (e) {}
    }
  });

  // 9. Click product image to attempt zoom (.zoom-pswp, .pswp opens)
  await tryDo('click-product-image', async () => {
    const img = await page.$('.product__image, .product-image-main, [data-zoom-image], .product__media-item img');
    if (img) {
      try { await img.click({ delay: 30 }); await new Promise(r => setTimeout(r, 500)); } catch (e) {}
      await page.keyboard.press('Escape').catch(() => {});
      await new Promise(r => setTimeout(r, 200));
    }
  });

  // 10. Trigger announcement bar / ticker interaction
  await tryDo('hover-announcement', async () => {
    const ann = await page.$('.announcement__bar, .ticker--animated, [data-announcement]');
    if (ann) { try { await ann.hover(); await new Promise(r => setTimeout(r, 200)); } catch (e) {} }
  });

  // 11. Hover footer links
  await tryDo('hover-footer', async () => {
    const footerLinks = await page.$$('footer a, .site-footer a, .footer-quicklinks a');
    for (const link of footerLinks.slice(0, 6)) {
      try { await link.hover(); await new Promise(r => setTimeout(r, 80)); } catch (e) {}
    }
  });

  // 12. Submit empty form to trigger error states (if a form is present)
  await tryDo('trigger-form-errors', async () => {
    const submit = await page.$('button[type=submit], input[type=submit]');
    // Don't actually submit — would navigate away. Just focus + blur empty input.
    const inputs = await page.$$('input[type=email], input[type=text]');
    for (const i of inputs.slice(0, 2)) {
      try { await i.focus(); await i.evaluate(el => el.dispatchEvent(new Event('blur', { bubbles: true }))); } catch (e) {}
    }
  });

  // Wait for any settled JS
  await new Promise(r => setTimeout(r, 800));
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function run() {
  const browser = await puppeteer.launch({
    executablePath: BRAVE,
    headless: 'new',
    args: [],
  });

  let totalTemplates = 0;
  const startedAt = Date.now();

  for (const [name, url] of Object.entries(TEMPLATES)) {
    totalTemplates++;
    const t0 = Date.now();
    console.log(`[${name}] navigating to ${url.substring(0, 80)}...`);

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    await page.setUserAgent(
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ' +
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36'
    );

    await page.coverage.startCSSCoverage({ resetOnNavigation: false });

    try {
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 35000 });
    } catch (e) {
      console.log(`  goto warn: ${e.message.slice(0, 80)}`);
    }

    await deepInteract(page, name);

    const coverage = await page.coverage.stopCSSCoverage();
    const wanted = coverage.filter(e => CSS_TARGETS.some(t => e.url.includes(t)));

    const out = {};
    for (const entry of wanted) {
      const file = CSS_TARGETS.find(t => entry.url.includes(t));
      const total = entry.text ? entry.text.length : 0;
      const used = entry.ranges.reduce((s, r) => s + (r.end - r.start), 0);
      out[file] = {
        url: entry.url,
        total_bytes: total,
        used_bytes: used,
        used_pct: total ? Math.round(used / total * 1000) / 10 : null,
        ranges: entry.ranges,
      };
      console.log(`  ${file}: used ${used}/${total} = ${out[file].used_pct}%`);
    }

    fs.writeFileSync(
      path.join(OUT, `${name}.json`),
      JSON.stringify(out, null, 2)
    );

    console.log(`  done in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
    await page.close();
  }

  await browser.close();
  const elapsed = ((Date.now() - startedAt) / 1000).toFixed(1);
  console.log(`\nDone. ${totalTemplates} templates in ${elapsed}s. Per-template`
              + ` coverage JSON written to ${OUT}/`);
}

run().catch(e => {
  console.error(e);
  process.exit(1);
});
