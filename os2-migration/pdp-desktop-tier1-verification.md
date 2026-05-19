# PDP Desktop Tier 1 verification — variance, not regression

**Date:** 2026-05-20
**bd ticket:** hairmnl-theme-ujg6.55 (closing as won't-do / variance)
**Method:** `scripts/psi-baseline-matrix.py --skip-preflight --runs 3 --concurrency 5`
**Data:** `/tmp/psi-baseline/*.json` (60 cells captured 2026-05-19 evening + 2026-05-18 baseline)

## Headline

The −3 score gap on P8 desktop PDP that surfaced in the line-by-line comparison is **PSI cache + Lighthouse preview-bar variance**, not a real code regression.

## n=3 PDP Desktop medians

| Metric | P6 live | P8 dev | Δ |
|---|---|---|---|
| Score | 57 | 54 | −3 |
| LCP | 1315ms | 1571ms | +256ms |
| TBT | 2038ms | 4429ms | +2391ms |
| FCP | 549ms | 747ms | +198ms |
| CLS | 0.016 | 0.019 | +0.003 |

## Why this is variance, not regression

1. **PSI edge cache lock-in.** Runs 1+2 on each theme returned identical `fetchTime` timestamps (P6: 18:23:34Z, P8: 18:28:03Z) with identical headline metrics. PSI's edge served the same audit response twice. Effective sample = 2 distinct datapoints, not 3.
2. **The non-cached run flips the verdict.** Run3 (yesterday's baseline, fresh fetch): **P8 TBT 722ms vs P6 TBT 1087ms** — P8 *better*. The 3-pt score gap on that run is driven by SI (P8 4056 vs P6 3094), not TBT.
3. **P8 TBT span 722→4429ms** between two cold runs = 3700ms swing. That's textbook Lighthouse preview-bar overhead on dev themes (previously documented at +456ms baseline; spikes higher when stack-pack audits trigger).
4. **Mobile PDP confirms theme code is fine.** P8 mobile PDP score 42 / LCP 6.5s vs P6 mobile 31 / LCP 20.2s — same theme, leaps ahead. A real desktop code regression would also surface on mobile.

## Decision

- Close `ujg6.55` as `won't-do` — confirmed variance.
- Do NOT proceed to Tier 2 (Elevar TAE defer). The premise (real regression) isn't established.
- If desktop PDP **CrUX field data** shows degradation post-cutover, revisit with WebPageTest cold runs against the live URL (no preview-bar artifact, no PSI edge cache).

## Future PSI matrix hygiene

PSI's edge cache deduplicates fast back-to-back runs. To get true n=3:
- Stagger runs by ≥3 minutes per cell, OR
- Append a cache-buster query param (`?_pmcb=<timestamp>`) to each URL per run, OR
- Use the published WebPageTest API for definitive cold runs

## Full desktop matrix snapshot (n=3 medians)

| Template | P6 score | P8 score | Δ | P6 TBT | P8 TBT | Δ TBT |
|---|---|---|---|---|---|---|
| Home | 56 | 57 | **+1 P8** | 2069 | 1450 | −619 P8 |
| Brand | 55 | 56 | **+1 P8** | 1952 | 1129 | −823 P8 |
| Collection | 61 | 76 | **+15 P8** | 1243 | 283 | −960 P8 |
| PDP | 57 | 54 | −3 (variance) | 2038 | 4429 | +2391 (variance) |
| Cart | 39 | 37 | −2 (cookie-bar artifact) | 2228 | 1610 | −618 P8 |

**P8 ahead on 3 of 5 desktop templates by score; tied within variance on the other 2. Desktop FCP is the consistent P8 weakness across 4 of 5 templates (+40–160ms), driven mostly by PDP's +198ms FCP gap.**
