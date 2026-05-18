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
