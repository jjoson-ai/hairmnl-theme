# Phase 4 lint + CLS audit report

> **Bead:** hairmnl-theme-2i8b.8 (Phase 4.M7 — Wave D)
> **Date:** 2026-05-17
> **Status:** PARTIAL — kt0 audit complete; CLS spot-checks gated on PSI_API_KEY

---

## kt0 CSS containment audit

- **Command:** `python3 scripts/check-overlay-css.py`
- **Result:** ✅ PASS
- **Scanned:** 362 files
- **Violations:** 0
- **Exit code:** 0

The Pipeline 8 working tree has zero CSS containment violations (`contain: layout`, `transform`, `filter`, `will-change: transform`, `backdrop-filter` on parent selectors that would trap fixed-position overlays). This audit specifically catches the kt0-class bug pattern where cart drawers, mobile navs, modals, and lightboxes get trapped inside a containing block.

## CLS spot-checks per template

**⚠ BLOCKED** — `PSI_API_KEY` environment variable is not set. The `scripts/run-psi.sh` script requires this key to call the PageSpeed Insights API.

### URLs queued for measurement

When the key becomes available, run:

```bash
export PSI_API_KEY="<insert from Google Cloud Console>"
./scripts/run-psi.sh "https://www.hairmnl.com/?preview_theme_id=141168312419" mobile 2
```

| Template | URL pattern (preview_theme_id=141168312419) |
|---|---|
| Homepage | `/?preview_theme_id=141168312419` |
| Product page | `/products/davines-momo-shampoo?preview_theme_id=141168312419` |
| Brand collection | `/collections/loreal-professionnel?preview_theme_id=141168312419` |
| Blog index | `/blogs/news?preview_theme_id=141168312419` |
| Article | (operator picks one article URL) |
| Cart | `/cart?preview_theme_id=141168312419` |

### P6 baseline CLS reference (from os2-migration/perf-baseline-comparison.md)

| Metric | Pipeline 6.1.3 (live, mobile lab) | Pipeline 8.1.1 bare (preview, mobile lab) |
|---|---|---|
| CLS | 0.015 | 0.000 |

Field CrUX: live mobile CLS p75 = 0.04 (FAST band). After cutover, CLS should trend toward 0.00 as the P8 reserved-space patterns take effect.

## Recommendations

1. **kt0:** No action needed — clean scan. The brand-collection consolidation (M4) and app-snippet drops (M6) did not introduce new containment violations.

2. **CLS:** Unblock by setting `PSI_API_KEY` and re-running the 6 template spot-checks. Compare results against the P6 baseline CLS of 0.015 (lab) / 0.04 (CrUX field). Expected: P8 CLS stays at or near 0.000 after M1-M6 work, since none of the ported code should introduce layout shifts.

3. **No re-open actions:** The kt0 audit confirms no regressions from M1-M6 porting. CLS regressions (if any) would be visible after the PSI runs complete.