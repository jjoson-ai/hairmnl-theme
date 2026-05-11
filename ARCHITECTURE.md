# HairMNL Shopify theme — architecture & operating model

**Audience:** any agent (Claude Code, OpenCode lead-architect/senior-developer, Cursor) landing fresh on this repo. Read this file plus `CLAUDE.md` + `.opencode_hints` + the bd issue's `description/design/acceptance` before touching any file. This document captures **what the system is** and **how we work on it** — it is the single source of architectural truth.

**This file is reference, not policy.** Hard rules live in `CLAUDE.md` (push protocol) and `.opencode_hints` (agent hard locks). When this doc and those disagree, those win.

---

## 1. Identity & live topology

| Field | Value |
|---|---|
| Storefront | `www.hairmnl.com` (Cloudflare in front of Shopify) |
| Shopify shop | `creations-gdc.myshopify.com` |
| Theme family | Pipeline 6.1.3 (Vanilla) — NOT Online Store 2.0 |
| Live theme ID | `131664707683` ("Pipeline 6 - Fix share image") |
| Draft theme ID | `140785582179` ("Claude Code draft") |
| Locale | `en` (Philippines store) |
| Auto-sync between draft/live | **None.** Manual `shopify theme push --only=<file>` is the only deployment path. |
| Apex DNS | A record `23.227.38.71` (Shopify). See bd memory `hairmnl_dns_config` for Namecheap quirks. |

**Why Pipeline 6 matters:** OS 2.0 (sections-everywhere, dynamic source blocks, JSON templates) is largely absent here. Most templates are `.liquid` (180+ files in `templates/`), section schemas are static, and there is no theme-editor block tree to worry about for most pages. The flip side: any per-page customization that an OS 2.0 theme would handle via Theme Editor must be done in Liquid + section schema here.

---

## 2. Repository layout

```
hairmnl-theme/
├── ARCHITECTURE.md         ← this file
├── CLAUDE.md               ← workflow guard (push protocol, Beads, session-close)
├── AGENTS.md               ← non-interactive shell + Beads quick-ref for agents
├── .opencode_hints         ← AGENT HARD LOCKS — read before any RW work
├── .theme-check.yml        ← theme-check linter config (many rules disabled by design)
│
├── layout/                 ← {{ content_for_layout }} wrappers (theme.liquid is THE entry point)
├── sections/               ← 98 sections — Pipeline 6 page-builder primitives
├── snippets/               ← 258 snippets — small reusable Liquid fragments
├── templates/              ← 180 templates — one per route (product/X.liquid, collection/Y.liquid, …)
├── assets/                 ← compiled CSS/JS + images + fonts
├── config/                 ← settings_data.json, settings_schema.json  ← ADMIN-MANAGED, do not edit
├── locales/                ← i18n JSON
│
├── dashboard/              ← self-hosted PWI/CWV dashboard (GitHub Pages)
│   ├── data/               ← snapshots.jsonl (daily perf snapshots)
│   ├── index.html
│   └── compare-*.html
│
├── scripts/                ← ALL operational tooling (Python + Bash + JS audit tools)
│   ├── build-perf-dashboard.py       ← daily dashboard generator
│   ├── smoke-test-drawers.py         ← Playwright kt0-killer smoke test (Layer 3 gate)
│   ├── smoke-test-drawers.config.json
│   ├── web-vitals-report.py          ← GA4 RUM query CLI
│   ├── layout-thrash-audit.js        ← forced-reflow scanner (Node)
│   ├── gtm-*.py                      ← GTM container API tooling (auth, audit, fix, replay)
│   ├── run-psi.sh / check-perf-budgets.sh
│   └── launchd/                      ← macOS launchd plist for local cron parity
│
├── docs/
│   ├── handoff-log.md                ← APPEND-ONLY log of every multi-model handoff
│   ├── gtm-js-error-handoff-*.md     ← long-form debug post-mortems
│   ├── baselines/                    ← perf baselines snapshotted before sprints
│   ├── HairMNL-90-Day-Modernization-Roadmap.docx
│   └── HairMNL-Theme-Modernization-Deck.pptx
│
├── design-research/        ← UI/UX research, not part of theme build
├── vertex-placement-design-brief.md  ← future Vertex AI rec-engine integration
├── vertex-placement-guide.md
│
├── .beads/                 ← Beads (bd) issue tracker DB (Dolt-backed)
├── .github/
│   └── workflows/
│       ├── pages.yml               ← deploys dashboard/ to GitHub Pages
│       └── perf-dashboard.yml      ← daily 13:00 UTC cron — runs build-perf-dashboard.py
└── .claude/                ← session telemetry, not source
```

### Asset families (`assets/`)

| File | Role | Source-of-truth status |
|---|---|---|
| `theme.css` (~350 KB) | minified production CSS | **OUTPUT — never hand-edit.** Override via `snippets/css-overrides.liquid`. |
| `theme.dev.css` (~475 KB) | source CSS with comments | hand-editable, but you must mirror to `theme.css` |
| `theme.js` (~260 KB) | minified production JS | **The script that runs.** Paired with `theme.dev.js`. |
| `theme.dev.js` (~300 KB) | readable JS source | hand-editable; changes MUST be mirrored to `theme.js` (single-letter vars, fragile) |
| `custom-theme.js` (~456 KB) | custom integrations | also paired; see `.opencode_hints` for mirror discipline |
| `custom-theme.css` (~70 KB) | custom CSS | paired with `custom-theme.dev.css` |
| `vendor.js` (~100 KB) | Rellax/axios/ellipsis | **No source available in this repo** (separate build pipeline). Tree-shake blocked (bd `yzk`). |

---

## 3. Critical contracts — DO NOT RENAME

These names are referenced from outside this repo (GTM, GA4, dashboard query, vendor scripts). Renaming any of them without coordinated updates breaks tracking, analytics, or the dashboard. (Source: `.opencode_hints` "Don't rename" tables.)

**JS events & dataLayer keys**

| Name | Origin | Consumers |
|---|---|---|
| `theme:cart:change` | `CartItems.fireChange` | header cart count, cart drawer, BOGOS, LimeSpot |
| `hairmnl_js_error` | `window.error` handler dataLayer push | GTM tag 776 → GA4 |
| `error_type` / `error_message` / `error_source` | dataLayer keys on `hairmnl_js_error` | GA4 custom dimensions |
| `web_vital` | dataLayer push from `web-vitals-reporter.liquid` | GTM tags 766 + 771 → GA4 |
| `metric_name` / `metric_value` / `metric_id` / `metric_rating` / `metric_delta` / `metric_navigation_type` | dataLayer keys on `web_vital` | GA4 custom dimensions; dashboard `build-perf-dashboard.py` queries by these |
| `template` (Liquid global) | dataLayer key for per-template CWV slicing | GA4 custom dimension `template` |
| `debug_target` | computed selector of shifted/slow element | GA4 custom dimension — drives debug_target breakdown in dashboard |

**DOM hooks (CSS + JS depend on these)**

| Selector / data-attr | Role |
|---|---|
| `data-section-id`, `data-block-id`, `data-section-type` | Shopify section system (do not strip) |
| `[data-cart-item]`, `[data-cart-form]`, `[data-cart-loading]` | CartItems class + cart drawer |
| `[data-header-wrapper]`, `data-header-height`, `data-header-sticky` | Header init + sticky scroll |
| `header.theme__header`, `.header__wrapper` | Header CSS + the kt0 `contain: layout` containing-block gotcha — see §5.4 |
| `[data-api-content]` | Section-rendering API (cart bulk-sections POST) |

**Admin-managed files — DO NOT EDIT IN GIT**

Edits here will be silently clobbered by the Shopify Theme Editor's auto-save:

- `templates/*.json` (OS 2.0 JSON templates, even though most templates are `.liquid` here)
- `config/settings_data.json`
- `config/settings_schema.json`

If a task seems to require a settings change, STOP and surface it. Settings changes happen in the Shopify admin UI, then `shopify theme pull` to git.

---

## 4. Build & deployment model

There is no build step for the theme itself. CSS/JS in `assets/` are committed pre-minified. The CI/CD pipeline does NOT touch the storefront; deployment is manual via `shopify theme push`.

### 4.1 The push protocol (CLAUDE.md is the authoritative source)

For every CSS/Liquid/JS change:

```
1. git diff HEAD <file>                              ← confirm exact intended hunks
2. shopify theme push --theme=140785582179 \
       --nodelete --only=<file>                       ← draft first
3. Visit https://www.hairmnl.com/?preview_theme_id=140785582179
       → run smoke checklist (§5.3) on draft
4. python3 scripts/smoke-test-drawers.py \
       --config=scripts/smoke-test-drawers.config.json --theme=draft   ← Layer 3 gate
       → exit 0 required
5. shopify theme push --theme=131664707683 \
       --allow-live --only=<file>                     ← live
6. git add <file>; git commit -m "..."; git pull --rebase; git push
7. bd update <id> --append-notes "MERGE_GATE_PASS at <ts>\n$(git show HEAD --stat)"
8. bd close <id>
```

### 4.2 Hard rules around `shopify theme push`

- **Never** `shopify theme push` without `--only=<file>` — a no-filter push uploads the entire working tree, almost guaranteeing to drag stale/WIP content into live. (This is the 2026-04-26 regression that triggered the guard.)
- `shopify theme push --only=<file>` uploads the **local working tree** version, not git HEAD. If your working tree is stale or has reverted content, the push will overwrite a good live file with old code. ALWAYS `git diff HEAD <file>` first.
- Draft preview before live push for anything in `layout/`, `sections/`, `snippets/css-overrides.liquid`, `assets/theme.css`, or `snippets/css-variables.liquid`.

### 4.3 Who pushes

**Only the coordinator (Claude Code session) runs `shopify theme push`.** OC and Cursor agents are HARD-LOCKED from running it (see `.opencode_hints` §1). Agents stage code with `git add`; the coordinator runs draft push → smoke test → live push → commit → bd close.

---

## 5. Quality gates (the kt0-prevention 3-layer defense)

A 2026-05-11 cart-drawer regression (commit ff1ef80; bd memory `css-containment-gotcha-kt0`) was caused by adding `contain: layout` to `.header__wrapper`, which silently created a containing block for the position:fixed cart drawer. Three independent defenses prevent recurrence:

### 5.1 Layer 1 — Author-time docs (`.opencode_hints` "CSS containment + position gotchas")

Documents the 8 CSS properties (`contain: layout|paint|strict|content`, `transform`, `filter`, `backdrop-filter`, `perspective`, `will-change: transform|filter`) that create containing blocks for fixed/absolute descendants, with a required `grep` audit before adding any of them to a parent selector.

### 5.2 Layer 2 — Manual pre-push smoke checklist (`.opencode_hints` "Pre-push smoke checklist")

6 interactions to click on the draft preview before any CSS/layout push: cart drawer, mobile nav, PhotoSwipe lightbox, search overlay, Klaviyo popup, LoyaltyLion launcher. Skip only for pure color/typography/comment diffs.

### 5.3 Layer 3 — Automated Playwright smoke test (`scripts/smoke-test-drawers.py`)

```
python3 scripts/smoke-test-drawers.py \
    --config=scripts/smoke-test-drawers.config.json \
    --theme=draft
```

Exit codes:
- `0` — all overlays pass the kt0-killer audit (safe to push live)
- `1` — at least one overlay broken (BLOCK push)
- `2` — script setup error (Playwright missing, network down)

The kt0-killer assertion walks every fixed-position overlay's parent chain and fails if any ancestor has a CSS property that creates a containing block. This catches the structural bug pattern, not just the symptom. Same script is generalized as a global Claude skill at `~/.claude/skills/smoke-test-overlays/`.

### 5.4 Source ↔ minified mirror discipline

`assets/theme.dev.js` ↔ `assets/theme.js`, `assets/custom-theme.dev.js` ↔ `assets/custom-theme.js`, and likewise for `.dev.css`. The minified files are what actually runs. Every source edit must be mirrored to the minified file. If the minification can't be reliably hand-edited (single-letter vars, comma operators), surface to the coordinator rather than guessing.

---

## 6. Performance instrumentation stack

End-to-end RUM + lab telemetry. **The dashboard is the single pane of glass for perf state.**

```
                          ┌─ web-vitals-reporter.liquid ──┐
Storefront page load      │ pushes web_vital events       │
        │                 │ + hairmnl_js_error events     │
        ▼                 │ to dataLayer with             │
  dataLayer push    ──────┤   metric_name, metric_value,  │
                          │   metric_rating, debug_target,│
                          │   template, etc.              │
                          └────────────┬──────────────────┘
                                       ▼
                         GTM container 12266146 (account 4702257664)
                         tags 766 (Web Vitals) + 771 (web_vital event)
                                       │
                                       ▼
                              GA4 property 248106289
                              custom dimensions registered
                                       │
                                       ▼
                  scripts/build-perf-dashboard.py
                  (daily 13:00 UTC via .github/workflows/perf-dashboard.yml)
                                       │
                                       ▼
                  dashboard/data/snapshots.jsonl
                                       │
                                       ▼
                  https://jjoson-ai.github.io/hairmnl-theme/  (GitHub Pages)
```

### 6.1 RUM (real users)

- `snippets/web-vitals-reporter.liquid` — pushes `web_vital` events with `metric_name`/`metric_value`/`metric_rating`/`metric_id`/`metric_delta`/`metric_navigation_type` + `debug_target` + `template` dimensions
- `layout/theme.liquid:625` — `window.error` + `unhandledrejection` handlers push `hairmnl_js_error` events with `error_type` (categorical: `error` | `rejection`), `error_message`, `error_source`

### 6.2 GTM (tag manager)

Auth credentials at `~/.config/hairmnl-gtm-token.json` + `~/.config/hairmnl-oauth-client.json`. Container 12266146.

Operational tooling (`scripts/gtm-*.py`):
- `gtm-audit.py` — read-only inspection
- `gtm-auth.py` — OAuth helper
- `gtm-cleanup-via-new-workspace.py` — the safe pattern: create a fresh workspace from live, NEVER edit workspace 197 (years of stale 2019 changes) or 190 (stale)
- `gtm-fix-*-YYYY-MM-DD.py` — one replayable script per published fix; pattern: audit → fresh workspace → apply fix → create Container Version (NOT publish) → coordinator publishes after review

**Hard rules:** never touch workspace 197 or 190; never publish a container version without coordinator review; one replayable script per fix.

### 6.3 Lab (synthetic)

- `scripts/run-psi.sh` — calls PageSpeed Insights API
- `scripts/check-perf-budgets.sh` — perf budget assertion (TBT ≤ X ms, etc.)
- `scripts/build-perf-dashboard.py --no-psi --no-crux --render-only` — fast local re-render of dashboard from existing snapshots

### 6.4 Field (CrUX)

`scripts/build-perf-dashboard.py` queries the public CrUX API for 28-day rolling histograms (LCP/CLS/INP/FCP/TTFB, mobile + desktop). No auth needed.

### 6.5 GA4 admin

Property ID **`248106289`** (display name "HairMNL.com - GA4 Main"). Custom dimensions registered for `template`, `metric_rating`, `debug_target`, `error_type`, `error_message`, `error_source`. Service-account key at `~/.config/hairmnl-ga4-key.json` for programmatic queries via `scripts/web-vitals-report.py`.

**Known data caveats:**
- `/pages/privacy-policy` receives ~538k bot events/14d (49× homepage volume); contaminates aggregate CLS/LCP/FCP/TTFB. Prefer page-specific RUM (homepage, cart, search) or CrUX for trend reads. (bd memory `ga4-privacy-policy-bot-2026-05-01`.)
- Forward-only bot filter cutoff is 2026-05-05; pre-2026-05-05 snapshots remain unfiltered.

---

## 7. Task tracking — Beads

`bd` (Beads) is the **only** issue tracker. TodoWrite, markdown TODOs, and ad-hoc tracking are PROHIBITED (see `CLAUDE.md` "Beads Issue Tracker").

| Command | Use |
|---|---|
| `bd ready -n 20` | available work |
| `bd show <id>` | issue detail |
| `bd update <id> --claim` | claim |
| `bd update <id> --append-notes "..."` | progress |
| `bd close <id>` | done (coordinator only — see `.opencode_hints` §3) |
| `bd remember "..."` | persistent cross-session knowledge |
| `bd memories <keyword>` | search persisted knowledge |
| `bd dolt push` | sync to Dolt remote |

**Issue-first development:** every code change must be linked to a `bd` issue with `description` + `design` + `acceptance_criteria` all filled in BEFORE dispatching to an agent. Thin specs are rejected at pre-flight (CLAUDE.md global rule).

Snapshot of state as of 2026-05-12: **132 total** (110 closed, 16 open, 5 in-progress, 0 blocked). See `bd ready` for actionable open work.

---

## 8. Offload model — how work gets dispatched

**The SOP (global, no deviations):** the coordinator (Claude Code, Opus 4.7) compresses to: file good bd specs → kick off OC's `lead-architect` sub-orchestrator via `/hh-orchestrate` or `/hh-swarm` → monitor → run merge-gate → close. Agents NEVER prompted directly; the bd issue IS the brief.

```
┌─ Coordinator (Claude Code, Opus 4.7) ──────────────────────────┐
│   1. File bd issue (description + design + acceptance)         │
│   2. Pre-flight: bd show, ~/.config/opencode/oc-tier.sh check  │
│   3. opencode run "/hh-orchestrate <bd-id>"                    │
│      (or /hh-swarm <bd-id-1> <bd-id-2> ... for ≥2 disjoint)    │
│   4. Monitor OC log + bd progress notes                        │
│   5. Merge-gate: lint + draft push + smoke test + live push    │
│   6. Commit + push + bd close                                  │
└─────────────────────────────┬──────────────────────────────────┘
                              ▼
┌─ OC sub-orchestrator (lead-architect, paid tier) ──────────────┐
│   reads bd issue → decomposes → delegates:                     │
│     • repo-explorer (devstral-small-2:24b-cloud)               │
│     • senior-developer (glm-5.1:cloud)                         │
│     • qa-reviewer (nemotron-3-super:cloud)                     │
│   → stages changes (no commit, no push, no bd close)           │
│   → returns summary to coordinator                             │
└────────────────────────────────────────────────────────────────┘
```

### 8.1 Tier control

`~/.config/opencode/oc-tier.sh` — single command that flips both the `agents/` symlink AND the `opencode.json` top-level model field. Status: `oc-tier`. Flip: `oc-tier paid` or `oc-tier free`. Tier flip requires explicit user approval per global CLAUDE.md.

### 8.2 Free-tier scope discipline

When `oc-tier=free`: hard scope cap per dispatch is ≤2 prod files + ≤1 test OR ≤120 LoC of new/changed code. Larger work decomposes into Layer A (core file) + Layer B (orchestration) dispatched separately. See global CLAUDE.md "Free-tier scope discipline."

### 8.3 Agent hard locks for this project

(from `.opencode_hints` §1) — agents must NEVER:
1. Run `shopify theme push` (coordinator only)
2. Run `git push` to remote (coordinator only)
3. Run `bd close <id>` (coordinator runs merge-gate first)
4. Edit `templates/*.json`, `config/settings_data.json`, `config/settings_schema.json` (admin-managed)
5. Edit `assets/theme.css` directly (use `snippets/css-overrides.liquid`)
6. `git add .` / `git add -A` (only stage explicit paths)
7. Paraphrase product titles / blog body / store strings (must stay verbatim unless bd issue says otherwise)

---

## 9. External integrations (in production)

| Vendor / app | Footprint (mobile bytes) | Role | Status |
|---|---|---|---|
| GTM | 618 KB | tag manager | OWNED — operational tooling in `scripts/gtm-*.py` |
| Judge.me | (deferred) | product reviews | static-stars + deferred loader shipped; further work admin-side only (see bd memory `strategic-decision-2026-04-27`) |
| LimeSpot | varies | recommendations | targeted for Vertex AI replacement (bd `oyw`) |
| LoyaltyLion | 266 KB | loyalty program | NOT Smile.io — common confusion (bd memory `loyalty-vendor-loyaltylion-not-smile`) |
| Personalizer.io | 249 KB | A/B + personalization | always-on |
| Reamaze | 213 KB | live chat | targeted for defer-on-interaction (bd `dgb`) |
| Klaviyo | ~120 KB | email + popups | always-on; popup CLS mitigated (bd `e4a-γ`) |
| BookThatApp | 171 KB | appointment booking | targeted for per-route gating (bd `xex`) |
| BSS B2B Customer Portal | (admin-heavy) | wholesale portal | scheduled for full uninstall (bd `bjk`) |
| VisualQuizBuilder | 447 KB | hair-type quiz | targeted for per-route gating (bd `d4c`) |
| Elevar | (proxied) | server-side tracking via `/a/elevar` | 2.6s latency on PSI (bd `15f`) |
| BOGOS | (script-side) | buy-X-get-Y promos | targeted for custom replacement (bd `ur0`, $420/yr saved) |
| STKY | (script-side) | sticky add-to-cart | targeted for custom replacement (bd `r8r`, $300/yr saved) |
| Vertex AI Search for Commerce | (planned) | LimeSpot replacement | 4-6 week build, repo at `github.com/jjoson-ai/hairmnl-vertex`, bd `oyw` |

---

## 10. Recent operational history (chronological)

Each entry references a bd memory or commit for the long-form record.

| Date | Event | Reference |
|---|---|---|
| 2026-04-26 | Push regression — stale working tree clobbered live `layout/theme.liquid`. Originated the push protocol in `CLAUDE.md`. | `CLAUDE.md` |
| 2026-04-27 | Draft theme drift cleanup (134+ files synced from main to draft). Shopify CLI bulk push proven unreliable; per-file push + verify-via-curl is now the pattern. | bd memory `draft-theme-drift-cleanup-2026-04-27` |
| 2026-04-29 → 2026-05-02 | Mobile CLS sprint: CrUX mobile CLS p75 0.30 → 0.07. Desktop CLS p75 stuck at 0.20 (bd `987`). | bd memory `ga4-cls-poor-events-7d-baseline` |
| 2026-05-05 | Dashboard sprint (18 issues, 3 batches). Forward-only bot filter cutoff. GHA daily cron at 13:00 UTC operational. | bd memory `dashboard-sprint-complete-2026-05-05` |
| 2026-05-05 | Vertex AI rec engine 22-fix audit; Phases 0-3 live. Phase 4 cutover gates open. | bd memory `vertex-project-state` |
| 2026-05-06 | GTM JS error pipeline fixed end-to-end (tag 776 trigger). Per-template CWV slicing live (vux). | bd memory `js-error-pipeline-fixed-end-to-end`, `per-template-cwv-slicing-live` |
| 2026-05-06 | Three live theme bugs fixed (jhb Liquid quote, dy0 Bloggle <a><img>, 0ru richtext→html schema). | bd memory `three-live-theme-bugs-fixed-end-to-end` |
| 2026-05-11 | kt0 cart-drawer regression — `contain: layout` on `.header__wrapper` trapped fixed cart drawer. Fixed in commit ff1ef80. Defense codified as 3-layer system (§5). | bd memory `css-containment-gotcha-kt0-cart-drawer-regression-2026` |
| 2026-05-11 | Layer 3 (Playwright smoke test) shipped; generalized as global Claude skill `~/.claude/skills/smoke-test-overlays/`. | commit be0e9cd + bd68477 |
| 2026-05-11 | `metric_rating` GTM fix staged (tag 771 was missing the param mapping; ~50-60% of CWV events had blank rating). Container Version 143 pending publish. | bd `d00`, `docs/handoff-log.md` |
| 2026-05-12 | OC dispatch tier-leak diagnosed — `commands/hh-*.md` per-command `model:` frontmatter was overriding the symlink. Stripped from all 6 hh-* files; `oc-tier.sh` helper added. | global `CLAUDE.md` |

---

## 11. Where to look for what

| Question | File |
|---|---|
| What is this project? | this file |
| What does an agent need to know before editing? | `.opencode_hints` |
| Push protocol details? | `CLAUDE.md` |
| Beads workflow / session-close? | `CLAUDE.md` "Beads Issue Tracker" + run `bd prime` |
| Why is X broken / how was Y fixed? | `bd memories <keyword>` |
| Long-form post-mortem? | `docs/*-handoff-*.md` |
| Daily multi-model handoff log? | `docs/handoff-log.md` (append-only) |
| Perf state? | https://jjoson-ai.github.io/hairmnl-theme/ |
| Theme-check exemptions and why? | `.theme-check.yml` (each disabled rule is documented inline) |
| GTM container access? | `~/.config/hairmnl-gtm-token.json`, `scripts/gtm-auth.py` |
| GA4 property + queries? | property `248106289`, `scripts/web-vitals-report.py` |
| Per-template CWV breakdown? | dashboard at /friction tables (from `template` custom dimension) |
| Live theme IDs? | top of this file + `CLAUDE.md` |

---

## 12. Things that are NOT in scope of this repo

So agents don't go looking:

- **Shopify admin settings** — separate UI; reflected in `config/settings_*.json` but those are read-only here
- **GA4 admin** (custom dimension registration, audience definitions) — done in GA4 web UI by humans
- **GTM publishing** — done in GTM admin UI by coordinator after review
- **Cloudflare config** (cache rules, WAF, DNS) — separate dashboard, not in this repo
- **Vertex AI rec engine source** — separate repo `github.com/jjoson-ai/hairmnl-vertex`
- **Build pipeline for `assets/vendor.js`** — separate build, source not in this repo (bd `yzk` blocked on access)
- **3rd-party app settings** (Judge.me, LimeSpot, Reamaze, BookThatApp, VisualQuizBuilder, etc.) — vendor admin UIs; theme-side gating is generally impossible for app embeds

When a task requires any of the above, surface to the coordinator — agents do not have admin credentials and should not attempt to acquire them.
