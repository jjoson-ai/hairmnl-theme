# Critical-CSS coverage audit — bd hairmnl-theme-ujg6.34

> **TL;DR:** Brand mobile loads **2896 KB of CSS** with only **6.1% actually used**. The 93.9% waste breaks down into 4 actionable buckets: third-party widget CSS that doesn't fire on collection pages, our theme.css carrying rules for other templates, embedded-player CSS from invisible YouTube embeds, and Shopify's preview-bar (dev-only, ignore).

Date: 2026-05-19
Tool: Chromium DevTools Coverage API via Playwright
Target: `https://g5a1snqu4toropj3-14124580.shopifypreview.com/collections/davines` (mobile, 390×844)

## Summary

| Metric | Value |
|---|---|
| Total CSS loaded | **2896.5 KB** (75 stylesheets) |
| Used | **177.6 KB (6.1%)** |
| Unused | **2718.9 KB (93.9%)** |

Note: PSI reports 411KB of compressed CSS transfer; Coverage reports uncompressed/parsed bytes (browser memory footprint). The 6.1% used figure measures BOTH used vs unused inside the same delivered bytes — so reducing total delivery has direct LCP / TBT impact.

## Top 15 by unused bytes

| Rank | Stylesheet | Total | Unused | % Unused | Action |
|---|---|---|---|---|---|
| 1 | shopifycloud/preview-bar/vendor.css | 824 KB | **783 KB** | 95% | **DEV-ONLY** — ignore, never on live |
| 2 | youtube.com player CSS (`www-player.css`) | 506 KB | **504 KB** | 99.5% | Investigate YouTube embed source on brand page |
| 3 | youtube ytembeds CSS | 435 KB | **417 KB** | 96% | Same as #2 |
| 4 | **OUR theme.css** | 285 KB | **245 KB** | 86% | **Split or template-gate** |
| 5 | searchanise/results_modern.css | 93 KB | **93 KB** | 100% | Gate to /search only |
| 6 | satcb.azureedge.net (Smart Add to Cart) | 76 KB | **76 KB** | 99% | Gate or defer |
| 7 | **OUR deferred-extras.css** | 69 KB | **69 KB** | 99.9% | Verify `media="print"` until scroll trick |
| 8 | bogos freegifts CSS | 52 KB | **51 KB** | 98% | Gate to templates with active gifts |
| 9 | judge.me widget_v3 CSS | 48 KB | **47 KB** | 98% | Gate to PDP only |
| 10 | **OUR custom-theme.css** | 53 KB | **45 KB** | 86% | Split above-fold / below-fold |
| 11 | shopify-giftwrap (LDT) | 39 KB | **37 KB** | 95% | Gate to /cart |
| 12 | (inline on brand page document) | 38 KB | **36 KB** | 95% | Audit critical-css.liquid inline block |
| 13 | **OUR aos.css** (animate-on-scroll) | 34 KB | **34 KB** | 99% | Lazy-load (defer until first scroll trigger) |
| 14 | searchanise/recommendation.css | 33 KB | **33 KB** | 100% | Same as #5 |
| 15 | searchanise/results_mobile.css | 28 KB | **28 KB** | 100% | Same as #5 |

**Subtotal of actionable unused CSS (excluding Shopify preview-bar and #1's dev-only artifact):** ~1.5 MB

## Action plan

Tier 1 — operator-only, no code:

- ✅ `ujg6.40` (already filed) — uninstalling LimeSpot Shopify app will eliminate any LimeSpot CSS too. But LimeSpot CSS didn't appear in the top-15 list, so this is small.

Tier 2 — single-template CSS gating (HIGH leverage, ~3 hrs each):

- **YouTube embeds (rank #2 + #3, ~921 KB unused).** No YouTube embed is visible on the Davines collection page, yet 921 KB of YouTube player CSS loads. Likely culprits: (a) a homepage video embed leaking via Shopify cache, (b) a brand-bio metafield containing an embedded video, (c) a section block emitting an iframe at zero height. **Action:** grep `youtube.com\|iframe` across snippets + sections; identify the offender; lazy-load via `loading="lazy"` on iframe + `data-src` swap.
- **Theme.css template-split (rank #4, ~245 KB unused).** theme.css currently ships ALL page styles to every template. Split into: `theme-core.css` (everything used on every page), `theme-collection.css`, `theme-product.css`, `theme-cart.css`, `theme-customer.css`. Wire conditionally in `layout/theme.liquid` based on `template`. Effort: 4-6 hrs (needs Coverage on each template type to map rules → split). Saves ~150-200 KB per page.

Tier 3 — TAE / app gate (MEDIUM, ~1-2 hrs each):

- **Searchanise (rank #5 + #14 + #15, ~153 KB unused).** Search CSS loads on every page but only `/search` uses it. Configure Searchanise to gate via `template == 'search'` OR lazy-load on first search-icon click.
- **Judge.me (rank #9, 47 KB unused).** Reviews CSS only needed on PDP + collection-with-stars. Gate via `template contains 'product'`.
- **BOGOS freegifts (rank #8, 51 KB unused).** Gate to templates with active free-gift campaigns.
- **LDT Gift Wrap (rank #11, 37 KB unused).** Gate to `template == 'cart'`.
- **Smart Add to Cart Button satcb (rank #6, 76 KB unused).** Currently loads on every page. Gate via TAE app embed settings to only PDP + collection.

Tier 4 — critical-css inline audit (LOW, ~3 hrs):

- **Inline brand-page CSS (rank #12, 36 KB unused).** `snippets/critical-css.liquid` ships an inline block on every page. 95% unused on brand mobile. Strip rules tagged for other templates (homepage hero, PDP gallery, etc).
- **aos.css (rank #13, 34 KB unused).** Animate-on-scroll library — only used by sections with scroll triggers. Lazy-load via IntersectionObserver on `[data-aos]` mount.
- **custom-theme.css (rank #10, 45 KB unused).** Same template-split treatment as theme.css.

## Expected impact if Tier 2+3 ships

| Metric | Today | After Tier 2+3 (est.) |
|---|---|---|
| Total CSS delivery (brand mobile) | 2896 KB | ~600-800 KB |
| Used / total | 6.1% | 25-35% |
| FCP brand mobile | 2.27s | -0.3 to -0.6s |
| LCP brand mobile (assuming hero preload from ujg6.31) | 7.41s | -0.5 to -1.0s |
| TBT brand mobile (CSS parse cost component) | 2822ms | -200 to -500ms |

The single highest-leverage action is **finding and removing the invisible YouTube embed** (Tier 2 first bullet). 921 KB of CSS for content nobody can see is the most egregious waste.

## Methodology to reproduce

```bash
cd /Users/y9378348c/Projects/hairmnl-theme/scripts/smoke-tests
NODE_OPTIONS="--tls-max-v1.2" node -e "
  // see ujg6.34 close-notes for the full Playwright coverage script
"
```

To run for other templates, change the URL: home, PDP, cart, etc. Compare across to determine which rules belong to "common core" vs "template-specific" buckets.
