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