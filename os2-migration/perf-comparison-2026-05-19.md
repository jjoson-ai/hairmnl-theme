# Perf snapshot — 2026-05-19 ~16:46 vs 2026-05-18 ~21:15 baseline

Methodology: PSI v5 lab via `scripts/psi-baseline-matrix.py` (Lighthouse 13.x, Slow 4G / wired). n=2 medians per cell. 34/40 cells OK today (6 transient API errors).

Cells format: `score / LCP / CLS / TBT`

## CrUX (real-user p75, 28-day rolling, P6 live only)

| Cell | LCP | CLS | INP | FCP | vs yesterday |
|---|---|---|---|---|---|
| Origin mobile | 2212ms | 0.08 | 168ms | 1868ms | LCP -55ms, INP -2ms |
| Origin desktop | 2000ms | 0.10 | 104ms | 1526ms | LCP -22ms, CLS -0.01 |
| Home mobile | 2791ms | 0.03 | 227ms | 2519ms | LCP -115ms, INP -10ms |
| Home desktop | 2314ms | 0.17 | 178ms | 2159ms | LCP -94ms, INP +19ms |

**Verdict:** CrUX origin-level passing 5/6 thresholds (origin desktop CLS marginal at 0.10). Slight improvement vs yesterday's pull, expected given the rolling-window mechanics.

## Mobile lab

| Tpl | P6 today | P8 today | Δ score P8 vs P6 today | Δ score P8 vs P8 yest | Notable change |
|---|---|---|---|---|---|
| home | 28 / 8.52s / 0.037 / 7915ms | 35 / 8.23s / 0.028 / 2339ms | +7 | -3 | TBT Δ 1322→2339ms |
| collection | 43 / 6.68s / 0.027 / 1317ms | — | — | — | — |
| brand | 40 / 6.11s / 0.035 / 1501ms | 35 / 7.41s / 0.015 / 2822ms | -5 | +3 | TBT Δ 4995→2822ms |
| pdp | 33 / 7.43s / 0.021 / 2924ms | 40 / 7.63s / 0.015 / 1115ms | +7 | +6 | TBT Δ 2161→1115ms |
| cart | 42 / 16.17s / 0.071 / 1036ms | 41 / 17.51s / 0.041 / 1021ms | -1 | +20 | CLS Δ 0.283→0.041, TBT Δ 1537→1021ms |

## Desktop lab

| Tpl | P6 today | P8 today | Δ score P8 vs P6 today | Δ score P8 vs P8 yest | Notable change |
|---|---|---|---|---|---|
| home | 55 / 1.62s / 0.009 / 2105ms | 58 / 1.34s / 0.011 / 2134ms | +3 | +5 | TBT Δ 4222→2134ms |
| collection | 57 / 1.31s / 0.009 / 3320ms | 60 / 1.47s / 0.010 / 1176ms | +3 | +3 | — |
| brand | 55 / 1.66s / 0.021 / 1463ms | 58 / 1.23s / 0.011 / 1130ms | +3 | +4 | — |
| pdp | 57 / 1.38s / 0.024 / 1642ms | 61 / 1.43s / 0.032 / 696ms | +4 | +2 | — |
| cart | 36 / 8.77s / 0.054 / 3497ms | 36 / 7.72s / 0.074 / 1391ms | +0 | -4 | TBT Δ 666→1391ms |

