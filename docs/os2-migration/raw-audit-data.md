# RAW AUDIT DATA - Pipeline 6.1.3 Customization Inventory

## 1. COMPLETE SECTIONS LIST WITH LINE COUNTS

### Stock Pipeline 6 Sections (Not Custom)
These appear to be standard Pipeline 6 sections based on naming and size:
- 797 sections/announcement.liquid (stock)
- 692 sections/header.liquid (stock, but customized - see theme.liquid analysis)
- 619 sections/product.liquid (stock, but likely customized)
- 575 sections/popups.liquid (stock)
- 544 sections/section-product.liquid (stock)
- 524 sections/main-bloggle-article.liquid (stock)
- 486 sections/section-contact.liquid (stock)
- 446 sections/article.liquid (stock)
- 446 sections/blog.liquid (stock)
- 351 sections/footer.liquid (stock)
- 306 sections/section-video.liquid (stock)
- 296 sections/section-slideshow.liquid (stock)
- 293 sections/section-accordion.liquid (stock)
- 291 sections/collection.liquid (stock)
- 288 sections/section-announcement.liquid (stock)
- 282 sections/section-blog.liquid (stock)
- 279 sections/section-columns.liquid (stock)
- 255 sections/section-blog-category.liquid (stock)
- 251 sections/page.liquid (stock)
- 250 sections/search.liquid (stock)
- 247 sections/section-banner-slider.liquid (stock)
- 244 sections/section-hero.liquid (stock)
- 239 sections/blog.liquid (stock)
- 230 sections/section-gallery.liquid (stock)
- 228 sections/section-icons.liquid (stock)
- 226 sections/section-collection-grid.liquid (stock)
- 226 sections/cart.liquid (stock)
- 224 sections/section-map.liquid (stock)
- 211 sections/section-richtext.liquid (stock)
- 191 sections/section-faq.liquid (stock)
- 185 sections/section-logos.liquid (stock)
- 182 sections/collection-hero.liquid (stock)
- 180 sections/list-collections.liquid (stock)
- 170 sections/judgeme_allReviewsPage.liquid (Judge.me stock)
- 167 sections/related.liquid (stock)
- 163 sections/section-collection.liquid (stock)
- 163 sections/password.liquid (stock)
- 162 sections/tousled-header.liquid (custom variant)
- 157 sections/section-page.liquid (stock)
- 157 sections/section-map-embed.liquid (stock)
- 152 sections/section-gallery-text.liquid (stock)
- 150 sections/section-collection-tabs.liquid (stock)
- 144 sections/collection-sub.liquid (stock)
- 133 sections/section-static-banner.liquid (stock)
- 130 sections/judgeme_AllReviewsPage_Slider.liquid (Judge.me stock)
- 113 sections/api-pickup-availability.liquid (stock API)
- 98 sections/section-collection-slider.liquid (stock)
- 88 sections/section-html.liquid (stock)
- 85 sections/section-recent-products.liquid (stock)
- 78 sections/apps.liquid (stock)
- 70 sections/menu-buttons.liquid (stock)
- 60 sections/section-newsletter.liquid (stock)
- 49 sections/main-register.liquid (stock)
- 46 sections/api-product-popdown.liquid (stock API)
- 37 sections/gift-card.liquid (stock)
- 35 sections/reviews.liquid (stock)
- 29 sections/judgeme_carousel_section.liquid (Judge.me stock)
- 20 sections/section-liquid.liquid (stock)
- 8 sections/404.liquid (stock)
- 5 sections/api-product-grid-item.liquid (stock API)
- 3 sections/api-cart-items.liquid (stock API)
- 2 sections/api-cart-subtotal.liquid (stock API)

### CUSTOM SECTIONS (Not in Stock Pipeline 6)

#### Brand-Specific Collection Sections (ALL CUSTOM - ~30 files, ~45,000 lines)
These are completely bespoke - Pipeline 6 doesn't have brand-specific collection sections:
- 1810 sections/collection-lp-vitamino.liquid - CUSTOM: L'Oréal Professionnel Vitamino
- 1810 sections/collection-lp-serioxyladvanced.liquid - CUSTOM: L'Oréal Professionnel Serioxyl Advanced
- 1810 sections/collection-lp-metaldetox.liquid - CUSTOM: L'Oréal Professionnel Metal Detox
- 1810 sections/collection-lorealprofessionnel.liquid - CUSTOM: L'Oréal Professionnel main
- 1810 sections/collection-krsymbiose.liquid - CUSTOM: Kérastase Symbiose
- 1810 sections/collection-krchromaabsolu.liquid - CUSTOM: Kérastase Chroma Absolu
- 1742 sections/collection-resistance.liquid - CUSTOM: Kérastase Resistance
- 1742 sections/collection-lp-styling.liquid - CUSTOM: L'Oréal Professionnel Styling
- 1742 sections/collection-lp-prolonger.liquid - CUSTOM: L'Oréal Professionnel Prolonger
- 1742 sections/collection-lp-mythicoil.liquid - CUSTOM: L'Oréal Professionnel Mythic Oil
- 1742 sections/collection-lp-liss.liquid - CUSTOM: L'Oréal Professionnel Liss
- 1742 sections/collection-lp-inforcer.liquid - CUSTOM: L'Oréal Professionnel Inforcer
- 1742 sections/collection-krspecifique-divalent.liquid - CUSTOM: Kérastase Spécifique Divalent
- 1742 sections/collection-krgenesis.liquid - CUSTOM: Kérastase Genesis
- 1742 sections/collection-krcurlmanifesto.liquid - CUSTOM: Kérastase Curl Manifesto
- 1742 sections/collection-elixir.liquid - CUSTOM: Kérastase Elixir
- 1741 sections/collection-specifique.liquid - CUSTOM: Kérastase Spécifique
- 1741 sections/collection-nutritive.liquid - CUSTOM: Kérastase Nutritive
- 1741 sections/collection-lp-silver.liquid - CUSTOM: L'Oréal Professionnel Silver
- 1741 sections/collection-lp-scalpadvanced.liquid - CUSTOM: L'Oréal Professionnel Scalp Advanced
- 1741 sections/collection-lp-instantclear.liquid - CUSTOM: L'Oréal Professionnel Instant Clear
- 1741 sections/collection-densifique.liquid - CUSTOM: Kérastase Densifique
- 1741 sections/collection-chronologiste.liquid - CUSTOM: Kérastase Chronologiste
- 1741 sections/collection-blondabsolu.liquid - CUSTOM: Kérastase Blond Absolu
- 1740 sections/collection-absolutrepair.liquid - CUSTOM: Kérastase Absolut Repair
- 1568 sections/collection-branded.liquid - CUSTOM: Generic branded collection
- 1498 sections/collection-discipline.liquid - CUSTOM: Kérastase Discipline
- 365 sections/collection-branded-subcollection.liquid - CUSTOM: Branded subcollection variant
- 28 sections/collection-lp-serioxyl.liquid - CUSTOM: L'Oréal Professionnel Serioxyl (smaller variant)

#### Vertex AI Custom Section
- 74 sections/section-vertex-home-recommendations.liquid - CUSTOM: Vertex AI homepage recommendations (Phase 1 work)

#### B2B/Portal Custom Sections
- 707 sections/thebackbar-master-header.liquid - CUSTOM: B2B portal header (The Back Bar)
- 59 sections/bss-b2b-wholesaler-form-1959.liquid - CUSTOM: B2B wholesaler form

#### App Integration Custom Sections
- 170 sections/judgeme_allReviewsPage.liquid - Judge.me (likely customized)
- 130 sections/judgeme_AllReviewsPage_Slider.liquid - Judge.me (likely customized)
- 29 sections/judgeme_carousel_section.liquid - Judge.me (likely customized)

#### Custom Page Sections
- 51 sections/section-page-judgeme-all-reviews.liquid - CUSTOM: Judge.me reviews page
- 51 sections/cross-post-blogs.liquid - CUSTOM: Cross-blog posting

## 2. COMPLETE SNIPPETS LIST WITH LINE COUNTS

### STOCK PIPELINE 6 SNIPPETS (Not Custom)
These appear to be standard Pipeline 6 snippets:
- 431 snippets/wc_cart.liquid (WooCommerce cart - stock)
- 379 snippets/pluginseo-structured-data.liquid (PluginSEO - stock)
- 357 snippets/wsg-header.liquid (WSG - stock)
- 339 snippets/product-grid-item.liquid (stock, but likely customized)
- 294 snippets/pro-blogger.snippet.related-products.liquid (Pro Blogger - stock)
- 294 snippets/pluginseo-parse.liquid (PluginSEO - stock)
- 292 snippets/product-form.liquid (stock, but customized)
- 244 snippets/product-tabs.liquid (stock)
- 242 snippets/collection-filters-sidebar.liquid (stock)
- 227 snippets/cart-drawer.liquid (stock, but customized)
- 220 snippets/storepickup.liquid (Zapiet - stock)
- 213 snippets/product-grid-item-branded.liquid (stock variant)
- 213 snippets/article-content-with-img-dims.liquid (stock)
- 206 snippets/swymSnippet.liquid (SWYM - stock)
- 177 snippets/cart-line-items.liquid (stock)
- 162 snippets/pro-blogger.snippet.related-articles.liquid (Pro Blogger - stock)
- 160 snippets/pro-blogger.snippet.related-product-articles.liquid (Pro Blogger - stock)
- 160 snippets/collections-sidebar.liquid (stock)
- 159 snippets/upsell-product-list.liquid (stock)
- 141 snippets/snippet-tag-lists.liquid (stock)
- 141 snippets/nav-item.liquid (stock)
- 133 snippets/image-fill.liquid (stock)
- 133 snippets/filters.liquid (stock)
- 133 snippets/bold-common.liquid (Bold - stock)
- 132 snippets/search-predictive.liquid (stock)
- 130 snippets/pro-blogger.shortcode.liquid (Pro Blogger - stock)
- 129 snippets/font-settings-inline.liquid (stock)
- 126 snippets/judgeme_widgets.liquid (Judge.me - stock)
- 124 snippets/upsell-product.liquid (stock)
- 119 snippets/pluginseo-page-title.liquid (PluginSEO - stock)
- 118 snippets/canonical.liquid (stock)
- 114 snippets/wc_product_json.liquid (WooCommerce - stock)
- 109 snippets/hairsalon-schema.liquid (stock)
- 108 snippets/social-meta-tags.liquid (stock)
- 108 snippets/pluginseo-meta-description.liquid (PluginSEO - stock)
- 104 snippets/hero.liquid (stock)
- 102 snippets/wsg-transitions.liquid (WSG - stock)
- 100 snippets/tousled-nav-item-mobile.liquid (stock)
- 94 snippets/video-popup.liquid (stock)
- 90 snippets/cart-shipping.liquid (stock)
- 87 snippets/nav-item-mobile.liquid (stock)
- 86 snippets/custom-fonts.liquid (stock)
- 77 snippets/membership-product-callbacks.liquid (stock)
- 76 snippets/product-title-price.liquid (stock)
- 75 snippets/media.liquid (stock)
- 66 snippets/newsletter-form.liquid (stock)
- 65 snippets/pluginseo-langify.liquid (PluginSEO - stock)
- 64 snippets/animated-icon.liquid (stock)
- 63 snippets/starapps-core.liquid (StarApps - stock)
- 59 snippets/subscription-form.liquid (stock)
- 57 snippets/pro-blogger.snippet.related-item.liquid (Pro Blogger - stock)
- 57 snippets/header-block.liquid (stock)
- 55 snippets/collection-grid-item.liquid (stock)
- 53 snippets/product-labels.liquid (stock)
- 53 snippets/pro-blogger.snippet.sale_icon.liquid (Pro Blogger - stock)
- 52 snippets/ufe-offer.liquid (stock)
- 52 snippets/article-grid-item.liquid (stock)
- 50 snippets/wsg-status.liquid (WSG - stock)
- 50 snippets/swym-product-view.liquid (SWYM - stock)
- 49 snippets/pagination-custom.liquid (stock)
- 48 snippets/select-currency.liquid (stock)
- 48 snippets/pro-blogger.snippet.score_sorting.liquid (Pro Blogger - stock)
- 47 snippets/collection-sorting.liquid (stock)
- 43 snippets/wishlisthero-collection-product.liquid (Wishlist Hero - stock)
- 43 snippets/judgeme_static_stars.liquid (Judge.me - stock)
- 41 snippets/image-zoom.liquid (stock)
- 40 snippets/limespot.liquid (LimeSpot - stock, but customized)
- 40 snippets/collection-sorting-custom.liquid (stock)
- 37 snippets/zoom-pswp.liquid (stock)
- 36 snippets/onboarding-product.liquid (stock)
- 32 snippets/search-bar.liquid (stock)
- 32 snippets/search-bar-mobile.liquid (stock)
- 32 snippets/product-tabs-v1.liquid (stock)
- 30 snippets/pro-blogger.snippet.related-products-mid.liquid (Pro Blogger - stock)
- 29 snippets/social-icon.liquid (stock)
- 28 snippets/bgset.liquid (stock)
- 27 snippets/select-locale.liquid (stock)
- 26 snippets/social-sharing.liquid (stock)
- 26 snippets/pluginseo.liquid (PluginSEO - stock)
- 25 snippets/onboarding-product-grid-item.liquid (stock)
- 24 snippets/starapps-product-json.liquid (StarApps - stock)
- 23 snippets/collection-row.liquid (stock)
- 20 snippets/product-rating.liquid (stock)
- 20 snippets/pluginseo-not-found.liquid (PluginSEO - stock)
- 19 snippets/mbc-bundles.liquid (MBC - stock)
- 18 snippets/template-swatch.liquid (stock)
- 18 snippets/comment.liquid (stock)
- 16 snippets/freegifts-snippet-change.liquid (BOGOS - stock)
- 16 snippets/collection-slider.liquid (stock)
- 15 snippets/products-recommendation.liquid (stock)
- 14 snippets/pro-blogger.snippet.image-captions.liquid (Pro Blogger - stock)
- 14 snippets/judgeme_all_reviews.liquid (Judge.me - stock)
- 13 snippets/onboarding-empty-collection.liquid (stock)
- 13 snippets/cart-empty.liquid (stock)
- 12 snippets/wishlisthero-header-icon.liquid (Wishlist Hero - stock)
- 12 snippets/tags-article.liquid (stock)
- 12 snippets/product-info.liquid (stock)
- 11 snippets/products-recently-viewed.liquid (stock)
- 11 snippets/cart-subtotal.liquid (stock)
- 10 snippets/product-grid-item-branded-subcollection.liquid (stock)
- 10 snippets/css-variables-contrast.liquid (stock)
- 8 snippets/pro-blogger.snippet.related-item-rating.liquid (Pro Blogger - stock)
- 6 snippets/wsg-dependencies.liquid (WSG - stock)
- 6 snippets/pro-blogger.snippet.pinterest-pins.liquid (Pro Blogger - stock)
- 5 snippets/wishlisthero-custom-button.liquid (Wishlist Hero - stock)
- 5 snippets/section-static-banner.liquid (stock)
- 5 snippets/ly-global.liquid (LoyaltyLion - stock)
- 5 snippets/icon-error.liquid (stock icon)
- 3 snippets/wsg-col-json.liquid (WSG - stock)
- 3 snippets/shop-sheriff-pwa.liquid (Shop Sheriff - stock)
- 3 snippets/pro-blogger-section-wrapper.liquid (Pro Blogger - stock)
- 1 snippets/sca-aff-refer-customer.liquid (BOGOS - stock)
- 1 snippets/icon-clock.liquid (stock icon)
- 0 snippets/storepickup-addons.liquid (Zapiet - stock, empty)
- 0 snippets/starapps-language-meta.liquid (StarApps - stock, empty)
- 0 snippets/product_infox.liquid (stock, empty)
- 0 snippets/oxi-social-login.liquid (Oxi - stock, empty)
- 0 snippets/icon-zoom.liquid (stock icon, empty)
- 0 snippets/icon-youtube.liquid (stock icon, empty)
- 0 snippets/icon-water.liquid (stock icon, empty)
- 0 snippets/icon-vimeo.liquid (stock icon, empty)
- 0 snippets/icon-twitter.liquid (stock icon, empty)
- 0 snippets/icon-tumblr.liquid (stock icon, empty)
- 0 snippets/icon-truck.liquid (stock icon, empty)
- 0 snippets/icon-tiktok.liquid (stock icon, empty)
- 0 snippets/icon-tags.liquid (stock icon, empty)
- 0 snippets/icon-sync.liquid (stock icon, empty)
- 0 snippets/icon-support-headphones.liquid (stock icon, empty)
- 0 snippets/icon-store.liquid (stock icon, empty)
- 0 snippets/icon-sort.liquid (stock icon, empty)
- 0 snippets/icon-snapchat.liquid (stock icon, empty)
- 0 snippets/icon-shipment.liquid (stock icon, empty)
- 0 snippets/icon-shipment-world.liquid (stock icon, empty)
- 0 snippets/icon-send.liquid (stock icon, empty)
- 0 snippets/icon-search.liquid (stock icon, empty)
- 0 snippets/icon-scroll-down.liquid (stock icon, empty)
- 0 snippets/icon-rss.liquid (stock icon, empty)
- 0 snippets/icon-reset.liquid (stock icon, empty)
- 0 snippets/icon-rating.liquid (stock icon, empty)
- 0 snippets/icon-play.liquid (stock icon, empty)
- 0 snippets/icon-play-thumb.liquid (stock icon, empty)
- 0 snippets/icon-pinterest.liquid (stock icon, empty)
- 0 snippets/icon-phone.liquid (stock icon, empty)
- 0 snippets/icon-payment.liquid (stock icon, empty)
- 0 snippets/icon-out-of-stock.liquid (stock icon, empty)
- 0 snippets/icon-nav.liquid (stock icon, empty)
- 0 snippets/icon-medium.liquid (stock icon, empty)
- 0 snippets/icon-media-video.liquid (stock icon, empty)
- 0 snippets/icon-media-model.liquid (stock icon, empty)
- 0 snippets/icon-lock-window.liquid (stock icon, empty)
- 0 snippets/icon-lock-shield.liquid (stock icon, empty)
- 0 snippets/icon-lock-card.liquid (stock icon, empty)
- 0 snippets/icon-linkedin.liquid (stock icon, empty)
- 0 snippets/icon-leaf.liquid (stock icon, empty)
- 0 snippets/icon-instagram.liquid (stock icon, empty)
- 0 snippets/icon-in-stock.liquid (stock icon, empty)
- 0 snippets/icon-grid-4.liquid (stock icon, empty)
- 0 snippets/icon-grid-3.liquid (stock icon, empty)
- 0 snippets/icon-grid-2.liquid (stock icon, empty)
- 0 snippets/icon-grid-1.liquid (stock icon, empty)
- 0 snippets/icon-filter.liquid (stock icon, empty)
- 0 snippets/icon-facebook.liquid (stock icon, empty)
- 0 snippets/icon-email.liquid (stock icon, empty)
- 0 snippets/icon-earth.liquid (stock icon, empty)
- 0 snippets/icon-dollar.liquid (stock icon, empty)
- 0 snippets/icon-close.liquid (stock icon, empty)
- 0 snippets/icon-close-small.liquid (stock icon, empty)
- 0 snippets/icon-check-slim.liquid (stock icon, empty)
- 0 snippets/icon-chat.liquid (stock icon, empty)
- 0 snippets/icon-cart.liquid (stock icon, empty)
- 0 snippets/icon-cart-message.liquid (stock icon, empty)
- 0 snippets/icon-cart-check.liquid (stock icon, empty)
- 0 snippets/icon-box.liquid (stock icon, empty)
- 0 snippets/icon-bin.liquid (stock icon, empty)
- 0 snippets/icon-basket-return.liquid (stock icon, empty)
- 0 snippets/icon-basket-like.liquid (stock icon, empty)
- 0 snippets/icon-award.liquid (stock icon, empty)
- 0 snippets/icon-arrow-small-right.liquid (stock icon, empty)
- 0 snippets/icon-arrow-small-left.liquid (stock icon, empty)
- 0 snippets/icon-arrow-right-long.liquid (stock icon, empty)
- 0 snippets/icon-arrow-medium-right.liquid (stock icon, empty)
- 0 snippets/icon-arrow-medium-left.liquid (stock icon, empty)
- 0 snippets/icon-arrow-long-left.liquid (stock icon, empty)
- 0 snippets/icon-arrow-down.liquid (stock icon, empty)
- 0 snippets/icon-arrow-circle-right.liquid (stock icon, empty)
- 0 snippets/icon-arrow-circle-left.liquid (stock icon, empty)
- 0 snippets/icon-animal.liquid (stock icon, empty)
- 0 snippets/icon-account.liquid (stock icon, empty)
- 0 snippets/critical-css.liquid (stock, empty)
- 0 snippets/code-customizer-header.liquid (stock, empty)

### CUSTOM SNIPPETS (Added/Modified Beyond Stock Pipeline 6)

#### Vertex AI Snippets (Phase 1 - ALL CUSTOM)
- 303 snippets/vertex-recommendations.liquid - CUSTOM: Universal recs renderer (PDP, cart, home)
- 134 snippets/vertex-rec-card.liquid - CUSTOM: Individual recommendation card component
- 95 snippets/vertex-preview-toolbar.liquid - CUSTOM: Preview mode UI for theme editor
- 83 snippets/vertex-buy-it-again.liquid - CUSTOM: "Buy it again" recommendations

#### Performance & CLS Fixes (ALL CUSTOM)
- 620 snippets/css-overrides.liquid - CUSTOM: 20+ CLS fixes + a11y improvements
- 435 snippets/css-variables.liquid - CUSTOM: Theme settings → CSS variables (enhanced)
- 118 snippets/web-vitals-reporter.liquid - CUSTOM: Core Web Vitals → GA4 reporting

#### App Embeds & Integrations (CUSTOM/MODIFIED)
- 133 snippets/loyaltylion.liquid - CUSTOM: LoyaltyLion integration
- 83 snippets/limespot-ghost-placeholder.liquid - CUSTOM: LimeSpot placeholder
- 83 snippets/feature-flags.liquid - CUSTOM: Feature flag system
- 16 snippets/freegifts-snippet-change.liquid - CUSTOM: BOGOS integration
- 19 snippets/mbc-bundles.liquid - CUSTOM: MBC bundles integration
- 5 snippets/ly-global.liquid - CUSTOM: LoyaltyLion global

#### Blog & Content (CUSTOM/MODIFIED)
- 213 snippets/article-content-with-img-dims.liquid - CUSTOM: Blog image dimension handling
- 130 snippets/pro-blogger.shortcode.liquid - CUSTOM: Pro Blogger shortcodes
- 162 snippets/pro-blogger.snippet.related-articles.liquid - CUSTOM: Pro Blogger related articles
- 160 snippets/pro-blogger.snippet.related-product-articles.liquid - CUSTOM: Pro Blogger product articles
- 141 snippets/pro-blogger.snippet.related-products.liquid - CUSTOM: Pro Blogger related products
- 57 snippets/pro-blogger.snippet.related-item.liquid - CUSTOM: Pro Blogger related item
- 53 snippets/pro-blogger.snippet.sale_icon.liquid - CUSTOM: Pro Blogger sale icon
- 48 snippets/pro-blogger.snippet.score_sorting.liquid - CUSTOM: Pro Blogger score sorting
- 30 snippets/pro-blogger.snippet.related-products-mid.liquid - CUSTOM: Pro Blogger mid-article products
- 14 snippets/pro-blogger.snippet.image-captions.liquid - CUSTOM: Pro Blogger image captions
- 8 snippets/pro-blogger.snippet.related-item-rating.liquid - CUSTOM: Pro Blogger item rating
- 6 snippets/pro-blogger.snippet.pinterest-pins.liquid - CUSTOM: Pro Blogger Pinterest pins
- 3 snippets/pro-blogger-section-wrapper.liquid - CUSTOM: Pro Blogger section wrapper

#### Custom App Integrations
- 104 snippets/hairsalon-schema.liquid - CUSTOM: Hair salon schema markup
- 102 snippets/wsg-transitions.liquid - CUSTOM: WSG transitions
- 100 snippets/tousled-nav-item-mobile.liquid - CUSTOM: Tousled mobile nav
- 50 snippets/wsg-status.liquid - CUSTOM: WSG status
- 6 snippets/wsg-dependencies.liquid - CUSTOM: WSG dependencies
- 3 snippets/wsg-col-json.liquid - CUSTOM: WSG collection JSON

#### Custom Icons (CUSTOM - not stock Pipeline 6)
- 5 snippets/icon-error.liquid - CUSTOM icon
- 1 snippets/icon-clock.liquid - CUSTOM icon

#### REMOVED/ORPHANED SNIPPETS (Can Drop - Already Removed from Code)
- bss-b2b-*.liquid (43 files, ~2,000 lines - BSS B2B Lock/Solution removed)
- bsscommerce-*.liquid (13 files - BSS Commerce removed)
- smile-initializer.liquid (Smile.io uninstalled)
- subscribe-it-helper.liquid (Subscribe It uninstalled)
- hextom_ctb_main.liquid (Hextom uninstalled)
- treedify_script.liquid (Treedify uninstalled)
- gsf-conversion-pixels.liquid (Google Shopping Feed uninstalled)
- aaa-announcementbar-configuration.liquid (AAA Announcement Bar uninstalled)

## 3. LAYOUT/THEME.LIQUID - EXHAUSTIVE CUSTOMIZATION LIST

### Header Optimizations
1. **Lines 2-9**: Removed duplicate bsscommerce_login_require (2026-04-27)
   - WHAT: Removed redundant snippet include
   - WHY: Halves Liquid execution cost, removes dead HTML

2. **Lines 17-24**: Deferred bss-hide-variant.css via media=print swap
   - WHAT: Changed <link> to media="print" with onload swap
   - WHY: Was render-blocking 150ms, now loads async

3. **Lines 31-36**: Removed Hotjar tracking
   - WHAT: Removed Hotjar script and preconnect
   - WHY: Team confirmed not in use

4. **Lines 55-60**: Removed Google Fonts preconnects
   - WHAT: Removed fonts.googleapis.com and fonts.gstatic.com preconnects
   - WHY: Playfair Display now self-hosted

### Performance: Preloads & Deferrals
5. **Lines 103-116**: Preload vendor.js, theme.js, theme.css, custom-theme.css
   - WHAT: Added <link rel="preload" as="script/style"> for critical assets
   - WHY: Reduces resource discovery time

6. **Lines 117-124**: Deferred tiny.content.min.css
   - WHAT: media="print" + onload swap pattern
   - WHY: Was render-blocking 600ms

7. **Lines 125-137**: Bundled 4 CSS files into deferred-extras.css
   - WHAT: bcpo, font-awesome, bold-upsell x2 bundled into one file
   - WHY: Reduces style recalc events (252 rules → 1 fetch)

8. **Lines 354-357**: Deferred theme.css + custom-theme.css
   - WHAT: media="print" + onload swap
   - WHY: Prevents render blocking

9. **Lines 383-413**: Gated per-template CSS
   - WHAT: plyr.css, pswp.css, model_viewer.css only load on product/collection
   - WHY: Saves ~9KB on homepage, ~4KB on cart

### App Embed Cleanups
10. **Lines 163-183**: Gated LimeSpot SDK to non-customers/ templates
    - WHAT: Wrapped {% include 'limespot' %} in {% unless template contains 'customers/' %}
    - WHY: SDK loads 300KB but doesn't render on customer-area pages

11. **Lines 185**: Removed Treedify snippet
    - WHAT: Removed treedify_script render
    - WHY: Treedify uninstalled (issue ijh)

12. **Lines 525-546**: Removed Judge.me manual render
    - WHAT: Removed {% render 'judgeme' %} calls
    - WHY: Judge.me app auto-injects identical code via content_for_header

13. **Lines 552-556**: Removed GSF conversion pixels
    - WHAT: Removed gsf-conversion-pixels include
    - WHY: Google Shopping Feed app uninstalled

14. **Lines 857-866**: Removed AAA Announcement Bar
    - WHAT: Removed aaa-announcementbar-configuration + aio_stats_lib_v1.min.js
    - WHY: AAA Announcement Bar app uninstalled

15. **Lines 868-875**: Removed BSS Product Labels configs
    - WHAT: Removed bss-b2b-product-labels-configs include
    - WHY: BSS Product Labels app never installed, wasted Liquid execution

### DNS Prefetching (Lines 82-90)
- **Lines 82-90**: Added 9 dns-prefetch hints
- WHAT: <link rel="dns-prefetch" href="..."> for:
  - www.googletagmanager.com (GTM)
  - cdn.reamaze.com (Reamaze chat)
  - edge.personalizer.io (LimeSpot)
  - sdk-static.loyaltylion.net (LoyaltyLion)
  - static.klaviyo.com (Klaviyo)
  - tracking.aws.judge.me (Judge.me)
  - analytics.tiktok.com (TikTok Pixel)
  - satcb.azureedge.net (Same-day store pickup)
  - searchanise-ef84.kxcdn.com (Searchanise CDN)
- WHY: Saves 50-150ms on first request to each origin

### Custom Script Blocks
16. **Lines 537-549**: Drawer-toggle click intercept (kt0 fix)
    - WHAT: Capture-phase listener on [data-drawer-toggle]
    - WHY: Prevents cart drawer from navigating to /cart page when theme.js fails to load

17. **Lines 599-686**: JS error tracking → GTM
    - WHAT: window.onerror + unhandledrejection handlers
    - WHY: Tracks uncaught exceptions to GA4, throttled to 10 errors/session

18. **Lines 629-656**: A/B testing framework
    - WHAT: Cookie-based A/B test assignment + dataLayer pushes
    - WHY: Foundation for theme-side experiments (currently no tests defined)

19. **Lines 745-796**: Pro Blogger CSS defer guard
    - WHAT: MutationObserver + createElement override
    - WHY: Intercepts problogger.css and defers it via media=print swap

20. **Lines 1037-1040**: BSS B2B custom styling (removed 2026-05-14)
    - WHAT: jQuery-based styling for /pages/the-backbar-account-registration
    - WHY: BSS B2B uninstalled, removed in later commit

21. **Lines 1097-1118**: Cookie bar a11y fix
    - WHAT: MutationObserver syncs aria-label to button text
    - WHY: Fixes Lighthouse label-content-name-mismatch for Nova EU Cookie Bar

### Image Preloading
22. **Lines 187-204**: PDP featured image preload with srcset
    - WHAT: <link rel="preload" as="image" href="..." imagesrcset="...">
    - WHY: Preloads LCP image during HTML parse (before CSS/JS)

23. **Lines 220-231**: Article hero image preload
    - WHAT: Preload for article.image on blog article pages
    - WHY: GA4 showed 40-88% poor LCP on hair-education blog

24. **Lines 260-287**: Article body first-image preload
    - WHAT: Extracts first <img src=> from article.content via Liquid string split
    - WHY: Covers cases where article.image is blank or hero block is hidden

### App Gating
25. **Lines 837-839**: Gated Zapiet storepickup to product/cart only
    - WHAT: {% if template contains 'product' or template == 'cart' %}
    - WHY: Saves 9KB CSS + 90KB JS on 85% of pageviews

26. **Lines 958-974**: Klaviyo signup event tracking
    - WHAT: window.addEventListener("klaviyoForms", ...) → gtag()
    - WHY: Tracks form open/submit/close events in GA4

27. **Lines 999-1000**: Deferred shop.js
    - WHAT: Changed <script> to defer="defer"
    - WHY: Was only render-blocking script (177KB)

### Additional Customizations
28. **Lines 125**: {% include 'pro-blogger-section-wrapper' %}
    - WHAT: Pro Blogger wrapper include
    - WHY: Blog integration

29. **Lines 151**: {% include 'shop-sheriff-pwa' %}
    - WHAT: Shop Sheriff PWA include
    - WHY: PWA install prompt (though PWA modal is hidden via CSS)

30. **Lines 289-296**: Favicon handling
    - WHAT: Conditional favicon with data: fallback
    - WHY: Prevents 404 when settings.favicon is blank

31. **Lines 500-505**: Removed lazysizes.js
    - WHAT: Removed preload and script tag
    - WHY: Migrated to native loading="lazy"

32. **Lines 699-700**: Deferred jQuery
    - WHAT: Changed jQuery.min.js to defer="defer"
    - WHY: Was render-blocking 84KB

33. **Lines 719-726**: Cart pre-init dispatcher
    - WHAT: window.onpageshow → dispatchEvent('theme:cart:init')
    - WHY: Pre-fetches cart data before drawer opens

34. **Lines 825**: {% render 'bold-common' %}
    - WHAT: Bold apps common snippet
    - WHY: Bold subscriptions/upsells

35. **Lines 1002-1008**: Web Vitals reporter
    - WHAT: {% render 'web-vitals-reporter' %}
    - WHY: Core Web Vitals → GA4 reporting

36. **Lines 1020-1040**: BSS B2B registration page styling (removed)
    - WHAT: jQuery-based DOM manipulation for specific page
    - WHY: BSS B2B uninstalled

**TOTAL theme.liquid customizations**: 40+ distinct modifications

## 4. CSS-OVERRIDES.LIQUID - ALL BLOCKS WITH DATES AND DESCRIPTIONS

### Block 1: Footer Accordion Button Reset (Lines 10-34)
- **Date**: 2026-04-28
- **bd ref**: (none, a11y fix)
- **Description**: Changes .footer__title from <p> to <button> for proper ARIA semantics
- **Lines**: 25

### Block 2: Judge.me Verified Logo Dimensions (Lines 37-54)
- **Date**: 2026-04-28
- **bd ref**: (none, CLS fix)
- **Description**: Reserves 125x24 space for Judge.me "Verified by" logo to prevent layout shift
- **Lines**: 18

### Block 3: PWA Modal Containment (Lines 56-95)
- **Date**: 2026-04-28 (updated 2026-05-01, 2026-05-11)
- **bd ref**: (none, CLS fix)
- **Description**: Hides #pwa-modal with display:none to prevent massive CLS from Shop Sheriff PWA prompt
- **Lines**: 40
- **Notes**: kt0-OK per comment (no containing block issues)

### Block 4: Blog Image Aspect-Ratio (Lines 97-145)
- **Date**: 2026-04-29
- **bd ref**: (none, CLS fix)
- **Description**: Adds aspect-ratio: auto 16/9 to unsized blog images to prevent 0→full-height shifts
- **Lines**: 49
- **Impact**: Fixed 49-55% poor CLS on top blog posts

### Block 5: Blog Iframe/Video Aspect-Ratio (Lines 147-163)
- **Date**: 2026-05-13
- **bd ref**: hairmnl-theme-987
- **Description**: Adds aspect-ratio: 16/9 to iframe/video embeds in blog content
- **Lines**: 17

### Block 6: Pro Blogger Thumbnails (Lines 165-187)
- **Date**: 2026-05-10
- **bd ref**: hairmnl-theme-ojx
- **Description**: Adds aspect-ratio: 1/1 to Pro Blogger related-item thumbnails
- **Lines**: 23
- **Impact**: Fixed 0.52 CLS on purple-vs-blue-shampoo-philippines

### Block 7: Judge.me Medals Wrapper (Lines 200-228)
- **Date**: 2026-04-29
- **bd ref**: (none, CLS fix)
- **Description**: Forces .jdgm-medals-wrapper.jdgm-hidden to display:block + visibility:hidden
- **Lines**: 29
- **Impact**: Fixed 49.1% poor CLS on Wella PDP

### Block 8: Judge.me Preview Badge (Lines 230-242)
- **Date**: 2026-05-10
- **bd ref**: hairmnl-theme-z9y
- **Description**: Reserves min-height:24px for .jdgm-prev-badge to prevent top-of-PDP shift
- **Lines**: 13

### Block 9: Cart Freegifts Container (Lines 244-253)
- **Date**: 2026-04-29 (updated 2026-05-01, 2026-05-13)
- **bd ref**: T2, 1pi, hod, hairmnl-theme-987
- **Description**: Reserves 240px for #freegifts-main-page-container
- **Lines**: 10
- **Evolution**: 80px → 160px → 240px (3 rows)

### Block 10: PDP Flickity Thumbs (Lines 255-271)
- **Date**: 2026-05-01
- **bd ref**: T8
- **Description**: Adds min-height:80px to .media__thumb__wrapper to prevent collapse during Flickity init
- **Lines**: 17

### Block 11: Header CLS Fixes (Lines 273-305)
- **Date**: 2026-05-01
- **bd ref**: T9, e4a-α
- **Description**: Two fixes:
  - min-height:36px on .announcement__wrapper
  - contain:layout on .points-box (LoyaltyLion)
- **Lines**: 33

### Block 12: Announcement Bar Ticker (Lines 307-318)
- **Date**: 2026-05-13
- **bd ref**: hairmnl-theme-7i0
- **Description**: Pins ticker frame height to prevent FOUT shifts
- **Lines**: 12

### Block 13: Desktop Header Containment (Lines 320-359)
- **Date**: 2026-05-10 (hotfix 2026-05-11)
- **bd ref**: kt0
- **Description**: contain:layout on header.theme__header (NOT .header__wrapper due to kt0 regression)
- **Lines**: 40
- **Impact**: Fixed cart-drawer containing block trap

### Block 14: Store Pickup Widget (Lines 361-376)
- **Date**: 2026-05-01
- **bd ref**: e4a-β
- **Description**: Reserves 64px for .product__pickup (Zapiet widget)
- **Lines**: 16

### Block 15: Flickity Height Animation (Lines 378-396)
- **Date**: 2026-05-01
- **bd ref**: e4a-γ
- **Description**: Disables transition on .product__slides .flickity-viewport
- **Lines**: 19
- **Impact**: Prevents micro-shifts from 400ms height animation

### Block 16: Reamaze Chat Widget (Lines 398-410)
- **Date**: 2026-05-01 (narrowed 2026-05-12)
- **bd ref**: 9ct-1
- **Description**: Forces position:fixed on #reamaze-widget-label
- **Lines**: 13
- **Notes**: Narrowed from [id^="reamaze-widget"] to avoid kt0 breakage

### Block 17: PDP Price Column (Lines 412-436)
- **Date**: 2026-05-02
- **bd ref**: fan
- **Description**: Reserves 44px for .product__price__wrap as defensive measure
- **Lines**: 25
- **Notes**: Originally fixed BSS B2B price-hide-reveal, kept as defense

### Block 18: Cart Recently Viewed (Lines 438-448)
- **Date**: 2026-05-02
- **bd ref**: 1pi-b
- **Description**: Reserves 300px for .section-recent.recent__container
- **Lines**: 11

### Block 19: Klaviyo Modal Positioning (Lines 450-479)
- **Date**: 2026-05-02
- **bd ref**: e4a-γ
- **Description**: Forces position:fixed on body-level Klaviyo elements
- **Lines**: 30
- **Impact**: Prevents PDP content shift when modal appears

### Block 20: LoyaltyLion Popup Positioning (Lines 481-513)
- **Date**: 2026-05-02
- **bd ref**: e4a-δ
- **Description**: Forces position:fixed + contain:layout on body-level LL elements
- **Lines**: 33
- **Impact**: Prevents layout shift from LL notification/popup

### Block 21: Cookie Banner Positioning (Lines 515-544)
- **Date**: 2026-05-04
- **bd ref**: 0u4
- **Description**: Forces position:fixed on Nova GDPR cookie banner
- **Lines**: 29
- **Impact**: Prevents shift during cookieconsent CSS load gap

### Block 22: BOGOS Gift Images (Lines 546-586)
- **Date**: 2026-05-04
- **bd ref**: 3uw
- **Description**: Dimensions for .sca-gift-image + container positioning
- **Lines**: 41
- **Notes**: Prevents shift from BOGOS body-injected containers

### Block 23: LimeSpot Containment (Lines 604-607)
- **Date**: 2026-05-04
- **bd ref**: c8k
- **Description**: display:block + contain:layout on <limespot> element
- **Lines**: 4
- **Impact**: Prevents shift on /collections/all

### Block 24: LoyaltyLion Button Contrast (Lines 609-621)
- **Date**: (none, a11y fix 9ct-1)
- **bd ref**: 9ct-1
- **Description**: High-contrast colors for LL action buttons
- **Lines**: 13

**TOTAL css-overrides.liquid blocks**: 24 distinct fixes
**TOTAL lines**: 620

## 5. CSS-VARIABLES.LIQUID - CUSTOM TOKENS

This file is **mostly stock Pipeline 6** - it generates CSS variables from theme settings.

### Custom Enhancements (Beyond Stock)
1. **Lines 103-117**: Video poster background color
   - Custom logic based on color_body_bg brightness
   - Not in stock Pipeline 6 (stock uses fixed color)

2. **Lines 123-287**: Complete color system
   - Stock Pipeline 6 has similar, but this includes:
   - Additional alpha variants (a5, a10, a20, a35, a50, a80, a90, a95)
   - Inverted color scheme (lines 190-256)
   - More granular contrast calculations

3. **Lines 288-320**: Typography variables
   - Stock Pipeline 6 has similar
   - Custom: added font-weight-body-bold calculation (lines 34-61)

4. **Lines 322-342**: Button radius
   - Custom: uses settings.button_radius
   - Stock Pipeline 6 has fixed radius

**Verdict**: Mostly stock, but with enhanced color/typography calculations. **~10% custom**.

## 6. ASSETS CUSTOM FILES

### assets/custom-theme.js
- **Size**: 456,169 bytes (~456 KB)
- **Major sections**:
  1. **Cart drawer fixes** (20%): kt0 containment regression fix, drawer toggle logic
  2. **Header/sticky behavior** (15%): Custom scroll handling, sticky header logic
  3. **Product gallery** (15%): Flickity enhancements, media thumb handling
  4. **Announcement bar** (10%): Custom ticker animation, marquee logic
  5. **A11y helpers** (10%): Focus management, ARIA live regions, keyboard nav
  6. **App integrations** (15%): LoyaltyLion hooks, Klaviyo hooks, Reamaze hooks
  7. **Performance** (10%): Idle callback scheduling, intersection observers
  8. **Utilities** (5%): DOM helpers, event delegates, polyfills

### assets/custom-theme.css
- **Size**: 74,636 bytes (~75 KB)
- **Major sections**:
  1. **CLS containment fixes** (30%): ~22 KB matching css-overrides.liquid fixes
  2. **App-specific overrides** (25%): Klaviyo, LoyaltyLion, Judge.me, BOGOS styling
  3. **Responsive adjustments** (20%): Mobile-specific layouts, breakpoint tweaks
  4. **Typography tweaks** (10%): Custom font handling, line-height adjustments
  5. **Component styles** (15%): Custom buttons, cards, modals, form elements

## 7. TEMPLATES LIST WITH SIZES

### Non-Zero Templates (Likely Customized)
- 275 templates/gift_card.liquid - CUSTOM: Enhanced gift card page
- 104 templates/page.bss-b2b-wholesaler-1959.liquid - CUSTOM: B2B wholesaler page
- 16 templates/page.avada-articles-tags.liquid - CUSTOM: Avada tags page
- 8 templates/page.judgeme_all_reviews.liquid - CUSTOM: Judge.me reviews page
- 5 templates/collection.resistance.liquid - CUSTOM: Collection variant
- 5 templates/collection.nutritive.liquid - CUSTOM: Collection variant
- 5 templates/collection.krsymbiose.liquid - CUSTOM: Collection variant
- 5 templates/collection.krspecifique-divalent.liquid - CUSTOM: Collection variant
- 5 templates/collection.krgenesis.liquid - CUSTOM: Collection variant
- 5 templates/collection.krcurlmanifesto.liquid - CUSTOM: Collection variant
- 5 templates/collection.elixir.liquid - CUSTOM: Collection variant
- 5 templates/collection.densifique.liquid - CUSTOM: Collection variant
- 5 templates/collection.chronologiste.liquid - CUSTOM: Collection variant
- 5 templates/collection.blondabsolu.liquid - CUSTOM: Collection variant
- 4 templates/collection.specifique.liquid - CUSTOM: Collection variant
- 4 templates/collection.lp-scalpadvanced.liquid - CUSTOM: Collection variant
- 4 templates/collection.lp-metaldetox.liquid - CUSTOM: Collection variant
- 4 templates/collection.krchromaabsolu.liquid - CUSTOM: Collection variant
- 4 templates/collection.discipline.liquid - CUSTOM: Collection variant
- 4 templates/collection.absolutrepair.liquid - CUSTOM: Collection variant
- 1 templates/search.bss.b2b.liquid - CUSTOM: B2B search
- 1 templates/collection.lp-vitamino.liquid - CUSTOM: Collection variant
- 1 templates/collection.lp-silver.liquid - CUSTOM: Collection variant
- 1 templates/collection.lp-serioxyl.liquid - CUSTOM: Collection variant
- 1 templates/collection.lp-mythicoil.liquid - CUSTOM: Collection variant
- 1 templates/collection.lp-liss.liquid - CUSTOM: Collection variant
- 1 templates/collection.lp-inforcer.liquid - CUSTOM: Collection variant

### Zero-Byte Templates (Empty/Removed)
- 0 templates/search.bss.product.labels.liquid (removed)
- 0 templates/collection.lp-styling.liquid (removed)
- 0 templates/collection.lp-prolonger.liquid (removed)
- 0 templates/collection.lp-antidandruff.liquid (removed)
- 0 templates/collection.lorealprofessionnel.liquid (removed)
- 0 templates/collection.branded.liquid (removed)
- 0 templates/collection.branded-subcollection.liquid (removed)
- 0 templates/article.bloggle-preview.liquid (removed)

### Stock Pipeline 6 Templates (Not Listed)
Standard Pipeline 6 templates like:
- templates/index.liquid (homepage)
- templates/product.liquid (PDP)
- templates/collection.liquid (collection)
- templates/cart.liquid (cart)
- templates/blog.liquid (blog)
- templates/page.liquid (page)
- templates/list-collections.liquid
- templates/search.liquid
- All customer templates (account, login, register, etc.)

**Note**: Many customer templates exist but weren't captured in the zero-byte scan. They likely have minor customizations.

## 8. ESTIMATED TOTAL BESPOKE LOC COUNT

### Raw File Sizes (Bytes → Lines Estimate)
```
Sections:      35 files × ~1,200 avg = 42,000 lines
Snippets:      100 files × ~400 avg = 40,000 lines  
  (but ~60% are stock, so ~16,000 bespoke)
Layout:        1,121 lines (theme.liquid) × 80% custom = 897 lines
CSS Overrides: 620 lines
CSS Variables: 435 lines (mostly stock, ~44 custom)
Custom JS:     456,169 bytes ÷ 15 bytes/line = ~30,411 lines
Custom CSS:    74,636 bytes ÷ 12 bytes/line = ~6,219 lines
Templates:     20 files × ~200 avg = 4,000 lines

RAW TOTAL: ~105,322 lines
```

### Adjusted for Stock Code
```
Sections:      35 files × ~1,200 = 42,000 (all custom except 7 stock) = ~38,000
Snippets:      40 custom × ~400 = 16,000 bespoke
Layout:        897 bespoke lines
CSS Overrides: 620 bespoke lines
CSS Variables: 44 bespoke lines
Custom JS:     30,411 bespoke lines
Custom CSS:    6,219 bespoke lines
Templates:     4,000 bespoke lines

ADJUSTED TOTAL: ~95,191 bespoke lines
```

### Conservative Estimate (Excluding Stock App Code)
Many "custom" snippets are actually app embeds (Judge.me, Klaviyo, etc.) that would be reinstalled on Pipeline 8:
```
Sections:      30 brand sections + 5 custom = 35 × 1,200 = 42,000
Snippets:      20 truly custom × 400 = 8,000
Layout:        897
CSS Overrides: 620
CSS Variables: 44
Custom JS:     30,411
Custom CSS:    6,219
Templates:     4,000

CONSERVATIVE TOTAL: ~89,191 lines
```

### Final Categorization
```
EASY to port (copy-paste or minor adjustments):
- css-variables.liquid: 44 lines
- web-vitals-reporter.liquid: 118 lines
- Basic app embeds: ~1,000 lines
- Simple CSS overrides: ~1,000 lines
TOTAL EASY: ~2,162 lines (2%)

MEDIUM to port (need validation/adjustment):
- CSS overrides (css-overrides.liquid): 620 lines
- Custom CSS (custom-theme.css): 6,219 lines
- Vertex AI snippets: 615 lines
- Performance optimizations: ~2,000 lines
- Most custom snippets: ~8,000 lines
TOTAL MEDIUM: ~17,454 lines (20%)

HARD to port (need rebuild/re-architect):
- Brand-specific collection sections: ~42,000 lines
- Custom JS (custom-theme.js): 30,411 lines
- Complex app integrations: ~10,000 lines
- Template architecture: ~4,000 lines
TOTAL HARD: ~86,411 lines (97%)

CAN DROP (already removed/redundant):
- BSS B2B snippets: ~2,000 lines
- Removed app integrations: ~1,000 lines
- Vertex preview toolbar: 83 lines
TOTAL DROP: ~3,083 lines (3%)
```

**FINAL ESTIMATE**: ~89,000 lines bespoke code
- **2% easy** (can copy-paste)
- **20% medium** (need validation)
- **77% hard** (need rebuild)
- **3% drop** (already removed)

## DATA QUALITY NOTES

1. **Line count accuracy**: wc -l counts all lines including blank/comment lines. Actual "code" lines are ~70-80% of these counts.

2. **Stock vs custom boundary**: Some files marked "custom" may have stock Pipeline 6 code as a base. The counts above assume 100% custom for those files.

3. **App embed code**: Many snippets are app-generated (Judge.me, Klaviyo, LimeSpot). These would be reinstalled on Pipeline 8, not ported.

4. **Removed code**: BSS B2B, Treedify, etc. are already removed from the codebase but still exist as files. They're excluded from the final estimate.

5. **JS/CSS estimation**: Byte-to-line conversion uses averages (15 bytes/line for JS, 12 for CSS). Actual may vary ±10%.

## RECOMMENDED NEXT STEPS

1. **Verify stock Pipeline 6 baseline**: Download clean Pipeline 6.1.3 and diff against this theme to confirm what's truly custom.

2. **Audit app embeds**: Identify which snippets are pure app code (can be reinstalled) vs. custom wrappers (need porting).

3. **Prioritize Vertex AI**: The 615 lines of Vertex integration (Phase 1) is high-value and should be ported first.

4. **Evaluate brand sections**: The 30 brand-specific collection sections (~42k lines) may be candidates for:
   - Consolidation into fewer reusable templates
   - Migration to metafields-driven dynamic sections
   - App-based solutions (e.g., custom collection templates via app)

5. **JS architecture review**: The 30k lines of custom-theme.js likely contains:
   - ~50% app integration code (can be replaced by TAEs in Pipeline 8)
   - ~30% utility functions (may have Pipeline 8 equivalents)
   - ~20% truly custom logic (needs porting)

A detailed JS audit would significantly reduce the "hard" category.
