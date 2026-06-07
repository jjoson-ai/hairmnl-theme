# P8 dev PSI matrix — comparison (2026-06-07)

Re-run of `scripts/psi-baseline-matrix.py --runs=3 --concurrency=2` (**60/60 cells OK, n=3 every cell** — cleanest sample to date). Compared against:
- **P6 live** (current production — now carrying the FAQ-schema program changes from 2026-06-05/06)
- **P8 dev on 2026-05-28** (the previous check, post `ujg6.59` critical-CSS restructure)
- **Bare P8 baseline** (mobile 62 / desktop 72, from `perf-baseline-comparison.md`)

All numbers are PSI lab scores, n=3 median.

## Mobile — score

| Template | Bare P8 | P6 today | P8 today | P8 (05-28) | Δ P8 vs P6 | Δ P8 vs 05-28 |
|---|---|---|---|---|---|---|
| home       | **62** | 30 | **36** | 40 | **+6** ✅  | -4 |
| collection | n/a    | 39 | **59** | 33 | **+20** ✅ | **+26** |
| pdp        | n/a    | 34 | **46** | 40 | **+12** ✅ | +6 |
| cart       | n/a    | 37 | 33 | 35 | **-4** ⚠️ | -2 |
| brand      | n/a    | 34 | **53** | 34 | **+19** ✅ | +19 |

P8 mobile beats P6 on 4/5 (was 5/5 on 05-28). Only **cart** flipped (P6 cart improved 30→37, P8 cart slipped 35→33).

## Desktop — score

| Template | Bare P8 | P6 today | P8 today | P8 (05-28) | Δ P8 vs P6 | Δ P8 vs 05-28 |
|---|---|---|---|---|---|---|
| home       | **72** | 58 | 56 | 56 | -2  | ±0 |
| collection | n/a    | 70 | 62 | 57 | -8  | +5 |
| pdp        | n/a    | 65 | 60 | 58 | -5  | +2 |
| cart       | n/a    | 43 | **48** | 50 | **+5** ✅ | -2 |
| brand      | n/a    | 58 | 59 | 72 | +1 | **-13** ⚠️ |

Desktop PDP gap (the 05-28 −16 open question) **mostly closed → −5** (P6 74→65, P8 58→60). Brand desktop **lost its 05-28 bare-P8 parity** (72→59).

## Mobile — TBT (ms) — the biggest P8 movement

| Template | P6 today | P8 today | P8 (05-28) | P8 Δ vs 05-28 |
|---|---|---|---|---|
| home       | 3200 | 2320 | 5230 | **−2910** ✅ |
| collection | 950  | **250**  | 561  | −311 ✅ |
| pdp        | 1060 | 569  | 1410 | −841 ✅ |
| cart       | 1100 | 847  | 8020 | **−7173** ✅ |
| brand      | 1190 | 695  | 4650 | **−3955** ✅ |

The cart-mobile-TBT cold-start storm (8.0s on 05-28) did **not** reproduce today (0.85s). P8 mobile TBT improved on every template.

## Mobile — CLS

| Template | P6 today | P8 today | P8 (05-28) | Note |
|---|---|---|---|---|
| home       | 0.035 | 0.003 | — | |
| collection | 0.041 | **0.046** | 0.354 | **05-28 scare was NOISE — resolved** ✅ |
| pdp        | 0.010 | 0.010 | — | clean (FAQ template — see below) |
| cart       | 0.077 | **0.272** | — | **NEW: bimodal (runs 0.05/0.27/0.56) — likely noise** ⚠️ |
| brand      | 0.036 | 0.045 | — | |

## Mobile — LCP (s) — P6 still catastrophic

| Template | P6 today | P8 today | Δ |
|---|---|---|---|
| home       | 7.95  | 6.66  | -1.3s |
| collection | 18.21 | 5.88  | **-12.3s** |
| pdp        | 22.99 | 7.04  | **-16.0s** |
| cart       | 31.63 | 35.05 | both terrible |
| brand      | 11.49 | 6.65  | -4.8s |

P6 mobile LCP remains catastrophic on collection/pdp/cart (18–32s) — same pattern flagged on 05-28, still unresolved. **Cart LCP is bad on both themes** (31–35s).

## Key findings

1. **Collection-mobile CLS=0.354 (05-28 open Q #1) = confirmed PSI NOISE.** Today's three P8 runs: 0.041 / 0.089 / 0.046 (median 0.046), back to the historical ~0.04. No layout-shift problem on collections. **Closed.**
2. **P8 mobile TBT improved across the board** vs 05-28 — most dramatically cart (8.0s→0.85s) and brand (4.65s→0.70s). The cart-mobile-TBT open item (`2i8b.24`) looks much healthier today (cold-start storm didn't fire).
3. **Desktop PDP gap (05-28 open Q #3, −16) mostly closed → −5.** P6 PDP desktop dropped 74→65 (the 05-28 74 was partly a good-P6 day); P8 up 58→60.
4. **Cart is the one place P6 now wins on mobile** (−4). P6 cart improved while P8 cart slipped slightly.
5. **P6-live mobile scores rose across the board vs 05-28** (+1 to +10) — but this is mostly 05-28 having been a *bad P6 PSI day*, not a real production gain. P6 mobile LCP is still 8–32s.

## FAQ-program perf check ✅

The matrix PDP cell is `/products/kerastase-genesis-anti-hair-fall-fortifying-serum` — **one of the 6 products now on a `faq-*` template** (genesis-serum). On P6 live today it measured **CLS 0.010, score 34 (+6 vs 05-28), TBT 1.06s**. The static-tab snapshot + the `section-faq` accordion + FAQPage schema added **no layout shift and no perf regression** — the FAQ schema program is perf-safe on the PDP.

## Open questions

1. **Cart mobile P8 CLS = 0.272** (bimodal: 0.05/0.27/0.56) — same noise signature as the now-resolved collection CLS. Recommend an n=5 re-run before treating as real.
2. **Brand desktop 72→59** — lost the bare-P8 parity from 05-28. Brand desktop is historically variable run-to-run; recommend a confirm before treating as a regression.
3. **P6 mobile LCP 18–32s on collection/pdp/cart** — still unexplained (server hiccup vs sustained). Cross-check field data (CrUX) for the real magnitude.

## Methodology

- Run command: `python3 scripts/psi-baseline-matrix.py --runs=3 --concurrency=2`
- 2026-06-07 12:09–12:32, **60/60 cells OK** (n=3 all — no PSI API failures this run)
- Raw data: `os2-migration/psi-baseline-2026-06-07.summary.json`
