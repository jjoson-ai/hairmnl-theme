# Lazysizes Callsite List
Generated: 2026-05-18 | bd: 2i8b.14

## Summary
- **Pattern 1 (lazyload + data-src): 1 callsite** — needs migration to native loading="lazy"
- **Pattern 2 (lazy-image with fade-in): 0 callsites**
- **Pattern 3 (already native loading="lazy"): ~50 callsites** — no change needed
- **Verdict: lazysizes can be fully removed** (98% complete; 1 remaining callsite + CSS/JS cleanup needed)

## Pattern 1 — Needs Migration (1 callsite)

| # | File | Line | Current Markup | Recommended Fix |
|---|------|------|---------------|-----------------|
| 1 | sections/main-bloggle-article.liquid | 364 | `<img class="bloggle--blog-item-img lazybloggle" data-src="{{ article.image \| image_url: width: 1200 }}" alt="{{ article.image.alt }}">` | Replace `class="… lazybloggle" data-src="…"` with `class="…" src="{{ article.image \| image_url: width: 1200 }}" loading="lazy" alt="{{ article.image.alt }}"` — remove `lazybloggle` class and `data-src`, add `src` + `loading="lazy"` |

## Pattern 3 — Already Native (no action needed)
~50 callsites across snippets/product-grid-item.liquid, snippets/image-fill.liquid, sections/header.liquid, sections/section-double.liquid, sections/section-map.liquid, sections/section-logos.liquid, sections/section-icons.liquid, sections/cross-post-blogs.liquid, snippets/hero.liquid, snippets/media.liquid, snippets/upsell-product.liquid, snippets/upsell-product-list.liquid, snippets/image-zoom.liquid, snippets/nav-item.liquid, snippets/tousled-nav-item-mobile.liquid, snippets/vertex-buy-it-again.liquid, snippets/vertex-rec-card.liquid, sections/section-announcement.liquid, sections/announcement.liquid, sections/thebackbar-master-header.liquid, sections/tousled-header.liquid, sections/gift-card.liquid, sections/page.liquid, sections/api-product-popdown.liquid, sections/judgeme_AllReviewsPage_Slider.liquid, and others. All use `loading="lazy"` directly on `<img>` or `<iframe>` elements. No changes required.

## CSS Rules Depending on Lazysizes Classes (needs cleanup when dropped)

### theme.css (production)

| # | File | Line(s) | Rule | Notes |
|---|------|---------|------|-------|
| 1 | assets/theme.css | 6852–6854 | `img.lazyload:not([src]) { visibility: hidden; }` | Can be removed — no `lazyload` class images remain after migration |
| 2 | assets/theme.css | 6855–6857 | `.fade-in-child .background-size-cover.lazyloaded { opacity: 1; }` | Orphaned — `.lazyloaded` is never added without lazysizes; will need alternative fade-in trigger or removal if `.fade-in-child` pattern is unused |
| 3 | assets/theme.css | 7243–7246 | `html.no-js .lazyload, html.supports-js .no-js { display: none; }` | `.lazyload` part of selector is orphaned; `html.no-js .lazyload` can be removed (the `.no-js` part is unrelated and should stay) |
| 4 | assets/theme.css | 8779–8781 | `.lazyloaded.logo__img--color { opacity: 1; }` | Logo images in header.liquid now use native `loading="lazy"` with `src` directly — `.lazyloaded` class is never applied. Consider removing or replacing with `.logo__img--color { opacity: 1; }` |
| 5 | assets/theme.css | 8799–8804 | `[data-header-transparent=true]:not(.meganav--visible) .header__logo--has-transparent .logo__img--transparent.lazyloaded { opacity: 1; transition: opacity 0.6s …; }` | Same as #4 — transparent logo never receives `.lazyloaded`. Simplify selector by dropping `.lazyloaded` |
| 6 | assets/theme.css | 10730–10732 | `.no-js .lazy-image { display: none; }` | `.lazy-image` div wrappers no longer used for new content; can be removed if no legacy content uses them |
| 7 | assets/theme.css | 11501–11522 | `.theme-animate-hover .lazy-image.has-zoom-animation …` (6 rules) | Zoom animation rules on `.lazy-image`. Can be removed if `.lazy-image` wrapper divs are no longer in use |
| 8 | assets/theme.css | 12177–12181 | `.lazy-image { display: block; position: relative; background-size: cover; }` | Orphaned — no new content uses `.lazy-image` divs |
| 9 | assets/theme.css | 12182–12189 | `.lazy-image img { display: block; position: absolute; top: 0; left: 0; width: 100%; height: auto; }` | Orphaned — same as #8 |
| 10 | assets/theme.css | 12190–12192 | `.fade-in.lazyloaded { opacity: 1; }` | Orphaned — `.lazyloaded` class never applied without lazysizes |

### theme.dev.css (source/dev)

| # | File | Line(s) | Rule | Notes |
|---|------|---------|------|-------|
| 1 | assets/theme.dev.css | 10986–10990 | `img.lazyload:not([src]) { … }` | Dev source for production rule #1 |
| 2 | assets/theme.dev.css | 10991–10993 | `.fade-in-child .background-size-cover.lazyloaded { … }` | Dev source for production rule #2 |
| 3 | assets/theme.dev.css | 11456–11458 | `html.no-js .lazyload { … }` | Dev source for production rule #3 |
| 4 | assets/theme.dev.css | 13194–13196 | `.lazyloaded.logo__img--color { … }` | Dev source for production rule #4 |
| 5 | assets/theme.dev.css | 13213–13216 | `… .logo__img--transparent.lazyloaded { … }` | Dev source for production rule #5 |
| 6 | assets/theme.dev.css | 15339–15341 | `.no-js .lazy-image { … }` | Dev source for production rule #6 |
| 7 | assets/theme.dev.css | 16200–16220 | `.theme-animate-hover .lazy-image.has-zoom-animation …` (7 rules) | Dev source for production rule #7 |
| 8 | assets/theme.dev.css | 16961–16965 | `.lazy-image { … }` | Dev source for production rule #8 |
| 9 | assets/theme.dev.css | 16967–16974 | `.lazy-image img { … }` | Dev source for production rule #9 |
| 10 | assets/theme.dev.css | 16976–16978 | `.fade-in.lazyloaded { … }` | Dev source for production rule #10 |

## JS Dependencies on Lazysizes (needs cleanup when dropped)

| # | File | Line(s) | Code | Notes |
|---|------|---------|------|-------|
| 1 | assets/theme.dev.js | 8201–8203 | `if (window.lazySizes) { window.lazySizes.autoSizer.checkElems(); }` | Guard clause (`if (window.lazySizes)`) already handles missing library gracefully — no-ops when lazysizes is absent. Safe to remove as dead code. |
| 2 | assets/theme.dev.js | 9348–9353 | `document.addEventListener('lazyloaded', function (event) { const lazyImage = event.target.parentNode; if (lazyImage.classList.contains('lazy-image')) { lazyImage.style.backgroundImage = 'none'; } });` | Event `'lazyloaded'` never fires without the library — this listener is entirely dead code. Safe to remove. |

## Load Status in theme.liquid

lazysizes.js was **removed** from `layout/theme.liquid` on 2026-04-26. The exact removal comment (lines 94–102):

```
Removed 2026-04-26 PM: lazysizes.js preload + script tag below.
All theme-side data-src/data-bgset usages migrated to native
loading="lazy" earlier today. Theme.js's lazySizes API call is
guarded (window.lazySizes && ...) so no-ops cleanly. The
"lazyloaded" event listener at theme.js:7207 is now a no-op
(event never fires) but only cleared placeholder background-
images on .lazy-image elements — cosmetic, no functional break.
```

The file `assets/lazysizes.js` (28.6 KB) exists on disk but is orphaned — not loaded on any page.

## Recommendation

1. **Migrate the single Bloggle callsite** — change `data-src` → `src`, add `loading="lazy"`, remove `lazybloggle` class (1 commit)
2. **Remove orphaned CSS rules** for `.lazyload`, `.lazyloaded`, `.lazy-image` from both `theme.dev.css` and `theme.css` (1 commit)
3. **Remove orphaned JS event listener** at theme.dev.js:9348 and dead guard clause at theme.dev.js:8201 (1 commit)
4. **Delete `/assets/lazysizes.js`** from repo (1 commit)

**Total: 4 small, safe follow-up commits.**