# Migration runbook v1 — Pipeline 6.1.3 → Pipeline 8.1.1

> **Status:** v1. Phase-by-phase playbook to execute IF a trigger fires (see `migration-triggers.md`) and the decision in `migration-decision.md` is re-confirmed.
> Ticket: `hairmnl-theme-80z0.6` (P2.3). Target: Pipeline 8.1.1.
> **No code in this doc.** Steps are executable as written by a future operator + Claude session.
> **Last updated:** 2026-05-17

---

## Pre-flight (before Phase 0)

Re-confirm the four gating conditions from `migration-decision.md` § "Decision authority + sign-off":
1. ☐ Trigger has fired and held for ≥14 days.
2. ☐ P1.3 perf delta confirmed not narrowed (re-run PSI baseline if last data >30 days old).
3. ☐ No Pipeline 9 announcement from Groupthought.
4. ☐ All 10 NEED-VERIFY apps in `app-compatibility-matrix.md` resolved to GREEN/YELLOW/RED with concrete TAE answers.

If any are unchecked, do NOT start Phase 0. Re-read `migration-decision.md`.

---

## Phase 0 — Backup + freeze (1–2 working days)

**Goal:** Lock down the live theme as a known-good rollback target and stop accruing new Pipeline-6 customization debt.

### 0.1 Backup the live theme

- ☐ In Shopify admin → Online Store → Themes → Theme library: locate the live theme (ID `131664707683` as of 2026-05-17).
- ☐ Click "Actions → Duplicate". Name the duplicate **"Pipeline 6 — Pre-Migration Backup YYYY-MM-DD"** (include exact date in name).
- ☐ Record the backup theme's ID in this runbook's verification section.
- ☐ Pull the backup theme locally: `shopify theme pull --theme=<backup-id> --store=creations-gdc.myshopify.com --path=/tmp/p6-backup-YYYY-MM-DD --nodelete`.
- ☐ Tar/compress and store offline: `tar czf ~/Backups/hairmnl-pipeline6-pre-migration-YYYY-MM-DD.tar.gz -C /tmp/p6-backup-YYYY-MM-DD .`. Two copies on different storage.

### 0.2 Snapshot perf baselines

- ☐ Run `./scripts/run-psi.sh https://www.hairmnl.com/ mobile 5` and `desktop 5` — increase n=5 for tighter median on the baseline that the migration will be judged against.
- ☐ Capture CrUX field data via PSI API (mobile + desktop), append to `perf-baseline-comparison.md`'s historical table with an "Pre-migration anchor" row.
- ☐ Screenshot key visual layouts: homepage above-the-fold (mobile + desktop), product page, cart drawer, three brand-collection pages, checkout flow. Save to `~/Backups/hairmnl-pre-migration-screenshots-YYYY-MM-DD/`.

### 0.3 Freeze new customizations

- ☐ Apply the freeze rule from `CLAUDE.md` § "Pipeline 6 customization freeze" (added by P3.3) — no new Pipeline-6 customizations beyond critical bug fixes.
- ☐ Stash or close any in-flight Pipeline-6 perf tickets that won't ship before Phase 6 cutover; resume them after migration on Pipeline 8.
- ☐ Notify any concurrent contributors (if applicable) of the freeze window.

**Phase 0 wall-clock:** 1 working day if backups + screenshots only; 2 if perf re-baseline is included.

---

## Phase 1 — Install Pipeline 8 dev theme (0.5–1 working day)

**Goal:** Get a fresh, current Pipeline 8 install on creations-gdc.myshopify.com as an unpublished theme.

### 1.1 Reuse or refresh existing install

- ☐ If theme `141168312419` ("Pipeline 8 Working Demo") from 2026-05-17 is still on the store and the Pipeline version matches the latest release, skip to 1.3.
- ☐ Otherwise, in Shopify admin: Online Store → Themes → Add theme → Shopify Theme Store → Pipeline → "Try theme". Capture the new theme ID.

### 1.2 Verify it's actually bare Pipeline 8

- ☐ `shopify theme pull --theme=<new-id> --store=creations-gdc.myshopify.com --path=/tmp/p8-pull-YYYY-MM-DD --nodelete`
- ☐ Confirm: `grep "Pipeline Theme V" /tmp/p8-pull-YYYY-MM-DD/layout/theme.liquid | head -1` shows version 8.1.x.
- ☐ Confirm `blocks/` directory exists with ≥30 theme blocks.
- ☐ Confirm `sections/group-header.json`, `group-footer.json`, `group-overlay.json` exist.

### 1.3 Set the working branch

- ☐ `git checkout -b migration/p8-port-YYYY-MM-DD`
- ☐ Commit the pulled Pipeline 8 files into the branch at a new path `p8-base/` (or similar) so the port diff is reviewable. This is reference-only; we'll port _from_ live and _toward_ this base.

**Phase 1 wall-clock:** 0.5 day if reusing `141168312419`; 1 day if fresh install.

---

## Phase 2 — Settings + branding config (1–3 working days)

**Goal:** Pipeline 8 dev theme renders HairMNL branding (logo, colors, fonts) via theme settings only — no code customization in this phase.

### 2.1 Theme settings in admin

- ☐ Customize the Pipeline 8 dev theme via Shopify admin → Customize.
- ☐ Settings → Colors → match HairMNL palette (currently in `config/settings_data.json` for live theme; export the relevant color values).
- ☐ Settings → Typography → match HairMNL font choices (Playfair Display for headings, etc.). Note: Pipeline 8 uses Shopify font CDN by default; self-hosted Playfair Display will need a code-level port in Phase 3 if we want to preserve it.
- ☐ Settings → Logo → upload current logo at appropriate dimensions.
- ☐ Settings → Favicon → upload current favicon.

### 2.2 Section group editing for header / footer

- ☐ Pipeline 8 splits header/footer into section groups (`group-header.json`, `group-footer.json`).
- ☐ Configure header section group: nav menu, search, account link, cart icon. Use Pipeline 8's stock section types — don't try to recreate `thebackbar-master-header.liquid` here.
- ☐ Configure footer section group: HairMNL business info (PH-based, payment icons, shipping carriers), newsletter signup placeholder, social links, legal links.
- ☐ Note any settings the Pipeline 8 stock sections don't expose that we need; flag for Phase 3 custom-section work.

### 2.3 Capture diff against bare

- ☐ `shopify theme pull --theme=<dev-id> --store=creations-gdc.myshopify.com --path=/tmp/p8-after-settings-YYYY-MM-DD --nodelete --only=config/settings_data.json --only=sections/group-header.json --only=sections/group-footer.json`
- ☐ Commit settings_data.json to the working branch.

**Phase 2 wall-clock:** 1 day if the settings map cleanly; 3 days if Pipeline 8's section-group editor surfaces friction with how we configured Pipeline 6.

---

## Phase 3 — Port customizations (7–12 working days)

**Goal:** Move the bespoke 17K+ LoC from Pipeline 6 onto Pipeline 8 per the audit's port/drop/rebuild tags.

### 3.1 Day 0 spike: 10% of `custom-theme.js` port (1 day)

Per `migration-decision.md` Risk #1, the `custom-theme.js` (9,118 LoC) is the largest unknown. Spike before committing to the full timeline:

- ☐ Pick 3 representative behaviors from `custom-theme.js`: sticky element (sticky-js library), drawer interaction, A/B test framework.
- ☐ Port each to Pipeline 8's `assets/theme.js` structure (Pipeline 8 still uses a single bundled file — easier than Dawn).
- ☐ Measure: hours per behavior. Extrapolate to full file. If extrapolation exceeds 10 working days, pause and re-plan (consider Dawn or trim dead code first).

### 3.2 Layout + theme.liquid port (1–2 days)

Source: `os2-migration/customization-audit.md` § "Section 1: layout/theme.liquid Customizations".

Strategy: start from Pipeline 8's stock `layout/theme.liquid`, port only the customizations tagged `need-port` (18 items per audit). Drop the 8 `can-drop` items.

- ☐ Port DNS prefetches/preconnects that survive verification (most can drop).
- ☐ Port custom canonical URL logic (`snippets/canonical.liquid` — 118 LoC).
- ☐ Port HairSalon JSON-LD (`snippets/hairsalon-schema.liquid` — 109 LoC).
- ☐ Port template-gated CSS splits (plyr, pswp, model_viewer, cart, AOS, deferred-templates).
- ☐ Port inline JS blocks: drawer-toggle interceptor, A/B framework, JS error tracking, cart pre-init dispatcher, Klaviyo form events, Backbar reorder. Each becomes a section-scoped JS or a small block in `assets/theme.js`.
- ☐ Drop Pro Blogger CSS interceptor (depends on Pro Blogger's OS 2.0 status; verify in Phase 4).
- ☐ Drop BSS-related deferrals (BSS uninstalled).

### 3.3 CSS variables + css-overrides port (2 days)

Source: `customization-audit.md` § "Section 4 + 5".

- ☐ Map `css-variables.liquid` (435 LoC, `---` triple-hyphen tokens) to Pipeline 8's variable conventions. Pipeline 8 uses similar triple-hyphen pattern — mapping is mostly mechanical.
- ☐ Port the 18 CSS override blocks: re-target selectors against Pipeline 8's DOM class names. Particularly important for the 3 header/cart behavior blocks and the kt0 containment audit.
- ☐ Run the `scripts/check-overlay-css.py` lint (project CLAUDE.md) against the Pipeline 8 port to catch any new kt0-class violations.
- ☐ Drop CSS overrides for uninstalled apps (PWA modal, BSS, Pro Blogger thumbnail if Pro Blogger is going away).

### 3.4 Consolidate 31 brand-collection sections → 1 parameterized (3 days)

Source: `customization-audit.md` § "Section 2.1".

This is the single biggest port win in the migration.

- ☐ Take `sections/collection-branded.liquid` (1,568 LoC) as the canonical base. All 30 brand variants are essentially the same code with different schema settings.
- ☐ Identify the truly variable schema: brand colors, brand logo, hero image, collection handle, brand description text. These become section settings.
- ☐ Build one Pipeline 8 section `sections/brand-collection.liquid` (target ~1,200 LoC) that accepts these as settings.
- ☐ Create 30 JSON templates `templates/collection.{handle}.json` that reference the single section with brand-specific settings. (1 already exists as a Pipeline 8 default; 29 to add.)
- ☐ Confirm each brand collection page renders with correct brand identity on dev theme.

### 3.5 custom-theme.js port (2–4 days)

After the 3.1 spike validates the estimate.

- ☐ Identify dead code in the 9,118 LoC: sticky-js library (`Sticky` class), Pipeline-6-specific Flickity overrides, jQuery dependencies. Estimated drop: ~30–40% of file.
- ☐ Port the survivors to Pipeline 8's `assets/theme.js`. Keep behaviors section-scoped where Pipeline 8's architecture supports it.
- ☐ Eliminate jQuery dependency (Pipeline 8 doesn't ship jQuery; rewrite jQuery-using code to vanilla JS).
- ☐ Target: ~5,000 LoC in the final `assets/theme.js` after dead-code removal.

### 3.6 Vertex AI port (1 day)

Source: `customization-audit.md` § "Section 7.4".

- ☐ Port `snippets/vertex-recommendations.liquid` (303 LoC) and `vertex-rec-card.liquid` (134 LoC) as-is — they're metafield-driven, theme-independent.
- ☐ Build a Pipeline 8 section that wraps the snippet for placement via theme editor.
- ☐ Verify `product.metafields.vertex.recs` and related fields render in dev theme preview.

**Phase 3 wall-clock total:** 7–12 working days. Wider band than other phases because of `custom-theme.js` uncertainty.

---

## Phase 4 — App re-integration (3–7 working days)

**Goal:** Re-install all retained apps on the Pipeline 8 dev theme via their TAE or legacy snippet, matching `app-compatibility-matrix.md`.

### 4.1 TAE-ready apps (1–2 days)

For each of the 10 GREEN-status apps in `app-compatibility-matrix.md`:
- ☐ Smart SEO (×2 blocks), Klaviyo, Shopify Inbox, Nova Cookie Bar, Hextom Timer Bar, LoyaltyLion (×2), LDT Gift Wrap, OXI Social Login
- ☐ For each: open Pipeline 8 dev theme customizer → Theme settings → App embeds → toggle on.
- ☐ Verify the app renders on the relevant page (product / collection / cart / homepage as applicable).

### 4.2 Mixed-support apps (1–2 days)

For each of the 5–7 YELLOW-status apps:
- ☐ BOGOS — toggle TAE; verify promotional UI.
- ☐ Judge.me — toggle TAE; ensure deferred loader + TAE don't double-load.
- ☐ Elevar — toggle TAE; audit latency on dev theme.
- ☐ Re:amaze — toggle TAE; enable defer-on-interaction in Re:amaze dashboard.
- ☐ STKY — toggle TAE; **CRITICAL**: do NOT also add the legacy hardcoded script tag.
- ☐ SWYM — install via TAE; remove legacy snippets.
- ☐ Zapiet — install via TAE; remove gated `storepickup.liquid` snippet.

### 4.3 Legacy snippet apps (1–3 days, depends on NEED-VERIFY outcomes)

For each app that lacks a TAE (verified during Phase 0 pre-flight):
- ☐ Port the legacy snippet to Pipeline 8 syntax (`{% include %}` → `{% render %}`).
- ☐ Wrap in a dedicated Pipeline 8 section for editor visibility.
- ☐ Likely candidates: Pro Blogger (5 snippets), MBC Bundles, possibly Searchanise, Personalizer.io, BookThatApp, VisualQuizBuilder.
- ☐ Drop entirely: Appikon (replaced by Klaviyo BIS), BSS B2B (uninstalled), LimeSpot (replaced by Vertex), pluginseo (replaced by Smart SEO).

### 4.4 Verify app weight + performance

- ☐ Run PSI on Pipeline 8 dev theme preview after Phase 4 completes (mobile + desktop n=3 each).
- ☐ Compare against the estimated +1.16 MB / ~5.04 MB projection from `perf-baseline-comparison.md`.
- ☐ If actual exceeds estimate by >30%, identify which app is heavier than expected and decide whether to defer / gate / replace.

**Phase 4 wall-clock:** 3 working days median, 5 if NEED-VERIFY surfaces unexpected legacy work, 7 if a critical app proves unportable.

---

## Phase 5 — Parallel-run + visual QA (4–6 working days)

**Goal:** Pipeline 8 dev theme is functionally and visually correct against live, with no regressions found by manual QA.

### 5.1 Side-by-side template comparison (2 days)

Open the live URL and the dev theme preview URL side-by-side. Compare each template:
- ☐ Homepage (above-the-fold, hero, collection tabs, custom content blocks, recommendations)
- ☐ Product page (gallery, variant selector, ATC, size chart, reviews, recommendations, upsells)
- ☐ Collection page (filter sidebar, product grid, sort, pagination)
- ☐ All 31 brand-collection pages (use the consolidated section's variant rendering)
- ☐ Cart page + cart drawer (free shipping progress, upsells, gift wrap)
- ☐ Blog index + article (with related products + related articles)
- ☐ Search results
- ☐ Customer account (login, register, account dashboard, addresses)
- ☐ Backbar account registration (the custom-DOM-reorder page)
- ☐ The Back Bar pages (use `thebackbar-master-header.liquid` equivalent)
- ☐ Lookbook, Story, Team, FAQ, Contact pages

### 5.2 Behavior testing (1–2 days)

- ☐ Cart drawer opens / closes correctly, free-shipping progress updates on item add
- ☐ A/B test framework: verify cookie set + dataLayer push fires
- ☐ JS error tracking: trigger a fake error, verify dataLayer event
- ☐ Klaviyo popup: render, submit, close — all three should push to dataLayer
- ☐ Reamaze chat: bubble appears, opens chat, closes cleanly
- ☐ Searchanise / LimeSpot: predictive search + recommendations render correctly
- ☐ Vertex AI: rec rails render in product page, collection page, cart page
- ☐ STKY: sticky ATC bar appears on product page, no duplicate-load
- ☐ Mobile: drawer-toggle interceptor works (no tap-through), nav menu renders

### 5.3 Edge-case + regression testing (1 day)

- ☐ CLS — run Lighthouse on the dev theme, confirm CLS ≤ 0.01 across product/collection/blog templates
- ☐ Each of the 18 CSS override blocks: verify the original CLS scenario doesn't reappear
- ☐ kt0 audit — run `scripts/check-overlay-css.py` on the Pipeline 8 working tree
- ☐ Cart drawer overlay test (`scripts/check-overlay-css.py` smoke test)
- ☐ Reamaze chat positioning on mobile (the 2026-05-12 incident shouldn't reproduce)
- ☐ Touch-target sizes on mobile across all CTAs
- ☐ Print-stylesheet / dark-mode if applicable

### 5.4 Lock down for cutover (0.5 day)

- ☐ Freeze new theme settings 48 hours before Phase 6.
- ☐ Final dev-theme PSI run; record numbers in runbook verification log.
- ☐ Confirm rollback target is still the Pipeline 6 backup from Phase 0.

**Phase 5 wall-clock:** 4 working days median; 6 if visual regressions surface and require Phase 3 follow-up patches.

---

## Phase 6 — Cutover (0.5–1 working day)

**Goal:** Publish Pipeline 8 dev theme as live; Pipeline 6.1.3 becomes "Pipeline 6 — Pre-Migration Backup" and stays as the rollback target.

### 6.1 Pre-cutover sanity (30 min)

- ☐ Live PSI re-check: confirm Pipeline 6 lab numbers match Phase 0 anchor (no surprise regression)
- ☐ All Phase 5 tests passed; no open visual/regression issues
- ☐ Calendar: low-traffic window (Tuesday or Wednesday morning Asia/Manila timezone — ~06:00–10:00 local)
- ☐ Operator dedicated for next 4 hours; no other tasks running

### 6.2 The cutover itself (15 min)

- ☐ In Shopify admin → Online Store → Themes → Theme library
- ☐ Click "Publish" on the Pipeline 8 dev theme (the one with all customizations)
- ☐ Pipeline 6.1.3 (theme `131664707683`) automatically becomes unpublished
- ☐ Rename the now-unpublished Pipeline 6 to `Pipeline 6 — Pre-Migration Backup YYYY-MM-DD` if not already done
- ☐ Verify the live site at https://www.hairmnl.com/ renders the Pipeline 8 theme (check Pipeline version in HTML source: search for `Pipeline Theme V`)

### 6.3 Real-time post-cutover monitoring (3 hours)

For 3 hours after publishing:
- ☐ Watch live PSI on the homepage (run 1x every 15 min; record into a temp log)
- ☐ Watch Shopify admin → Live View for any sales drop signal
- ☐ Watch the Sentry / error-tracking dashboard if applicable
- ☐ Watch Reamaze for customer-reported issues
- ☐ Check checkout completion rate vs prior day baseline

### 6.4 Rollback triggers (locked in BEFORE Phase 6.2)

**Immediate rollback if any of these fires in the first 3 hours post-cutover:**

1. ☐ Homepage 5xx rate >2% over a 15-min window (vs <0.5% baseline)
2. ☐ Cart-add success rate drops >20% vs prior 24h baseline
3. ☐ Checkout completion rate drops >15% vs prior 24h baseline
4. ☐ Critical app (Klaviyo, Reamaze, Vertex recs) is fully not rendering on >50% of relevant page views
5. ☐ Visual regression so severe that the homepage is not usable on mobile (P0 brand impact)

**Rollback procedure:**
- Shopify admin → Theme library → "Pipeline 6 — Pre-Migration Backup YYYY-MM-DD" → Publish.
- Wall-clock: ~5 minutes to flip; ~1 hour to settle as Shopify CDN refreshes.
- Post-mortem: file a bd ticket within 24h documenting what went wrong; the migration project re-opens for Phase 3 / 4 patch work.

**Phase 6 wall-clock:** 0.5 day median (cutover + 3h monitoring); 1 day if rollback triggers fire.

---

## Phase 7 — Post-cutover verification + perf measurement (2–5 working days, with a 4-week field-data window)

**Goal:** Confirm the migration actually delivered the expected gains in field data, and resolve any post-cutover issues that didn't fire the immediate-rollback triggers.

### 7.1 24-hour vigilance (Day 1)

- ☐ Periodic PSI checks on key templates (homepage, product, collection)
- ☐ Customer support inbox / Reamaze monitoring for new visual / functional reports
- ☐ Sales / conversion / checkout funnel watching (Shopify admin or GA4)
- ☐ Log any "near-miss" issues that didn't trigger rollback but warrant patches

### 7.2 First-week tactical patches (Days 2–5)

- ☐ File a bd ticket per issue surfaced in Day 1; prioritize P0 (customer-facing breakage) and P1 (perf regression)
- ☐ Patch in fast iterations; each patch follows the project's normal push-to-draft → smoke → push-to-live workflow
- ☐ Common expected issues: a few CSS-override misses, an app TAE that needs re-toggling, a custom-theme.js behavior that regressed

### 7.3 Field-data window (Weeks 1–4)

- ☐ Do NOT make non-critical theme changes for 4 weeks — the CrUX field-data window needs clean signal
- ☐ Capture CrUX field data weekly via PSI API; append to `perf-baseline-comparison.md` historical table
- ☐ Expected field improvements: INP and CLS should show measurable gains within 2 weeks; LCP within 3–4 weeks
- ☐ If by week 4 the field numbers haven't improved significantly, run a fresh root-cause investigation — the lab/field disconnect from P1.3 may apply post-migration too

### 7.4 Migration retrospective + close (after Week 4)

- ☐ Open a new bd ticket for the migration retro
- ☐ Capture: actual wall-clock vs estimate, actual operator-weeks, what went wrong, what went well
- ☐ Update `feasibility.html` deck with the actual post-migration numbers (an Update history entry)
- ☐ Update `target-theme-research.md` with measured Pipeline 8 + apps lab numbers (replacing the estimates)
- ☐ Delete the Pipeline 6 backup theme **only after** field data confirms migration success and a final tar.gz archive is verified intact offline

**Phase 7 wall-clock:** 2 days active (Day 1 vigilance + early patches), 4 weeks calendar (passive field-data window), 1 day retrospective.

---

## Total wall-clock summary

| Phase | Median | Range |
|---|---|---|
| Phase 0 — Backup + freeze | 1d | 1–2d |
| Phase 1 — Install dev theme | 0.5d | 0.5–1d |
| Phase 2 — Settings + branding | 1d | 1–3d |
| Phase 3 — Port customizations | 9d | 7–12d |
| Phase 4 — App re-integration | 3d | 3–7d |
| Phase 5 — Parallel-run + QA | 5d | 4–6d |
| Phase 6 — Cutover | 0.5d | 0.5–1d |
| Phase 7 — Post-cutover (active) | 2d | 2–5d |
| **Sprint subtotal** | **22d (≈4–5 weeks)** | **19–37d** |
| Phase 7 — Field-data window | +4 weeks calendar | passive |

---

## Verification log (fill during execution)

| Date | Phase | Action | Outcome |
|---|---|---|---|
| | 0 | Backup theme created (ID: ____, name: ____) | |
| | 0 | Backup tar.gz path verified | |
| | 0 | Pre-migration PSI baseline n=5 captured | |
| | 1 | Pipeline 8 dev theme ID + version | |
| | 2 | Settings_data.json committed | |
| | 3 | custom-theme.js spike result (hours per behavior × extrapolation) | |
| | 3 | 31 → 1 brand-collection consolidation complete | |
| | 4 | All TAE apps toggled + verified | |
| | 4 | NEED-VERIFY apps resolved (count green / yellow / red after verification) | |
| | 5 | Visual QA pass — all templates | |
| | 5 | CLS spot-checks pass (≤0.01 across templates) | |
| | 6 | Cutover timestamp + new published theme ID | |
| | 6 | Rollback triggered? (Y/N) | |
| | 7 | First-week patches landed (count) | |
| | 7 | Week 4 CrUX field data — INP / LCP / CLS deltas vs anchor | |
| | 7 | Retrospective ticket ID | |
