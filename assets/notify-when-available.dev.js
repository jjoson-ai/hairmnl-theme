/**
 * notify-when-available.dev.js — Back-in-Stock modal driver (Klaviyo-native).
 *
 * MIGRATION-DEBT: bd hairmnl-theme-g1n.5 (2026-07-24). Appikon replacement
 * (epic g1n). Plain DOM + fetch; zero Pipeline-6 coupling beyond the
 * theme:variant:change event and themeVendor.MicroModal. Port to OS 2.0:
 * copy both asset files + the theme.liquid wiring block.
 *
 * Canonical source: THIS file. assets/notify-when-available.js is the
 * minified mirror — regenerate after every edit with:
 *   npx esbuild assets/notify-when-available.dev.js --minify \
 *     --outfile=assets/notify-when-available.js
 *
 * Klaviyo client API (public key only, CORS-enabled, no auth header):
 *   POST /client/back-in-stock-subscriptions/  (BIS waitlist signup)
 *   POST /client/subscriptions/                (newsletter consent, optional)
 * Payload shapes verified against developers.klaviyo.com 2026-07-24
 * (profile is a nested {data:{type,attributes}} object — NOT flat).
 *
 * Company id resolution order (anti-fabrication — never hardcoded):
 *   1. <meta name="klaviyo-company-id">          (explicit override, T1 owner)
 *   2. The existing Klaviyo app-embed script tag  (?company_id= or path form)
 * Newsletter list id: <meta name="klaviyo-newsletter-list-id">. Absent ⇒
 * newsletter call is skipped (BIS signup still proceeds).
 *
 * SMS: decision 2026-07-24 = Option A (email-only). The phone branch below
 * activates only if the modal renders a [data-notify-field="sms"] block,
 * which is Liquid-gated behind settings.bis_sms_enabled (undefined today).
 */
(function () {
  'use strict';

  var API_REVISION = '2024-10-15';
  var API_BASE = 'https://a.klaviyo.com';
  var MODAL_ID = 'notify-when-available-modal';
  var CLOSE_DELAY_MS = 2000;
  var PH_LOCAL_PATTERN = /^9\d{9}$/;

  var state = {
    companyId: null,
    newsletterListId: null,
    variantId: null,
    variantSku: null,
    productTitle: null,
    variantTitle: null,
    warnedNoList: false
  };

  /* ── Config resolution ─────────────────────────────────────── */

  function resolveCompanyId() {
    var meta = document.querySelector('meta[name="klaviyo-company-id"]');
    if (meta && meta.content) return meta.content.trim();

    var tags = document.querySelectorAll('script[src*="static.klaviyo.com/onsite/js"]');
    for (var i = 0; i < tags.length; i++) {
      var src = tags[i].getAttribute('src') || '';
      var q = src.match(/[?&]company_id=([A-Za-z0-9]+)/);
      if (q) return q[1];
      var p = src.match(/onsite\/js\/([A-Za-z0-9]+)\/klaviyo\.js/);
      if (p) return p[1];
    }
    return null;
  }

  function resolveNewsletterListId() {
    var meta = document.querySelector('meta[name="klaviyo-newsletter-list-id"]');
    return meta && meta.content ? meta.content.trim() : null;
  }

  /* ── Modal helpers ─────────────────────────────────────────── */

  function modalEl() {
    return document.getElementById(MODAL_ID);
  }

  function fireFormsEvent(type) {
    // Matches the shape the GA4 bridge in layout/theme.liquid listens for.
    try {
      window.dispatchEvent(new CustomEvent('klaviyoForms', {
        detail: {
          type: type,
          formId: 'notify-when-available',
          metaData: { variantId: state.variantId, sku: state.variantSku }
        }
      }));
    } catch (err) { /* analytics must never break the flow */ }
  }

  function setError(message) {
    var box = modalEl().querySelector('[data-notify-error]');
    if (!box) {
      box = document.createElement('p');
      box.className = 'notify-modal__error';
      box.setAttribute('data-notify-error', '');
      box.setAttribute('role', 'alert');
      var form = modalEl().querySelector('[data-notify-form]');
      form.insertBefore(box, form.firstChild);
    }
    box.textContent = message || '';
    box.hidden = !message;
  }

  function setBusy(busy) {
    var btn = modalEl().querySelector('[data-notify-submit]');
    if (btn) {
      btn.disabled = busy;
      btn.classList.toggle('is-busy', busy);
    }
  }

  function showSuccess() {
    var modal = modalEl();
    modal.querySelector('[data-notify-form]').hidden = true;
    var ok = modal.querySelector('[data-notify-success]');
    ok.hidden = false;
    fireFormsEvent('submit');
    window.setTimeout(function () {
      try { themeVendor.MicroModal.close(MODAL_ID); } catch (err) { /* already closed */ }
    }, CLOSE_DELAY_MS);
  }

  function resetModal() {
    var modal = modalEl();
    var form = modal.querySelector('[data-notify-form]');
    form.hidden = false;
    modal.querySelector('[data-notify-success]').hidden = true;
    setError(null);
    setBusy(false);
  }

  /* ── Klaviyo calls ─────────────────────────────────────────── */

  function klaviyoPost(path, payload) {
    return window.fetch(
      API_BASE + path + '?company_id=' + encodeURIComponent(state.companyId),
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', revision: API_REVISION },
        body: JSON.stringify(payload)
      }
    ).then(function (res) {
      if (res.ok) return res; // BIS + subscriptions return 202, empty body
      return res.json().catch(function () { return {}; }).then(function (body) {
        var detail = body && body.errors && body.errors[0] && body.errors[0].detail;
        throw new Error(detail || ('Klaviyo error ' + res.status));
      });
    });
  }

  function subscribeBackInStock(channel, profileAttributes) {
    return klaviyoPost('/client/back-in-stock-subscriptions/', {
      data: {
        type: 'back-in-stock-subscription',
        attributes: {
          channels: [channel],
          profile: { data: { type: 'profile', attributes: profileAttributes } }
        },
        relationships: {
          variant: {
            data: {
              type: 'catalog-variant',
              id: '$shopify:::$default:::' + state.variantId
            }
          }
        }
      }
    });
  }

  function subscribeNewsletter(profileAttributes) {
    if (!state.newsletterListId) {
      if (!state.warnedNoList) {
        state.warnedNoList = true;
        console.warn('[notify-bis] newsletter list id meta tag missing — skipping list signup (see bd g1n.2/g1n.7)');
      }
      return Promise.resolve();
    }
    return klaviyoPost('/client/subscriptions/', {
      data: {
        type: 'subscription',
        attributes: {
          custom_source: 'Back in Stock modal',
          profile: { data: { type: 'profile', attributes: profileAttributes } }
        },
        relationships: {
          list: { data: { type: 'list', id: state.newsletterListId } }
        }
      }
    }).catch(function (err) {
      // Newsletter consent is best-effort; the BIS signup already succeeded.
      console.warn('[notify-bis] newsletter signup failed:', err.message);
    });
  }

  /* ── Submit flow ───────────────────────────────────────────── */

  function selectedChannel(form) {
    var sms = form.querySelector('[data-notify-channel="sms"]');
    return sms && sms.checked ? 'SMS' : 'EMAIL';
  }

  function onSubmit(event) {
    event.preventDefault();
    var form = event.currentTarget;
    setError(null);

    if (!state.companyId) {
      setError('Notifications are temporarily unavailable. Please try again later.');
      console.warn('[notify-bis] Klaviyo company id not found on page');
      return;
    }
    if (!state.variantId) {
      setError('Something went wrong — please close this window and try again.');
      return;
    }

    var channel = selectedChannel(form);
    var emailInput = form.querySelector('[data-notify-input="email"]');
    var phoneInput = form.querySelector('[data-notify-input="phone"]');
    var profileAttributes = {};

    if (channel === 'SMS' && phoneInput) {
      var local = (phoneInput.value || '').replace(/\D/g, '');
      if (!PH_LOCAL_PATTERN.test(local)) {
        setError(phoneInput.closest('[data-notify-field]')
          .querySelector('.notify-modal__phone-hint').textContent);
        phoneInput.focus();
        return;
      }
      profileAttributes.phone_number = '+63' + local;
    } else {
      if (!emailInput || !emailInput.checkValidity() || !emailInput.value) {
        setError('Please enter a valid email address.');
        if (emailInput) emailInput.focus();
        return;
      }
      profileAttributes.email = emailInput.value.trim();
    }

    var wantsNewsletter = !!form.querySelector('input[name="accepts_marketing"]:checked');

    setBusy(true);
    subscribeBackInStock(channel, profileAttributes)
      .then(function () {
        return wantsNewsletter ? subscribeNewsletter(profileAttributes) : null;
      })
      .then(showSuccess)
      .catch(function (err) {
        setBusy(false);
        setError(err.message || 'Could not save your request. Please try again.');
      });
  }

  /* ── Trigger + variant wiring ──────────────────────────────── */

  function openFromTrigger(trigger) {
    state.variantId = trigger.getAttribute('data-variant-id');
    state.variantSku = trigger.getAttribute('data-sku');
    state.productTitle = trigger.getAttribute('data-product-title');
    state.variantTitle = trigger.getAttribute('data-variant-title');

    var modal = modalEl();
    if (!modal) return;
    resetModal();

    var subtitle = modal.querySelector('[data-notify-product-title]');
    if (subtitle) {
      var label = state.productTitle || '';
      if (state.variantTitle && state.variantTitle !== 'Default Title') {
        label += ' — ' + state.variantTitle;
      }
      subtitle.textContent = label;
    }

    themeVendor.MicroModal.show(MODAL_ID, {
      onClose: function () { fireFormsEvent('close'); }
    });
    fireFormsEvent('open');
  }

  function onVariantChange(event) {
    var variant = event.detail && event.detail.variant;
    if (!variant) return;

    var soldOut = variant.available === false;
    var triggers = document.querySelectorAll('[data-notify-trigger]');
    for (var i = 0; i < triggers.length; i++) {
      triggers[i].hidden = !soldOut;
      if (variant.id) triggers[i].setAttribute('data-variant-id', String(variant.id));
      if (variant.sku != null) triggers[i].setAttribute('data-sku', variant.sku);
      if (variant.title != null) triggers[i].setAttribute('data-variant-title', variant.title);
    }
    var wrappers = document.querySelectorAll('.product__submit__buttons');
    for (var j = 0; j < wrappers.length; j++) {
      wrappers[j].classList.toggle('product__submit__buttons--notify', soldOut);
    }
  }

  /* ── Init ──────────────────────────────────────────────────── */

  function init() {
    if (!modalEl()) return; // non-PDP or snippet not rendered
    if (window.__hairmnlNotifyBISInit) return;
    window.__hairmnlNotifyBISInit = true;

    state.companyId = resolveCompanyId();
    state.newsletterListId = resolveNewsletterListId();

    // Portal the sticky tab to <body>: Pipeline sections animate with AOS
    // transforms, which would trap a position:fixed tab inside the section
    // (kt0 containing-block rule). Direct child of body has no such ancestor.
    var tab = document.querySelector('[data-notify-tab]');
    if (tab && tab.parentElement !== document.body) {
      document.body.appendChild(tab);
    }

    document.addEventListener('click', function (event) {
      var trigger = event.target.closest ? event.target.closest('[data-notify-trigger]') : null;
      if (trigger) openFromTrigger(trigger);
    });

    document.addEventListener('theme:variant:change', onVariantChange);

    var form = document.querySelector('[data-notify-form]');
    if (form) form.addEventListener('submit', onSubmit);
  }

  window.HairMNLNotifyBIS = { init: init };

  if (document.readyState !== 'loading') {
    init();
  } else {
    document.addEventListener('DOMContentLoaded', init);
  }
})();
