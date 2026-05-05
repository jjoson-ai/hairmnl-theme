# Vertex Recommendations — Placement & Layout Design Brief

> **Mission**: produce a design guide that tells engineering exactly **where** each Vertex AI recommendation slider goes on HairMNL, and **how** to lay it out for maximum conversion. Engineering will use this guide as the source of truth when wiring the remaining 3 placements (cart, homepage, PDP-similar) and refining the already-shipped PDP-FBT slot.

---

## 1. What's being built

HairMNL is a Filipino hair-care e-commerce store on Shopify. We're replacing **LimeSpot** ($403/month) with **Vertex AI Search for Commerce** as the recommendation engine. Vertex models (FBT, similar-items, buy-it-again, recommended-for-you) are nightly-precomputed into Shopify product/customer metafields and rendered storefront-side via Liquid — there's no live predict API in the storefront request path.

The recommendation **engine** is solved. The **storefront presentation** is what this design brief addresses.

---

## 2. Stack constraints (read before designing)

| Constraint | Implication |
|---|---|
| Theme: **Pipeline 6.1.3** (Shopify, NOT OS 2.0) | No section-level customization in admin UI. Section-level Liquid edits only via theme code. Auto-sync between dev & live is OFF. |
| Theme IDs: live `131664707683`, draft `140785582179` | Design must be testable on draft before live push. |
| BSS B2B Wholesaler app is installed and is a known perf bottleneck on mobile | Designs must NOT add significant JS. CSS-only carousels strongly preferred. Any JS must defer & not block critical render. |
| CLS (Cumulative Layout Shift) is an active concern | Every image needs explicit width/height. Reserve space for the slider before async content loads (skeleton OK). Lighthouse CLS regression = ship-blocker. |
| Mobile traffic is the majority. Phone screens are small (375–414px viewports common). | Mobile-first design. Touch targets ≥44px. Horizontal swipe-scroll preferred over vertical for rec carousels on mobile. |
| Current `vertex-recommendations.liquid` snippet is placeholder-quality | It works; it ships; but the visual treatment is bare-bones. The redesign should specify a polished version that replaces the existing markup. |

---

## 3. The four placements

All four are part of the LimeSpot replacement. Each gets a separate section in the design guide. Two are live or about to go live — design for them takes priority. Two are deferred — design now so future wiring is mechanical.

### 3.1 `pdp_below_atc` — "Complete the routine" — **LIVE NOW**
- **Vertex model**: frequently-bought-together (FBT)
- **Position**: product detail page, **below the Add-to-Cart button block, above the description tabs**
- **Industry data**: Baymard's PDP study (n=145 e-comm sites) reports 6–12% CTR + 3–8% AOV lift for this slot. Amazon canonized this layout in 2003.
- **HairMNL fit**: Hair-care is routine-based — shampoo + conditioner + treatment usually purchased together. Highest single-slot AOV lever.
- **Status**: Wired into `sections/product.liquid`, rendering real FBT recs from `product.metafields.vertex.recs`. **Visual polish needed.**

### 3.2 `cart_above_checkout` — "Frequently bought with these items" — **NOT YET WIRED**
- **Vertex model**: FBT keyed on cart contents
- **Position**: cart page, **above the checkout CTA, below the line items**
- **Industry data**: 5–15% AOV lift, 2–3% conversion lift (BigCommerce 2024). Visitor at peak intent.
- **Note**: HairMNL's cart currently shows ₱0/wk attributed revenue from LimeSpot's cart widget — possibly because LimeSpot's cart layout is poor. Vertex + a strong layout could meaningfully change this number.

### 3.3 `home_below_hero` — "Trending in your routine" — **NOT YET WIRED**
- **Vertex model**: recommended-for-you (RFY) for logged-in returning customers; popularity-default for first-time visitors
- **Position**: homepage, **below the hero carousel, above the featured collections**
- **Industry data**: ~4% bounce-recovery lift (LimeSpot internal benchmark)
- **Status**: model creation calendar-gated to ~2026-05-07 (pixel-event threshold). Wiring will follow once model is ACTIVE.

### 3.4 `pdp_below_description` — "Similar items" — **NOT YET WIRED**
- **Vertex model**: similar-items (recovery placement for visitors who scrolled past ATC without converting)
- **Position**: product detail page, **after the description / tabs / reviews block, before the footer**
- **Industry data**: 2–4% CTR, additive to FBT (different sessions click each)
- **Status**: model is currently TRAINING (stuck >3 days, separate diagnostic in flight). Wiring will follow.

### Slots explicitly OUT OF SCOPE for this design

- Search no-results page (low traffic)
- Order-confirmation page (attribution complexity)
- 404 / dead-end pages (low volume)
- Anywhere mid-checkout (Shopify checkout extension territory, separate effort)

---

## 4. What the design guide must produce per placement

For each of the 4 placements, produce:

### 4.1 Position spec
- Exact insertion point in the page hierarchy. **Quote the surrounding Liquid context.** E.g. "after `{% render 'product-info' %}` in `sections/product.liquid`, before `{% if section.settings.zoom_enable %}`".
- Vertical spacing above and below (px values for desktop, mobile).
- Behavior at section boundaries (does it bleed full-width? respect the `.wrapper` container?)

### 4.2 Layout spec — HOW the slider looks
This is the most important section. **Don't hand-wave with "responsive grid."** Specify:

- **Container**: full-bleed vs. wrapped; max-width; horizontal padding at each breakpoint.
- **Header**: title text, optional subtitle / "why this" tooltip, alignment, font size, weight, spacing below.
- **Card grid**:
  - Desktop (≥768px): how many cards across? Card width, gap.
  - Mobile (<768px): horizontal scroll? Snap points? How many partially visible (e.g. 2.25 cards wide signals scrollability)? Touch-scroll behavior.
  - Tablet edge cases.
- **Card anatomy** — pixel-precise:
  - Image: aspect ratio, object-fit, fallback, lazy-load behavior.
  - Title: lines clamp (1, 2?), font, size, color.
  - Price: original + sale, currency formatting, strikethrough rule.
  - Vendor / brand badge: shown? where?
  - Rating stars: shown if available?
  - "Free Gift" / "Sold Out" / "Sale" badges: position & priority order if multiple.
  - CTA: "Add to cart" inline button vs. just card-clickable? At what breakpoint does the button appear?
- **States**:
  - Loading skeleton (CLS prevention).
  - Empty state (when metafield absent — fallback behavior).
  - Out-of-stock card (greyed? hidden? badged?).
- **Interaction**:
  - Hover state (desktop): elevation, shadow, image zoom?
  - Tap state (mobile): scale-down feedback?
  - Click target: full card vs. just title vs. just CTA?

### 4.3 Conversion rationale
For every non-trivial layout choice (e.g. "show 4 cards on desktop, not 6"), cite:
- Industry research (Baymard, NN/g, BigCommerce, Shopify Plus benchmarks), OR
- Competitor evidence (Sephora, Ulta, Cult Beauty, BeautyMNL, Watsons), OR
- HairMNL-specific data (LimeSpot historical, dashboard cohorts).
**No unsourced opinions.** If you don't have a source, say so explicitly and call it a hypothesis.

### 4.4 Liquid implementation notes
For each placement, give engineering:
- The **target file** to edit (e.g. `sections/product.liquid`, `sections/cart.liquid`, `sections/section-home-hero.liquid`).
- The **render call** to add (e.g. `{% render 'vertex-recommendations', placement: 'cart_above_checkout', ... %}`).
- Any required modifications to the **shared snippet** `snippets/vertex-recommendations.liquid` (the existing snippet is placeholder-quality and will need a redesign).
- Any new CSS — should live in `assets/` as a separate file named `vertex-recommendations.css` (do NOT inline in Liquid for caching).

---

## 5. Reference materials to consult

The next session has full repo + browser access. Use them.

### 5.1 Existing code (read these first)
- `/Users/y9378348c/Projects/hairmnl-theme/snippets/vertex-recommendations.liquid` — current placeholder, contains placement docstring with original rationale
- `/Users/y9378348c/Projects/hairmnl-theme/snippets/vertex-buy-it-again.liquid` — sibling snippet for BIA, similar shape
- `/Users/y9378348c/Projects/hairmnl-theme/snippets/vertex-preview-toolbar.liquid` — preview-mode toolbar (informs the "VERTEX" badge styling currently in use)
- `/Users/y9378348c/Projects/hairmnl-theme/sections/product.liquid` — where the FBT slot is currently rendered (line ~187, `{% render 'vertex-recommendations', placement: 'pdp_below_atc', ... %}`)
- `/Users/y9378348c/Projects/hairmnl-theme/snippets/product-grid-item.liquid` — the existing collection-grid card; the rec slider cards should feel like a sibling (consistent type, density), not an alien element
- `/Users/y9378348c/Projects/hairmnl-theme/snippets/upsell-product.liquid` — existing upsell card on PDP; check for component patterns to reuse

### 5.2 Live & preview themes
- **Preview theme** (where Vertex is wired): https://creations-gdc.myshopify.com/?preview_theme_id=140785582179 — current FBT slot is rendering on every PDP. Use Chrome MCP to capture screenshots at desktop & mobile breakpoints.
- **Live theme** (LimeSpot reference): https://www.hairmnl.com — observe LimeSpot's current implementations on PDP, cart, and home. Note what works and what doesn't. The placement guide replaces these.

### 5.3 Competitor benchmarks (open with Chrome MCP and screenshot)
- **Sephora.com** — gold standard for beauty PDP recommendations. Look at "Customers also bought" placement & layout.
- **Ulta.com** — strong cart-page upsell pattern.
- **Cult Beauty (cultbeauty.co.uk)** — strong "complete the look" PDP slot.
- **BeautyMNL.com** — direct local competitor; how do they structure recs?
- **Watsons.com.ph** — local pharmacy/beauty; benchmark for PH-market expectations.

### 5.4 Research sources (use WebSearch + WebFetch)
- **Baymard Institute** — PDP & cart UX research (most authoritative source for e-comm conversion specifics).
- **Nielsen Norman Group (nngroup.com)** — recommendation widget patterns.
- **BigCommerce 2024 personalization study** (cited in current snippet).
- **Shopify Plus design patterns blog** — platform-native conventions.

---

## 6. Hard constraints / anti-goals

- **Do NOT redesign the entire PDP, cart, or homepage.** Scope is the rec sliders only.
- **Do NOT propose components that require ripping out Pipeline 6.1.3 sections.** Drop-in replaceable Liquid + CSS only.
- **Do NOT propose anything that adds >5KB of JS.** Mobile perf is critical. CSS scroll-snap > Slick / Flickity / Swiper for the carousels.
- **Do NOT propose third-party JS dependencies.** Self-contained CSS + minimal vanilla JS only.
- **Do NOT depend on Shopify Liquid features that don't exist in Pipeline 6.1.3** (e.g. no `section.settings` if the section doesn't already define them — call out any new settings needed).
- **Do NOT introduce dark patterns** (countdown timers, fake scarcity, etc). HairMNL is a premium brand; rec sliders should feel curated, not pushy.

---

## 7. Deliverable format

Write a single markdown file: `vertex-placement-guide.md` in the same directory as this brief. Structure:

```
# Vertex Placement & Layout Guide
## Executive summary (1 paragraph)
## Universal design system
   ### Typography
   ### Color & badges
   ### Card component (shared across all 4 placements)
   ### Loading & empty states
## Placement 1: pdp_below_atc (FBT)
   ### Position
   ### Layout
   ### Rationale
   ### Implementation
## Placement 2: cart_above_checkout (FBT)
   (same subsections)
## Placement 3: home_below_hero (RFY)
   (same subsections)
## Placement 4: pdp_below_description (Similar items)
   (same subsections)
## Mobile-specific notes
## Performance budget
## Open questions for engineering
```

Include screenshots of:
- Current preview-theme FBT slot (before)
- 2–3 competitor reference points per placement
- Optional: ASCII / mermaid wireframes if helpful

Save screenshots under `/Users/y9378348c/Projects/hairmnl-theme/design-research/` (create if missing) with descriptive filenames.

---

## 8. Verification & handoff

When the guide is done:

1. Open the current FBT slot on the preview theme (3 PDPs minimum) and **annotate where the redesign would change vs. the current placeholder**. This makes the engineering diff obvious.
2. Spot-check the guide against the brief — every placement listed in §3 should have all four sections (position, layout, rationale, implementation) in §4.
3. Output a short "Engineering quick-start" section at the end: a numbered list of file edits engineering would make to ship the new design, in order.

---

## 9. Project background (for context only — don't redo this work)

- HairMNL is migrating from LimeSpot to Vertex AI Search for Commerce.
- Phase 1b-α (Buy-it-again precompute) deployed 2026-05-01.
- Phase 1b-γ.2 (FBT precompute) deployed 2026-05-02 — 2,642 products now have `vertex.recs` metafield populated.
- Phase 1b-γ.3 (PDP wiring) deployed 2026-05-02 — `vertex-recommendations` snippet rendering on every PDP via `sections/product.liquid`.
- Phase 1b-γ.6 (exclude-list audit) is in flight separately — don't worry about which products are excluded; assume the data layer handles that. Focus on the visual layer only.
- Phase 1b-γ.8 (push FBT to live) is gated on this design guide for the visual polish before final deployment.

---

## 10. Recommended model & effort for this work

**Opus 4.7 / Extra high.** Reasons:
- Cross-functional judgment: balancing UX research, perf budget, mobile-first constraints, brand premium-ness, and Liquid implementation realities simultaneously.
- Visual judgment: assessing competitor layouts and translating to specs.
- Research synthesis: pulling Baymard / NN/g / Shopify Plus into actionable specs, not just citations.

If you hit a budget ceiling: Sonnet 4.6 / High can produce a competent guide but will likely need 1 review pass with you.

---

**End of brief. Begin the design guide.**
