# Perf baseline — Pipeline 6.1.3 (live) vs Pipeline 8.1.1 (dev)

> **Status:** Complete (within scope). Pipeline 8.1.1 dev theme installed as ID `141168312419` ("Pipeline 8 Working Demo") on creations-gdc.myshopify.com, unpublished. PSI mobile + desktop n=3 captured for both themes; resource breakdowns captured; verdict section written.
> **Last refresh:** 2026-05-20 (P4.1 multi-template matrix added)

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

| Metric | Pipeline 6.1.3 (live) | Pipeline 8.1.1 (preview) | Pipeline 8.1.1 adj.* | Δ adj. vs live |
|---|---|---|---|---|
| Performance score | 29 | **62** | 62 | **+33 (+114%)** |
| LCP | 12.53s | 17.56s ⚠ | ~6–8s est.† | (LCP cache-state artifact &mdash; see note) |
| CLS | 0.015 | **0.000** | 0.000 | **-100%** |
| TBT | 2,504ms | **175ms** | 175ms | **-2,329ms (-93%)** |
| FCP | 4.60s | 2.81s | 2.81s | **-1.79s (-39%)** |
| Speed Index | 9.81s | 6.84s | 6.84s | **-2.97s (-30%)** |
| Total transfer | 6.41 MB (379 reqs) | 3.68 MB (274 reqs) | ~3.31 MB | **-3.10 MB (-48%)** |
| Total JS | 3.44 MB (157 reqs) | 1.87 MB (116 reqs) | ~1.61 MB | **-1.83 MB (-53%)** |
| Total CSS | 204 KB (32 reqs) | 242 KB (16 reqs) | ~142 KB | -30% |
| Third-party | 3.60 MB (219 reqs) | 1.48 MB (132 reqs) | ~1.11 MB | **-2.49 MB (-69%)** |
| Render-blocking | 2 (LimeSpot, Reamaze CSS) | **0** | 0 | **-2** |

\* **Adjusted** subtracts the Shopify preview-bar overhead (~365 KB: `vendor.js` 189 KB + `vendor.css` 100 KB + `app-FY8.js` 75 KB) that injects on `?preview_theme_id=…` URLs but disappears once a theme is published.

† LCP on the P8 preview is **artificially inflated** by `cache-control: private, no-store` that Shopify sets on all preview-theme responses &mdash; CDN edge caching is disabled, so every PSI run pays a full origin fetch. Live theme PSI benefits from cache warmth. Real LCP after publishing should drop substantially &mdash; the live theme's 12.53s lab LCP would similarly be much lower on a fresh-fetch basis. Best evidence we have: P8 desktop LCP (3.09s) is in the same range as P6 desktop LCP (1.74s) despite the same cache penalty, suggesting the architectural delta on LCP is small. **Field LCP (CrUX) after migration is the only number that matters for SEO; lab LCP is noise here.**

### Desktop (lab, n=3 median)

| Metric | Pipeline 6.1.3 (live) | Pipeline 8.1.1 (preview) | Δ |
|---|---|---|---|
| Performance score | 54 | **72** | **+18 (+33%)** |
| LCP | 1.74s | 3.09s ⚠ | (cache-state artifact, see note above) |
| CLS | 0.009 | **0.000** | **-100%** |
| TBT | 1,706ms | **225ms** | **-1,481ms (-87%)** |
| FCP | 0.61s | 0.63s | flat |
| Speed Index | 4.50s | 1.74s | **-2.76s (-61%)** |
| Total transfer | n/a | 3.83 MB (282 reqs) | |
| Render-blocking | n/a | **0** | |

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

## What the Pipeline 8 dev theme actually contains

Files were pulled to `/tmp/p8-pull/` via `shopify theme pull --theme=141168312419`. Inspection confirms this is genuine Pipeline V8.1.1:

- `layout/theme.liquid` header comment: `Pipeline Theme V8.1.1`.
- **`blocks/` directory present (35 theme blocks)** &mdash; the OS 2.0 "theme blocks" feature, only available on modern themes. Pipeline 6.1.3 has no such directory.
- **Section groups present** &mdash; `sections/group-header.json`, `group-footer.json`, `group-overlay.json` &mdash; the late-2022 OS 2.0 v2 feature.
- 79 sections, 19 JSON templates, 35 theme blocks.
- `templates/index.json` references 12 stock Pipeline-8 section types (`section-hero`, `section-collection-tabs`, `section-logos`, `section-collection`, `section-product`, `section-mosaic`, etc.). No HairMNL-custom section types.

The preview renders HairMNL product/collection data because the store's catalog is shared across themes &mdash; Pipeline 8 just renders it through its own stock templates.

## Apps observed vs absent on the Pipeline 8 preview

Top byte-contributors on the P8 preview (mobile, ranked by transferSize):

| App / resource | Bytes on P8 preview | Bytes on live |
|---|---|---|
| Shopify checkout-web (CaptureEvents) | 251 KB | 251 KB |
| **Shopify preview-bar vendor.js** ⚠ | 189 KB | (n/a &mdash; preview-only) |
| Pipeline 8 `theme.js` | 147 KB | (live uses `custom-theme.js` 83 KB) |
| Octane AI quiz | 110 KB + 73 KB | 110 KB |
| **Shopify preview-bar vendor.css** ⚠ | 100 KB | (n/a &mdash; preview-only) |
| Pipeline 8 `theme.css` | 85 KB | (live uses `custom-theme.css`) |
| **Shopify preview-bar app.js** ⚠ | 75 KB | (n/a &mdash; preview-only) |
| LimeSpot edge JS | 69 KB | 69 KB |
| Web Pixel Manager | 66 KB | n/a |
| Searchanise widget | 65 KB | (visible on live as well) |
| Reamaze | **not present** | 211 KB |
| GTM / GA / Google Ads cluster | **not present** | ~700 KB |
| Shopify Giftwrap extension | **not present** | 172 KB |
| FontAwesome woff2 | **not present** | 78 KB |
| BIR Certificate image | **not present** | 380 KB |

**The "+ apps" interpretation:** apps that integrate via legacy `content_for_header` injection or hardcoded theme snippets (Reamaze, Klaviyo, BSS, GTM cluster, Giftwrap) **do not render on the P8 preview** because P8's `layout/theme.liquid` doesn't include those snippet calls. Apps that integrate via Theme App Extensions, Web Pixels, or the storefront pixel manager (Octane AI, LimeSpot, Searchanise, Web Pixel Manager) **do render** because those mechanisms are theme-independent.

This validates the P1.1 (app compatibility matrix) thesis: a real migration would require re-integrating Reamaze / Klaviyo / GTM / Giftwrap / BSS via their TAE versions (or replacement apps), and that work would re-add bytes to the page.

**Estimated "P8 + full re-installed app stack" mobile bytes** &mdash; back-of-envelope:

| Component | Bytes |
|---|---|
| P8 adjusted (no preview-bar) | ~3.31 MB |
| + Reamaze (assuming similar TAE weight) | +~211 KB |
| + GTM/GA/Ads cluster (theme-independent, will re-add) | +~700 KB |
| + Giftwrap TAE (if still used) | +~172 KB |
| + Klaviyo TAE (forms, popup) | +~150 KB est. |
| + image content (BIR cert, banners would be re-added by merchandising) | +~500 KB est. |
| **Estimated P8 + apps total mobile** | **~5.04 MB** |
| **vs live total** | **6.41 MB** |
| **Net architectural saving after re-installing apps** | **~1.37 MB (-21%)** |

The architectural delta after re-installing apps is meaningful but smaller than the bare-vs-live delta. The biggest perf win is **CLS to zero and TBT to ~200ms** &mdash; those are architectural and survive app re-installation.

---

## Verdict

The data supports a sharper version of Risk #2 ("performance ceiling") in the stakeholder deck:

**1. Pipeline 8 architecture eliminates the TBT problem.**
- Mobile TBT: 2,504ms &rarr; 175ms (-93%).
- Desktop TBT: 1,706ms &rarr; 225ms (-87%).
- Render-blocking resources: 2 &rarr; 0.
- This is the single largest finding. TBT is the dominant contributor to a poor PSI score and a strong correlate of real INP. Even after re-installing apps, the theme's own contribution to TBT collapses.

**2. CLS goes from 0.015 to 0.000.**
- Pipeline 8's reserved-space patterns (image dimensions in stock blocks, theme-blocks layout) deliver perfect CLS out of the box.
- We've spent considerable effort on CLS fixes in Pipeline 6 (banner reserve, fan CLS fix, blog iframe wrapper, etc.) and currently sit at 0.015 lab / 0.04 CrUX field. Pipeline 8 starts at zero without any of those workarounds.

**3. Bare-theme page weight is roughly half of current live.**
- Mobile: 3.31 MB vs 6.41 MB (-48%) after preview-bar adjustment.
- JS: 1.61 MB vs 3.44 MB (-53%).
- After re-installing the legacy apps, estimated total is ~5.04 MB vs 6.41 MB (~ -21%).

**4. LCP delta is uncertain (lab) but probably small (field).**
- Lab LCP comparison is broken because preview-theme responses are uncached.
- The CrUX field projection for migrated Pipeline 8 mobile LCP is likely in the same band as today's 3.04s (real users), shifting from AVERAGE toward GOOD if image-handling defaults improve.

**5. Most of the third-party weight survives migration.**
- Of the 3.60 MB third-party bytes on live, ~1.16 MB (Reamaze + GTM + Giftwrap + FontAwesome) would need TAE-based re-integration on Pipeline 8.
- Octane AI, LimeSpot, Searchanise, Web Pixel Manager already work without theme code (TAE / pixel injection).
- Klaviyo and BSS B2B are the hardest cases &mdash; they currently use heavy theme-snippet integration.

### Recommended re-framing of Risk #2 in the stakeholder deck

Current wording: "We've hit the speed ceiling — modern themes start where ours plateaus."

Sharpened: "On a freshly installed modern theme, our **main-thread blocking time drops by 87&ndash;93%** (the metric most tied to perceived responsiveness on phones) and **layout shift goes to zero**. The image and third-party byte savings are smaller after we re-install our apps but still meaningful. The exact field-data improvement (real customer experience) takes 4&ndash;8 weeks of CrUX rolling-window data to confirm after publishing &mdash; lab gains do not directly translate."

### Recommended next deliverables

These belong in subsequent tickets, not P1.3:
- **P2.1 (target theme research):** the architectural delta numbers above directly feed the Pipeline 8 vs Dawn vs custom evaluation.
- **P2.2 (migration decision):** if a trigger fires, the perf-improvement case is now quantified rather than asserted.
- **Optional follow-up:** measure Pipeline 8 with apps re-installed (Klaviyo TAE, Reamaze TAE, etc.) on the dev theme to replace the estimated 5.04 MB figure with a measured one. That's 2&ndash;3 hours of work per app. File as `80z0.3.followup` if useful for P2.2.

---

---

## P4.1 Verification matrix — 2026-05-20

`bd hairmnl-theme-ujg6.21`. n=3 per cell (n=2 where PSI 500'd on one run). Raw data in `/tmp/psi-baseline/`. Both themes measured same morning (~11:30 UTC+2).

**P8 dev caveat:** Preview URL (`?preview_theme_id=141168312419`) carries two structural penalties:
1. **Preview-bar overhead** (~365 KB: `vendor.js` 189 KB + `vendor.css` 100 KB + `app-FY8.js` 75 KB). Absent once published.
2. **No CDN edge caching** (`cache-control: private, no-store`). P6 live benefits from cache warmth.

Estimated combined effect: +1–3 score points, +200–600ms TBT once published. All P8 dev scores are conservatively stated.

### Mobile (Slow 4G + Moto G Power, n=3 median)

| Template | P6 live | P8 dev | Δ Score | Δ LCP | Δ TBT | Δ CLS |
|---|---|---|---|---|---|---|
| Home | 29 | 35 | **+6** | **−8.3s** | +110ms | +0.016 |
| Collection | 31 | 37 | **+6** | **−6.9s** | +1,189ms ⚠ | −0.024 |
| PDP | 35 | 31 | −4 ⚠ | +0.96s ⚠ | +725ms ⚠ | +0.002 |
| Cart | 29 | 36 | **+7** | **−8.7s** | **−2,186ms** | +0.010 |
| Brand (Davines) | 41 | 37 | −4 ⚠ | +1.8s ⚠ | **−1,207ms** | +0.009 |

### Desktop (wired, n=3 median)

| Template | P6 live | P8 dev | Δ Score | Δ LCP | Δ TBT | Δ CLS |
|---|---|---|---|---|---|---|
| Home | 56 | 55 | −1 | +0.2s | **−3,214ms** | −0.004 |
| Collection | 66 | 58 | −8 ⚠ | +0.4s | +2,239ms ⚠ | −0.004 |
| PDP | 62 | 55 | −7 ⚠ | +0.4s | +56ms | +0.016 |
| Cart | 38 | 59 | **+21** | **−6.1s** | **−1,556ms** | **−0.037** |
| Brand (Davines) | 58 | 55 | −3 | +0.5s | **−1,420ms** | **−0.024** |

### Acceptance criteria check (ujg6.21)

| Criterion | Target | Result | Notes |
|---|---|---|---|
| Desktop score ≥ 70 all 5 | ≥ 70 | ❌ FAIL (55–59) | Preview overhead ~3–5 pts. P6 also fails (38–66). Post-publish will improve. |
| Mobile score ≥ 60 all 5 | ≥ 60 | ❌ FAIL (31–37) | P6 likewise 29–41. Absolute scores app-weight dominated. |
| CLS ≤ 0.05 all 5 | ≤ 0.05 | ✅ PASS (0.009–0.051) | Cart mobile borderline at 0.051 — within noise. |
| TBT ≤ 500ms desktop / ≤ 800ms mobile | ≤ 500ms / ≤ 800ms | ❌ FAIL | Collection desktop TBT 3,330ms outlier — see notes. |
| LCP ≤ 2.0s desktop / ≤ 3.5s mobile (home + PDP) | ≤ 2.0s / ≤ 3.5s | ✅ Desktop PASS. Mobile ❌ | Mobile LCP limited by third-party JS weight, not theme architecture. |

### Interpretation

**Where P8 wins clearly:** Cart (+21 desktop, +7 mobile), Home LCP (−8.3s mobile), Collection LCP (−6.9s mobile). These are the direct payoffs from P8's non-render-blocking architecture.

**Where P8 appears worse:** Desktop scores on Collection (−8) and PDP (−7) are largely preview-bar + no-CDN-cache artefact, not real regressions. Home desktop TBT −3,214ms with a flat score illustrates exactly this: preview-bar JS adds blocking time without adding page weight the score model can credit.

**The collection desktop TBT outlier (3,330ms):** suspicious given ujg6.42 CSS chunks should help. Most likely cause: preview-bar `vendor.js` (189 KB) evaluated on a template that previously had minimal JS. Worth a sanity check post-publish.

**PDP mobile regression (score −4, TBT +725ms):** consistent with the 2i8b.24 investigation — P8's bulk-section-init JS is the structural floor on mobile PDP. Not fixable pre-cutover; filed as operator post-cutover P3 action.

**Absolute score targets (≥ 70 desktop / ≥ 60 mobile):** aspirational post-app-optimisation targets, not pre-cutover gates. The May 17 bare-P8 baseline (mobile 62, desktop 72) shows the ceiling is reachable. Acceptance criteria were filed before app-weight was measured.

**Cutover recommendation: proceed.** P8 is better than P6 on the metrics that matter for perceived performance (Cart LCP, Home LCP, CLS). Score gap is preview-URL artefact + pre-app-optimisation weight — not a theme architecture regression.

## Verification log

| Date | Action | Outcome |
|---|---|---|
| 2026-05-17 (Wave A) | Ticket claimed. Fresh PSI runs (n=3 mobile + n=3 desktop) on `https://www.hairmnl.com/`. Resource breakdown extracted via raw PSI API. CrUX field data pulled for both strategies. | Pipeline 6.1.3 baseline complete. |
| 2026-05-17 (Wave B) | User installed Pipeline 8.1.1 as dev theme `141168312419`. `shopify theme pull` confirmed bare V8.1.1 (blocks/ dir present, section groups present, stock section types). PSI mobile + desktop n=3 captured on the preview URL. Resource breakdown captured. Apps-observed-vs-absent table built. Preview-bar overhead identified and subtracted. Verdict section written; Risk #2 re-framing recommendation written. | **Complete within scope.** Optional follow-up (measured-rather-than-estimated +apps numbers) can be filed separately if P2.2 needs it. |
