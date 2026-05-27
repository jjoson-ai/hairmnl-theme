# Critical-CSS template usage map (bd hairmnl-theme-ujg6.59)

Generated 2026-05-27 from `snippets/critical-css.liquid` (430 selectors, 39.6KB).
Method: querySelectorAll via BeautifulSoup+soupsieve on static HTML for 7 templates.

## Summary

| Category | Selectors | % | Action |
|---|---|---|---|
| **Universal** (matches ≥5/7 templates) | 181 | 42% | Keep always inline |
| **Per-template** (matches 1-4/7) | 316 unique-by-template assignments (174 unique sels) | 40% | Gate via Liquid `{% if template.name == 'X' %}` |
| **Unused** (matches 0/7) | 48 | 11% | Remove from critical CSS (still loaded via theme.css for dynamic state) |
| **Errored** (pseudo-element selectors) | 27 | 6% | Keep inline (soupsieve can't query, conservatively assumed used) |

## Templates audited

- **home** — 67 per-template selectors used here
- **collection** — 59 per-template selectors used here
- **pdp** — 78 per-template selectors used here
- **cart** — 19 per-template selectors used here
- **brand** — 63 per-template selectors used here
- **article** — 27 per-template selectors used here
- **search** — 3 per-template selectors used here

## Universal selectors (181)

Keep in the always-inlined critical CSS block:

```
button
input[type=email]
input[type=search]
textarea
body
input
em
.btn--full
.grid__item img
.display-none
.home__subtitle
.accordion__title
*
header
main
nav
section
ul
li
.rte ul
.rte li
.rte a:not([class])
.float__wrapper
.float__wrapper input
.float__wrapper label
.site-footer-wrapper a
.site-footer-wrapper .btn--secondary.btn
.footer-quicklinks li
.footer-quicklinks a
.footer-quicklinks
.site-footer-wrapper .rte
html
.grid
.grid__item
:root
.uppercase
.h4--body
h2
h3
p
.wrapper
.wrapper .grandparent .header__dropdown__wrapper
.main-content
.icon
.rte
.rte img
.columns
.btn
.btn--soft
[class*=btn].uppercase
a
form
textarea.input-full
label
.errors
img
svg:not(:root)
.image-overlay
.image-overlay-5
.align--middle-center
.visually-hidden
.m0
.palette--light
.theme__header
.header__backfill
.header__logo
.header__logo__link
.header__logo__link img
.header__mobile
.header__mobile__left
.header__mobile__right
.header__mobile__left .header__mobile__button
.header__mobile__right .header__mobile__button
.header__mobile__button
.header__desktop
.header__desktop__bar__l
.header__desktop__bar__r
.header__desktop__bar__inline
.header__desktop__buttons
.header__menu__inner
.header__desktop__button .navlink
.navlink--toplevel
.navtext
.navlink
.navlink .icon
.header__mobile__left .icon
.header__mobile__right .icon
.header__desktop__bar__r>.header__desktop__bar__inline
.header__desktop__buttons--icons .header__desktop__button .navlink
.logo__img
.header__dropdown
.grandparent .header__dropdown
.grandparent .header__dropdown__inner
.grandparent.kids-8 .header__dropdown__inner
.header__dropdown .navlink .navtext
.parent .header__dropdown
.hover__bar
[data-header-cart-count]
[data-header-cart-full]
[data-header-cart-price]
.header__desktop__buttons--icons .header__cart__status
.header__mobile__button .header__cart__status
.header__desktop__buttons--icons .header__cart__status [data-header-cart-count]
.header__mobile__button .header__cart__status [data-header-cart-count]
.announcement__wrapper
.announcement__bar
.announcement__bar:not(.desktop):not(.mobile)
.announcement__bar a:link
.announcement__text
.announcement__text>*
.announcement__text *
.announcement__text a
.announcement__text p
.announcement__font.font--3 .announcement__bar
.announcement__divider
.announcement__message
.announcement__scale
.header__drawer
.header__drawer__selects
.sliderule__panel
.sliderow
.sliderow__title
.sliderule__panel .sliderow__title
.sliderule__chevron--left
.sliderule__chevron--right
.sliderule__panel .sliderow
.sliderule__panel .sliderow .sliderow__title
.sliderule__panel>*
.sliderule__panel>:last-child
.sliderule-grid
.accordion__body
.footer__title .icon
.search__predictive
.search__predictive__outer
.search__predictive__main
.search__predictive__close
.search__predictive__close__inner
.search__predictive__clear
.search__predictive__clear .icon-close
.search-drawer .search__predictive__close
.search__results__products__list
.search__predictive:not(.search--empty) .search__results__empty
.input-group
.input-group .input-group-field:first-child
.input-group .input-group-button:last-child>.btn
.input-group-button
.input-group-field
.input-group .btn
.input-group .input-group-field
.input-group--inner-button
.input-group--inner-button .input-group-button
.input-group--inner-button input
.item--loadbar
.empty-content
.product-add-popdown
.product-add-popdown:not(.has-errors)
.search-popdown
.search-popdown .search__predictive__main
.search-popdown .search__predictive__form
.search-popdown .search__predictive__form input
.search-popdown .search__predictive__form__button
.grandparent:not(.grandparent--all-images) .header__dropdown__wrapper
.header__desktop__bar__inline .tousled-logo
.header__desktop__bar__inline .navtext.tousled
.points-box
.points-box .points-label
.header__mobile .header__mobile__left
.header__mobile .header__mobile__left .header__mobile__button
.header__mobile .header__mobile__left .reward-box
.header__mobile .header__mobile__left .reward-box a
.header__mobile .header__mobile__left .reward-box a img
.header__mobile .header__mobile__left .reward-box a span
.header__mobile .header__mobile__right
.header__mobile .header__mobile__right .header__mobile__button
.header__mobile .header__logo
.header__mobile .header__logo__link
.search-bar-mobile
.search-bar-mobile .input-group
.search-bar-mobile .input-group .btn
.search-bar-mobile .input-group .input-group-field
.search-bar-mobile input[type=search]
```

## Per-template selector buckets

### home (67 selectors)

Gate with `{% if template.name == 'home' %}` (or correct Liquid variable for the template type):

```
.swiper-button-prev.swiper-button-disabled
.collection-slider .swiper-button-prev
.collection-slider .swiper-button-next
.pt1
.pb1
.homepage-collection
.search__page__heading .input-group .btn
.search__page__heading .input-group .input-group-field
.search-bar
.swiper
.swiper-wrapper
.swiper-slide
.swiper-button-next
.swiper-button-prev
.swiper-pagination
.banner-slider .swiper
.banner-slider .swiper-slide
.banner-slider .swiper-slide img
.section-search .search-bar
.btn--outline
.is-hidden
.section-recent .recent__container__inner:not(.is-hidden)
.tabs__arrow
.tabs__arrow--prev
.tabs__arrow--next
ul.tabs
ul.tabs--center
.tab-link
.tab-link.current
.tabs--center>.tab-link
.tab-content
.tab-content.current
.collection-tabs
.collection-tabs .tab-content
.collection-tabs .tabs__arrow
.related__products
.recent__container .tab-content
.text-center
.js-grid[data-grid-small="2"]
.js-grid
.js-grid>*
.product-grid-item
.product__grid__info a
.product__grid__title
.product__grid__price
.product-grid-item .product__grid__info--under
.lazy-image
.lazy-image img
.collection__image__top
.product-grid-item__slide
.collection
.product__grid__title__wrapper
.product__grid__info.text-center .product__grid__title__wrapper
.link-over-image
.section--image
.image-overlay--bottom
.hero__content__wrapper
.align--bottom-left
.mb0
.text--white
.image__fill
.hidden-pocket
.jm-stars-static
.jm-stars-static__count
.jm-star
.jm-star--on
.jm-star--half
```

### collection (59 selectors)

Gate with `{% if template.name == 'collection' %}` (or correct Liquid variable for the template type):

```
aside
.text-center
.collection__filters__outer
.collection__filters__inner
.collection__filters__inner .sidebar__item .icon
.standard__rte
.standard__rte p
.js-grid[data-grid-small="2"]
[data-toggle-grid="3"]
[data-toggle-grid="4"]
.js-grid
.js-grid>*
.js-grid[data-grid-large="4"]
[data-toggle-grid="1"]
[data-toggle-grid]
[data-toggle-grid]:last-child
.product-grid-item
.product__grid__info a
.product__grid__title
.product__grid__price
.product-grid-item .product__grid__info--under
.lazy-image
.lazy-image img
.collection__image__top
.product-grid-item__slide
.collection
.collection__content
.collection__products
.collection__nav
.collection__layout
.collection__nav__buttons
.collection__filters__toggle .hide-filters
.collection__filters__wrapper
.sidebar__heading:first-of-type
.sidebar__navigation__list
.sidebar__heading
.sidebar__heading-chevron
.accordion-is-open>.sidebar__heading-chevron
.sidebar__filter__group .icon-box
.icon-box
.checkbox-border
.checkbox-core
.sidebar__item
.sidebar__item a
.sidebar__filter__group
.sidebar__navigation__list--grouped .sidebar__item
.sidebar__navigation__list--grouped .sidebar__item svg
.sidebar__navigation__list--grouped .link--disable
.sidebar__navigation__list--grouped .link--disable .icon-box
.product__grid__title__wrapper
.product__grid__info.text-center .product__grid__title__wrapper
.template-collection .main-content
.collection__sort
.text-left
.jm-stars-static
.jm-stars-static__count
.jm-star
.jm-star--on
.jm-star--half
```

### pdp (78 selectors)

Gate with `{% if template.name == 'pdp' %}` (or correct Liquid variable for the template type):

```
input[type=number]
select
.hide
.medium-up--one-half
.btn--outline
[data-add-to-cart]
.btn-state-loading
.btn-state-complete
.shopify-product-form
.btn--add-to-cart
.shopify-payment-button .shopify-payment-button__button
.quantity__wrapper input
option
.is-hidden
.fill-bg
.fill-text-light
.svg-loader
.svg-loader circle
.svg-loader circle~circle
.section-recent .recent__container__inner:not(.is-hidden)
.accordion__wrapper
.accordion__body p:first-of-type
.product-accordion .accordion__title
.tabs-wrapper
.tabs__arrow
.tabs__arrow--prev
.tabs__arrow--next
ul.tabs
ul.tabs--center
.tab-link
.tab-link.current
.tabs--center>.tab-link
.tab-content
.tab-content.current
.collection-tabs
.collection-tabs .tab-content
.collection-tabs .tabs__arrow
.breadcrumb
.breadcrumb a
.breadcrumb span
.breadcrumb a:first-child
.related__products
.recent__container .tab-content
.product-page
.product__headline
.product__price__main
.shop-pay-terms
.product__price
.product__form__outer
.product__form__outer.product__form--buybutton
.shop-pay-terms:empty
.product__title__wrapper
.product__title
.product__align-left .shopify-product-form
.product__align-left .product__title
.product__price--off
.product__price--off em
.quantity__wrapper
.quantity__input
.quantity__button
.quantity__button--plus
.quantity__button--minus
.product__media__wrapper
.product__slides
.media__zoom__icon
.media__zoom__icon svg
.media__thumb
.media__thumb img
.add-action-errors
.lazy-image
.lazy-image img
h1
.rte>div
.jm-stars-static
.jm-stars-static__count
.jm-star
.jm-star--on
.jm-star--half
```

### cart (19 selectors)

Gate with `{% if template.name == 'cart' %}` (or correct Liquid variable for the template type):

```
.is-hidden
.section-recent .recent__container__inner:not(.is-hidden)
.tabs__arrow
.tabs__arrow--prev
.tabs__arrow--next
ul.tabs
ul.tabs--center
.tab-link
.tab-link.current
.tabs--center>.tab-link
.tab-content
.tab-content.current
.collection-tabs
.collection-tabs .tab-content
.collection-tabs .tabs__arrow
.related__products
.recent__container .tab-content
.pt2
.pb4
```

### brand (63 selectors)

Gate with `{% if template.name == 'brand' %}` (or correct Liquid variable for the template type):

```
.homepage-collection
.swiper
.swiper-wrapper
.swiper-slide
.swiper-button-next
.swiper-button-prev
.swiper-pagination
.banner-slider .swiper
.banner-slider .swiper-slide
.banner-slider .swiper-slide img
.btn--outline
.is-hidden
.section-recent .recent__container__inner:not(.is-hidden)
.tabs__arrow
.tabs__arrow--prev
.tabs__arrow--next
ul.tabs
ul.tabs--center
.tab-link
.tab-link.current
.tabs--center>.tab-link
.tab-content
.tab-content.current
.collection-tabs
.collection-tabs .tab-content
.collection-tabs .tabs__arrow
.related__products
.recent__container .tab-content
.text-center
.standard__heading
.standard__rte
.standard__rte p
.js-grid[data-grid-small="2"]
.js-grid
.js-grid>*
.js-grid[data-grid-large="4"]
.product-grid-item
.product__grid__info a
.product__grid__title
.product__grid__price
.product-grid-item .product__grid__info--under
.lazy-image
.lazy-image img
.collection__image__top
.product-grid-item__slide
.product__grid__title__wrapper
.product__grid__info.text-center .product__grid__title__wrapper
.template-collection .main-content
.text-left
h1
.link-over-image
.section--image
.image-overlay--bottom
.hero__content__wrapper
.align--bottom-left
.mb0
.text--white
.image__fill
.jm-stars-static
.jm-stars-static__count
.jm-star
.jm-star--on
.jm-star--half
```

### article (27 selectors)

Gate with `{% if template.name == 'article' %}` (or correct Liquid variable for the template type):

```
.text-center
article
.one-whole
.text-left
.medium-up--one-third
.medium-up--two-thirds
h1
hr
hr.hr--small
.link-over-image
.section--image
.image-overlay--bottom
.hero__content__wrapper
.align--bottom-left
.mb0
.pt2
.pb4
.text--white
.image__fill
.hidden-pocket
.hidden-lap-and-up
.tousled-header__wrapper
.tousled-header__wrapper header
.tousled-header__wrapper .mobile-menu-box
.tousled-header__wrapper .link-list
.tousled-header__wrapper .link-list .header__dropdown
.tousled-header__wrapper .link-list .hover__bar
```

### search (3 selectors)

Gate with `{% if template.name == 'search' %}` (or correct Liquid variable for the template type):

```
.standard__rte
.text-left
.rte>div
```

## Deletion candidates (48)

These selectors had zero matches in static HTML across all 7 templates. They CAN still appear when JS adds dynamic classes (e.g., `.flickity-enabled`, `.swiper-button-prev.swiper-button-disabled`) — but they don't need to be in CRITICAL CSS because they only appear post-interaction. Remove from critical-css.liquid; the full theme.css (deferred) retains them.

```
.swiper-pointer-events
.swiper-backface-hidden .swiper-slide
.swiper-horizontal>.swiper-pagination-bullets
.swiper-pagination-bullets.swiper-pagination-horizontal
.swiper-pagination-bullet
.swiper-pagination-bullet-active
.swiper-horizontal>.swiper-pagination-bullets .swiper-pagination-bullet
.swiper-pagination-horizontal.swiper-pagination-bullets .swiper-pagination-bullet
.banner-slider .swiper-pagination-bullet-active
.collection-slider .spinner-wrapper
.collection-slider .spinner
.collection-slider .spinner>div
.flickity-enabled
.flickity-viewport
.flickity-slider
.shopify-payment-button .shopify-payment-button__button--unbranded
input[type=checkbox]
.grid__item iframe
.rte__video-wrapper
.rte__video-wrapper iframe
.neighbor--white+.neighbor--white .section-recent .recent__container__inner:not(.is-hidden)
.recent__container .related__products.alt .tab-link
.product__slides .flickity-slider>*
.product__slides .flickity-slider>.is-selected
.product__slides.flickity-enabled .product__media:not(.is-selected)
.flickity-button:disabled
.flickity-button-icon
.hidden
.collection-tabs .flickity-button
.related__products .flickity-button[disabled]
.align--top-center
.standard__heading:first-child
.fade-in.lazyloaded
.fade-in
.collection__heading
.collection__heading .collection__heading__text:last-child
.satcb_quick_buy.satcb_qb_top_right
.ticker--animated
.announcement__bar-holder>.announcement__bar .ticker--animated
audio
img.lazyload:not([src])
.fade-in-child .background-size-cover.lazyloaded
.fade-in-child .background-size-cover
.background-size-cover
.lazyloaded.logo__img--color
.ticker__comparitor
.template__cart__footer .upsell__holder
.jdgm-prev-badge .jdgm-prev-badge__stars:empty
```

## Errored selectors (27)

These contain `::before/::after/::-webkit-*` pseudo-elements that soupsieve can't query against the DOM. They're not deletable based on this audit (their parents likely match, and the pseudo-element styling matters). Keep inline.

```
.swiper-button-next:after
.swiper-button-prev:after
input[type=number]::-webkit-inner-spin-button
input[type=number]::-webkit-outer-spin-button
html:not(.no-js) input[type=number]::-webkit-inner-spin-button
html:not(.no-js) input[type=number]::-webkit-outer-spin-button
select::-ms-expand
.home__subtitle:after
.accordion__title:after
.accordion__title.accordion-is-open:after
.tabs__arrow:before
.tabs__arrow:after
ul.tabs::-webkit-scrollbar
.media__thumb.is-selected:after
:after
:before
.footer-quicklinks a:after
input[type=search]::-webkit-search-cancel-button
input[type=search]::-webkit-search-decoration
.grid:after
.wrapper .grandparent .header__dropdown__wrapper:after
.wrapper:after
.header__desktop__buttons--icons .header__desktop__button .navlink:after
.announcement__text a:after
.input-group input:-webkit-autofill
.input-group input::-moz-focus-inner
.item--loadbar:before
```

## Estimated impact

- **Unused removal**: ~4.3KB / ~10% of critical CSS
- **Per-template gating**: 174 selectors moved out of universal block. Net universal CSS shrinks from 430 to ~210 selectors (~50% reduction).
- **Combined**: critical-css.liquid universal block ~20-25KB (down from 39.6KB). Per-template gated additions added back for the specific template the user is on.

## Implementation plan (for next session)

1. Use this map to partition rules in critical-css.liquid by selector
2. Rebuild critical-css.liquid as:
   ```liquid
   {%- comment -%} Universal — always inlined {%- endcomment -%}
   /* universal rules */
   {%- case template.name -%}
   {%- when 'product' -%} /* PDP rules */
   {%- when 'collection' -%} /* collection rules */
   {%- when 'article' -%} /* article rules */
   {%- when 'index' -%} /* home rules */
   {%- when 'cart' -%} /* cart rules */
   {%- endcase -%}
   ```
3. Smoke test on draft theme: verify each template renders visually identically. Use Chrome DevTools to compare computed styles before/after on key elements per template.
4. Push to live + P8 for parity.
