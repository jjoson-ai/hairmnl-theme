# custom-theme.js — behavior inventory + template-usage audit

> **Bead:** hairmnl-theme-ujg6.10 (P2.1)
> **Date:** 2026-05-18
> **Status:** Complete
> **File:** assets/custom-theme.js (~9,118 LoC, 445 KB)

---

## Behavior inventory

| # | Behavior | LoC | Line Range | Templates | Key Selectors | Vendor Deps | Removable? |
|---|----------|-----|------------|-----------|---------------|-------------|------------|
| 1 | **sticky-filter-bar** | ~34 | 3243–3276 | collection, search, thebackbar collections | `.collection__nav` | sticky-js | Partial — can replace with `position:sticky` CSS |
| 2 | **product-tabs-v1** | ~26 | 3278–3304 | PDP (product, product.kr-product, product.backbar-product, product.reward-product, product.promo-product) | `.tab-button`, `.tabs`, `.active-tab` | None | No — active on PDPs |
| 3 | **cross-post-blogs** | ~98 | 8429–8526 | article (all article/blog templates), collection, product.backbar-product, product.reward-product, product.promo-product, many thebackbar collections | `.cross-post-blogs`, `.cross-post-blogs .swiper-slide`, `.cross-post-blogs .swiper-container` | Swiper (Navigation) | No — active on articles + collections |
| 4 | **hover-line** (Tousled header) | ~173 | 8528–8701 | All pages using `tousled-header` (article, blog) + all pages using `header.liquid` (global header) | `[data-tousled-header-wrapper]`, `[data-main-menu-text-item]`, `[data-text-items-wrapper]`, `.navtext`, `[data-links-wrapper]` | None | No — global header behavior |
| 5 | **header-mobile-sliderule** | ~110 | 8703–8808 | All pages with `tousled-header` section + pages using `header.liquid`/`thebackbar-master-header.liquid` | `[data-tousled-sliderule]`, `data-tousled-sliderule-open`, `data-tousled-sliderule-close`, `data-tousled-sliderule-pane` | None | No — mobile nav, global |
| 6 | **lion-points** (Loyalty points display) | ~20 | 8810–8829 | All pages (header is global) — but only fires when `.navlink-account.is-loggedin` exists | `.navlink-account.is-loggedin`, `.points-approved`, `.points-label` | None | Partial — only activates for logged-in users with LoyaltyLion points; always parsed though |
| 7 | **banner-slider** | ~22 | 8831–8853 | home (index), many collection templates, page.hairmnlstudio-main, page.hairmnlstudio-portfolio, page.hairmnlstudio-menu, page.academy-feature, page.judgeme-all-reviews + thebackbar collections | `.banner-slider .swiper` | Swiper (Navigation, Pagination, Autoplay) | No — active on home + collections |
| 8 | **collection-slider** | ~98 | 8855–8953 | home (index — 8 instances), collection pages, thebackbar collections, branded collections, many blog/article pages, brand collection pages | `.swiper.collection` | Swiper (Navigation) | No — active on most pages with products |
| 9 | **domparser** (metafield text strip) | ~10 | 8955–8978 | PDP variants (where `.metafield-multi_line_text_field` exists) | `.metafield-multi_line_text_field` | None | Partial — only if metafield multi-line text fields exist in product descriptions |
| 10 | **consent-modal** (technical products consent) | ~123 | 8980–9103 | cart page only | `form.cart`, `.cart__items__row[data-with-consent]`, `[data-drawer="drawer-cart"]`, `.checkout__button` | sweetalert2, he | Partial — only on cart page when products with `with-consent` tag exist; but sweetalert2 bundles are parsed on every page |

---

## Vendor library bundle

| Vendor | LoC | Line Range | Used By | Remove? |
|--------|-----|------------|---------|---------|
| **sticky-js** | ~344 | 24–367 | Behavior #1 (sticky-filter-bar) | Yes — replace with `position:sticky` CSS |
| **he** (HTML entities) | ~241 | 369–609 | Behavior #10 (consent-modal, via SweetAlert2's HTML entity encoding) | Yes if SweetAlert2 is removed; he is a dependency of sweetalert2's HTML sanitization |
| **sweetalert2** | ~2,631 | 611–3241 | Behavior #10 (consent-modal) | Yes — replace with native `<dialog>` or lightweight custom modal |
| **ssr-window** | ~144 | 3306–3449 | Swiper (SSR compatibility shim) | Yes if Swiper is extracted to async — unnecessary in browser-only context |
| **dom7** | ~682 | 3450–4131 | Swiper (DOM manipulation utility) | Yes if Swiper is extracted to async |
| **Swiper core + modules** (Navigation, Pagination, Autoplay) | ~4,296 | 4132–8427 | Behaviors #3, #7, #8 (cross-post-blogs, banner-slider, collection-slider) | No — but can be async-loaded only on pages that need it |

**Vendor total:** ~8,038 LoC (88% of file)
**Custom behavior total:** ~727 LoC (8% of file)
**Boilerplate/bundler shim:** ~353 LoC (~4% — `__commonJS`, `__toESM`, etc.)

---

## Removable code

**Total removable LoC:** ~3,216
**Total removable KB:** ~157 KB (assuming ~50 bytes/line average — vendor code is denser)

| Behavior/Vendor | Reason removable | LoC saved |
|----------------|-----------------|-----------|
| **sticky-js** (vendor) | Replace with `position: sticky` CSS + `top: var(--menu-height)` — already using CSS custom property `--menu-height` in theme | ~344 |
| **sweetalert2** (vendor) | Replace consent-modal with native `<dialog>` element + custom CSS. SweetAlert2 is ~2,631 LoC used only for one modal on the cart page | ~2,631 |
| **he** (vendor) | SweetAlert2 dependency; if SA2 is removed, he can be removed too | ~241 |
| **consent-modal** (behavior) | Can be replaced with a lightweight `<dialog>`-based consent form — no need for a full modal library | ~123 (behavior) but effectively 0 if SA2 removed inline |

**Conditional removable** (async/lazy-load strategy):

| Behavior/Vendor | Strategy | LoC saved from main thread |
|----------------|----------|---------------------------|
| **Swiper bundle** (vendor: ssr-window + dom7 + Swiper) | Async-chunk loaded only on pages with sliders (home, collections, PDPs with cross-post-blogs, articles) — not on cart, account, search-only pages | ~5,122 |
| **cross-post-blogs** (behavior) | Already IO-deferred; could move to async chunk with Swiper | ~98 |
| **banner-slider** (behavior) | Already eager; could IO-defer + move to async chunk | ~22 |
| **collection-slider** (behavior) | Already IO-deferred; could move to async chunk | ~103 |

---

## Top 3 TBT-reduction recommendations

Ranked by estimated main-thread time saved:

1. **Async-chunk Swiper (+ dependencies: ssr-window, dom7, Navigation, Pagination, Autoplay)** — The Swiper bundle is ~5,122 LoC (~250 KB unminified) parsed and executed on every page load, even on pages without any sliders (cart, account, password). Moving Swiper to an async chunk that loads only when `.swiper.collection` or `.banner-slider .swiper` or `.cross-post-blogs .swiper-container` is detected in the DOM would eliminate ~250 KB of synchronous JS parse + ~150-200ms of TBT on pages without sliders. On slider pages, the IO-defer pattern already delays init, but the parse cost still blocks main thread.

2. **Remove SweetAlert2 + he, replace consent-modal with `<dialog>`** — SweetAlert2 is ~2,631 LoC (~128 KB) parsed on every single page but only used on the cart page for a consent dialog. A native `<dialog>` element with custom CSS is ~20 LoC and has zero parse cost. This alone saves ~128 KB of JS parse + ~80-120ms of TBT across all non-cart pages. On cart pages, the dialog still works with no perceptible delay difference.

3. **Replace sticky-js with CSS `position: sticky`** — sticky-js is ~344 LoC (~17 KB) parsed on every collection/search page load. A native CSS `position: sticky; top: var(--menu-height)` rule achieves identical behavior with zero JS. The theme already sets `--menu-height` as a CSS custom property. Estimated savings: ~17 KB parse + ~10-20ms TBT on collection + search pages.

---

## Per-template JS parse overhead

The entire `custom-theme.js` (9,118 LoC, 445 KB) is parsed on every page. Below is the active behavior breakdown per template type:

| Template | Active behaviors | Total LoC parsed (full bundle) | LoC actually useful | Wasted LoC |
|----------|-----------------|-------------------------------|--------------------|-------------| 
| **home** (/) | hover-line, mobile-sliderule, lion-points, banner-slider, collection-slider | 9,118 | ~423 | ~8,695 (95%) |
| **collection** | hover-line, mobile-sliderule, lion-points, sticky-filter-bar, banner-slider, collection-slider, cross-post-blogs (some) | 9,118 | ~575 | ~8,543 (94%) |
| **PDP** (product) | hover-line, mobile-sliderule, lion-points, product-tabs-v1, domparser, collection-slider (cross-sell) | 9,118 | ~450 | ~8,668 (95%) |
| **cart** | hover-line, mobile-sliderule, lion-points, consent-modal | 9,118 | ~421 | ~8,697 (95%) |
| **article** (blog post) | hover-line, mobile-sliderule, lion-points, cross-post-blogs, collection-slider | 9,118 | ~419 | ~8,699 (95%) |
| **brand-collection** | hover-line, mobile-sliderule, lion-points, sticky-filter-bar, banner-slider, collection-slider | 9,118 | ~457 | ~8,661 (95%) |

**Key insight:** Across all template types, 94-95% of the parsed JS is unused vendor/behavior code. Even on the most slider-heavy pages (collection), only ~6% of the bundle is relevant. This confirms the primary OS2 migration strategy: code-split vendor libraries into async chunks and remove sweetalert2/he entirely.

---

## Detailed behavior notes

### Behavior #3: cross-post-blogs (lines 8429–8526)
- Uses **IntersectionObserver** with 200px rootMargin to lazy-init
- Creates Swiper instance with init:false, then calls `.init()` on intersect
- Has console.log statements leftover from debugging (`console.log("wrapper", ...)` at line 8733, `console.log` in showSliderule)
- Mobile detection uses `typeof window.orientation !== "undefined"` — non-standard API

### Behavior #5: header-mobile-sliderule (lines 8703–8808)
- Contains **3 `console.log` calls** (lines 8733, 8789, 8794-8795) — debug leftovers that fire on every mobile menu interaction
- Uses custom event `theme:sliderule:close`

### Behavior #4: hover-line (lines 8528–8701)
- Uses CSS custom properties (`--bar-left`, `--bar-width`, `--bar-bottom`, `--bar-text`, `--bar-opacity`) for animation
- Has layout-thrash mitigation comments (INP fix)
- Listens to custom `theme:resize` event
- Only activates when `[data-tousled-header-wrapper]` exists in DOM

### Behavior #1: sticky-filter-bar (lines 3243–3276)
- Only activates on mobile (`max-width: 600px` matchMedia)
- Sets `data-margin-top` from `--menu-height` CSS var
- Dependencies on sticky-js can be fully replaced with `position: sticky`

### Behavior #10: consent-modal (lines 8980–9103)
- Hardcoded consent HTML string in JS (not i18n-ready)
- Has early-return guard for non-cart pages (`if (!cartForm) return`) — but SweetAlert2 is still parsed
- Uses `setInterval` polling on drawer open (100ms interval)
- Registers `submit` event on cart form — only relevant on `/cart` page

### Behavior #8: collection-slider (lines 8855–8953)
- IntersectionObserver lazy-init with 1200px rootMargin (Fix B, 2026-05-16)
- Navigation buttons scoped to slider's `.wrapper` parent (Fix C, 4crg bug)
- Spinner display guard (`spinnerEl.classList.contains('spinner-wrapper')`) — spinner template was removed, guard for backward compat
- `allowSlidePrev: false` initially — prevents backward sliding until first forward slide

### Behavior #7: banner-slider (lines 8831–8853)
- Eager init at DOMContentLoaded (not IO-deferred)
- Uses Swiper modules: Navigation, Pagination, Autoplay
- Loop mode enabled with `centeredSlides: true`

### Behavior #9: domparser (lines 8955–8978)
- Originally used node-html-parser (~5,400 LoC bundled) — already replaced with native `el.textContent = el.textContent`
- Simple DOMContentLoaded guard with early return
- Only activates when `.metafield-multi_line_text_field` elements exist
---

# Phase A.3 refresh — 2026-05-18 PM

> **Context:** post-revert (49ae3dc) re-orientation. The base audit above
> (commit 04e6f9e) inventoried custom-theme.js. This refresh adds the missing
> companion files (shop.js, jquery.min.js, lazysizes.js, custom-theme.css)
> and applies the explicit **KEEP / TAE / DROP** classification required
> by p8-cutover-checklist.md Phase A.3.

## Classification key

- **KEEP** — Behavior survives in the P8 bundled `theme.js`. Re-implement in
  the new bundle. May change syntax/style but functionality preserved.
- **TAE** — Move to a Shopify Theme App Extension (vendor-provided block).
  Theme code is removed; the app self-loads via Shopify's TAE injection.
- **DROP** — No longer needed. The functionality is replaced by a modern
  native API, OR the behavior was vestigial and no callsite needs it.

## custom-theme.js — 10 behaviors classified

| # | Behavior | LoC | Classification | Replacement strategy |
|---|----------|-----|----------------|---------------------|
| 1 | sticky-filter-bar | ~34 | **DROP** | Replace with native `position: sticky; top: var(--menu-height)` CSS. Already partially done in path-b's hairmnl-custom.js section 1; port to P8 bundle as a CSS rule (no JS) inside `snippets/css-overrides.liquid` or `assets/theme.css`. |
| 2 | product-tabs-v1 | ~26 | **KEEP** | Re-implement in P8 bundle with vanilla JS (no jQuery). Already vanilla in path-b's hairmnl-custom.js section 2 — port that. Active on 5 PDP variants. |
| 3 | cross-post-blogs | ~98 | **KEEP** | Re-implement in P8 bundle. Async-chunk with Swiper (see vendor section below). IO-defer is already in the implementation. |
| 4 | hover-line (Tousled header) | ~173 | **KEEP** | Re-implement in P8 bundle. Global header behavior — every page. Already vanilla in path-b's hairmnl-custom.js section 6 — port that. |
| 5 | header-mobile-sliderule | ~110 | **KEEP** | Re-implement in P8 bundle. Mobile nav slide-rule pattern, global. Already vanilla in path-b's hairmnl-custom.js section 3 — port that. |
| 6 | lion-points (LoyaltyLion display) | ~20 | **KEEP** | Re-implement in P8 bundle. Tiny — just a DOM observer for `.points-approved` populating. Active only on logged-in user pages but parsed everywhere. Path-b section 4 has it ported. |
| 7 | banner-slider | ~22 | **KEEP** | Re-implement in P8 bundle as async-chunk with Swiper. IO-defer pattern needs to be added (currently eager). |
| 8 | collection-slider | ~98 | **KEEP** | Re-implement in P8 bundle as async-chunk with Swiper. IO-defer already in implementation. |
| 9 | domparser (metafield strip) | ~10 | **KEEP** | Re-implement in P8 bundle. Trivial — `el.textContent = el.textContent`. Path-b section 5. |
| 10 | consent-modal | ~123 | **KEEP (refactored)** | Re-implement in P8 bundle but **replace SweetAlert2 + he with native `<dialog>`** (~20 LoC custom CSS + minimal JS). Only loads on cart page when `data-with-consent` products are in cart. |

**Net KEEP-but-refactored count**: 9 behaviors → ~580 LoC of hand-written vanilla JS in the P8 bundle (down from 727 LoC including consent-modal's modal-library bloat).

## custom-theme.js — 6 vendor libs classified

| Vendor | LoC | KB | Classification | Notes |
|--------|-----|-----|---------------|-------|
| sticky-js | ~344 | ~17 | **DROP** | Replaced by CSS `position: sticky`. |
| he (HTML entities) | ~241 | ~12 | **DROP** | Was a sweetalert2 dep. Removed when sweetalert2 leaves. |
| sweetalert2 | ~2,631 | ~128 | **DROP** | Replace consent-modal with native `<dialog>`. |
| ssr-window | ~144 | ~7 | **DROP** | Was a Swiper SSR shim. P8 client-only — never needed. |
| dom7 | ~682 | ~33 | **DROP** | Swiper's jQuery-style helper. Modern Swiper versions don't need it; use Swiper-bundle.min from a CDN OR import the modules directly. |
| Swiper (core + Navigation, Pagination, Autoplay) | ~4,296 | ~210 | **KEEP (async-chunked)** | Active on home, collection, PDP, article. Bundle as a separate chunk loaded only when `[data-swiper-instance]` or similar selector exists in DOM. Estimated chunk size: ~80 KB minified (Swiper 11+ tree-shaken). |

**Net vendor reduction**: 8,038 LoC → ~4,296 LoC chunked (i.e., not on critical path). **Savings: ~177 KB synchronous JS parse on non-slider pages.**

## shop.js (134 KB, 35 lines) — vendor bundle on live storage only

**Status**: Loaded by `layout/theme.liquid:999`. Exists on Shopify CDN (HTTP 200 verified). **NOT in git repo.** Pulled from live as `/tmp/p8-live-snapshot/assets/shop.js`.

**Contents** (per file header):
- `window.theme = window.theme || {}` — global namespace stub
- `Modernizr` polyfill — only `touch` feature detection
- **lodash 4.5.1 (Custom Build, "lodash core")** — ~134 KB minified

| Component | KB | Classification | Replacement |
|-----------|-----|----------------|-------------|
| window.theme stub | ~0.1 | **DROP** | P8 bundle has its own namespace; set at top of bundle. |
| Modernizr touch detect | ~0.5 | **DROP** | Replace with `'ontouchstart' in window \|\| navigator.maxTouchPoints > 0` (5-LoC inline). |
| lodash core | ~133 | **DROP** | Audit callsites in snippets/sections. Most lodash functions have native ES2020+ equivalents (`_.map` → `.map`, `_.filter` → `.filter`, `_.debounce` → custom 5-LoC implementation, etc.). |

**Net savings if shop.js is removed entirely**: 134 KB synchronous JS off every page. Requires a callsite audit (separate bd ticket) before removal.

## jquery.min.js (~85 KB, jQuery 2.2.3) — P6 legacy dependency

**Status**: Loaded by `layout/theme.liquid:699`. Version 2.2.3 (released 2016) — outdated. Bundled in repo at `assets/jquery.min.js`.

**Usage scope**: ~77 callsites across snippets/sections matching lazysizes/data-src/loading-class patterns (see lazysizes section below). Plus app-injected jQuery usage from BSS B2B and other legacy apps.

| Classification | Rationale |
|----------------|-----------|
| **DROP** (target) | Modern P8 should not depend on jQuery. Most usage is `$(selector).addClass/removeClass/on(event)` — trivial to replace with vanilla JS. |
| **CONDITIONAL KEEP** (fallback) | If a TAE-loaded app (BSS B2B, Smart SEO, Klaviyo) injects code that references `window.$` or `window.jQuery`, those apps would break. Per `app-compatibility-matrix.md`, most GREEN-tier apps no longer require jQuery. **Verify before drop**: grep app-injected scripts in production for `$(` or `jQuery(` — if any third-party app references it, keep jQuery loaded conditionally. |

**Recommended for Phase B**: drop jQuery from the P8 bundle. If any app breaks during Phase C verification, re-add jQuery with a `defer` attribute and a follow-up ticket to remove that app's dependency.

## lazysizes.js (~29 KB) — image lazy-loader

**Status**: Loaded by `layout/theme.liquid` (in the `<head>` section, before line 105 references). 77 callsites in snippets/sections use the lazysizes pattern (`data-src=`, `class="lazyload"`, `class="lazy-image"`).

**Classification**: **DROP** (with callsite migration).

**Migration plan**:
1. **Phase B precondition**: identify all 77 callsites. They fall into three patterns:
   - `<img class="lazyload" data-src="..." />` — direct lazysizes pattern
   - `<div class="lazy-image" style="padding-top: X%">...</div>` — aspect-ratio reservation wrapper (depends on lazysizes adding `.lazyloaded` class)
   - `<img loading="lazy" src="..." />` — already native (some callsites partially migrated)
2. **For pattern 1**: replace `class="lazyload" data-src="..."` with `loading="lazy" src="..."`. Native browser-driven.
3. **For pattern 2**: the `.fade-in` opacity flip depends on `lazyloaded` class. Replace with `loading="lazy"` + a CSS-only opacity transition triggered on `<img>` load via `:has()` or on a wrapper class set by a small IntersectionObserver (5-LoC). OR drop the `.fade-in` effect entirely — it's a stylistic nicety, not core UX.
4. **For pattern 3**: already done — no change needed.

**Tactical**: lazysizes itself is **drop in Phase B**. Callsite migration is a separate bd ticket (P2 candidate) that should land before Phase C verification.

## custom-theme.css (~2,757 lines, ~75 KB, 608 top-level selectors) — P6 brand bundle

**Status**: Loaded by `layout/theme.liquid:115` and `:356` (deferred via media=print+onload swap). Critical for: megamenu chrome, product card layout, button overrides, brand color palette, collection slider styling.

**Top-level selector categories** (608 unique):
- Buttons / actions: `.btn--*`, `.button-*` — ~30 selectors
- Menu / nav: `.menu-buttons`, `.tousled-header__*`, `.navtext`, `.collection-nav-*` — ~70 selectors
- Product cards: `.product-grid-item*`, `.product__card*`, `.discover-collection*` — ~60 selectors
- Layout helpers: `.align--*`, `.section--*`, `.hidden-pocket*` — ~50 selectors
- Sliders: `.banner-slider`, `.collection-slider`, `.cross-post-blogs`, `.swiper-*` overrides — ~50 selectors
- Forms / cart: `.cart-*`, `.input-group*`, `.search-bar-*` — ~40 selectors
- Branded sections: `.collection-branded*`, `.brand-*`, `.salon-*` — ~80 selectors
- Typography: `.h1--*` through `.h6--*`, `.font-*`, RTE selectors — ~80 selectors
- Modals / overlays: `.modal-*`, `.drawer-*`, `.popdown-*` — ~30 selectors
- Hover/focus interactions: `:hover`, `:focus` variants — ~120 selectors (counted)

| Classification | Per-cluster destination | Rationale |
|----------------|------------------------|-----------|
| **KEEP (port to theme.css)** | Buttons, layout helpers, typography, hover/focus interactions | Used globally; should live in the base stylesheet. Re-implement using P8's design-token system if available. |
| **KEEP (port to section stylesheet)** | Menu/nav, product cards, sliders, forms/cart, branded sections | Scoped to specific section types. Move into each section's `{% stylesheet %}` block per OS 2.0 best practice. |
| **DROP** | Modal/overlay styles for sweetalert2 (~10 selectors); `.lazyload` / `.lazy-image` / `.fade-in` opacity flip rules (~5 selectors); any IE9/legacy-browser hacks | These depend on assets we're dropping (sweetalert2, lazysizes). |

**Phase B implementation note**: don't try to migrate all 2,757 lines in one PR. Cluster-by-cluster ports are individually reviewable and reversible.

## Summary — Phase A.3 deliverable

| Asset | Total KB | DROP'd KB | KEPT KB (in bundle/section) | Net synchronous JS/CSS savings |
|-------|---------|-----------|-------|----------------------|
| custom-theme.js (~9,118 LoC / 445 KB) | 445 | ~177 (sticky-js + he + sweetalert2 + ssr-window + dom7) + ~210 (Swiper async-chunked, parsed only on slider pages) | ~58 (custom behaviors in P8 bundle) | **~387 KB off critical path** |
| shop.js (~134 KB) | 134 | ~134 (lodash + Modernizr + namespace stub) | 0 | **~134 KB off critical path** |
| jquery.min.js (~85 KB) | 85 | ~85 (drop entirely, conditional fallback) | 0 | **~85 KB off critical path** |
| lazysizes.js (~29 KB) | 29 | ~29 (replace with native `loading="lazy"`) | 0 | **~29 KB off critical path** |
| custom-theme.css (~75 KB) | 75 | ~5 (sweetalert2 + lazysizes related) | ~70 (cluster-ported to theme.css + per-section stylesheets) | minimal direct savings; CSS is already deferred |

**Grand total estimated savings**: ~635 KB of synchronous JS removed from the critical path. (Swiper's 210 KB stays in the codebase but moves to an async chunk that loads only on slider pages.)

## Open questions before Phase B starts

1. **shop.js callsite audit**: which snippets/sections actually invoke `_.map`, `_.filter`, `_.debounce`, etc., or `Modernizr.touch`? Need to grep before declaring lodash droppable. **File as bd 2i8b.B1.audit-lodash before Phase B.**
2. **jQuery TAE-app dependency check**: which TAE-loaded apps reference `window.$` or `window.jQuery` at runtime? **File as bd 2i8b.B1.audit-jquery before Phase B.**
3. **Swiper version target**: Swiper 11.x is tree-shakable to ~80 KB; current bundled version (4,296 LoC) is older Swiper 6.x/7.x. **Decide bundle version + module imports in Phase B.1.**
4. **lazysizes 77-callsite list**: needs an enumerated grep + classification (pattern 1/2/3) before Phase B. **File as bd 2i8b.B1.lazysizes-callsites.**

## Recommended next step

File the 3 audit follow-up bd tickets (lodash, jquery, lazysizes) as `2i8b.B1.*` and dispatch them as a Wave-A2 OC swarm. Each is a pure read+report task — zero blast radius.

Then proceed to Phase B.1 (bundle architecture decision) on CC Opus 4.7 / High.
