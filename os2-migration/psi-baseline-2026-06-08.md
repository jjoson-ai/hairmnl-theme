# PSI matrix — comparison (2026-06-08)

Re-run of `scripts/psi-baseline-matrix.py --runs=3 --concurrency=2` — **60/60 cells OK, n=3 every cell**, 26.0 min. This is a **confirmation run** after the `wscl` header-CLS fix + the FAQ/GEO program shipped; compared against the **2026-06-07 baseline** (the previous check). Lab scores, n=3 median. Raw: `psi-baseline-2026-06-08.summary.json`.

## Mobile — score (today vs 06-07)

| Template | P6 06-07 | P6 today | P8 06-07 | P8 today | P6 Δ | P8 Δ |
|---|---|---|---|---|---|---|
| home       | 30 | 29 | 36 | 33 | −1 | −3 |
| collection | 39 | 34 | 59 | 50 | −5 | −9 |
| pdp        | 34 | **38** | 46 | **52** | +4 | +6 |
| cart       | 37 | 34 | 33 | 36 | −3 | +3 |
| brand      | 34 | **43** | 53 | 40 | +9 | −13 |

## Desktop — score (today vs 06-07)

| Template | P6 06-07 | P6 today | P8 06-07 | P8 today | P6 Δ | P8 Δ |
|---|---|---|---|---|---|---|
| home       | 58 | 58 | 56 | **63** | ±0 | +7 |
| collection | 70 | 64 | 62 | **71** | −6 | +9 |
| pdp        | 65 | **71** | 60 | **72** | +6 | +12 |
| cart       | 43 | **53** | 48 | 38 | +10 | −15 |
| brand      | 58 | 60 | 59 | 60 | +2 | +1 |

All score deltas sit inside normal PSI lab variance (±5–15, worst on cart/brand). No consistent direction = noise, not a real shift.

## CLS — clean across the board (the thing the recent work targeted)

| | home | collection | pdp | cart | brand |
|---|---|---|---|---|---|
| P6 desktop | 0.011 | 0.011 | 0.029 | 0.056 | 0.012 |
| P8 desktop | 0.010 | 0.012 | 0.022 | 0.055 | 0.008 |
| P6 mobile  | 0.041 | 0.045 | 0.000 | 0.075 | 0.041 |
| P8 mobile  | 0.009 | 0.045 | 0.010 | 0.051 | 0.044 |

## Key findings

1. **No regression from `wscl` (header CLS fix) or the FAQ/GEO program.** P6-live (production, carries both) is flat-to-up vs 06-07 — desktop pdp +6, cart +10, brand +2, home ±0; only collection −6 (noise). `wscl` is a `min-width` rule (lab-invisible CLS), so flat lab scores are expected and confirmed.
2. **FAQ/GEO program re-confirmed perf-safe.** The PDP cell (`genesis-serum`, a `faq-*` template) on P6-live rose 65→71 desktop / 34→38 mobile, CLS desktop 0.029 / mobile 0.000. No layout shift, no perf cost from the FAQPage schema + static-tab snapshot.
3. **Both 06-07 open questions resolved — confirmed noise by this fresh n=3** (matching my earlier n=5 rechecks):
   - Cart-mobile P8 CLS: 06-07 **0.272** (bimodal) → today **0.051**. Noise. ✅
   - Brand-desktop P8: 06-07 72→59 "lost parity" → today **60** (sits in the 57–76 variable band). Just a noisy template, not a regression. ✅
4. **P8 migration advantage holds.** P8 beats P6 on 7/10 cells (desktop home/collection/pdp; mobile home/collection/pdp/cart). The exceptions are all P8's known weak spots.
5. **Cart is P8's weak template — recheck candidate.** Desktop cart P8 **38 vs P6 53** (−15; P8 TBT 1.08s vs P6 0.37s). P8 cart desktop slipped (48→38) while P6 rose (43→53). Cart has a documented cold-start TBT storm; recommend an n=5 confirm before treating as real. P8-dev only (not live) → low urgency.
6. **P6 mobile LCP still catastrophic — unchanged structural issue.** home 13.1s / collection 18.6s / pdp 24.5s / cart 33.2s. Same 8–33s pattern flagged 06-07 + 05-28 (BSS B2B dominates per memory). P8 mobile LCP much better (5–7s) except cart (34s, bad on both). This is the one genuinely unresolved item — not CLS, not regression, a long-standing P6 LCP problem.

## Methodology
- `python3 scripts/psi-baseline-matrix.py --runs=3 --concurrency=2`, 2026-06-08 21:06–21:31, 60/60 OK.
- p6-live = bare production URLs; p8-dev = `?preview_theme_id=141168312419`. Bare-P8 reference: mobile 62 / desktop 72 (2026-05-17, not re-measured).
