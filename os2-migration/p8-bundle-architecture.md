# P8 bundled `hairmnl-custom.js` — architecture decision

> **Bead:** `2i8b.B1` (Phase B.1 of `os2-migration/p8-cutover-checklist.md`)
> **Authored:** 2026-05-18 PM, on Opus 4.7 / High after Phase A complete (`9f34026`).
> **Status:** DRAFT — operator review required before Phase B.2 (implementation) can begin.
> **Reverses?** Yes — file-level only. No live impact until Phase D cutover.

This document captures the irreversible architecture decisions for the
P8 bundled JavaScript — the replacement for `custom-theme.js` (445 KB)
+ `shop.js` (134 KB) + `jquery.min.js` (85 KB) + `lazysizes.js` (29 KB)
on live. Phase A.3 inventoried what each legacy file does and classified
each behavior **KEEP / TAE / DROP**. This doc decides *how* the KEEP
behaviors are implemented.

---

## Context — what we're building

Per Phase A.3 (`os2-migration/custom-theme-js-audit.md`):

- **9 KEEP behaviors** (~580 LoC of hand-written vanilla JS) need to land
  in a P8 bundle: sticky-filter-bar (CSS-only — see decision 6),
  product-tabs-v1, cross-post-blogs, hover-line, header-mobile-sliderule,
  lion-points, banner-slider, collection-slider, domparser, consent-modal.
- **5 vendor libs DROP** entirely: sticky-js, he, sweetalert2, ssr-window,
  dom7.
- **1 vendor lib (Swiper)** stays in the codebase but loads as an
  **async chunk** triggered by DOM presence of slider selectors.
- **lodash + Modernizr + jQuery + lazysizes** are all DROP (with
  conditional fallbacks where TAE-app dependencies require it; audit
  follow-ups `2i8b.B1.audit-lodash`, `2i8b.B1.audit-jquery`,
  `2i8b.B1.lazysizes-callsites` resolve those).

Estimated total: ~660 LoC of hand-written vanilla JS in the main bundle,
plus a separate Swiper chunk of ~80 KB minified.

---

## Decisions

### Decision 1 — Target file: extend `assets/hairmnl-custom.js`

The file already exists at `assets/hairmnl-custom.js` (currently
[P8-PENDING] in `intentionally-orphan-assets.txt` — not loaded on live).
It has 7 sections in place (1: sticky-filter-bar JS legacy, 2:
product-tabs-v1, 3: header-mobile-sliderule, 4: lion-points, 5:
domparser, 6: hover-line, 7: cart-drawer-on-atc v2). Continuing this
file is the cheapest path:

- No new file means no new entry in the wiring lint, the orphan asset
  list, or `layout/theme.liquid`'s loader sequence — just one entry to
  flip from `[P8-PENDING]` to wired when Phase D ships.
- The single-file IIFE-with-numbered-sections pattern is already
  established by Opus 4.7 in the P4 spike (commit `64b034f`,
  "6-8x scope reduction"). Don't break a known-good pattern.

**REJECTED**: extending `assets/theme.js` (the P8 stock bundle) —
prohibited by project CLAUDE.md hard rule. **REJECTED**: starting a
new file (`assets/hairmnl-theme.js` etc.) — would discard the 7 already-
ported sections.

### Decision 2 — Build pipeline: no bundler, vanilla single-file IIFE

Continue the existing pattern: one `assets/hairmnl-custom.js`, IIFE
wrapper, numbered behavior sections inside. Each section is its own
inner IIFE so a runtime error in one doesn't poison the others.

Rationale:
- The codebase has no existing build pipeline. Adding esbuild/rollup
  introduces a `node_modules`, lockfile, CI step, and a "did you rebuild
  before pushing?" failure mode.
- The bundle target is ~30 KB minified (~660 LoC of vanilla JS).
  Tree-shaking saves nothing meaningful at this scale.
- Shopify Liquid `asset_url` handles cache-busting — we don't need a
  bundler-generated hash.

**REJECTED**: esbuild — adds a build step for marginal benefit at this
size. **REJECTED**: rollup — same. **REJECTED**: plain ES modules via
`<script type="module">` — Shopify CDN technically supports it but the
`asset_url` cache-busting on imported modules is brittle in practice.

Trade-off accepted: no minification. P8 stock `theme.js` already
loads ~440 KB minified; our +30 KB unminified hand-written code is
within noise.

### Decision 3 — Module structure: numbered sections, one IIFE each

Existing pattern (sections 1–7) continues:

```js
/*
 * HairMNL custom theme JS — Pipeline 8 add-on
 * Single-file vanilla JS bundle. No build step. Loaded after theme.js
 * with defer. Each section is an inner IIFE so a runtime error in one
 * doesn't poison the others.
 */
(function () {
  'use strict';

  // 1) sticky-filter-bar — handled by CSS only (decision 6). This
  //    section reserved for backward-compat only.

  // 2) product-tabs-v1 — tab switching on PDPs.
  (function () { /* ... */ })();

  // 3) header-mobile-sliderule — mobile nav slide-rule pattern.
  (function () { /* ... */ })();

  // ... etc, up to 11.

  // 12) swiper-chunk-loader — lazy-loads Swiper from a separate asset
  //     when any of `.swiper.collection`, `.banner-slider .swiper`, or
  //     `.cross-post-blogs .swiper-container` exists in DOM.
  (function () { /* ... */ })();
})();
```

Each section's first line is a guard: `var el = document.querySelector(SELECTOR); if (!el) return;` — so behavior parses but doesn't execute on templates where its DOM doesn't exist.

**REJECTED**: ES modules with `import` — see Decision 2. **REJECTED**:
class syntax per section — vanilla function + closure is sufficient
and reads consistently with sections 1–7.

### Decision 4 — Swiper async-chunk strategy: vendored, dynamically loaded

Vendor Swiper 11.x as `assets/swiper-bundle.min.js` (downloaded once
from npm/CDN, committed to the repo). The main `hairmnl-custom.js`
detects slider selectors and injects a `<script>` tag pointing to
`{{ 'swiper-bundle.min.js' | asset_url }}` only when needed:

```js
// Section 12 — swiper-chunk-loader
(function () {
  var hasSlider = document.querySelector(
    '.swiper.collection, .banner-slider .swiper, .cross-post-blogs .swiper-container'
  );
  if (!hasSlider) return;
  var s = document.createElement('script');
  s.src = window.theme.swiperBundleUrl;  // set in layout/theme.liquid inline
  s.defer = true;
  s.onload = function () {
    document.dispatchEvent(new CustomEvent('theme:swiper:ready'));
  };
  document.head.appendChild(s);
})();
```

Sections 8 (cross-post-blogs), 9 (banner-slider), 10 (collection-slider)
listen for `theme:swiper:ready` before initializing.

Trade-off accepted: extra HTTP request on slider pages. But the request
is `defer` and runs after first paint; the perf win (no Swiper on cart,
account, search-no-results pages) is substantial.

`window.theme.swiperBundleUrl` is set inline in `layout/theme.liquid` via:
```liquid
<script>window.theme = window.theme || {}; window.theme.swiperBundleUrl = "{{ 'swiper-bundle.min.js' | asset_url }}";</script>
```
This is the only `layout/theme.liquid` touch needed (single small additive line — Rule 8 cache-bypass diff will show one new `<script>` tag added).

**REJECTED**: CDN-served Swiper (e.g., `cdn.skypack.dev/swiper@11`) —
third-party dependency, no version lock, no offline dev. **REJECTED**:
bundling Swiper into `hairmnl-custom.js` — defeats the async-chunking
benefit.

### Decision 5 — Budget: 30 KB hand-written + 80 KB Swiper async

| Component | Target size | Notes |
|---|---|---|
| `hairmnl-custom.js` (main bundle) | ≤ 35 KB unminified, ≤ 15 KB gzipped | ~660 LoC of vanilla JS; no minification |
| `swiper-bundle.min.js` (async chunk) | ≤ 90 KB minified, ≤ 30 KB gzipped | Swiper 11 + Navigation + Pagination + Autoplay; tree-shaken at vendor build |
| **Combined critical-path JS** | **~15 KB gzipped, deferred** | Swiper not on critical path |
| **Net vs current custom-theme.js** | **−330 KB minified** | (current: 445 KB; new main: 15 KB gzip; async chunk loads only on slider pages) |

This easily clears the checklist's "≤ 120 KB minified" target.

### Decision 6 — `sticky-filter-bar` ports as CSS-only (no JS)

The legacy `sticky-filter-bar` (sticky-js, ~344 LoC) becomes a single
CSS rule in `snippets/css-overrides.liquid`:

```css
@media (max-width: 600px) {
  .collection__nav {
    position: sticky;
    top: var(--menu-height, 0);
    z-index: 10;
    background: var(--color-body-bg);
  }
}
```

No JavaScript needed. Section 1 of `hairmnl-custom.js` is kept as a
documentation comment but contains no code. Saves ~344 LoC of sticky-js
vendor + ~34 LoC of behavior bootstrap.

### Decision 7 — `consent-modal` uses native `<dialog>` element

Replace SweetAlert2 (2,631 LoC) with native `<dialog>`. Estimated
~30 LoC vanilla JS + ~40 LoC CSS in `snippets/css-overrides.liquid`.
Lives in section 11 of `hairmnl-custom.js`.

```js
// Section 11 — consent-modal (cart only)
(function () {
  var cartForm = document.querySelector('form.cart');
  if (!cartForm) return;
  var hasConsentItem = !!document.querySelector('.cart__items__row[data-with-consent]');
  if (!hasConsentItem) return;
  // ... create + insert <dialog>, wire submit handler
})();
```

Saves ~2,631 LoC of SweetAlert2 + ~241 LoC of `he` HTML entities
dependency + ~123 LoC of legacy modal wiring.

### Decision 8 — jQuery removal: drop from bundle, defer to audit for layout/theme.liquid

The bundle does **not** import or depend on jQuery. Whether
`{{ 'jquery.min.js' | asset_url }}` stays in `layout/theme.liquid`
is decided by bd `2i8b.B1.audit-jquery` (audit of TAE-loaded apps that
reference `window.$` at runtime):

- **If audit finds no app dependency**: drop jQuery `<script>` from
  `layout/theme.liquid` in the same Phase D cutover commit.
- **If audit finds dependencies**: keep the jQuery `<script>` loaded
  (defer), file a follow-up bd per app to remove its dependency, and
  drop jQuery in a future P8.1 cutover.

Either way, the bundle is jQuery-free from day one.

### Decision 9 — lazysizes removal: drop from bundle, callsites are P2 follow-up

The bundle does not implement lazy-loading. All 77 callsites
(per `2i8b.B1.lazysizes-callsites` enumeration) get migrated to
native `loading="lazy"` as a separate P2 ticket. **lazysizes can be
dropped from `layout/theme.liquid` only after that migration ships.**

In the meantime: bundle is lazysizes-free; the legacy `lazysizes.js`
script tag stays in `layout/theme.liquid` until callsite migration is
complete. Decoupled from cutover gate.

### Decision 10 — shop.js removal: drop from bundle, lodash usage is P2 follow-up

Same pattern as lazysizes. Bundle doesn't import lodash. The legacy
`shop.js` script tag stays in `layout/theme.liquid` until the
`2i8b.B1.audit-lodash` callsite migration is complete.

---

## The worked example: `hover-line` (decision-3 pattern in practice)

Section 6 of the current `assets/hairmnl-custom.js` (lines 211–340)
already implements the pattern. Reproduced here as the canonical
template for sections 8–11:

```js
// ============================================================
// 6) hover-line — TousledHoverLine animated underline (M5 port)
// ----------------------------------------------------------------
// Pure DOM + CSS-variable manipulation. No vendor deps. Preserves
// the INP-fix discipline from the P6 version (batch reads before
// writes; geometry reads kept separate from setProperty calls).
// ============================================================
(function () {
  var SEL = {
    item: '[data-main-menu-text-item]',
    text: '.navtext',
    isActive: 'data-menu-active',
    sectionOuter: '[data-tousled-header-wrapper]',
    underlineCurrent: 'data-underline-current',
    defaultItem: '.menu__item.main-menu--active .navtext, .header__desktop__button.main-menu--active .navtext',
  };
  var defaultPositions = null;

  var TousledHoverLine = function (el) {
    this.wrapper = el;
    this.itemList = this.wrapper.querySelectorAll(SEL.item);
    this.sectionOuter = document.querySelector(SEL.sectionOuter);
    if (!this.sectionOuter) return;
    // ... constructor continues
    document.fonts.ready.then(this._init.bind(this));
  };

  TousledHoverLine.prototype._init = function () { /* ... */ };
  TousledHoverLine.prototype._measure = function () { /* ... */ };
  // ... more prototype methods

  // Bootstrap
  var container = document.querySelector('[data-tousled-header-wrapper]');
  if (container) {
    var el = container.querySelector('[data-links-wrapper]');
    if (el) new TousledHoverLine(el);
  }
})();
```

Pattern elements every section follows:
1. **Outer IIFE** — isolates this behavior's variables from sibling sections.
2. **`SEL` constant** — all CSS selectors at the top, easy to audit/grep.
3. **Constructor + prototype methods** — vanilla, no classes (keeps
   pattern consistent with sections 3, 6, 7 already there).
4. **DOM-presence guard** at the bootstrap line — `if (el) new Behavior(el)`.
   Behavior parses but doesn't execute on templates where DOM is absent.
5. **No globals** — nothing escapes the inner IIFE except event listeners.
6. **Layout-thrash awareness** — geometry reads (`offsetLeft`, `clientWidth`)
   batched before any writes (`setProperty`, `setAttribute`). Existing
   comments call this out where it matters.

For sections 8–10 (the Swiper-using behaviors), the bootstrap waits on
the `theme:swiper:ready` event instead of executing immediately:

```js
// Section 8 — cross-post-blogs (Swiper-using)
(function () {
  var container = document.querySelector('.cross-post-blogs');
  if (!container) return;
  // Wait for Swiper chunk to load (Section 12 dispatches the event)
  if (window.Swiper) {
    init();
  } else {
    document.addEventListener('theme:swiper:ready', init, { once: true });
  }
  function init () { /* IO-deferred Swiper construction */ }
})();
```

---

## Implementation order — Phase B.2 sub-tickets

Filed as children of `2i8b.B2`. Each is a separate small commit, each
runs the wiring lint + Rule 8 cache-bypass HTML diff before close. **All
work happens on feature branch `claude/p8-port-v2`, not main**, per R3.

| Order | Sub-ticket | Section | LoC est. | Model/effort | CC or OC? |
|---|---|---|---|---|---|
| 1 | `2i8b.B2.1` Set up feature branch + bundle scaffolding | 1, 12 setup | ~20 | Opus 4.7 / Medium | **CC** |
| 2 | `2i8b.B2.2` Section 8 — cross-post-blogs | 8 | ~98 | Opus 4.7 / Medium | **CC** (worked example for OC to follow) |
| 3 | `2i8b.B2.3` Section 9 — banner-slider | 9 | ~22 | Sonnet 4.6 / Medium | **OC** (replicates B2.2 pattern) |
| 4 | `2i8b.B2.4` Section 10 — collection-slider | 10 | ~98 | Sonnet 4.6 / Medium | **OC** |
| 5 | `2i8b.B2.5` Section 11 — consent-modal (native dialog) | 11 + CSS | ~70 | Opus 4.7 / Medium | **CC** (replaces sweetalert2; risk of dialog API edge cases) |
| 6 | `2i8b.B2.6` Vendor Swiper 11 bundle + wire chunk-loader | swiper-bundle.min.js + section 12 | ~30 | Opus 4.7 / Medium | **CC** (vendoring decisions) |
| 7 | `2i8b.B2.7` sticky-filter-bar CSS rule | css-overrides.liquid | ~10 | Sonnet 4.6 / Low | **OC** |
| 8 | `2i8b.B2.8` Bundle Liquid: add `swiperBundleUrl` inline + load `hairmnl-custom.js` from layout/theme.liquid | `layout/theme.liquid` | ~5 lines | **Opus 4.7 / High** | **CC ONLY** — Rule 8 / Rule 5 verify mandatory |

Sub-tickets 1–7 do NOT touch `layout/theme.liquid`. Only 8 does, and
it is the explicit cutover prep commit — fully reviewable, single
Wiring Delta table, cache-bypass verify after dev push.

---

## What this doc does NOT decide (deferred)

- **Migrating the 77 lazysizes callsites** — separate P2 ticket. Doesn't
  block Phase B bundle work.
- **Migrating the lodash callsites in snippets** — same.
- **Custom-theme.css cluster-port** — separate P2-P3 stream of work,
  parallel to Phase B but not blocking. The bundle doesn't depend on
  the CSS port.
- **TAE app migrations (ujg6.15)** — independent admin work, no
  bundle dependency.
- **The 5 KB of custom-theme.css "DROP" rules** (sweetalert2 + lazysizes-
  related selectors) — folds into Phase B.2.5's CSS additions.

---

## Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| TAE app references `window.$` at runtime → drops jQuery breaks app | Medium | Audit `2i8b.B1.audit-jquery` precedes Phase D. Conditional keep if dependencies found. |
| Swiper async-chunk timing breaks slider on slow connections | Low | `theme:swiper:ready` event ensures init waits for chunk load. Slider DOM is present from server-render; only the JS init is async. |
| `<dialog>` element compat with old Safari (< 15.4) | Low | Polyfill at ~3 KB if needed; or accept fallback to inline form for ancient browsers. Audit current visitor browser-share before Phase D. |
| Bundle exceeds 35 KB target | Low | Re-audit; trim less-critical behaviors (lion-points could move to a microtask deferred until interaction). |
| Cache-shadow class regression (2026-05-18 PM repeat) | **MITIGATED** | All Phase D pushes follow Rules 5/7/8 cache-bypass verify and pre-flight pull. Hook + CI enforce. |
| Bundle parses but doesn't execute correctly on some template | Medium | Phase C template-by-template smoke test covers home, PDP, collection, cart, blog, search, account, brand. |

---

## Phase B.2 entry criteria (checklist update)

Before starting B.2.1:
- [ ] Operator reviews this doc and ticks **Decision 1 through Decision 10**.
- [ ] `2i8b.B1.audit-jquery` (CC) returns: jQuery dependency status known.
- [ ] `2i8b.B1.audit-lodash` (OC paid) returns: lodash callsite list known.
- [ ] `2i8b.B1.lazysizes-callsites` (OC paid) returns: 77-callsite migration list known.
- [ ] Feature branch `claude/p8-port-v2` cut from `main` at the post-revert baseline.
- [ ] `p8-cutover-checklist.md` Phase B.1 section ticks the architecture-doc box.

Once all five are checked: `2i8b.B2.1` starts on the feature branch.

---

## Open questions for operator

1. **Bundle file naming**: confirm `assets/hairmnl-custom.js` is the
   right target (vs renaming to `assets/hairmnl-theme.js` or similar).
   Default per this doc: **keep `hairmnl-custom.js`**.
2. **Swiper version**: target Swiper 11.1.x (latest stable as of writing).
   Confirm or pin to a specific minor.
3. **CSS bundle ownership**: the 2,757-line `custom-theme.css` port is a
   separate stream. Phase B bundle work doesn't wait on it — but the
   Phase D cutover commit will drop the legacy `custom-theme.css`
   stylesheet tag from `layout/theme.liquid` only after CSS port lands.
   Confirm sequencing.
4. **Dialog polyfill decision**: include or accept fallback for Safari
   < 15.4? Audit browser share before Phase D.

---

## Status

DRAFT pending operator review. Phase B.1 checkbox in
`p8-cutover-checklist.md` opens once operator confirms decisions.
