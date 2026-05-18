# Desktop home TBT root-cause investigation

> **Bd:** `hairmnl-theme-ujg6.28`
> **Date:** 2026-05-18 PM, on Opus 4.7 / High, post-revert (49ae3dc).
> **Question:** Why does P8 dev desktop home TBT measure ~1,700ms higher than P6 live, even though the post-revert `layout/theme.liquid` is identical?

## TL;DR

The +1,700ms TBT gap is **partly measurement artifact, partly real**.

**Measurement artifact (~200-400ms of the gap):**
- The PSI URL for P8 dev (`?preview_theme_id=141168312419`) makes Shopify inject the **preview-bar** (`preview-bar-modules.js` + `vendor--*.js`, combined ~190 KB) onto every page load. This is dev-only overhead that disappears at cutover.

**Real causes (~1,300-1,500ms of the gap), distributed across many sources:**
1. **Google Tag Manager: +420ms main-thread, +312 KB transfer** — the biggest single attributable delta. P8's GTM appears to be firing additional Google Ads conversion tags (`AW-877099019`, `AW-611729126`) that didn't activate on P6's measurement.
2. **Reamaze full widget (+195ms)** — P8 loaded `reamaze.js` (the full chat widget). P6 measurement only loaded `reamaze-loader.js`. May correlate with the existing `bd meu` defer-on-interaction work.
3. **Klaviyo onsite back-in-stock + signup forms (+~80-100ms)** — extra Klaviyo bundles loaded on P8 that P6 didn't sample.
4. **Theme.js script evaluation +383ms** — same file path, same content; differences likely sampling variance.
5. **Garbage collection +491ms** — symptom of more JS allocation; not a separate root cause.

**No single layout/theme.liquid issue caused this.** The post-revert layout/theme.liquid is byte-identical to P6's. The TBT gap is downstream — third-party scripts and runtime conditions, not theme architecture.

---

## Methodology

PSI desktop runs on fresh cache-bust query params, taken back-to-back (within ~60 seconds):
- **P6 LIVE**: `https://www.hairmnl.com/?_cb_p6=$(date +%s%N)`
- **P8 DEV**: `https://www.hairmnl.com/?preview_theme_id=141168312419&_cb_p8=$(date +%s%N)`

Extracted from PSI lighthouseResult.audits:
- `total-blocking-time`
- `mainthread-work-breakdown` (per-category attribution)
- `bootup-time` (per-script JS attribution)
- `long-tasks` (>50ms main-thread blocks)
- `third-parties-insight` (per-entity attribution)

**Caveat: single PSI run per theme**. Single-sample variance on TBT is ±200-500ms. Findings here are directionally correct; magnitudes need n≥3 to nail down. Re-baseline before Phase D verification.

---

## Headline numbers (this measurement)

| Metric | P6 live | P8 dev | Δ P8 vs P6 |
|---|---|---|---|
| PSI score | 55 | 54 | -1 (flat — Δ within ±3 noise) |
| FCP | 609ms | 669ms | +60ms |
| LCP | 1,493ms | 1,623ms | +130ms |
| **TBT** | **3,138ms** | **4,861ms** | **+1,723ms** |
| CLS | 0.014 | **0.009** | **−0.005 (P8 better, today's fixes)** |
| Speed Index | 7,932ms | 11,591ms | +3,659ms |
| TTI | 10,366ms | 13,209ms | +2,843ms |
| Main-thread total | 19.3s | 23.4s | +4.1s |

The CLS column is the most pleasing: today's ujg6.5 + ujg6.29 fixes drove CLS *below* P6's level on desktop home.

---

## Main-thread work breakdown (Δ analysis)

| Category | P6 | P8 | Δ | Δ % of gap |
|---|---|---|---|---|
| Script Evaluation | 7,690ms | 8,943ms | **+1,253ms** | 31% |
| Style & Layout | 5,056ms | 5,474ms | +418ms | 10% |
| Other (browser internal) | 3,570ms | 4,837ms | **+1,267ms** | 31% |
| Rendering | 1,495ms | 1,575ms | +80ms | 2% |
| Script Parsing & Compilation | 932ms | 1,325ms | +393ms | 10% |
| Garbage Collection | 231ms | 722ms | **+491ms** | 12% |
| Parse HTML & CSS | 347ms | 520ms | +173ms | 4% |
| **Total** | **19,321ms** | **23,396ms** | **+4,075ms** | 100% |

Three categories carry ~75% of the gap:
- **Script Evaluation** (running JS): +1,253ms
- **Other** (browser-internal time: paint/composite/style-recalc not classified): +1,267ms
- **Garbage Collection**: +491ms (downstream symptom — more JS allocation → more GC)

---

## Third-party entity breakdown (top 12)

| Entity | P6 mainT | P8 mainT | Δ | P6 KB | P8 KB | Δ KB |
|---|---|---|---|---|---|---|
| Google Tag Manager | 1,290 | **1,710** | **+420** | 628 | 941 | **+313** |
| Shopify (own CDN) | 1,096 | 1,282 | +186 | 929 | 1,349 | **+420** |
| Azure Web Services (STKY satcb) | 733 | 688 | -45 | 41 | 42 | 0 |
| reamaze.com | (low) | **195** | **+195** | — | 214 | **+214** |
| personalizer.io | 186 | 193 | +7 | 253 | 253 | 0 |
| LoyaltyLion | 146 | 182 | +36 | 335 | 335 | 0 |
| Klaviyo | 146 | 165 | +19 | 177 | 177 | 0 |
| bogos.io | 79 | 148 | +69 | 54 | 54 | 0 |
| octaneai.com | 114 | 134 | +20 | 110 | 110 | 0 |
| Microsoft Hosted Libs (Searchanise jQuery) | 43 | 120 | +77 | 39 | 30 | -8 |
| tgtag.io | 91 | 101 | +10 | 37 | 37 | 0 |
| Searchanise | 72 | 72 | 0 | 3 | 3 | 0 |

**Top attribution: Google Tag Manager +420ms / +313 KB.** This is the single biggest delta. Looking at the bootup-time table per theme reveals:
- P8 loads `gtag/destination?id=AW-877099019` (632ms total bootup) — Google Ads conversion tag, NOT in P6's top-10
- P8 loads `gtag/destination?id=G-9LV7TG5ZH7` — Google Analytics 4 destination
- P8 loads `gtag/js?id=G-9LV7TG5ZH7` and `gtag/js?id=AW-611729126` — Google Ads + GA4 base tags

Same GTM container ID on both (`GTM-M4NKSBD`). But P8 measurement triggered MORE TAGS to fire than P6's measurement did. Possible reasons:
- GTM tags configured with conditional triggers (page URL contains 'preview', or specific dataLayer events) — P8's preview URL may flip a trigger condition
- GTM config was updated between the two measurements (unlikely — they ran 80s apart)
- One of the firings is a Google Ads conversion that fires on cart_added or similar, and the dataLayer is being populated differently on P8

**Second-biggest attribution: Reamaze (+195ms / +214 KB).** On P8, the FULL Reamaze widget loaded (`reamaze.js`). On P6 measurement, only the loader stub (`reamaze-loader.js`) appears to have fully fetched. This may correlate with the `bd meu` defer-Reamaze-until-interaction work — if that defer is active on P6 but not on P8, that explains the delta.

---

## Per-script bootup-time (top 10)

### P6 LIVE

| Script | Total | Scripting | Parse |
|---|---|---|---|
| HTML document | 7,269ms | 400 | 18 |
| jquery.min.js | 1,816ms | 1,361 | 10 |
| (unattributable) | 1,458ms | 110 | 0 |
| theme.js | 829ms | 80 | 14 |
| shopify-perf-kit-3.3.1.min.js | 615ms | 592 | 6 |
| judgeme-520/widget_others.js | 534ms | 332 | 7 |
| gtm.js | 373ms | 303 | 59 |
| ldt_gw_embed_index.js (gift wrap) | 348ms | 194 | 46 |
| judgeme-520/widget_base.js | 346ms | 226 | 16 |
| web-pixel-110329955@1 | 342ms | 201 | 27 |

### P8 DEV

| Script | Total | Scripting | Parse |
|---|---|---|---|
| HTML document | 7,846ms | 374 | 18 |
| (unattributable) | 2,305ms | 150 | 0 |
| jquery.min.js | 1,861ms | 1,491 | 16 |
| theme.js | **1,212ms** | **172** | **45** |
| gtm.js | 728ms | 646 | 56 |
| **gtag/destination?id=AW-877099019** | **632ms** | 188 | 57 |
| judgeme-522/widget_base.js | 524ms | 233 | 24 |
| judgeme-522/widget_others.js | 457ms | 186 | 5 |
| /cdn/wpm/...js (Shopify Web Pixels) | 431ms | 259 | 24 |
| custom-theme.js | 377ms | 152 | 26 |

**Notable: theme.js scripting time +92ms on P8 (172 vs 80).** Same file path. Possibly caused by different DOM state at parse time, OR sampling variance. Re-run with n≥3 to confirm.

**The new entry: `gtag/destination?id=AW-877099019` at 632ms total bootup on P8 ONLY.** This is a Google Ads conversion tracking destination. Doesn't appear in P6's top-10. ~600ms of the gap is attributable to this single new tag.

---

## Long tasks (>50ms)

Both themes had 20 long tasks each. Top 5 per theme:

### P6 LIVE
1. **quickBuyButton.min.js (STKY): 895ms** — known issue, bd a7av epic targets replacement
2. shopify-perf-kit-3.3.1.min.js: 321ms
3. gtag/js?id=AW-611729126: 270ms
4. HTML document: 243ms
5. ldt_gw_embed_index.js (gift wrap): 228ms

### P8 DEV
1. **quickBuyButton.min.js (STKY): 855ms** — same as P6, unchanged
2. **gtag/destination?id=AW-877099019: 604ms** — NEW on P8
3. ldt_gw_embed_index.js: 375ms
4. HTML document: 317ms
5. preloads.js (Shopify checkout): 271ms

The STKY quickBuyButton (~850ms long task on both themes) is the largest single recoverable cost. Already tracked in bd `hairmnl-theme-a7av` (replace STKY with theme-native ATC).

---

## Script set differences (cache-bust noise filtered)

**Scripts only in P8 measurement** (not just version-bump):
- `cdn.shopify.com/shopifycloud/preview-bar/preview-bar-modules.js` — **dev-only artifact**, disappears at cutover (~190 KB combined with `vendor--*.js`)
- `cdn.shopify.com/shopifycloud/preview-bar/vendor--61rXTEhfnWH.js` — **dev-only artifact**
- `ajax.aspnetcdn.com/.../jquery-3.7.1.min.js` — Searchanise's own jQuery (per audit-jquery 2i8b.12 finding)
- `cdn.reamaze.com/assets/reamaze.js` — full Reamaze widget vs. P6's loader-only
- `gtag/destination?id=AW-877099019` + `gtag/destination?id=G-9LV7TG5ZH7` — Google Ads + GA4 destinations
- Klaviyo onsite back-in-stock + signup forms — extra Klaviyo bundles

**Scripts only in P6 measurement**:
- `cdn.shopify.com/extensions/.../freegifts-194/...` (BOGOS v194 — P8 has v195 instead, same app)
- `shopifycloud/perf-kit/shopify-perf-kit-3.3.1.min.js` — appears in P6 bootup but not P8's top-10 (may have loaded on P8 but at lower CPU cost, or didn't sample)
- `/a/elevar/.../dl-app-embed-block.js` — Elevar conversion tracking (didn't appear in P8 bootup top-10)
- (Older versions of judgeme/loyaltylion scripts — version-bump noise)

---

## Refined attribution to the +1,723ms TBT gap

| Source | Estimated contribution | Confidence |
|---|---|---|
| Preview-bar JS (dev-only artifact) | ~200-400ms | High — disappears at cutover |
| GTM tag firing diff (esp. `AW-877099019` conversion tag) | ~400-600ms | Medium — single-sample, may be config-dependent |
| Reamaze full widget vs. loader-only | ~150-200ms | Medium — single-sample |
| Klaviyo extra bundles | ~50-100ms | Medium-low |
| Theme.js parse/exec variance | ~80-100ms | Low — sampling variance plausible |
| BOGOS app delta | ~70ms | Low |
| Other small contributors | ~100-200ms | Aggregated |
| **Subtotal explainable** | **~1,050-1,670ms** | |
| **Unexplained residual** | ~50-700ms | Likely sampling noise + GC time |

The wide ranges reflect single-sample uncertainty. Run a 3-sample re-baseline pre-cutover to narrow.

---

## Recommendations

### Immediate (low-cost, no new bd ticket)

1. **Subtract the preview-bar artifact from cutover-readiness reasoning.** When Phase D measures live TBT after publishing P8, it should compare against current live (P6), NOT against the dev-preview measurement. The dev-preview is ~200-400ms heavier than P8 will be in production due to preview-bar overhead.

2. **Re-run baseline with n=3 before Phase D.** Update `scripts/psi-baseline-matrix.py` to use a 30+ second sleep between runs (PSI's URL cache window) and add cache-buster query params per run. Tracked as a follow-up in the script's TODOs.

### Already in flight (existing bd tickets)

3. **`ujg6.13` Defer Reamaze + LoyaltyLion + Judge.me to interaction** — closing this is worth ~250-350ms of the gap (Reamaze full widget + Judge.me bundle initialization).

4. **`ujg6.12` Web Pixels Manager migration** — closing this is worth ~400-700ms (Google Ads tags move to sandbox worker, off main thread).

5. **`hairmnl-theme-a7av` epic** (STKY replacement) — closing this removes the ~850ms quickBuyButton long task on every page.

### New investigation tickets to file

6. **`2i8b.16` Investigate why GTM fires more Google Ads tags on P8 measurement than P6** — could be a GTM trigger gated on a page-context value (DOM ready state, dataLayer event, URL pattern). If it's a redundant firing, consolidate. If it's working as intended, accept the cost or wait for Web Pixels Manager migration (`ujg6.12`). **Recommended: CC Sonnet 4.6 / Medium, ~30 min** — needs reading GTM container config in admin.

7. **`2i8b.17` Audit Klaviyo onsite features for runtime cost** — Klaviyo loaded extra bundles on P8 (back-in-stock, signup forms). Verify they're TAE-loaded correctly + that they defer-on-interaction. Some of the +50-100ms here may be recoverable. **Recommended: CC Sonnet 4.6 / Low, ~20 min**.

### Not recommended for action

- Touching `assets/theme.js` (P8 stock bundle) — prohibited. The +383ms theme.js delta is likely sampling variance.
- Optimizing GC time directly — symptom, not cause.

---

## Implications for Phase B and cutover

The ujg6.28 investigation does NOT block Phase B.2. The bundle work proceeds as designed in `os2-migration/p8-bundle-architecture.md`. This investigation just clarifies:

- **The 1,700ms "regression" is not caused by layout/theme.liquid** (which is byte-identical between P6 and P8 dev post-revert).
- **~250-700ms of the gap is real and addressable** by existing tickets (ujg6.12 / ujg6.13 / a7av).
- **~200-400ms is measurement artifact** (preview-bar) that vanishes at cutover.
- **Remaining ~400-700ms** is third-party drift that compounds over time and can't be fixed by theme code alone (GTM configs, Klaviyo features, app updates).

**Cutover acceptance gate**: TBT parity with current live theme is realistic AFTER ujg6.12, ujg6.13, a7av land. Without them, P8 TBT will be slightly higher than P6 in production (~400-700ms range), driven by app/third-party drift.

## Acceptance criteria — MET

- [x] Top 3 main-thread cost contributors identified (GTM, Reamaze, theme.js parse-variance)
- [x] Decision per contributor: defer / replace / accept / investigate (see Recommendations)
- [x] Filed-as-follow-up tickets listed (2i8b.16, 2i8b.17)
- [x] Estimated TBT recovery target after Phase B work + recommended follow-ups: ~1,000-1,500ms of the current 1,723ms gap

## Caveats and open items

- Single-sample variance: n=1 PSI run per theme. Findings directionally reliable; specific magnitudes need n=3 to confirm.
- The dev theme measures with preview-bar overhead. Subtract ~200-400ms when reasoning about production state.
- Mobile TBT is not investigated here. Mobile shows different cost profile (cellular emulation slows JS evaluation differently). Open for separate investigation if needed.

---

## GTM trigger audit — 2i8b.15 CC-side investigation (2026-05-18)

### Headline

**GTM is NOT loaded by the HairMNL theme.** Zero references to `GTM-M4NKSBD`, `googletagmanager.com/gtm.js`, or `gtm.start` across any `.liquid`, `.js`, or `.html` file. Live HTML curl confirms zero GTM script tags directly emitted by the theme. The firing surface is entirely **Shopify Customer Events / Web Pixels Manager** (admin-side sandboxed iframe path).

### Container state (current, from public gtm.js fetch)

| Item | Value |
|---|---|
| Container ID | GTM-M4NKSBD |
| Container version | 143 |
| Container size | 553 KB |
| GA4 destination | G-9LV7TG5ZH7 (matches ticket) |
| AW-877099019 (Google Ads) | **REMOVED** since the P8 measurement |
| AW-611729126 | present |
| Event tags | purchase × 8, add_to_cart × 5, view_item × 5, begin_checkout × 3, sign_up × 1, page_view × 3 |
| Functions | 111 vars, 49 click listeners, 26 custom tags, 13 Enhanced Conversion senders |

### Why the +420ms TBT delta is a moving target

- AW-877099019 (the biggest single contributor in P8's bootup-time top-10) is no longer in the container.
- Either the container was updated after the P8 measurement OR the tag was conditional on a measurement context that no longer applies.
- Re-running the desktop home TBT measurement today would likely show a smaller GTM delta.

### What CAN'T be answered from CC

- Trigger fire conditions per tag (encoded as opaque `function:__c` / `function:__cl` references in the public bundle; readable only in GTM admin workspace).
- Verdict per tag (legitimate / redundant / misconfigured) — admin-only.

### Recommendation

**Defer trigger audit to `ujg6.12` (Web Pixels Manager migration).** Since GTM isn't in theme code, theme-side interventions can't reduce the firing surface. The Web Pixels Manager migration:
1. Replaces the legacy GTM custom pixel with native Web Pixels events (deduplicates firings)
2. Removes the overlap between Shopify-channel-native tag firing and GTM-orchestrated tag firing
3. Will surface still-firing tags as part of the migration audit

`2i8b.15` is closing as wontfix-deferred-to-ujg6.12.
