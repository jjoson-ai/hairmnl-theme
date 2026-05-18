/*
 * HairMNL custom theme JS — Pipeline 8 add-on
 * Split from hairmnl-custom.js per bd ujg6.14
 * Product-template behaviours only (~30 LoC)
 */

(function () {
  'use strict';

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

})();