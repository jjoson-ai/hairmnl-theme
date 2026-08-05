# PSI matrix — CLEAN re-run (2026-08-05 ~09:00 MNL), post-DNS-recovery

**Why this exists:** the first launch-day matrix (`psi-baseline-2026-08-05.md`) was measured while
`hairmnl.com`'s registration had lapsed and DNS was migrating to Namecheap parking (bd `wzt4`).
Roughly half of first-attempt cells failed with `ERR_CONNECTION_FAILED`, which at the time was
misattributed to origin strain from the crawler flood (bd `8ile`). This re-run is the authoritative
launch-day read: domain renewed (expiry now 2027-08-04), DNS fully converged on 8.8.8.8 / 1.1.1.1 /
9.9.9.9, storefront serving normally.

Same harness (`scripts/psi-baseline-matrix.py`, live-theme-only, n=3 target + serial retry pass).
Coverage 26/30 cells. Raw: `/tmp/psi-baseline-20260805-rerun/`.

## Score and mobile/desktop LCP — morning (contaminated) vs now (clean)

| | Mob score AM | **Mob score clean** | Desk score AM | **Desk score clean** | Mob LCP AM | **Mob LCP clean** | Desk LCP AM | **Desk LCP clean** |
|---|---|---|---|---|---|---|---|---|
| home       | 59 (n=1) | **47** | 48.5 | **69** | 8.4s | **13.9s** | 1.7s | **1.1s** |
| collection | 49.5 | **55** | 78 | **78** | 7.4s | **9.2s** | 0.8s | **1.0s** |
| pdp        | 66 | **41** | 66 | **78** | 6.5s | **23.5s** | 0.9s | **1.7s** |
| cart       | 53 | **45** | 93 | **77.5** | 7.3s | **26.0s** | 0.9s | **1.7s** |
| brand      | 41 | **34** | 75 | **69** | 4.1s | **23.5s** | 1.3s | **0.9s** |

## ⚠️ CORRECTION: the "mobile LCP step-change" does NOT survive a clean measurement

The morning report claimed *"every template's mobile lab LCP now 4–8s (P6: 5.6–37s)… a step-change up."*
The clean re-run does not reproduce that. Mobile LCP comes back at **9–26s**, i.e. the same band as
the P6 baselines (pdp was 22.3–23.9s on P6; it reads 23.5s here). The morning's 4–8s mobile figures
were measured during the DNS transition and should be treated as unreliable, not as a P8 win.

**What DOES hold up: desktop.** Desktop LCP is **0.9–1.7s on every template** in both runs, versus
P6's 07-16 read (cart 6.96s, and desktop cart score 40). Desktop scores are up on home (48.5→69) and
pdp (66→78). The desktop improvement is real and reproducible; the mobile one is not established.

Neither run should be over-read on mobile: this store's mobile lab LCP has been documented as
bimodal/lantern-artifact-prone since 06-10. A third read under stable conditions is warranted before
any mobile claim is made either way.

## CLS — the dh8x bug CONFIRMED, and it is bigger than first measured

Per-run spreads (GOOD < 0.1):

| Template | Mobile runs | Desktop runs |
|---|---|---|
| home       | [0.000, 0.000, 0.036] | [0.010, 0.023, 0.034] |
| collection | [0.000, 0.041, **0.158**] | [0.040, **0.146**, **0.351**] |
| pdp        | [0.020, 0.020, 0.051] | [0.004, 0.006] |
| cart       | [0.041, 0.051] | [0.029, **0.682**] |
| brand      | [0.045, 0.046, **2.011**] | [0.042, **0.971**] |

- **brand mobile hit 2.011** — twice the 1.0 seen this morning (a single reflow event can exceed 1.0
  when the element shifts more than once within the session window).
- Fires on **brand, cart and collection**, desktop and mobile. Still race-dependent (1 of 2–3 runs).
- This is the `dh8x` containing-block defect: critical CSS inlines
  `.hero__content__wrapper{position:absolute;…}` while the only rule positioning its ancestor,
  `.brick__block{position:relative}`, ships in the DEFERRED `theme-collection.css`.

## Why the mobile A/B came back inconclusive — and the fix for the method

The chain's Phase 3 A/B (control vs the `dh8x` fix, mobile, n=9 each) returned **control 0/9 fired**,
so the treatment's 0/9 proves nothing — with a zero base rate there is nothing to detect.

The reason is mechanistic, not random. The bug needs the deferred stylesheet to land **after** FCP.
During that phase mobile median LCP was **25.4s**, i.e. very late FCP, so CSS always applied before
first paint and the exposure window never opened. Confirmed against this run's own data:

| PSI brand run (this morning) | CSS end − FCP | fired |
|---|---|---|
| run1 | +609 ms | 1.0000 |
| run2 | +894 ms | 1.0000 |
| run3 | −3448 ms | clean |

**Method correction:** run the A/B on **desktop**, where FCP is fast (LCP 0.9–1.7s) and the window
opens readily — desktop fired 1/2 on brand, 1/2 on cart, 1/3 on collection in this very matrix.
Mobile is the wrong instrument for this bug; local Lighthouse is worse still (1/8, and 0/3 even with
real throttling and a confirmed-open window, because the parser must also have reached section
20-of-24 of a 1.4 MB document inside that window).

## Status

- `dh8x` root cause: verified. Fix built and serving on test theme `142428438627` (`t/115`):
  `/*dh8x*/.brick__block{position:relative}` appended to `snippets/critical-css.liquid`.
- Decisive desktop A/B: running.
- Cart shifts are a SEPARATE bug (unsized footer BIR-certificate `<img loading="lazy">`), not dh8x.
- Cleanup owed: delete the three `CLS-AB-*` unpublished themes when the experiment concludes.
