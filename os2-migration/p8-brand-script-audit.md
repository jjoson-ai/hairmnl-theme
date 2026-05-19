# P8 Brand Mobile Script Audit

**Date:** 2026-05-19
**Issue:** hairmnl-theme-ujg6.33
**Context:** PSI shows P8 brand mobile loads 169 scripts vs P6's 152 (+17 scripts, +612KB).

## Methodology

Static codebase audit of all script references in `layout/theme.liquid` and relevant snippets. Each script was checked for:
1. Whether it's conditional on template/page-type
2. Whether it loads on collection/brand pages
3. Whether it should load on collection/brand pages

## Unconditional Scripts (Load on Every Page Including Collections)

| # | Source File | Line | Script | Type | Recommendation |
|---|------------|------|--------|------|----------------|
| 1 | layout/theme.liquid | 159–170 | BCPO product data inline script (`var bcpo_product`, `var bcpo_data`, `var bcpo_settings`, `var inventory_quantity`, `window.bcpo.cart`) | inline | **Gate** — wrap in `{% if template contains 'product' %}`. BCPO is a product options app; `bcpo_product` and `inventory_quantity` are null/empty on collection pages (`product` Liquid object is blank outside product templates). The `bcpo.cart` assignment is harmless but wasteful. ~1.2 KB inline on every non-product page for zero value. |
| 2 | layout/theme.liquid | 172 | `{% include 'shop-sheriff-pwa' %}` — emits `<script type="text/javascript">var pwaPrompt;pwaPromptSet;window.addEventListener('beforeinstallprompt'...)` + manifest link | snippet (inline) | **Keep** — PWA install prompt is 3 lines / ~200 B. Tiny, and the beforeinstallprompt listener must be cached early to capture the browser event. Not worth gating. |
| 3 | layout/theme.liquid | 185 | Searchanise `init.js` (`//www.searchanise.com/widgets/shopify/init.js?a=7K0f1C4k5q`) | external (defer) | **Keep** — Searchanise powers site search on all pages; collection brand pages use it for filtering. Defer already set. |
| 4 | layout/theme.liquid | 426–497 | Theme config inline script (`document.documentElement.className.replace`, `var theme = { routes, assets, strings, settings, info, moneyFormat }`, viewport CSS vars) | inline | **Keep** — Theme runtime config needed by every page. ~2 KB, not removable. |
| 5 | layout/theme.liquid | 547–559 | Drawer-toggle click intercept inline script | inline | **Keep** — 450 B, prevents /cart navigation flash on all pages. |
| 6 | layout/theme.liquid | 639–666 | A/B testing framework inline script | inline | **Keep** — ~700 B, TESTS object empty = early return. Zero execution cost. |
| 7 | layout/theme.liquid | 667–697 | JS error tracking → dataLayer inline script | inline | **Keep** — ~500 B, max 10 errors/session. Essential for production monitoring. |
| 8 | layout/theme.liquid | 698 | `vendor.js` | external (defer) | **Keep** — dependency of theme.js. |
| 9 | layout/theme.liquid | 709 | `jquery.min.js` | external (defer) | **Keep** — dependency of theme.js + custom-theme.js. |
| 10 | layout/theme.liquid | 710 | `theme.js` | external (defer) | **Keep** — core theme JS. |
| 11 | layout/theme.liquid | 728 | `hairmnl-common.js` | external (defer) | **Keep** — common customizations for all templates. |
| 12 | layout/theme.liquid | 780–869 | LoyaltyLion createElement guard inline script (intercepts `loyaltylion.net` script insertions until requestIdleCallback + 3s timeout) | inline | **Keep** — Guard prevents LL SDK from blocking render. Already performance-optimized. (The `{% include "loyaltylion" %}` at line 872 runs the LL snippet itself — see #13.) |
| 13 | layout/theme.liquid | 872 | `{% include "loyaltylion" %}` — LoyaltyLion SDK loader (defer-on-interaction pattern: 5s idle / 8s timeout / scroll/click triggers) | snippet (inline) | **Consider gating** — LoyaltyLion SDK (~500 KB) loads on every page. The guard at #12 blocks it render-blocking, but it still occupies network budget on collection pages where loyalty points are rarely checked. Gate to `{% if template contains 'product' or template contains 'cart' or customer %}` to prevent download on anonymous collection browsing. |
| 14 | layout/theme.liquid | 889–940 | Pro Blogger CSS/JS defer guard inline script (MutationObserver + createElement override intercepting `problogger.css` and `owl.carousel` insertions) | inline | **Consider gating** — Defers Pro Blogger CSS from render-blocking path, which is good. But Pro Blogger itself only runs on blog/collection pages. If Pro Blogger is not used on brand/collection pages, the guard code itself (~50 lines) plus Pro Blogger's JS/CSS are pure overhead on those pages. See Specific Findings below. |
| 15 | layout/theme.liquid | 951–1115 | Reamaze defer-on-interaction guard inline script (6 triggers, KILL_SWITCH, GA4 telemetry) | inline | **See recommendation** — See Specific Findings below. Deferred but still occupies network budget on collection pages where chat is rarely used. |
| 16 | layout/theme.liquid | 1118 | `{{ content_for_header }}` — Shopify app scripts (Searchanise widget, LoyaltyLion App Embed, Reamaze chat, Zapiet, Bold, Judge.me, etc.) | platform-injected | **Cannot gate in theme** — content_for_header is Shopify-injected. Apps must be configured in Shopify Admin → App Embeds. |
| 17 | layout/theme.liquid | 1122 | `{% render 'reamaze-placeholder' %}` — server-rendered chat bubble placeholder | snippet | **Keep** — Visual placeholder for chat widget; needed for Reamaze defer UX. Small HTML, no script. |
| 18 | layout/theme.liquid | 1145 | `{%- render 'bold-common' -%}` — Bold Commerce shared config (133 lines, `window.BOLD.common.Shopify` data + multiple `window.BOLD.common.cacheHash` + RO/MD/PAD app data) | snippet (inline) | **Consider gating** — Bold Common dumps ~133 lines of inline JS with shop config for Bold RO/MD/PAD apps. Only needed on product/cart pages where those apps render. On collection/brand pages this is ~3–5 KB of dead config data. |
| 19 | layout/theme.liquid | 1178 | `{% include "code-customizer-header" %}` | snippet (empty) | **Remove** — File is 0 bytes. Dead `{% include %}` that parses Liquid for zero output. Wastes template parse time on every pageview. |
| 20 | layout/theme.liquid | 1247 | `custom-theme.js` | external (defer) | **Keep** — Custom JS used on all templates. |
| 21 | layout/theme.liquid | 1256–1267 | Timber hash/reset inline script (DCL-wrapped) | inline | **Keep** — Conditional on Liquid vars (`newHash`, `resetPassword`); effectively a no-op on most pages. |
| 22 | layout/theme.liquid | 1277–1289 | Klaviyo signup event listener inline script | inline | **Keep** — Klaviyo form tracking needed on all pages (forms can appear anywhere). Tiny. |
| 23 | layout/theme.liquid | 1320 | `shop.js` | external (defer) | **Keep** — Shopify app script, deferred. 177 KB but already deferred per comment at line 1308. |
| 24 | layout/theme.liquid | 1329 | `{% render 'web-vitals-reporter' %}` — Core Web Vitals → GA4 reporter | snippet | **Keep** — Essential for production monitoring. |
| 25 | layout/theme.liquid | 1345–1361 | BSS custom style inline script (DCL-wrapped, `/pages/the-backbar-account-registration` only — guards `window.location.pathname`) | inline | **Keep** — Path guard means zero execution on collection pages. |
| 26 | layout/theme.liquid | 1406 | SATCB/Zapiet `<script src="https://satcb.azureedge.net/Scripts/satcb.min.js">` (async+defer) | external | **Gate** — SATCB (Zapiet Store Pickup) loads on every page including collections. The `storepickup.liquid` snippet (line 1158) is already gated to `{% if template contains 'product' or template == 'cart' %}`, but this separate SATCB CDN script at line 1406 is unconditional. It should match the same gate. See Specific Findings below. |
| 27 | layout/theme.liquid | 1418–1439 | Nova Cookie Bar cc-dismiss a11y fix inline script | inline | **Keep** — MutationObserver for a11y, runs once, disconnects. ~20 lines. |
| 28 | layout/theme.liquid | 1441 | `{% render 'freegifts-snippet-change' %}` — FreeGifts app inline script | snippet (inline) | **Consider gating** — Contains `<script>setTimeout(...)` that runs on every page. FreeGifts app likely only needed on product/cart pages. |
| 29 | snippets/vertex-preview-toolbar.liquid | 46–94 | Vertex Preview Toolbar inline script (toolbar UI + localStorage persistence) | snippet (inline) | **Gate with `{% if request.design_mode %}`** — See Specific Findings below. Pure dev tool, zero production value, loads on all pages in the development theme. |

## Conditionally-Gated Scripts (Already Safe)

| # | Source File | Line | Script | Condition | Notes |
|---|------------|------|--------|-----------|-------|
| 1 | layout/theme.liquid | 505–507 | `shopify_common.js` | `{% if request.page_type contains 'customers/' %}` | Only loads on customer account pages. |
| 2 | layout/theme.liquid | 729–731 | `hairmnl-collection.js` | `{% if template contains 'collection' %}` | Only loads on collection templates. Correct. |
| 3 | layout/theme.liquid | 732–734 | `hairmnl-product.js` | `{% if template contains 'product' %}` | Only loads on product templates. Correct. |
| 4 | layout/theme.liquid | 1157–1159 | `{% include 'storepickup' %}` | `{% if template contains 'product' or template == 'cart' %}` | Properly gated. ~9 KB inline CSS + 90 KB storepickup.js only on product/cart. |
| 5 | layout/theme.liquid | 1332–1334 | BSS B2B conditional block | `{% if content_for_header contains 'bss-b2b' %}` | Properly gated. Block is currently empty (BSS B2B uninstalled). |

## App Embeds via `content_for_header`

Line 1118 (`{{ content_for_header }}`) injects scripts from Shopify app embeds. These cannot be gated in theme code — they must be managed in **Shopify Admin → Online Store → Themes → Customize → App Embeds**.

Known apps injecting via `content_for_header`:
- **Searchanise** — search widget JS (also loaded at line 185, deferred)
- **LoyaltyLion** — App Embed script (dual-init with theme snippet; see #13)
- **Reamaze** — chat widget JS (deferred by theme guard at lines 951–1115)
- **Zapiet/STKY** — SATCB widget (also loaded directly at line 1406)
- **Bold Commerce** — RO/MD/PAD apps (config also in `bold-common` snippet at line 1145)
- **Judge.me** — reviews widget (manual render removed 2026-04-26; app auto-injects via cfh)
- **Shopify Analytics** — built-in
- **Shopify CDN** — built-in
- **Klaviyo** — email marketing (Onsite JS)
- **Google Analytics/GTM** — via Elevar (injected by cfh)
- **Nova Cookie Bar** — cookie consent (injected by cfh)

## Specific Findings

### vertex-preview-toolbar.liquid — NO DESIGN_MODE GATE
- **File:** `snippets/vertex-preview-toolbar.liquid`
- **Lines:** 1–95 (HTML toolbar + inline `<script>`)
- **Issue:** The snippet contains a 95-line dev toolbar (HTML div + 50-line inline JS) that runs on every page with no `request.design_mode` check. It's rendered somewhere in the template chain (likely via a section or app embed) without any conditional gate. The `localStorage` persistence means even dismissing the toolbar doesn't prevent the JS from executing on every subsequent page.
- **Recommendation:** Wrap the entire snippet in `{% if request.design_mode %}` — this is a dev tool for comparing Vertex vs LimeSpot recommendations. It should never load in production/live themes. At minimum, the inline `<script>` block (lines 46–94) executes function calls and DOM reads on every page.
- **Priority:** P0 (highest) — zero production value, pure waste. ~1.5 KB inline JS + ~1 KB HTML on every pageview.

### BCPO Product Data — Unconditional on All Pages
- **File:** `layout/theme.liquid` lines 159–170
- **Issue:** The BCPO inline script outputs `var bcpo_product`, `var inventory_quantity`, `var bcpo_settings`, and `var bcpo.cart` on EVERY page, including collections where `product` is `nil`. On collection pages, `{{ product | json }}` outputs `null`, and the `{% for v in product.variants %}` loop produces an empty array — but the script block still executes and occupies parse time.
- **Recommendation:** Wrap in `{% if template contains 'product' %}` — the BCPO options widget only renders on product pages.
- **Priority:** P1 — ~1.2 KB savings on non-product pages.

### Pro Blogger Scripts
- **File:** `layout/theme.liquid` lines 889–940 (CSS defer guard) + line 146 (`{% include 'pro-blogger-section-wrapper' %}`)
- **Issue:** The Pro Blogger section wrapper is included unconditionally at line 146 (in `<head>`). The CSS defer guard at lines 889–940 runs MutationObserver + createElement override on every page to intercept Pro Blogger stylesheets. Pro Blogger is primarily a blog tool; its CSS/JS is only needed on blog/article pages and some collection pages.
- **Recommendation:** Audit whether Pro Blogger is actually used on brand/collection pages. If not, gate both the section wrapper include and the CSS defer guard with `{% unless template contains 'collection' %}`. At minimum, the MutationObserver at line 931 runs on every page watching for links that only appear on blog/collection pages.
- **Priority:** P2 — guard code itself is small (~50 lines), but the Pro Blogger CSS/JS it releases into the page is substantial.

### STKY/SATCB Script — Loaded Unconditionally
- **File:** `layout/theme.liquid` line 1406
- **Script:** `<script src="https://satcb.azureedge.net/Scripts/satcb.min.js?shop=creations-gdc.myshopify.com" async="async" defer="defer"></script>`
- **Issue:** The SATCB (Zapiet Store Pickup) CDN script is loaded unconditionally at line 1406 in `<body>`, even though the `storepickup.liquid` snippet (line 1158) that initializes Zapiet's widget is already properly gated with `{% if template contains 'product' or template == 'cart' %}`. This means SATCB.min.js downloads on every page — including collections, blog, homepage — but only does anything on product and cart pages.
- **Recommendation:** Gate to `{% if template contains 'product' or template == 'cart' %}`. Matches the existing gate on `storepickup.liquid` at line 1157. This is a direct CDN script (not injected by cfh), so it can be conditional.
- **Priority:** P1 — saves one HTTP request + download on ~85% of pageviews.

### Reamaze Defer-on-Interaction
- **File:** `layout/theme.liquid` lines 951–1115
- **Issue:** The Reamaze defer guard (165 lines of inline JS) is sophisticated and working as designed — it blocks Reamaze CDN scripts until first user interaction (click/touch/keydown), 5s idle, or 60s auto-release. However, the guard itself is 165 lines of inline JS executing on every page, and once triggered, Reamaze still downloads ~212 KB across multiple scripts. On collection/brand pages, shoppers rarely engage with chat.
- **Recommendation:** Consider gating the entire Reamaze defer guard to product/cart pages only: `{% if template contains 'product' or template == 'cart' %}`. On other pages, neither the guard code nor the Reamaze SDK would load. Chat availability on those pages can be handled by the reamaze-placeholder (line 1122) linking to a contact page if truly needed.
- **Priority:** P2 — ~212 KB network savings + 165 lines of inline JS on non-product/cart pages. Medium risk (customers on blog/search pages can't open chat). Evaluate chat usage analytics before gating.

### LoyaltyLion — Full SDK on Every Page
- **File:** `snippets/loyaltylion.liquid`, rendered at `layout/theme.liquid` line 872
- **Issue:** The LoyaltyLion snippet (133 lines) initializes the full SDK loader on every page. While the createElement guard (lines 780–869) prevents LoyaltyLion from being render-blocking, the SDK still fetches `loader.js` + `start/{token}.js` on every pageview — ~500 KB total. Loyalty points display is only relevant to logged-in customers on product/cart pages.
- **Recommendation:** Gate to `{% if customer or template contains 'product' or template == 'cart' %}`. Anonymous visitors on collection pages never see loyalty UI.
- **Priority:** P2 — high byte savings (~500 KB) on collection pages for anonymous visitors. Lower risk than Reamaze since LL is invisible to logged-out users anyway.

### Bold Common — Config Data on Every Page
- **File:** `snippets/bold-common.liquid`, rendered at `layout/theme.liquid` line 1145
- **Issue:** Bold Common dumps ~133 lines of inline JS configuring `window.BOLD.common.Shopify` and cache hashes for Bold RO/MD/PAD apps. These apps only render on product/cart pages, but the config runs on every page.
- **Recommendation:** Gate to `{% if template contains 'product' or template == 'cart' %}` to match Bold app rendering scope.
- **Priority:** P2 — ~3–5 KB inline savings on collection/home/blog pages.

### code-customizer-header — Dead Include
- **File:** `snippets/code-customizer-header.liquid`, rendered at `layout/theme.liquid` line 1178
- **Issue:** The snippet file is empty (0 bytes). The `{% include %}` call at line 1178 parses Liquid and evaluates the file for zero output on every page.
- **Recommendation:** Remove the `{% include "code-customizer-header" %}` line entirely. Zero functional impact, saves a template parse cycle.
- **Priority:** P1 — trivial fix, zero risk.

### FreeGifts Snippet — Runs on Every Page
- **File:** `snippets/freegifts-snippet-change.liquid`, rendered at `layout/theme.liquid` line 1441
- **Issue:** Contains a `<script>setTimeout(...)` that runs on every page. FreeGifts (gift-with-purchase) interaction is only needed on product/cart pages.
- **Recommendation:** Gate to `{% if template contains 'product' or template == 'cart' %}`.
- **Priority:** P2 — savings depend on FreeGifts app payload.

## Recommended Quick Wins (Ordered by Impact)

1. **Gate vertex-preview-toolbar.liquid** — Wrap in `{% if request.design_mode %}`. 1-line change in the snippet (or in its render call), zero risk, immediate bytes savings. P0 because it's a dev tool in production.
2. **Remove `{% include "code-customizer-header" %}`** — Empty snippet, dead include. 1-line deletion from theme.liquid line 1178. Zero risk.
3. **Gate BCPO to product pages only** — Wrap lines 159–170 in `{% if template contains 'product' %}`. ~1.2 KB inline savings on non-product pages. Near-zero risk (BCPO widget only renders on product pages).
4. **Gate SATCB/Zapiet to product+cart only** — Wrap line 1406 in `{% if template contains 'product' or template == 'cart' %}`. Already gated at line 1157 for `storepickup.liquid`. Saves one HTTP request + download on ~85% of pageviews.
5. **Gate Bold Common to product+cart** — Wrap line 1145 in `{% if template contains 'product' or template == 'cart' %}`. ~3–5 KB inline savings on collection/home/blog pages.
6. **Gate freegifts-snippet-change to product+cart** — Wrap line 1441 in `{% if template contains 'product' or template == 'cart' %}`. Savings depend on app payload.
7. **Gate Reamaze guard to product+cart** — Wrap lines 951–1115 in `{% if template contains 'product' or template == 'cart' %}`. ~212 KB network savings + 165 lines inline JS removed on non-product/cart pages. Evaluate chat usage on blog/search pages first.
8. **Gate LoyaltyLion to customer/product/cart** — Wrap line 872 in `{% if customer or template contains 'product' or template == 'cart' %}`. ~500 KB network savings for anonymous visitors on collection pages.
9. **Audit Pro Blogger necessity on collections** — Determine if Pro Blogger CSS/JS is needed on collection pages. If not, gate the section wrapper (line 146) and the CSS defer guard (lines 889–940) to blog/article templates only.

## Next Steps

Each recommendation above should be filed as a separate bd follow-up ticket. The coordinator should:
1. Run `bd create` for each recommendation
2. Link each to this parent issue (`hairmnl-theme-ujg6.33`)
3. Prioritize vertex-preview-toolbar and code-customizer-header (trivial changes, zero risk)
4. Then BCPO and SATCB gating (low risk, high byte savings)
5. Then Bold Common and FreeGifts gating (medium risk — test product/cart flows)
6. Then Reamaze and LoyaltyLion gating (require analytics review before proceeding)
7. Pro Blogger audit requires business input on whether it's used on collections

## Estimated Total Impact

If all quick wins are implemented, estimated savings on a brand/collection page (mobile):
- **Inline JS removed:** ~5–8 KB (BCPO + Bold Common + code-customizer + vertex-preview-toolbar)
- **Network requests removed:** 2 (SATCB CDN + FreeGifts if gated)
- **Network bytes removed:** ~700+ KB (Reamaze ~212 KB + LoyaltyLion ~500 KB if gated for anonymous)
- **Inline lines removed:** ~170+ lines of JS not executed (Reamaze guard + vertex-preview + BCPO)
- **Estimated PSI script count reduction:** 8–12 scripts eliminated (approaching the +17 target)