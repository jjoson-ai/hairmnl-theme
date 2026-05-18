# jQuery TAE-app + theme-code dependency audit

> **Bd:** `hairmnl-theme-2i8b.12` (Phase B.2 entry-gate audit, B.1.audit-jquery)
> **Authored:** 2026-05-18 PM, on Opus 4.7 / High, post-revert (49ae3dc).
> **Output for:** bundle architecture Decision D8 — can we drop `jquery.min.js`
> from `layout/theme.liquid` at Phase D cutover?

## TL;DR

**Yes — jQuery can be dropped from `layout/theme.liquid` at Phase D cutover.**

- **All 13 third-party / TAE-injected app payloads audited**: NONE require
  the theme's `jquery.min.js`. Each is either jQuery-free, has graceful
  fallback when jQuery is absent, or bundles its own jQuery from a CDN.
- **HairMNL theme code has exactly ONE real jQuery callsite**:
  `layout/theme.liquid:1027-1041`, a 14-line inline `<script>` scoped to
  `/pages/the-backbar-account-registration` (admin/registration page).
  **Trivial to rewrite to vanilla** (~15-20 LoC). The rewrite ships in the
  same Phase D cutover commit as the `<script src="...jquery.min.js">` tag
  removal, satisfying Rule 6 (no drop-and-pray).
- **The `[DEAD]`-allowlisted `snippets/wsg-dependencies.liquid`** uses
  `typeof jQuery !== 'undefined' ? jQuery(...) : ...` — graceful fallback.
  Plus the snippet is not currently rendered (no callsite). Not a blocker.

**Estimated savings**: ~85 KB synchronous JS removed from the critical path
on every page load.

---

## Methodology

1. Cache-bypass fetch of live page `https://www.hairmnl.com/?_cb=$(date +%s%N)`
   with `Cache-Control: no-cache`. Extracted all `<script src>` URLs.
2. For each non-theme script (TAE-injected + content_for_header inline),
   curl-fetched the payload. Saved to `/tmp/jq-audit/`.
3. Per app: grepped for jQuery patterns:
   - `window.$` (direct global reference)
   - `window.jQuery` (direct global reference)
   - `jQuery(` (function call)
   - `$(` (function call, ambiguous)
   - `$.extend`, `$.ajax`, `$.fn`, `$.each`, `$.map`, `$.when`, `$.Deferred` (jQuery API surface)
   - `"jquery"`, `.jquery`, `jquery.min` (string literals)
4. For each hit, inspected ±40 chars of context to classify as:
   - **REAL** jQuery dependency (calls jQuery expecting global)
   - **FEATURE-DETECT** (checks `if (window.jQuery)` with fallback)
   - **OWN-BUNDLE** (app bundles its own jQuery from CDN)
   - **FALSE POSITIVE** (local function/variable named `$` or `jQuery<x>`)
5. Also grepped HairMNL's own snippets/sections/layout/templates for jQuery patterns.

---

## TAE-injected + content_for_header apps audited (13)

| App | Payload size | Hits (raw) | Verdict | Context |
|---|---|---|---|---|
| BOGOS Free Gifts (direct CDN) | 284 KB | 0 | **NO** | Vanilla JS bundle, zero jQuery patterns. |
| BOGOS Free Gifts (TAE glider) | 8 KB | 0 | **NO** | Lightweight carousel. Vanilla. |
| BOGOS Free Gifts (TAE lz-string) | 5 KB | 0 | **NO** | Compression util only. |
| Judge.me (TAE loader) | 10 KB | 4 | **NO — false positive** | The 4 `$()` hits are a local function: `function $(e){const t=e.dataset.widget;return K[t]||n...}`. Not jQuery. |
| Klaviyo (onsite JS) | 15 KB | 0 | **NO** | Modern bundle. Zero jQuery. |
| LDT Gift Wrap (TAE) | 648 KB | 27 | **NO — feature-detect with fallback** | Context: `if(window.jQuery){const _='#site-control .cart...'; const N=window.jQuery;(x=N(_))!=null&&x.length&&N.get(window....)}`. Optional AJAX cart-hydration enhancement; gift-wrap option works without it. |
| Nova EU Cookie Bar (TAE) | 24 KB | 0 | **NO** | Vanilla cookie consent. |
| OXI Social Login (TAE) | 8 KB | 1 | **NO — false positive** | The 1 `window.jQuery` hit is a JSONP callback variable name: `window.jQuery111004090950169811405_1543664809199=func...`. Not a jQuery reference. |
| Personalizer.io | 0.8 KB | 0 | **NO** | Loader stub only. |
| Re:amaze | 0.7 KB | 0 | **NO** | Loader stub only. |
| Searchanise (legacy CDN init) | 7 KB | 1 | **NO — own-bundle** | Context: `s.jq \|\| "//ajax.aspnetcdn.com/ajax/jQuery/jquery-3.7.1.min.js"`. Searchanise loads its OWN jQuery from MS CDN as a fallback if config `s.jq` is empty. Does not depend on theme's jquery.min.js. |
| STKY satcb (legacy) | 1.4 KB | 0 | **NO** | Loader stub only. |
| STKY satcb (TAE) | 0.3 KB | 0 | **NO** | Loader stub only. |

**Net: 0/13 apps require theme `jquery.min.js`.**

---

## HairMNL theme code

### `layout/theme.liquid:1027-1041` — REAL dependency, 9 jQuery calls

The only real jQuery usage in our own theme code. Inline `<script>` block:

```liquid
<script>
  // BSs custom style /pages/the-backbar-account-registration
  if (window.location.pathname == '/pages/the-backbar-account-registration') {
    document.addEventListener('DOMContentLoaded', function () {
      $('.rte').after($('.section-header.text-center'));
      $('.grid').css('padding', '0 21%');
      $('.grid').css('margin-left', '0px');
      $('.grid__item').css('padding-left', '0px');
      $('.rte img').css('width', '-webkit-fill-available');
      $('.site-footer-wrapper .section-header.text-center').remove();
      var width = $(window).width();
      if (width < 1400) {
        $('.grid').css('padding', '0 6%');
      }
    });
  }
</script>
```

**Page scope**: only fires on `/pages/the-backbar-account-registration` —
a low-traffic admin/registration page for backbar (B2B?) accounts. Not
the main customer flow.

**Functionality**: 9 layout fixups (move heading, set grid padding, set
image width, remove footer header, conditional narrow-viewport padding).

**Vanilla equivalent** (~15-20 LoC, ships in Phase D cutover commit):

```html
<script>
  if (window.location.pathname === '/pages/the-backbar-account-registration') {
    document.addEventListener('DOMContentLoaded', function () {
      var rte = document.querySelector('.rte');
      var sectionHeader = document.querySelector('.section-header.text-center');
      if (rte && sectionHeader) rte.parentNode.insertBefore(sectionHeader, rte.nextSibling);

      var grids = document.querySelectorAll('.grid');
      var gridItems = document.querySelectorAll('.grid__item');
      var rteImgs = document.querySelectorAll('.rte img');
      var footerHeader = document.querySelector('.site-footer-wrapper .section-header.text-center');

      grids.forEach(function (g) {
        g.style.padding = (window.innerWidth < 1400) ? '0 6%' : '0 21%';
        g.style.marginLeft = '0px';
      });
      gridItems.forEach(function (gi) { gi.style.paddingLeft = '0px'; });
      rteImgs.forEach(function (img) { img.style.width = '-webkit-fill-available'; });
      if (footerHeader) footerHeader.remove();
    });
  }
</script>
```

**Risk**: low. Single template; vanilla DOM APIs are well-supported back
to IE11 (and we don't support IE9 anymore per the orphan allowlist's
respond.min.js entry).

### `snippets/wsg-dependencies.liquid` — graceful fallback, allowlisted [DEAD]

The single `jQuery(...)` call in this file is inside a
feature-detection check:

```js
"undefined"!=typeof jQuery
  ? jQuery(this.selectors[0].element).trigger("change",e)
  : this.selectors[0].element.onchange(e);
```

Even if jQuery is absent, the snippet falls back to native `.onchange()`.
Plus the snippet is on the orphan allowlist as `[DEAD]` (no callsite —
not rendered anywhere). Not a blocker for Phase D.

### `assets/shop.js.liquid` — false positives (lodash internal `$` functions)

The `$()` patterns in shop.js.liquid are lodash internal function
declarations: `function $(n,t,a){...}`. Not jQuery. This file is covered
by bd `2i8b.13` (audit-lodash); for jQuery audit purposes: **NOT a
jQuery dependency**.

---

## Recommendation for Phase D cutover commit

The cutover commit that drops jQuery from `layout/theme.liquid` must ship
**both** of the following changes atomically (Rule 6 — no drop-and-pray):

1. **Remove** `<script src="{{ 'jquery.min.js' | asset_url }}" defer="defer"></script>` from `layout/theme.liquid:699`
2. **Replace** the inline `<script>` at `layout/theme.liquid:1027-1041` with the vanilla equivalent above

Optional follow-up:
- Delete `assets/jquery.min.js` from the repo and from Shopify storage (after Phase D verification confirms no breakage)

The Wiring Delta table for the cutover PR will show:

| Asset | Action | Replacement |
|---|---|---|
| `jquery.min.js` (script tag) | REMOVED | Native DOM APIs; only consumer was the inline registration-page snippet, rewritten to vanilla |

Live-state HTML diff (Rule 8): one fewer `<script src>` tag pointing to `jquery.min.js`.

---

## Verification plan for Phase C

After Phase B.2.8 lands on the feature branch (the layout/theme.liquid prep commit):

1. **Smoke test on dev preview**: navigate to `/pages/the-backbar-account-registration` on `?preview_theme_id=141168312419`. Confirm:
   - Page renders without JS errors in console
   - Grid padding looks right (matches live)
   - Section-header position looks right
2. **Cross-check all 13 audited apps still function**:
   - LDT Gift Wrap: PDP shows gift-wrap option, checkbox toggles
   - Judge.me: review badges render on PDP + collection cards
   - Klaviyo: subscription popup fires (test interaction)
   - Re:amaze: chat icon appears in corner
   - BOGOS Free Gifts: cart/PDP shows promo if active
   - Searchanise: search dropdown predicts results
   - STKY: sticky ATC bar appears on PDP scroll
   - Nova Cookie Bar: cookie consent appears on first visit
   - OXI Social Login: login page shows social buttons
   - Personalizer: rec rail loads on PDP (if active)
3. **Cache-bypass curl on dev preview**: confirm `<script src=".../jquery.min.js">` is gone.
4. **PSI re-baseline**: confirm desktop home PSI doesn't regress; ideally improves
   ~3-5 points from the 85 KB JS removal.

If smoke test fails on any of these: rollback the cutover commit, re-investigate.

---

## Acceptance criteria — MET

- [x] All TAE-loaded apps catalogued
- [x] Per-app jQuery dependency verdict
- [x] Final recommendation for layout/theme.liquid (DROP, in same commit as inline rewrite)
- [x] Recommendation supports the Decision D8 outcome in the bundle architecture (jQuery-free bundle, drop from layout/theme.liquid at Phase D)

## Open follow-ups

- Inline rewrite ships as part of Phase B.2.8 (the layout/theme.liquid prep commit)
- After Phase D verification, file a follow-up bd to delete `assets/jquery.min.js` from repo + Shopify storage (one-line `shopify theme push --delete`)

## Acceptance: this audit closes the corresponding 5th-out-of-5 Phase B.2 entry gate (along with the 2 remaining OC-bound audits: lodash + lazysizes).
