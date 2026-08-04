# PSI matrix — P8-LIVE launch day (2026-08-05) vs 07-16 pull and 06-10 baseline

**Context:** P8 (theme `141168312419`) published to live **2026-08-05 00:28 MNL** (a7av.7). This is the first
matrix where the bare URL = Pipeline 8. Run ~17h post-launch.

**Methodology:** `scripts/psi-baseline-matrix.py` patched to a single `p8-live` theme (bare URLs), n=3 target,
c=3 → then two serial retry passes. PSI lab was unstable all afternoon (`FAILED_DOCUMENT_REQUEST /
net::ERR_CONNECTION_FAILED` on ~50% of first attempts — suspected origin strain from the faceted-URL crawler
flood, bd `8ile`). Final coverage **25/30 cells**: n=3 everywhere except home-mobile n=1, collection-mobile n=2,
pdp-mobile n=2, home-desktop n=2. Raw: `/tmp/psi-baseline-20260805/` + `summary-aggregated.json` at run time.

## Score — three-way (P6 06-10 baseline → P6 07-16 → P8-live 08-05)

| Template | Mob 06-10 | Mob 07-16 | **Mob P8** | Desk 06-10 | Desk 07-16 | **Desk P8** |
|---|---|---|---|---|---|---|
| home       | 40 | 41 | **59** (n=1) | 58 | 59 | **48.5** (n=2, CLS/TBT-dragged) |
| collection | 37 | 49 | **49.5** | 68 | 65 | **78** |
| pdp        | 35 | 36 | **66** | 77 | 68 | **66** |
| cart       | 33 | 38 | **53** | 56 | 40 | **93** |
| brand      | 44 | 36 | **41** | 59 | 66.5 | **75** |

## Mobile lab LCP — three-way

| | home | collection | pdp | cart | brand |
|---|---|---|---|---|---|
| P6 06-10 | 5.6s | 11.9s | 23.9s | 30.8s | 5.1s |
| P6 07-16 | 5.55s | 5.59s | 22.30s | 36.99s | 34.40s |
| **P8 08-05** | **8.4s** (n=1) | **7.4s** | **6.5s** | **7.3s** | **4.1s** |

Desktop lab LCP today: **0.7–1.7s on every template** (P6 07-16 cart was 6.96s).

## CLS — the launch regression class (per-run spreads, GOOD < 0.1)

| Template | Mobile runs | Desktop runs | Shifting element (from raw Lighthouse) |
|---|---|---|---|
| home       | [0.000] | [0.038, **0.497**] | main `shopify-section` + header desktop bar |
| collection | [0.028, 0.042] | [0.047, 0.096, **0.308**] | main collection section; LoyaltyLion notif micro-shifts |
| pdp        | [0.000, 0.018] | [0.013, 0.015, **0.591**] | `div.product-page > .grid__item` (main grid) |
| cart       | [0.033, **0.133, 0.419**] | [0.001, 0.054, **0.637**] | `__recent_products` section (client-injected), footer, glider |
| brand      | [0.041, **1.005, 1.009**] | [0.012, 0.039, **1.720**] | `brick__block__video > hero__content__wrapper` (yt-facade video hero) |

**8 of 10 templates exceeded 0.1 in at least one run.** For contrast: the 07-16 matrix (including the P8-dev
preview cells) was "CLS clean across all 20 cells, max 0.045" — this instability appeared **between Jul 16 dev
and the Aug 5 live state**, i.e. in the launch-window changes (team's final template edits incl. the brand video
hero; rails/recent-products wiring; CSS-deferral interactions; LimeSpot/STKY/Appikon uninstalls).

**Root-cause pattern (CORRECTED 2026-08-05 PM — the original attribution in this row was wrong; see below).**
The named elements are the *representative* (largest-moving) nodes Lighthouse reports for each shift event, NOT
the causes. Bimodal per-run values = timing decides whether the lab catches the shift window; real users on slow
loads hit the same window. bd: `hairmnl-theme-dh8x`.

### Attribution correction — the brand "video hero" is a victim, not a cause

Investigated 2026-08-05 PM. Evidence from the raw Lighthouse JSONs:

1. In the two bad mobile runs the page has **exactly one** shift event, `score = 1.0000` (the per-event cap),
   with the yt-facade wrapper as representative node; every other shift is ≤0.004. The clean run (0.041) has
   **12 small shifts and no video-hero event at all.** So it is one binary, race-dependent, page-wide event.
2. That node's final position is **y≈13554 (mobile) / 9177 (desktop)** — far below the viewport, and the video
   hero is **section 20 of 24** on the page. An element that never enters the viewport cannot itself generate
   viewport impact; Lighthouse scores the whole *event* and labels it with the biggest mover. The 1.0 therefore
   describes a **page-wide reflow**, not a video-hero reservation gap.
3. `unsized-images` **passes** (0 items) and `render-blocking-resources` is **0** — images are correctly sized;
   all layout CSS is deferred (`media="print"` → `onload this.media='all'`, with `<noscript>` fallbacks).
4. The inlined critical CSS (`snippets/critical-css.liquid`) contains `.hero__content__wrapper{position:absolute}`
   but **no** `.brick__section` / `.brick__block` / `.use_screen_*` rules, so brick sections are sized only once
   the deferred sheet lands and `preventOverflow()/doubles()` runs (`assets/theme.dev.js:223-251`), which sets
   `min-height` from measured content. `--one-fifth` is JS-set (`theme.dev.js:156`) but *does* have a `20vh`
   fallback in critical CSS, so that variable is not the trigger.
5. **Hypothesis tested and falsified:** "sections above the hero collapse to 0 because their content is absolutely
   positioned." There are **zero** `hero__content__wrapper` and **zero** `use_screen_*` elements above the brick
   section — all 7 and 2 occurrences respectively sit at or below it.

**Consequence:** the fix the ticket originally prescribed (aspect-ratio/min-height on `.brick__block__video`)
would be a **placebo** — it cannot move this CLS. Not shipped, deliberately.

**Still unidentified:** which content produces the single page-wide reflow. Remaining prime suspect is the
deferred-CSS swap relayouting the whole 1.4 MB / 24-section document after first paint. Confirming it needs an
A/B (critical-CSS coverage for above-the-fold collection layout, or making the core sheet render-blocking) —
which needs a **P8 test theme that no longer exists post-cutover** (see Blocked, below).

## Field (real users) — day-1 reads

- **Mobile RUM (GA4 web-vitals pipeline SURVIVED cutover, events flowing):** sitewide LCP **85.9% good** /
  6.9% poor (7d context 87.9%); **/products/ LCP 87.7% good** (vs 88.7% pre-launch post-fix window — held);
  CLS **94.7% good**; INP **86.3% good**. No user-facing launch shock in day-1 mobile data (small n, launch-day mix).
- **Field CLS on the lab-flagged pages is the watch item** — /collections/davines 9/9 good and /cart 75% good
  day-1, but n is tiny; the lab shift-window will surface in the field tail as volume accumulates.
- **Desktop RUM is POISONED** by a JS-executing crawler hammering faceted `/collections/<h>/<tag>+<tag>` URLs
  since launch: 76,865 desktop LCP events/24h on faceted paths (one URL: 10,215 events = ~90% of its 7d total),
  ~72% poor/NI, plus ~215K/day web-pixels `importScripts` errors. Excluded from all reads above. bd `8ile`.
- **CrUX origin lock (Jul 5 – Aug 1 window = pure P6 era, the bar P8 must beat when the window turns over):**
  - PHONE: LCP p75 **1803ms** (86.6% good) · CLS p75 **0.06** (88.0% good) · INP p75 **161ms** (82.8% good) · TTFB 707ms
  - DESKTOP: LCP p75 **1607ms** (88.8% good) · CLS p75 **0.04** (86.7% good) · INP p75 **103ms** (89.5% good) · TTFB 426ms
  - Re-check ~2026-09-02 when the 28d window is majority-P8.

## Other launch-day signals

- `themeVendor is not defined` (556/day) — from the OLD theme's asset path (`/t/104/`); stale-cache transition
  artifact, live P8 (`/t/111/`) loads vendor.js→theme.js correctly. Decays on its own; re-check in a few days.
- Cart/PDP/desktop LCP transformation is real and big: the BOGOS glider no longer wins lab LCP on P8's cart
  (mobile 37s→7.3s, desktop 6.96s→0.9s, desktop cart score 40→93).

## Key findings

1. **P8-live lab perf is a step-change up**: every template's mobile lab LCP now 4–8s (P6: 5.6–37s, with pdp
   22s and cart 37s artifacts); desktop LCP sub-2s everywhere; desktop scores up on 4/5 templates. The P8
   eager-LCP pipeline + native sections deliver what the June dev numbers promised.
2. **One real regression shipped: the CLS instability class** (see table). It was NOT present in the Jul-16 dev
   matrix. **It is NOT a per-element reservation gap** — see the attribution correction above: on brand it is a
   single page-wide reflow event scoring the 1.0 cap, for which the video hero is only the representative node.
   bd `dh8x` (P1), now re-scoped to "find the page-wide reflow trigger", blocked on a P8 test theme.
3. **Field day-1 mobile is healthy** — no launch shock; RUM pipeline confirmed alive on P8.
4. **Desktop field data unusable until the crawler flood is filtered** (bd `8ile`) — likely also the cause of
   the PSI lab instability during this run.
5. home-mobile (n=1, 8.4s LCP) and home-desktop (score 48.5, TBT 1115ms) warrant a clean re-run once the
   crawler flood settles — do not act on single-run home numbers.

## Blocked — no P8 test surface exists post-cutover

`shopify theme list` (2026-08-05) shows **`Pipeline 8 Working Demo` #141168312419 is now `[live]`**. The former
draft/dev surfaces (`140785582179` "Claude Code", and the P6 backups) are all Pipeline-6-based. There is
currently **no unpublished P8 theme** to test against, so any CLS experiment would have to be run directly on
the live storefront — 17 hours after cutover, on a theme whose CSS-deferral script already caused one live
incident on launch night (a7av.7). Unblock = duplicate the live theme to an unpublished copy and A/B there.

**NOTE: `CLAUDE.md`'s theme table is now stale** — it still names `131664707683` as live and treats
`141168312419` as the dev target. Every "never wide-push to live" rule now applies to `141168312419`.
