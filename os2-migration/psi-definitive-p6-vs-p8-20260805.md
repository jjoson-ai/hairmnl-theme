# DEFINITIVE: P6 baseline vs P6 last pull vs P8 live (2026-08-05, post-dh8x-fix)

The authoritative three-way lab comparison. Columns:
- **P6 baseline** = 2026-06-10 locked baseline (`psi-baseline-2026-06-10.md`). Desktop LCP from the
  06-08 summary JSON (same harness, 2 days earlier, score deltas within noise) — marked †.
- **P6 last pull** = 2026-07-16 (`psi-baseline-2026-07-16.md`), the final P6-live matrix.
- **P8 live now** = 2026-08-05 ~13:00 MNL post-fix matrix: current production (P8 + the dh8x
  containing-block fix), clean DNS, n=3/cell (30/30 cells OK). Raw: `/tmp/psi-baseline-20260805-postfix`.

Two earlier 08-05 matrices exist and are NOT the P8 column: the morning run (DNS-contaminated,
superseded) and the pre-fix clean run (input to the dh8x fix; CLS shown below as "P8 at launch").

## Lighthouse performance score

| Template | Mob base | Mob 07-16 | **Mob P8** | Desk base | Desk 07-16 | **Desk P8** |
|---|---|---|---|---|---|---|
| home       | 40 | 41 | **37** | 58 | 59 | **58** |
| collection | 37 | 49 | **40** | 68 | 65 | **74** |
| pdp        | 35 | 36 | **35** | 77 | 68 | **68** |
| cart       | 33 | 38 | **37** | 56 | 40 | **43** |
| brand      | 44 | 36 | **33** | 59 | 66.5 | **68** |

**Verdict: parity.** Every delta sits inside this store's documented ±5–15 lab-noise band.
Against the *last P6 pull*, P8 desktop is equal-or-better on all five templates (collection +9,
brand +1.5, cart +3, pdp 0, home −1). Against the locked baseline, desktop pdp/cart read lower — but
those two cells were at their historical highs on 06-10, and cart is artifact-dominated (below).
Mobile TBT ran high (0.9–1.3s) across the whole post-fix batch — afternoon lab variance, not a
theme signal.

## Lab LCP

| Template | Mob base | Mob 07-16 | **Mob P8** | Desk base† | Desk 07-16 | **Desk P8** |
|---|---|---|---|---|---|---|
| home       | 5.6s | 5.6s | **12.0s** | 1.2s | n/r | **1.3s** |
| collection | 11.9s | 5.6s | **14.1s** | 1.2s | n/r | **1.2s** |
| pdp        | 23.9s | 22.3s | **23.8s** | 1.3s | n/r | **1.2s** |
| cart       | 30.8s | 37.0s | **29.8s** | 6.6s | 6.96s | **5.8s** |
| brand      | 5.1s | 34.4s | **28.6s** | 1.2s | n/r | **1.2s** |

**Verdict, desktop: flat at ~1.2s in all three eras** (non-cart). The cart cell alternates between
~1s and ~6–7s depending on whether the BOGOS/Secomapp promo glider wins LCP on the empty lab cart —
the documented `wwni` artifact, present on P6 and P8 alike. There is no desktop LCP regression and
no step-change either; an earlier claim of a broad desktop improvement was overstated (only the
artifact-class cart cell ever differed).

**Verdict, mobile: the lab cannot establish direction, either way.** The same cells swing wildly
across pulls of the *same* theme — P6 home read 13.1→5.6s across two days, P6 brand 5.1→34.4s
across five weeks, and P8 brand read 4.1→23.5→28.6s within a single day. This is the documented
lantern/render-start bimodality. **Field RUM is the instrument for mobile**, and day-1 field was
healthy: sitewide mobile LCP 85.9% good, /products/ 87.7% (vs 88.7% pre-launch), CLS 94.7%,
INP 86.3%.

## CLS — the one real launch regression, and its resolution

| State | Worst cells |
|---|---|
| P6 baseline (06-10) | all 10 cells < 0.1 (worst: mobile cart 0.077) |
| P6 last pull (07-16) | all cells clean, max 0.045 |
| **P8 at launch (pre-fix)** | **brand mobile 2.011 · desktop brand 0.971 · desktop cart 0.682 · desktop collection 0.351** |
| **P8 live now (post-fix)** | **all 30 cells < 0.1 (worst: mobile cart 0.087)** + focused check: **0/12 fired on desktop brand, max 0.0244** |

The launch regression (bd `dh8x`) was a containing-block chain split across the inline/deferred CSS
boundary — latent since the 05-20 per-template CSS split, exposed when the cutover pulled FCP into
the deferred-CSS window, never introduced by the P8 code itself. Root-caused, A/B-tested on
unpublished duplicates, and shipped same-day (`/*dh8x*/.brick__block{position:relative}` in critical
CSS). Cumulative evidence: unfixed arms 4/40 runs show the defect signature; fixed arms **0/53**
(41 A/B + 12 live) — Fisher one-tailed **p ≈ 0.031**, on top of the deterministic mechanism proof.

Still open: bd `fj5m` — bimodal cart shifts (0.68 desktop / 0.41 mobile, "media lacking explicit
size" on the cart main + recent-products sections). Post-fix cart cells read clean, but 3 runs do
not clear a bimodal bug; it needs its own fix and n≥6 verification.

## Field (the real P8-vs-P6 verdict, pending)

CrUX origin p75, locked as the P6-era bar (window Jul 5–Aug 1): phone LCP **1803ms** (86.6% good),
CLS **0.06** (88.0%), INP **161ms** (82.8%); desktop LCP 1607ms, CLS 0.04, INP 103ms.
**Re-check ~2026-09-02** when the 28-day window is majority-P8 — that comparison, not the lab, is
the definitive P8-vs-P6 outcome. GA4 RUM day-1 shows no launch shock (mobile; desktop RUM is
crawler-poisoned until bd `8ile` is resolved).

## Bottom line

1. **P8 lab = P6 lab, within noise**, on every trustworthy cell; desktop ≥ the last P6 pull on all
   five templates.
2. **The single real launch regression (CLS up to 2.011) was found, root-caused, fixed and verified
   on live the same day.** CLS is now at P6-era cleanliness.
3. Mobile lab LCP is not a valid comparison instrument on this store in either direction; field RUM
   (healthy day-1, CrUX verdict ~Sep 2) is.
4. Known artifact cells (empty-cart glider LCP; lantern mobile bimodality) predate P8 and carry over
   unchanged. Open follow-ups: `fj5m` (cart CLS), `8ile` (crawler flood), GA4/GSC outage-window
   checks from `wzt4`.
