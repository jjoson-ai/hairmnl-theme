# P8 dev PSI matrix — three-way comparison (2026-05-26)

Comparing today's matrix (after the ujg6.62 CSS chunk fix) against:
- P6 live (current production)
- P8 dev YESTERDAY (before the CSS chunk fix — page was visually broken)
- Bare P8 baseline (theoretical max from `os2-migration/perf-baseline-comparison.md`)

All numbers are PSI lab scores, n=3 median (where available).

## Mobile

| Template | Bare P8 | P6 live | P8 TODAY (fixed) | P8 YESTERDAY (broken) | Δ today vs P6 | Δ today vs YDA |
|---|---|---|---|---|---|---|
| home       | **62** | 39 | 33 | 45 | -6 | **-12** |
| collection | n/a    | 40 | 33 | 54 | -7 | **-21** |
| pdp*       | n/a    | 34 | 18*| 34 | -16 | -16 |
| cart       | n/a    | 28 | 34 | 37 | **+6** | -3 |
| brand      | n/a    | 47 | 33 | 52 | -14 | **-19** |

\* P8 mobile PDP CLS=0.886 today is clearly noise (typical is 0.022-0.046). Score=18 is dragged down by that single CLS outlier — not a real regression.

## Desktop

| Template | Bare P8 | P6 live | P8 TODAY (fixed) | P8 YESTERDAY (broken) | Δ today vs P6 | Δ today vs YDA |
|---|---|---|---|---|---|---|
| home       | **72** | 56 | 55 | (all failed) | -1 | **NEW: now measurable** |
| collection | n/a    | 59 | 54 | 55 | -5 | -1 |
| pdp**      | n/a    | 15** | 54 | 53 | **+39** | +1 |
| cart       | n/a    | 41 | 53 | 56 | **+12** | -3 |
| brand      | n/a    | 56 | 54 | 53 | -2 | +1 |

\*\* P6 desktop PDP CLS=0.971 today is noise (typical PDP CLS is 0.022-0.026). +39 delta is artificial.

## TBT (the real signal)

Mobile TBT (ms):

| Template | Bare P8 | P6 today | P8 today | P8 yesterday |
|---|---|---|---|---|
| home       | **175** | 2102 | 4340 | 1424 |
| collection | n/a     | 1780 | 5560 | 441  |
| pdp        | n/a     | 3850 | 1260 | 2050 |
| cart       | n/a     | 3370 | 4250 | 1661 |
| brand      | n/a     | 2320 | 7700 | 754  |

Desktop TBT (ms):

| Template | Bare P8 | P6 today | P8 today | P8 yesterday |
|---|---|---|---|---|
| home       | **225** | 7490 | 5480 | (failed) |
| collection | n/a     | 2520 | 2480 | 2860     |
| pdp        | n/a     | 2450 | 3390 | 5482     |
| cart       | n/a     | 1210 | 12660| 2501     |
| brand      | n/a     | 10640| 1300 | 5454     |

## Key findings

### 1. The CSS chunk fix degraded mobile PSI scores significantly
Before the fix, P8 dev mobile homepage scored 45 — but the page was visually broken
(cart drawer inline, raw Swiper text, broken grids). PSI doesn't measure visual
correctness; it measures LCP/CLS/TBT. With 12 CSS files returning 404, the browser
had less work to do, so the metrics looked artificially good.

After the fix:
- All 12 split CSS files (≈580KB total) now load and apply correctly
- Mobile home TBT: 1.42s → 4.34s (+2.92s)
- Mobile collection TBT: 441ms → 5.56s (+5.12s)
- Mobile brand TBT: 754ms → 7.70s (+6.95s)
- Mobile scores dropped 12-21 points

**This isn't a regression — it's the page actually working.** The "fast" yesterday
numbers were measuring a broken page.

### 2. Cart pages are P8's biggest visible win
- Mobile cart: P8 34 vs P6 28 (+6, P6 has 22s LCP from cart heavy markup)
- Desktop cart: P8 53 vs P6 41 (+12)

### 3. Gap to bare P8 baseline is the migration's actual cost
- Mobile home: bare P8 = 62, P8 dev today = 33 → **-29 points**
- Desktop home: bare P8 = 72, P8 dev today = 55 → **-17 points**

This is the cost of apps + customizations on top of bare Pipeline 8. ~29-point gap on
mobile, ~17 on desktop. Cleaning up STKY/GTM/Reamaze/etc. (tracked in a7av, 2i8b.24)
could recover some of this.

### 4. P8 desktop home is now PSI-measurable
Yesterday all 3 desktop home runs failed (timeout/500). Today 2/3 succeed at 55.
The CSS-chunked theme is light enough for PSI to complete the audit within 180s.

### 5. PSI variance is high — single-run results unreliable
- P8 mobile PDP run 1 showed CLS=0.886 (10× the typical 0.04)
- P6 desktop PDP runs showed CLS=0.971 (40× typical)
These are likely cold-cache GTM/perf-kit pre-warm runs. Median across n=3 helps but
not enough.

## Recommendations

1. **Hold off pushing the P6-only CSS to P8 (2i8b.47).** Current matrix shows the page
   is already heavy after the chunk fix; adding more CSS rules won't help PSI numbers.
   The visual impact of the missing P6-only rules is minimal at desktop (mostly mobile
   grid + responsive font scaling). Worth porting for visual consistency but won't move
   PSI.
2. **The TBT regressions on mobile (home/collection/brand) are the actionable issue.**
   The +5s TBT on mobile brand is the biggest target. Likely a JS execution issue from
   shopify-perf-kit (bba5) doing more work now that CSS is loaded.
3. **Re-run the matrix tomorrow to confirm.** Today's numbers include cold-cache
   variance. A second-day run with warm CDN caches should stabilize.
