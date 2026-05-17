# Phase 4 lint + CLS audit report

> **Bead:** hairmnl-theme-2i8b.8 (Phase 4.M7 — Wave D)
> **Date:** 2026-05-17 (CC merge-gate update same day)
> **Status:** COMPLETE within M7 scope. kt0 audit PASS. CLS runtime measurement deferred to Phase 5 (which deploys the dev theme that makes the measurement meaningful).

---

## kt0 CSS containment audit

- **Command:** `python3 scripts/check-overlay-css.py`
- **Result:** ✅ PASS
- **Scanned:** 362 files
- **Violations:** 0
- **Exit code:** 0

The Pipeline 8 working tree has zero CSS containment violations (`contain: layout`, `transform`, `filter`, `will-change: transform`, `backdrop-filter` on parent selectors that would trap fixed-position overlays). This audit specifically catches the kt0-class bug pattern where cart drawers, mobile navs, modals, and lightboxes get trapped inside a containing block.

## CLS spot-checks per template

### Why CLS measurement is deferred (not blocked)

OC's initial M7 dispatch flagged `PSI_API_KEY` as the blocker. That's an OC environment limitation (the key is in macOS Keychain and OC's runtime can't read it), not the real blocker. The actual blocker is **the dev theme hasn't been deployed yet.**

The 6 template URLs use `?preview_theme_id=141168312419`. That theme is bare Pipeline 8 as it was when P1.3 baseline ran. Our Phase 4 work (M1–M6 + Vertex) lives only on `origin/main` in the git working tree — no `shopify theme push --theme=141168312419` has run since the P1.3 install. A PSI run on the preview URL right now would measure **bare Pipeline 8**, not "Pipeline 8 with our Phase 4 ports" — duplicating the P1.3 baseline (mobile CLS 0.000) without producing new signal.

The with-our-ports CLS measurement is **a Phase 5 visual QA step**, not an M7 step. Phase 5 includes the `shopify theme push` deploy + visual QA + PSI verification together.

### What Phase 5 does (operator action items, not in M7)

1. `shopify theme push --theme=141168312419 --store=creations-gdc.myshopify.com` — deploy current main to the dev theme
2. Run PSI on the 6 template preview URLs (script handles Keychain lookup):
   ```bash
   ./scripts/run-psi.sh "https://www.hairmnl.com/?preview_theme_id=141168312419" mobile 2
   ./scripts/run-psi.sh "https://www.hairmnl.com/products/davines-momo-shampoo?preview_theme_id=141168312419" mobile 2
   ./scripts/run-psi.sh "https://www.hairmnl.com/collections/loreal-professionnel?preview_theme_id=141168312419" mobile 2
   ./scripts/run-psi.sh "https://www.hairmnl.com/blogs/news?preview_theme_id=141168312419" mobile 2
   ./scripts/run-psi.sh "https://www.hairmnl.com/blogs/hair-education/rebonding-vs-keratin-treatment?preview_theme_id=141168312419" mobile 2
   ./scripts/run-psi.sh "https://www.hairmnl.com/cart?preview_theme_id=141168312419" mobile 2
   ```
3. Compare each CLS reading against the reference baselines below.
4. Append results to this report's appendix or to `perf-baseline-comparison.md` under a new "Post-port dev theme" row.

### Reference baselines (no fresh PSI needed for M7)

| Metric | Pipeline 6.1.3 (live) | Pipeline 8.1.1 bare (preview) | Source |
|---|---|---|---|
| Mobile CLS (lab) | 0.015 | **0.000** | P1.3 baseline 2026-05-17 |
| Mobile CLS (CrUX p75 field) | 0.04 (FAST band) | n/a — preview never serves real users | P1.3 CrUX pull |
| Desktop CLS (lab) | 0.009 | **0.000** | P1.3 baseline 2026-05-17 |

The bare-P8 CLS of 0.000 is the floor we need to preserve through M1–M6 porting. M7's kt0 audit confirms no static CSS-containment violations were introduced. Phase 5 confirms the runtime number matches.

## Recommendations

1. **kt0 audit:** No action needed — clean scan. The brand-collection consolidation (M4) and app-snippet drops (M6) did not introduce new containment violations.

2. **CLS measurement:** Deferred to Phase 5 visual QA. The PSI-on-preview-URL queue documented above is for Phase 5, not for M7 re-open.

3. **M7 closes here.** The remaining work — deploying Phase 4 to the dev theme + running PSI per template — is Phase 5 scope, not lint-pass scope.

## Verification log

| Date | Action | Outcome |
|---|---|---|
| 2026-05-17 | OC dispatched M7. kt0 audit ran via `python3 scripts/check-overlay-css.py` — 362 files, 0 violations. Initial report drafted noting PSI_API_KEY gate. | kt0 PASS. Commit e843c3a on main. |
| 2026-05-17 (CC merge-gate) | Clarified the real gating concern (dev theme hasn't received our ports yet, not PSI key access). Restructured report to defer CLS measurement to Phase 5 explicitly. | M7 complete within scope. |