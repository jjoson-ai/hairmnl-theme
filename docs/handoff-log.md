# Coordinator Handoff Log

Append-only log of coordinator sessions. Newest entries at the top.

Format spec: see `docs/coordinator-handoff.md` §10.

### 2026-05-06 (model: glm-5.1:cloud via OpenCode, coordinated by claude-opus-4-7)

**Issues touched:** dy0, 0ru (Batch G2 — iterative debug of Bug 2 + Bug 3)
**Outcome:** staged for coordinator review, not yet committed

**What was done (Bug 2 — dy0):**
- Root cause identified via v7 diagnostic (`pre_gen=0 post_gen=12 post_gen_after=0`): the `article.content` enters the snippet with `<a>` tags properly closed by Shopify's sanitizer, but the `<img ` split-and-reassemble dimension-injection algorithm loses the `>` that closes parent `<a>` tags. This creates `"<img` malformations in the output.
- Fix: three-pass repair in `snippets/article-content-with-img-dims.liquid`:
  1. Pass 1: Pre-split repair for known `target="_blank"<img` variants in raw content
  2. Pass 2: Post-reassembly general repair `"<img` → `"><img` on final output (catches 12 instances the split algorithm introduces)
  3. Pass 3: Convert `<div style="text-align: center;">` → `<p style="text-align: center;">` (and `</a></div>` → `</a></p>`) — fixes Bloggle image collapse where centered `<div>` wrappers following `<ul>` lists hide images
- Diagnostic markers removed from production code
- Known artifact: `<img alt="HairMNL">` (no `src`) appears in some Bloggle articles as inline branding pixel — pre-existing, not introduced by this change

**What was done (Bug 3 — 0ru):**
- Root cause: schema change `richtext`→`html` allows HTML content, but some products store Liquid template syntax (`{{ product.metafields.hmnl.<key> | metafield_tag }}`) in the setting, expecting Shopify to evaluate it. Settings values are NOT processed as Liquid.
- Fix: In `snippets/product-tabs.liquid`, both tabs and accordions render paths now detect `product.metafields` in `_content`, dynamically extract namespace and key, resolve to the actual metafield value, and output directly via `{{ _mf }}` (not `metafield_tag`, which wraps in `<span>` and escapes HTML).
- Namespace is dynamically extracted (not hardcoded to `hmnl`), supporting any metafield namespace.

**Files modified:**
- `snippets/article-content-with-img-dims.liquid` — three-pass repair (Pass 1: pre-split, Pass 2: post-reassembly, Pass 3: div→p conversion)
- `snippets/product-tabs.liquid` — metafield resolution in both tabs and accordions render paths
- `docs/handoff-log.md` — this entry

**Verification:**
- Bug 2: v7 diagnostic confirmed `post_gen=12, post_gen_after=0` — all 12 malformations caught and repaired
- Bug 2: Images load correctly on sulfate-free shampoo article (15 images, previously broken after `<ul>` lists)
- Bug 3: Accordion tabs on K18 product page render actual metafield content (not escaped HTML, not literal `{{ ... }}` text)
- Production code has no diagnostic markers

**Next-session handoff notes:**
- Coordinator (Claude Code): push to live theme 131664707683 with --allow-live, commit, push to GitHub, bd close dy0 0ru
- Known Bloggle artifact: `<img alt="HairMNL">` (no src) renders as broken image icon in some article text — this is a Bloggle app content issue, not a theme bug
- The `<img>` split algorithm bug (losing `>` from parent tags) should be considered for a future refactor — the Pass 2 post-repair is a safety net, not a structural fix

---

### 2026-05-06 (model: minimax-m2.7:cloud via OpenCode, coordinated by claude-opus-4-7)

**Issues touched:** l3g (in progress) + 3 new follow-ups: hairmnl-theme-4r8, hairmnl-theme-t4m, hairmnl-theme-miy
**Outcome:** dashboard query staged; GTM container version created in new workspace, NOT YET PUBLISHED — coordinator review pending

**What was done:**
- Updated dashboard JS error query at scripts/build-perf-dashboard.py:503 to filter both `js_error` and `hairmnl_js_error` event names
- Created GTM workspace `fix-js-error-trigger-2026-05-06` (workspace ID: 198) from live v140
- In new workspace: updated tag 776 firing trigger from [2147479573 (Window Loaded)] → [772 (Custom Event - hairmnl_js_error)]. DLV verification: all 3 DLVs (js_error_type, js_error_message, js_error_source) read correct post-rename fields (error_type, error_message, error_source) ✓
- Created GTM Container Version 141 in the new workspace (name: "Fix JS Error tag trigger (bd hairmnl-theme-l3g)"). Coordinator review URL: https://tagmanager.google.com/#/container/accounts/4702257664/containers/12266146/versions/141
- Filed 3 new bd issues for orphan-trigger tags 12 (Conversion Linker, P1 hairmnl-theme-4r8), 415 (Klaviyo Form Listener, P1 hairmnl-theme-t4m), 94 (TrafficGuard, P2 hairmnl-theme-miy)
- Wrote replayable script scripts/gtm-fix-js-error-tag-2026-05-06.py

**Files modified:**
- scripts/build-perf-dashboard.py — 1-line query update
- scripts/gtm-fix-js-error-tag-2026-05-06.py — new file, replayable fix script
- .beads/issues.jsonl — l3g claimed, 3 new issues (4r8, t4m, miy)
- docs/handoff-log.md — this entry

**Verification:**
- py_compile clean: ✓
- render-only succeeds: ✓
- snapshots.jsonl unchanged: ✓
- New GTM workspace + version exist: ✓ (verified via API — workspace 198, version 141)
- Container NOT yet published: ✓

**Next-session handoff notes:**
- **COORDINATOR ACTION REQUIRED:** review the GTM Container Version diff at https://tagmanager.google.com/#/container/accounts/4702257664/containers/12266146/versions/141; if the change is exactly 1 tag (776) with trigger change to 772 (no other surprises), publish via the GTM admin UI.
- After publish: synthetic-error test in storefront incognito + DevTools to verify GA4 DebugView shows real error_type/error_message/error_source on `js_error` events.
- Wait ~24h, then `python3 scripts/build-perf-dashboard.py --no-crux` to confirm dashboard surfaces real errors. Legacy (not set) rows age out of the 7-day window after 7 days.
- Then `bd close hairmnl-theme-l3g`. The 3 new bd issues (4r8, t4m, miy) stay OPEN — separate follow-up sessions.

---

### 2026-05-06 (model: glm-5.1:cloud via OpenCode, coordinated by claude-opus-4-7)

**Issues touched:** 236 (Batch E — per-template CWV slicing)
**Outcome:** staged for coordinator review, not yet committed (theme push pending)

**What was done:**
- Theme: web-vitals-reporter.liquid now includes `template: {{ template | json }}` in the GA4 event payload
- Dashboard: query_ga4_rum() now queries customEvent:template; new top_templates field on the response
- New render_top_templates() helper; new "Top friction templates" section in HTML showing LCP/INP/CLS per template
- Empty-state messages handle the period before GA4 admin registration + 24h data accumulation

**Files modified:**
- `snippets/web-vitals-reporter.liquid` — added template field to event payload
- `scripts/build-perf-dashboard.py` — query_ga4_rum() per-template query, render_top_templates(), HTML_TEMPLATE new section, render_html() replacements

**Verification:**
- render-only succeeds: ✓
- py_compile clean: ✓
- snapshots.jsonl unchanged: ✓
- New section renders empty states (expected — no data yet): ✓

**Next-session handoff notes:**
- **MANUAL ACTION (USER)**: register `template` as a custom dimension in GA4 admin: GA4 → Admin → Custom Definitions → Create custom dimension → Dimension name: `template`, Scope: Event, Event parameter: `template`. Required for the dashboard query to return data.
- Coordinator (Claude Code): review diff, push web-vitals-reporter.liquid to draft theme 140785582179, smoke test in Brave, push to live 131664707683 with --allow-live, commit, push, bd close 236
- Per-template data will start populating ~24h after both: (a) custom dimension registered, (b) live theme push of the new snippet

---

### 2026-05-06 (model: claude-opus-4-7) — coordinator review of Batch E (LIVE THEME PUSH)

**Issues touched:** 236 (Batch E — per-template CWV slicing)
**Outcome:** shipped to live (theme 131664707683) and to GitHub Pages

**What was done:**
- Reviewed OpenCode diff — exactly 1 line added in Liquid snippet (template field with comma fixup); Python additions match brief
- Pre-push diff check: ✓ surgical, no surprises
- Pushed `snippets/web-vitals-reporter.liquid` to draft theme 140785582179 (Claude Code)
- Smoke tested 4 templates via Brave + Claude-in-Chrome:
  - `/` → `template: "index"` ✓
  - `/cart` → `template: "cart"` ✓
  - `/collections/davines` → `template: "collection.brand.davines-sis"` ✓
  - `/products/...-thinning-hair` → `template: "product"` ✓
- Pushed `snippets/web-vitals-reporter.liquid` to live theme 131664707683 with --allow-live
- Closed 236

**Verification:**
- py_compile clean: ✓
- render-only succeeds (57,698 bytes): ✓
- "Top friction templates" h2 in HTML: ✓
- All __TOP_TEMPLATES_ placeholders replaced: ✓
- snapshots.jsonl unchanged: ✓
- Draft smoke test ✓ across 4 templates
- Live theme push ✓

**Next-session handoff notes:**
- **GA4 admin step DONE by user** — `template` custom dimension registered before this push.
- Per-template friction tables will populate once GA4 has ~24h of post-push data. First useful look: 2026-05-07 onwards.
- Bot URL `/products/davines-momo-shampoo` still redirects to `/` (issue `3q4`) — discovered during smoke test; admin-side fix.
- Sprint complete: 21 of 21 dashboard issues shipped (gjv + 18 dashboard sprint + 6o0 GHA debug + Batch D + Batch F + Batch E).
- gjv RUM verification still pending after 2026-05-12.

---

### 2026-05-06 (model: claude-opus-4-7) — coordinator review of Batch F

**Issues touched:** ofc, 2em (Batch F — A/B comparison + Slack alerts)
**Outcome:** shipped to GitHub Pages

**What was done:**
- Reviewed OpenCode diff — scope contained, all expected symbols present at expected line ranges
- ofc: `--compare <iso1> <iso2>` CLI; render_comparison() + find_snapshot_by_prefix() helpers; standalone HTML at dashboard/compare-{slug1}-vs-{slug2}.html with PSI mobile/desktop, GA4 RUM, CrUX mobile/desktop side-by-side; color-coded deltas via td.delta.improve/regress/muted
- 2em: evaluate_alerts() + post_alerts_to_slack() helpers; wired into main() after append_snapshot(); silently no-ops when SLACK_WEBHOOK_URL unset; covers RUM <75% good, RUM WoW drop >10pp, PSI mobile score regression >10, GA4 sampling, RUM volume drop ≥50%
- Test artifact dashboard/compare-2026-04-29-vs-2026-05-05.html (18KB) shipped as a working example

**Verification:**
- py_compile clean: ✓
- --render-only succeeds (54KB HTML): ✓
- --compare 2026-04-29 2026-05-05 generates 18KB comparison HTML: ✓
- evaluate_alerts() detects synthetic LCP regression at 50% good: ✓ ('🔴 *LCP* good% is 50.0%')
- snapshots.jsonl unchanged: ✓
- Closed ofc, 2em (already closed by OpenCode)

**Next-session handoff notes:**
- Slack alerts won't fire until user adds SLACK_WEBHOOK_URL secret (GHA + local). Coordinator should update .github/SECRETS.md to document the new secret post-merge (low priority — alerts are purely additive).
- A/B comparison is on-demand only — not wired into daily run. Use `python3 scripts/build-perf-dashboard.py --compare <prefix1> <prefix2>` to invoke; output goes to dashboard/compare-<slug1>-vs-<slug2>.html.
- Batch E (236 — per-template CWV slicing) brief at /tmp/oc-batch-E.md remains the next offload. Multi-file (theme + dashboard); coordinator handles draft→live theme push.

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

### 2026-05-06 (model: glm-5.1:cloud via OpenCode, coordinated by claude-opus-4-7)

**Issues touched:** ofc, 2em (Batch F — A/B comparison + Slack alerts)
**Outcome:** staged for coordinator review, not yet committed

**What was done:**
- A/B comparison mode: new `--compare <iso1> <iso2>` CLI; render_comparison() helper; standalone HTML at dashboard/compare-{slug1}-vs-{slug2}.html with PSI mobile/desktop, GA4 RUM, CrUX mobile/desktop side-by-side tables; color-coded deltas (ofc)
- Slack alerts: evaluate_alerts() + post_alerts_to_slack() helpers; wired into main() after append_snapshot(); skips silently when SLACK_WEBHOOK_URL unset; covers RUM <75%, RUM WoW drop >10pp, PSI score regression >10, sampling, volume drop (2em)

**Files modified:**
- `scripts/build-perf-dashboard.py` — new --compare CLI, render_comparison, find_snapshot_by_prefix, evaluate_alerts, post_alerts_to_slack, main() wiring

**Verification:**
- render-only succeeds: ✓
- --compare generates valid HTML (>18KB): ✓
- evaluate_alerts() detects synthetic regression: ✓
- py_compile clean: ✓
- snapshots.jsonl unchanged: ✓

**Next-session handoff notes:**
- For Slack alerts to fire: user must add SLACK_WEBHOOK_URL secret (GHA + local env) and update .github/SECRETS.md to reference it
- A/B comparison is on-demand only — not wired into daily run; user invokes via `python3 scripts/build-perf-dashboard.py --compare 2026-04-26 2026-05-05`
- Coordinator (Claude Code) to commit and push, bd close ofc + 2em

---

### 2026-05-06 (model: glm-5.1:cloud via OpenCode, coordinated by claude-opus-4-7)

**Issues touched:** jhb, dy0, 0ru (Batch G — three P0 production bugs)
**Outcome:** staged for coordinator review, not yet committed

**What was done:**
- jhb: Standardized 14-entry brand-prefix replace chain to use double quotes throughout in 2 files (product-grid-item.liquid:294 + product-grid-item-branded.liquid:187). Resolves the "Unexpected character é" Liquid parser error on Kérastase landing pages.
- dy0: Added a 4-pattern defensive replace chain at the top of article-content-with-img-dims.liquid to repair malformed target="..."<img> sequences before chunk-splitting. Repairs blog body images where the parent <a> tag is missing its closing > (10 of 11 broken on /blogs/hair-education/2026-best-in-beauty-hair-protocols-essentials).
- 0ru: Changed `"type": "richtext"` to `"type": "html"` for raw_content_1..5 in sections/product.liquid (5 changes) and sections/section-product.liquid (5 changes). Resolves the visible <ol><li> markup on PDP accordions.

**Files modified:**
- snippets/product-grid-item.liquid:294
- snippets/product-grid-item-branded.liquid:187
- snippets/article-content-with-img-dims.liquid:54
- sections/product.liquid (raw_content_1..5)
- sections/section-product.liquid (raw_content_1..5)

**Verification:**
- grep checks per DoD: ✓
- git diff scope contained to listed files: ✓
- snapshots.jsonl unchanged: ✓
- staged but not committed: ✓

**Next-session handoff notes:**
- Coordinator (Claude Code) to: pre-push diff check; push to draft theme 140785582179 (--only=<each>); smoke test in Brave on /collections/kerastase, /blogs/hair-education/2026-best-in-beauty-hair-protocols-essentials, and a PDP with tabs; push to live theme 131664707683 with --allow-live; commit + push to GitHub; bd close jhb dy0 0ru.
- Bug 3 caveat: existing escaped tab content stays escaped after schema change — merchant must re-save each affected product in theme editor for old data to re-render. If many products affected, follow-up with a bulk-unescape ticket.

---

<!-- Append new entries above this line. Older entries below. -->
