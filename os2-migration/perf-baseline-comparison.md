# Perf baseline — Pipeline 6.1.3 (live) vs Pipeline 8.1.1 (dev)

> **Status:** Partial. The current-theme baseline is populated. The Pipeline 8 dev-theme column is **blocked on a one-time user action** — see the [Pipeline 8 install gate](#pipeline-8-install-gate) section. The doc updates in place when those numbers land.
> **Last refresh:** 2026-05-17

---

## Why this doc exists

Ticket: `hairmnl-theme-80z0.3` (P1.3 of the OS 2.0 / Pipeline 8+ migration readiness epic).

We need to know how much of HairMNL's mobile-perf gap is **theme architecture** (fixable by migrating) vs **the apps we'd reinstall on any theme** (not fixable by migrating). The answer reshapes Risk #2 ("performance ceiling") in the stakeholder brief from a qualitative claim into a number.

The methodology: measure the current Pipeline 6.1.3 live theme, install Pipeline 8.1.1 as a separate **unpublished** dev theme on the same store, run the same measurements, then compare bare-Pipeline-8 vs Pipeline-8-plus-our-apps to isolate the two contributions.

## Methodology

| Variable | Setting |
|---|---|
| Store | `creations-gdc.myshopify.com` (production) |
| Live theme | `131664707683` &mdash; Pipeline 6.1.3 ("Pipeline 6 - Fix share image"). **No changes.** |
| Dev theme | Pipeline 8.1.1 installed as a **fresh unpublished theme**. Branding (logo, colors, fonts) configured to match HairMNL via theme settings only &mdash; no code customizations. |
| Page under test | Homepage `https://www.hairmnl.com/` (live) and the equivalent preview URL on the dev theme. |
| PSI tool | PageSpeed Insights API (Lighthouse 13.x) via `scripts/run-psi.sh`. |
| Samples | n=3 per cell, median reported. Single-run numbers in footnotes when median is unstable. |
| Throttling | PSI defaults: mobile = Moto G Power on Slow 4G; desktop = wired. |
| Field data | CrUX p75, 28-day rolling window where available. |

### Metric definitions (PSI / Lighthouse)
- **LCP** &mdash; Largest Contentful Paint. When the main content visually loads.
- **CLS** &mdash; Cumulative Layout Shift. How much things jump around during load (0 = none, &lt;0.1 GOOD).
- **INP** &mdash; Interaction to Next Paint. Responsiveness to clicks/taps (field-only, hard to measure in lab).
- **FCP** &mdash; First Contentful Paint. When anything visible first appears.
- **TBT** &mdash; Total Blocking Time. Time the main thread is blocked &gt;50ms (lab-only proxy for INP).
- **TTFB** &mdash; Time To First Byte. Server response delay.

---

## Side-by-side scores

### Mobile (lab, Lighthouse 13.x, Slow 4G + Moto G Power, n=3 median)

| Metric | Pipeline 6.1.3 (live) | Pipeline 8.1.1 (bare) | Pipeline 8.1.1 + our apps | Δ "modern theme alone" | Δ "after re-installing apps" |
|---|---|---|---|---|---|
| Performance score | **29** | **TBD** | **TBD** | | |
| LCP | **12.53s** | **TBD** | **TBD** | | |
| CLS | **0.015** | **TBD** | **TBD** | | |
| TBT | **2,504ms** | **TBD** | **TBD** | | |
| FCP | **4.60s** | **TBD** | **TBD** | | |
| Speed Index | **9.81s** | **TBD** | **TBD** | | |
| Total transfer size | **6.41 MB** (379 reqs) | **TBD** | **TBD** | | |
| Total JS transfer | **3.44 MB** (157 reqs) | **TBD** | **TBD** | | |
| Total CSS transfer | **204 KB** (32 reqs) | **TBD** | **TBD** | | |
| Third-party bytes | **3.60 MB** (219 reqs, **56% of total**) | **TBD** | **TBD** | | |
| Render-blocking resources | **2** (LimeSpot storefront, Reamaze cookie CSS) | **TBD** | **TBD** | | |

Single-run variance was wide (run 1+2 score 29 / LCP 12.5s / TBT 2.5s vs run 3 score 33 / LCP 8.1s / TBT 5.2s). Reported value is the median.

### Desktop (lab, n=3 median)

| Metric | Pipeline 6.1.3 (live) | Pipeline 8.1.1 (bare) | Pipeline 8.1.1 + our apps | Δ "modern theme alone" | Δ "after re-installing apps" |
|---|---|---|---|---|---|
| Performance score | **54** | **TBD** | **TBD** | | |
| LCP | **1.74s** | **TBD** | **TBD** | | |
| CLS | **0.009** | **TBD** | **TBD** | | |
| TBT | **1,706ms** | **TBD** | **TBD** | | |
| FCP | **0.61s** | **TBD** | **TBD** | | |
| Speed Index | **4.50s** | **TBD** | **TBD** | | |

### Field (CrUX p75, 28-day rolling — real users on hairmnl.com)

| Metric | Mobile (today) | Mobile category | Desktop (today) | Desktop category |
|---|---|---|---|---|
| LCP | **3,039ms** | AVERAGE | **2,412ms** | FAST |
| CLS | **0.04** | FAST | **0.019** | AVERAGE |
| INP | **240ms** | AVERAGE | **146ms** | FAST |
| FCP | **2,631ms** | AVERAGE | **2,238ms** | AVERAGE |
| TTFB | **897ms** | AVERAGE | **412ms** | FAST |

Pipeline 8 field data is **not measurable** — the dev theme is unpublished and never serves real users. CrUX projections for a migrated theme can only be inferred from the lab delta between bare-P8 and current-live.

> **Important framing note:** the field data above is the ground truth for SEO ranking and real customer experience. Mobile LCP 3.0s, INP 240ms, CLS 0.04 are all within Google's pass/needs-improvement thresholds; CLS specifically is in the FAST band. The lab numbers are alarming because PSI emulates a Moto G Power on Slow 4G — a deliberate worst-case. **The migration case must be built on field-data improvement potential, not lab-number cosmetic gains.**

---

## Historical lab measurements (Pipeline 6.1.3, for trend context)

Drawn from the perf-work cycles over April–May 2026. Use as a sanity check against today's fresh sample.

| Date | Source | Mobile score | Mobile LCP | Mobile TBT | Mobile CLS | Desktop score | Desktop TBT |
|---|---|---|---|---|---|---|---|
| 2026-04-26 SoD | Lab baseline | 26 | 11.8s | 4,340ms | 0.043 | 55 | 5,600ms |
| 2026-04-26 EoD | After Searchanise defer + Hotjar removal + Judge.me dedup | 26 | 12.7s | 4,320ms | 0.015 | 52 | 2,910ms |
| 2026-04-27 09:42 | After BSS gating, font self-host, Klaviyo defer | 36 | 6.3s | 1,530ms | 0.047 | n/c | n/c |
| 2026-05-02 | After 9g9 theme-check fixes | 31 (med n=2) | 9.17s | 5,010ms | 0.041 | 57.5 | 2,340ms |
| 2026-05-03 | n=4 follow-up, no deploys | n/c | 14.2s med | 4,155ms med | 0.035 | n/c | n/c |
| 2026-05-17 | **This baseline (n=3)** | **29** | **12.53s** | **2,504ms** | **0.015** | **54** | **1,706ms** |

Mobile TBT held flat to slightly improved vs 05-03 (2,504 vs 4,155 median). Desktop TBT improved further (1,706 vs 2,340 May 2). The Slow-4G / Moto-G-Power lab profile continues to penalize hairmnl.com heavily on LCP for the same reason: heavy third-party JS payload (see below).

---

## Early read on the data (before Pipeline 8 measurement)

Even without the dev-theme numbers, the current-live baseline already points the migration case:

**1. Third-party app weight dominates.** Of 6.41 MB total mobile transfer, 3.60 MB (**56%**) is third-party. Top contributors by transferSize:

| Resource | Bytes | Owner |
|---|---|---|
| BIR Certificate image | 380 KB | Shopify CDN (our content) |
| Checkout-web CaptureEvents | 251 KB | Shopify checkout (theme-independent) |
| Reamaze chat | 211 KB | Reamaze |
| GTM / GA / Google Ads tags (4 scripts) | ~700 KB | Google Tag Manager |
| Shopify Giftwrap extension | 172 KB | Shopify giftwrap app |
| Octane AI quiz | 111 KB | Octane AI |
| `custom-theme.js` (our code) | 83 KB | HairMNL theme |
| FontAwesome woff2 | 78 KB | bootstrapcdn (legacy dep) |
| LimeSpot edge JS | 69 KB | LimeSpot |

The theme's own JS payload (`custom-theme.js` ~83 KB) is a small fraction of total. **A theme migration will not move the needle on third-party weight unless we also re-evaluate which apps are installed.**

**2. Render-blocking is mostly handled.** Lighthouse 13's `render-blocking-insight` finds only 2 items: LimeSpot's `storefront.min.js` and Reamaze's `nova-cookie.css`. The prior Phase 2 defer work (storepickup, BSS, tiny content, judge.me, Klaviyo) is paying off — both remaining blockers are third-party, not theme code.

**3. Field data is healthier than lab data suggests.** Mobile CrUX p75 is LCP 3.04s, INP 240ms, CLS 0.04. These are AVERAGE or FAST on Google's CrUX thresholds. **The "performance ceiling" risk in the stakeholder brief should be re-read against the field number, not the Slow-4G lab number.** A migration would improve lab numbers (cosmetic for the score badge) but the field gain depends mostly on what we do about third-party JS — which is largely orthogonal to theme version.

This shifts the expected interpretation of the Pipeline 8 measurement once it lands:
- **If bare-P8 mobile LCP < 4s:** confirms ~8s of LCP gap is theme architecture — strong migration case.
- **If bare-P8 mobile LCP ≈ live LCP:** confirms the lab gap is third-party-driven — migration case must lean on other factors (TAE compatibility, merchandiser productivity, etc.) rather than perf.
- **If P8-with-apps mobile LCP ≈ live LCP:** strongest signal yet that perf improvement requires app rationalization, not theme migration.

---

## Pipeline 8 install gate

The dev-theme columns above stay TBD until **one of the following** happens:

### Option A — User-driven Shopify admin install (recommended, ~5 min)
1. Shopify admin → **Online Store → Themes → Theme library**.
2. **Add theme → Shopify Theme Store**. Search **Pipeline**.
3. On the Pipeline theme page, click **Try theme** (free for existing licensees per Groupthought policy &mdash; verified 2026-05-16).
4. The theme appears in *Theme library* as an **Unpublished** Pipeline 8.1.1.
5. **Do not publish.** Note the theme ID (it appears in the URL when you click *Customize*).
6. Hand the theme ID back to this session.

I will then:
- Run `shopify theme pull --theme=<ID> --store=creations-gdc.myshopify.com` to fetch the files locally for inspection.
- Use the Shopify admin **Preview** URL to run PSI (n=3 mobile + n=3 desktop) against the bare theme.
- Walk through minimum branding config (logo, primary color, fonts) via theme settings.
- Install the same apps we run on live (Klaviyo, Reamaze, LimeSpot, Judge.me, Smart SEO, etc.) on the dev theme, then re-run PSI to get the "+ our apps" column.

### Option B — Groupthought zip download (~10 min)
1. Groupthought customer portal → **My account → Themes → Pipeline → Download latest (.zip)**.
2. Place the zip at `~/Downloads/Pipeline-8.1.1.zip` (or any path you tell me about).
3. I unzip and `shopify theme push --unpublished --store=creations-gdc.myshopify.com` to install.

Option A is preferred &mdash; it's the canonical Shopify install path, ensures licensing is recorded with the merchant account, and the theme appears in admin alongside our existing themes.

### What I cannot do autonomously
- Download Pipeline 8 from Groupthought (paywalled to your licensee account).
- Install themes to your Shopify store (requires your admin auth in the CLI session).
- Configure theme settings in the admin UI without a live human session.

---

## What this doc will look like once unblocked

Once Pipeline 8 is installed and configured to minimum branding:
1. Side-by-side score tables fully populated.
2. Δ columns calculated.
3. Verdict section interpreting the gap: how much is theme architecture vs apps.
4. Recommendation for whether Risk #2 in the stakeholder deck should be sharpened from "performance ceiling, capped 75–80" to a specific quantified claim.
5. Per-resource breakdown (which scripts / styles / images contribute the most bytes on each theme), to feed P2.1's target-theme recommendation.

---

## Verification log

| Date | Action | Outcome |
|---|---|---|
| 2026-05-17 | Ticket claimed. Fresh PSI runs (n=3 mobile + n=3 desktop) on `https://www.hairmnl.com/`. Resource breakdown extracted via raw PSI API. CrUX field data pulled for both strategies. Doc fully populated for the Pipeline 6.1.3 baseline column; Pipeline 8 install gate shipped as the user-action ask. Early-read interpretation section written. | Pipeline 6.1.3 baseline complete; awaiting Pipeline 8 dev-theme install to complete the comparison. |
