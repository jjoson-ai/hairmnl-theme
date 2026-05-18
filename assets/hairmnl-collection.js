/*
 * HairMNL custom theme JS — Pipeline 8 add-on
 * Split from hairmnl-custom.js per bd ujg6.14
 * Collection-template behaviours only
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
  // 2) facet-ajax — Section Rendering API for filter/sort (bd ujg6.16)
  // ----------------------------------------------------------------
  // P8 stock's filter-form class (theme.js Ir) binds debounced input
  // listeners on [data-sidebar-filter-form] that call this.form.submit()
  // — a programmatic submit triggers a FULL PAGE RELOAD (~3-5s on mobile
  // Slow 4G). The Section Rendering API can re-render just the collection
  // section's HTML in a fraction of that time.
  //
  // Intercept point: form.submit() is the only call site, so we monkey-
  // patch the form's submit method. Submit-event listeners don't fire on
  // programmatic .submit() — the method patch is the cleanest hook.
  //
  // Flow:
  //   1. Build URL from FormData → currentPath?filter.v.option1=X&...
  //   2. fetch URL + &section_id=<dynamic> (id discovered from the form's
  //      enclosing .shopify-section element so it works on the standard
  //      'collection' template and any future variants)
  //   3. Swap section innerHTML with response
  //   4. Dispatch shopify:section:load so P8's filter-form class re-binds
  //   5. history.pushState(newPath)
  //
  // V1 concessions (documented):
  //   - popstate triggers a full reload (back-button state restoration
  //     would require storing facet snapshots; out of scope V1)
  //   - Network failure → graceful fallback to full reload
  //   - Scope: collection-template only (this file is template-gated);
  //     /search is a separate template + separate ticket
  //
  // Out of scope: pagination (separate ticket if also full-reload);
  // brand-collection.liquid templates (30 templates, no filters present).
  // ============================================================
  (function () {
    var FACET_FORM_SELECTOR = '[data-sidebar-filter-form]';

    function initFacetAjax() {
      var form = document.querySelector(FACET_FORM_SELECTOR);
      if (!form) return;
      // Prevent double-patching when shopify:section:load fires on the
      // section we just swapped.
      if (form.__facetAjaxPatched) return;
      form.__facetAjaxPatched = true;

      var sectionEl = form.closest('.shopify-section');
      if (!sectionEl || !sectionEl.id) return;
      var sectionId = sectionEl.id.replace(/^shopify-section-/, '');

      form.submit = function () {
        var formData = new FormData(form);
        var params = new URLSearchParams();
        formData.forEach(function (value, key) {
          // Skip empty values to keep URLs clean and match Shopify's own
          // filter URL convention (omits empties on standard submits).
          if (value !== '' && value != null) params.append(key, value);
        });

        var newSearch = params.toString();
        var newPath = window.location.pathname + (newSearch ? '?' + newSearch : '');
        var fetchUrl = newPath + (newSearch ? '&' : '?') + 'section_id=' + encodeURIComponent(sectionId);

        sectionEl.setAttribute('aria-busy', 'true');

        fetch(fetchUrl, { headers: { 'Accept': 'text/html' }, credentials: 'same-origin' })
          .then(function (r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.text();
          })
          .then(function (html) {
            sectionEl.innerHTML = html;
            sectionEl.removeAttribute('aria-busy');

            // Trigger P8's section onLoad lifecycle so the (now-new) filter
            // form class re-binds its debounced input handlers. P8's handler
            // (theme.js line 324) uses event.target as the section element,
            // so dispatch FROM the section element with bubbles:true.
            sectionEl.dispatchEvent(new CustomEvent('shopify:section:load', {
              bubbles: true,
              detail: { sectionId: sectionId }
            }));

            history.pushState({ facetState: newPath }, '', newPath);

            // The shopify:section:load above will trigger initFacetAjax again
            // (via our own listener below). Belt-and-suspenders: also call
            // here in case section-load doesn't propagate as expected.
            initFacetAjax();
          })
          .catch(function (err) {
            console.warn('[hairmnl-collection] facet AJAX failed, falling back to full reload:', err);
            sectionEl.removeAttribute('aria-busy');
            window.location.href = newPath;
          });
      };
    }

    // Bind on initial page load + after any section reload (TAE re-init etc.)
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initFacetAjax);
    } else {
      initFacetAjax();
    }
    document.addEventListener('shopify:section:load', initFacetAjax);

    // V1 popstate: full reload. Acceptable concession; saves the complexity
    // of snapshotting facet HTML on every change. Browsers cache the previous
    // page anyway, so back-button is usually instant from bfcache.
    window.addEventListener('popstate', function (e) {
      if (e.state && e.state.facetState) window.location.reload();
    });
  })();

})();