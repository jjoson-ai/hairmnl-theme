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

  // ============================================================
  // 4) lion-points — LoyaltyLion points label reveal (M5 port)
  // ----------------------------------------------------------------
  // Polls .points-approved spans for the LoyaltyLion-injected points
  // value, then unhides .points-label once any are populated.
  // Only runs for logged-in users (navlink-account.is-loggedin).
  // ============================================================
  document.addEventListener('DOMContentLoaded', function () {
    var navlinkAccounts = document.querySelectorAll('.navlink-account.is-loggedin');
    if (!navlinkAccounts.length) return;

    var pointsApproved = document.querySelectorAll('.points-approved');
    var pointsLabel = document.querySelectorAll('.points-label');
    pointsApproved.forEach(function (el) {
      var interval = setInterval(function () {
        if (el.innerHTML !== '') {
          clearInterval(interval);
          pointsLabel.forEach(function (label) { label.style.display = 'block'; });
        }
      }, 1000);
    });
  });

  // ============================================================
  // 5) domparser — strip HTML from metafield multi-line text (M5 port)
  // ----------------------------------------------------------------
  // Pipeline 6 used node-html-parser (5400 LoC library) to do what
  // textContent=textContent does natively. Carries over the same fix.
  // ============================================================
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.metafield-multi_line_text_field').forEach(function (el) {
      el.textContent = el.textContent;
    });
  });

  // ============================================================
  // 6) hover-line — TousledHoverLine animated underline (M5 port)
  // ----------------------------------------------------------------
  // Pure DOM + CSS-variable manipulation. No vendor deps. Preserves
  // the INP-fix discipline from the P6 version (batch reads before
  // writes; geometry reads kept separate from setProperty calls).
  // ============================================================
  (function () {
    var SEL = {
      item: '[data-main-menu-text-item]',
      text: '.navtext',
      isActive: 'data-menu-active',
      sectionOuter: '[data-tousled-header-wrapper]',
      underlineCurrent: 'data-underline-current',
      defaultItem: '.menu__item.main-menu--active .navtext, .header__desktop__button.main-menu--active .navtext',
    };
    var defaultPositions = null;

    var TousledHoverLine = function (el) {
      this.wrapper = el;
      this.itemList = this.wrapper.querySelectorAll(SEL.item);
      this.sectionOuter = document.querySelector(SEL.sectionOuter);
      if (!this.sectionOuter) return;
      this.underlineCurrent = this.sectionOuter.getAttribute(SEL.underlineCurrent) === 'true';
      this.defaultItem = this.underlineCurrent ? this.wrapper.querySelector(SEL.defaultItem) : null;
      this.textBottom = null;
      this._setDefault();
      document.fonts.ready.then(this._init.bind(this));
    };
    TousledHoverLine.prototype._init = function () {
      if (!this.itemList.length) return;
      this._listen();
      document.addEventListener('theme:resize', this._reset.bind(this));
      var vert = this._measure();
      this._setDefault();
      var barLeftDefault = null;
      var barLeftElse = null;
      var navItemInit = this.sectionOuter.querySelector(SEL.item);
      if (defaultPositions) {
        if (this.defaultItem) barLeftDefault = this.defaultItem.offsetLeft || 0;
      } else if (navItemInit) {
        barLeftElse = Math.ceil(navItemInit.getBoundingClientRect().left + window.scrollX);
      } else {
        barLeftElse = 0;
      }
      this._applyVertical(vert.textHeight, vert.textBottom);
      if (defaultPositions) {
        if (this.defaultItem) this.sectionOuter.style.setProperty('--bar-left', barLeftDefault + 'px');
        this._applyResetStyles();
      } else {
        this.sectionOuter.style.setProperty('--bar-left', barLeftElse + 'px');
        this.sectionOuter.style.setProperty('--bar-width', '0px');
      }
      this.sectionOuter.style.setProperty('--bar-opacity', '1');
    };
    TousledHoverLine.prototype._setDefault = function () {
      if (!this.defaultItem) return;
      defaultPositions = { left: this.defaultItem.offsetLeft || null, width: this.defaultItem.clientWidth || null };
    };
    TousledHoverLine.prototype._measure = function () {
      var height = this.wrapper.clientHeight;
      var text2 = this.itemList[0].querySelector(SEL.text);
      var textHeight = text2.clientHeight;
      var textBottom = Math.floor(height / 2 - textHeight / 2) - 4;
      return { textHeight: textHeight, textBottom: textBottom };
    };
    TousledHoverLine.prototype._applyVertical = function (textHeight, textBottom) {
      if (this.textBottom !== textBottom) {
        this.sectionOuter.style.setProperty('--bar-text', textHeight + 'px');
        this.sectionOuter.style.setProperty('--bar-bottom', textBottom + 'px');
        this.textBottom = textBottom;
      }
    };
    TousledHoverLine.prototype._listen = function () {
      var self = this;
      this.itemList.forEach(function (element) {
        element.addEventListener('mouseenter', function (evt) {
          var item = evt.target.querySelector(SEL.text);
          self._startBar(item);
        });
      });
      this.wrapper.addEventListener('mouseleave', this._clearBar.bind(this));
    };
    TousledHoverLine.prototype._startBar = function (item) {
      var vert = this._measure();
      var leftPos = Math.ceil(item.getBoundingClientRect().left + window.scrollX);
      var width = item.clientWidth;
      var active = this.sectionOuter.getAttribute(SEL.isActive) !== 'false';
      this._applyVertical(vert.textHeight, vert.textBottom);
      if (active) {
        this._render(width, leftPos);
      } else {
        this.sectionOuter.setAttribute(SEL.isActive, true);
        this._render(0, leftPos);
        var self = this;
        setTimeout(function () { self._render(width, leftPos); }, 10);
      }
    };
    TousledHoverLine.prototype._render = function (width, left) {
      this.sectionOuter.style.setProperty('--bar-left', left + 'px');
      this.sectionOuter.style.setProperty('--bar-width', width + 'px');
    };
    TousledHoverLine.prototype._applyResetStyles = function () {
      if (defaultPositions && defaultPositions.left && defaultPositions.width) {
        this.sectionOuter.style.setProperty('--bar-left', defaultPositions.left + 'px');
        this.sectionOuter.style.setProperty('--bar-width', defaultPositions.width + 'px');
      } else {
        this.sectionOuter.style.setProperty('--bar-width', '0px');
      }
    };
    TousledHoverLine.prototype._reset = function () {
      this._setDefault();
      this._applyResetStyles();
    };
    TousledHoverLine.prototype._clearBar = function () {
      var self = this;
      this.sectionOuter.setAttribute(SEL.isActive, false);
      setTimeout(function () {
        var active = self.sectionOuter.getAttribute(SEL.isActive) !== 'false';
        if (!active) self._reset();
      }, 150);
    };

    var container = document.querySelector('[data-tousled-header-wrapper]');
    if (container) {
      var el = container.querySelector('[data-links-wrapper]');
      if (el) new TousledHoverLine(el);
    }
  })();

  // ============================================================
  // 7) cart-drawer-on-atc — P6 UX parity for add-to-cart
  // ----------------------------------------------------------------
  // Pipeline 6's add-to-cart slid the cart drawer open immediately on
  // success. Pipeline 8's stock flow instead shows a mini product popdown
  // (the `bo` class in theme.js dispatches `theme:cart:popdown`, then the
  // user has to click "View Cart" in the popdown to actually open the
  // drawer). Reads as "slide cart drawer doesn't work" for anyone used to
  // the P6 behavior — the drawer is healthy, the user just never sees it
  // because the popdown intercepts the event.
  //
  // Fix: catch `theme:cart:popdown` in the capture phase, stop it from
  // reaching P8's popdown handler, and dispatch `theme:drawer:open`
  // directly on the cart drawer instead. `ln` (AJAX cart) is already
  // listening on the drawer for `theme:drawer:open` and will fetch +
  // render the updated cart HTML.
  (function () {
    document.addEventListener('theme:cart:popdown', function (e) {
      // Capture phase: fires before P8's bo handler on document
      e.stopImmediatePropagation();
      var drawer = document.querySelector('[data-drawer="drawer-cart"]');
      if (!drawer) return;
      drawer.dispatchEvent(new CustomEvent('theme:drawer:open', {
        bubbles: false
      }));
    }, true);
  })();

  // ============================================================
  // DEFERRED — vendor-library-dependent scripts (Phase 5 visual QA)
  // ----------------------------------------------------------------
  // The following 4 P6 scripts depend on vendor libraries that P8's stock
  // theme.js doesn't include:
  //
  //   - cross-post-blogs.js  (98 LoC)  — uses Swiper
  //   - banner-slider.js     (23 LoC)  — uses Swiper
  //   - collection-slider.js (99 LoC)  — uses Swiper
  //   - consent-modal.js     (138 LoC) — uses sweetalert2
  //
  // Pipeline 8 ships Flickity (slider) + MicroModal (modal) but the APIs
  // differ from Swiper / sweetalert2. Per-script API translation + visual
  // QA decision deferred to Phase 5 when the dev-theme preview is live.
  //
  // Per-script options (operator picks during P5):
  //   (a) Rewrite using P8 stock equivalents — cleanest, ~3h work per script
  //   (b) Vendor-load Swiper + sweetalert2 from CDN — faster, +90 KB JS
  //   (c) Drop the script, replace behavior with P8 stock equivalent
  //
  // Reference: os2-migration/p4-spike-report.md (vendor-lib analysis).
  // ============================================================
})();
