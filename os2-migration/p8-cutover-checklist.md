# P8 cutover checklist — Rule 10 gate tracking

> **Purpose**: Track the four `MIGRATION-CONTRACT.md` Rule 10 preconditions for any
> P8 push to live theme `131664707683`. **All four phases must be checked off** before
> the operator gives `--allow-live` approval.
>
> Created: 2026-05-18 PM after the cache-shadow escalation + emergency revert (commit `49ae3dc`).
> Authoritative until P8 cutover is complete.

---

## How to use this file

- Edit it directly. Tick boxes via `- [x]`.
- Each phase has its own section. Phases must complete IN ORDER (A → B → C → D).
- Each item has a definition of done. If an item can't be checked, document why in
  the "Blockers" subsection below the phase.
- The operator reviews this file in the cutover PR. Unchecked items = no `--allow-live`.

---

## Phase A — Re-orient (no production impact)

Goal: P8 session has the new contract rules loaded and the dev theme synced
against the post-revert live baseline.

### A.1 — Read mandatory context

- [x] Read `MIGRATION-CONTRACT.md` **end-to-end**, with special attention to:
  - Rules 5–10 (cache-shadow defense, added 2026-05-18 PM)
  - "Incident log" section (both 2026-05-18 events)
  - "What MIGRATION ports must preserve" — non-negotiables list (now includes
    8 asset_url loads + 5 renders + infrastructure items)
- [x] Read `os2-migration/intentionally-orphan.txt` (snippet allowlist)
- [x] Read `os2-migration/intentionally-orphan-assets.txt` (asset allowlist —
      new file from 2026-05-18 PM)
- [x] Run `python3 scripts/check-snippet-wiring.py` locally to confirm both
      checks pass on `main` HEAD (snippets: 0 blocking; assets: 0 blocking).

### A.2 — Sync dev theme to post-revert live baseline

- [x] `shopify theme pull --theme=131664707683 --path=/tmp/p8-live-snapshot --nodelete`
- [x] Diff `/tmp/p8-live-snapshot/layout/theme.liquid` against
      `git show 6d4a246:layout/theme.liquid`. Should match byte-for-byte
      (the revert restored to this commit's state).
- [x] Push `main` HEAD to dev theme `141168312419`:
      `shopify theme push --theme=141168312419 --nodelete`
- [x] Cache-bypass curl on dev preview URL, confirm dev = live for `<script src>` +
      `<link rel="stylesheet">` tags. Reference:
      `https://creations-gdc.myshopify.com/?preview_theme_id=141168312419&_cb=$(date +%s%N)`

### A.3 — Behavior inventory

- [x] Refresh `os2-migration/custom-theme-js-audit.md` (from `04e6f9e`). Confirm
      every behavior in `custom-theme.js` is classified as either:
      - **KEEP in bundle** — implementing in P8 bundled theme.js
      - **MIGRATE TO TAE** — moving to a Shopify app extension
      - **DROP** — no longer needed (must document why)
- [x] Same for `shop.js` and `jquery.min.js`. (Jquery is mostly required by
      app snippets; check the app-compatibility-matrix.md for TAE coverage.)
- [x] `lazysizes.js` is mostly replaceable by native `loading="lazy"`. Confirm
      the `.fade-in` opacity-flip dependency on the `lazyloaded` class is
      resolved (either by removing `.fade-in` or replacing the JS hook).
- [x] `custom-theme.css` (5K LoC P6 brand bundle): inventory each rule's fate
      — port to `theme.css`, port to a section's `{% stylesheet %}` block, or
      retire.

### Blockers (Phase A)

_(Document anything that prevents Phase A completion. Operator reviews.)_

---

## Phase B — Build the bundled `theme.js`

Goal: A new `assets/theme.js` (or `assets/hairmnl-theme.js`, name TBD) that
replaces ALL the dropped legacy assets functionally. Dev-theme-only — no live
impact.

### B.1 — Bundle architecture

- [ ] Decide bundle target: extend existing `theme.js`, or new file like
      `hairmnl-custom.js`. Document choice in the PR. (Note: `hairmnl-custom.js`
      already exists from the P4 spike `64b034f` but is `[P8-PENDING]` in the
      asset allowlist — currently not loaded.)
- [ ] Bundle MUST replace every behavior marked "KEEP in bundle" in Phase A.3.
- [ ] Bundle MUST NOT exceed the budget. Reference: `bd ujg6.28` cited
      `custom-theme.js` at 456 KB as the source of ~85% of TBT regression.
      Target a budget that's substantially below 456 KB (proposed: ≤120 KB
      minified). Document the achieved size in the PR.

### B.2 — Replace specific behaviors

Each behavior gets its own checkbox. Add rows as Phase A.3 inventory uncovers
more.

- [ ] Megamenu dropdown JS (replace `custom-theme.js` handler)
- [ ] Slider / carousel init (Swiper) — currently initialized by `custom-theme.js`
- [ ] Sticky filter bar — `custom-theme.js`
- [ ] Product tabs v1 — `custom-theme.js`
- [ ] Header mobile slide rule — `custom-theme.js`
- [ ] Cart drawer ATC behavior — currently in `hairmnl-custom.js` section 7
      (from `416b58b`, `6409df8`)
- [ ] Image lazy loading — replace `lazysizes.js` with native `loading="lazy"`
      everywhere; resolve the `.fade-in` opacity flip dependency.
- [ ] jQuery removal — every snippet/section that uses `$(...)` either
      replaced with vanilla JS (e.g., `2v8p` precedent in
      `snippets/collection-sorting-custom.liquid`) OR keeps jQuery as a
      dependency (document why in the PR).
- [ ] Other behaviors from Phase A.3 inventory: _(add)_

### B.3 — Test on dev theme

- [ ] Bundle pushed to dev theme `141168312419`.
- [ ] All `intentionally-orphan-assets.txt` entries that say `[P8-PENDING]` are
      now either wired or moved to `[DEAD]`.
- [ ] `python3 scripts/check-snippet-wiring.py` passes on the dev-theme branch.
- [ ] Smoke test on dev preview: homepage, PDP, collection, /cart, blog,
      search, account. All major interactions work:
      - [ ] Megamenu dropdowns open + close
      - [ ] Hero carousel auto-advance + click controls
      - [ ] Best Sellers slider scrolls horizontally
      - [ ] Product card images load (no permanent invisibility)
      - [ ] PDP: image zoom (PhotoSwipe), thumbnail carousel, variant selector
      - [ ] Cart drawer opens on ATC + manual click
      - [ ] /cart page renders styled
      - [ ] Sticky filter bar pins on scroll on collection pages
      - [ ] Mobile nav slides correctly

### Blockers (Phase B)

_(Document anything that prevents Phase B completion. Operator reviews.)_

---

## Phase C — Side-by-side dev vs live verification

Goal: Operator confirms the new bundle delivers visual + behavioral parity vs
the current live theme (pre-P4 baseline).

### C.1 — Visual parity

- [ ] Operator opens two browser windows in incognito:
      - Window 1: `https://www.hairmnl.com/?_cb=$(date +%s%N)` with
        Cache-Control: no-cache (live = pre-P4 baseline)
      - Window 2: `https://creations-gdc.myshopify.com/?preview_theme_id=141168312419&_cb=$(date +%s%N)` (dev = new P8 bundle)
- [ ] Walk through these templates in BOTH windows and confirm visual + behavior
      parity:
      - [ ] Homepage (`/`) — hero, menu buttons, Best Sellers, etc.
      - [ ] PDP — e.g., `/products/davines-purifying-shampoo-for-oily-or-dry-dandruff-250ml`
      - [ ] Collection — `/collections/all` + a branded subcollection
      - [ ] /cart — with at least one item
      - [ ] Blog index + an article
      - [ ] Search results page
      - [ ] Customer account (if applicable)
      - [ ] /pages/hairmnlstudio-main (salon page)

### C.2 — PSI baseline

- [ ] Run `./scripts/run-psi.sh https://www.hairmnl.com/ desktop 3` and
      `mobile 3` — that's the LIVE baseline.
- [ ] Run same on dev preview URL — that's the NEW baseline.
- [ ] Compare median scores. Accept if dev is no worse than live on:
      - [ ] LCP (median Δ ≥ -300 ms acceptable — i.e., dev can be up to 300ms slower)
      - [ ] CLS (median Δ ≥ -0.05 acceptable)
      - [ ] TBT (median Δ ≥ -200 ms acceptable)
      - [ ] Overall PSI score (Δ ≥ -3 points acceptable)
- [ ] Document the comparison table in the cutover PR body.

### C.3 — Asset diff (Rule 8)

- [ ] On dev preview URL, cache-bypass fetch and capture all `<script src>`
      + `<link rel="stylesheet">` tags. Same for live URL. Diff them in the
      cutover PR body per Rule 8.
- [ ] Expected diff: dev loads new bundle, NOT loads custom-theme.js +
      shop.js + jquery.min.js + lazysizes.js (or whichever the bundle replaces).
      Each "removed" line must have a Wiring Delta justification.

### Blockers (Phase C)

_(Document anything that prevents Phase C completion. Operator reviews.)_

---

## Phase D — Controlled cutover

Goal: A single PR + push that flips live to the new bundle, with rollback ready.

### D.1 — PR construction

- [ ] PR title starts with `feat(stream:b): P8 cutover — bundled theme.js + ...`
- [ ] PR body MUST contain:
      - [ ] **Wiring Delta** table (Rule 2 — every render/asset_url/script change)
      - [ ] **Live-state HTML diff** (Rule 8 — script + stylesheet tag diff)
      - [ ] **PSI comparison table** from Phase C.2
      - [ ] **Phase B.2 behavior verification log** (Phase C.1 checkboxes)
      - [ ] Reference to this checklist with all boxes ticked
      - [ ] Reference to the Emergency Revert Playbook from MIGRATION-CONTRACT.md
            (if cutover fails, revert is: restore `layout/theme.liquid` to
            commit `6d4a246`, push with `--only=layout/theme.liquid`)
- [ ] PR review by stream:a session (if available) for outside-eye check
      against MIGRATION-CONTRACT.md rules.

### D.2 — Pre-flight (Rule 7)

- [ ] `shopify theme pull --theme=131664707683 --only=layout/theme.liquid --path=/tmp/preflight`
- [ ] `diff /tmp/preflight/layout/theme.liquid layout/theme.liquid` — confirm
      no divergence. If divergent: STOP, investigate (cache is hiding something).

### D.3 — Operator approval

- [ ] Operator gives explicit `--allow-live` approval in chat (Rule 10).
      No implied approval. No "go ahead based on the PR." A direct chat message.

### D.4 — Cutover push

- [ ] `shopify theme push --theme=131664707683 --allow-live --only=layout/theme.liquid --only=assets/<new-bundle>.js [other files...] --nodelete`
- [ ] Note the exact push command in the PR body (for audit trail).

### D.5 — Post-push verification (Rule 5)

- [ ] Wait 60–120 seconds.
- [ ] `curl -sL "https://www.hairmnl.com/?_cb=$(date +%s%N)" -H "Cache-Control: no-cache" > /tmp/post-cutover.html`
- [ ] Diff `<script src>` and `<link rel="stylesheet">` tags vs the expected
      list from D.1's Wiring Delta. If a tag from pre-cutover theme.liquid
      persists, the cache hasn't rolled — wait longer, repeat.
- [ ] Operator visual confirmation in incognito on live URL. Same template
      walkthrough as Phase C.1.

### D.6 — Commit + push to origin/main

- [ ] After D.5 passes: `git add -A && git commit -m "feat(stream:b): P8 cutover ..."`
      with the full Wiring Delta in the commit body.
- [ ] `git pull --rebase && git push`.

### D.7 — Bd hygiene

- [ ] Close all relevant `ujg6.*` + `2i8b` child tickets with the cutover
      commit hash in the closing notes.
- [ ] Append an "Incident log" entry to `MIGRATION-CONTRACT.md` describing
      the successful cutover (no errors) — completes the documentation.
- [ ] Future: update `CLAUDE.md` and `MIGRATION-CONTRACT.md` to remove the
      "live = Pipeline 6.1.3" assumption, since live will now be P8.

### D.8 — Rollback readiness (NOT triggered unless something breaks)

If anything looks wrong in D.5 or D.6:

- [ ] Execute the Emergency Revert Playbook from MIGRATION-CONTRACT.md:
      1. `git show 6d4a246:layout/theme.liquid > layout/theme.liquid`
      2. `python3 scripts/check-snippet-wiring.py` — confirm pass
      3. `shopify theme push --theme=131664707683 --allow-live --only=layout/theme.liquid`
      4. Wait 60–120s, cache-bypass verify
      5. Commit with `revert(stream:b/EMERGENCY): ...` prefix
- [ ] File a bd ticket documenting what went wrong; reopen the affected
      ujg6 / 2i8b tickets.

### Blockers (Phase D)

_(Document anything that prevents Phase D completion. Operator reviews.)_

---

## Status summary (for operator at-a-glance)

| Phase | Status | Date completed |
|---|---|---|
| A. Re-orient | COMPLETE | 2026-05-18 |
| B. Build bundle | NOT STARTED | — |
| C. Side-by-side verify | NOT STARTED | — |
| D. Cutover | NOT STARTED | — |

When all four phases are checked off, this file's status row updates and the
operator gives `--allow-live` approval.

---

## Notes

- This checklist is the authoritative gate for Rule 10. If a step here is
  skipped, the gate is not open — full stop.
- If the checklist itself needs amendment (a step is wrong or missing),
  amend it in a separate PR BEFORE acting on the gate. Don't edit the
  checklist mid-cutover.
- Two AI sessions touching `main` simultaneously is what produced today's
  cache-shadow escalation. Per MIGRATION-CONTRACT.md coordination protocol §5,
  the stream:a session does not push to live theme.liquid while Phase D is
  in flight.
