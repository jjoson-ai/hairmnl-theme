# CLS attribution (Phase 0.2) — bd hairmnl-theme-ujg6.2

Extracted from `layout-shifts` audit in Lighthouse 13.x via PSI API. Scores are summed across all runs per cell, then top-5 categories by total score are listed. Categories are best-effort classifications of the shifting DOM node (by selector + snippet + label).

**Caveat on `n_runs`**: PSI API caches identical-URL requests within ~30s, so n=3 often returns 1 fresh + 2 cached. Treat `n_runs` as upper bound; effective unique samples may be 1.

## Mobile

### home

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | — | 0 |  |
| p8-dev | 3 | 0.256 | 6 | Other (0.513) · Main content (broad) (0.118) |

**Top shift per cell:**

- p6-live: (no shifts recorded)
- **p8-dev**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<div id="shopify-section-template--18745200345187__8e66ad54-68f1-48bf-b688-5be1f765…" clas` — Other (score 0.513, box 412×318)

### collection

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.000 | 0 |  |
| p8-dev | 3 | 0.115 | 18 | Main content (broad) (0.190) · LoyaltyLion widget (0.155) · Other (0.005) |

**Top shift per cell:**

- p6-live: (no shifts recorded)
- **p8-dev**: `body#hairmnl-best-sellers-greatest-haircare-hits > main#MainContent` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.190, box 412×7617)

### pdp

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.048 | 40 | Other (0.201) · LoyaltyLion widget (0.143) · Main content (broad) (0.031) · Judge.me widget (0.000) |
| p8-dev | 3 | 0.305 | 10 | Other (1.346) · Main content (broad) (0.177) |

**Top shift per cell:**

- **p6-live**: `div.grid__item > div.product-description > div.tabs-wrapper` — `<div class="tabs-wrapper">` — Other (score 0.201, box 380×210)
- **p8-dev**: `div.wrapper > div.grid > div.grid__item` — `<div class="grid__item medium-up--one-half">` — Other (score 1.346, box 396×1130)

### cart

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.215 | 25 | Other (0.308) · Main content (broad) (0.193) · LoyaltyLion widget (0.139) |
| p8-dev | 3 | 0.107 | 33 | Other (0.178) · Main content (broad) (0.177) · LoyaltyLion widget (0.150) |

**Top shift per cell:**

- **p6-live**: `body#your-shopping-cart > main#MainContent > div#shopify-section-template--1652…` — `<div id="shopify-section-template--16528967270499__main" class="shopify-section">` — Other (score 0.308, box 412×1424)
- **p8-dev**: `body#your-shopping-cart > main#MainContent > div#shopify-section-template--1874…` — `<div id="shopify-section-template--18745200115811__main" class="shopify-section">` — Other (score 0.178, box 412×1247)

### brand

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.037 | 21 | LoyaltyLion widget (0.110) · Main content (broad) (0.046) · Carousel/slider (0.000) |
| p8-dev | 3 | 0.059 | 12 | Main content (broad) (0.177) · Other (0.005) |

**Top shift per cell:**

- **p6-live**: `div#lion-loyalty-panel-custom-css > div.lion-notification-container > div.lion-…` — `<div class="lion-notification lion-notification--guest-introduction lion-notification-…">` — LoyaltyLion widget (score 0.110, box 335×137)
- **p8-dev**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.177, box 412×159236)

## Desktop

### home

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.009 | 25 | Main content (broad) (0.028) · LoyaltyLion widget (0.010) · Other (0.003) · Carousel/slider (0.000) |
| p8-dev | 3 | 0.235 | 4 | Other (0.470) · Main content (broad) (0.093) |

**Top shift per cell:**

- **p6-live**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.028, box 1335×11069)
- **p8-dev**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<div id="shopify-section-template--18745200345187__8e66ad54-68f1-48bf-b688-5be1f765…" clas` — Other (score 0.470, box 1335×45)

### collection

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.000 | 9 | LoyaltyLion widget (0.012) |
| p8-dev | 3 | 0.049 | 7 | Main content (broad) (0.228) · Header/nav (0.001) · Other (0.000) |

**Top shift per cell:**

- **p6-live**: `div#lion-loyalty-panel-custom-css > div.lion-notification-container > div.lion-…` — `<div class="lion-notification lion-notification--guest-introduction">` — LoyaltyLion widget (score 0.012, box 335×135)
- **p8-dev**: `body#hairmnl-best-sellers-greatest-haircare-hits > main#MainContent` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.228, box 1335×4914)

### pdp

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.040 | 39 | Other (0.181) · LoyaltyLion widget (0.037) |
| p8-dev | 3 | 0.075 | 29 | Carousel/slider (0.205) · Main content (broad) (0.183) · Other (0.050) · Header/nav (0.001) · Judge.me widget (0.000) |

**Top shift per cell:**

- **p6-live**: `div.grid__item > div.product-description > div.tabs-wrapper` — `<div class="tabs-wrapper">` — Other (score 0.181, box 542×210)
- **p8-dev**: `div.grid > div.grid__item > div.media__thumb__wrapper` — `<div data-product-thumbs="" class="media__thumb__wrapper flickity-enabled is-draggable" ta` — Carousel/slider (score 0.205, box 542×73)

### cart

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | 0.083 | 24 | Main content (broad) (0.160) · Other (0.052) · LoyaltyLion widget (0.038) |
| p8-dev | 3 | 0.059 | 27 | Main content (broad) (0.139) · Other (0.041) · LoyaltyLion widget (0.039) · Header/nav (0.001) |

**Top shift per cell:**

- **p6-live**: `div#shopify-section-template--16528967270499__main > div.cart__template > div.w…` — `<div class="wrapper pt2 pb4 cart--hidden" data-cart-form="" data-cart-loading="">` — Main content (broad) (score 0.160, box 1180×857)
- **p8-dev**: `body#your-shopping-cart > main#MainContent` — `<main class="main-content" id="MainContent">` — Main content (broad) (score 0.139, box 1335×1629)

### brand

| Theme | n | median CLS | shifts | Top categories (score) |
|---|---|---|---|---|
| p6-live | 3 | — | 0 |  |
| p8-dev | 3 | 0.216 | 9 | Other (0.648) · Main content (broad) (0.139) · Header/nav (0.001) |

**Top shift per cell:**

- p6-live: (no shifts recorded)
- **p8-dev**: `body#hairmnl-buy-kerastase-davines-aveda-l-39-oreal-olaplex-and-more > main#Mai…` — `<div id="shopify-section-template--18745200345187__e0961ca3-7855-47ed-9a02-e46ede50…" clas` — Other (score 0.648, box 1335×45)
