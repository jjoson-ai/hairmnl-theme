# P8 perf parity + leverage — architecture

> **Status:** Design (2026-05-18). Filed as bd epic at design time.
> **Owner:** Operator + CC (Opus 4.7 for design/diagnosis; Sonnet 4.6 for bulk ports).
> **Branch:** `claude/p4-pathb-cc` (this worktree) → cut a new branch `claude/p8-perf` for the epic.
> **Dev theme:** `141168312419` ("Pipeline 8 Working Demo"). **Never push to live `131664707683`.**

---

## Why this epic exists

Two measurements, taken five months apart, define the problem:

**Bare Pipeline 8.1.1 (2026-05-17 baseline, `os2-migration/perf-baseline-comparison.md`):**

| Metric (n=3 median) | P6 LIVE | Bare P8 | Δ |
|---|---|---|---|
| Mobile PSI | 29 | **62** | **+33** |
| Desktop PSI | 54 | **72** | **+18** |
| Mobile CLS | 0.015 | **0.000** | **-100%** |
| Mobile TBT | 2,504ms | **175ms** | **-93%** |
| Desktop TBT | 1,706ms | **225ms** | **-87%** |
| Render-blocking | 2 | **0** | **-2** |

**Current P8 dev (this branch, 2026-05-18, after Phase 4 port work):**

| Metric (n=2-3) | P6 LIVE | P8 dev now | Δ vs P6 | Δ vs bare P8 |
|---|---|---|---|---|
| Desktop PSI | 58 | **31** | **-27** | **-41** |
| Desktop CLS | 0.010 | **0.681** | **+0.671** ⚠ | **+0.681** ⚠ |
| Desktop TBT | 1,710ms | 2,100ms | +390ms | **+1,875ms** |
| Desktop LCP | 1.52s | 1.73s | +0.21s | flat |

**The gap is regression, not architecture.** Bare P8 was decisively faster than P6. Our Phase 4 ports — `custom-theme.js/css` re-enable, 7 newly-wired CSS files, P6 template reverts — recreated most of P6's perf profile on top of P8's bundle. Closing the gap is mostly *subtraction* (undo what regressed) plus *substitution* (replace P6 patterns with OS 2.0-native equivalents that don't carry the cost).

---

## Strategy: subtract, substitute, surpass

Three concentric goals:

1. **Subtract (parity floor):** get back to bare-P8 perf numbers by surgically removing or refactoring the Phase 4 changes that introduced render-blocking / layout-shifting / blocking-JS regressions. Target: desktop PSI ≥ 70, CLS ≤ 0.02, TBT ≤ 300ms on the dev theme homepage.

2. **Substitute (P6 parity through OS 2.0 patterns):** where a Phase 4 port was *functionally necessary* (logo, cart drawer, vertex recs, font fix), replace the perf-regressing implementation with an OS 2.0-native pattern that achieves the same functional outcome without the cost. E.g., critical-CSS inlining + deferred non-critical CSS instead of seven render-blocking `stylesheet_tag` lines.

3. **Surpass (beat P6 by leveraging OS 2.0):** use OS 2.0 features P6 *cannot* use to push P8 past P6's ceiling.
   - Theme app extensions (TAE) for the 14 GREEN apps in `app-compatibility-matrix.md` (Klaviyo, Smart SEO, Re:amaze, LoyaltyLion, Judge.me, etc.) — removes their JS from the main theme bundle.
   - Web Pixels Manager for GTM/analytics events — runs in a sandboxed worker, zero main-thread cost.
   - Section Rendering API + `IntersectionObserver` for below-fold sections and filter/sort UX — defers entire DOM subtrees.
   - `fetchpriority="high"` + `<link rel="preload">` for LCP element + critical font.
   - `section.shopify.refresh` for cart drawer content reload — replaces the current full-HTML fetch + innerHTML splice.
   - `content-visibility: auto` on below-fold sections — browser skips render/layout cost until viewport reaches them.

---

## Phasing

Five phases + one closeout. Phase 0 is sequential gating; Phases 1-3 run in parallel; Phase 4 is the verification gate; Phase 5 is the global-rule-mandated closeout audit.

### Phase 0 — Diagnosis (CC, Opus 4.7 / High, ~1 day)

Goal: a concrete, evidence-based map from observed regression → causal commit → mitigation strategy.

- **0.1 Baseline matrix.** Run `scripts/run-psi.sh` n=5 (mobile + desktop) against three URLs: P6 live, bare-P8 stand-in (a temporary checkout of `0ab1295` if accessible OR re-create on a second dev theme), current P8 dev. Five templates: home, collection (best sellers), PDP (top product), cart, brand-collection (L'Oréal). Output: a markdown table replacing tonight's ad-hoc results.
- **0.2 CLS attribution.** Use Chrome DevTools Performance recording + `PerformanceObserver` on each template; identify the largest individual layout-shift events and their associated DOM nodes. Per-template attribution: hero, slider, font swap, AOS, app injection, etc.
- **0.3 TBT bisect.** Walk the commit list from `c108dc7` forward; for each commit that touched `assets/*.js`, `layout/theme.liquid`, or `snippets/css-overrides.liquid`, capture which one(s) re-introduce the 2100ms TBT.
- **0.4 Diagnosis report.** Write `os2-migration/perf-regression-analysis.md` consolidating 0.1-0.3. This is the input contract for Phases 1-3.

### Phase 1 — CLS elimination (CC + OC senior-dev, ~2-3 days)

Goal: desktop CLS ≤ 0.02, mobile CLS ≤ 0.05. This is ~25 of the 27 desktop PSI points lost.

- **1.1 Hero/slider pre-init reservation.** Continuation of bd `hairmnl-theme-ehrm`. Verify the slider-A/B fix shipped on `main` is in this branch; extend to slider-C (homepage "For Frizz" tile grid).
- **1.2 Image dimension audit.** Sweep `product-grid-item*.liquid`, `header-block.liquid`, `slideshow.liquid`, brand-section image renders. Every `<img>` must have `width` and `height` attributes (browser reserves aspect-ratio box). Use Lighthouse "Image elements do not have explicit width and height" report.
- **1.3 Font CLS.** `BasisGrotesquePro` vs UA fallback have different metrics; the swap causes text reflow. Tune via `size-adjust: 100%` and `ascent-override` / `descent-override` on the `@font-face`, OR set `font-display: optional` for non-critical weights. Tonight's `:root` font-stack fix in `css-overrides.liquid` did not address swap-metric mismatch.
- **1.4 AOS layout-shift fix.** `aos.css` was just wired in tonight (`7d4c71c`). AOS elements start `opacity:0; translateY(20px)` and animate in — if the translated state takes a different layout slot than the final state, it shifts on scroll. Either: (a) gate to `prefers-reduced-motion: no-preference`, (b) replace AOS with `IntersectionObserver` + CSS-only `opacity` (no `translate`), or (c) drop AOS entirely if the visual effect is non-essential.
- **1.5 Defer non-critical CSS.** Convert 5 of the 7 newly-added CSS `stylesheet_tag` lines to `<link rel="preload" as="style" onload="this.rel='stylesheet'">` (asynchronous). Keep `cart.css` and `aos.css` render-blocking only if Phase 1.4 keeps AOS; otherwise defer them too. Above-fold critical CSS goes inline in `<head>` via a new `snippets/critical-css.liquid` (P6 has this snippet — port the pattern).

### Phase 2 — TBT / JS reduction (CC + OC senior-dev, ~3-4 days)

Goal: desktop TBT ≤ 400ms, mobile TBT ≤ 500ms. This closes the 1,875ms gap vs bare P8.

- **2.1 custom-theme.js audit.** Quantify which behaviours in `assets/custom-theme.js` are still wired up on which templates. Per the P4 spike report, ~750 LoC of actual custom code; the rest is vendor (sticky-js, sweetalert2, swiper, dom7, he, ssr-window — ~8,000 LoC of dependencies). Determine: which vendors are referenced by hairmnl-custom.js's seven sections? (Likely none.)
- **2.2 Replace heavy vendor deps with native APIs.** `sticky-js` → native `position: sticky` (done in `hairmnl-custom.js` section 1). `swiper` → P8 already ships Flickity for sliders. `sweetalert2` → native `<dialog>` element. Goal: shrink or eliminate `custom-theme.js` entirely. Each vendor removal is its own ticket.
- **2.3 Web Pixels Manager migration.** GTM + Klaviyo + Elevar currently load synchronously via `content_for_header` or hardcoded scripts. Migrate to Web Pixels Manager (Shopify-native, runs in sandbox worker) — zero main-thread cost. Per app-compat matrix, Klaviyo and Elevar are TAE-ready with pixel-mode.
- **2.4 Defer app scripts on user interaction.** Re:amaze (213 KB), LoyaltyLion (266 KB SDK + 100 KB embed), Judge.me deferred-loader. Each has a known "defer until interaction" pattern; per the matrix, Re:amaze and LL both support this via dashboard toggle.
- **2.5 Tree-shake hairmnl-custom.js per-template.** Section 1 (sticky-filter-bar) only matters on collection pages; section 2 (product-tabs) only on PDP; sections 3+4 (mobile nav + LL points) on every page. Split into `hairmnl-{collection,product,common}.js` and load conditionally via `{% if template contains 'collection' %}` etc.

### Phase 3 — OS 2.0-native uplift (CC + OC senior-dev, ~3-5 days, parallel with Phase 1-2)

Goal: PSI ≥ bare-P8 (72 desktop / 62 mobile) and *demonstrate* OS 2.0 features as the cutover narrative.

- **3.1 TAE migration: 10 GREEN apps.** Per `app-compatibility-matrix.md`: BOGOS, Smart SEO (core + broken-link), Klaviyo, Shopify Inbox, Nova Cookie Bar, Hextom Timer, LoyaltyLion (×2), LDT Gift Wrap, OXI Social Login, Hextom CTB. Each app: toggle TAE block in admin, verify functional parity, remove any legacy snippet/script residue. **CC-only** — Shopify admin work, not offloadable.
- **3.2 Section Rendering API for filter/sort.** Collection page filter changes currently force a full page reload (P6 pattern). P8 supports `?section_id=` to render just the product grid. Replace `window.location.href = …` filter submissions with `fetch(?section_id=...)` + targeted innerHTML swap.
- **3.3 `content-visibility: auto`.** Apply to below-fold sections on home + collection + PDP. Browser skips render/paint/layout for off-screen content. Pair with `contain-intrinsic-size` to prevent scrollbar jumping.
- **3.4 Lazy section render.** For heavy below-fold sections (best-sellers, featured collections, brand grids), defer the entire section's `{% section %}` render to client-side `fetch(?section_id=...)` after IntersectionObserver entry. Trade: slightly slower below-fold first-paint for substantially faster TTI.
- **3.5 LCP optimization.** Add `fetchpriority="high"` + `<link rel="preload" as="image">` to the homepage hero LCP image. Preload `BasisGrotesquePro-Regular.woff2` (currently `font-display: swap` but no preload).
- **3.6 Cart drawer `section.shopify.refresh`.** P8's current cart drawer fetches `?section_id=api-cart-items` and innerHTML-splices the response. `section.shopify.refresh` is the OS 2.0-native equivalent that's more efficient and handles section JS bindings automatically.

### Phase 4 — Verification (CC, Opus 4.7 / High, ~1 day)

- **4.1 Re-baseline.** PSI n=5 mobile + desktop on the same 5 templates from 0.1. Compare to bare-P8 baseline AND to P6 live. Acceptance: desktop ≥ 70, mobile ≥ 60, CLS ≤ 0.05 across all templates.
- **4.2 CrUX projection.** Field data is only available *after* publishing. Document the methodology + sampling cadence for post-cutover monitoring (week-1, week-2, week-4 checkpoints). This is a methodology doc, not a measurement.
- **4.3 Lighthouse CI integration.** Add GitHub Action that runs Lighthouse against PR previews; fails the PR if PSI drops > 5 points or CLS > 0.05 on any template. Prevents the next regression.

### Phase 5 — Closeout (CC, Opus 4.7 / High, ~0.5 day) — REQUIRED per global rule

- **5.1 epic-audit closeout.** Per the closeout-audit-always rule in `~/.claude/CLAUDE.md`. Baseline tag the start of Phase 0; run `epic-audit p8-perf` against the diff. Focus on fix-regressions / incomplete-fixes / interaction-effects across Phases 1-3. Escape hatch: if < 3 code-changing follow-ups emerge during triage, close as `won't-do` with notes.

---

## OC offload strategy

Aligns with `~/.claude/CLAUDE.md` OC tier discipline:

| Phase | Offload? | Why |
|---|---|---|
| 0 (diagnosis) | **CC** | Requires synthesis + judgment. PSI baselines are mechanical (CC). Bisect requires reading commit context. |
| 1 (CLS) | **Hybrid** | 1.1 / 1.4 need judgment (which CLS source is dominant). 1.2 (image dimension audit) is OC-friendly bulk. 1.3 (font CLS) is judgment. 1.5 (defer CSS) is OC-friendly. |
| 2 (TBT) | **Hybrid** | 2.1 / 2.2 need careful refactoring (CC). 2.3 / 2.4 / 2.5 are OC-friendly once specified. |
| 3 (OS 2.0) | **CC** for TAE (admin work) + **OC** for section-rendering refactors | TAE toggles must be done in Shopify admin (CC). 3.2-3.6 are codeable specs OC can execute. |
| 4 (verify) | **CC** | Judgment-heavy interpretation of PSI / CrUX deltas. |
| 5 (closeout) | **CC, Opus 4.7 / High** | Final code review — never offload (per global rule). |

Concurrent OC dispatch caps (≤3) and disjoint-file rules apply throughout. Phase 1.2 + 1.5 + 3.2 are a clean triple-disjoint wave.

---

## Hard rules (don't violate)

1. **Never push to live theme `131664707683`.** All work on dev `141168312419`.
2. **Never modify** `assets/theme.js`, `assets/vendor.js`, `config/settings_data.json`, `config/settings_schema.json` (per branch CLAUDE.md).
3. **No bypassing kt0 lint.** `python3 scripts/check-overlay-css.py` must exit 0 before each push to dev. Any new `contain`/`transform`/`filter` on an overlay selector requires `kt0-OK` justification.
4. **No `--force` git operations.** No `--no-verify` commits.
5. **Each PSI verification step requires n=5 samples on each URL.** Single-run numbers are not authoritative.
6. **Phase 4.1 acceptance must hold across all 5 templates, not just homepage.** PSI parity on one template is not parity.
7. **Phase 0.4 diagnosis report is the contract.** If Phase 0 reveals a different root cause than the strategy assumed, the strategy must be re-designed BEFORE Phase 1 begins.

---

## Pre-flight checks (must pass before Phase 0 begins)

1. ☐ `oc-tier.sh` reports `tier: PAID ✓` (or `FREE ✓`). PAID preferred for diagnosis depth.
2. ☐ Dev theme `141168312419` is reachable; `shopify theme pull --theme=141168312419` succeeds.
3. ☐ `scripts/run-psi.sh` works with current `PSI_API_KEY` (verified tonight — works).
4. ☐ `scripts/check-overlay-css.py` exits 0 on current tree.
5. ☐ Branch is clean; no uncommitted Phase 4 changes pending.
6. ☐ Phase 4 closeout (`hairmnl-theme-2i8b.10`) reviewed — its findings inform Phase 0.4 inputs.
7. ☐ Calendar window: 5-7 focus days within next 2 weeks (before cutover).

---

## Acceptance criteria for the epic

The epic closes when ALL hold:

1. Desktop PSI ≥ 70 (n=5 median) on homepage, collection, PDP, cart, brand-collection.
2. Mobile PSI ≥ 60 (n=5 median) on same five templates.
3. CLS ≤ 0.05 (lab) on all five templates.
4. TBT ≤ 500ms (desktop), ≤ 800ms (mobile) on all five templates.
5. LCP ≤ 2.0s (desktop), ≤ 3.5s (mobile) on home + PDP.
6. ≥ 10 of the 14 GREEN-tier apps from `app-compatibility-matrix.md` are confirmed running via TAE (no theme code).
7. `scripts/check-overlay-css.py` clean on the final diff.
8. Lighthouse CI workflow live in `.github/workflows/`.
9. Phase 0.4 diagnosis report + Phase 4.2 CrUX methodology doc both committed to `os2-migration/`.
10. Phase 5 closeout audit run OR closed as `won't-do` with triage notes citing < 3 follow-ups.

---

## Out of scope (deliberate)

- INP optimization (requires field data; can only verify post-cutover).
- Image format conversion (WebP already deployed per memory).
- Lazy loading of below-the-fold images (already done in P6 via `loading="lazy"`, ported to P8).
- A/B testing infrastructure (GrowthBook or similar) — separate epic if needed.
- BSS B2B uninstall (separate epic, scheduled separately).
- Pro Blogger replacement (bd `01vl`, separate epic).

---

## Why this can't be deferred until post-cutover

Two of the listed acceptance criteria — desktop CLS ≤ 0.05 and TBT ≤ 500ms — are *worse on current P8 dev than on P6 live*. Cutover to a slower theme would harm SEO (CrUX-based ranking signals) and conversion. The whole point of the OS 2.0 migration program was a perf win; cutting over without first restoring (and ideally extending) the bare-P8 advantage would be a self-inflicted regression visible in field data within 28 days.

The bare-P8 baseline doc (`perf-baseline-comparison.md`) is the implicit promise. This epic delivers on it.
