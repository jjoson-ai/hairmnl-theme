// ujg6.42 Wave A — real Chrome CSS Coverage via Puppeteer + Brave.
//
// Launches Brave, navigates to 5 templates, instruments CSS Coverage,
// scrolls + interacts (open hamburger, hover a product card) to trigger
// JS-injected classes that static analysis can't see, then saves the
// per-template usage data as JSON for the Python bucketer.
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const BRAVE = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser';
// ujg6.42.4 (audit hardening): create the pipeline tempdir as owner-only
// (0o700). Without this, a co-resident user or compromised process on
// the same machine could swap our intermediate JSON files between
// coverage capture and bucketing, injecting arbitrary CSS into the
// emitted chunk files. Path is stable (bucket.py + wave-b-emit.py read
// from the same fixed location) but mode is owner-only.
const TMP_ROOT = '/tmp/ujg6.42';
const OUT = `${TMP_ROOT}/coverage`;
fs.mkdirSync(TMP_ROOT, { recursive: true, mode: 0o700 });
fs.chmodSync(TMP_ROOT, 0o700);
fs.mkdirSync(OUT, { recursive: true, mode: 0o700 });
fs.chmodSync(OUT, 0o700);

const TEMPLATES = {
  home: 'https://www.hairmnl.com/',
  collection: 'https://www.hairmnl.com/collections/davines',
  product: 'https://www.hairmnl.com/products/loreal-professionnel-serie-expert-absolut-repair-shampoo-300ml-oil-30ml',
  cart: 'https://www.hairmnl.com/cart',
  search: 'https://www.hairmnl.com/search?q=shampoo',
};

// CSS files we care about — order matters: more specific names first so
// "custom-theme.css" isn't matched by the more general "theme.css" rule.
const CSS_TARGETS = ['custom-theme.css', 'theme.css'];

async function run() {
  // ujg6.42.4 (audit hardening): keep Chromium's sandbox enabled so a
  // renderer exploit in a crawled page can't escape to the host.
  // Original ran with --no-sandbox to work around a launch flake; default
  // sandbox works fine in normal use.
  const browser = await puppeteer.launch({
    executablePath: BRAVE,
    headless: 'new',
    args: [],
  });

  for (const [name, url] of Object.entries(TEMPLATES)) {
    console.log(`[${name}] navigating to ${url}`);
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    await page.setUserAgent(
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ' +
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36'
    );

    await page.coverage.startCSSCoverage({ resetOnNavigation: false });

    try {
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
    } catch (e) {
      console.log(`  goto warn: ${e.message}`);
    }

    // Interact to trigger JS-injected classes
    try {
      // Scroll the page in chunks to trigger lazy-mounted components.
      // ujg6.42.4 (audit hardening): use page.evaluate() function form +
      // argument passing instead of string interpolation. Prevents any
      // Node-side variable (even a numeric `y`) from being interpreted
      // as JavaScript inside the page context.
      const innerHeight = await page.evaluate(() => window.innerHeight);
      const docHeight = await page.evaluate(() => document.body.scrollHeight);
      for (let y = 0; y < docHeight; y += innerHeight * 0.8) {
        await page.evaluate((scrollY) => window.scrollTo(0, scrollY), y);
        await new Promise(r => setTimeout(r, 200));
      }
      await page.evaluate(() => window.scrollTo(0, 0));

      // Open the cart drawer if present (triggers cart drawer classes)
      const cartIconSel = '[data-cart-toggle], [href="/cart"], .header__cart, .cart__icon';
      const cart = await page.$(cartIconSel);
      if (cart) {
        await cart.hover();
      }

      // Open the mobile hamburger / search drawer to trigger header drawer classes
      const drawer = await page.$('[data-drawer-toggle], .header__mobile__button');
      if (drawer) {
        try { await drawer.click({ delay: 50 }); } catch (e) {}
        await new Promise(r => setTimeout(r, 500));
      }

      // Wait for any settled-state JS
      await new Promise(r => setTimeout(r, 1500));
    } catch (e) {
      console.log(`  interact warn: ${e.message}`);
    }

    const coverage = await page.coverage.stopCSSCoverage();

    // Filter to the theme.css and custom-theme.css entries
    const wanted = coverage.filter(e =>
      CSS_TARGETS.some(t => e.url.includes(t))
    );

    // Reduce to bytes-used range list per file
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

    await page.close();
  }

  await browser.close();
  console.log('\nDone. Per-template coverage JSON written to /tmp/ujg6.42/coverage/');
}

run().catch(e => {
  console.error(e);
  process.exit(1);
});
