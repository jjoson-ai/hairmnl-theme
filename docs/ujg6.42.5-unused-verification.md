# ujg6.42.5 — Verify-and-remove unused CSS

Date: 2026-05-20

## Methodology

Scan the deployed `assets/theme-core.css` and `assets/custom-theme-core.css` chunk files. For each rule, classify into one of 5 verdicts based on 4 evidence sources:

1. **Extended Coverage** — re-run real Chrome CSS Coverage with deeper interactions (modal opens, hover-all-cards, accordion clicks, swatch selects, search-drawer-with-type) across **10 templates**: 5 original (home, collection, product, cart, search) + 5 new (blog, article, page, 404, collection-filtered).
2. **HTML class presence** — class→templates map from rendered HTML of the 5 main templates.
3. **Forced-core overrides** — selector patterns from `wave-b-emit.py` that always land in core (JS-lib bases, app-injection points, modal/drawer/popup state, form errors, hero/section/wrapper).
4. **Ambiguity heuristics** — patterns that are dormant by design but critical when triggered: `:focus-visible`, `:checked`, `.template-customers-*`, `@media print`, `prefers-reduced-motion`, `sold-out`, etc.

## Verdict legend

| Verdict | Action |
|---|---|
| `REMOVE_CANDIDATE` | Safe to strip from chunk (no evidence of use) |
| `KEEP_EXTENDED` | Extended Coverage saw bytes used |
| `KEEP_HTML` | Classes appear in rendered HTML |
| `KEEP_FORCED_CORE` | Always-core pattern match |
| `KEEP_AMBIGUOUS` | Risky-to-remove heuristic match |

## Per-file results

### theme-core.css

| Verdict | Rules | Bytes | KB | % |
|---|---:|---:|---:|---:|
| `REMOVE_CANDIDATE` | 1530 | 91,564 | 89.4 | 33.6% |
| `KEEP_EXTENDED` | 516 | 60,201 | 58.8 | 22.1% |
| `KEEP_HTML` | 396 | 71,420 | 69.7 | 26.2% |
| `KEEP_FORCED_CORE` | 281 | 33,240 | 32.5 | 12.2% |
| `KEEP_AMBIGUOUS` | 126 | 16,235 | 15.9 | 6.0% |

#### Sample selectors per verdict

**`REMOVE_CANDIDATE` (1530 rules) — top 15 by bytes:**

```
  [ 568B] .product__info__link
  [ 560B] .product__info__link--inline
  [ 394B] .sidebar__item a, .sidebar__item span
  [ 351B] @@@ @media only screen and (max-width: 479px) @@@ .table--responsive td:before
  [ 324B] .subcollection__title
  [ 300B] .caps--link
  [ 297B] .custom-prev-next-button.next
  [ 287B] .product__subs__option input[type="radio"]
  [ 286B] .home--uppercase
  [ 282B] [data-header-transparent="true"][data-header-sticky="static"]   + .announcement__bar-outer--high, [data-header-transpare
  [ 280B] .product__popdown__title
  [ 278B] .selector-wrapper label
  [ 270B] .rating__wrapper__title
  [ 266B] .rating__wrapper__search
  [ 264B] .pickup__product__title
```

**`KEEP_EXTENDED` (516 rules) — top 15 by bytes:**

```
  [3862B] .neighbor--black + .neighbor--black .frame, .neighbor--black + .neighbor--black .homepage-blog, .neighbor--black + .neig
  [ 898B] .form-horizontal .popout__toggle, .form-horizontal input[type="email"], .form-horizontal input[type="file"], .form-horiz
  [ 749B] .helper-note .helper-icon
  [ 691B] .btn--link
  [ 660B] .js__header__stuck.js__header__stuck__backdrop .theme__header
  [ 576B] .template-giftcard .wrapper .grandparent .header__dropdown__wrapper iframe, .template-giftcard .wrapper .grandparent .he
  [ 496B] .main-content .shopify-section:last-child .brick__section, .main-content .shopify-section:last-child .frame, .main-conte
  [ 484B] .radio__fieldset .radio__button label
  [ 476B] .badge
  [ 472B] <<at-rule>> @keyframes bloop
  [ 469B] @@@ @media only screen and (min-width: 480px) @@@ .double__image:hover .collection__image__bottom
  [ 439B] .header__logo__text
  [ 426B] .helper-note
  [ 385B] .modal__close
  [ 383B] .popout__toggle, input[type="email"], input[type="file"], input[type="number"], input[type="password"], input[type="sear
```

**`KEEP_HTML` (396 rules) — top 15 by bytes:**

```
  [1907B] @@@ @media only screen and (min-width: 480px) and (max-width: 989px) @@@ .gallery .small-medium--five-tenths:nth-child(o
  [1907B] @@@ @media only screen and (min-width: 768px) and (max-width: 1399px) @@@ .gallery .medium-large--five-tenths:nth-child(
  [1875B] @@@ @media only screen and (max-width: 989px) @@@ .gallery .medium-down--five-tenths:nth-child(odd),   .gallery .medium-
  [1843B] @@@ @media only screen and (max-width: 767px) @@@ .gallery .small-down--five-tenths:nth-child(odd),   .gallery .small-do
  [1843B] @@@ @media only screen and (max-width: 1399px) @@@ .gallery .large-down--five-tenths:nth-child(odd),   .gallery .large-d
  [1843B] @@@ @media only screen and (min-width: 1400px) @@@ .gallery .widescreen--five-tenths:nth-child(odd),   .gallery .widescr
  [1811B] @@@ @media only screen and (min-width: 768px) @@@ .gallery .medium-up--five-tenths:nth-child(odd),   .gallery .medium-up
  [1779B] @@@ @media only screen and (min-width: 480px) @@@ .gallery .small-up--five-tenths:nth-child(odd),   .gallery .small-up--
  [1779B] @@@ @media only screen and (min-width: 990px) @@@ .gallery .large-up--five-tenths:nth-child(odd),   .gallery .large-up--
  [1715B] @@@ @media only screen and (max-width: 479px) @@@ .gallery .mobile--five-tenths:nth-child(odd),   .gallery .mobile--four
  [1715B] @@@ @media only screen and (min-width: 768px) and (max-width: 989px) @@@ .gallery .medium--five-tenths:nth-child(odd),  
  [1683B] @@@ @media only screen and (min-width: 480px) and (max-width: 767px) @@@ .gallery .small--five-tenths:nth-child(odd),   
  [1683B] @@@ @media only screen and (min-width: 990px) and (max-width: 1399px) @@@ .gallery .large--five-tenths:nth-child(odd),  
  [ 578B] .js__header__stuck .theme__header
  [ 560B] .grandparent.kids-10 .header__dropdown__inner, .grandparent.kids-11 .header__dropdown__inner, .grandparent.kids-12 .head
```

**`KEEP_FORCED_CORE` (281 rules) — top 15 by bytes:**

```
  [ 502B] .drawer--visible .drawer__underlay .drawer__underlay__blur, .drawer__underlay.underlay--visible .drawer__underlay__blur
  [ 492B] .popup .input-group .input-group-field:-webkit-autofill, .popup .input-group .input-group-field:-webkit-autofill:active,
  [ 481B] .product-reviews .spr-summary-actions-newreview
  [ 415B] .drawer__content
  [ 369B] .drawer__accordion .accordion__title
  [ 349B] .drawer__accordion .accordion__title:after
  [ 330B] .focus-enabled .grid__swatch__container .grid__swatch__placeholder, .product-grid-item:hover .grid__swatch__container .g
  [ 329B] @@@ @media only screen and (max-width: 479px) @@@ .brick__collection.flickity-enabled .brick__product,   .brick__collect
  [ 311B] .drawer--pop .drawer__content
  [ 302B] body.focus-enabled .product__media:not(.is-selected) .media__contain iframe, body.focus-enabled .product__media:not(.is-
  [ 301B] .product__grid__title
  [ 299B] .popup--bottom .popup__inner > :first-child, .popup--bottom .popup__inner > a:not(.btn), .popup--bottom .popup__inner > 
  [ 293B] @@@ @media only screen and (max-width: 479px) @@@ .brick__collection.flickity-enabled .flickity-slider,   .flickity-grid
  [ 287B] @@@ @media only screen and (min-width: 768px) @@@ .drawer--visible .collection__filters__inner,   .filters--default-visi
  [ 282B] .popup .popup__title
```

**`KEEP_AMBIGUOUS` (126 rules) — top 15 by bytes:**

```
  [ 606B] .active__filters__clear, .active__filters__remove
  [ 598B] .palette--dark, body.default--dark
  [ 426B] .poppy__tooltip
  [ 378B] .share__link
  [ 364B] .tooltip__label
  [ 364B] .variant__countdown
  [ 339B] .popout__toggle
  [ 335B] .popout-list__option
  [ 313B] .shopify-challenge__message
  [ 307B] .accordion__block-title
  [ 297B] :root
  [ 294B] .shopify-challenge__button
  [ 291B] <<at-rule>> @keyframes slideup
  [ 284B] .tooltip:before
  [ 253B] .popout-list
```

---

### custom-theme-core.css

| Verdict | Rules | Bytes | KB | % |
|---|---:|---:|---:|---:|
| `REMOVE_CANDIDATE` | 126 | 12,801 | 12.5 | 22.0% |
| `KEEP_EXTENDED` | 113 | 16,381 | 16.0 | 28.2% |
| `KEEP_HTML` | 45 | 4,002 | 3.9 | 6.9% |
| `KEEP_FORCED_CORE` | 148 | 18,110 | 17.7 | 31.2% |
| `KEEP_AMBIGUOUS` | 56 | 6,822 | 6.7 | 11.7% |

#### Sample selectors per verdict

**`REMOVE_CANDIDATE` (126 rules) — top 15 by bytes:**

```
  [ 920B] .new-list-tags.collection-nav
  [ 379B] .mobile-view.bg-backdrop .list-container
  [ 379B] .mobile-view.bg-backdrop .list-container
  [ 323B] .btn-search-tags
  [ 287B] .mobile-view.bg-backdrop .list-container span.button-up:after
  [ 287B] .mobile-view.bg-backdrop .list-container span.button-up:after
  [ 253B] .tousled-header__wrapper .mobile-menu-box
  [ 221B] .mobile-view.bg-backdrop
  [ 216B] .mobile-view.bg-backdrop .list-container span.button-up
  [ 185B] .mobile-view.bg-backdrop .collection-nav--footer
  [ 184B] .kerastase-menu.collection-nav--heading, .kerastase-menu .collection-nav--heading, .kerastase-menu .collection-nav--grou
  [ 170B] .new-list-tags.collection-nav li span.checkmark
  [ 168B] .tab-menu li
  [ 161B] .collection-branded .featured-collection__title, .collection-branded .discover-collection__title
  [ 158B] .cross-post-blogs .grid-box
```

**`KEEP_EXTENDED` (113 rules) — top 15 by bytes:**

```
  [2327B] <<at-rule>> @font-face
  [ 920B] .new-list-tags.collection-nav
  [ 458B] .collection-branded h1, .collection-branded h2, .collection-branded h3, .collection-branded h4, .collection-branded h5, 
  [ 407B] .swiper-button-prev, .swiper-button-next
  [ 331B] .new-list-tags.collection-nav li input[type=checkbox]:checked ~ span.checkmark:after
  [ 322B] .btn-search-tags
  [ 295B] .spr-header-title::after, .related_articles_header h5::after, .related_products_header h5::after, .jdgm-carousel-title:a
  [ 264B] .collection-branded .section-header__title, .collection-branded .section-title, .collection-branded .featured-collection
  [ 248B] .swiper-cube .swiper-slide-shadow-top, .swiper-cube .swiper-slide-shadow-bottom, .swiper-cube .swiper-slide-shadow-left,
  [ 248B] .swiper-flip .swiper-slide-shadow-top, .swiper-flip .swiper-slide-shadow-bottom, .swiper-flip .swiper-slide-shadow-left,
  [ 237B] .swiper-vertical > .swiper-pagination-bullets .swiper-pagination-bullet, .swiper-pagination-vertical.swiper-pagination-b
  [ 228B] .swiper-button-prev:after, .swiper-button-next:after
  [ 221B] .mobile-view.bg-backdrop
  [ 216B] .mobile-view.bg-backdrop .list-container span.button-up
  [ 206B] .swiper-pagination-fraction, .swiper-pagination-custom, .swiper-horizontal > .swiper-pagination-bullets, .swiper-paginat
```

**`KEEP_HTML` (45 rules) — top 15 by bytes:**

```
  [ 483B] .tousled-header__wrapper .link-list .hover__bar
  [ 182B] .sliderule__wrapper .tousled-logo
  [ 145B] .header__mobile .header__mobile__left .reward-box a span
  [ 144B] .header__dropdown__inner .dropdown__family .navlink.navlink--child.has-grandchild .navtext
  [ 132B] .header__dropdown__inner > .navlink.navlink--child.no-grandchild .navtext
  [ 128B] .header__dropdown__inner .dropdown__family .navlink.navlink--grandchild .navtext
  [ 115B] .collection-branded .h4--body
  [ 114B] @@@ @media screen and (max-width: 768px) @@@ .search-bar-mobile .input-group .input-group-field,   .search-bar-mobile .i
  [ 111B] @@@ @media only screen and (min-width: 768px) @@@ body.template-cart .cart__template .cart__items__price .line__price:fi
  [ 108B] body.template-index .homepage-blog .grid__item
  [ 106B] .header__mobile .header__mobile__left .header__mobile__button
  [ 106B] .header__mobile .header__mobile__right .header__mobile__button
  [  96B] .announcement__text, .announcement__text p
  [  94B] body.template-index .homepage-blog .grid.grid--uniform
  [  91B] @@@ @media screen and (max-width: 768px) @@@ .collection-branded .grid.custom-section .grid__item:last-child
```

**`KEEP_FORCED_CORE` (148 rules) — top 15 by bytes:**

```
  [ 630B] .collection-branded .section-header__title, .collection-branded .section-title, .collection-branded .featured-collection
  [ 512B] .spr-header-title, .related_articles_header h5, .related_products_header h5, .jdgm-carousel-title
  [ 407B] .banner-slider .swiper-slide
  [ 394B] .swiper-pagination-bullet
  [ 355B] .swiper-horizontal > .swiper-pagination-progressbar, .swiper-pagination-progressbar.swiper-pagination-horizontal, .swipe
  [ 355B] .swiper-vertical > .swiper-pagination-progressbar, .swiper-pagination-progressbar.swiper-pagination-vertical, .swiper-ho
  [ 346B] .swiper-lazy-preloader
  [ 307B] .swiper-3d .swiper-wrapper, .swiper-3d .swiper-slide, .swiper-3d .swiper-slide-shadow, .swiper-3d .swiper-slide-shadow-l
  [ 302B] .swiper-3d .swiper-slide-shadow, .swiper-3d .swiper-slide-shadow-left, .swiper-3d .swiper-slide-shadow-right, .swiper-3d
  [ 291B] .swiper-vertical > .swiper-pagination-bullets.swiper-pagination-bullets-dynamic .swiper-pagination-bullet, .swiper-pagin
  [ 271B] .swiper-horizontal > .swiper-pagination-bullets.swiper-pagination-bullets-dynamic .swiper-pagination-bullet, .swiper-pag
  [ 270B] .swiper-pagination-progressbar .swiper-pagination-progressbar-fill
  [ 243B] .swiper-horizontal > .swiper-pagination-bullets.swiper-pagination-bullets-dynamic, .swiper-pagination-horizontal.swiper-
  [ 229B] .swiper-vertical > .swiper-pagination-bullets.swiper-pagination-bullets-dynamic, .swiper-pagination-vertical.swiper-pagi
  [ 225B] .swiper-horizontal > .swiper-pagination-bullets .swiper-pagination-bullet, .swiper-pagination-horizontal.swiper-paginati
```

**`KEEP_AMBIGUOUS` (56 rules) — top 15 by bytes:**

```
  [ 331B] .new-list-tags.collection-nav li input[type=checkbox]:checked ~ span.checkmark:after
  [ 257B] .product-label
  [ 253B] html:not(.lt-ie9) .image_autoheight_enable .grid__image img
  [ 227B] @@@ @media screen and (min-width: 769px) @@@ html:not(.lt-ie9) .image_autoheight_enable .large-up--one-whole > .grid__im
  [ 225B] @@@ @media only screen and (min-width: 481px) and (max-width: 768px) @@@ html:not(.lt-ie9) .image_autoheight_enable .med
  [ 224B] @@@ @media screen and (max-width: 480px) @@@ html:not(.lt-ie9) .image_autoheight_enable .small--one-whole > .grid__image
  [ 177B] @@@ @media screen and (min-width: 1120px) @@@ html:not(.lt-ie9) .image_autoheight_enable .large-up--one-third .grid__ima
  [ 175B] @@@ @media only screen and (min-width: 769px) and (max-width: 960px) @@@ html:not(.lt-ie9) .image_autoheight_enable .lar
  [ 175B] @@@ @media screen and (min-width: 960px) @@@ html:not(.lt-ie9) .image_autoheight_enable .large-up--one-quarter .grid__im
  [ 175B] @@@ @media screen and (min-width: 1120px) @@@ html:not(.lt-ie9) .image_autoheight_enable .large-up--one-quarter .grid__i
  [ 173B] @@@ @media only screen and (min-width: 769px) and (max-width: 960px) @@@ html:not(.lt-ie9) .image_autoheight_enable .lar
  [ 172B] @@@ @media only screen and (min-width: 481px) and (max-width: 768px) @@@ html:not(.lt-ie9) .image_autoheight_enable .med
  [ 171B] @@@ @media only screen and (min-width: 769px) and (max-width: 960px) @@@ html:not(.lt-ie9) .image_autoheight_enable .lar
  [ 171B] @@@ @media screen and (min-width: 960px) @@@ html:not(.lt-ie9) .image_autoheight_enable .large-up--one-third .grid__imag
  [ 171B] @@@ @media screen and (min-width: 960px) @@@ html:not(.lt-ie9) .image_autoheight_enable .large-up--one-fifth .grid__imag
```

---

## Total potential savings

- **theme-core.css**: 91,564 B (89.4 KB) safe to remove
- **custom-theme-core.css**: 12,801 B (12.5 KB) safe to remove
- **Total**: 104,365 B (101.9 KB) safe to remove sitewide

Sitewide because both `*-core.css` files load on every pageview. Wave A originally projected ~225 KB of removable `_unused` rules; the verification above is conservative about which of those can be safely removed.