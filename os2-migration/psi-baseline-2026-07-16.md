# PSI matrix — comparison (2026-07-16 vs 2026-06-10)

`scripts/psi-baseline-matrix.py --runs=3 --concurrency=3`, 59/60 OK (1 brand-desktop run failed), 16.2 min. First matrix since the 2026-06-10 PDP LCP fixes (zlwx/y79d) and the 06-16 shop-the-guide launch. Raw: `/tmp/psi-baseline/summary.{json,md}` at run time.

## P6-live — score (06-10 → today)

| Template | Mobile 06-10 | Mobile today | Desktop 06-10 | Desktop today |
|---|---|---|---|---|
| home       | 40 | 41 | 58 | 59 |
| collection | 37 | **49** | 68 | 65 |
| pdp        | 35 | 36 | 77 | 68 |
| cart       | 33 | 38 | 56 | **40** |
| brand      | 44 | 36 | 59 | 66.5 (n=2) |

## P6-live mobile LCP (06-10 → today)

| | home | collection | pdp | cart | brand |
|---|---|---|---|---|---|
| 06-10 | 5.6s | 11.9s | 23.9s | 30.8s | n/a |
| today | 5.55s | **5.59s** | 22.30s | 36.99s | 34.40s |

## Key findings

1. **CLS clean across all 20 cells** (P6 mobile max 0.045; nothing near 0.1) — the CLS program holds 5 weeks on, including through the shop-the-guide launch.
2. **PDP fix: lab flat, FIELD improved.** Lab median ~22.3s unchanged — the documented render-start/lantern bimodality (y79d closeout) still dominates the bare-URL lab cell. But **GA4 RUM field LCP on /products/ mobile: 81.0% good (May10–Jun09, pre-fix) → 88.7% good (Jun11–Jul15, post-fix), +7.7pts** — the featured-first/eager fix works where it matters. Do not chase the lab number further; it's an attribution artifact, not user experience.
3. **Cart (37s) + brand (34.4s) mobile lab LCP = the annotated artifact class.** Cart is the known empty-cart BOGOS-glider artifact (wwni). Brand joining at 34.4s is new — same late-paint signature; check the brand template's promo elements if it persists next run. Field cart LCP was 79% good at last check.
4. **Collection mobile genuinely improved** (37→49 score, LCP 11.9→5.6s) — second consecutive good read; upgrading from "favorable variance" to "probably real."
5. Desktop: cart 56→40 (glider on desktop too, LCP 6.96s), pdp 77→68 (within the historical variance band — watch, don't act). P8-dev collection LCP 18.6s is dev-theme drift (P8 stream item, not live-relevant).
