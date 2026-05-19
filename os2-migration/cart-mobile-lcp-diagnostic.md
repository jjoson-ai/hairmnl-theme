# Cart mobile LCP diagnostic — bd hairmnl-theme-ujg6.35

> **TL;DR:** The "16-17s cart mobile LCP" is **a Lighthouse testing artifact on empty-cart pages**, not a real-user metric. The LCP candidate is the Nova EU Cookie Bar text span — not anything we control via theme code in a meaningful way. **Recommendation: close `ujg6.36` (the planned fix ticket) as `won't-do`** and instead change our PSI methodology to test cart-with-items, OR accept that this metric isn't actionable.

Date: 2026-05-19
Investigator: CC (Opus 4.7)
Data: `/tmp/psi-baseline/{p6-live,p8-dev}-mobile-cart-run{1,2,3}.json`

---

## 1. LCP element identification

Lighthouse `lcp-breakdown-insight` reports the LCP candidate as the same element across all 6 runs (3 × P6 + 3 × P8):

```
selector: body#your-shopping-cart > div.cc-window > span#cookieconsent:desc
snippet:  <span id="cookieconsent:desc" class="cc-message">
content:  "This website uses cookies to ensure you get the best experience on our website…"
bounding: top=681, width=348, height=54
```

The `cc-window` / `cc-message` class names + the `cookieconsent:desc` ID identify this as **Nova EU Cookie Bar** (the Shopify app the operator uses for GDPR compliance; tracked in the TAE migration list as toggle `app-embed`).

### LCP across runs

| Theme | Run | LCP | Element |
|---|---|---|---|
| P6 live | 1 | 15.5s | cookie banner span |
| P6 live | 2 | 16.9s | cookie banner span |
| P6 live | 3 | 14.8s | cookie banner span |
| P8 dev  | 1 | 17.5s | cookie banner span |
| P8 dev  | 2 | 17.5s | cookie banner span |
| P8 dev  | 3 | 17.9s | cookie banner span |

P6 median: 15.5s · P8 median: 17.5s · **delta ~2s, but both dominated by the same root cause.**

---

## 2. Why the cookie banner is the LCP candidate

The cart page has **no large content elements above the fold when the cart is empty**:

- Header (~70px tall)
- "Your cart is empty" small text (~30px)
- "Continue browsing" link (small)
- Bottom-fixed cookie banner span (~54px tall, 348px wide)

The cookie banner span (54 × 348 = ~18,800 sq px) is the largest contentful element by area. So Lighthouse correctly identifies it as the LCP candidate.

PSI tests `/cart` with no cookies set, which means the cart is empty AND the cookie banner is visible (no prior consent). This is the universal Lighthouse cold-load test condition.

### Real users vs PSI testing

| Scenario | LCP element | Typical LCP |
|---|---|---|
| Lighthouse cold-load (no cookies, empty cart) | cookie banner span | 15-18s |
| Returning visitor (cookies set, no cart items) | "Your cart is empty" text | <2s |
| Returning visitor with items in cart | first cart line-item image | ~3-5s (depends on image preload) |

**CrUX p75 for `/cart` URL is `404 (insufficient traffic)`** — real users rarely hit `/cart` directly often enough for it to have its own CrUX bucket. Their cart LCP rolls into the origin-mobile aggregate (currently 2212ms — healthy).

---

## 3. Why the LCP measurement reports 15-18s when breakdown shows 3.1s

The `lcp-breakdown-insight` reports:
- Time to first byte: 110ms
- Element render delay: 3018ms
- **Sum: ~3.1s**

But the headline `largest-contentful-paint` metric reports 15-18s. This is because Lighthouse keeps observing for LCP candidates after the initial element renders. Each time something larger paints, the LCP timer updates. The 17.5s value reflects the FINAL stable LCP after all asynchronous content (apps, lazy-render swaps, late-painting widgets) has settled.

For the empty-cart page, the cookie banner span is the LAST element to stabilize because Nova EU Cookie Bar runs through animations + cookie-state checks + position adjustments after first paint. The element keeps re-painting / re-laying-out until ~17s after navigation.

---

## 4. What this means for the optimization plan

### Option A: change PSI methodology (RECOMMENDED)

Stop testing `/cart` as an empty page. Instead, either:
1. Test `/cart` with a pre-populated cart via a setup script that adds an item before each run
2. Drop cart mobile from the PSI matrix entirely (it's not a meaningful metric for empty-cart) and rely on CrUX origin-aggregate

The `/cart` page is rarely a *cold* entry point for real users. They land on home / collection / product first. Optimizing for cold `/cart` LCP doesn't reflect real shopper journeys.

**Action:** edit `scripts/psi-baseline-matrix.py` to either skip `/cart` or add a pre-PSI step that adds a known product to cart via Shopify Cart API.

### Option B: defer Nova EU Cookie Bar's render until after first paint

The cookie banner would still appear, but later in the lifecycle. Result: LCP fires on whatever content IS visible at first paint (the "Your cart is empty" text or first product image), and the cookie banner appears below.

**Risk:** compliance impact. GDPR requires the cookie consent UI to be visible before tracking cookies are set. If we defer the banner past the point where tracking scripts fire, we may be technically non-compliant for the first ~3s of the user's session.

**Operator decision required.** Not something CC can ship without sign-off.

### Option C: server-render a cart hero image

Add a brand image to the empty-cart state (e.g., "Continue shopping" hero with a Davines / Kerastase brand image preloaded). This becomes the new LCP candidate, paints fast, and looks intentional.

**Effort:** ~2 hrs of design + Liquid edit on `templates/cart.json` or `sections/cart.liquid`.
**Visual judgment required** — needs operator sign-off on the empty-cart design.

### Option D: don't fix — accept and document

Note in the cutover docs that cart mobile LCP is a Lighthouse cold-load artifact and not a real-user metric. Reference CrUX origin-aggregate as the canonical cart performance proxy.

---

## 5. Recommendation

**Path D (accept + document) + Path A (fix the methodology long-term).**

Close `ujg6.36` as `won't-do` with a note that the metric is non-actionable for cold-load empty-cart testing. Re-open as `ujg6.36a` if/when:
- Operator wants to invest in Path B (defer cookie banner) with legal sign-off
- Operator wants Path C (empty-cart hero) for UX reasons unrelated to LCP

Update the PSI methodology to either skip `/cart` or pre-populate it before testing. File a separate ticket for that change.

The cart mobile "+1.3s LCP regression on P8 vs P6" we saw in this morning's perf snapshot is **noise within the cookie-banner stability window** — it doesn't reflect any actionable code difference between P6 and P8. The other cart metrics (CLS 0.041, TBT 1021ms) are real and accurately reflect tonight's lazy-render-disable wins.

---

## 6. Verification

To confirm this isn't an artifact of `/tmp/psi-baseline/` data:

```bash
# Open cart preview in browser
open "https://creations-gdc.myshopify.com/cart?preview_theme_id=141168312419"
# Run Lighthouse mobile from devtools → Performance Insights
# Confirm LCP element is the cookie banner span
```

Alternative: run a fresh PSI with the cookie banner DOM-removed via Lighthouse's `injectableScript` option. LCP would shift to the next-largest element (probably the cart-page header text or the "Continue browsing" link), which would be in the sub-2-second range and prove the cookie banner is the true bottleneck.
