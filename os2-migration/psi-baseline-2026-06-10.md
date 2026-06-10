# PSI matrix — 2026-06-10 vs 2026-06-08
Re-aggregated from the 60 raw cell JSONs (the run completed all cells but was killed before writing its own summary). n=3 median. p6-live = production; p8-dev = ?preview_theme_id=141168312419.

## Mobile — Lighthouse score (06-08 → 06-10)
| template | P6 08 | P6 10 | ΔP6 | P8 08 | P8 10 | ΔP8 |
|---|---|---|---|---|---|---|
| home | 29 | 40 | +11 | 33 | 34 | +1 |
| collection | 34 | 37 | +3 | 50 | 45 | -5 |
| pdp | 38 | 35 | -3 | 52 | 49 | -3 |
| cart | 34 | 33 | -1 | 36 | 40 | +4 |
| brand | 43 | 44 | +1 | 40 | 54 | +14 |

## Desktop — Lighthouse score (06-08 → 06-10)
| template | P6 08 | P6 10 | ΔP6 | P8 08 | P8 10 | ΔP8 |
|---|---|---|---|---|---|---|
| home | 58 | 58 | +0 | 63 | 67 | +4 |
| collection | 64 | 68 | +4 | 71 | 64 | -7 |
| pdp | 71 | 77 | +6 | 72 | 72 | +0 |
| cart | 53 | 56 | +3 | 38 | 38 | +0 |
| brand | 60 | 59 | -1 | 60 | 60 | +0 |

## CLS (06-10) — GOOD threshold is <0.1
| template | P6 desk | P8 desk | P6 mob | P8 mob |
|---|---|---|---|---|
| home | 0.008 | 0.013 | 0.036 | 0.017 |
| collection | 0.011 | 0.021 | 0.041 | 0.041 |
| pdp | 0.029 | 0.022 | 0.01 | 0.01 |
| cart | 0.056 | 0.055 | 0.077 | 0.041 |
| brand | 0.013 | 0.008 | 0.042 | 0.041 |

## P6 mobile LCP — the long-standing structural issue (BSS B2B), seconds
| template | 06-08 | 06-10 |
|---|---|---|
| home | 13.1s | 5.6s |
| collection | 18.6s | 11.9s |
| pdp | 24.5s | 23.9s |
| cart | 33.1s | 30.8s |
| brand | 5.0s | 5.1s |

## Key findings (06-10 vs 06-08)
1. **Live (P6) stable - no regression from the 2026-06-09 GEO work.** All score deltas sit inside PSI lab noise (+/-5-15, no consistent direction): P6 desktop home 0 / collection +4 / pdp +6 / cart +3 / brand -1; P6 mobile mostly flat (home +11 is favorable variance, not a real gain). The Azta/David's schema + ItemList + near-win content shipped 06-09 are perf-safe (lab-invisible to Lighthouse, as expected for structured data + below-fold content).
2. **CLS clean** - every cell < 0.1 (GOOD) except the known cart bimodal noise (P6 mobile cart 0.077; cart-desktop ~0.056). The 06-07 watch-items stay resolved: cart-mobile P8 CLS 0.041 (06-07 0.272 -> 06-08 0.051 -> 06-10 0.041); brand stable.
3. **P6 mobile LCP root-caused (2026-06-10 follow-up) — NOT an app main-thread problem.** Operator confirmed BSS B2B is long uninstalled, and the bootup data agrees (top main-thread entries are just theme.js, GTM/gtag, web-pixels, freegift extension — all modest). Per-cell LCP-element analysis of the 60 raw Lighthouse JSONs found two concrete causes:
   - **PDP mobile 22-24s = lazy-loaded LCP image.** All 3 runs: LCP element is the product gallery img (`div.product__media .lazy-image img.srcset`, data-image-id 22744548147299) with `loading="lazy"`. The `is_first` eager+fetchpriority logic in `snippets/media.liquid:44` works — but it eager-loads the DOM-FIRST media, while the initially-VISIBLE slide is the variant-featured media (2nd in DOM) and stays lazy. Proof: P8's rendered LCP img is `loading="eager"` -> 7.0-7.5s vs P6 22-24s. The ~17s gap is this one attribute. bd filed (stream:a).
   - **Cart 30-37s mobile / 6-7s desktop = BOGOS promo glider.** ALL 12 cart cells (both themes, both form factors): LCP element is `#sca-promotion-glider .content-promotion-message` ("FREE Tote Bag...") — the Secomapp/BOGOS free-gift ticker painting late on a lab-EMPTY cart (real carts have product rows as LCP). Mostly a lab artifact; field-check then decide. bd filed.
   - home (5.6s) / collection (11.9s) improvements vs 06-08: proper banner-image LCP elements, bimodal throttled-load variance — not a fix.
4. **P8-dev stable** - still beats P6 on most cells; the P8 cart-desktop weakness (38) persists (documented cold-start TBT storm), P8-only so low urgency.

Methodology: re-aggregated from /tmp/psi-baseline/*.json (60 cells = 2 themes x 2 strategies x 5 templates x 3 runs, n=3 median) after the run was killed before writing its own summary; compared to psi-baseline-2026-06-08.summary.json.
