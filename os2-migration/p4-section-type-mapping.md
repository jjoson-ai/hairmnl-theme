# Pipeline 6 → Pipeline 8 section-type mapping

> **Purpose:** translation table for the Path B automation dispatch. When OC's senior-developer generates Pipeline 8 JSON templates from Pipeline 6 settings, it maps P6 section types to P8 stock equivalents using this table. Judgment calls live here; OC follows the table mechanically.
> **Date:** 2026-05-17

---

## How to use

For each P6 section instance in `config/settings_data.json`'s `current.sections`:

1. Look up its `type` in the table below.
2. If a P8 equivalent exists → emit it in the new `templates/<scope>.json` with the equivalent P8 type + best-effort setting key translation.
3. If marked "drop" → don't emit; the section is going away with the migration.
4. If marked "rebuild" → leave a TODO comment in the JSON template noting the section was P6-specific and needs Phase 5 manual reconfiguration.

P8 stock section files are at `/tmp/p8-pull/sections/` (pulled from theme `141168312419` during P1.3). Reference the source files for accurate setting key names.

---

## Mapping table

### Layout / chrome sections

| P6 type | P8 equivalent | Action | Notes |
|---|---|---|---|
| `header` | `header` (rendered via `sections/group-header.json`) | **Group-render** | P8 uses OS 2.0 v2 section groups. Output goes to `sections/group-header.json`, not a per-template reference. Keep menu handle + logo settings; drop P6-only fields like `hide_header_at_top`. |
| `footer` | `footer` (rendered via `sections/group-footer.json`) | **Group-render** | Output to `sections/group-footer.json`. Preserve column menu handles, payment-icon visibility flag, social-link blocks. |
| `announcement` | `section-announcement` OR keep `announcement` | **Map** | P8 has both `announcement` (simple bar) and `section-announcement` (richer). Prefer `announcement` for direct P6 parity. Preserve `text`, `link`, `text_color`, `bg_color` settings. |
| `popups` | `popups` | **Map directly** | P8 has its own `popups` section. Most apps inject popups via TAE anyway. |
| `thebackbar-master-header` | (no P8 equivalent) | **Drop + flag** | P6 custom alternate header for The Back Bar pages. Phase 5 reconfiguration: use `sections/group-header.json` with conditional logic OR a separate `templates/page.thebackbar.json` if needed. |

### Brand-collection sections (26 P6 types)

All of these map to the **single P8 `brand-collection` section** we built in M4. The 30 `templates/collection.<handle>.json` files (already on main) handle this — no JSON template generation needed for these.

| P6 type | Maps to | Notes |
|---|---|---|
| `collection-branded` | `brand-collection` | Base — already covered by `templates/collection.branded.json` |
| `collection-branded-subcollection` | `brand-collection` | Covered by `templates/collection.branded-subcollection.json` |
| `collection-absolutrepair` | `brand-collection` | Covered by `templates/collection.absolutrepair.json` |
| `collection-blondabsolu` | `brand-collection` | Covered by `templates/collection.blondabsolu.json` |
| `collection-chronologiste` | `brand-collection` | Covered |
| `collection-densifique` | `brand-collection` | Covered |
| `collection-discipline` | `brand-collection` | Covered |
| `collection-elixir` | `brand-collection` | Covered |
| `collection-krchromaabsolu` | `brand-collection` | Covered |
| `collection-krcurlmanifesto` | `brand-collection` | Covered |
| `collection-krgenesis` | `brand-collection` | Covered |
| `collection-krspecifique-divalent` | `brand-collection` | Covered |
| `collection-krsymbiose` | `brand-collection` | Covered |
| `collection-lorealprofessionnel` | `brand-collection` | Covered |
| `collection-lp-inforcer` | `brand-collection` | Covered |
| `collection-lp-liss` | `brand-collection` | Covered |
| `collection-lp-metaldetox` | `brand-collection` | Covered |
| `collection-lp-mythicoil` | `brand-collection` | Covered |
| `collection-lp-scalpadvanced` | `brand-collection` | Covered |
| `collection-lp-silver` | `brand-collection` | Covered |
| `collection-lp-vitamino` | `brand-collection` | Covered |
| `collection-nutritive` | `brand-collection` | Covered |
| `collection-resistance` | `brand-collection` | Covered |
| `collection-specifique` | `brand-collection` | Covered |

**Action for Path B:** For the 5 "minimal templates" (lp-styling, lp-prolonger, lp-instantclear, lp-antidandruff, lp-serioxyl) that M4 left without block defaults, **read the corresponding P6 `sections/collection-<handle>.liquid` file** (or look at the section's settings in `config/settings_data.json`) and extract: brand_name, brand_primary_color, brand_logo, brand_hero_image, brand_description_html. Inject those into the existing minimal JSON templates.

### Homepage content sections (most need new mapping)

P6's homepage uses these section types. Map each to a P8 equivalent. Settings keys won't all match — best-effort translation; what doesn't fit gets dropped with a comment.

| P6 type | P8 equivalent | Action | Mapping notes |
|---|---|---|---|
| `collection-row` | `section-collection-tabs` OR `section-collection` | **Map** | P6 collection-row shows a featured collection + product grid. P8's `section-collection-tabs` is a tab-switcher; `section-collection` is a single rail. Choose based on `collection_count` setting in P6: 1 collection → `section-collection`; 2+ collections → `section-collection-tabs`. |
| `image-with-text` / `section-custom-content` | `section-custom-content` | **Map directly** | P8's `section-custom-content` is the most flexible match. Carry image + heading + body + button settings. |
| `slideshow` / `banner-slider` | `section-hero` (single slide) OR `section-gallery` (multi-slide) | **Map** | P8 doesn't have a direct multi-slide hero; `section-gallery` is the closest. Single slides become `section-hero`. |
| `featured-product` | `section-product` | **Map** | Both render a single product. Preserve `product` handle setting. |
| `featured-collection-list` / `collection-list` | `section-list-collections` | **Map** | Lists multiple collections with images. P8 stock supports this. |
| `richtext` | `section-richtext` (if exists) OR `section-custom-content` | **Map** | Simple text section. |
| `video` | `section-video` | **Map** | Both have featured-video sections. |
| `logos` / `featured-logos` | `section-logos` | **Map directly** | Brand logo bar. P8 ships this stock. |
| `accordion` / `faq` | `section-accordion` | **Map directly** | P8 stock accordion section. |
| `gallery` / `image-gallery` | `section-gallery` | **Map directly** | |
| `map` | `section-map` | **Map directly** | |
| `contact-form` / `contact` | `section-contact` | **Map directly** | |
| `newsletter` / `signup` | (none — handled by Klaviyo TAE) | **Drop** | Klaviyo's app embed handles popup signup; no theme section needed. |
| `instagram` / `social-feed` | (no P8 equivalent) | **Drop + flag** | Was P6-specific. Phase 5: install a TAE-based social-feed app OR replace with `section-gallery`. |

### Product page sections

| P6 type | P8 equivalent | Action |
|---|---|---|
| `product` (PDP main) | `product` | **Map directly** |
| `product-recommendations` | `related` (P8 stock related-products) OR our custom `vertex-recommendations` | **Map** — prefer `vertex-recommendations` with `placement: pdp_below_atc` since we built it in M9 |
| `product-tabs` | (no P8 equivalent) | **Drop** — our `assets/hairmnl-custom.js` handles tab behavior; section is replaced by inline block in product page |
| `product-reviews` (Judge.me) | (handled by Judge.me TAE) | **Drop + flag** | Judge.me TAE app embed handles widget placement |

### Cart page sections

| P6 type | P8 equivalent | Action |
|---|---|---|
| `cart` | `cart` (P8 stock) | **Map directly** |
| `cart-recommendations` | `vertex-recommendations` with `placement: cart_above_checkout` | **Map** |
| `freegifts` / BOGOS gift area | (handled by BOGOS TAE) | **Drop** — BOGOS app embed renders in its own slot |

### Blog / article sections

| P6 type | P8 equivalent | Action |
|---|---|---|
| `blog` | `blog` (P8 stock) | **Map directly** |
| `article` | `article` (P8 stock) | **Map directly** |
| `related-articles` / `cross-post-blogs` | (no P8 stock equivalent) | **Drop + flag** | Pro Blogger app may inject equivalent; pending bd 01vl (Pro Blogger replacement). |

### Customer account sections

| P6 type | P8 equivalent | Action |
|---|---|---|
| `customer-account` | `customer-account` | **Map directly** |
| `customer-login` | `customer-login` | **Map directly** |
| `customer-register` | `customer-register` | **Map directly** (also see `templates/customers/register.liquid` for the Backbar-specific register reorder JS — that lives in `hairmnl-custom.js`) |
| `customer-addresses` | `customer-addresses` | **Map directly** |
| `customer-order` | `customer-order` | **Map directly** |

### Sections to drop entirely

| P6 type | Why drop |
|---|---|
| `bss-b2b-wholesaler-form-1959` | BSS B2B uninstalled in M6 |
| `judgeme_AllReviewsPage_Slider` | Judge.me TAE handles all-reviews page |
| `judgeme_allReviewsPage` | Same — Judge.me TAE |

---

## Setting key translation conventions

For P6 → P8 setting keys within sections, P8 generally uses the same names with these patterns:
- `text` / `title` / `subtitle` — same
- Image fields — same (image_picker source URL works across versions)
- Color picker fields — same
- Boolean toggles — same
- Color tokens like `bg_color`, `text_color`, `accent_color` — same
- Per-block settings — P8 uses block-with-`type`+`settings` structure; verify each block type exists on the target P8 section's `{% schema %}` blocks list

When in doubt: emit the P6 settings as-is and let Shopify silently drop unrecognized keys. The push will succeed even with extra keys; they just don't render.

---

## Confidence

This mapping is **best-effort guidance**, not a contract. Phase 5 visual QA will surface mismatches. Most likely mismatches:
- Setting key renames (e.g., P6 `featured_collection_1` → P8 `collection_1`)
- Block type names within sections
- Required vs optional settings (P8 may require defaults P6 didn't)

Resolve mismatches by:
1. Reading the P8 stock section's `{% schema %}` block in `/tmp/p8-pull/sections/<section>.liquid`
2. Renaming the setting key in the generated JSON
3. Re-pushing
