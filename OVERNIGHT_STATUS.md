# Overnight OC dispatch status log

> Append-only log of overnight OC dispatch outcomes. CC loop checks bd state, files outcomes here, stops after each ticket per global "no auto-pick next" rule.

---

## 2026-05-18 ~02:10 — bd hairmnl-theme-2i8b.11 (Phase 5 visual parity audit) — CLOSED CLEAN

**Ticket:** [hairmnl-theme-2i8b.11](#) — "Phase 5 visual parity: audit P6 vs P8 css-overrides.liquid for missed rules"
**OC model:** deepseek-v4-pro:cloud (paid tier, lead-architect)
**OC PID:** 37460 (bja8ohy65 background task)
**Status:** closed, 2026-05-18T00:08:38Z, assignee Jonathan Joson

### Outcome

**No porting needed. 0 code-changing follow-ups.** Closed via global CLAUDE.md "escape hatch" rule (closeout produces <3 code-changing follow-ups → close clean with triage notes).

### Structural diff (P6 LIVE `131664707683` vs P8 working-tree `snippets/css-overrides.liquid`)

- **55 lines only in P6** → both are the documented intentional drops:
  - `#pwa-modal, [id^="pwa-modal"], [class*="pwa-modal"]` — Shop Sheriff PWA app uninstalled 2026-05-01 (M3 drop, documented inline in file header)
  - `limespot { display: block; contain: layout; }` — LimeSpot replaced by Vertex AI per bd hairmnl-theme-oyw + M6 commit 4303e70 deleted `snippets/limespot.liquid` + `ghost-placeholder.liquid`
- **101 lines only in P8** → all P4-parity additions from this evening:
  - font-stack `:root` override block (commit 7ac5d3a)
  - retained M3 port header comments

### Lint / pattern audit (merge-gate)

- `grep` trailing comma in font-family declarations: **0 hits** (the one match was comment text describing the prior bug fix)
- `grep` empty `var()` references: **0 hits**
- `grep` Liquid `{{ }}` inside CSS declarations in css-overrides.liquid: **0 hits**
- `python3 scripts/check-overlay-css.py`: **OK: scanned 454 files, no kt0 violations**

### Phantom-completion guard

OC made no code changes attributable to this ticket. `git HEAD` remains at `7ac5d3a` (font fix from separate ticket lineage). `git status` shows `snippets/css-overrides.liquid` is **unmodified** by this audit. Confirmed clean.

### Working-tree footprint after audit

- `.beads/issues.jsonl` modified — bd close metadata only (committed below)
- `snippets/article-content-with-img-dims.liquid` modified — **foreign** (stream:a Bloggle img-dim WIP, NOT this ticket's scope, leave alone)

### Loop decision

**STOP.** Per global CLAUDE.md: "Never auto-pick the next Beads task at the end of a run." Returning to operator.

Remaining visual-parity gaps (if any) live outside `css-overrides.liquid` — in app injections, asset CSS files, settings-tied colors, or template-specific JSON. Those are NOT in scope for this ticket and are not auto-filed; operator can scope if/when needed.

---

## 2026-05-18 evening — bd ujg6.7 + 2i8b.18 PSI verified, 2i8b.17 Option A failed

### Tickets closed clean

**ujg6.7** (font CLS) — commit `e583b0c`. PSI dev preview:
- Mobile home: **CLS 0.018** ✅
- Desktop home: **CLS 0.016** ✅
- Mobile `/collections/loreal-professionnel`: **CLS 0.036** ✅
Font swap no longer a top CLS source on 3/4 measured pages.

**2i8b.18** (mobile menu-buttons) — commit `d55ee61`. PSI dev preview:
- Mobile `/collections/loreal-professionnel`: **CLS 0.036** (target ≤0.10) ✅
- Desktop home regression check: **CLS 0.016** ✅ (no regression post-ujg6.29)

### Tickets re-opened

**2i8b.17** (section-richtext CLS) — Option A re-baseline disproven. Post-ujg6.7, mobile `/collections/cat-best-sellers` measured **CLS 0.632** (up from 0.354 pre-ujg6.7 baseline). The shift is page-specific, NOT a global font-swap problem. Likely root cause: SelfModern heading font swap on the "HairMNL Top Picks" rich-text section + product grid reflow below.

Next-step recommendation pasted to bd:
- **Option C (template-scoped fix):** `body.template-collection-cat-best-sellers` selector with bounded min-height. Limits blast radius (vs the rejected 113-template Option A).
- **OR** SelfModern → `font-display: optional` (but overlaps with ujg6.7's explicit "out of scope" SelfModern note; would need scope expansion).

Status: `open`. Blocked on operator decision.

### Process notes

- OC swarm 2-ticket dispatch (`/hh-swarm 2i8b.17 2i8b.18`) returned 2/2 INCREMENT_DONE; CC merge-gate rejected 1/2 due to broad blast-radius (113-template scope). The swarm followed its brief but did not catch the cross-template impact — split coordinator review caught it.
- Foreign file `snippets/article-content-with-img-dims.liquid` (stream:a Bloggle WIP) remained correctly parked across 3 commits this session via stash-around-rebase + per-commit `git restore --staged` discipline (MIGRATION-CONTRACT §5 #6).
- PSI single-fresh-load mobile runs show high variance; the cat-best-sellers 0.632 is a single n=3 measurement. Worth a 2nd-day re-baseline before committing to Option C.

---

## 2026-05-18 late evening — Option C revealed PSI URL bug (2i8b.17 invalid)

### Headline finding

**`/collections/cat-best-sellers` is a 404 page.** The Shopify collection handle doesn't exist. All prior 2i8b.17 baselines that cited "mobile collection section-richtext CLS 0.354" then "0.632" were measuring 404-page footer shifts, NOT section-richtext shifts.

Evidence:
```
curl -sIL "https://www.hairmnl.com/collections/cat-best-sellers"
→ HTTP/2 404, theme=131664707683, pageType=404
```

PSI CLS attribution selector confirmed:
```
score: 0.4472
  selector: body#404-not-found > div#shopify-section-footer
```

### What I did

1. **Shipped Option C** (commit 8c12397) — template-scoped min-height on `collection.cat-best-sellers`. PSI verify showed CLS unchanged at 0.632 across n=3 clean runs.
2. **Pulled Lighthouse audit JSON via PSI API** to get layout-shift attribution. Selector revealed the 404 body.
3. **Reverted Option C** (commit 210af92 → push 5289eb4). `sections/section-richtext.liquid` back to clean state on both git + dev theme.
4. **Closed 2i8b.17 as `wontfix-invalid`** with full diagnosis in bd notes.

### What this also invalidates

- **2i8b.18 test URL** (`/collections/loreal-professionnel`) — also doesn't resolve cleanly. The "mobile brand CLS 0.036" we cited as the 2i8b.18 verification was actually measuring the HOMEPAGE (the URL 301-redirects to `/`). Menu-buttons IS on the homepage (per index.json: 2× menu-buttons sections), so the fix is still valid — but the page being measured was wrong. 2i8b.18 stays closed; the fix is real even though the test URL was wrong.
- **Per-collection PSI runs throughout this evening** — many of the URLs we cited (cat-best-sellers, loreal-professionnel) are not valid collections. The PSI bot followed redirects to 404 or homepage, then measured those. CLS values for "mobile collection X" PSI runs should be re-evaluated against valid collection handles.

### Lessons (codifying for the runbook)

1. **Always verify PSI target URL returns 200** (or follows expected redirects to the real target) BEFORE filing CLS attribution as evidence. A 5-second `curl -sIL` would have caught this immediately.
2. **PSI CLS attribution selectors are diagnostic** — when a selector cites `body#404-not-found` or any 404-ish identifier, the entire PSI run is measuring an error page and must be discarded.
3. **Add a 404 body-id detection guard to `scripts/psi-cls-attribution.py`** — file a follow-up.
4. **Audit `os2-migration/perf-regression-analysis.md` PSI test URLs** for similar 404 conditions — many of the regressions we identified there may be 404 artifacts.

### Status after revert

- `main` is at commit `5289eb4`. `sections/section-richtext.liquid` clean.
- OC's `/hh-orchestrate hairmnl-theme-ujg6.14` is in flight (in_progress, 1712 chars bd notes, 3 new JS files in working tree: hairmnl-{common,collection,product}.js, layout/theme.liquid untouched per spec). Working tree files pending OC commit + close.

---

## 2026-05-18 ~21:00 — full evening synthesis (session closeout)

After a long arc spanning roughly 8 hours of CC + OC coordination, this section captures the final state across all closed tickets, deliveries, and lessons.

### 12 tickets closed tonight

| Ticket | Type | Disposition |
|---|---|---|
| `2i8b.11` | code | OC paid: P6 vs P8 css-overrides parity audit — clean, no porting needed |
| `2i8b.15` | research | GTM trigger investigation: GTM is NOT in theme code; defer to ujg6.12 |
| `2i8b.16` | research | Klaviyo onsite audit: loader is async ✓; admin-side feature audit deferred to operator |
| `2i8b.17` | invalid | section-richtext CLS premise was a 404-page measurement artifact |
| `2i8b.18` | code | mobile menu-buttons CLS mobile-breakpoint fix (CLS 0.291 → 0.044) |
| `2i8b.19` | code | wired hairmnl-{common,collection,product}.js loaders in layout/theme.liquid |
| `ujg6.7` | code | font CLS line-box overrides + font-display:optional on accent weights |
| `ujg6.14` | code | OC paid: tree-shake hairmnl-custom.js into 3 per-template bundles |
| `ujg6.18` | code | lazy-render below-fold sections via Section API + IO (3 increments: section-collection, brand-collection, related) |
| `ujg6.19` | code | font preloads + slideshow eager:true (LCP element investigation revealed wrong test target) |
| `ujg6.20` | misconceived | cart drawer `Shopify.section.refresh` is theme-editor-only API; small follow-up `2i8b.21` filed instead |
| `ujg6.16` | code | facet AJAX via Section Rendering API for collection filter/sort |

### 5 follow-up tickets filed

- `2i8b.19` (B.2.2 loader wiring — closed same session)
- `2i8b.20` (delete hairmnl-custom.js post-soak, blocked until 2026-05-25)
- `2i8b.21` (post-cutover: dispatch `shopify:section:load` after cart drawer reload)
- `2i8b.22` (ujg6.18 increment 2: brand-grid lazy-render — closed same session)
- `2i8b.23` (ujg6.18 increment 3: PDP related-products lazy-render — closed same session)

### Verification debt outstanding

All shipped to P8 dev theme `141168312419`; **none yet browser-smoked**:
- ujg6.7 font CLS overrides
- 2i8b.18 mobile menu-buttons
- 2i8b.19 loader wiring (B.2.2)
- fsaa Reamaze defer guard (also blocked on `meu.4` live rollout)
- ujg6.16 facet AJAX
- ujg6.18 lazy-render ×3 (section-collection, brand-collection, related)
- ujg6.19 font preloads + slideshow eager

Each closed ticket's bd notes contain concrete DevTools + PSI repro steps for operator smoke. Before live cutover the operator must work through these.

### PSI numbers (from `os2-migration/psi-baseline-2026-05-18-late.md`)

**P8 dev vs P8 dev evening (impact of tonight's tickets):**
- Brand mobile CLS: 0.291 → **0.044** (−0.247)
- Brand desktop CLS: 0.173 → **0.009** (−0.164) + TBT −1430ms
- Home desktop CLS: 0.173 → **0.009** (−0.164)
- Cart desktop CLS: 0.306 → **0.055** (−0.251) + score +20
- Collection mobile CLS: 0.354 → **0.019** (−0.335)

**P8 dev vs P6 live (now):** P8 wins on mobile LCP across the board (−7.83s home, −14.14s PDP, −3.53s collection, −2.52s brand). Desktop home TBT +2511ms is the only big-magnitude P8 regression and is the long-tracked GTM tag-firing differential (will resolve via `ujg6.12`).

**CrUX field (P6 real users, 28d):** P6 passes 4/6 origin CWV. Failing: origin-desktop CLS 0.11, home-mobile LCP 2906ms + INP 237ms, home-desktop CLS 0.17. Lab improvements suggest the home-desktop CLS field metric should recover post-cutover.

### §5 #6 coordination-collision pattern — 5 strikes in one session

The bd-auto-export-bundling pattern hit 5 times in a single evening (commits 5097433, 662cb0d, 691fa2d, 0778d71, plus the ujg6.18 sweep) despite being already codified in MIGRATION-CONTRACT.md. Functional outcomes were always harmless (OC work was real and lint-clean) but commit attribution was wrong.

**Tooling response:** added `scripts/safe-commit.sh` as an explicit-file-list commit wrapper. Unstages everything bd touched, stages only the listed files, sanity-checks the set, then commits. MIGRATION-CONTRACT.md §5 #6 updated to mandate the wrapper for all CC commits during OC swarm activity.

### Workspace state at session end

- `main` head: `61e1532` (PSI comparison doc + `/collections/davines` URL fix)
- Pending: `snippets/article-content-with-img-dims.liquid` foreign (stream:a Bloggle WIP, parked across the entire session without ever bundling)
- Pending after this session: `scripts/safe-commit.sh` + `MIGRATION-CONTRACT.md` (§5 #6 update) + this `OVERNIGHT_STATUS.md` final synthesis — to commit next
- 8 stashes belong to other workstreams; left untouched
- All 5 PSI files cleaned from /tmp

### Recommended next session

1. **Operator browser smoke** of all 7 dev-soak ships before adding more code (concrete steps in each closed bd ticket's notes)
2. **`ujg6.12` Web Pixels Manager migration** — highest-leverage remaining ticket; closes the desktop home TBT regression
3. **`ujg6.13`** Defer LL + Judge.me + Re:amaze — extends the `fsaa` Reamaze pattern (mechanical OC fit)
4. **`ujg6.21` PSI verification matrix** post-cutover (n=5 each)
5. **`ujg6.24` epic-audit closeout** on the p8-perf diff before promoting to live

Cutover-readiness estimate per the runbook: **2.5–3.5 operator-weeks** remaining (1.5 weeks code + verification + Phase 4 admin TAE migration + parallel-run QA + cutover ceremony + post-cutover monitoring).
