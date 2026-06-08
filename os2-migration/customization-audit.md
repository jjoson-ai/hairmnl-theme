# HairMNL Pipeline 6.1.3 Customization Audit — OS 2.0 Migration Readiness

| Field | Value |
|---|---|
| **Date** | 2026-05-17 |
| **Status** | Complete |
| **Scope** | All bespoke Liquid/CSS/JS in Pipeline 6.1.3 theme vs stock Pipeline 6. |
| **Base theme** | Pipeline 6.1.3 (confirmed: `layout/theme.liquid:37`, `theme.version: '6.1.3'` L471) |

---

## Executive Summary

| Metric | Value |
|---|---|
| **Total bespoke LoC** | ~19,000 |
| **Files touched (non-stock or materially modified)** | ~75 |
| **Sections** | 98 total; ~31 custom collection-branded pages + 4 custom sections |
| **Snippets** | 202 total; ~35 custom or materially modified |
| **Templates** | 180 total; ~31 custom collection + 3 app templates |

### Per-Category Breakdown

| Category | Files | LoC (est.) | Can Drop | Need Port | Need Rebuild |
|---|---|---|---|---|---|
| layout/theme.liquid | 1 | ~1,121 | 8 | 18 | 0 |
| Custom sections (brand collections) | 31 | ~52,500 | 0 | 31 | 0 |
| Custom sections (other) | 3 | ~1,390 | 0 | 2 | 1 |
| Custom snippets | ~35 | ~4,400 | 10 | 15 | 10 |
| CSS overrides + variables | 2 | 1,056 | 5 | 15 | 1 |
| Templates (collection variants) | 31 | ~155 | 0 | 31 | 0 |
| Templates (app pages) | 3 | ~128 | 3 | 0 | 0 |
| Custom JS (custom-theme.js) | 1 | 9,118 | 0 | 1 | 0 |
| Assets (CSS splits, vendor) | ~15 | ~12,000 | 2 | 13 | 0 |

---

## Section 1: layout/theme.liquid Customizations

Layout file: 1,121 lines. Stock Pipeline 6 `theme.liquid` is ~500 lines; the HairMNL version carries ~620 lines of bespoke additions/changes.

### 1.1 DNS Prefetches / Preconnects (Lines 39–90)

| Lines | Customization | Difficulty | Notes |
|---|---|---|---|
| 39–54 | 4 custom `<link rel="preconnect">`: cdn.shopify.com, fonts.shopify.com, monorail-edge.shopifysvc.com, cdn.judge.me | **easy** | OS 2.0 renders these from app embeds automatically; manual preconnects for app CDNs can be dropped if apps self-register. |
| 82–90 | 9 custom `<link rel="dns-prefetch">`: googletagmanager.com, cdn.reamaze.com, edge.personalizer.io (LimeSpot), sdk-static.loyaltylion.net, static.klaviyo.com, tracking.aws.judge.me, analytics.tiktok.com, satcb.azureedge.net, searchanise CDN + 1 preconnect | **easy** | All serve specific third-party apps. In OS 2.0, most apps inject their own resource hints via `{{ content_for_header }}`. Can drop after verifying each app handles its own. |

### 1.2 Critical Resource Loading (Lines 103–413)

| Lines | Customization | Difficulty | Notes |
|---|---|---|---|
| 17 | `{% render 'critical-css' %}` inlined critical CSS | **easy** | Pipeline 8 / Dawn have their own critical CSS strategy. Re-audit. |
| 22–24 | Deferred BSS hide-variant CSS via `media="print"` swap | **easy** | BSS B2B now uninstalled; can drop entirely. |
| 111–116 | Preloads for vendor.js, theme.js, theme.css, custom-theme.css | **medium** | OS 2.0 uses `{{ content_for_header }}` for script loading; custom preloads need manual migration. |
| 122–123 | Deferred tiny.content.min.css via `media="print"` swap | **easy** | TinyMCE editor CSS; Dawn uses its own RTE editor. |
| 125 | `{% include 'pro-blogger-section-wrapper' %}` — Pro Blogger app integration | **easy** | App snippet; OS 2.0 Pro Blogger update handles this. |
| 136–137 | Bundled deferred-extras.css (bcpo, font-awesome, bold-upsell) | **medium** | In OS 2.0, apps self-inject. The bundling optimization needs re-verification. |
| 138–149 | BCPO product option JS data initialization | **medium** | Bold Custom Product Options; need to verify OS 2.0 compatibility. |
| 164 | Searchanise init.js with `defer` | **easy** | App loads own scripts; can drop if Searchanise OS 2.0 app embed works. |
| 181–183 | LimeSpot SDK gated to non-customers templates | **medium** | Custom gating logic; needs port to OS 2.0 `request.page_type` conditional. |
| 187–204 | Product featured image LCP preload with srcset | **medium** | Dawn handles LCP preloading differently. Need to port srcset pattern. |
| 220–231 | Article hero image LCP preload (WebP, imagesrcset) | **medium** | Custom LCP optimization; Dawn has its own `<picture>` pattern. |
| 260–287 | First-body-image LCP extraction from `article.content` | **hard** | Complex Liquid string parsing to extract `<img src>` from rich text. Dawn/OS 2.0 has no equivalent; would need porting or rewriting as a section. |
| 28 | `{% render 'canonical' %}` — custom canonical URL management (118 lines) | **medium** | Complex product handle overrides, collection query-string stripping, LimeSpot canonical defer. OS 2.0 uses `{{ canonical_url }}` but doesn't handle these edge cases. |
| 29 | `{% render 'hairsalon-schema' %}` — HairSalon JSON-LD (109 lines) | **easy** | Structured data for two Studio pages. Can become a custom OS 2.0 block or section. |
| 342 | `{% render 'font-settings-inline' %}` — self-hosted Playfair Display | **easy** | Pipeline 8 uses Shopify font CDN; self-hosting is a perf optimization that needs re-verification. |
| 352 | `{% render 'css-variables' %}` — 435 lines of CSS custom properties | **medium** | Pipeline 8 has its own variable system; HairMNL variables need mapping. |
| 354–413 | Template-gated CSS splits (plyr, pswp, model_viewer, cart, cart-page, AOS, deferred-templates) | **medium** | All custom perf splits. Dawn loads all CSS from one bundle; would need reimplementation or acceptance of larger initial CSS. |
| 414 | `{% render 'css-overrides' %}` — 621 lines of custom CSS | **hard** | Extensive custom CLS/a11y/app CSS overrides. Needs careful port, many are app-specific workarounds. |

### 1.3 JavaScript and Data Layer (Lines 416–812)

| Lines | Customization | Difficulty | Notes |
|---|---|---|---|
| 422–493 | `window.theme` config object (routes, assets, strings, settings, moneyFormat, version) | **easy** | Dawn uses `window.Shopify` + section-level `schema`. Needs mapping. |
| 537–550 | Drawer-toggle click-intercept (capture-phase) | **medium** | Custom UX fix for drawer-tap-through; Dawn's cart drawer uses different event model. |
| 629–656 | A/B testing framework (cookie-based, CSS class + dataLayer) | **medium** | Custom implementation. Dawn has no equivalent; needs port to custom JS or external A/B tool. |
| 657–687 | JS error tracking → `window.dataLayer` (`hairmnl_js_error`, throttled to 10/session) | **medium** | Custom RUM; needs port to Dawn's global scope. |
| 688–700 | Script loading: vendor.js (defer), jquery.min.js (defer), theme.js (defer) | **easy** | Dawn uses its own `global.js` + `vendor.min.js`. Mapping needed. |
| 719–726 | Cart pre-init dispatcher (`theme:cart:init` on `pageshow`) | **medium** | Custom cart preloading pattern; Dawn's cart section has its own fetch mechanism. |
| 728 | `{% include "loyaltylion" %}` — LoyaltyLion SDK embedding | **easy** | App embed; OS 2.0 version available. |
| 745–796 | Pro Blogger CSS defer interceptor (createElement override + MutationObserver) | **hard** | Complex DOM interception to defer app-injected CSS. In OS 2.0, app embeds use `{{ content_for_header }}` — this interception approach may break or be unnecessary. |
| 799 | `{{ content_for_header }}` | **stock** | Standard Shopify; no customization. |
| 801–802 | Bold Brain widget CSS (deferred) | **easy** | App CSS; verify Bold OS 2.0 compatibility. |
| 825 | `{% render 'bold-common' %}` — Bold app common snippet (133 lines) | **easy** | App snippet; verify OS 2.0 version. |
| 837–839 | Zapiet storepickup gated to product + cart templates | **medium** | Custom gating; OS 2.0 Zapiet app embed may handle this. |
| 858 | `{% include "code-customizer-header" %}` — Code Customizer app | **easy** | App-injected; drop with app uninstall or use OS 2.0 app embed. |
| 878–879 | Vertex AI recommendations CSS (disabled) | **easy** | Will be activated with Vertex AI Phase 1; needs section-level CSS in OS 2.0. |

### 1.3a Notable Stock-Pipeline Gaps: STKY Duplicate-Load

**STKY Sticky Add-to-Cart** has both a TAE app embed block (`shopify://apps/stky-sticky-add-to-cart/blocks/satcb/...`) in `config/settings_data.json` **and** a legacy hardcoded `<script src=".../satcb.min.js?shop=creations-gdc.myshopify.com">` at line 969 of `layout/theme.liquid`. This causes duplicate initialization — the script loads twice per page. Cleanup is needed regardless of migration timing.

### 1.4 Body Footer (Lines 882–1121)

| Lines | Customization | Difficulty | Notes |
|---|---|---|---|
| 883 | `<body>` tag with `hairmnl-theme` class | **easy** | Used by custom-theme.css; needs port. |
| 889–893 | `thebackbar` template conditional for alternate header | **medium** | Custom header per template; needs OS 2.0 section group mapping. |
| 897 | `<noscript class="endOfLayoutContentX">` | **easy** | Performance marker; likely not needed in Dawn. |
| 907–909 | LimeSpot `<limespot>` element gated to non-customers | **medium** | App element; verify OS 2.0 LimeSpot embed. |
| 930 | `custom-theme.js` (deferred) — 9,118 lines of bundled custom JS | **hard** | Massive custom JS file including sticky-js library, custom behaviors. Needs complete rewrite for Dawn's ES module architecture. |
| 940–949 | DCL-wrapped timber hash/reset handlers | **easy** | Pipeline-specific; Dawn uses different JS framework. |
| 960–972 | Klaviyo form event tracking (open/submit/close → gtag) | **medium** | Custom analytics; needs port to Dawn's event system. |
| 975 | `{% render 'mbc-bundles' %}` — MBC Bundles app (19 lines) | **easy** | App snippet; verify OS 2.0 app. |
| 985–999 | Deferred shop.js (177KB, formerly render-blocking) | **medium** | Per-optimization deferral; Dawn loads scripts differently. |
| 1008 | `{% render 'web-vitals-reporter' %}` — RUM Core Web Vitals → GA4 (118 lines) | **medium** | Custom RUM; needs port to Dawn's theme scope. |
| 1024–1040 | Backbar account registration page DOM reorder (jQuery) | **medium** | Custom page styling; can be a standalone section in OS 2.0. |
| 1051–1083 | Judge.me carousel CSS + BOGOS promotion inline styles | **medium** | App-specific CSS; can be moved to custom CSS in OS 2.0 theme editor. |
| 1085 | Zapiet same-day pickup script (async) | **easy** | App script; OS 2.0 Zapiet manages this. |
| 1097–1117 | A11y fix: cc-dismiss aria-label sync (MutationObserver) | **easy** | Cookie bar fix; verify Nova GDPR app handles this in OS 2.0. |
| 1120 | `{% render 'freegifts-snippet-change' %}` — BOGOS/Secomapp (16 lines) | **easy** | App snippet; verify OS 2.0 BOGOS app. |

---

## Section 2: Custom Sections

### 2.1 Brand-Specific Collection Sections (31 total, ~52,500 LoC)

These are all variants of `collection-branded.liquid` (1,568 lines), each heavily customized for a specific brand line with hero banners, brand logos, curated product grids, and custom schema settings.

| Section | LoC | Purpose | Port Difficulty |
|---|---|---|---|
| collection-absolutrepair.liquid | 1,740 | L'Oréal Professionnel Absolut Repair | **medium** — needs OS 2.0 section schema + JSON template |
| collection-blondabsolu.liquid | 1,741 | L'Oréal Professionnel Blond Absolu | **medium** |
| collection-chronologiste.liquid | 1,741 | Kérastase Chromatique | **medium** |
| collection-densifique.liquid | 1,741 | Kérastase Densifique | **medium** |
| collection-discipline.liquid | 1,498 | Kérastase Discipline | **medium** |
| collection-elixir.liquid | 1,742 | Kérastase Elixir | **medium** |
| collection-specifique.liquid | 1,741 | Kérastase Spécifique | **medium** |
| collection-nutritive.liquid | 1,741 | Kérastase Nutritive | **medium** |
| collection-resistance.liquid | 1,742 | Kérastase Résistance | **medium** |
| collection-lorealprofessionnel.liquid | 1,810 | L'Oréal Professionnel (parent brand) | **medium** |
| collection-krsymbiose.liquid | 1,810 | Kérastase Symbiose | **medium** |
| collection-krchromaabsolu.liquid | 1,810 | Kérastase Chroma Absolu | **medium** |
| collection-krcurlmanifesto.liquid | 1,742 | Kérastase Curl Manifesto | **medium** |
| collection-krgenesis.liquid | 1,742 | Kérastase Genesis | **medium** |
| collection-krspecifique-divalent.liquid | 1,742 | Kérastase Spécifique Divalent | **medium** |
| collection-lp-vitamino.liquid | 1,810 | L'Oréal Professionnel Vitamino | **medium** |
| collection-lp-serioxyladvanced.liquid | 1,810 | L'Oréal Professionnel Serioxyl Advanced | **medium** |
| collection-lp-metaldetox.liquid | 1,810 | L'Oréal Professionnel Metal Detox | **medium** |
| collection-lp-styling.liquid | 1,742 | L'Oréal Professionnel Styling | **medium** |
| collection-lp-prolonger.liquid | 1,742 | L'Oréal Professionnel Pro Longer | **medium** |
| collection-lp-mythicoil.liquid | 1,742 | L'Oréal Professionnel Mythic Oil | **medium** |
| collection-lp-liss.liquid | 1,742 | L'Oréal Professionnel Liss Unlimited | **medium** |
| collection-lp-inforcer.liquid | 1,742 | L'Oréal Professionnel Inforcer | **medium** |
| collection-lp-silver.liquid | 1,741 | L'Oréal Professionnel Silver | **medium** |
| collection-lp-scalpadvanced.liquid | 1,741 | L'Oréal Professionnel Scalp Advanced | **medium** |
| collection-lp-instantclear.liquid | 1,741 | L'Oréal Professionnel Instant Clear | **medium** |
| collection-lp-serioxyl.liquid | 28 | L'Oréal Professionnel Serioxyl (minimal) | **easy** — likely redirect template |
| collection-lp-antidandruff.liquid | * | L'Oréal Professionnel Anti-Dandruff | **medium** |
| collection-branded.liquid | 1,568 | Base branded collection template | **medium** — parent for all above |
| collection-branded-subcollection.liquid | * | Branded sub-collection | **medium** |

**Key insight**: These 31 sections are all near-identical structure (brand hero → brand description → product grid → recommendation). In OS 2.0, they should be **consolidated into 1 reusable section** with JSON template variants — not ported as 31 separate sections. The `collection-branded.liquid` base (1,568 lines) is the canonical version; the per-brand variants only differ in `{% schema %}` settings (brand colors, logos, collection handles, hero images).

### 2.2 Other Custom Sections

| Section | LoC | Purpose | Port Difficulty |
|---|---|---|---|
| section-custom-content.liquid | 1,529 | Custom content bricks (image + text) | **medium** — Dawn has `custom-content.liquid`; settings need migration |
| section-double.liquid | 1,507 | Double-column section | **medium** — similar to Dawn `image-with-text` |
| section-recent-products.liquid | * | Recently viewed products | **medium** — Dawn has `recently-viewed-products`; needs schema port |
| thebackbar-master-header.liquid | 707 | Alternate header for The Back Bar template | **medium** — Dawn uses `header-group`; needs full rebuild |
| section-vertex-home-recommendations.liquid | 74 | Vertex AI homepage RFY/trending slot | **hard** — depends on custom metafield schema + vertex-rec-card snippet |

---

## Section 3: Custom Snippets

### 3.1 Performance & CLS Fix Snippets

| Snippet | LoC | Purpose | Exists in Pipeline 8/Dawn? | Tag |
|---|---|---|---|---|
| css-overrides.liquid | 621 | CLS fixes, a11y overrides, app CSS overrides | No — all custom | **need-port** |
| css-variables.liquid | 435 | CSS custom property definitions from settings | Yes — Dawn has its own `:root` variables | **need-port** (mapping needed) |
| article-content-with-img-dims.liquid | 213 | Injects width/height on article `<img>` tags from CDN URL patterns | No equivalent | **need-port** |
| critical-css.liquid | * | Inlined critical CSS | Dawn has own critical path strategy | **need-rebuild** |
| web-vitals-reporter.liquid | 118 | RUM: Core Web Vitals → GA4 dataLayer | No equivalent | **need-port** |
| font-settings-inline.liquid | 129 | Self-hosted Playfair Display @font-face declarations | Dawn uses Shopify font CDN | **can-drop** (if accepting CDN fonts) |

### 3.2 SEO & Structured Data Snippets

| Snippet | LoC | Purpose | Exists in Pipeline 8/Dawn? | Tag |
|---|---|---|---|---|
| canonical.liquid | 118 | Canonical URL management with handle overrides and collection query-string stripping | No — Dawn uses `{{ canonical_url }}` | **need-port** |
| hairsalon-schema.liquid | 109 | HairSalon JSON-LD for two Studio pages | No equivalent (custom business data) | **need-port** |
| pluginseo.liquid + 5 children | ~900+ | SmartSEO app (structured-data, page-title, meta-description, parse, langify, not-found) | App provides; Dawn has built-in SEO | **can-drop** |
| social-meta-tags.liquid | * | Open Graph + Twitter cards | Dawn has its own | **need-port** (if modified) |

### 3.3 App Integration Snippets

| Snippet | LoC | Purpose | Exists in Pipeline 8/Dawn? | Tag |
|---|---|---|---|---|
| loyaltylion.liquid | 133 | LoyaltyLion SDK embedding | App has OS 2.0 embed | **can-drop** |
| storepickup.liquid | 220 | Zapiet Store Pickup + Delivery widget | App has OS 2.0 embed | **can-drop** |
| bold-common.liquid | 133 | Bold app bootstrap | App has OS 2.0 embed | **can-drop** |
| swymSnippet.liquid | 206 | Swym wishlist integration | App has OS 2.0 embed | **can-drop** |
| swym-product-view.liquid | * | Swym product page event tracking | App has OS 2.0 embed | **can-drop** |
| judgeme_widgets.liquid | 126 | Judge.me review widget rendering | App has OS 2.0 embed | **can-drop** |
| judgeme_static_stars.liquid | * | Judge.me star rating badge (deferred loader pattern — loads after page render to reduce blocking) | App has OS 2.0 embed | **can-drop** |
| judgeme_all_reviews.liquid | * | Judge.me aggregate reviews page | App has OS 2.0 embed | **can-drop** |
| mbc-bundles.liquid | 19 | MBC Bundles app embed | App has OS 2.0 embed | **can-drop** |
| wc_cart.liquid | 431 | Wholesale Cart (BSS B2B) — BSS uninstalled | Dead code | **can-drop** |
| wsg-header.liquid | 357 | Wholesale header (BSS B2B) — BSS uninstalled | Dead code | **can-drop** |
| freegifts-snippet-change.liquid | 16 | BOGOS/Secomapp Free Gifts | App has OS 2.0 embed | **can-drop** |
| limespot.liquid | 40 | LimeSpot personalization SDK loader | App has OS 2.0 embed | **can-drop** |
| pro-blogger.liquid (11 files) | ~950+ | Pro Blogger blog enhancements (related products, related articles, shortcode, section wrapper) | App has OS 2.0 embed; also being replaced by Vertex AI | **can-drop** |

### 3.4 Custom Feature Snippets

| Snippet | LoC | Purpose | Exists in Pipeline 8/Dawn? | Tag |
|---|---|---|---|---|
| vertex-recommendations.liquid | 303 | Vertex AI product recs slot renderer (5 placements) | No — custom build | **need-rebuild** |
| vertex-rec-card.liquid | 134 | Single recommendation card for Vertex AI | No — custom build | **need-rebuild** |
| product-form.liquid | 292 | Modified product form with size chart, variant selection | Dawn has its own `product-form.liquid` | **need-port** |
| product-grid-item.liquid | 339 | Product card rendering for collection grids | Dawn has `card-product.liquid` | **need-port** |
| product-grid-item-branded.liquid | 213 | Branded variant of product card | No — custom | **need-rebuild** |
| cart-drawer.liquid | 227 | Slide-out cart drawer with free shipping progress | Dawn has its own cart drawer | **need-port** |
| collection-filters-sidebar.liquid | 242 | Collection page filter sidebar with custom filter UI | Dawn uses `facets.liquid` | **need-port** |
| upsell-product-list.liquid | 159 | Upsell product list rendering | No — custom | **need-rebuild** |
| upsell-product.liquid | 124 | Single upsell product card | No — custom | **need-rebuild** |

### 3.5 Modified Stock Snippets

| Snippet | LoC | Modified? | Notes |
|---|---|---|---|
| search-predictive.liquid | 132 | Likely stock + minor mods | Verify against Pipeline 6 original |
| filters.liquid | 133 | Likely stock + minor mods | Dawn uses `facets.liquid`; mapping needed |
| nav-item.liquid | 141 | Likely stock + minor mods | Dawn has different nav architecture |

---

## Section 4: CSS Overrides Detail

Source: `snippets/css-overrides.liquid` (621 lines). **18 override blocks** identified:

| # | Lines | Date/Bead | Description | OS 2.0 Implication |
|---|---|---|---|---|
| 1 | 2–8 | — | Header height pin (desktop 70px, mobile 60px) | Port to Dawn's `:root` CSS vars |
| 2 | 10–35 | 2026-04-28 A11y | Footer accordion `<button>` reset (was `<p>`, Lighthouse aria violation) | Dawn uses `<button>` by default — **can-drop** |
| 3 | 37–54 | 2026-04-28 CLS | Judge.me verified-by image dimension reservation (125×24px) | Reverify with OS 2.0 Judge.me embed |
| 4 | 56–95 | 2026-04-28→2026-05-01 CLS | PWA modal suppression (`display:none`) — Shop Sheriff app uninstalled | **can-drop** (app removed) |
| 5 | 97–145 | 2026-04-29 CLS | Blog article body image dimension reservation (`aspect-ratio`, `width`, `background`) | **need-port** — blog content images are universal |
| 6 | 147–163 | 2026-05-13 CLS (987) | Blog body iframe/video 16:9 containment | **need-port** |
| 7 | 165–198 | 2026-05-10 CLS (ojx) | Pro Blogger related-article thumbnail dimension reservation (1:1) | **can-drop** if Pro Blogger removed for Vertex |
| 8 | 200–228 | 2026-04-29 CLS | Judge.me medals wrapper CLS reservation (min-height 80px, visibility hidden) | Reverify with OS 2.0 Judge.me |
| 9 | 230–242 | 2026-05-10 CLS | Judge.me preview badge reservation (min-height 24px, min-width 100px) | Reverify with OS 2.0 Judge.me |
| 10 | 244–253 | 2026-05-01→2026-05-13 CLS | Free gifts container reservation (min-height 240px, 3 gift rows) | **need-port** — BOGOS app behavior |
| 11 | 255–271 | 2026-05-01 CLS (T8) | Flickity media thumb strip reservation (min-height 80px) | **need-port** — Dawn uses different media gallery |
| 12 | 273–318 | 2026-05-01→2026-05-13 CLS (T9) | Announcement bar + LoyaltyLion points-box CLS + ticker height lock | **need-port** — universal header patterns |
| 13 | 320–359 | 2026-05-10 CLS (kt0) | Desktop header `contain: layout` (hotfixed: removed `.header__wrapper` to unfreeze cart drawer) | **need-port** — kt0 containment audit critical for OS 2.0 |
| 14 | 361–376 | 2026-05-01 CLS (e4a-α) | PDP store pickup reservation (min-height 64px) | Reverify with OS 2.0 Zapiet |
| 15 | 378–396 | 2026-05-01 CLS (e4a-β) | PDP Flickity viewport height animation disable (`transition: none`) | **need-port** — media gallery behavior |
| 16 | 398–410 | 2026-05-02 CLS | Reamaze chat widget label (`position: fixed`) | Reverify with OS 2.0 Reamaze |
| 17 | 412–436 | 2026-05-02 CLS (fan) | Product price column reservation (min-height 44px, `contain: layout`) | **need-port** — now defensive; original BSS cause removed |
| 18 | 438–621 | 2026-05-01→2026-05-04 | 10 additional CLS/a11y fixes: recently-viewed section reservation, Klaviyo modal containment, LoyaltyLion popup containment, cookie bar positioning, BOGOS gift image dimensions, LimeSpot element sizing, and LoyaltyLion button contrast | Mix of **need-port** and **can-drop** (app-specific) |

### Summary CSS Override Categories

| Category | Count | Can Drop | Need Port | Need Rebuild |
|---|---|---|---|---|
| CLS layout shift fixes | 15 | 4 | 9 | 2 |
| A11y fixes | 2 | 1 | 1 | 0 |
| App-specific overrides | 5 | 5 | 0 | 0 |
| Header/cart behavior | 3 | 0 | 3 | 0 |

---

## Section 5: Custom CSS Variables

Source: `snippets/css-variables.liquid` (435 lines). This is **a modified version of the stock Pipeline 6 file** with these custom additions/bespoke tokens:

### 5.1 Stock Pipeline 6 Variables (Retained)

The majority of the file (lines 101–435) defines CSS custom properties from `settings_schema.json` — these are standard Pipeline 6 and will need mapping to Pipeline 8/Dawn's `:root` variable system. Key variable groups:

| Variable Group | Lines | Example Tokens | Notes |
|---|---|---|---|
| Color backgrounds | 124–127 | `---color-bg`, `---color-bg-accent` | 3-hyphen prefix (Pipeline specific) |
| Text colors | 130–135 | `---color-text-dark`, `---color-text`, `---color-text-light` | Need mapping to Dawn's `--color-foreground` etc. |
| Primary/secondary colors | 138–168 | `---color-primary`, `---color-primary-hover`, `---color-primary-fade` | Dawn uses `--color-btn-primary` etc. |
| Inverse colors | 192–255 | `---inverse-*` series | Pipeline-specific dark mode system |
| Typography | 364–426 | `---font-stack-body`, `---font-weight-body`, `---font-adjust-heading` | Dawn uses different variable names and unit system |
| Buttons | 351–362 | `---btn-border-color`, `---btn-bg-color`, `---btn-text-color` | Need mapping to Dawn button system |
| Product grid | 289 | `---product-grid-aspect-ratio` | Dawn uses `--ratio-container` |

### 5.2 HairMNL Custom Modifications

| Lines | Customization | Notes |
|---|---|---|
| 7–100 | Font weight resolution logic (base, heading, accent, product-heading font bold detection) | Extended from Pipeline 6 stock — adds `product_heading_font` variant and weight stepping logic |
| 77–99 | Custom heading/base/accent font family overrides (`use_custom_heading_font`, etc.) | Pipeline 6 stock but with `product_*` additions |
| 117–118 | `---color_video_bg` (poster background computation) | Stock Pipeline 6 |
| 417–424 | `---font-stack-product-heading`, `---font-weight-product-heading-bold`, `---font-adjust-product-heading` | **Custom**: HairMNL added a fourth font stack for product type headings |
| 431–434 | `{% if settings.high_contrast %} {% render 'css-variables-contrast' %} {% endif %}` | Conditional high-contrast mode variable overrides |

**Port assessment**: The `---` (triple-hyphen) variable naming and the custom product-heading font stack are Pipeline-6-specific. Dawn uses `--` (double-hyphen) convention and a different settings schema. Every variable needs mapping. The `css-variables-contrast.liquid` snippet (referenced but not audited) likely contains a dark-mode/inverse color override set.

---

## Section 6: Template Customizations

### 6.1 Collection Template Variants (28 files)

All follow the pattern `collection.{handle}.liquid` and point to their corresponding section. Example: `templates/collection.resistance.liquid` renders `sections/collection-resistance.liquid`.

**Assessment**: These are thin template wrappers (typically 5–8 lines) that reference their section. In OS 2.0, each becomes a JSON template in `templates/collection.{handle}.json` with section ordering. The actual section logic (hero, brand info, product grid) needs porting, not the template files.

| Template | LoC | Points to |
|---|---|---|
| collection.branded.liquid | ~5 | sections/collection-branded.liquid |
| collection.branded-subcollection.liquid | ~5 | sections/collection-branded.liquid |
| collection.lp-*.liquid (12) | ~5 each | sections/collection-lp-*.liquid |
| collection.kr*.liquid (5) | ~5 each | sections/collection-kr*.liquid |
| Other brand collections (9) | ~5 each | sections/collection-{brand}.liquid |

### 6.2 App-Specific Templates (can-drop)

| Template | LoC | Purpose | Tag |
|---|---|---|---|
| page.bss-b2b-wholesaler-1959.liquid | 104 | BSS B2B wholesaler page — app uninstalled | **can-drop** |
| page.avada-articles-tags.liquid | 16 | Avada SEO articles tags | **can-drop** |
| page.judgeme_all_reviews.liquid | 8 | Judge.me all reviews page | **can-drop** (app has OS 2.0 embed) |
| search.bss.b2b.liquid | 1 | BSS B2B search — app uninstalled | **can-drop** |

### 6.3 Product Form Modifications

`snippets/product-form.liquid` (292 lines) — modified from stock Pipeline 6. Key deviations from stock:
- Size chart modal integration
- Dynamic checkout button handling
- Selling plan group logic

In OS 2.0, this maps to Dawn's `product-form.liquid` snippet — the size chart modal pattern needs porting but the variant selection and selling plan logic are handled by Dawn's built-in components.

### 6.4 Gift Card Template

`templates/gift_card.liquid` (275 lines) — stock Pipeline 6 gift card template. Dawn has its own `gift_card.json` template. Verify schema settings.

---

## Section 7: JS Customizations

### 7.1 custom-theme.js (9,118 lines)

This is a **bundled/compiled** JS file containing:
- **sticky-js** library (~400 lines) — sticky element behavior
- **Numerous custom behaviors** mixed with Pipeline 6 DOM manipulation

The file is minified/compiled and not easily diffed against stock Pipeline 6 `theme.js`. Key observations from the source:
- Contains a `Sticky` class for sticky elements (product grid sidebar, ATC bar)
- Inherits heavily from Pipeline 6's `theme.js` architecture (Flickity, Drawer, Cart, etc.)

**Port assessment**: This needs a **complete rewrite** for Dawn's ES module architecture. Dawn uses `global.js` + section-scoped JS modules. The `sticky-js` library can be replaced by Dawn's built-in sticky behavior or Intersection Observer-based approach.

### 7.2 theme.dev.js and vendor.js

- `assets/theme.dev.js` — development version of Pipeline 6 theme.js
- `assets/vendor.js` — third-party dependencies (Flickity, photoswipe, etc.)

Both are Pipeline 6 stock; Dawn replaces them with Dawn's own `global.js` and `vendor.min.js`.

### 7.3 Inline JS in theme.liquid

| Block | Lines (approx.) | Purpose | OS 2.0 Port |
|---|---|---|---|
| Drawer-toggle capture interceptor | L537–550 | Capture-phase click handler for drawer toggle | Dawn has different drawer; needs rewrite |
| A/B testing framework | L629–656 | Cookie-based variant assignment, CSS class + dataLayer | Need port to custom JS or external tool |
| JS error tracking | L657–687 | `hairmnl_js_error` → dataLayer, throttled | Need port to Dawn global scope |
| Cart pre-init dispatcher | L719–726 | `theme:cart:init` on `pageshow` | Dawn has different cart architecture |
| Pro Blogger CSS defer interceptor | L745–796 | createElement override + MutationObserver | Can drop if Pro Blogger removed |
| Klaviyo form event tracking | L960–972 | form_open/form_submit/form_close → gtag | Need port |
| Backbar account registration reorder | L1024–1040 | jQuery DOM reorder for `/pages/the-backbar-account-registration` | Need section-based approach |
| Cookie bar aria-label fix | L1097–1117 | MutationObserver for `.cc-dismiss` | Reverify with OS 2.0 cookie app |

### 7.4 Vertex AI Integration (JS aspect)

- `snippets/vertex-recommendations.liquid` (303 lines) includes inline JS for scroll-snap rail navigation (~25 lines)
- `assets/vertex-recommendations.css` (599 lines) — styles for rec cards
- No external JS dependency; all CSS scroll-snap based

**Port assessment**: The Vertex AI system uses metafield-driven data (`product.metafields.vertex.recs`, `.similar`, `cart_recs`; `customer.metafields.vertex.recommended_for_you`; `shop.metafields.vertex.homepage_trending`). In OS 2.0, this becomes a custom section + block architecture. The Liquid rendering and scroll-snap approach can port directly; the metafield schema needs to be preserved.

---

## Section 8: Port Recommendation

### Summary Table

| Category | Count | Easy | Medium | Hard | Notes |
|---|---|---|---|---|---|
| layout/theme.liquid modifications | ~26 | 8 | 14 | 4 | Most are app embeds or perf optimizations |
| Custom collection sections | 31 | 0 | 31 | 0 | Consolidate into 1 parameterized section |
| Other custom sections | 4 | 0 | 2 | 2 | custom-content, double, thebackbar, vertex |
| CLS/a11y CSS overrides (18 blocks) | 18 | 4 | 12 | 2 | ~4 are for uninstalled apps (drop); rest need port |
| CSS variables mapping | 1 file | 0 | 1 | 0 | Variable name mapping `---` → `--` |
| App integration snippets (droppable) | 14 | 14 | 0 | 0 | All have OS 2.0 app embed equivalents |
| Custom feature snippets | 7 | 0 | 4 | 3 | Vertex, product-form, cart-drawer, grid items |
| SEO/structured data snippets | 7 | 3 | 2 | 0 | SmartSEO droppable; canonical+hairsalon need port |
| Blog/img processing snippets | 2 | 0 | 1 | 1 | article-content-with-img-dims needs Liquid parsing port |
| Template variants (collection) | 31 | 0 | 31 | 0 | JSON template migration |
| App templates (droppable) | 4 | 4 | 0 | 0 | BSS B2B, Avada, Judge.me |
| Inline JS blocks | ~8 | 1 | 4 | 3 | A/B framework, error tracking, Pro Blogger interceptor |
| custom-theme.js | 1 | 0 | 0 | 1 | Full rewrite for Dawn ES modules |
| Asset CSS splits | ~8 | 2 | 6 | 0 | Template-gated loads; Dawn has different approach |

### Final Recommendation

**Of ~75 customized files and ~19,000 bespoke LoC:**

- **~17 items can be dropped** (already redundant in Pipeline 8/Dawn or app has OS 2.0 embed): PWA modal CSS, BSS B2B snippets (wc_cart, wsg-header), all app integration snippets when apps are reinstalled via OS 2.0 app embeds (loyaltylion, storepickup, bold-common, swym, judgeme, mbc-bundles, freegifts, limespot, pro-blogger, pluginseo), and app-specific templates (bss-b2b, avada, judgeme, search.bss.b2b).

- **~46 items need porting** with moderate effort: All 31 brand collection sections (consolidatable to 1), the 18 CLS fix blocks in `css-overrides.liquid`, canonical URL management, hairsalon JSON-LD, product-form modifications, cart-drawer, collection filters, inline JS blocks (drawer interceptor, A/B framework, error tracking, Klaviyo tracking, backbar reorder), font variable mapping, and template-gated CSS splits.

- **~8 items need rebuilding** from scratch for Dawn's architecture: The `custom-theme.js` bundle (9,118 lines needs full rewrite), Vertex recommendations system (section + snippets), article LCP image extraction (Liquid parser), Pro Blogger CSS interceptor (may be moot if app removed), and the thebackbar header section.

**The highest-risk items are:**

1. **custom-theme.js** — 9,118 lines of bundled Pipeline 6 JS. Dawn uses a completely different ES module architecture. Every custom behavior (sticky elements, drawer interactions, Flickity overrides) needs identification and rewrite.

2. **CSS overrides** — 621 lines of CLS fixes targeting specific Pipeline 6 DOM structure (`.header__desktop`, `.announcement__wrapper`, `.product__price__wrap`, etc.). Every selector needs verification against Dawn's DOM class names.

3. **31 brand collection sections** — At ~1,740 lines each, these are the largest chunk of custom Liquid. They MUST be consolidated into a single parameterized section for OS 2.0, not ported individually.

**Recommended port sequence:**

1. **Phase 1 — Scaffold Dawn theme** with correct settings_data.json
2. **Phase 2 — Port structural elements**: canonical, css-variables mapping, header/footer/cart sections
3. **Phase 3 — Consolidate brand collections** into 1 parameterized section
4. **Phase 4 — Port CLS fixes** with updated selectors for Dawn's DOM
5. **Phase 5 — Rebuild custom-theme.js behaviors** as Dawn ES modules
6. **Phase 6 — Port Vertex AI** as custom section + block
7. **Phase 7 — Reinstall apps** via OS 2.0 app embeds (dropping all custom app snippets)
8. **Phase 8 — Regression test** all CLS fixes, drawer behavior, and rec placements
## Recent additions

Per CLAUDE.md customization-freeze rule: every NEW Pipeline 6 customization added
after 2026-05-02 must log here with file path, LoC, what it does, port difficulty,
and why no-op alternatives weren't sufficient.

| Date | bd | File | +LoC | What | Port difficulty | No-op alts considered |
|---|---|---|---|---|---|---|
| 2026-05-22 | oo57 | `sections/article.liquid` (lines ~282-311) | +27 | Moves LimeSpot `<limespot-container>` from end-of-body to before `#shopify-section-footer` on blog article pages. LimeSpot Personalizer admin's BlogArticle layout has empty `data-placement-sibling`, causing fallback append. | **Easy** — deletable on cutover if LimeSpot admin is properly configured during migration. The proper fix is the LimeSpot admin's Placement Sibling setting, which is theme-independent. | Option A (LimeSpot admin fix) was offered to the operator; they chose Option B (theme JS) for faster ship-from-session. The LimeSpot admin route remains the migration-target fix — this script becomes a no-op safe to delete once LimeSpot admin is set during cutover. |
| 2026-05-25 | oo57 (revised) | `sections/article.liquid` (lines ~282-298) | -27 / +3 | **Superseded the move-script.** Operator chose to remove LimeSpot recommendation sliders from blog articles entirely. JS observer + insertBefore replaced with a 3-line CSS rule (`body.template-article limespot-container { display: none !important; }`). Visual-only removal — LimeSpot JS/API requests still fire. | **Trivial** — pure CSS, ports as-is to OS 2.0 article template. Full byte cleanup is `hvoo` (LimeSpot uninstall) or a separate defer-guard. | N/A — operator already had the JS in place; this is a refactor-to-CSS for the same intent (no sliders on article pages), not a fresh customization. |
| 2026-05-30 | iaxt.1, iaxt.7 | `templates/llms.txt.liquid`, `templates/agents.md.liquid` | +151, +152 | Override Shopify's auto-generated `/llms.txt` + `/agents.md` (GEO / agent discovery). Each = Shopify default boilerplate reproduced verbatim + a "Featured Catalog" of 23 curated revenue-ranked URLs (6 concern + 7 brand collections, 5 hero PDPs, 5 guides). The two files are identical except the self-reference line. | **Easy** — special-template overrides, same pattern as seo-platform `robots.txt.liquid`. Delete the asset → Shopify's auto-generated default resumes; or re-push the template post-cutover. No DOM/JS/CSS coupling. | These ARE the no-op-friendly option (step 2): stock OS-2.0 customizable text-template overrides that survive migration as theme assets. FREEZE caveat: once the templates exist the endpoints stop auto-updating — refresh the UCP boilerplate by hand if Shopify bumps versions (noted in both file comments). |

## Recent additions (GEO Capitalize epic 0kv3)

| Date | File | LoC | What | Port difficulty | Why not a no-op |
|---|---|---|---|---|---|
| 2026-06-09 | snippets/salon-menu-schema.liquid + 1 render line in layout/theme.liquid | ~75 | GEO structured data (HairSalon + OfferCatalog of 29 priced services + BreadcrumbList) for the Azta partner-salon menu page — #1.1 traffic page, previously ZERO schema. bd 0kv3.1. | easy — gated snippet; port to OS-2.0 as a metaobject-driven section | Smart SEO does not emit Service/OfferCatalog for custom pages; theme snippet is the precedent (hairsalon-schema.liquid). NOTE: P8 layout/theme.liquid needs the `{% render 'salon-menu-schema' %}` line added at cutover. |
