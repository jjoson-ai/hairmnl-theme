/*
 * HairMNL custom theme JS — Pipeline 8 add-on
 * Split from hairmnl-custom.js per bd ujg6.14
 * Common behaviours loaded on every template:
 *
 *   3) header-mobile-slide-rule (~88 LoC)
 *   4) lion-points (~22 LoC)
 *   5) domparser (~12 LoC)
 *   6) hover-line (~130 LoC)
 *   7) cart-drawer-on-atc (~55 LoC)
 */

(function () {
  'use strict';

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
  // 8) lazy-render — IntersectionObserver Section Rendering API (bd ujg6.18)
  // ----------------------------------------------------------------
  // Below-fold heavy sections (featured-collections, brand-grid,
  // related-products) render as lightweight placeholders on pageload
  // and are fetched via Shopify's Section Rendering API when they
  // approach the viewport. Reduces initial page weight and TTI on
  // mobile. Triggered when the placeholder is 200px from viewport
  // edge. Non-JS users and crawlers see the <noscript> fallback.
  // ============================================================
  document.addEventListener('DOMContentLoaded', function () {
    var placeholders = document.querySelectorAll('[data-lazy-render]');
    if (!placeholders.length) return;

    var pending = new Set();

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var url = el.getAttribute('data-lazy-url');
        if (!url || pending.has(url)) return;

        pending.add(url);
        observer.unobserve(el);

        fetch(url)
          .then(function (r) {
            if (!r.ok) throw new Error('Section fetch failed: ' + r.status);
            return r.text();
          })
          .then(function (html) {
            var sid = el.getAttribute('data-section-id');
            // ----------------------------------------------------------------
            // bd 2i8b.30 + 2i8b.34 — Parse with DOMParser from the start.
            //
            // section-collection.liquid (and brand-collection / related)
            // use `{%- if request.design_mode or request.page_type == null -%}`
            // to detect Section Rendering API requests. Shopify does NOT
            // null out request.page_type for ?section_id= requests, so the
            // API returns the SAME lazy-render placeholder + a <noscript>
            // fallback containing the actual products. We extract from
            // the <noscript>.
            //
            // Key: DOMParser('text/html') parses with "scripting disabled"
            // context, so <noscript> contents become real DOM children
            // (not opaque text as they would in a JS-enabled
            // innerHTML parse). The earlier innerHTML approach collapsed
            // nested <noscript>s inside each product card, losing 11/12
            // products. bd 2i8b.34
            // ----------------------------------------------------------------
            var doc = new DOMParser().parseFromString(html, 'text/html');
            // Find a non-placeholder section first (in case the page_type
            // detection ever starts working)
            var candidates = doc.querySelectorAll('[data-section-id="' + sid + '"]');
            var fetched = null;
            for (var i = 0; i < candidates.length; i++) {
              if (!candidates[i].hasAttribute('data-lazy-render')) {
                fetched = candidates[i];
                break;
              }
            }
            // If only placeholder candidates found, use the <noscript>
            // fallback content. In DOMParser-parsed docs, noscript children
            // ARE real DOM nodes.
            if (!fetched) {
              var noscripts = doc.querySelectorAll('noscript');
              for (var j = 0; j < noscripts.length; j++) {
                var match = noscripts[j].querySelector('[data-section-id="' + sid + '"]');
                if (match) {
                  fetched = match;
                  break;
                }
              }
            }
            // Last resort: use first matching element regardless
            if (!fetched && candidates.length) fetched = candidates[0];
            if (fetched) fetched = document.adoptNode(fetched);
            if (fetched) {
              el.replaceWith(fetched);
              // Dispatch a custom event so any section-specific init code can re-run
              fetched.dispatchEvent(new CustomEvent('section:lazy-rendered', { bubbles: true }));
            } else {
              // Fallback: if we couldn't find the specific wrapper, use the whole response
              el.innerHTML = html;
            }
          })
          .catch(function (err) {
            // Show the <noscript> fallback (it's a sibling of the placeholder)
            var fallback = el.nextElementSibling;
            if (fallback && fallback.tagName === 'NOSCRIPT') {
              var div = document.createElement('div');
              div.innerHTML = fallback.textContent;
              el.replaceWith(div.firstElementChild || div);
            }
            pending.delete(url);
          });
      });
    }, { rootMargin: '200px 0px' });

    placeholders.forEach(function (el) { observer.observe(el); });
  });

  // ============================================================
  // 9) YouTube Facade — click-to-load (bd hairmnl-theme-ujg6.41)
  // ----------------------------------------------------------------
  // section-double.liquid's 'youtube' block renders a <button.yt-facade>
  // with a thumbnail in place of an <iframe>. On click, swap to a real
  // iframe with autoplay=1 so playback starts immediately.
  //
  // Why: loading="lazy" on iframes is ignored when the iframe is already
  // in initial viewport (brand-page hero is above the fold). YouTube
  // player CSS + JS (~1.4 MB) was loading on cold pageload despite the
  // lazy attribute. Facade defers all youtube.com network requests
  // until the user opts in.
  // ============================================================
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('.yt-facade');
    if (!btn) return;
    e.preventDefault();
    var vid = btn.getAttribute('data-yt-facade');
    if (!vid) return;
    var iframe = document.createElement('iframe');
    iframe.src = 'https://www.youtube.com/embed/' + vid + '?autoplay=1&rel=0&hd=1';
    iframe.setAttribute('frameborder', '0');
    iframe.setAttribute('allowfullscreen', '');
    iframe.setAttribute('allow', 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture');
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.aspectRatio = '16/9';
    iframe.style.border = '0';
    btn.replaceWith(iframe);
  });

  // ============================================================
  // bd a7av.8 — Sticky-bar collection-mode hydration + card-click update.
  // ----------------------------------------------------------------
  // When sections/collection.liquid (or brand-collection.liquid) renders
  // {% render 'product-sticky-bar', is_collection: true %}, the snippet
  // outputs a bar pre-filled with the FIRST product in the collection as
  // a server-rendered fallback. This block then:
  //   1) on DOM ready: if sessionStorage has a `hairmnl_last_viewed_product`,
  //      replace the bar's content with that product instead of the fallback.
  //   2) on product-card click within the collection page, update the bar
  //      to feature THAT product (no nav — let the link navigate the card,
  //      and the new PDP's PDP-mode bar will be visible there too).
  //   3) hide the bar entirely on cart / search / account / checkout pages
  //      (defensive — render call should also be omitted from those templates).
  //
  // Hidden by default below 1024px (CSS gate in css-overrides.liquid).
  // ============================================================
  (function () {
    var bar = document.getElementById('vrec-product-sticky-bar');
    if (!bar) return;
    if (bar.getAttribute('data-vrec-sticky-mode') !== 'collection') return;

    // Defensive hide on excluded surfaces.
    var path = window.location.pathname;
    if (/^\/(cart|search|account|checkout)/.test(path)) {
      bar.style.display = 'none';
      return;
    }

    // Helper: update the bar DOM in-place from a payload object.
    function applyPayload(p) {
      if (!p || !p.id) return;
      bar.setAttribute('data-product-id', p.id);
      bar.setAttribute('data-product-handle', p.handle || '');
      bar.setAttribute('data-product-url', p.url || '');

      var titleEl = bar.querySelector('.vrec-product-sticky-bar__title');
      if (titleEl && p.title) titleEl.textContent = p.title;

      var thumbImg = bar.querySelector('.vrec-product-sticky-bar__thumb img');
      if (thumbImg && p.thumb_src) thumbImg.src = p.thumb_src;

      var priceEl = bar.querySelector('.vrec-product-sticky-bar__price');
      if (priceEl && p.price_html) priceEl.innerHTML = p.price_html;

      var variantEl = bar.querySelector('[data-vrec-sticky-variant]');
      if (variantEl && p.variant_label) variantEl.textContent = p.variant_label;

      var idInput = bar.querySelector('[data-vrec-sticky-id]');
      if (idInput && p.variant_id) idInput.value = p.variant_id;

      var btn = bar.querySelector('.vrec-product-sticky-bar__cta');
      if (btn && typeof p.available !== 'undefined') {
        btn.disabled = !p.available;
        btn.setAttribute('aria-disabled', String(!p.available));
      }
    }

    // Hydrate from sessionStorage if a previously-viewed product exists
    // AND it's newer than the server-rendered fallback (always treat
    // sessionStorage as more recent on collection pages).
    try {
      var stored = sessionStorage.getItem('hairmnl_last_viewed_product');
      if (stored) {
        var p = JSON.parse(stored);
        // Sanity: stale entries (>2hr) get ignored — operator could have a
        // long tab open while the catalog changes. Falls back to the
        // first-product server render in that case.
        if (p && p.ts && (Date.now() - p.ts) < 2 * 60 * 60 * 1000) {
          applyPayload(p);
        }
      }
    } catch (e) { /* sessionStorage disabled or parse error — keep fallback */ }

    // Card-click handler: when user clicks a product card on the collection
    // page, capture the product info and update the bar immediately. The
    // anchor's natural navigation continues to PDP after this synchronously
    // returns (no preventDefault).
    document.addEventListener('click', function (e) {
      var card = e.target.closest && e.target.closest('.product-grid-item, [data-product-grid-item]');
      if (!card) return;
      var anchor = card.querySelector('a[href*="/products/"]');
      if (!anchor) return;

      // Best-effort scrape from the card DOM (the home/collection card markup).
      // Falls back gracefully if any field is missing.
      var titleEl = card.querySelector('.product__grid__title, .product-grid-item__title, [class*="title"]');
      var priceEl = card.querySelector('.product__grid__price, .product-grid-item__price, [class*="price"]');
      var imgEl = card.querySelector('img');
      var handleMatch = anchor.href.match(/\/products\/([^/?#]+)/);

      var payload = {
        id: card.getAttribute('data-product-id') || '',
        handle: handleMatch ? handleMatch[1] : '',
        url: anchor.getAttribute('href') || '',
        title: titleEl ? titleEl.textContent.trim() : '',
        price_html: priceEl ? priceEl.innerHTML : '',
        thumb_src: imgEl ? imgEl.currentSrc || imgEl.src : '',
        variant_id: '',         // collection card has no variant info; ADD will redirect to PDP
        variant_label: '',
        available: true,
        ts: Date.now()
      };

      // Update bar visually for any brief moment before navigation.
      applyPayload(payload);

      // Persist for the next collection-page visit.
      try { sessionStorage.setItem('hairmnl_last_viewed_product', JSON.stringify(payload)); }
      catch (err) { /* sessionStorage disabled */ }
    });
  })();

  // ============================================================
  // 10) rec-card AJAX add-to-cart (bd a7av.10 / 2i8b.50 + 2i8b.51)
  // ----------------------------------------------------------------
  // Vertex rec cards on the cart page + cart drawer use a formless
  // <button data-vrec-add data-variant-id> (snippets/vertex-rec-card.liquid)
  // instead of a per-card {% form 'product' %} — a nested <form> is invalid
  // inside the cart page form (sections/cart.liquid) and the drawer form
  // (cart-drawer.liquid). This handler adds via /cart/add.js and REUSES the
  // theme's existing flow (no parallel cart state): it re-dispatches the same
  // events the stock form-submit onSuccess fires — theme:cart:popdown (caught
  // + flagged by §7) then theme:cart:change (which §7 uses to open the drawer
  // and the drawer's AJAX controller uses to reload its line items). The
  // header count/price are read from the authoritative /cart.js.
  // ============================================================
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('[data-vrec-add]');
    if (!btn) return;
    e.preventDefault();
    if (btn.getAttribute('aria-busy') === 'true') return;
    var variantId = btn.getAttribute('data-variant-id');
    if (!variantId) return;

    btn.setAttribute('aria-busy', 'true');
    btn.disabled = true;

    fetch('/cart/add.js', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ id: variantId, quantity: 1 })
    })
      .then(function (r) {
        if (!r.ok) {
          return r.json().then(function (j) {
            throw new Error((j && j.description) || ('add failed: ' + r.status));
          });
        }
        return r.json();
      })
      .then(function () {
        // Read the authoritative cart and update the header count/price.
        return fetch('/cart.js', { headers: { 'Accept': 'application/json' } })
          .then(function (r) { return r.json(); })
          .then(function (cart) {
            var countEl = document.querySelector('[data-header-cart-count]');
            if (countEl) {
              countEl.setAttribute('data-header-cart-count', cart.item_count);
              countEl.textContent = '(' + cart.item_count + ')';
            }
            var priceEl = document.querySelector('[data-header-cart-price]');
            if (priceEl) priceEl.setAttribute('data-header-cart-price', cart.total_price);
            var fullEl = document.querySelector('[data-header-cart-full]');
            if (fullEl) fullEl.setAttribute('data-header-cart-full', cart.item_count > 1);
            // Hand off to the theme's own drawer flow (open + reload line items).
            document.dispatchEvent(new CustomEvent('theme:cart:popdown', { bubbles: true }));
            document.dispatchEvent(new CustomEvent('theme:cart:change', { bubbles: true }));
          });
      })
      .catch(function (err) {
        if (window.console && console.warn) console.warn('[vrec-add]', err && err.message ? err.message : err);
      })
      .then(function () {
        btn.removeAttribute('aria-busy');
        btn.disabled = false;
      });
  });

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