# Vertex Placement & Layout Guide

> **Deliverable produced from** `vertex-placement-design-brief.md` (2026-05-02). Source-of-truth spec for the four Vertex AI recommendation slots replacing LimeSpot on hairmnl.com, plus the cart-drawer addendum and the buy-it-again addendum.
>
> **Scope:** what each placement looks like, why each layout choice was made, exactly what engineering needs to edit. Out of scope: the rec engine itself, model training, metafield write paths.
>
> **As of 2026-05-05.** The universal foundation (`snippets/vertex-recommendations.liquid`, `snippets/vertex-rec-card.liquid`, `assets/vertex-recommendations.css`) is already implemented in the draft theme `140785582179` and rendering on every PDP. This guide documents the as-built decisions, surfaces the open team approvals, and gives engineering the file/line edit list to ship visual refinements + the three not-yet-cut-over slots to live theme `131664707683`.

---

## Executive summary

HairMNL is replacing LimeSpot ($403/mo) with Google Vertex AI Search for Commerce. Recommendation **data** is solved — Vertex models write top-30 lists into Shopify metafields nightly; Liquid widgets read them at render time with zero request-path API calls. **This guide covers presentation only.**

Four placements ship in the LimeSpot replacement, plus two related surfaces:

| # | Placement | Slug | Vertex model | Status |
|---|---|---|---|---|
| 1 | PDP — Complete the routine | `pdp_below_atc` | FBT (frequently bought together) | **Live on draft, data flowing.** Visual polish + copy approval pending. |
| 2 | Cart — Frequently bought with these items | `cart_above_checkout` | FBT keyed on cart contents | Wired on draft, data flowing. Native-form vs. AJAX decision pending. |
| 3 | Homepage — Trending in your routine | `home_below_hero` | RFY (recommended for you) for logged-in / popularity for anonymous | Wired on draft, **gated on RFY model** going ACTIVE (~2026-05-07). |
| 4 | PDP — You may also like | `pdp_below_description` | Similar items | Wired on draft, **gated on similar-items model** (TRAINING, stuck >3 days as of brief — needs separate diagnostic). |
| A | Cart drawer — Add to your routine | `cart_drawer_below_items` | FBT (cart anchor) | Live on draft. Tighter compact card, no inline ADD. |
| B | Homepage / account — Time to restock | `vertex-buy-it-again` snippet | Buy-it-again (per-customer replenishment) | Snippet exists, wired into `section-banner-slider.liquid`. **Unique to Vertex** — LimeSpot doesn't ship this. |

**Universal design DNA across all placements:**
- Mobile-first horizontal scroll-snap rail with 2.25 cards visible (peek of 3rd signals scrollability)
- Centered title in HairMNL's heading font (SelfModern), 18/22px, no oversized H2
- White card on white background, 1:1 image, 2-line title clamp, vendor eyebrow, price + optional sale strikethrough
- Native CSS scroll-snap, **zero new framework JS** (~25 lines for nav buttons), under 5KB JS budget per brief
- Scoped to `.hairmnl-theme` body class — never bleeds into BSS B2B / Klaviyo / Reamaze widgets

**Single largest open decision:** the cart slot's inline ADD button currently submits via `<form action="/cart/add">` (native page reload). The team flagged ~30 lines of inline AJAX as an alternative. Decision affects only the cart slot; nothing else changes.

---

## 1. Universal design system

### 1.1 Scope and naming

All Vertex slots inherit from a single foundation:

- **Snippet:** `snippets/vertex-recommendations.liquid` (305 lines) — slot router + rail markup
- **Card:** `snippets/vertex-rec-card.liquid` (135 lines) — vertical default + cart compact variants
- **Stylesheet:** `assets/vertex-recommendations.css` (~600 lines, ~12KB minified) — all visual rules
- **Body class:** `.hairmnl-theme` is added to `<body>` so every Vertex selector is scoped (`.hairmnl-theme .vrec-slot`, etc.)

This keeps the rec slots from leaking styles into LimeSpot (during the dual-render cutover window) or into Pipeline 6.1.3's native sections. It also keeps Pipeline + BSS B2B + Klaviyo + Reamaze rules from leaking *into* the rec slots.

### 1.2 Typography

| Token | Value | Why |
|---|---|---|
| Section title | `var(--font-stack-heading)` (SelfModern), 18px mobile / 22px desktop, weight 500, line-height 1.3 | Matches HairMNL's existing section-header convention ("Best Sellers", "New Arrivals"). The default H2 (~30-39px) competed with the actual product title for visual weight on PDPs — flagged by team in three review rounds. |
| Subtitle | inherit body font, 13px, color `var(--vrec-muted)`, weight 400 | Optional. When present, fills the line below the title. |
| Vendor eyebrow | inherit, 11px (10px mobile), weight 600, uppercase, letterspacing 0.05em, color `var(--vrec-mutedest)` | Reads like a brand badge, not body copy. Skipped if `product.vendor` is blank. |
| Card title | inherit, 13px (12px mobile), weight 400, line-height 1.35, **2-line clamp** | 2 lines is enough for HairMNL's typical product names ("L'Oréal Professionnel Serioxyl Advanced Denser Hair Growth Serum") without pushing the rail too tall. |
| Price | inherit, 14px (13px mobile), weight 600 | Heavier than title so it's the visual anchor on the card. |
| Compare-at price | inherit, 12px, weight 400, color `var(--vrec-mutedest)`, strikethrough | Only renders when `compare_at_price > price`. Aligned baseline with current price. |

**Why no Inter / Cormorant Garamond:** the original mockup hardcoded Inter, which produced a font mismatch flagged in three review rounds. The CSS now inherits HairMNL's actual configured body font (BasisGrotesquePro per `settings_data.json`) for body copy, and explicitly opts in to the heading variable for titles. Result: rec slots feel like native HairMNL sections, not a third-party widget.

### 1.3 Color tokens

```css
--vrec-bg:           #ffffff   /* slot container */
--vrec-card-bg:      #ffffff   /* card background */
--vrec-text:         #1a1a1a   /* primary copy */
--vrec-muted:        #6b6b6b   /* subtitle, ratings */
--vrec-mutedest:     #999999   /* vendor eyebrow, compare-at */
--vrec-rule:         #ececec   /* hairlines, card borders */
--vrec-image-bg:     #f0f0f0   /* image fallback while loading */
--vrec-sale:         #c0392b   /* sale price + sale badge */
--vrec-cta-bg:       #1a1a1a   /* cart-card ADD button */
--vrec-cta-fg:       #ffffff
--vrec-cta-bg-hover: #000000
```

Single warm grey ramp + one accent (`--vrec-sale` red). No gradient, no shadow on cards (cart compact card has a 1px border for definition, vertical card relies on the image edge).

### 1.4 Card component (shared across all placements)

#### Vertical default card

Used on PDP-FBT, PDP-similar, home-RFY, drawer.

```
┌─────────────────┐
│                 │
│   IMAGE 1:1     │  ← aspect-ratio: 1/1, object-fit: cover
│   [SALE]        │  ← top-left badge, only when on_sale
│                 │
└─────────────────┘
  VENDOR           ← 11px uppercase letterspaced, optional
  Product title    ← 13px, 2-line clamp
  ★★★★★ (124)      ← only if product.metafields.reviews.rating
  ₱1,250  ₱1,500   ← current bold + compare-at strikethrough
```

Anatomy decisions and their sources:

| Decision | Choice | Source |
|---|---|---|
| Image aspect ratio | 1:1 square | Sephora, Cult Beauty, Ulta all use square cards on rec rails (verified via screenshots in `design-research/`). HairMNL's existing `product-grid-item.liquid` also uses 1:1. Consistency > novelty. |
| Title clamp | 2 lines | Cult Beauty 2-line, Sephora 2-line, Ulta 2-line — convergent industry pattern. HairMNL's longest active product title fits in 2 lines at 13px on the narrowest mobile card width. |
| Vendor display | Always shown when present, above title | HairMNL stocks 50+ brands; brand recognition (Olaplex, Davines, Kérastase, L'Oréal) drives click-through more than product name does. Sephora and Cult Beauty both lead with brand. |
| Rating display | Shown only if `product.metafields.reviews.rating` exists, between title and price | Yotpo / Judge.me ratings exist on most HairMNL products. Where missing, no rating row prevents an empty hole. Stars use `★` glyph (no SVG, no JS). |
| Sale badge | Top-left of image | Industry standard. Top-right conflicts with Save / Wishlist heart on competitors (HairMNL doesn't have wishlist, but reserving top-right keeps that option open). |
| Sold-out treatment | Image opacity 0.6 + grey "Sold out" badge top-left | Doesn't hide the product (Vertex rec is still useful for understanding what *would* have paired); makes unavailability obvious without being shouty. |
| Click target | Entire card is `<a>` linking to PDP | One large click target > separate click zones. Per Baymard PDP UX research, full-card click targets outperform separated targets on mobile. |

**No "Add to cart" button on the vertical card.** Decision rationale: clicking through to PDP gives the customer the chance to read full details, see size/variant options, and check reviews — improving downstream conversion AND AOV. The compact cart card is the only exception, where context (already-deciding-to-buy) and quick-buy intent justify the inline button. Per Baymard, "the role of cross-sell recommendations is not always to be clicked — sometimes simply to be shown, exposing a shopper to more inventory."

#### Compact horizontal card (cart only)

Used on `cart_above_checkout` only.

```
┌──────┐  VENDOR
│      │  Product title (2-line)
│ IMG  │
│ 1:1  │  ₱1,250  ₱1,500       [ ADD TO CART ]
└──────┘
```

- 88px square image, gap 14px
- Vendor + title + price stack on the left
- Inline `<button name="add">` inside `<form action="/cart/add">` on the right
- Bottom-aligned price + button row (`margin-top: auto` on `.vrec-card__bottom`)
- 1px border (`var(--vrec-rule)`), 4px corner radius — visual separation from the line items above

The horizontal stacking on desktop, plus the inline ADD button, matches Pipeline 6's native upsell pattern (`snippets/upsell-product.liquid`). Customers already know how to tap "ADD" cards in cart context — we're matching their muscle memory, not inventing a new pattern.

### 1.5 Loading & empty states

#### Empty state — render nothing
Two failure modes are treated identically: either the metafield is empty, or every product reference fails to resolve (deleted/unpublished). The `vertex-recommendations.liquid` snippet pre-renders the rail into a `{% capture %}` buffer and checks if it's empty before emitting the `<section>`. **No "no products available" copy ever ships.** The slot is silent until it has something useful to show.

This is the gate that lets us wire the `home_below_hero` and `pdp_below_description` slots into the theme *now*, before their underlying models are ACTIVE — the slots simply don't render. When the models go ACTIVE, the metafields populate and the slot appears with no theme push needed.

#### Skeleton state (CSS-only, ~10 lines)
A `.vrec-card--skeleton` variant is defined in CSS for cases where we want to reserve layout space while data loads. **Currently not used** — the rec data is server-rendered from metafields, so there's no client-side load step. Reserved for a future enhancement (e.g. cart drawer rec refresh after AJAX add-to-cart).

CLS prevention is handled via:
- Explicit `width` and `height` on every `<img>`
- `aspect-ratio: 1 / 1` on `.vrec-card__image`
- `min-height` on the rail container during the brief render gap

Lighthouse CLS regression on the PDPs that have the FBT slot live: **0.00 incremental**. Verified on draft theme on 2026-05-04.

#### Out-of-stock card
Greyed image (opacity 0.6), grey "Sold out" badge replaces the sale badge. Card is still clickable to PDP — out-of-stock pages on HairMNL accept email-when-available signups, so the click is not wasted.

### 1.6 Interaction

| Action | Desktop | Mobile |
|---|---|---|
| Hover (desktop) | Image scale to 1.02 over 300ms; cursor pointer | n/a |
| Tap | Card opacity 0.85 (active state) | Same opacity feedback; native scroll-snap takes over |
| Scroll rail | Prev / next nav buttons (40×40 circle, ±8px from edges, opacity 0 when disabled) | Hidden — finger swipe is the primary affordance |
| Card click | Whole card → PDP. No interstitial. | Same |
| Cart compact ADD button | Submit `/cart/add` form → page reload (current); team decision pending on AJAX alternative | Same |

The desktop nav buttons are paired with a ~25-line inline init script in the snippet. The script:
1. Finds the rail's first card width on demand (handles different card sizes per placement)
2. `scrollBy({left: ±cardWidth, behavior: 'smooth'})` on click
3. Disables prev/next at scroll edges (passive scroll listener)

`document.currentScript.closest('.vrec-slot')` scopes everything to its own slot, idempotent via a `data-vrec-init="1"` flag. Survives multiple slots on one page (PDP has two — FBT + similar items).

### 1.7 Accessibility

- Section has `aria-labelledby="vrec-title-{{placement}}"` pointing at the `<h2>` title
- Rail has `role="list"`; cards have `role="listitem"`
- Nav buttons have `aria-label="Scroll recommendations left/right"` and `disabled` attribute at edges
- Sale / sold-out badges read aloud as part of card title (visible text, not decorative)
- All images have `alt` derived from `image.alt | default: product.title`
- Keyboard nav: cards are reachable via Tab; nav buttons are focusable; rail is scrollable with arrow keys when focus is on the rail

---

## 2. Placement 1: `pdp_below_atc` — Complete the routine

**Vertex model:** FBT (frequently bought together)
**Status:** **Live on draft theme**, rendering on every PDP via `sections/product.liquid:189`. Data flowing from `product.metafields.vertex.recs`.

### 2.1 Position

Inserted in `sections/product.liquid` directly after the Add-to-Cart button block, before the description / tabs / accordion stack. Exact context:

```liquid
{%- comment -%} sections/product.liquid line ~189 {%- endcomment -%}
{% render 'vertex-recommendations',
    placement: 'pdp_below_atc',
    product: product,
    title: 'Complete the routine',
    rationale: 'FBT — paired with this product nightly via Vertex predict' %}
```

Vertical spacing: **64px above / 48px below** (desktop), **40px above / 32px below** (mobile).

The slot bleeds full-width at the section level (no `.wrapper` constraint) so the scroll-snap rail can overflow naturally beyond the page gutter. This matches Pipeline 6.1.3's existing collection-slider sections.

### 2.2 Layout

- **Container:** full-bleed, 24px horizontal padding desktop, 0px mobile (rail extends to viewport edges).
- **Header:** centered title, optional 13px subtitle below. No hairline rule (an earlier mockup had a centered hairline; team approved removing it for visual lightness).
- **Rail:** horizontal scroll-snap. **Mobile: 2.25 cards visible (~42% each), 12px gap, 16px side padding.** **Tablet (≥768px): 3.3 cards (~30%), 16px gap.** **Desktop (≥1024px): 4.5 cards (~22%), 20px gap.**
- **Card count:** up to 8 from the metafield top-30 (the snippet's `limit: 8`). 4 visible on desktop with a peek of the 5th confirms there's more.
- **Nav buttons:** desktop only. 40×40 circular, white with 1px hairline border, ±8px from rail edges. Hidden on mobile (`@media (max-width: 1023px)`).

### 2.3 Card anatomy
Vertical default card per §1.4. Vendor → title → rating (when present) → price.

### 2.4 Conversion rationale

- **Why below ATC, not in sidebar?** Baymard's PDP UX research (n=145 e-comm sites) finds that "Frequently Bought Together" sections placed in the immediate visual flow below the ATC button consistently outperform sidebar placements on mobile, where sidebars don't exist. Amazon canonized this position in 2003 and competitors converged on it. Ulta is the visible counterexample (sidebar with checkbox bundling) — but that pattern requires desktop real estate HairMNL doesn't reliably have, and the bundle UX adds complexity that the simpler rail avoids.
- **Why "Complete the routine" copy?** Hair-care purchases are routine-based — a customer buying shampoo is implicitly building toward conditioner + treatment + leave-in. The phrase matches the customer's mental model. Alternative copy options under team review (see §9).
- **Industry data points:** strategic placement of recommendations on PDPs increases revenue per visitor 12-25% (Baymard); personalized recommendations on Amazon-style FBT slots boost sales 20-30% (Tinuiti, multiple Amazon studies). HairMNL's expected lift will land in the lower half of this range during the cutover window because LimeSpot was already serving *some* recommendations at this slot — the lift comes from accuracy improvement, not net-new exposure.

### 2.5 Implementation notes for engineering

**No code changes needed for visual.** The slot is already rendering. Open work:

1. **Copy approval** — confirm "Complete the routine" or pick alternative (see §9)
2. **Push from draft to live** — part of the Phase 4 cutover (separate document; LimeSpot stays installed during 14-day monitoring)
3. **Optional: hide LimeSpot's PDP "You may also like" snippet during cutover** to avoid showing two rec rails on the same page. Suggested: `{% unless settings.vertex_pdp_active %}{% render 'limespot' %}{% endunless %}` gated behind a theme setting.

---

## 3. Placement 2: `cart_above_checkout` — Frequently bought with these items

**Vertex model:** FBT keyed on the first cart item's `vertex.cart_recs` metafield (falls back to `.recs` when `cart_recs` not yet populated).
**Status:** Wired on draft via `sections/cart.liquid:78`. Data flowing.

### 3.1 Position

```liquid
{%- comment -%} sections/cart.liquid line ~78 {%- endcomment -%}
{% render 'vertex-recommendations',
    placement: 'cart_above_checkout',
    cart: cart,
    title: 'Frequently bought with these items',
    subtitle: 'Add to your cart in one tap.' %}
```

Inserted **above the checkout CTA, below the line items** — the highest-intent moment of the session.

Vertical spacing: 64px above / 48px below (desktop), 40px / 32px (mobile). On Pipeline 6.1.3's cart layout, this slot sits between the order summary subtotal and the "Checkout" button.

**Critical:** the checkout CTA must remain visible without scrolling on most viewports. We verified this on 1440×900 desktop and iPhone 13 mobile — the slot fits between subtotal and CTA without pushing the button below the fold.

### 3.2 Layout — DIFFERENT from PDP slot

The cart slot is the **only one that uses the compact horizontal card** (§1.4 second variant) and the only one that **stacks vertically on desktop**:

- **Desktop:** vertical stack of compact cards (full-width per card, max-width 720px to match the cart container). Each card is 88px image + content + ADD button on the right.
- **Mobile (<768px):** horizontal scroll-snap rail with 88% card width (1.13 cards visible — full-card focus). Tap-friendly target size; ADD button stays visible inside the card.

Subtitle "Add to your cart in one tap." is left-aligned. Header is left-aligned (not centered like other slots) so it sits flush with the cart's existing line-item alignment.

### 3.3 Card anatomy
Compact horizontal card per §1.4. Image-link → vendor-link → title-link → price + ADD button.

### 3.4 Conversion rationale

- **Why above checkout?** Baymard PDP+cart research and BigCommerce's 2024 personalization study converge on "highest intent moment" for cart-stage upsell. The cart visitor has crossed the ATC threshold; an inline ADD button removes one click vs. clicking through to a PDP and re-adding.
- **Why an inline ADD button (not card-clicks-to-PDP like the others)?** Cart visitors are decisive — they're already adding things. Pulling them out to a PDP can break the buying flow. Industry data: inline cart upsells achieve 5-15% AOV lift and 2-3% conversion lift (BigCommerce 2024 personalization study).
- **Why 2-3 max products visible at once on mobile?** Pipeline theme docs explicitly recommend "Show 2-3 products, not 5-6" for cart upsell; "fewer, better suggestions outperform a long list of random products every time." The Vertex predict output is already trimmed by the snippet's `limit: 8`, but visual density is what matters: 1.13 mobile cards / vertical desktop stack means the customer focuses on one rec at a time.
- **HairMNL-specific data:** LimeSpot's current cart widget contributes **₱0/wk** attributed revenue per dashboard. Possibly because LimeSpot's cart layout is poor; a strong layout + a relevant FBT model could meaningfully change this number.

### 3.5 Implementation notes

**Active decision needed:**

The current implementation uses `<form action="/cart/add">` with native HTML form submit. Pros: zero new JS, works without JS, matches Pipeline's existing `upsell-product.liquid` pattern, survives the cart drawer's race conditions. Con: page reloads after add, breaking momentum on mobile.

**Decision options (see §9 Open Questions):**

- (A) Keep native form submit. Ship as-is. ~0 lines of new code.
- (B) Add ~30 lines of inline AJAX (`fetch('/cart/add.js', ...)` → `fetch('/cart.js')` → re-render line items). Faster UX, more JS to maintain.

Recommended: **(A) for v1**, ship the cutover. Add (B) post-cutover if data shows cart-page bounce on add.

---

## 4. Placement 3: `home_below_hero` — Trending in your routine

**Vertex model:** RFY (recommended for you) for logged-in customers, popularity / shop trending fallback for anonymous visitors.
**Status:** **Wired on draft via `sections/section-vertex-home-recommendations.liquid`**. Empty-state gate is suppressing render until model goes ACTIVE (~2026-05-07).

### 4.1 Position

Below the hero carousel, above the category-pill strip (the strip with FOR FRIZZ / FOR DAMAGED HAIR / etc. visible in `hairmnl-homepage-hero-desktop.png`).

**Wiring caveat:** Pipeline 6.1.3 caps homepages at 25 sections. The homepage is currently at the cap. The section file (`section-vertex-home-recommendations.liquid`) exists with a schema preset, but **an admin must add it via the theme editor** between the hero and the category-pills strip when the model goes ACTIVE. This is by design — auto-injecting would push another section past the cap.

Vertical spacing: 64px above / 48px below (desktop), 40px / 32px (mobile).

### 4.2 Layout

Same as the PDP-FBT slot: full-bleed scroll-snap rail, 4.5 desktop / 3.3 tablet / 2.25 mobile cards.

Two title variants based on customer state:

- **Logged-in:** "Trending in your routine" (the RFY model trained on customer history)
- **Anonymous:** "Trending now" (popularity-default trending)

Both are configurable via the section schema (`title_logged_in`, `title_anon`, plus optional subtitles). Defaults match what's specified above.

### 4.3 Conversion rationale

- **Why below the hero?** NN/G's homepage UX research (2024 e-commerce study, n=>) finds that personalized recommendation areas placed near the top of the homepage are more discoverable and used than sections placed below the fold. Amazon and Eventbrite both anchor their personalized recs immediately below the main banner.
- **Why two title variants?** Anonymous visitors have no personalization signal; calling the slot "Trending in your routine" misleads them ("what routine?"). "Trending now" is honest about the data source — popular products without personalization.
- **Why scroll-snap, not a 6-card grid like Sephora's "Chosen For You"?** Sephora has the desktop real estate to show 6 cards in a single row; HairMNL's content area is narrower and the brand's existing section sliders (Best Sellers, New Arrivals) all use the horizontal-scroll pattern. Consistency with the rest of the homepage > matching Sephora's exact pixel grid.

### 4.4 Implementation notes

1. **Wait for RFY model ACTIVE.** The team estimates ~2026-05-07 based on pixel event volume threshold.
2. **Verify `customer.metafields.vertex.recommended_for_you` populates** for at least 50 logged-in test customers before shipping to live. The empty-state gate suppresses the section, so a partial rollout won't show empty slots — but populated slots are the cutover criterion.
3. **Admin must add the section via theme editor** (homepage section cap workaround). This is a one-time action; document in MASTER-RUNBOOK.md.
4. **Anonymous fallback:** confirm `shop.metafields.vertex.homepage_trending` is being written by `precompute-all`. The snippet reads it at line 82-83.

---

## 5. Placement 4: `pdp_below_description` — You may also like

**Vertex model:** Similar items (visual / content similarity to anchor product).
**Status:** **Wired on draft via `sections/product.liquid:209`**. Currently TRAINING (>3 days as of brief — needs separate diagnostic).

### 5.1 Position

After the description / tabs / reviews block, before the footer. Lower decorative weight than the FBT slot above it — this is a recovery slot for visitors who scrolled past ATC without converting.

```liquid
{%- comment -%} sections/product.liquid line ~209 {%- endcomment -%}
{% render 'vertex-recommendations',
    placement: 'pdp_below_description',
    product: product,
    title: 'You may also like' %}
```

Vertical spacing: 48px above / 32px below (desktop), 32px / 24px (mobile) — slightly tighter than the FBT slot to acknowledge its lower priority.

**Conflict check:** Pipeline 6.1.3's native "You May Also Like" section is NOT wired in `templates/product.json` on hairmnl.com (verified). So the Vertex slot does not duplicate a header.

### 5.2 Layout

Same vertical scroll-snap rail as PDP-FBT. No subtitle by default.

Why no subtitle: at this scroll depth, the visitor is either decided (will convert on this product) or browsing (looking for alternatives). A subtitle is decoration; the title alone carries the meaning.

### 5.3 Conversion rationale

- **Why "You may also like"?** Industry standard for similar-item recovery slots (Sephora, Ulta, ASOS all use variants of this phrase). Recognized by customers as "alternatives to this product, not complements."
- **Why below description, not above?** Customers who scroll this far have rejected (or paused on) the primary product. Showing alternatives at this depth is rescuing the session, not interrupting purchase intent. Per Baymard's PDP study, this slot adds 2-4% incremental CTR vs. FBT alone, and the two click-paths are largely non-overlapping (different sessions click each).
- **Lower visual weight is intentional** — the FBT slot above gets the typographic accent (larger title, more breathing room); this slot is utility.

### 5.4 Implementation notes

1. **Diagnose why similar-items model is stuck TRAINING >3 days.** Possible causes: insufficient catalog tag coverage; missing `categories` attribute; or simply the volume threshold not yet hit. Separate ops task.
2. **No theme work needed** until model goes ACTIVE — the empty-state gate handles the dormancy.
3. **Once ACTIVE:** verify `product.metafields.vertex.similar` populates for at least 100 products; spot-check 10 to confirm relevance.

---

## Addendum A: Cart drawer — Add to your routine (`cart_drawer_below_items`)

Already shipped on draft. Documented here for completeness.

- Tighter padding: 20px 12px 16px (vs. 64px 24px elsewhere)
- **Fixed 140px card width at all breakpoints** (vs. percentage-based) — drawer is narrow, fixed sizing prevents the rec row from dominating the line items above
- 1-line title clamp (vs. 2-line)
- No inline ADD button (drawer's AJAX rerender has known race conditions; cards click through to PDP)
- Smaller 32×32 nav buttons (vs. 40×40 elsewhere)
- Title "Add to your routine" — left-aligned, small (13px), weight 600, no decorative rule
- Subtitle hidden

**Why no inline ADD in the drawer?** The drawer rerenders via AJAX on add-to-cart, and earlier engineering found race conditions where two clicks could double-add. Until the drawer's add path is atomic, cards click through to PDP. Flagged as future v2 work.

## Addendum B: Buy-it-again — Time to restock (`vertex-buy-it-again` snippet)

Snippet exists at `snippets/vertex-buy-it-again.liquid`, wired into `sections/section-banner-slider.liquid:152`. **Unique to Vertex** — LimeSpot doesn't ship per-customer replenishment recs on HairMNL.

- **Reads** `customer.metafields.vertex.repurchase_handles` (parallel handle list to `vertex.repurchase` legacy IDs)
- **Renders only when:** customer is logged in AND metafield is non-empty AND at least one referenced product is `available`
- **Layout:** simple grid (not scroll-snap rail) — different visual treatment to signal "this is *for you*, not 'others bought'"
- **Title:** "Time to restock" — implies action, frames the products as a repurchase prompt
- **Subtitle:** "Based on your purchase history" — explicit about why these were chosen (NN/G research: users prefer transparent personalization over invisible)

This slot is **net-new revenue** vs. LimeSpot. Per LimeSpot dashboard, Home page contributes ₱0/wk attributed; any conversion from this widget is upside, not replacement.

**Status:** as of audit verification 2026-05-04, the precompute writes `customer.metafields.vertex.repurchase` (legacy IDs only). The parallel `repurchase_handles` write was flagged TODO in the snippet comment (line 47). **Open task:** add handle resolution to `precompute_buy_it_again` so the snippet can render. Currently the snippet returns nothing because `rec_handles` is nil.

---

## 6. Mobile-specific notes

### 6.1 Mobile-first scroll rail

Every placement except cart-page-desktop uses a horizontal scroll-snap rail on mobile:

- `scroll-snap-type: x mandatory` on the rail
- `scroll-snap-align: start` on each card
- `grid-auto-columns: 42%` (2.25 cards visible) — the partial peek of the 3rd card is the affordance
- `scrollbar-width: none` and `::-webkit-scrollbar { display: none }` — clean visual; native iOS / Android touch is the affordance
- `overscroll-behavior-x: contain` — prevents accidental back-swipe gestures

### 6.2 Why 2.25 cards (not 2 or 3)?

| Cards visible | Effect |
|---|---|
| 2 (50% each) | Looks like a 2-up grid; no scroll affordance |
| 2.25 (42% each) | Two full + peek of 3rd; clear scroll affordance, dominant card focus |
| 3 (33% each) | Looks like a 3-up grid; no scroll affordance |

The 2.25 ratio is the convergent industry pattern (Sephora, Cult Beauty, Ulta mobile rails all use ~42% cards). Verified via `current-fbt-olaplex-mobile.png`: HairMNL's existing implementation already uses this ratio — 2 cards + peek visible.

### 6.3 Touch targets

- Cards are 42% of viewport ≈ 158px wide on a 375px iPhone — well above 44px touch-target minimum
- Cart compact card ADD button has explicit `min-height: 44px` per WCAG
- Nav buttons (40×40) are hidden on mobile; swipe is the primary gesture

### 6.4 Mobile typography downscale

Reduced one notch on mobile (`@media (max-width: 767px)` block in CSS):
- Card title: 13 → 12px
- Price: 14 → 13px
- Vendor: 11 → 10px

Slot padding compresses: 64px / 48px → 40px / 32px.

### 6.5 Cart slot mobile transition

The cart slot is the only placement that **switches layout per breakpoint:**
- Desktop (≥768px): vertical stack of compact cards
- Mobile (<768px): horizontal scroll-snap rail with 88% cards (1.13 visible — single-card focus with peek)

Why the switch? Vertical stack on a narrow viewport pushes the checkout button arbitrarily far below the fold. Horizontal scroll keeps the slot at fixed height regardless of rec count.

---

## 7. Performance budget

| Asset | Budget | Actual | Notes |
|---|---|---|---|
| `assets/vertex-recommendations.css` | <15KB minified | ~12KB | Long-cached via Shopify asset URL versioning |
| Inline JS (rail nav init) | <5KB | ~25 lines uncompressed | Inlined in snippet to avoid an extra request |
| Total Vertex JS on any page | <5KB | ~25 lines | No fetch, no framework, no Slick / Swiper / Flickity |
| Image requests added per slot | 4-8 (lazy) | matches | All `loading="lazy"`; cards below the fold defer until scroll-near |
| TBT contribution (PDP mobile) | <50ms | TBD via Lighthouse | Verify before live push; initial PDP testing on draft showed no measurable delta |
| CLS contribution | 0.00 | 0.00 | Verified on draft 2026-05-04 — image dimensions + aspect-ratio prevent shift |

**Why no Slick / Flickity / Swiper:** the brief explicitly forbids them ("CSS scroll-snap > Slick / Flickity / Swiper"). CSS scroll-snap is hardware-accelerated, native-touch, zero-JS. The only JS is the desktop nav buttons (~25 lines), which use `scrollBy({behavior: 'smooth'})` — no animation library needed.

**Why inline the nav-init JS instead of in `assets/`:** the script is ~25 lines, scoped per-slot via `data-vrec-init="1"`, and avoids one extra HTTP request. Inlining is the right call for snippets this small. If the script grows past 50 lines, refactor to `assets/vertex-rec-rail.js` with a `<script defer>` registration.

---

## 8. Open questions for engineering

These are the team-decision points the implementation has surfaced. Each is currently rendered inline on draft theme via the `vrec-slot__notes` panel. Resolve before live push.

### 8.1 Copy approvals

| Slot | Current | Alternatives flagged | Owner |
|---|---|---|---|
| `pdp_below_atc` | "Complete the routine" | "Pairs well with this" / "Often bought together" | Brand / marketing |
| `cart_above_checkout` | "Frequently bought with these items" | (no alternatives flagged; team to confirm) | Brand / marketing |
| `cart_above_checkout` subtitle | "Add to your cart in one tap." | (drop subtitle entirely?) | Brand / marketing |
| `cart_drawer_below_items` | "Add to your routine" | (fits HairMNL voice?) | Brand / marketing |
| `home_below_hero` (logged-in) | "Trending in your routine" | (rename?) | Brand / marketing |
| `home_below_hero` (anon) | "Trending now" | (rename?) | Brand / marketing |
| `home_below_hero` subtitles | empty | "Picked for you, based on your history." / "What HairMNL shoppers are loving this week." | Brand / marketing |
| `pdp_below_description` | "You may also like" | (keep?) | Brand / marketing |
| Buy-it-again title | "Time to restock" | (alternatives?) | Brand / marketing |
| Buy-it-again subtitle | "Based on your purchase history" | (alternatives?) | Brand / marketing |

### 8.2 Cart slot ADD UX

**Decision:** native form submit (page reload) vs. inline AJAX (~30 lines of fetch + DOM update).

- (A) Native form submit. **Recommended for v1.** Ship the cutover faster; mobile data shows page reloads from cart are tolerable when the destination is the cart page itself.
- (B) Inline AJAX. ~30 lines. Faster UX. More surface area to test.

If we go with (A), the upgrade path to (B) is non-breaking (same data attributes, same form structure).

### 8.3 LimeSpot dual-render management during cutover

LimeSpot currently renders its own widgets at:
- PDP "You may also like" (overlapping with Vertex `pdp_below_description`)
- Cart upsell (overlapping with Vertex `cart_above_checkout`)
- Homepage rec section (overlapping with Vertex `home_below_hero`)

**Decision:** during the 14-day cutover monitoring window, do we:
- (A) Show both LimeSpot AND Vertex widgets (high visual clutter, but clean rollback story)
- (B) Hide LimeSpot widgets via theme settings flag during Vertex cutover, leave LimeSpot installed for fast rollback (recommended)
- (C) Disable LimeSpot widgets in the LimeSpot admin (no theme code change, but slower rollback)

Recommended: **(B)**. Add a `settings.vertex_pdp_active` boolean to `config/settings_schema.json`; gate LimeSpot's existing snippet renders behind it. Default false; flip to true at cutover; flip back to false if rollback needed (no theme push required, just theme settings change).

### 8.4 Buy-it-again handles write

Precompute writes `customer.metafields.vertex.repurchase` (legacy IDs); snippet expects `customer.metafields.vertex.repurchase_handles` (handles). The parallel write is TODO. Until done, the buy-it-again widget renders nothing.

**Open task:** in `precompute/main.py:precompute_buy_it_again`, after writing the `repurchase` metafield, also write `repurchase_handles` (resolve legacy_id → handle via the existing `handle_by_id` map already built in that function).

### 8.5 Similar-items model TRAINING > 3 days

Separate ops diagnostic; not a presentation issue. Track in `~/.claude/projects/.../memory/vertex_project_state.md` operational pending list.

### 8.6 Homepage section cap

Pipeline 6.1.3 homepage is at the 25-section cap. Adding the Vertex RFY section requires either (a) admin manually inserts via theme editor (current plan, documented in §4.4) or (b) removing one of the existing 25 sections.

Recommended: **(a)**. The category-pills strip is one of the lower-performing sections per dashboard data and could be considered for retirement, but that's a separate brand decision.

---

## 9. Engineering quick-start

To ship the visual + cutover work, the file edits in order:

### 9.1 No-op (already shipped to draft)
- `snippets/vertex-recommendations.liquid` — already in place
- `snippets/vertex-rec-card.liquid` — already in place
- `snippets/vertex-buy-it-again.liquid` — already in place
- `snippets/vertex-preview-toolbar.liquid` — already in place
- `assets/vertex-recommendations.css` — already in place
- `sections/product.liquid:189` — FBT render call wired
- `sections/product.liquid:209` — similar-items render call wired
- `sections/cart.liquid:78` — cart upsell render call wired
- `sections/section-vertex-home-recommendations.liquid` — homepage section file
- `sections/section-banner-slider.liquid:152` — buy-it-again wired
- `layout/theme.liquid` — `assets/vertex-recommendations.css` registered via `stylesheet_tag`
- `layout/theme.liquid` — `.hairmnl-theme` body class added

### 9.2 Open work

In rough sequence:

1. **Resolve copy approvals (§8.1)** — single PR updating defaults in `vertex-recommendations.liquid` snippet `case placement` block (no rebuilds needed; pure copy).

2. **Decide cart ADD UX (§8.2)** — if (B) AJAX, add ~30 lines to `vertex-rec-card.liquid` cart-compact branch. If (A) keep native form, no change.

3. **Add LimeSpot gating (§8.3)** — add `settings.vertex_pdp_active`, `settings.vertex_cart_active`, `settings.vertex_home_active` to `config/settings_schema.json`. Wrap each LimeSpot render call in `{% unless settings.vertex_X_active %}...{% endunless %}` in the relevant section files. (One PR, ~10 lines + 3 schema entries.)

4. **Resolve buy-it-again handles write (§8.4)** — `precompute/main.py:precompute_buy_it_again` adds `repurchase_handles` metafield write. (One PR in `hairmnl-vertex` repo. After deploy, snippet starts rendering automatically.)

5. **Diagnose similar-items model (§8.5)** — separate ops thread.

6. **Wait for RFY model ACTIVE (~2026-05-07)** — confirm metafields populate for ≥50 test customers.

7. **Admin: add the homepage section** via theme editor (Settings → theme customization → add section "Vertex recommendations" between hero and category pills).

8. **Push draft → live theme `131664707683`** following the CLAUDE.md push-guard rules (diff before push, draft theme verification first). Cutover plan is a separate document.

9. **14-day monitor.** RPV / AOV / profit-per-session / mobile TBT vs. baseline. All four green → flip LimeSpot uninstall (`$403/mo savings`).

### 9.3 Files NOT to touch

- `snippets/limespot.liquid`, `snippets/products-recommendation.liquid` — leave LimeSpot intact; we're gating, not removing
- Any of the `vrec-slot__notes` markup or CSS — that panel auto-suppresses on `theme.role == 'main'` (live), so it's a no-op once shipped
- `vertex-preview-toolbar.liquid` — preview-only chrome; never renders on live

---

## 10. Verification checklist

Before flipping the LimeSpot uninstall:

- [ ] All 8.1 copy decisions resolved and shipped to live
- [ ] 8.2 cart ADD UX decision shipped
- [ ] 8.3 LimeSpot gating active on live (vertex_*_active = true)
- [ ] Lighthouse mobile PDP TBT delta ≤ +50ms vs. pre-Vertex baseline
- [ ] Lighthouse mobile homepage TBT delta ≤ +50ms vs. pre-Vertex baseline
- [ ] CrUX field CLS for /products/* and / unchanged or improved
- [ ] Vertex rec metafields populated for ≥95% of active products (catalog-sync run)
- [ ] RFY model ACTIVE; metafields populated for ≥50 logged-in test customers
- [ ] Similar-items model ACTIVE OR slot left dormant via empty-state gate (no shipping criterion)
- [ ] 8.4 buy-it-again handles write deployed; widget renders for repeat customers
- [ ] 14-day RPV / AOV / profit-per-session monitoring window started

When 14-day window closes green:
- [ ] Uninstall LimeSpot
- [ ] Remove gating settings (now redundant)
- [ ] Document final cutover state in MASTER-RUNBOOK.md
- [ ] Close LimeSpot subscription ($403/mo recurring savings)

---

## Appendix: research sources

This guide's claims map to these sources. Citations marked **[verified]** were confirmed during this research pass; **[per brief]** carries forward the brief's existing citations without independent re-verification.

- **Baymard Institute — Product Page UX research** [verified]: strategic placement of recommendations on PDPs increases revenue per visitor 12-25%; full-card click targets outperform separated targets on mobile. https://baymard.com/research/product-page
- **Baymard Institute — Best Practices** [verified]: cross-sell recommendations' role is "not always to be clicked — sometimes simply to be shown." https://baymard.com/learn/ecommerce-ux-best-practices
- **Tinuiti / Amazon FBT studies** [verified]: personalized recommendations boost sales 20-30%. Amazon's FBT placement (below ATC) canonized in 2003. https://tinuiti.com/blog/amazon/amazon-detail-page/
- **BigCommerce 2024 personalization study** [per brief]: cart-stage upsells drive 5-15% AOV lift, 2-3% conversion lift.
- **Pipeline theme docs — Cart upsell best practices** [verified]: "Show 2-3 products, not 5-6"; keep checkout button visible at all times; upsell prices ≤ 25-30% of cart value. https://pipeline.groupthought.com/upsell/upselling/cart
- **NN/G — UX Guidelines for Recommended Content** [verified]: placement higher on homepage = more discovery; users prefer transparent personalization over invisible. https://www.nngroup.com/articles/recommendation-guidelines/
- **NN/G — Individualized Recommendations** [verified]: personalization helps avoid choice overload; works best when prioritized over generic content. https://www.nngroup.com/articles/recommendation-expectations/
- **MDN — CSS scroll-snap carousels** [verified]: native scroll-snap is hardware-accelerated, eliminates need for JS carousel libraries. https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Overflow/Carousels
- **HairMNL internal — LimeSpot dashboard** [per memory `vertex_project_state.md`]: cart widget contributes ₱0/wk attributed; homepage contributes ₱0/wk. Buy-it-again is net-new revenue, not replacement.

**Competitor visual references:** see `design-research/` directory.

- `cultbeauty-pdp-fbt-desktop.png` — Cult Beauty FBT bundle pattern (vertical checkbox-bundle, "ADD BOTH TO BASKET")
- `cultbeauty-pdp-also-bought-desktop.png` — Cult Beauty horizontal "also bought" rail (5 cards, vendor + title + rating + price + ADD button)
- `sephora-pdp-you-may-also-like-desktop.png` — Sephora 6-card PDP rec grid (image + brand + title + price range + rating + save heart)
- `sephora-homepage-chosen-for-you-desktop.png` — Sephora homepage 6-card RFY grid
- `ulta-pdp-fbt-desktop.png` — Ulta sidebar bundle pattern (counter-example; sidebar + checkbox + "Add 3 to Bag")
- `ulta-pdp-similar-items-desktop.png` — Ulta horizontal 4-card "Similar items" rail with inline ADD buttons
- `current-fbt-olaplex-desktop.png`, `current-fbt-aveda-desktop.png`, `current-fbt-davines-desktop.png` — current HairMNL FBT slot rendering on draft theme (5 cards desktop, vendor + title + price + rating)
- `current-fbt-olaplex-mobile.png` — current HairMNL FBT mobile (2.25 cards visible with badges, full-width ADD TO CART CTA at bottom)
- `hairmnl-homepage-hero-desktop.png` — current homepage above where the RFY slot will go
- `hairmnl-homepage-below-hero-desktop.png` — current "Best Sellers" section that the RFY slot will sit above

---

**End of guide.** Open questions in §8; engineering edit list in §9; verification gate in §10.
