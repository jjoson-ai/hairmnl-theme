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
