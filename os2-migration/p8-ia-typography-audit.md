# P8 Information Architecture + Typography Audit

**Date:** 2026-05-21
**Author:** Claude Code (Opus 4.7 / High)
**Theme:** Pipeline 8.1.1 dev `141168312419` ("Pipeline 8 Working Demo") + HairMNL customizations
**Scope:** Header, footer, PDP, collection grid, cart page, cart drawer, article page, search page, product card snippet, theme.css + custom-theme.css, theme settings schema.
**Not audited:** Home page section blocks (24 individual hero / slider / image-text sections — separate audit), 30 brand-collection JSON templates, blog list, account pages, checkout (vendor-controlled), every CSS rule in 18K combined lines.
**Status:** Findings only. No code changes made.

---

## TL;DR

Pipeline 8's typography **foundation is solid** — a clean fluid modular scale, three named font stacks (heading / accent / body), CSS-variable-driven so theme editor settings flow through cleanly. The issues are not in the foundation; they're in **how HairMNL's content is mapped onto that foundation.**

Top three concerns, in priority order:

1. **Collection pages have zero heading hierarchy.** No `<h1>` for the collection name, product card titles are `<p>` not `<h2>`/`<h3>`. SEO crawlers and screen readers see a flat, structureless page on the highest-revenue route shape (best-sellers, brand collections, search-result-like routes).
2. **Body text is too small.** 13.14px on mobile, 14.53px on desktop — both below the 16px modern standard. HairMNL has not overridden Pipeline 8's default. Reads as cramped; raises accessibility risk on long-form (article, product description).
3. **PDP product title is undersized.** HairMNL custom override makes the `<h1>` render at ~17px (`custom-theme.css:686-693`), about the size of a body subheading. Loses visual hierarchy and the semantic-visual coupling needed for natural reading.

Each is concrete, file-and-line cited, and individually small to fix. Together they account for most of the readability + SEO ceiling on the current theme.

---

## What's already good

Worth noting before the criticism — Pipeline 8 + HairMNL's customizations get a lot right:

- **Modular fluid typographic scale** (`theme.css:4561-4592` plus per-heading rules). h1 35.5px → 47.9px, h2 30.1px → 39.3px, etc. Calc-based fluid scaling between 480px and 1400px breakpoints. Heads will look right at every viewport.
- **Three named font stacks** (`---font-stack-heading`, `---font-stack-accent`, `---font-stack-body`) driven by CSS variables, set by Liquid from theme settings. Future font swaps are one-setting changes, not code rewrites.
- **`.h1--body` family** lets designers use heading sizes with body font when desired — clean separation of size and font-family.
- **Consistent line-height tokens.** All headings 1.25, body 1.6. Not every component sets its own.
- **Accent uppercase utility** (`.uppercase`, `theme.css:4549-4560`) has letter-spacing 1px baked in — small CSS contract that makes uppercase always look right, never tracked at default 0.
- **Semantic landmarks present.** `<header role="banner">`, `<footer role="contentinfo">`, `<nav role="navigation" aria-label="breadcrumbs">` on PDP (`product.liquid:36`), proper `<nav aria-label="main_menu">` on mobile drawer (`header.liquid:228`).
- **Icon accessibility.** Every icon-only button paired with `<span class="visually-hidden">` for label text. Visible across header (`header.liquid:132,138,164,181,195,250`), footer (`footer.liquid:155,169`).
- **Form label association.** `<label for="…">` ↔ `<input id="…">` pairs throughout cart and footer forms. Visually hidden labels used where chrome doesn't permit visible (`cart-drawer.liquid:190`).
- **Translation-first CTAs.** `{{ 'cart.general.checkout' | t }}` etc. — no hardcoded English. Localisation-ready.

If we change nothing else, the theme is **already at par for accessibility chrome**. The problems are at the content/section level, where Pipeline 8 leaves choices to the merchant and HairMNL hasn't made them.

---

## Critical findings

### 1. Collection pages — no h1, no h2, no semantic outline

**Evidence:**
- `sections/collection.liquid:1-302` — searched end to end. Zero `<h1>` for the collection name. The page heading "Best Sellers" / "Davines" / etc. is rendered by a **separate hero section** (`sections/hero.liquid`, configured per template via `templates/collection.json`). The hero section is optional — collections without a hero have no page title at all.
- `snippets/product-grid-item.liquid:278` — every product card across the entire site renders its title as:
  ```liquid
  <p class="product__grid__title">…</p>
  ```
  Not an `<h2>`. Not an `<h3>`. A plain paragraph.
- Filter sidebar label is `<p class="cart__drawer__title">{{ 'collections.sidebar.filter' | t }}</p>` (`collections.liquid:60`).
- Search results: `sections/search.liquid:152` — product titles are `<p class="h6--body product__inline__title">`. Same pattern, h6 *styling* (smallest heading), no actual heading tag.

**Impact:**
- **SEO:** Google scans heading structure to understand content hierarchy. A collection page with no h1/h2/h3 reads as a structureless list to the crawler. Brand collection pages (Davines, Kérastase, L'Oréal — high-intent commercial keywords) lose ranking signal.
- **Accessibility:** Screen-reader users navigate by heading level (VoiceOver: VO+H, NVDA: H). Heading-jumping is the second-most-common SR navigation strategy after links. A flat page provides zero way-finding.
- **Skim-readability for sighted users.** Product cards are visually distinct (image + price), but the title is typographically downgraded by being a `<p>` with default p styling (13.14-14.53px) instead of a card-headline weight.

**Recommendation:**
- Add `<h1>` for the collection name. Either in `sections/collection.liquid` directly (if hero is missing/disabled), or as the title element inside `sections/hero.liquid` when the hero is the page's intro.
- Promote `product-grid-item.liquid:278` from `<p>` to `<h2>` (when card is on collection/search) or `<h3>` (when nested under a section h2 like "Best Sellers"). Pass the heading level as a snippet parameter so the snippet knows context — e.g. `{% render 'product-grid-item', product: product, heading_level: 'h2' %}`. Default to `<h2>` if none passed.
- Keep visual styling identical — only the element name changes. The `.product__grid__title` class drives the look.

### 2. Body text is undersized

**Evidence:**
- `theme.css:4519-4546` — body `font-size` calc resolves to ~13.14px at mobile breakpoint, ~14.53px at desktop ≥1400px. This is Pipeline 8 stock; HairMNL hasn't overridden it.
- The W3C-recommended baseline for body text is **16px**. Apple HIG: 17pt. Material Design: 14sp body, 16sp body-large. Most modern e-commerce themes default to 16px.

**Impact:**
- Long-form text (article, product description, FAQs in the footer accordions) reads as small + cramped, especially on mobile.
- WCAG 2.1 doesn't mandate a specific size, but **WCAG SC 1.4.4** requires text to be resizable to 200% without loss of functionality — small base sizes amplify the cost of zoom-out users.
- The 13.14px mobile size is below most accessibility audit "comfortable" thresholds.

**Recommendation:**
- Bump the body base from ~14.53px → 16px desktop, with a fluid `clamp(15px, 1vw + 12px, 17px)` curve for responsive. Mobile bumps to ~15px, desktop ~17px.
- This is a single CSS-variable change in theme-editor settings (`type_base_font` size picker is 75-125% — current default is 100%, recommend ~110% to land at 16px). Try it via the theme editor first — no code change required if the picker delivers.
- Visually verify: the body bump cascades to button labels, form inputs, cart line item meta, footer accordion body, blog excerpts. Re-check those don't break wrapping.

### 3. PDP product title is undersized

**Evidence:**
- `snippets/product-title-price.liquid:12`: `<h1 class="product__title">{{ product.title }}</h1>` — correct semantic.
- `custom-theme.css:686-693`: HairMNL's override:
  ```css
  .product__title__wrapper .product__title {
    font-size: 17.14px;
    font-family: var(---font-stack-product-heading);
    font-weight: var(---font-weight-product-heading);
  }
  ```
- That 17.14px is roughly the size of a body subheading. Pipeline's stock h1 would be 35-48px. HairMNL has knocked it down to ~36% of the default.

**Impact:**
- The PDP h1 should be **the most visually prominent text on the page** — it's the page's reason for existing, the SEO title element, the screen-reader landmark. At 17px it's smaller than the section sub-headings around it ("Description", "Reviews"). Visual hierarchy is inverted.
- Hurts the brand: a luxury beauty retailer's product page typically presents the product name as a confident, generous typographic statement. 17px reads as utility text.

**Recommendation:**
- Bump `.product__title__wrapper .product__title` to a size in the 24-32px range. Keep HairMNL's product-heading font stack — just larger.
- If the small size was deliberate (e.g. to fit a specific layout box on a particular product), revisit that constraint: either size the box bigger or wrap the title at 2 lines. Don't downsize the headline.
- This is one CSS rule change. ~1 line of work.

---

## Medium findings

### 4. PDP has no h2 section headings

`sections/product.liquid` renders the product description, tabs, sharing, pickup, and upsell sections as `<div>` blocks with no h2 headings (description block at line 135, tabs at line 159, subheading at line 172 uses `<div class="product__subheading">`).

After the h1 product title, the next semantic heading on the page is... nothing, until the Vertex AI rec rail's `<h2 class="vrec-slot__title">` or the Judge.me reviews widget heading. Screen-reader users can't outline the page.

**Recommendation:** Wrap each named PDP section in a real `<h2>`:
- Description: `<h2>Description</h2>` (visible OR `<h2 class="visually-hidden">`)
- Tabs: each tab title in `<h2>` (the tablist labels Pipeline renders are already buttons — consider `<h2>` wrappers OR `aria-labelledby` pointing at the tab button text)
- Sharing: `<h2 class="visually-hidden">Share</h2>` if you don't want visible
- Pickup: `<h2>Store availability</h2>` or visually-hidden

The "visually-hidden" pattern keeps current design and adds SEO + a11y outline.

### 5. Article page h1 carries h3 styling

`sections/article.liquid:50`:
```liquid
<h1 class="h3 blog__article-title …">{{ article.title }}</h1>
```

The semantic tag is `<h1>` (correct) but the visual class `.h3` overrides it to h3 size. This is **technically valid HTML** (size and tag are independent), but it creates a visual-semantic mismatch:
- The blog article's most important content is the article title.
- Visually it renders at h3 size (25-32px), smaller than h1 (35-48px) and h2 (30-39px).
- A skim-reader scrolling the article won't see the title with the prominence its role demands.

**Recommendation:** Drop the `.h3` class. Let the `<h1>` carry default h1 sizing. If layout was constraining width, fix that constraint, not the heading size.

### 6. Footer accordions have hardcoded `aria-expanded="true"`

`footer.liquid:37-41` (and lines 56, 69, 84, 97 — 5 accordion sections):
```liquid
<button type="button"
        aria-controls="…"
        aria-haspopup="true"
        aria-expanded="true">
```

That `aria-expanded="true"` is a **static Liquid string** — never updated by JS when the accordion toggles. Assistive tech will always report "expanded" even after a user collapses it. This is the same accordion-state pattern that Pipeline 8 ships with by default — likely fine on first load (accordion DOES start expanded on desktop) but breaks the moment a user interacts.

**Recommendation:** Either
- (a) Audit the JS that toggles the accordion (likely in `assets/theme.js`) and confirm it updates `aria-expanded`. If yes, change the Liquid attribute from a hardcoded `"true"` to read initial state from a `block.settings.expanded` or equivalent. If no JS handler exists, add one. This is bug-level work, not a sweeping refactor.
- (b) If accordions actually never collapse (desktop-only, mobile shows full), just remove the `aria-expanded` attribute entirely — incorrect ARIA is worse than absent ARIA.

### 7. Cart page heading is h3, not h1/h2

`sections/cart.liquid:31`: `<h3 class="h3--body">{{ 'cart.general.title' | t }}</h3>` (≈ "Your Cart").

There's no h1 or h2 above this h3 on the cart route. Cart is a top-level page with its own URL (`/cart`) and its own title role. The h3 should be h1 (or h2 if the page wraps it in some chrome heading).

**Recommendation:** Promote to `<h1 class="h2--body">` (h1 tag, h2 visual size if the current 27-32px is the right look). Single attribute change.

### 8. Cart drawer uses `<p>` for the drawer title

`cart-drawer.liquid:27`: `<p class="cart__drawer__title">…</p>`

The drawer is an overlay; semantically it deserves a heading (typically `<h2>` within an overlay landmark / dialog). Screen-reader users opening the drawer hear "dialog" or "region" but not an introductory heading announcing what the drawer is for.

**Recommendation:** Change to `<h2 class="cart__drawer__title">`. Add `role="dialog"` and `aria-labelledby` pointing at the h2 if not already present on the drawer container (worth a follow-up scan).

---

## Minor findings

### 9. Font-size token sprawl in custom-theme.css

`custom-theme.css` defines **multiple ~17.14px overrides** for unrelated content: product title (line 686), section headers (line 670), blog/article titles (line 727). These are functionally the same size but written as three separate rules. If the design system intent is "all secondary headings sit at this size", introduce a custom property (e.g. `--text-heading-secondary: 17.14px`) and reference it. Future size changes become one edit.

### 10. Heading utility class naming is verbose

The `.h1--body` pattern is fine — it's a clear modifier. But there's also `.h1`, `.h2--display` (if it exists), `.product__title`, `.vrec-slot__title`, `.blog__article-title`, `.cart__drawer__title`, `.product__grid__title`, `.product__inline__title`, `.spr-header-title`, `.related_articles_header h5`. The system mixes BEM (`block__element`), classes-as-utility (`.h1--body`), and ad-hoc names (`.related_articles_header`).

This isn't a bug — it's an architectural inconsistency that makes the design system harder to extend. **Recommendation:** post-cutover, do a class-naming-convention sweep on heading classes. Pick one (probably BEM matching Pipeline 8 stock) and migrate stragglers. Not P8-cutover-blocking.

### 11. `.uppercase` accent font is used as both styling and semantic emphasis

Footer accordion titles (`footer.liquid:37` etc.) are `<button class="uppercase footer__title">`. The accent font + uppercase is sometimes a heading-replacement (footer "Information", "Customer Care", etc.) and sometimes decorative ("Newsletter signup", small labels). Same visual treatment, different semantic role.

**Recommendation:** If footer section titles are content navigation (which they are), promote them to `<h2 class="footer__title">` inside the `<footer>` landmark. The accordion-button can be nested *inside* the h2, or the h2 can become the accordion trigger directly with `aria-expanded` on the h2's child button. Currently the h2-equivalent has no heading semantics at all.

### 12. Generic product card alt text

`product-grid-item.liquid:195,231` — alt text falls back to `product.title | replace: 'HairMNL ', '' | …`. This is functional but generic. Image search SEO benefits from richer alt text (e.g. "Davines OI Oil 135ml — frizz-control hair oil") rather than just the product title. The product title is what the alt resolves to for ~all products since `featured_media.alt` is rarely set in Shopify Admin.

**Recommendation:** Either (a) operator backfills `featured_media.alt` with richer descriptions on top-traffic products, OR (b) snippet appends `product.vendor` and `product.product_type` to the fallback alt (small Liquid change). The latter is cheaper but vendor + product_type concatenation can be awkward — try on a few products first.

---

## Recommendations — grouped by impact

### High impact (most readability + SEO win per hour)
1. **Add h1 to collection pages** (#1) — single edit in `sections/collection.liquid` or `sections/hero.liquid`. Highest SEO and a11y ROI.
2. **Promote product card titles from `<p>` to `<h2>`/`<h3>`** (#1) — single edit in `snippets/product-grid-item.liquid:278`. Cascades to every collection / search / homepage product rail.
3. **Bump body text to 16px** (#2) — try via theme-editor settings first (no code change). If picker doesn't reach, one CSS variable edit.
4. **Resize PDP product title** (#3) — one CSS rule in `custom-theme.css`.

Each is <30 minutes of work. Combined: ~1.5 hours for the high-impact set.

### Medium impact (a11y / SEO completeness)
5. **Add h2 wrappers to PDP description / tabs / pickup / sharing** (#4) — modest Liquid edits in `sections/product.liquid`. Use `visually-hidden` to preserve current visual design.
6. **Fix article page h1 styling** (#5) — drop `.h3` class on the h1 in `sections/article.liquid:50`.
7. **Promote cart page h3 → h1** (#7) — one attribute change in `sections/cart.liquid:31`.
8. **Cart drawer `<p>` → `<h2>`** (#8) — one attribute change in `snippets/cart-drawer.liquid:27`.
9. **Footer accordion ARIA state** (#6) — investigate JS; either fix the state-update or remove the misleading attribute.

### Low impact (design-system polish)
10. **Footer "section title" semantics** (#11) — promote `<button>` titles to `<h2>` inside the buttons or restructure as h2 + button-trigger pattern.
11. **17.14px token consolidation** (#9) — introduce `--text-heading-secondary` custom property in custom-theme.css.
12. **Heading class naming convention** (#10) — post-cutover sweep.
13. **Richer product card alt text** (#12) — operator backfill OR snippet enhancement.

### Worth doing as a follow-up audit
- Home page section blocks (24 sections in `templates/index.json`) — each section type (hero, slider, image-with-text, etc.) has its own heading logic. Sample several before generalising.
- Brand-collection JSON templates (30 templates referenced as `templates/collection.<brand>.json`) — likely all use the same `sections/hero.liquid` + `sections/collection.liquid` pattern, but worth confirming.
- Color contrast pass — the `color_body_text` default `#656565` on white (`#FFFFFF`) is **4.61:1**, just over WCAG AA 4.5:1. Margins are thin; if any backgrounds aren't pure white, contrast could drop below AA. Worth a dedicated WebAIM contrast pass on every text/background pairing in the rendered theme.
- Skip-link / focus-ring audit — `<a class="in-page-link visually-hidden skip-link" href="#MainContent">` exists in `theme.liquid:1271`, but its focus styling and target hit-state should be tested with keyboard.

---

## How to use this audit

- **Pre-cutover:** worth doing #1, #2, #3, #5, #7, #8 before going live. They're small (<3 hours combined) and they're the highest user-visible + SEO impact items.
- **Post-cutover:** the medium and low items become regular polish tickets.
- **Don't bundle:** each of these is a single-concern small PR. Bundling makes a regression-bisect harder.
- **One thing this audit doesn't tell you:** how the live customer reads the typography. The 16px-body recommendation is industry standard, but HairMNL's existing customer base may be acclimatised to the smaller text. If you want certainty: A/B test the body bump for a week, measure scroll-depth + time-on-page + conversion.
