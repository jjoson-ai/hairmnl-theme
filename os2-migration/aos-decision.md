# AOS gate/replace/remove decision — bd ujg6.8

> **Bd:** `hairmnl-theme-ujg6.8`
> **Date:** 2026-05-18 PM, on Opus 4.7 / Medium.
> **Decision required:** gate AOS, replace with native equivalent, or remove entirely.

## TL;DR

**Recommendation: KEEP AOS as-is (option D — defer, won't-fix-without-more-evidence).**

The current data does not justify changing AOS. Post-fix measurements show:
- AOS is NOT in top-5 CLS attribution on any template I've measured
- Total AOS cost is bounded: 38 KB async-loaded CSS + gated JS init
- 61 callsites would need migration to replace or remove cleanly

Closing the ticket as "WONT FIX — pragmatic; revisit if AOS surfaces as a perf cost in CrUX field data post-cutover."

---

## Inventory

### Callsites (theme code)

61 `data-aos=` callsites across 9 section files:

| File | Callsites |
|---|---|
| `sections/section-double.liquid` | ~20 |
| `sections/section-hero.liquid` | ~10 |
| `sections/section-slideshow.liquid` | ~8 |
| `sections/section-video.liquid` | ~6 |
| `sections/section-richtext.liquid` | ~5 |
| `sections/page.liquid` | ~4 |
| `sections/section-icons.liquid` | ~4 |
| `sections/section-custom-content.liquid` | ~3 |
| `sections/section-accordion.liquid` | ~1 |

By value:
- `data-aos="hero"` × 59 (97% of usage)
- `data-aos="svg-dash"` × 1
- `data-aos="icon__column__icon"` × 1

So in practice this is **one animation variant** used widely.

### Init point

`assets/theme.js` line 7223 (P8 stock bundle, prohibited to modify):

```js
window.theme.settings.animate_scroll
  && document.querySelector("[data-aos]")
  && (u.init({...}), document.body.classList.add("aos-initialized"))
```

Gated by:
1. Theme setting `animate_scroll` (operator-toggleable in Shopify admin)
2. DOM presence of `[data-aos]` (page-level guard)

### Asset cost

`assets/aos.css`: 1,487 lines (~38 KB unminified). Loaded via:
```liquid
<link rel="stylesheet" href="{{ 'aos.css' | asset_url }}" media="print" onload="this.media='all';this.onload=null;">
<noscript><link rel="stylesheet" href="{{ 'aos.css' | asset_url }}"></noscript>
```
(layout/theme.liquid:811-812)

**Async pattern**: `media="print"` initially means the stylesheet doesn't apply (print sheets don't apply to screen). `onload` swaps to `media="all"` to apply. Effect: doesn't block FCP.

---

## Current perf cost

### CLS

**Not in top-5 attribution on any template I've measured today.**

- Desktop home (post-fix re-baseline, 2026-05-18): top shifts are `<main>` broad 0.0093, `<div class="wrapper">` 0.0044, LoyaltyLion 0.0031. AOS not visible.
- Mobile home: similar — LoyaltyLion + main-content-broad dominate.
- Desktop PDP: Flickity carousel + tabs-wrapper; AOS not visible.

This is unsurprising: AOS animates `opacity` and `transform` (translateY), neither of which trigger layout shifts. The animation happens INSIDE existing layout slots.

### TBT

AOS JS lives inside `assets/theme.js`. Both AOS-enabled and AOS-disabled pages parse the same theme.js — there's no extra parse cost from AOS being on. The init function is small (~30 LoC inside theme.js's IIFE).

`aos.css` parse cost: ~5-10ms for 38 KB CSS on modern hardware.

### LCP

If LCP element has `data-aos="hero"` (likely on home/landing pages with hero sections), AOS could delay perceived LCP because the element fades in. But PSI measures LCP at first paint, not animation completion; fade-in starting from opacity:0 still registers the element at its final position. **Net impact: negligible.**

---

## The four options

### Option A — Gate behind `prefers-reduced-motion`

Add to `snippets/css-overrides.liquid`:
```css
@media (prefers-reduced-motion: reduce) {
  [data-aos] {
    opacity: 1 !important;
    transform: none !important;
    transition: none !important;
  }
}
```

**Effort**: 5 min, 1 commit, ~10 LoC CSS.
**Benefit**: Accessibility win for users with motion sensitivity. No perf change.
**Cost**: None.

### Option B — Replace with native IntersectionObserver + CSS-only fade

Replace all 61 `data-aos="hero"` with `data-fade-in`. Add small IO in `hairmnl-custom.js`:
```js
new IntersectionObserver((entries) => {
  entries.forEach(e => e.isIntersecting && e.target.classList.add('faded-in'));
}, { rootMargin: '100px 0px' }).observe(...);
```
CSS for `.faded-in` in `css-overrides.liquid`:
```css
[data-fade-in] { opacity: 0; transition: opacity 0.6s; }
[data-fade-in].faded-in { opacity: 1; }
```

**Effort**: 2-3 hr. 61 callsite migration across 9 section files. New JS section. CSS additions. kt0 lint check (none expected — `opacity` transitions don't trigger kt0).
**Benefit**: -38 KB aos.css. Bundle stays small.
**Cost**: 9 section file edits. Lose `data-aos="svg-dash"` and `data-aos="icon__column__icon"` (would need separate handling for these 2).

### Option C — Remove AOS entirely

Steps:
1. Toggle `theme.settings.animate_scroll = false` in Shopify admin (turns off AOS init in theme.js).
2. Remove `aos.css` `<link>` from `layout/theme.liquid:811-812` (requires Phase D cutover commit per Rule 10).
3. Leave 61 `data-aos="hero"` attributes in markup — harmless without JS init reading them.
4. Add `intentionally-orphan-assets.txt` entry for `assets/aos.css` until Shopify storage cleanup.

**Effort**: 5 min admin + Phase D layout/theme.liquid edit. Total ~30 min including cutover-PR ceremony.
**Benefit**: -38 KB aos.css load on every page. Cleaner architecture.
**Cost**: Lose hero fade-in animations site-wide. Visual change on 9 section types (page, hero, double, slideshow, video, richtext, icons, custom-content, accordion).

### Option D — Defer, accept current state

Do nothing. Revisit if:
- CrUX field data post-cutover shows AOS in top CLS sources, OR
- Phase D layout/theme.liquid PR has spare scope to drop the aos.css link without justifying the visual change separately, OR
- Merchandising decides to redesign the hero animations from scratch.

**Effort**: 0.
**Benefit**: 0.
**Cost**: 0.

---

## Recommendation: Option D (defer)

Rationale:
1. **No current CLS regression attributable to AOS** — post-fix top attribution is dominated by LoyaltyLion + main-content-broad, both unrelated to AOS.
2. **No meaningful TBT cost** — JS init is in theme.js (untouchable), CSS is async, parse cost trivial.
3. **Option B is 2-3 hours of work** for ~38 KB savings — better leverage from other Phase B sub-tickets.
4. **Option C requires a Shopify admin change + Phase D commit** — small but ceremony-heavy for a non-blocking change.
5. **Option A is cheap and accessibility-positive** — could ship anytime as a small stream:b PR if we want the WCAG win.

**Specific recommendation**: close ujg6.8 as **`wontfix`** with note: revisit if AOS surfaces as a measurable cost in post-cutover CrUX field data.

**Optional micro-action**: if you want the WCAG-friendly accessibility win, I can add Option A's `prefers-reduced-motion` rule to `snippets/css-overrides.liquid` in ~5 min. It's stream:b, single-file, zero risk. Just say the word.

---

## Open questions

1. **Is the hero fade-in visually important to brand?** Affects whether Option C (full removal) is acceptable. **Operator/merch input needed.** Until then, default to "keep."
2. **Are there CrUX-field motion-sensitivity complaints?** Affects Option A's priority. Operator-side info.

---

## What this ticket does NOT block

- Phase B.2 bundle work proceeds without AOS changes.
- Phase D cutover layout/theme.liquid edit can include `aos.css` removal IF Option C is approved by then; otherwise leave the `<link>` in place.

## Decision: close as `wontfix` unless operator wants Option A.
