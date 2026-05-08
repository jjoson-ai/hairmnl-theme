---
title: Pre-Phase-1-cutover PSI baselines
date: 2026-05-08
strategy: mobile (Slow 4G, Moto G Power)
source: PageSpeed Insights API v5 via scripts/run-psi.sh
purpose: pre-LimeSpot→Vertex-FBT-cutover reference point
related_beads: hairmnl-vertex-cji.3
---

## Why this exists

Phase 1 of the LimeSpot → Vertex cutover replaces the LimeSpot
"Frequently Bought Together" widget on the PDP and the cart with
Vertex Recommendations Liquid snippets. The architecture perf
contract (§2.6) requires Vertex to add **<50ms TBT** vs the
LimeSpot baseline captured here.

Day 14 review compares post-cutover PSI against these numbers.
If TBT regresses by >50ms median (across 3+ runs), we revert.

## Conditions

- All runs hit live theme `131664707683` ("Pipeline 6 - Fix share image")
- LimeSpot SDK loaded normally (no gating yet)
- Vertex Liquid blocks present but commented out (no rendering)
- Mobile Slow 4G, single CPU throttle 4× (PSI default)
- API was flaky throughout the session (~50% timeout rate);
  collected samples until each URL had n≥3 successful runs

## Per-URL medians

### Homepage — `https://hairmnl.com/`
- n = 3 successful runs
- TBT samples (ms): 2511, 3388, 4211
- LCP samples (s):  6.9, 7.0, 14.9
- Score samples:    19, 31, 32
- **Median TBT: 3,388ms** · Median LCP: 7.0s · Median score: 31

### PDP — `https://hairmnl.com/products/davines-momo-shampoo`
- n = 5 successful runs
- TBT samples (ms): 1561, 2489, 2539, 5774, 6294
- LCP samples (s):  7.0, 7.0, 7.6, 7.6, 7.6
- Score samples:    26, 31, 31, 32, 33
- **Median TBT: 2,539ms** · Median LCP: 7.6s · Median score: 31

### Cart — `https://hairmnl.com/cart`
- n = 4 successful runs
- TBT samples (ms): 1721, 1721, 3339, 4624
- LCP samples (s):  17.6, 18.7, 25.6, 25.6
- Score samples:    25, 25, 26, 29
- **Median TBT: 2,530ms** · Median LCP: 22.2s · Median score: 25.5

## Notes on cart LCP

The 22s cart LCP is misleading. PSI loads `/cart` with no items in
session, so the page renders an empty-cart state. The LCP element
is likely the Shopify "BUY IT WITH" rec card or footer content
that paints late after the product-recommendation API call. This
metric isn't representative of a real-shopper cart load — but it
IS a useful comparison point for the cutover, since the LimeSpot
SDK currently runs on `/cart` regardless of cart state.

## Comparison protocol post-cutover

Day 0 cutover ships → wait ~30 min for CDN edge to warm → re-run
the same three URLs with the same `scripts/run-psi.sh` invocation.
Record at least n=3 successful samples per URL.

**Pass criteria:**
- Median PDP TBT change ≤ +50ms vs 2,539ms baseline (≤2,589ms)
- Median Cart TBT change ≤ +50ms vs 2,530ms baseline (≤2,580ms)
- Median Homepage TBT no regression > +100ms (less critical —
  homepage isn't directly touched by Phase 1)

If pass: continue Day 1–14 monitoring per `MASTER-RUNBOOK.md`.
If fail by >50ms: revert the cutover commit and re-push the four
files; investigate the regression before re-attempting.

## Raw run logs

- `psi-baseline-home-2026-05-08.txt`
- `psi-baseline-pdp-2026-05-08.txt`
- `psi-baseline-cart-2026-05-08.txt`
