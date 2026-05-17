# Phase 4.M4 — deviation report + Phase 5 visual QA checklist

> **Bead:** `hairmnl-theme-2i8b.5` (Step 5 of 5).
> **What this doc replaces:** the PR description that would normally accompany M4 — OC's `/hh-orchestrate` pushed directly to `main` instead of opening a PR, so this is the after-the-fact review surface.
> **Date:** 2026-05-17

---

## Cumulative M4 outcome

| Metric | Pipeline 6 | Pipeline 8 (after M4) | Δ |
|---|---|---|---|
| Section files for brand collections | 31 files, ~54,000 LoC | 1 file (`sections/brand-collection.liquid`, 1,800 LoC) | **-96.7% LoC** |
| Template files for brand collections | 31 `.liquid` (live) | 31 `.liquid` (still live, Phase 6 deletes) + 30 new `.json` (Pipeline 8) | duplicate during dev, P8-only post-cutover |
| Block / setting variability | Hardcoded per section | 14 block types + 60 settings, all parameterizable | one section, many configurations |

**Commits on `origin/main` (no PR, OC pushed directly):**
- `d080833` — feat(p4-m4): consolidate 31 brand-collection sections into sections/brand-collection.liquid
- `bfe2e54` — feat(p4-m4): add 30 brand-collection JSON templates (Step 4)
- `56bc6e5` + `89d9282` — chore: bd state appends

**Cumulative `git show` for review:**
```
sections/brand-collection.liquid              | 1800 LoC (NEW)
templates/collection.<handle>.json × 30       | ~2065 LoC total (29 NEW + 1 modified)
```

---

## Known deviations from P6 (Phase 5 must verify each)

### 1. `lp-serioxyladvanced.json` — replaced an in-flight P8 experiment

**What it was:** 423 LoC of auto-generated multi-section P8 JSON template (section-banner-slider with banner_slide blocks + likely other custom sections — created via Shopify admin theme editor on a Claude Code draft theme, not live).

**What it is now:** 14-line minimal brand-collection reference.

**Risk:** if this URL (`/collections/lp-serioxyladvanced`) is currently being prepared for a P8 launch with a special multi-section design (banner slider + branded content), that work is **gone from `templates/`**. The history is recoverable from `git show e7c0834:templates/collection.lp-serioxyladvanced.json`.

**Live impact:** zero — live theme `131664707683` is Pipeline 6.1.3, which uses `templates/collection.lp-serioxyladvanced.liquid` + `sections/collection-lp-serioxyladvanced.liquid` (untouched).

**Phase 5 decision needed:** confirm with the operator whether the lost multi-section template was needed. If yes, restore the old `.json` and place its banner content as a NEW section preceding `brand-collection` in the order array.

### 2. Five minimal templates — no block defaults extracted

Five brand handles ended up with the minimum settings (only `collection_custom_nav_list` and `grid_setting_large`), no blocks:

- `templates/collection.lp-styling.json`
- `templates/collection.lp-prolonger.json`
- `templates/collection.lp-instantclear.json`
- `templates/collection.lp-antidandruff.json`
- `templates/collection.lp-serioxyl.json`

**Reason:** OC's senior-developer extracted defaults from `config/settings_data.json`, which the live Pipeline 6 doesn't populate for these brands (their P6 sections were rendered with hardcoded values in `sections/collection-{handle}.liquid` directly, not via theme-editor settings).

**Phase 5 decision needed:** for each of the 5, render the page on dev theme. If the brand-specific UI elements (hero image, logo, description text) are missing because no blocks are configured, the operator needs to either:
- Manually configure the missing settings via the theme editor when the dev theme is in design mode
- OR add the brand defaults from the P6 `.liquid` sections directly into the JSON template's `settings` block

### 3. Pipeline-6 stock grid class names normalized to `large-up--*`

Per the Step 1 analysis, the 31 variants had a mix of P6 grid class conventions:
- Older variants: `large--one-half` / `push--large--one-quarter`
- Newer variants: `large-up--one-half` / `push--large-up--one-quarter`

The consolidated section uses only the newer `large-up--*` convention.

**Risk:** any CSS that targeted the older `large--*` classes from P6 stock will not apply on the new templates. P6 stock CSS files are being replaced by P8 stock in any case, so this resolves itself at cutover — but Phase 5 visual QA should confirm grid layouts don't visibly break on the new templates while still rendering on P6 dev theme.

### 4. `{% include %}` → `{% render %}` syntax normalization

All 5 snippet includes in the consolidated section use `{% render %}` (P8 / OS 2.0 standard). Some P6 variants used `{% include %}`. The `{% render %}` semantics differ:
- `{% include %}` — variables in caller scope leak into included snippet
- `{% render %}` — snippet runs in isolated scope, only explicit args available

**Risk:** if any of the original brand variants relied on variable-leakage from `{% include %}`, the new rendering will show those variables as undefined / empty. Phase 5 inspects this per brand.

### 5. Wholesale Club (BSS B2B) logic preserved

Per the OC lead-architect's validation, the section still contains BSS Wholesale Club markers (best_sellers + new_arrivals + 4 markers total). BSS B2B was uninstalled 2026-05-13 — these markers are dead code that won't render on either P6 or P8 (the BSS app doesn't inject anymore). Harmless but worth flagging for Phase 5 cleanup if the operator wants to drop them.

---

## Phase 5 visual QA checklist — 30 brand handle URLs

Each URL renders on the Pipeline 8 dev theme `141168312419` preview. The URL pattern is:

```
https://www.hairmnl.com/collections/<handle>?preview_theme_id=141168312419
```

Spot-check criteria per page:
- ☐ Brand hero image renders (or fallback gracefully if image is null)
- ☐ Brand logo renders in correct position
- ☐ Brand name + description text appears with correct styling
- ☐ Brand primary + accent colors apply correctly
- ☐ Product grid renders with `grid_setting_large` columns (default 4)
- ☐ "Discover {{ brand_title }}" copy renders
- ☐ Featured collection sections render (if blocks configured)
- ☐ Wholesale Club markers don't visibly break the page (should be dead-code no-ops)
- ☐ No JS errors in console
- ☐ No CLS regressions vs live P6 baseline

### The 30 handles (one row per template)

| # | Handle | Block count | Notes |
|---|---|---|---|
| 1 | `absolutrepair` | populated | Kérastase Absolu Repair |
| 2 | `blondabsolu` | populated | Kérastase Blond Absolu |
| 3 | `branded` | populated | Base brand template — used by sub-collections |
| 4 | `branded-subcollection` | minimal (18 LoC) | Sub-collection variant |
| 5 | `chronologiste` | populated | Kérastase Chronologiste |
| 6 | `densifique` | populated | Kérastase Densifique |
| 7 | `discipline` | populated | Kérastase Discipline (largest, 157 LoC) |
| 8 | `elixir` | populated | Kérastase Elixir Ultime |
| 9 | `krchromaabsolu` | populated | Kérastase Chroma Absolu |
| 10 | `krcurlmanifesto` | populated | Kérastase Curl Manifesto |
| 11 | `krgenesis` | populated | Kérastase Genesis |
| 12 | `krspecifique-divalent` | populated | Kérastase Spécifique Divalent |
| 13 | `krsymbiose` | populated | Kérastase Symbiose |
| 14 | `lorealprofessionnel` | populated | L'Oréal Professionnel parent brand |
| 15 | `lp-antidandruff` | **minimal — no blocks** | Verify hero / logo on dev theme |
| 16 | `lp-inforcer` | populated | L'Oréal Inforcer |
| 17 | `lp-instantclear` | **minimal — no blocks** | Verify hero / logo on dev theme |
| 18 | `lp-liss` | populated | L'Oréal Liss Unlimited |
| 19 | `lp-metaldetox` | populated | L'Oréal Metal Detox |
| 20 | `lp-mythicoil` | populated | L'Oréal Mythic Oil |
| 21 | `lp-prolonger` | **minimal — no blocks** | Verify hero / logo on dev theme |
| 22 | `lp-scalpadvanced` | populated (largest, 168 LoC) | L'Oréal Scalp Advanced |
| 23 | `lp-serioxyl` | **minimal — no blocks** | Verify hero / logo on dev theme |
| 24 | `lp-serioxyladvanced` | minimal — **lost prior P8 multi-section template** | Verify whether the prior banner-slider design was needed; restore from `e7c0834` if yes |
| 25 | `lp-silver` | populated | L'Oréal Silver |
| 26 | `lp-styling` | **minimal — no blocks** | Verify hero / logo on dev theme |
| 27 | `lp-vitamino` | populated | L'Oréal Vitamino — used as canonical structural base by Step 1 |
| 28 | `nutritive` | populated | Kérastase Nutritive |
| 29 | `resistance` | populated | Kérastase Résistance |
| 30 | `specifique` | populated (largest, 189 LoC) | Kérastase Spécifique |

### Rollback procedure if a brand page breaks

If a Phase 5 visual QA finding requires reverting M4:

1. **For a single broken brand**: edit just its `.json` template to add the missing settings or revert to the P6 variant by changing `"type": "brand-collection"` to `"type": "collection-<handle>"` (the P6 section is still on `main` and on the dev theme — Phase 6 cutover deletes it).

2. **For a structural problem in the consolidated section**: revert commit `d080833` (the section file) — that brings back all 31 P6 sections + `sections/collection-branded.liquid` as the base. The 30 JSON templates can stay (they reference `brand-collection` which would then be absent — harmless, they'd render empty and the operator could change `"type"` per template back to the per-brand section name).

3. **Full M4 rollback**: revert both `d080833` (section) and `bfe2e54` (templates). Brings live theme behavior fully back to the P6 brand-collection pattern.

---

## Step status

| Step | Description | Status |
|---|---|---|
| 1 | Repo-explorer analysis | ✅ Closed (OC) |
| 2 | Senior-developer creates `sections/brand-collection.liquid` | ✅ Closed (OC, commit d080833) |
| 3 | qa-reviewer review of section | ✅ Closed (OC; qa hallucinated, lead-architect cross-checked) |
| 4 | Generate 30 JSON templates | ✅ Closed (OC, commit bfe2e54; qa-reviewer APPROVED with no hallucination this round) |
| 5 | Deviation report + Phase 5 visual QA checklist | ✅ Closed (this doc) |

**M4 is ready to close.** Remaining work is Phase 5 visual QA on the dev theme, which is a separate Phase 5 ticket (not part of M4 acceptance).

---

## bd close criteria checklist

- [x] `sections/brand-collection.liquid` exists on main and validates (1800 LoC, schema valid, kt0 lint pass)
- [x] 30 `templates/collection.<handle>.json` files exist on main and validate (all JSON parses, all reference `brand-collection`)
- [x] No `.liquid` template files touched (P6 live behavior preserved)
- [x] No `docs/os2-migration/` mis-paths
- [x] Deviation report committed at `os2-migration/p4-m4-deviation-report.md` (this PR)
- [x] Phase 5 visual QA checklist documented (30 handles enumerated above)
- [x] Rollback procedure documented

After this PR merges, M4 closes with the cumulative `git show d080833 bfe2e54 <this-pr-merge-sha> --stat` as phantom-completion evidence.
