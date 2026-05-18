## Autonomous smoke tests 2026-05-18 ~22:30 — 7 tickets verified, 1 issue caught + fixed

Static-content smoke tests against P8 dev theme `141168312419` via `shopify theme pull`. Verifies that what's IN GIT is also DEPLOYED to the dev theme.

### Issue caught + remediated

**`assets/hairmnl-product.js` was missing from dev theme** despite being in git (added by OC ujg6.14 swarm in commit 9832966). The OC swarm staged the file to git, but the corresponding `shopify theme push` for ujg6.14 only included layout/theme.liquid (B.2.2 wiring). The JS file landed in git but never got pushed to Shopify.

Impact had this gone undetected: post-cutover, product templates would 404 on `<script src="{{ 'hairmnl-product.js' | asset_url }}">` (Liquid would render the URL but the file doesn't exist). The product-tabs-v1 behavior section would silently fail to load on PDPs.

Fix: `shopify theme push --theme=141168312419 --only=assets/hairmnl-product.js --nodelete` during smoke. Re-pull confirms file is now present (37 LoC, matches local).

### 7 tickets verified clean

| Ticket | Smoke | Evidence |
|---|---|---|
| `ujg6.7` font CLS overrides | ✅ PASS | 3 line-box overrides (ascent 90.5%, descent 21.2%, line-gap 3.3%) + 4 `font-display: optional` on accent weights in `snippets/custom-fonts.liquid` |
| `ujg6.14` + `2i8b.19` split JS + wiring | ✅ PASS (after fix) | All 3 files present on dev (`hairmnl-common.js` 389 LoC, `hairmnl-collection.js` 154 LoC, `hairmnl-product.js` 37 LoC); 3 script tags in `layout/theme.liquid` lines 739, 741, 744 with `template contains 'collection'`/`'product'` gates |
| `2i8b.18` mobile menu-buttons CLS | ✅ PASS | `font-weight: var(---menu-btn-bold, normal)` + `text-transform: var(---menu-btn-caps, none)` present in mobile @media block of `sections/menu-buttons.liquid` |
| `fsaa` Reamaze defer guard | ✅ PASS | KILL_SWITCH at L854, 4 cdn.reamaze refs, 3 GA4 telemetry events, placeholder render at L1023, correctly ORDERED before `{{ content_for_header }}` (L1019) |
| `ujg6.16` facet AJAX | ✅ PASS | Second IIFE block in `assets/hairmnl-collection.js` starts L76; facet-ajax markers (5), Section API refs (8), pushState (2), popstate handler (3 — code + comment + window listener) |
| `ujg6.18` lazy-render ×3 | ✅ PASS | All 3 sections (`section-collection`, `brand-collection`, `related`) have `request.design_mode` + `request.page_type == null` + `data-lazy-render` + `<noscript>`; IO hook in `hairmnl-common.js` section 8 has 4 lazy-render markers |
| `ujg6.19` font preloads + slideshow eager | ✅ PASS | 2 font preload `<link>` blocks for BasisGrotesquePro-Regular.woff2 + SelfModern.woff2 at L128/133; slideshow `forloop.first → eager:true` logic in `sections/section-slideshow.liquid` L68-79 |

### What smoke testing CAN'T do from CC

These remain for operator browser smoke:

- **Visual regression** — does brand-collection still LOOK right after lazy-render swaps in? No automated way to verify pixel-perfect.
- **Interactive flow** — cart drawer reload, filter checkbox toggle → grid update, related-products tab switching.
- **Network timing** — DevTools waterfall showing Reamaze SDK NOT fetched until interaction.
- **Real LCP / CLS measurement** — beyond PSI lab numbers, real-user CrUX takes 28d.
- **TAE-block side effects** — does Klaviyo signup form still display on first visit? Does Judge.me badges still render?

These tests require a logged-in browser session with cookies — not curl-accessible.

### Recommendation

The 7 static-content smoke tests give high confidence that **what was supposed to ship is on the dev theme**. The remaining browser smoke (interactive verification) is the right operator next step.

### Mechanism

```
shopify theme pull --theme=141168312419 --path=/tmp/dev-smoke --only=<file>...
# Then grep for expected markers per ticket.
```

This pattern should become part of pre-cutover verification — file as `2i8b.X` follow-up if desired.
