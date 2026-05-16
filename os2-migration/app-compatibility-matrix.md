# HairMNL OS 2.0 / Pipeline 8+ Migration — App Compatibility Matrix

**Date:** 2026-05-17
**Status:** Draft — Local audit complete
**Bead:** hairmnl-theme-80z0.1 (P1.1: App embed compatibility audit)

> **Scope note:** Generated from local theme code audit (`bd hairmnl-theme-80z0.1`). Full enumeration requires Shopify Admin → Apps view verification. Rows marked 🔴 NEED-VERIFY require admin-side confirmation.

---

## Traffic-Light Legend

| Badge | Meaning |
|-------|---------|
| 🟢 GREEN | TAE available; clean install on Pipeline 8 expected |
| 🟡 YELLOW | Mixed support — TAE available but legacy scripts also present; cleanup needed |
| 🔴 RED | Legacy embed only — no TAE; manual port required |
| ⚪ GRAY | Not applicable / out of scope / being uninstalled |

---

## App Compatibility Matrix

| # | App Name | Vendor | Current Embed Mechanism | TAE Available? | TAE Block Names | Vendor Deprecation Stance | Pipeline 8 Install Behavior | Recommended Migration Path | Status |
|---|----------|--------|------------------------|----------------|-----------------|---------------------------|----------------------------|---------------------------|--------|
| 1 | BOGOS Free Gifts | BOGOS | App embed block: `shopify://apps/free-gifts-bogo-buy-x-get-y/blocks/app-embed/0432bba6…` | Yes | `app-embed` | Active, OS2.0 compliant | Installs via TAE editor toggle | Toggle TAE block; verify promotional UI renders in Pipeline 8 sections. **Note:** Targeted for custom replacement — $420/yr saved (bd oyw). | 🟡 |
| 2 | Smart SEO (core) | SherifG | App embed block: `shopify://apps/smartseo/blocks/smartseo/7b0a6064…` | Yes | `smartseo` | Active, OS2.0 badge on App Store | Installs via TAE; SEO meta injection should work unchanged | Toggle TAE block; verify structured-data output unchanged. | 🟢 |
| 3 | Smart SEO (broken-link detection) | SherifG | App embed block: `shopify://apps/smartseo/blocks/brokenLinkDetection/7b0a6064…` | Yes | `brokenLinkDetection` | Same vendor as #2 | Installs alongside core Smart SEO TAE block | Toggle TAE block; verify 404 redirect logic still fires. | 🟢 |
| 4 | Klaviyo Email Marketing / SMS | Klaviyo | App embed block: `shopify://apps/klaviyo-email-marketing-sms/blocks/klaviyo-onsite-embed/2632fe16…` | Yes | `klaviyo-onsite-embed` | Active, OS2.0 compliant; ~120 KB always-on | Installs via TAE; popup CLS mitigated | Toggle TAE block; verify onsite JavaScript + popup CLS fix still applies. | 🟢 |
| 5 | Judge.me Reviews | Judge.me | App embed block: `shopify://apps/judge-me-reviews/blocks/judgeme_core/61ccd3b1…`; **also** deferred loader + static stars already shipped in theme | Yes | `judgeme_core` | Active, OS2.0 compliant | Installs via TAE; theme-level deferred loader should coexist cleanly | Verify deferred-loader + TAE block don't double-load; may be able to rely on TAE only. | 🟡 |
| 6 | Elevar Conversion Tracking | Elevar | App embed block: `shopify://apps/elevar-conversion-tracking/blocks/dataLayerEmbed/bc30ab68…` | Yes | `dataLayerEmbed` | Active; 2.6s latency on PSI reported | Installs via TAE; data-layer injection persists | Audit Elevar TAE block latency; consider deferring or gating to key routes. | 🟡 |
| 7 | Shopify Inbox | Shopify | App embed block: `shopify://apps/inbox/blocks/chat/841fc607…` | Yes | `chat` | First-party; fully OS2.0 native | Installs via TAE; first-party reliability | Toggle TAE block; no migration risk. | 🟢 |
| 8 | Nova EU Cookie Bar (GDPR) | Nova Apps | App embed block: `shopify://apps/nova-eu-cookie-bar-gdpr/blocks/app-embed/6667ecbd…` | Yes | `app-embed` | Active, OS2.0 badge on App Store | Installs via TAE | Toggle TAE block; verify GDPR banner renders in Pipeline 8 header/footer zone. | 🟢 |
| 9 | Re:amaze (Live Chat + Helpdesk) | Re:amaze | App embed block: `shopify://apps/reamaze-live-chat-helpdesk/blocks/reamaze-config/ef7a830c…` | Yes | `reamaze-config` | Active; 213 KB; targeted for defer-on-interaction | Installs via TAE; 213 KB payload deferred by vendor toggle | Enable defer-on-interaction in Re:amaze dashboard alongside TAE toggle. | 🟡 |
| 10 | Hextom Timer Bar (CTB) | Hextom | App embed block: `shopify://apps/hextom-timer-bar/blocks/ctb-embeded-block/f7b88b6e…` | Yes | `ctb-embeded-block` | Active, OS2.0 badge on App Store | Installs via TAE | Toggle TAE block; verify countdown bar renders in Pipeline 8 announcement bar area. | 🟢 |
| 11 | LoyaltyLion (SDK embed) | LoyaltyLion | App embed block: `shopify://apps/loyalty-rewards-and-referrals/blocks/embed-sdk/6f172e67…` | Yes | `embed-sdk` | Active; 266 KB; NOT Smile.io | Installs via TAE alongside main embed | Toggle both TAE blocks; verify loyalty widget + SDK load order. | 🟢 |
| 12 | LoyaltyLion (main embed) | LoyaltyLion | App embed block: `shopify://apps/loyalty-rewards-and-referrals/blocks/embed-main/6f172e67…` | Yes | `embed-main` | Same vendor as #11 | Installs alongside SDK TAE block | Same as #11 — verify both blocks enabled together. | 🟢 |
| 13 | LDT Gift Wrap | LDT | App embed block: `shopify://apps/ldt-gift-wrap/blocks/embed/4046b73d…` | Yes | `embed` | Active, OS2.0 badge on App Store | Installs via TAE | Toggle TAE block; verify gift-wrap checkbox renders on product form. | 🟢 |
| 14 | OXI Social Login | OXI Apps | App embed block: `shopify://apps/oxi-social-login/blocks/social-login-embed/24ad60bc…` | Yes | `social-login-embed` | Active, OS2.0 badge on App Store | Installs via TAE | Toggle TAE block; verify social-login buttons appear on Pipeline 8 customer login form. | 🟢 |
| 15 | STKY Sticky Add-to-Cart | STKY | **Dual embed — app embed block** `shopify://apps/stky-sticky-add-to-cart/blocks/satcb/2d1e1d5d…` **AND legacy hardcoded script tag** (duplicate load). | Yes | `satcb` | Active; **duplicate-load bug** — TAE block + legacy script both active | Installs via TAE but legacy hardcoded script will cause double-load | **Critical:** Remove legacy hardcoded `<script>` from theme.liquid before migration. Replacement planned (bd a7av; $300/yr saved). | 🟡 |
| 16 | Searchanise | Searchanise | **Hardcoded `<script src="//www.searchanise.com/widgets/shopify/init.js?a=7K0f1C4k5q">`** in `layout/theme.liquid:164` | Likely — Searchanise has OS2.0 badge on App Store | Unknown — verify in Shopify admin | Likely supports TAE; verify | Remove hardcoded script tag; install via TAE if available; otherwise port to theme snippet wrapped in `{% render %}` | 🔴 NEED-VERIFY |
| 17 | Personalizer.io (Visually) | Visually | DNS prefetch in `layout/theme.liquid`; 249 KB always-on; no local snippet detected | Unknown — no local evidence of TAE block | Unknown — verify in Shopify admin | Unknown — likely loads via `content_for_header` | If TAE available, switch to TAE; otherwise leave as content_for_header. Audit 249 KB payload for gating potential. | 🔴 NEED-VERIFY |
| 18 | BookThatApp | BookThatApp | DNS prefetch mention only in theme; 171 KB; targeted for per-route gating | Unknown — verify in Shopify admin | Unknown — verify in Shopify admin | Unknown — may load entirely via `content_for_header` | Implement per-route gating (bd oyw); if TAE available, switch to TAE. | 🔴 NEED-VERIFY |
| 19 | VisualQuizBuilder | Visual Quiz Builder | No local evidence found; 447 KB; may be injected via `content_for_header` only | Unknown — no local snippets or blocks found | Unknown — verify in Shopify admin | Unknown — entirely admin-side? | If TAE available, switch to TAE. Otherwise, implement per-route gating per ARCHITECTURE.md §9. | 🔴 NEED-VERIFY |
| 20 | Pro Blogger / SA | Pro Blogger | **Multiple legacy snippets:** `pro-blogger.snippet.related-products.liquid`, `pro-blogger.snippet.related-product-articles.liquid`, `pro-blogger.snippet.related-articles.liquid`, `pro-blogger-section-wrapper.liquid`, `pro-blogger.shortcode.liquid` | Unlikely — legacy snippet-based app | N/A | Legacy embed; unlikely to have OS2.0 TAE | Snippets remain but may need `{% render %}` syntax update | Port snippets to `{% render %}` syntax; wrap in a dedicated section for OS2.0. Verify vendor still supports these snippets. | 🔴 |
| 21 | MBC Bundles | MBC | **Legacy snippet:** `mbc-bundles.liquid` | Unknown — verify in Shopify admin | Unknown — verify in Shopify admin | Unknown — may have TAE version | If TAE available, switch; otherwise port snippet to `{% render %}` syntax | 🔴 NEED-VERIFY |
| 22 | PluginSEO (SherifG) | SherifG | **Multiple legacy snippets:** `pluginseo.liquid`, `pluginseo-structured-data.liquid`, `pluginseo-meta-description.liquid`, `pluginseo-langify.liquid`, `pluginseo-page-title.liquid`, `pluginseo-parse.liquid` | Unlikely — legacy snippet-based; same vendor as Smart SEO (#2/#3) | N/A | **Likely deprecated** — superseded by Smart SEO TAE blocks (#2, #3) | Snippets may conflict with Smart SEO TAE structured-data output | **Remove all pluginseo snippets** after confirming Smart SEO TAE handles structured data + meta. Audit for unique features before deleting. | 🔴 |
| 23 | SWYM Wishlist | SWYM | **Legacy snippets:** `swymSnippet.liquid`, `swym-product-view.liquid` | Likely — SWYM has OS2.0 badge on App Store | Unknown — verify in Shopify admin | Likely supports TAE; legacy snippets may be outdated | TAE block should replace snippets | Remove legacy snippets; install via TAE. Verify wishlist UI renders in Pipeline 8 product page. | 🟡 |
| 24 | Appikon Back-in-Stock | Appikon | **Legacy hardcoded `<script>`** loading `subscribe-it.js`; targeted for Klaviyo-native Back-in-Stock replacement (bd g1n) | N/A — being replaced | N/A | Being replaced; no point migrating | Klaviyo-native BIS to replace | **Do not migrate.** Replace with Klaviyo-native Back-in-Stock flow (bd g1n). Remove hardcoded script. | ⚪ |
| 25 | Zapiet Store Pickup | Zapiet | **Legacy snippet:** `storepickup.liquid` (gated) | Likely — Zapiet has OS2.0 badge on App Store | Unknown — verify in Shopify admin | Likely supports TAE; snippet may be legacy | TAE block should replace gated snippet | Remove gated snippet; install via TAE. Verify pickup widget renders on Pipeline 8 cart page. | 🟡 |
| 26 | BSS B2B Customer Portal | BSS Commerce | **Legacy snippets + templates:** `page.bss-b2b-wholesaler-1959.liquid`, `search.bss.b2b.liquid`; scheduled for full uninstall | N/A — being uninstalled | N/A | Scheduled for full uninstall per ARCHITECTURE.md §9 | Will be removed entirely | **Do not migrate.** Complete uninstall per schedule. Remove all BSS templates and snippets. | ⚪ |
| 27 | Google Maps API | Google | **Hardcoded in `assets/theme.js` lines 6652–6710** | N/A — not a Shopify app, no TAE concept | N/A | N/A (first-party JS library) | Remains as-is; no app embed mechanism | Extract Maps logic into a dedicated section/snippet; load API key from theme settings. Consider lazy-loading. | 🔴 |
| 28 | GTM (Google Tag Manager) | Google | DNS prefetch + managed via `content_for_header`; OWNED tag, 618 KB | N/A — TAE not applicable to GTM | N/A | N/A | Remains as `content_for_header` injection; no TAE migration needed | No TAE path; GTM loads via `content_for_header`. Optimize container size (618 KB) independently. | ⚪ |
| 29 | LimeSpot (Personalized Recommendations) | LimeSpot | **Legacy `{% include 'limespot' %}` snippet** which loads their SDK; targeted for Vertex AI replacement (bd oyw) | N/A — being replaced | N/A | Being replaced with Vertex AI custom recommender | LimeSpot SDK will be fully removed | **Do not migrate.** Replace with Vertex AI recommendation engine per bd oyw. Remove `limespot` snippet. | ⚪ |
| 30 | Growave (possible) | Growave | No local snippets found; may load via `content_for_header` only | Unknown — no local evidence | Unknown — verify in Shopify admin | Unknown — may not be installed | N/A — presence itself is uncertain | **Verify in Shopify Admin** whether Growave is installed before taking action. | 🔴 NEED-VERIFY |

---

## Summary

| Category | Count | Apps |
|----------|-------|------|
| **Total apps enumerated** | **30** | 15 app-embed blocks + 15 script/snippet/other |
| 🟢 TAE-ready | 10 | Smart SEO (×2), Klaviyo, Shopify Inbox, Nova Cookie Bar, Hextom Timer Bar, LoyaltyLion (×2), LDT Gift Wrap, OXI Social Login |
| 🟡 Mixed / some TAE | 5 | BOGOS, Judge.me, Elevar, Re:amaze, STKY, SWYM, Zapiet |
| 🔴 Legacy only / NEED-VERIFY | 10 | Searchanise, Personalizer.io, BookThatApp, VisualQuizBuilder, Pro Blogger, MBC Bundles, PluginSEO, Google Maps API, Growave, (+ partial: STKY legacy side) |
| ⚪ Out of scope / being replaced | 4 | Appikon (→ Klaviyo BIS), BSS B2B (uninstall), LimeSpot (→ Vertex AI), GTM (content_for_header, no TAE path) |

> **Note:** The 🟡 count includes STKY which straddles 🟢 (TAE block exists) and 🔴 (legacy hardcoded duplicate). The 🔴 count includes apps that may have TAE available but lack local evidence — these are flagged as NEED-VERIFY.

---

## Key Findings

### 1. STKY Duplicate-Load Bug (High Priority)
STKY Sticky Add-to-Cart has **both** an active TAE app embed block (`satcb`) **and** a legacy hardcoded `<script>` tag in the theme. This causes duplicate initialization and wasted bandwidth. **This must be cleaned up regardless of migration timing** — remove the legacy script tag before any Pipeline 8 switch.

### 2. PluginSEO → Smart SEO Overlap
Six `pluginseo-*.liquid` legacy snippets likely duplicate functionality now handled by the Smart SEO TAE blocks (#2, #3). Running both simultaneously may cause conflicting structured-data output or duplicate meta tags. Recommend audit + removal of pluginseo snippets after confirming Smart SEO TAE coverage.

### 3. Apps With No Local Evidence (content_for_header Only)
Several apps — VisualQuizBuilder (447 KB), Personalizer.io (249 KB), BookThatApp (171 KB), and possibly Growave — have **no local snippets or TAE blocks** in the theme. They likely load entirely via Shopify's `content_for_header` injection. These are invisible to a local audit and **must be verified in Shopify Admin → Apps**. Their large payloads make gating/defer strategies critical.

### 4. Legacy Snippet Apps Need Manual Port
Pro Blogger (5 snippets), MBC Bundles (1 snippet), and historically PluginSEO (6 snippets) use `{% include %}`-based embedding with no TAE equivalent found locally. These require either: (a) vendor TAE migration, or (b) manual port to `{% render %}` + dedicated OS2.0 sections.

### 5. Google Maps API Hardcoded in Theme JS
Google Maps API calls are hardcoded directly in `assets/theme.js` (lines 6652–6710). This is an architectural debt — not a Shopify app, so no TAE path exists. Should be extracted into a lazy-loaded section with API key in theme settings.

---

## Recommended Pre-Migration Actions

1. **Verify full app list in Shopify Admin → Apps.** The local audit cannot see `content_for_header`-only apps. Cross-reference the admin app list against this matrix and add any missing entries.

2. **For each 🔴 NEED-VERIFY app, contact the vendor** or check their App Store listing to confirm TAE availability and OS2.0 compatibility. Prioritize high-payload apps: VisualQuizBuilder (447 KB), Personalizer.io (249 KB), BookThatApp (171 KB).

3. **Clean up STKY duplicate load immediately** — remove the legacy hardcoded `<script>` tag from `theme.liquid`. This is a bug fix independent of the OS2.0 migration timeline.

4. **Audit PluginSEO vs Smart SEO overlap** — determine whether the six `pluginseo-*.liquid` snippets can be safely removed now that Smart SEO TAE blocks handle structured data and SEO metadata.

5. **Plan replacement timelines** for apps marked ⚪ (being replaced): Appikon (bd g1n → Klaviyo BIS), LimeSpot (bd oyw → Vertex AI), BSS B2B (uninstall). Ensure these removals happen before the Pipeline 8 cutover to avoid carrying dead code.

6. **Extract Google Maps API** from `theme.js` into a lazy-loaded section to reduce initial bundle size and make the Maps dependency explicit.

7. **Document `content_for_header` payload** — request a Shopify Admin export or use browser dev tools to capture the full `content_for_header` output, revealing any apps invisible to file-system audits.