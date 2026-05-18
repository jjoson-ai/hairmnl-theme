# CLS attribution (Phase 0.2) — bd hairmnl-theme-ujg6.2

Extracted from `layout-shifts` audit in Lighthouse 13.x via PSI API. Scores are summed across all runs per cell, then top-5 categories by total score are listed. Categories are best-effort classifications of the shifting DOM node (by selector + snippet + label).

**Caveat on `n_runs`**: PSI API caches identical-URL requests within ~30s, so n=3 often returns 1 fresh + 2 cached. Treat `n_runs` as upper bound; effective unique samples may be 1.

## Mobile

### home

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.015 | 8 | Main content (broad) (0.031) · Carousel/slider (0.000) |
| p8-dev | 3 | 0.013 | 30 | Main content (broad) (0.040) · Other (0.032) · Carousel/slider (0.000) |

**Top shift per cell:**

- **p6-live**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.031, box 412×18403)
- **p8-dev**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.040, box 412×17099)

### collection

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.041 | 20 | LoyaltyLion widget (0.083) · Main content (broad) (0.031) · Other (0.000) |
| p8-dev | 3 | 0.354 | 36 | Other (1.062) · LoyaltyLion widget (0.117) · Main content (broad) (0.040) |

**Top shift per cell:**

- **p6-live**: `div#lion-loyalty-panel-custom-css > div.lion-notification-container > div.lion-…` — `<div class="lion-notification lion-notification--guest-introduction lion-notification-…">` — LoyaltyLion widget (score 0.083, box 335×137)
- **p8-dev**: `body#hairmnl-best-sellers-greatest-haircare-hits > main#MainContent > div#shopi…` — `<div id="shopify-section-template--18751980929123__section_richtext_GhY8it" class="shopify` — Other (score 1.062, box 412×536)

### pdp

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.021 | 17 | Other (0.064) · LoyaltyLion widget (0.052) · Main content (broad) (0.046) |
| p8-dev | 3 | 0.028 | 30 | LoyaltyLion widget (0.103) · Other (0.058) · Main content (broad) (0.040) |

**Top shift per cell:**

- **p6-live**: `div.wrapper > div.grid > div.grid__item` — `<div class="grid__item medium-up--one-half">` — Other (score 0.064, box 396×1454)
- **p8-dev**: `div#lion-loyalty-panel-custom-css > div.lion-notification-container > div.lion-…` — `<div class="lion-notification lion-notification--guest-introduction lion-notification-…">` — LoyaltyLion widget (score 0.103, box 335×137)

### cart

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.051 | 18 | Other (0.197) · Main content (broad) (0.089) · LoyaltyLion widget (0.027) |
| p8-dev | 3 | 0.283 | 42 | Other (1.048) · LoyaltyLion widget (0.103) · Main content (broad) (0.089) |

**Top shift per cell:**

- **p6-live**: `body#your-shopping-cart > main#MainContent > div#shopify-section-template--1652…` — `<div id="shopify-section-template--16528967270499__main" class="shopify-section">` — Other (score 0.197, box 412×411)
- **p8-dev**: `body#your-shopping-cart > main#MainContent > div#shopify-section-template--1874…` — `<div id="shopify-section-template--18745200115811__recent_products" class="shopify-section` — Other (score 1.048, box 412×308)

### brand

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.015 | 6 | Main content (broad) (0.015) · LoyaltyLion widget (0.003) · Carousel/slider (0.000) · Other (0.000) |
| p8-dev | 3 | 0.291 | 35 | Other (0.872) · Main content (broad) (0.215) · LoyaltyLion widget (0.081) · Carousel/slider (0.001) |

**Top shift per cell:**

- **p6-live**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.015, box 412×18403)
- **p8-dev**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<div id="shopify-section-template--18745200345187__8e66ad54-68f1-48bf-b688-5be1f765…" clas` — Other (score 0.872, box 412×341)

## Desktop

### home

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.009 | 24 | Main content (broad) (0.038) · Other (0.003) · LoyaltyLion widget (0.001) · Carousel/slider (0.000) |
| p8-dev | 3 | 0.173 | 30 | Other (0.518) · Main content (broad) (0.028) · LoyaltyLion widget (0.003) · Header/nav (0.000) · Carousel/slider (0.000) |

**Top shift per cell:**

- **p6-live**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.038, box 1335×11069)
- **p8-dev**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<div id="shopify-section-template--18745200345187__164442519884b6f73e" class="shopify-sect` — Other (score 0.518, box 1335×1018)

### collection

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.010 | 3 | Main content (broad) (0.009) · Other (0.001) · LoyaltyLion widget (0.000) |
| p8-dev | 3 | 0.009 | 24 | Main content (broad) (0.028) · LoyaltyLion widget (0.023) · Other (0.002) |

**Top shift per cell:**

- **p6-live**: `body#hairmnl-best-sellers-greatest-haircare-hits > main#MainContent` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.009, box 1335×4411)
- **p8-dev**: `body#hairmnl-best-sellers-greatest-haircare-hits > main#MainContent` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.028, box 1335×4552)

### pdp

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.025 | 45 | Other (0.071) · Judge.me widget (0.067) · Main content (broad) (0.028) · LoyaltyLion widget (0.026) · Header/nav (0.000) |
| p8-dev | 3 | 0.020 | 45 | Judge.me widget (0.062) · LoyaltyLion widget (0.035) · Main content (broad) (0.028) · Other (0.025) · Header/nav (0.000) |

**Top shift per cell:**

- **p6-live**: `div.tabs-wrapper > div.product-accordion > div.accordion__wrapper` — `<div class="accordion__wrapper">` — Other (score 0.071, box 542×52)
- **p8-dev**: `div#shopify-block-ATi9wN21Xd1YxaWszY__judgeme_review_snippet > div#jdgm-review-…` — `<div class="jdgm-widget jdgm-review-snippet-widget" data-widget-name="review_snippet_widge` — Judge.me widget (score 0.062, box 542×138)

### cart

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.259 | 21 | Other (0.989) · Main content (broad) (0.040) · LoyaltyLion widget (0.031) |
| p8-dev | 3 | 0.306 | 45 | Other (0.971) · Main content (broad) (0.040) · LoyaltyLion widget (0.035) |

**Top shift per cell:**

- **p6-live**: `main#MainContent > div#shopify-section-template--16528967270499__cd287ffa-cf2d-…` — `<div class="section-recent recent__container palette--light bg--neutral js" data-section-i` — Other (score 0.989, box 1335×329)
- **p8-dev**: `body#your-shopping-cart > main#MainContent > div#shopify-section-template--1874…` — `<div id="shopify-section-template--18745200115811__recent_products" class="shopify-section` — Other (score 0.971, box 1335×328)

### brand

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.011 | 23 | Main content (broad) (0.022) · LoyaltyLion widget (0.010) · Other (0.002) · Header/nav (0.000) · Carousel/slider (0.000) |
| p8-dev | 3 | 0.173 | 30 | Other (0.518) · Main content (broad) (0.028) · LoyaltyLion widget (0.001) · Header/nav (0.000) · Carousel/slider (0.000) |

**Top shift per cell:**

- **p6-live**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.022, box 1335×11069)
- **p8-dev**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<div id="shopify-section-template--18745200345187__164442519884b6f73e" class="shopify-sect` — Other (score 0.518, box 1335×1018)
