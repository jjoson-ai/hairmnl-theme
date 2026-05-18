# CLS attribution (Phase 0.2) — bd hairmnl-theme-ujg6.2

Extracted from `layout-shifts` audit in Lighthouse 13.x via PSI API. Scores are summed across all runs per cell, then top-5 categories by total score are listed. Categories are best-effort classifications of the shifting DOM node (by selector + snippet + label).

**Caveat on `n_runs`**: PSI API caches identical-URL requests within ~30s, so n=3 often returns 1 fresh + 2 cached. Treat `n_runs` as upper bound; effective unique samples may be 1.

## Mobile

### home

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.027 | 25 | LoyaltyLion widget (0.074) · Main content (broad) (0.046) · Other (0.000) · Carousel/slider (0.000) |
| p8-dev | 3 | 0.196 | 23 | Other (0.590) · LoyaltyLion widget (0.110) · Main content (broad) (0.015) · Carousel/slider (0.000) |

**Top shift per cell:**

- **p6-live**: `div#lion-loyalty-panel-custom-css > div.lion-notification-container > div.lion-…` — `<div class="lion-notification lion-notification--guest-introduction lion-notification-…">` — LoyaltyLion widget (score 0.074, box 335×137)
- **p8-dev**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<div id="shopify-section-template--18745200345187__8e66ad54-68f1-48bf-b688-5be1f765…" clas` — Other (score 0.590, box 412×313)

### collection

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.041 | 30 | LoyaltyLion widget (0.124) · Main content (broad) (0.046) · Other (0.000) |
| p8-dev | 3 | 0.138 | 25 | Main content (broad) (0.244) · Other (0.139) · LoyaltyLion widget (0.047) |

**Top shift per cell:**

- **p6-live**: `div#lion-loyalty-panel-custom-css > div.lion-notification-container > div.lion-…` — `<div class="lion-notification lion-notification--guest-introduction lion-notification-…">` — LoyaltyLion widget (score 0.124, box 335×137)
- **p8-dev**: `body#hairmnl-best-sellers-greatest-haircare-hits > main#MainContent` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.244, box 412×7743)

### pdp

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.021 | 9 | Other (0.064) · Main content (broad) (0.046) · LoyaltyLion widget (0.009) |
| p8-dev | 3 | 0.058 | 17 | Main content (broad) (0.189) · Other (0.065) · LoyaltyLion widget (0.009) |

**Top shift per cell:**

- **p6-live**: `div.wrapper > div.grid > div.grid__item` — `<div class="grid__item medium-up--one-half">` — Other (score 0.064, box 396×1454)
- **p8-dev**: `body#kerastase-genesis-anti-hair-fall-fortifying-serum-hairmnl > main#MainConte…` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.189, box 412×4585)

### cart

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.045 | 37 | LoyaltyLion widget (0.136) · Other (0.124) · Main content (broad) (0.089) |
| p8-dev | 3 | 0.094 | 14 | Main content (broad) (0.330) · Other (0.185) · LoyaltyLion widget (0.002) |

**Top shift per cell:**

- **p6-live**: `div#lion-loyalty-panel-custom-css > div.lion-notification-container > div.lion-…` — `<div class="lion-notification lion-notification--guest-introduction lion-notification-…">` — LoyaltyLion widget (score 0.136, box 335×137)
- **p8-dev**: `body#your-shopping-cart > main#MainContent` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.330, box 412×1927)

### brand

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.043 | 20 | LoyaltyLion widget (0.070) · Main content (broad) (0.031) · Other (0.000) · Carousel/slider (0.000) |
| p8-dev | 3 | 0.015 | 24 | LoyaltyLion widget (0.044) · Main content (broad) (0.015) · Other (0.002) · Carousel/slider (0.000) |

**Top shift per cell:**

- **p6-live**: `div#lion-loyalty-panel-custom-css > div.lion-notification-container > div.lion-…` — `<div class="lion-notification lion-notification--guest-introduction lion-notification-…">` — LoyaltyLion widget (score 0.070, box 335×137)
- **p8-dev**: `div#lion-loyalty-panel-custom-css > div.lion-notification-container > div.lion-…` — `<div class="lion-notification lion-notification--guest-introduction lion-notification-…">` — LoyaltyLion widget (score 0.044, box 335×137)

## Desktop

### home

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.009 | 34 | Main content (broad) (0.031) · LoyaltyLion widget (0.022) · Other (0.003) · Carousel/slider (0.000) |
| p8-dev | 3 | 0.532 | 42 | Other (2.312) · Main content (broad) (0.028) · LoyaltyLion widget (0.001) · Carousel/slider (0.000) |

**Top shift per cell:**

- **p6-live**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.031, box 1335×11069)
- **p8-dev**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<div id="shopify-section-template--18745200345187__8e66ad54-68f1-48bf-b688-5be1f765…" clas` — Other (score 2.312, box 1335×68)

### collection

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.013 | 33 | LoyaltyLion widget (0.038) · Main content (broad) (0.028) · Other (0.003) |
| p8-dev | 3 | 0.152 | 18 | Main content (broad) (0.404) · Other (0.223) · LoyaltyLion widget (0.046) · Product grid card (0.005) |

**Top shift per cell:**

- **p6-live**: `div#lion-loyalty-panel-custom-css > div.lion-notification-container > div.lion-…` — `<div class="lion-notification lion-notification--guest-introduction">` — LoyaltyLion widget (score 0.038, box 335×137)
- **p8-dev**: `body#hairmnl-best-sellers-greatest-haircare-hits > main#MainContent` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.404, box 1335×4958)

### pdp

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.017 | 37 | Other (0.069) · Judge.me widget (0.061) · Main content (broad) (0.028) · LoyaltyLion widget (0.013) |
| p8-dev | 3 | 0.025 | 29 | Other (0.117) · Judge.me widget (0.051) · Main content (broad) (0.028) |

**Top shift per cell:**

- **p6-live**: `div.tabs-wrapper > div.product-accordion > div.accordion__wrapper` — `<div class="accordion__wrapper">` — Other (score 0.069, box 542×52)
- **p8-dev**: `div.grid > div.grid__item > div.product__details` — `<div class="product__details">` — Other (score 0.117, box 542×531)

### cart

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.313 | 30 | Other (0.989) · Main content (broad) (0.040) · LoyaltyLion widget (0.026) |
| p8-dev | 3 | 0.015 | 13 | Other (0.049) · Main content (broad) (0.032) · LoyaltyLion widget (0.010) |

**Top shift per cell:**

- **p6-live**: `main#MainContent > div#shopify-section-template--16528967270499__cd287ffa-cf2d-…` — `<div class="section-recent recent__container palette--light bg--neutral js" data-section-i` — Other (score 0.989, box 1335×329)
- **p8-dev**: `body#your-shopping-cart > main#MainContent > div#shopify-section-template--1874…` — `<div id="shopify-section-template--18745200115811__main" class="shopify-section">` — Other (score 0.049, box 1335×1620)

### brand

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.011 | 33 | Main content (broad) (0.040) · LoyaltyLion widget (0.016) · Other (0.001) · Carousel/slider (0.000) |
| p8-dev | 3 | 0.831 | 36 | Other (2.494) · LoyaltyLion widget (0.043) · Main content (broad) (0.028) · Carousel/slider (0.000) |

**Top shift per cell:**

- **p6-live**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.040, box 1335×11069)
- **p8-dev**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<div id="shopify-section-template--18745200345187__8e66ad54-68f1-48bf-b688-5be1f765…" clas` — Other (score 2.494, box 1335×68)
