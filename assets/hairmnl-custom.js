/*
 * HairMNL custom theme JS — Pipeline 8 add-on
 *
 * This file is hand-written, NOT bundled. Loaded after Pipeline 8's stock
 * theme.js. Contains only HairMNL-specific behaviors that are not in
 * Pipeline 8's stock bundle.
 *
 * Architecture decision (P4 spike, 2026-05-17):
 *   - The Pipeline 6 custom-theme.js (9,118 LoC) is mostly bundled vendor
 *     libraries (sticky-js, sweetalert2, swiper, dom7, he, ssr-window) that
 *     Pipeline 8 already provides via Flickity + MicroModal + native APIs.
 *   - Actual custom hand-written code is ~750 LoC across 10 small scripts.
 *   - This file ports those scripts as standalone IIFEs. No bundler needed.
 *
 * Status: SPIKE — 3 of 10 behaviors ported as feasibility demonstration.
 * Remaining 7 behaviors (cross-post-blogs, hover-line, lion-points,
 * banner-slider, collection-slider, domparser, consent-modal) follow the
 * same pattern and are scheduled for OC bulk port in bd hairmnl-theme-2i8b.6
 * (M5).
 */

(function () {
  'use strict';

  // ============================================================
  // 1) sticky-filter-bar — sticky collection nav on mobile
  // ----------------------------------------------------------------
  // Pipeline 6 used the sticky-js library (~400 LoC of vendor code) to
  // make .collection__nav sticky below 600px width. Pipeline 8 drops the
  // library entirely in favor of native CSS `position: sticky` — the
  // library was solving a problem that no longer exists on modern browsers.
  //
  // The CSS for this lives in snippets/css-overrides.liquid (P4.M3) under
  // a new block "collection-nav sticky on mobile". This JS only handles
  // the dynamic `top` offset based on the menu height var, which CSS can't
  // compute on its own.
  // ============================================================
  document.addEventListener('DOMContentLoaded', function () {
    var collectionNav = document.querySelector('.collection__nav');
    if (!collectionNav) return;

    var mql = window.matchMedia('(max-width: 600px)');
    var setStickyTop = function () {
      if (!mql.matches) {
        collectionNav.style.removeProperty('top');
        return;
      }
      var rawMenu = document.documentElement.style.getPropertyValue('--menu-height');
      var menuHeight = parseFloat(rawMenu);
      var top = (!Number.isNaN(menuHeight) && menuHeight > 0) ? Math.round(menuHeight) - 1 : 0;
      collectionNav.style.top = top + 'px';
    };

    setStickyTop();
    mql.addEventListener('change', setStickyTop);
    window.addEventListener('load', setStickyTop, { once: true });
  });

  // ============================================================
  // 2) product-tabs-v1 — tab switching on product page
  // ----------------------------------------------------------------
  // Pure DOM, no library dependencies. Direct port from Pipeline 6.
  // Pipeline 8's stock theme has Disclosure / details-summary patterns
  // but no tab pattern, so this custom version stays.
  // ============================================================
  document.addEventListener('DOMContentLoaded', function () {
    var tabLinks = document.querySelectorAll('.tab-button');
    if (!tabLinks.length) return;

    var tabContents = document.querySelectorAll('.tabs');

    var clearActive = function () {
      tabLinks.forEach(function (el) { el.classList.remove('active-tab'); });
      tabContents.forEach(function (el) { el.classList.remove('active-tab'); });
    };

    tabLinks.forEach(function (link) {
      link.addEventListener('click', function () {
        clearActive();
        var target = document.querySelector('.' + this.dataset.tab);
        if (target) target.classList.add('active-tab');
        this.classList.add('active-tab');
      });
    });
  });

  // ============================================================
  // 3) header-mobile-slide-rule — mobile nav slide-rule pattern
  // ----------------------------------------------------------------
  // Pipeline 6 version had 4 console.log statements firing per construction
  // (INP issue, partially noted 2026-05-01 T5). This port:
  //   - Strips ALL console.log statements (INP win)
  //   - Adds the missing `wrapper` selector key the original referenced via
  //     `selectors.wrapper` but never defined
  //   - Keeps the keyboard event handler (was defined but never called in P6)
  //   - Replaces deprecated `evt.which` with `evt.code`
  // ============================================================
  (function () {
    var SELECTORS = {
      slideruleOpen: 'data-tousled-sliderule-open',
      slideruleClose: 'data-tousled-sliderule-close',
      sliderulePane: 'data-tousled-sliderule-pane',
      slideruleWrapper: '[data-tousled-sliderule]',
      slideruleWrapperContainer: '[data-tousled-sliderule-wrapper]',
      focusable: 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
      children: ':scope > [data-animates], :scope > * > [data-animates], :scope > * > * >[data-animates], :scope > .sliderule-grid  > *',
    };
    var CLASSES = { isVisible: 'is-visible' };

    var HeaderMobileSliderule = function (el) {
      this.sliderule = el;
      this.wrapper = el.closest(SELECTORS.slideruleWrapperContainer);
      this.key = this.sliderule.id;
      this.trigger = document.querySelector('[' + SELECTORS.slideruleOpen + '=\'' + this.key + '\']');
      this.exit = document.querySelector('[' + SELECTORS.slideruleClose + '=\'' + this.key + '\']');
      this.pane = document.querySelector('[' + SELECTORS.sliderulePane + ']');
      this.children = this.sliderule.querySelectorAll(SELECTORS.children);

      if (!this.trigger || !this.exit || !this.pane) return;

      this.trigger.setAttribute('aria-haspopup', true);
      this.trigger.setAttribute('aria-expanded', false);
      this.trigger.setAttribute('aria-controls', this.key);

      this._bindClicks();
      this._bindKeys();
      this._stagger();
      document.addEventListener('theme:sliderule:close', this._close.bind(this));
    };

    HeaderMobileSliderule.prototype._bindClicks = function () {
      this.trigger.addEventListener('click', this._show.bind(this));
      this.exit.addEventListener('click', this._hide.bind(this));
    };
    HeaderMobileSliderule.prototype._bindKeys = function () {
      this.trigger.addEventListener('keyup', function (evt) {
        if (evt.code !== 'Space') return;
        this._show();
      }.bind(this));
      this.sliderule.addEventListener('keyup', function (evt) {
        if (evt.code !== 'Escape') return;
        this._hide();
      }.bind(this));
    };
    HeaderMobileSliderule.prototype._stagger = function () {
      this.children.forEach(function (child, i) {
        child.style.transitionDelay = (i * 50 + 10) + 'ms';
      });
    };
    HeaderMobileSliderule.prototype._show = function () {
      this.sliderule.classList.add(CLASSES.isVisible);
      this.children.forEach(function (el) { el.classList.add(CLASSES.isVisible); });
      var pos = parseInt(this.pane.dataset.sliderulePane, 10) + 1;
      this.pane.setAttribute('data-sliderule-pane', pos);
    };
    HeaderMobileSliderule.prototype._hide = function () {
      this.sliderule.classList.remove(CLASSES.isVisible);
      this.children.forEach(function (el) { el.classList.remove(CLASSES.isVisible); });
      var pos = parseInt(this.pane.dataset.sliderulePane, 10) - 1;
      this.pane.setAttribute('data-sliderule-pane', pos);
    };
    HeaderMobileSliderule.prototype._close = function () {
      if (!this.pane || !this.pane.hasAttribute(SELECTORS.sliderulePane)) return;
      if (parseInt(this.pane.getAttribute(SELECTORS.sliderulePane), 10) > 0) {
        this._hide();
        this.pane.setAttribute(SELECTORS.sliderulePane, 0);
      }
    };

    document.querySelectorAll(SELECTORS.slideruleWrapper).forEach(function (el) {
      new HeaderMobileSliderule(el);
    });
  })();
})();
