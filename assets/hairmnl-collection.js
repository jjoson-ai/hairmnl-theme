/*
 * HairMNL custom theme JS — Pipeline 8 add-on
 * Split from hairmnl-custom.js per bd ujg6.14
 * Collection-template behaviours only (~30 LoC)
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

})();