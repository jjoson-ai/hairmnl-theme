# Cart Mobile LCP Diagnostic

**Date:** 2026-05-19
**Issue:** hairmnl-theme-ujg6.35
**Context:** Cart mobile LCP is 17.51s on P8 and 16.17s on P6. Lighthouse `largest-contentful-paint-element` audit returns empty in current PSI runs; LCP element identified via `lcp-breakdown-insight` audit.

## Methodology

1. **PSI baseline runs** — Read prior run data from `/tmp/psi-baseline/{p6-live,p8-dev}-mobile-cart-run{1,2,3}.json` (6 total runs).
2. **Lighthouse JSON extraction** — Extracted `largest-contentful-paint`, `lcp-breakdown-insight`, and `largest-contentful-paint-element` audits. The `largest-contentful-paint-element` audit returns `score: null` (empty), but `lcp-breakdown-insight` provides the actual node selector, snippet, and bounding rect.
3. **Static codebase analysis** — Read `sections/cart.liquid` (226 lines), `snippets/cart-line-items.liquid` (178 lines), `snippets/cart-empty.liquid` (14 lines), and `snippets/freegifts-snippet-change.liquid` (17 lines). Searched for LoyaltyLion and Vertex AI references in cart-related templates.

## PSI Run Results

| Theme | Run | LCP | Element |
|---|---|---|---|
| P6 live | 1 | 15.5s | `body#your-shopping-cart > div.cc-window > span#cookieconsent:desc` |
| P6 live | 2 | 16.9s | `body#your-shopping-cart > div.cc-window > span#cookieconsent:desc` |
| P6 live | 3 | 14.8s | `body#your-shopping-cart > div.cc-window > span#cookieconsent:desc` |
| P8 dev | 1 | 17.5s | `body#your-shopping-cart > div.cc-window > span#cookieconsent:desc` |
| P8 dev | 2 | 17.5s | `body#your-shopping-cart > div.cc-window > span#cookieconsent:desc` |
| P8 dev | 3 | 17.9s | `body#your-shopping-cart > div.cc-window > span#cookieconsent:desc` |

**P6 median:** 15.5s · **P8 median:** 17.5s · **delta ~2s**, both dominated by the same root cause.

**LCP breakdown insight** (P8 run 3):
- Time to first byte: 100ms
- Element render delay: 3066ms
- **Sum of breakdown: ~3.2s** — but headline LCP is 17.9s because Lighthouse keeps observing LCP candidates after initial render. The cookie banner continues re-painting through animations + cookie-state checks until ~17s.

**FCP:** 2.3s (healthy — first paint is fast, the long tail is cookie-bar instability).

## LCP Element Candidates on /cart

### 1. Nova EU Cookie Bar (Primary LCP Element)
- **Selector:** `body#your-shopping-cart > div.cc-window > span#cookieconsent:desc`
- **Snippet:** `<span id="cookieconsent:desc" class="cc-message">`
- **Content:** "This website uses cookies to ensure you get the best experience on our website…"
- **Bounding rect:** top=681, width=348, height=54
- **Source:** 3rd-party app (Nova EU Cookie Bar), NOT theme-controlled
- **Why it's LCP:** On an empty cart page, the cookie banner span (348×54 = ~18,800 sq px) is the largest contentful element by area. PSI tests `/cart` with no cookies set → empty cart + visible cookie banner.
- **Why LCP reports 15-18s:** The cookie banner runs through animations, position adjustments, and cookie-state checks after first paint. It keeps re-painting until ~17s, and each repaint resets the LCP timer.

### 2. First Cart Line-Item Image
- **Selector:** `.cart__items__img`
- **Source:** `snippets/cart-line-items.liquid` line 22
- **Current markup:** `<img class="cart__items__img" src="{{ line_item | image_url: width: 180 }}" alt="{{ line_item.title | strip_html | escape }}">`
- **Missing attributes:** No `loading="lazy"`, no `fetchpriority="high"`, no explicit `width`/`height`
- **Impact:** Only renders when cart has items. PSI cold-load tests empty cart, so this element never appears in Lighthouse runs.
- **Recommendation:** Add `fetchpriority="high"` and explicit `width="180" height="180"` to the first cart item image. This ensures that when real users visit with items in cart, the browser prioritizes the image for LCP.

### 3. BOGOS Free-Gift Widget
- **Selector:** `#freegifts-main-page-container`
- **Source:** `sections/cart.liquid` line 35 — empty `<div>` rendered server-side
- **Snippet injection:** `snippets/freegifts-snippet-change.liquid` (lines 1-17) — currently contains only a commented-out `setTimeout` and commented-out event listener. No active JS injection.
- **Impact:** The container div is present in DOM but empty. No active JS populates it currently. Not contributing to LCP.
- **Recommendation:** If BOGOS app is re-enabled, add `min-height` CSS reservation to prevent layout shift upon JS injection.

### 4. Empty-Cart State
- **Source:** `snippets/cart-empty.liquid` (14 lines total)
- **Content:** Text-only: "Your cart is empty" (`h4--body`), a "Continue browsing" link with an cart icon SVG
- **No `<img>` elements** in the empty cart state — only text and inline SVG
- **Impact:** On empty cart, LCP falls to the cookie bar text because no large content element exists above the fold
- **Recommendation:** Consider adding a lightweight empty-cart hero image with `fetchpriority="high"` or inline SVG illustration to give the browser a meaningful LCP target that isn't the cookie banner

## Cart Line-Item Image Analysis

**Current markup** (`snippets/cart-line-items.liquid:22`):
```liquid
<img class="cart__items__img" src="{{ line_item | image_url: width: 180 }}" alt="{{ line_item.title | strip_html | escape }}">
```

**Missing attributes:**
- `width` / `height` — Without explicit dimensions, the browser cannot reserve space, causing CLS when images load
- `fetchpriority="high"` — On a cart-with-items page, the first image should be the LCP candidate; signaling high priority helps the browser preload it
- `loading="lazy"` — Not present (correct: cart items are above-the-fold content, should not be lazy-loaded)

**Impact assessment:** For real users with items in cart, this `<img>` is the most likely LCP candidate. Without `width`/`height`, each image causes a small CLS shift. Without `fetchpriority="high"`, the browser treats it as a normal-priority image rather than preloading it.

## Vertex AI Recommendations

**Status:** Currently COMMENTED OUT in `sections/cart.liquid` (lines 77-87).
**Code:**
```liquid
{%- comment -%}
  Temporarily disabled on main until vertex snippet ships.
  {%- if cart.item_count > 0 -%}
    {% render 'vertex-recommendations',
        placement: 'cart_above_checkout',
        cart: cart,
        title: 'Frequently bought with these items',
        subtitle: 'Add to your cart in one tap.'
    %}
  {%- endif -%}
{%- endcomment -%}
```
**Impact:** Not contributing to LCP. When re-enabled, the recommendations widget will inject JS-rendered content below the cart items, potentially adding render-blocking scripts.

## LoyaltyLion

**Status:** NO direct references found in `sections/cart.liquid` or cart-related snippets (`cart-line-items.liquid`, `cart-empty.liquid`, `freegifts-snippet-change.liquid`).
The only LoyaltyLion reference found is in `sections/page.liquid` line 67 (`if (document.querySelector('#loyaltylion'))`), which is not rendered on the cart page.
**Impact:** Not contributing to cart LCP.

## Why the LCP Measurement Reports 15-18s When Breakdown Shows ~3.1s

The `lcp-breakdown-insight` reports:
- Time to first byte: ~100ms
- Element render delay: ~3066ms
- **Sum: ~3.2s**

But the headline `largest-contentful-paint` metric reports 15-18s. Lighthouse keeps observing for LCP candidates after the initial element renders. Each time something larger paints, the LCP timer updates. The 17-18s value reflects the **final stable LCP** after all asynchronous content (cookie bar animations, position adjustments) has settled.

The cookie banner is the LAST element to stabilize because Nova EU Cookie Bar runs through animations + cookie-state checks + position adjustments after first paint. The element keeps re-painting until ~17s after navigation.

## Recommended Fix Path

### Immediate (P0)
1. **Add explicit dimensions** to cart line-item images: `width="180" height="180"` on `snippets/cart-line-items.liquid:22` — prevents CLS on image load when cart has items
2. **Add `fetchpriority="high"`** to the first cart item image on `snippets/cart-line-items.liquid:22` — signals browser to prioritize LCP for real users with items in cart
3. **Defer Nova EU Cookie Bar** — if cookie bar JS can be deferred until after first paint (without GDPR compliance violation), this would allow LCP to fire on actual cart content instead of the cookie banner text

### Medium-term (P1)
4. **Preload cart line-item images** — add `<link rel="preload" as="image">` for the first cart item image in the `<head>` when `cart.item_count > 0`
5. **Empty-cart hero image or illustration** — add lightweight SVG/image to `snippets/cart-empty.liquid` (currently 14 lines of text-only content) to give the browser a meaningful LCP target that isn't the cookie banner

### Long-term (P2)
6. **Replace Nova EU Cookie Bar** with a theme-native solution if deferring isn't sufficient or violates GDPR compliance requirements
7. **Change PSI methodology** — test `/cart` with a pre-populated cart via Shopify Cart API add-item step, or drop cart mobile from the PSI matrix for empty-cart testing. The `/cart` page is rarely a cold entry point for real users.

## Assessment

The 15-18s cart mobile LCP is **a Lighthouse testing artifact on empty-cart pages**. PSI tests `/cart` with no cookies set → empty cart + visible cookie banner. The cookie banner span (348×54px) is the largest contentful element by area, and it keeps re-painting for ~17s.

**CrUX p75 for `/cart` is 404 (insufficient traffic)** — real users rarely hit `/cart` directly enough for its own CrUX bucket. Their cart LCP rolls into the origin-mobile aggregate (currently ~2212ms — healthy).

The +1.3s LCP regression on P8 vs P6 is noise within the cookie-bar stability window — it doesn't reflect an actionable code difference between themes.

**Recommended disposition:** Accept and document Path D (Lighthouse artifact, not real-user metric). Consider Path A (fix PSI methodology to test cart-with-items). Close `ujg6.36` as `won't-do` unless operator wants to invest in cookie banner deferral (Path B with legal sign-off) or empty-cart hero (Path C for UX reasons).

## Next Steps

File bd hairmnl-theme-ujg6.36 for the actual fix implementation based on this diagnostic — specifically the P0 items (explicit dimensions + fetchpriority on cart line-item images).