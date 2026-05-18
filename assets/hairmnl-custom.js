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
  // Fix (v2): catch `theme:cart:popdown` in the capture phase to suppress
  // the mini popdown. Set a flag, then open the drawer on the NEXT
  // `theme:cart:change` event. P8's onSuccess() calls updateHeaderTotal()
  // (async /cart.js fetch) before dispatching `theme:cart:popdown`
  // synchronously. Opening the drawer immediately on the popdown event
  // caused it to open with stale content because theme:cart:change (which
  // sets stale=true on the drawer's AJAX cart controller) hadn't fired yet.
  // Waiting for theme:cart:change guarantees the drawer's controller has
  // fresh cart data and stale=true, so loadHTML() renders the added item.
  (function () {
    var pendingOpen = false;

    document.addEventListener('theme:cart:popdown', function (e) {
      e.stopImmediatePropagation();
      pendingOpen = true;
    }, true);

    document.addEventListener('theme:cart:change', function () {
      if (!pendingOpen) return;
      pendingOpen = false;
      var drawer = document.querySelector('[data-drawer="drawer-cart"]');
      if (!drawer) return;
      drawer.dispatchEvent(new CustomEvent('theme:drawer:open', { bubbles: false }));
    }, false);
  })();

  // ============================================================
  // B.2 — Phase 2 sub-ticket stubs (2i8b.B2.x)
  // ============================================================
  // Sections 8–11 are stubs waiting on per-section implementation per
  // os2-migration/p8-bundle-architecture.md D3 + B.2 sub-ticket list.
  // Each section follows the pattern in hover-line (section 6) — outer
  // IIFE, SEL constants, vanilla function+prototype, DOM-presence guard.
  //
  // Section 12 (swiper-chunk-loader) is implemented in this commit as
  // the canonical pattern for sections 8–10 to follow when they land.
  // ============================================================

  // ============================================================
  // 8) cross-post-blogs — TODO bd 2i8b.B2.2 (Opus 4.7 / Medium)
  // ----------------------------------------------------------------
  // Port from custom-theme.js lines 8429–8526 (~98 LoC). Uses Swiper.
  // Active on article + collection + thebackbar collections.
  // Waits for theme:swiper:ready (Section 12) before initializing.
  //
  // Replaces: custom-theme.js cross-post-blogs behavior + Swiper bundle
  // ============================================================
  // STUB — implementation pending B.2.2.

  // ============================================================
  // 9) banner-slider — TODO bd 2i8b.B2.3 (Sonnet 4.6 / Medium → OC)
  // ----------------------------------------------------------------
  // Port from custom-theme.js lines 8831–8853 (~22 LoC). Uses Swiper
  // (Navigation + Pagination + Autoplay). Active on home + many
  // collection templates + hairmnlstudio pages.
  //
  // Selector: .banner-slider .swiper
  // Waits for theme:swiper:ready (Section 12) before initializing.
  // ============================================================
  // STUB — implementation pending B.2.3.

  // ============================================================
  // 10) collection-slider — TODO bd 2i8b.B2.4 (Sonnet 4.6 / Medium → OC)
  // ----------------------------------------------------------------
  // Port from custom-theme.js lines 8855–8953 (~98 LoC). Uses Swiper
  // (Navigation). Active on home (8 instances), collection pages,
  // brand-collection pages, many blog/article pages.
  //
  // Selector: .swiper.collection
  // Existing IO-defer pattern with 1200px rootMargin preserved.
  // Waits for theme:swiper:ready (Section 12) before initializing.
  // ============================================================
  // STUB — implementation pending B.2.4.

  // ============================================================
  // 11) consent-modal — TODO bd 2i8b.B2.5 (Opus 4.7 / Medium)
  // ----------------------------------------------------------------
  // Replace custom-theme.js consent-modal (lines 8980–9103, ~123 LoC)
  // + the entire SweetAlert2 bundle (~2,631 LoC) + `he` HTML entities
  // dep (~241 LoC) with native <dialog> + ~30 LoC vanilla JS + ~40
  // LoC CSS in snippets/css-overrides.liquid.
  //
  // Selectors: form.cart, .cart__items__row[data-with-consent],
  //            [data-drawer="drawer-cart"], .checkout__button
  // Active on /cart page only when products with `with-consent` tag
  // are in cart.
  //
  // Per-D7 (bundle architecture): native <dialog> element. Polyfill
  // decision for Safari <15.4 deferred to operator browser-share
  // audit before Phase D.
  // ============================================================
  // STUB — implementation pending B.2.5.

  // ============================================================
  // 12) swiper-chunk-loader — Phase B.2.1 (Opus 4.7 / Medium) [DRAFT]
  // ----------------------------------------------------------------
  // Async-loads assets/swiper-bundle.min.js (vendored, ~90 KB minified,
  // Phase B.2.6) only when slider selectors are present in DOM.
  // Dispatches `theme:swiper:ready` on document when Swiper global is
  // available. Sections 8/9/10 listen for this event before init.
  //
  // Per D4 (bundle architecture): vendored chunk, not CDN.
  // Per D5 (budget): chunk loaded only on slider pages; non-slider
  //                  pages (cart, account, search-empty) skip Swiper
  //                  parse cost entirely.
  //
  // Requires `window.theme.swiperBundleUrl` to be set inline in
  // layout/theme.liquid (Phase B.2.8 wires this — until then, the
  // loader logs a warning and dispatches the ready event with a
  // null Swiper to let dependent sections short-circuit gracefully).
  // ============================================================
  (function () {
    var sliderSelectors = [
      '.swiper.collection',
      '.banner-slider .swiper',
      '.cross-post-blogs .swiper-container',
    ];
    var hasSlider = sliderSelectors.some(function (sel) {
      return document.querySelector(sel) !== null;
    });
    if (!hasSlider) return;

    // Already loaded? (defensive — covers edge case where another
    // session already loaded Swiper or P8's theme.js exposed it)
    if (window.Swiper) {
      document.dispatchEvent(new CustomEvent('theme:swiper:ready', {
        detail: { source: 'pre-loaded', Swiper: window.Swiper },
      }));
      return;
    }

    // Phase B.2.8 will set this via inline <script> in layout/theme.liquid:
    //   <script>window.theme = window.theme || {};
    //           window.theme.swiperBundleUrl = "{{ 'swiper-bundle.min.js' | asset_url }}";
    //   </script>
    var bundleUrl = (window.theme && window.theme.swiperBundleUrl) || null;
    if (!bundleUrl) {
      // Pre-B.2.8 dormant state. Log once, dispatch null-Swiper event so
      // Sections 8/9/10 can graceful-degrade (no slider; static markup
      // remains in place per server-rendered Liquid).
      if (window.console && console.warn) {
        console.warn(
          '[hairmnl-custom] section 12: swiper bundle URL not set ' +
          '(layout/theme.liquid not yet wired per B.2.8). ' +
          'Sliders will render as static markup until then.'
        );
      }
      document.dispatchEvent(new CustomEvent('theme:swiper:ready', {
        detail: { source: 'unwired', Swiper: null },
      }));
      return;
    }

    // Inject async <script> for the bundle. Defer-loaded; non-blocking.
    var s = document.createElement('script');
    s.src = bundleUrl;
    s.defer = true;
    s.onload = function () {
      document.dispatchEvent(new CustomEvent('theme:swiper:ready', {
        detail: { source: 'chunk-loaded', Swiper: window.Swiper || null },
      }));
    };
    s.onerror = function () {
      if (window.console && console.error) {
        console.error('[hairmnl-custom] swiper chunk failed to load:', bundleUrl);
      }
      // Still dispatch (with null Swiper) so dependent sections can
      // graceful-degrade rather than hanging.
      document.dispatchEvent(new CustomEvent('theme:swiper:ready', {
        detail: { source: 'chunk-error', Swiper: null },
      }));
    };
    document.head.appendChild(s);
  })();
})();
