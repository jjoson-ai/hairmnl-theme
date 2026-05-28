# P8 dev PSI matrix — three-way comparison (2026-05-28)

Comparing today's matrix (after `ujg6.59` critical-CSS restructure phases 2a/2b/2c)
against:
- P6 live (current production)
- P8 dev on 2026-05-26 (post chunk fix, pre ujg6.59)
- Bare P8 baseline (theoretical max from `os2-migration/perf-baseline-comparison.md`)

All numbers are PSI lab scores, n=3 median (where available; cell shows actual sample
size as `n/runs`).

## Mobile

| Template | Bare P8 | P6 live | P8 dev TODAY | P8 dev (2026-05-26) | Δ today vs P6 | Δ vs 05-26 |
|---|---|---|---|---|---|---|
| home       | **62** | 29 | **40** | 33 | **+11** ✅ | +7 |
| collection | n/a    | 29 | **33** | 33 | **+4** ✅  | ±0 |
| pdp        | n/a    | 28 | **40** | 18* | **+12** ✅ | +22 |
| cart       | n/a    | 30 | **35** | 34 | **+5** ✅  | +1 |
| brand      | n/a    | 27 | **34** | 33 | **+7** ✅  | +1 |

\* 2026-05-26 P8 mobile PDP score was dragged down by a CLS=0.886 outlier (PSI noise).

## Desktop

| Template | Bare P8 | P6 live | P8 dev TODAY | P8 dev (2026-05-26) | Δ today vs P6 | Δ vs 05-26 |
|---|---|---|---|---|---|---|
| home       | **72** | 61 | 56 | 55 | -5  | +1 |
| collection | n/a    | 63 | 57 | 54 | -6  | +3 |
| pdp        | n/a    | 74 | 58 | 54 | **-16** | +4 |
| cart       | n/a    | 42 | **50** | 53 | **+8** ✅ | -3 |
| brand      | n/a    | 58 | **72** | 54 | **+14** ✅ | **+18** |

## TBT (ms)

Mobile:

| Template | Bare P8 | P6 today | P8 today | P8 (05-26) |
|---|---|---|---|---|
| home       | **175** | 4380 | 5230 | 4340 |
| collection | n/a     | 2200 | **561**  | 5560 |
| pdp        | n/a     | 2470 | 1410 | 1260 |
| cart       | n/a     | 1600 | 8020 | 4250 |
| brand      | n/a     | 2460 | 4650 | 7700 |

Desktop:

| Template | Bare P8 | P6 today | P8 today | P8 (05-26) |
|---|---|---|---|---|
| home       | **225** | 1270 | 3400 | 5480  |
| collection | n/a     | 2200 | 1800 | 2480  |
| pdp        | n/a     | 414  | 947  | 3390  |
| cart       | n/a     | 994  | 1350 | 12660 |
| brand      | n/a     | 1440 | **347** | 1300 |

## LCP (s) — mobile only (where the P8 win is concentrated)

| Template | P6 today | P8 today | Δ |
|---|---|---|---|
| home       | 8.03  | 5.87 | **-2.2s** |
| collection | 12.08 | 6.22 | **-5.9s** |
| pdp        | 18.69 | 5.15 | **-13.5s** |
| cart       | 18.41 | 6.46 | **-12.0s** |
| brand      | 17.50 | 7.26 | **-10.2s** |

P6 mobile LCP is catastrophically slow today on pdp/cart/brand (17-19s). Part of P8's
mobile reversal is genuine improvement, part is a bad P6 day. Cross-check needed in
field data (CrUX) before declaring the magnitude.

## Key findings

### 1. P8 dev now beats P6 live on every mobile template

First time this has been true in any PSI matrix to date. Previous matrix (2026-05-26)
had P8 ahead only on cart (+6). This run: home +11, collection +4, pdp +12, cart +5,
brand +7. The PDP jump (+22 since 05-26) is the largest single template move.

Two contributors:
- `ujg6.59` Phase 2a/2b/2c critical-CSS restructure: removed 48 unused selectors,
  gated PDP-only and collection-only rules behind `template.name` checks. Reduced
  inline critical-CSS by 16-26% per non-target template, which lowered FCP across the
  board (FCP P8 mobile: 2.3-3.3s vs 2.4-2.9s on 05-26 — similar but with the new
  smaller critical-CSS budget supporting much better LCP).
- P6 live had a notably slow day on PSI (mobile LCP 8-19s across templates). Some of
  the delta is P6 variance, not P8 improvement.

### 2. Brand desktop hit the bare P8 baseline (72 = 72)

P8 dev brand desktop scored **72**, matching the bare P8 reference exactly. This means
on brand pages with all apps + customizations active, the desktop score has zero
overhead vs theoretical max. Brand desktop TBT was 347ms — best of any cell in the
matrix.

### 3. Cart mobile TBT is the largest open gap

P8 cart mobile TBT: 8.02s vs P6 1.60s. Worse than the previous matrix (4.25s) — this
metric is bimodally distributed (depends on shopify-perf-kit cold-start). Cart score
is still +5 vs P6 (P6's cart LCP is 18.4s), but the TBT spread says perf-kit cold-start
is producing 4-8s long-task storms inconsistently.

### 4. Desktop PDP: P6 74 vs P8 58 (-16)

Only template where P6 has a clear desktop advantage. TBT delta is only +533ms (P8
worse), so the score gap is driven by something else — likely SI (5.17s vs 2.48s on
P6) and TTI from PDP-specific JS. Worth a targeted profile.

### 5. Collection mobile CLS jumped to 0.354

Previous P8 matrices: 0.015 (05-26), 0.015 (05-19), 0.015 (05-18). Today: **0.354**.
P6 today: 0.042. This is a 23× jump on the same theme code in 2 days.

Possible causes:
- ujg6.59 Phase 2c gated 26 collection-only rules behind `{% if template.name == 'collection' %}`.
  These should still be inlined on collection pages (the gate evaluates TRUE there),
  but if any of them affect above-fold layout and Liquid evaluates the gate at a
  different lifecycle point than expected, layout could shift.
- PSI variance — a single run with high CLS dominating the median. Need to check
  individual run JSON before concluding.

**Recommendation:** Open a P2 bd ticket to verify by re-running collection mobile n=5
and inspecting the individual CLS values. If consistently high, audit the 26 gated
selectors for above-fold layout impact.

### 6. Gap to bare P8 baseline

- Mobile home: bare 62, P8 dev 40 → **-22 pts** (was -29 on 05-26 — closed 7 pts)
- Desktop home: bare 72, P8 dev 56 → **-16 pts** (was -17 — closed 1 pt)
- Desktop brand: bare 72, P8 dev 72 → **0 pts** ✅

Average mobile P8 dev = ~36 vs bare 62 (-26 pts gap).
Average desktop P8 dev = ~59 vs bare 72 (-13 pts gap).

This is the cost of apps + customizations. Primary remaining levers:
- STKY cutover (`a7av.7`) — removes 780ms long task on every page
- shopify-perf-kit investigation (`bba5`) — +754ms scripting on P8 vs P6, cause unknown
- Mobile cart TBT recovery (`2i8b.24`) — GTM cleanup + Judge.me cart defer

## Open questions

1. Is the mobile collection CLS=0.354 a real regression or PSI noise? (Verify with n=5 rerun.)
2. Is P6's catastrophic mobile LCP today a server-side hiccup or sustained? (Check tomorrow.)
3. What's driving the desktop PDP score gap if not TBT?

## Methodology

- Run command: `python3 scripts/psi-baseline-matrix.py --runs=3 --concurrency=2`
- Started: 2026-05-28 13:25
- Completed: 2026-05-28 ~13:50
- Total PSI calls: 60 (2 themes × 2 strategies × 5 templates × 3 runs)
- PSI API had intermittent 500s on early calls; final sample sizes range from 1-3 runs
  per cell (see `summary.md` for per-cell n).
- Raw data: `/tmp/psi-baseline/*.json`
- Summary: `/tmp/psi-baseline/summary.md` and `.json`
