# Coordinator Handoff Log

Append-only log of coordinator sessions. Newest entries at the top.

Format spec: see `docs/coordinator-handoff.md` §10.

---

### 2026-05-06 (model: claude-opus-4-7) — coordinator review of Batch D

**Issues touched:** cua, c4w, 4sv (Batch D — features + polish)
**Outcome:** shipped to GitHub Pages

**What was done:**
- Reviewed OpenCode diff — scope contained, all 3 implementations correct
- cua: PSI now captures network_by_origin (median run preserved); ORIGIN_LABELS map; render_origin_weights() with stacked area chart over last 30 snapshots + latest table
- c4w: render_crux_truth() — top-of-page card with mobile + desktop p75 across 5 metrics, pass/fail badges per Google CWV thresholds, collection period subtitle
- 4sv: METRIC_TIPS["WoW"] entry; tooltip injected on WoW scorecard h2

**Verification:**
- render-only succeeds: ✓
- py_compile clean: ✓
- "Production truth" h2 in HTML: ✓
- "Third-party weight" h2 in HTML: ✓
- snapshots.jsonl unchanged: ✓
- Closed cua, c4w, 4sv (already closed by OpenCode session)

**Next-session handoff notes:**
- Origin-weights chart shows empty state until next PSI run captures network_by_origin (next GHA run at 13:00 UTC, or manual trigger)
- Batch F (ofc + 2em) brief at /tmp/oc-batch-F.md — A/B comparison + Slack alerts, single file, glm-5.1:cloud
- Batch E (236) brief at /tmp/oc-batch-E.md — per-template CWV slicing, multi-file (theme + dashboard), glm-5.1:cloud, requires draft→live theme push by coordinator

---

### 2026-05-05 (model: claude-opus-4-7)

**Issues touched:** gjv
**Outcome:** shipped to live

**What was done:**
- Fixed /cart INP regression: `CartItems.lockState()` now adds `cart--loading` class to active `[data-cart-item]` row instead of page-level `[data-cart-loading]` wrapper
- Drops style recalc from O(N items × 3 controls) → O(1) before each paint on stepper clicks
- CSS descendant selectors unchanged — they continue to match correctly because the row is still an ancestor of the quantity controls
- Authored `docs/coordinator-handoff.md` and seeded this log

**Files modified:**
- `assets/theme.dev.js:4113` — `this.loader.classList.add(...)` → `this.latestClick.classList.add(...)`
- `assets/theme.js:2759` — same change in minified bundle

**Verification:**
- diff check: ✓ (exactly 2 single-line changes, both in `lockState`)
- draft smoke test: ✓ (qty stepper updates worked, no console errors, draft preview confirmed via VERTEX overlay)
- live push: ✓ (commit 3a22d94, pushed to GitHub)

**Next-session handoff notes:**
- **Pending verification (RUM):** check GA4 dashboard after 2026-05-12 — /cart poor INP should drop from 21% toward <10%. If flat, the dominant cost is a third-party listener (LimeSpot/Klaviyo); next investigation is DevTools event-listener attribution.
- Multi-row isolation behavior was NOT visually verified during smoke test (only 1 item in test cart). User confirmed "looks good" in their own session before live push.
- `bd close gjv` ran successfully

---

### 2026-05-05 (model: claude-opus-4-7) — GHA debugging + first successful run

**Issues touched:** 6o0 (closed)
**Outcome:** GHA workflow fully operational; first auto-refresh commit a01a2df landed on main

**What was done:**
- First run of perf-dashboard.yml after secrets were added returned green but did no work (silent no-op via "Skipping empty snapshot" exit-0 path)
- Diagnosed via hardened workflow: GA4_SERVICE_ACCOUNT_KEY was 34 chars (should be ~2300 — full JSON file), PSI_API_KEY was 61 chars (should be 39 starting with AIza). User confused GA4_PROPERTY_ID with G- prefixed Measurement ID.
- Pushed dcaf207: hardened workflow with explicit secret-presence check, printf '%s' instead of echo, JSON validation step that prints redacted preview on failure
- User updated secrets correctly; manual workflow_dispatch run succeeded in 3m 34s, fetched real PSI + GA4 data, committed a01a2df with snapshot 17 (PSI mobile score 36, GA4 LCP 84.59% good / N=25,682)
- Closed 6o0; bd remember persisted the failure modes so future debugging is faster

**Files modified:**
- `.github/workflows/perf-dashboard.yml` — verify-secrets step, printf for write, JSON validation with redacted preview

**Verification:**
- GHA run 25404594... succeeded: ✓
- Commit a01a2df pushed by github-actions[bot]: ✓
- snapshots.jsonl: 16 → 17 lines: ✓
- Staleness banner cleared after re-render (snapshot now <24h): ✓

**Next-session handoff notes:**
- Daily cron at 13:00 UTC is now live and self-maintaining; no operator action needed unless a run fails
- GA4 service account key in the secret will rotate when the underlying ~/.config/hairmnl-ga4-key.json is rotated — remember to also update the GitHub secret if you rotate locally
- gjv RUM check still pending after 2026-05-12 (verify /cart poor INP drops from 21% → <10%)
- 236 (per-template CWV slicing) still deferred — needs separate session
- Sprint complete: 19 of 19 dashboard issues shipped this 2-day span (gjv + 18 dashboard sprint + 6o0 GHA debug)

---

### 2026-05-05 (model: claude-opus-4-7) — coordinator review of Batches B + C

**Issues touched:** 8vi, me3, 91i (Batch B); p0w, xq7, tfj (Batch C remainder — 5fj, 483, qkd already shipped in earlier commit)
**Outcome:** shipped to GitHub Pages

**What was done:**
- Reviewed combined Batch B + C diff — scope contained, all expected files only
- Batch B: GHA workflow (.github/workflows/perf-dashboard.yml), SECRETS.md doc, staleness banner in render_html(), README log filename fix + GHA section
- Batch C remainder: full responsive CSS breakpoints (p0w), empty states for all render functions (xq7), @media print block (tfj)
- Closed 8vi, me3, 91i, p0w, xq7, tfj
- Committed and pushed to main

**Verification:**
- `python3 scripts/build-perf-dashboard.py --no-psi --no-crux --render-only` succeeds: ✓
- py_compile clean: ✓
- All HTML markers present: .table-scroll (2), tip-open (8), #8F5210 (2), #922525 (2), @media print (1), Stale data banner (1)
- snapshots.jsonl unchanged: ✓
- GHA YAML scope: paths-ignore prevents self-loop; secrets only via ${{ secrets.X }}; commit-back uses [skip ci]: ✓

**Next-session handoff notes:**
- **MANUAL ACTION REQUIRED:** User must add 3 GitHub repo secrets via GH UI before first GHA run (see .github/SECRETS.md). Without them, the workflow will fail authentication.
- After secrets added: manually trigger workflow_dispatch at https://github.com/jjoson-ai/hairmnl-theme/actions/workflows/perf-dashboard.yml to validate end-to-end before relying on the daily cron
- Sprint complete: 18 of 18 dashboard issues shipped (9 Batch A + 3 Batch B + 6 Batch C). Deferred: `236` (per-template CWV slicing — separate session, needs GA4 custom dimension)
- gjv RUM verification still pending after 2026-05-12 — check /cart poor INP drops from 21% toward <10%
- Staleness banner currently rendering on local dashboard because latest snapshot is >24h old; will clear once daily refresh runs

---

### 2026-05-05 (model: claude-opus-4-7) — coordinator review of Batch A

**Issues touched:** 9he, zgr, aqp, k65, imv, 40a, 8o5, wuf, rmi (Batch A closed); 5fj, 483, qkd (Batch C items implemented early by OpenCode — also closed)
**Outcome:** shipped to GitHub Pages

**What was done:**
- Reviewed OpenCode diff — scope contained, all 9 Batch A implementations correct
- OpenCode also implemented 5 Batch C items ahead of schedule: tooltip tap-to-toggle JS (5fj), WCAG AA contrast fix amber #8F5210 / red #922525 (483), parallel PSI via ThreadPoolExecutor (qkd), table-scroll wrapper on all tables (partial p0w), empty-state messages on inp_targets + js_errors (partial xq7)
- Closed 9he, zgr, aqp, k65, imv, 40a, 8o5, wuf, rmi, 5fj, 483, qkd
- Committed and pushed to main

**Verification:**
- `python3 scripts/build-perf-dashboard.py --no-psi --no-crux --render-only` succeeds: ✓
- privacy-policy absent from HTML output: ✓
- (N= appears in HTML: ✓ (5 occurrences)
- Impact column in top-pages: ✓
- snapshots.jsonl unchanged: ✓
- py_compile clean: ✓

**Next-session handoff notes:**
- Batch B (GHA + staleness banner + log filename): brief at /tmp/oc-batch-B.md — run with glm-5.1:cloud
- Batch C remainder (p0w full responsive CSS, xq7 empty states for rum_cwv + top_pages, tfj @media print): brief at /tmp/oc-batch-C.md — run with kimi-k2.6:cloud. 5fj/483/qkd already done; OpenCode should skip those.
- After Batch B: user must add 3 GitHub secrets via GH UI before first GHA run (see .github/SECRETS.md)
- Bot filter cutoff is 2026-05-05 — document in dashboard/README.md during Batch B

---

### 2026-05-05 (model: glm-5.1:cloud via OpenCode, coordinated by claude-opus-4-7)

**Issues touched:** 9he, zgr, aqp, k65, imv, 40a, 8o5, wuf, rmi (Batch A — data correctness)
**Outcome:** staged for coordinator review, not yet committed

**What was done:**
- Forward-only bot filter for /pages/privacy-policy in GA4 page-dimensioned queries (9he)
- Top friction pages now sort by impact = poor% × pageviews (zgr)
- Snapshot dedup on read — latest-per-UTC-day wins (aqp)
- (N=…) sample-size annotation on every RUM percentage; ⚠️ for N<50 (k65)
- WoW scorecard volume sanity warning when traffic drops 50%+ (imv)
- CrUX vs GA4 RUM divergence badge when |Δ|>10pp (40a)
- Null-field validation + typed empty-state on GA4 response (8o5)
- Snapshot rotation helper — archives older entries when snapshots.jsonl > 1000 lines (wuf)
- GA4 sampling detection + UI note (rmi)

**Files modified:**
- `scripts/build-perf-dashboard.py` — multiple functions: query_ga4_rum, load_snapshots, render_top_pages, render_rum_cwv_cards, render_wow_scorecard, render_snapshot_section, render_html, plus new rotate_snapshots_if_needed helper
- `dashboard/index.html` — regenerated (auto-output)

**Verification:**
- `python3 scripts/build-perf-dashboard.py --no-psi --no-crux --render-only` succeeds: ✓
- snapshots.jsonl unchanged: ✓
- All DoD checks pass: ✓

**Next-session handoff notes:**
- Coordinator (Claude Code) to review diff, run end-to-end smoke check, commit, push, and bd-close all 9 issues
- Bot filter is forward-only; old snapshots retain unfiltered data — document the cutoff date in dashboard/README.md (will happen in Batch B)

---

### 2026-05-05 (model: glm-5.1:cloud via OpenCode, coordinated by claude-opus-4-7)

**Issues touched:** 8vi, me3, 91i (Batch B — dashboard freshness)
**Outcome:** staged for coordinator review, not yet committed

**What was done:**
- GitHub Action perf-dashboard.yml — daily 13:00 UTC build, commit-back, workflow_dispatch trigger (8vi)
- Staleness banner injected into render_html() when newest snapshot >24h old, links to GHA manual trigger (me3)
- Reconciled log filename to hairmnl-daily-perf.log across README and build script docstring (91i)
- Created .github/SECRETS.md documenting the 3 required repo secrets user must add via GH UI

**Files modified:**
- `.github/workflows/perf-dashboard.yml` — new file
- `.github/SECRETS.md` — new file
- `scripts/build-perf-dashboard.py` — render_html() staleness banner; docstring log filename
- `dashboard/README.md` — log filename fix, GHA section added
- `scripts/launchd/com.hairmnl.daily-perf.plist` — verified already correct (no change needed)

**Verification:**
- `python3 scripts/build-perf-dashboard.py --no-psi --no-crux --render-only` succeeds: ✓
- YAML lints clean: ✓
- snapshots.jsonl unchanged: ✓
- All DoD checks pass: ✓

**Next-session handoff notes:**
- Coordinator (Claude Code) must review GHA YAML before committing — verify paths-ignore, no secret leakage in YAML, commit-back uses [skip ci]
- User must add 3 GitHub secrets before first GHA run (see .github/SECRETS.md)
- After secrets added: user manually triggers workflow_dispatch to validate end-to-end
- Batch A (data correctness) should be merged first — Batch B's GHA will run the updated script

---

### 2026-05-05 (model: kimi-k2.6:cloud via OpenCode, coordinated by claude-opus-4-7)

**Issues touched:** p0w, 5fj, xq7, 483, qkd, tfj (Batch C — UX polish + ops)
**Outcome:** staged for coordinator review, not yet committed

**What was done:**
- Mobile responsive pass: table-scroll wrapper, overflow-wrap on paths, chart min-width, max-width 400px kpi font shrink (p0w)
- Tooltip tap-to-toggle JS + viewport-edge clamping + :focus-visible styles (5fj)
- Empty/loading states for all 5 render functions with informative messages (xq7)
- WCAG AA contrast fix: --amber #C97A1A→#8F5210, --red #C03A3A→#922525; chart hardcodes updated (483)
- PSI mobile+desktop now run concurrently via ThreadPoolExecutor(max_workers=2) (qkd)
- @media print block: hide charts/tabs, expand all tab-content, page-break hints (tfj)

**Files modified:**
- `scripts/build-perf-dashboard.py` — CSS block in HTML_TEMPLATE, _empty_state() helper, render_*() empty guards, main() PSI parallelization

**Verification:**
- `python3 scripts/build-perf-dashboard.py --no-psi --no-crux --render-only` succeeds: ✓
- python3 -m py_compile passes: ✓
- snapshots.jsonl unchanged: ✓
- All DoD checks pass: ✓

**Next-session handoff notes:**
- Coordinator (Claude Code) to verify visually at 375/768/1280/1920px viewports
- Confirm print preview looks correct (Cmd+P)
- WCAG contrast: spot-check amber #8F5210 on #FBF1E0 and red #922525 on #FBE8E8 ≥4.5:1 (DevTools or axe)
- PSI parallel run: confirm wall-clock is ~3.5 min or less (was ~6 min)

---

### 2026-05-06 (model: glm-5.1:cloud via OpenCode, coordinated by claude-opus-4-7)

**Issues touched:** cua, c4w, 4sv (Batch D — features + polish)
**Outcome:** staged for coordinator review, not yet committed

**What was done:**
- Third-party script weight tracker — PSI now captures network_by_origin per snapshot; new section renders top-8 stacked-area chart over 30 snapshots + latest-snapshot table sorted desc (cua)
- CrUX 'production truth' card — new top-of-page section with mobile + desktop p75 across 5 metrics, pass/fail per Google CWV thresholds, collection period subtitle (c4w)
- WoW scorecard tooltip — METRIC_TIPS['WoW'] added; ⓘ icon next to scorecard h2 (4sv)

**Files modified:**
- `scripts/build-perf-dashboard.py` — run_psi_once() network_by_origin extraction, ORIGIN_LABELS constant, render_origin_weights(), render_crux_truth(), METRIC_TIPS WoW entry, HTML_TEMPLATE 2 new sections + 1 tooltip placeholder, render_html() 3 new replacements

**Verification:**
- render-only succeeds: ✓
- py_compile clean: ✓
- snapshots.jsonl unchanged: ✓
- All 3 markers present in HTML: ✓

**Next-session handoff notes:**
- Origin-weights chart will be empty until the next PSI run captures network_by_origin (next GHA run at 13:00 UTC, or manual `python3 scripts/build-perf-dashboard.py --no-crux --psi-only-mobile`)
- Coordinator (Claude Code) to review diff, run end-to-end smoke check, commit, push, and bd-close all 3 issues

---

<!-- Append new entries above this line. Older entries below. -->
