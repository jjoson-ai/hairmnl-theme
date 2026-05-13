# HairMNL Shopify theme

Production theme for [www.hairmnl.com](https://www.hairmnl.com) — a Philippines-based haircare retailer (Kérastase, Davines, Aveda, L'Oréal Professionnel, Olaplex, K18, and more) running on Shopify with the **Pipeline 6.1.3** vanilla theme family.

This repo is the source of truth for the live theme. It also carries the operational tooling (perf dashboard, Beads issue tracker, agent-dispatch scripts) that supports continuous Core Web Vitals work and multi-agent collaboration.

---

## What this is

| Field | Value |
|---|---|
| Storefront | `www.hairmnl.com` (Cloudflare in front of Shopify) |
| Shopify shop | `creations-gdc.myshopify.com` |
| Theme family | Pipeline 6.1.3 (Vanilla) — **not** Online Store 2.0 |
| Live theme ID | `131664707683` |
| Draft theme ID | `140785582179` |
| Issue tracker | [Beads](https://github.com/steveyegge/beads) (`bd`) — local + DoltDB |
| Dashboard | [jjoson-ai.github.io/hairmnl-theme](https://jjoson-ai.github.io/hairmnl-theme/) (PSI + GA4 RUM + CrUX) |
| Primary contact | `jjoson@clickcommerce.digital` |

Static page templates are `.liquid` (180+ in `templates/`). There is **no auto-sync** between draft and live themes — every deploy is an explicit `shopify theme push --only=<file>` followed by a git commit. The 2026-04-26 regression that triggered this guardrail is documented in [`CLAUDE.md`](CLAUDE.md).

## Quick start

```bash
# 1. Clone
git clone git@github.com:jjoson-ai/hairmnl-theme.git
cd hairmnl-theme

# 2. Install the Shopify CLI 3.x (https://shopify.dev/docs/themes/tools/cli)
brew install shopify-cli
shopify theme list                 # prompts an OAuth flow on first run

# 3. Beads issue tracker
brew install beads                 # or `cargo install beads-cli`
bd prime                           # show project context + commands

# 4. (Optional) Python tooling for the perf dashboard + GTM/GA4 scripts
python3 -m pip install -r scripts/requirements.txt 2>/dev/null \
  || python3 -m pip install google-api-python-client google-auth google-analytics-data google-auth-oauthlib

# 5. Copy env template — fill in any secrets you have access to
cp .env.example .env
# then either `source .env` or export the vars in your shell rc.
```

The repo does NOT auto-load `.env` — scripts read `os.environ` directly. Put exports in your shell profile, or run scripts inline: `GA4_PROPERTY_ID=248106289 ./scripts/build-perf-dashboard.py`.

## Repository layout

```
hairmnl-theme/
├── README.md                ← you are here
├── ARCHITECTURE.md          full architecture + operating model (read this next)
├── CLAUDE.md                project-specific rules + push protocol (hard locks)
├── AGENTS.md                Beads workflow rules for any agent
├── .opencode_hints          OC sub-orchestrator rules (CSS gotchas, kt0 rule, etc.)
│
├── layout/                  theme.liquid (the master <head>/<body> shell)
├── templates/               180+ .liquid page templates (PDP, collection, cart, etc.)
├── sections/                section snippets bound to dynamic blocks
├── snippets/                shared partials — most CSS overrides live in
│                            snippets/css-overrides.liquid
├── assets/                  theme.css (production minified), custom-theme.css,
│                            cart-page.css, theme.js, vendor.js, images
├── config/                  settings_data.json (admin-managed — do not edit
│                            manually), settings_schema.json
├── locales/                 i18n
│
├── docs/                    handoff-log.md (per-session coordinator notes),
│                            coordinator-handoff.md, baselines, vertex briefs
├── dashboard/               self-hosted perf dashboard (deployed to GH Pages)
│   ├── index.html
│   └── data/snapshots.jsonl
│
├── scripts/                 Python tooling — see "Tooling" below
├── design-research/         design exploration artifacts (gitignored from theme push)
│
├── .beads/                  Beads issue tracker state (versioned)
└── .github/workflows/       kt0-css-lint, perf-dashboard refresh, GH Pages deploy,
                             admin-file-sync
```

## Tooling

The Python scripts under `scripts/` automate the operations layer. Most useful entry points:

| Script | Purpose |
|---|---|
| `build-perf-dashboard.py` | Refresh dashboard (PSI + GA4 RUM + CrUX). Output: `dashboard/index.html` + appends `dashboard/data/snapshots.jsonl`. |
| `web-vitals-report.py` | Slice GA4 CWV data (LCP/CLS/INP/FCP/TTFB) by page / device / template / `debug_target`. |
| `check-overlay-css.py` | kt0 CSS lint — catches `contain: layout` / `transform` on parents of fixed/absolute descendants. Runs in CI on every push touching `*.liquid` / `*.css` / `*.scss`. **Required to pass before any live push.** |
| `smoke-test-drawers.py` | Playwright-based check that cart drawer, mobile nav, search overlay, and modals render correctly on draft. Required before any push touching layout or stacking-context CSS. |
| `gtm-audit.py` | Read-only audit of the GTM container (tags, triggers, variables). |
| `gtm-find-js-error.py`, `gtm-fix-js-error-*.py` | GTM tag fixes via API (used for the d00 / l3g metric_rating chain). |
| `weekly-game-plan.py` | Generate a markdown weekly summary from GA4 + Beads. |

Most scripts require `GA4_PROPERTY_ID=248106289` and access to the credential files in `~/.config/` (see [Credentials](#credentials)).

## Push protocol (live theme deploys)

**Never `shopify theme push` without `--only=<file>` flags.** A no-filter push uploads the entire working tree, which is almost guaranteed to drag stale or WIP content into live. See [`CLAUDE.md`](CLAUDE.md) for the full protocol.

Standard flow:

```bash
# 1. Verify the diff is exactly what you intend
git diff HEAD <file>

# 2. Run the kt0 lint
python3 scripts/check-overlay-css.py

# 3. Push to DRAFT first
shopify theme push --store=creations-gdc.myshopify.com \
  --theme=140785582179 --nodelete --only=<file>

# 4. Smoke-test the draft preview (manual + scripted)
open "https://www.hairmnl.com/?preview_theme_id=140785582179"
python3 scripts/smoke-test-drawers.py --config=scripts/smoke-test-drawers.config.json --theme=draft

# 5. Push to LIVE
shopify theme push --store=creations-gdc.myshopify.com \
  --theme=131664707683 --allow-live --only=<file>

# 6. Commit + push git
git add <file>
git commit -m "..."
git pull --rebase
git push
```

## Beads issue tracker workflow

```bash
bd ready              # find available work (filters out blocked deps)
bd show <id>          # full description + design + acceptance
bd update <id> --claim
# ... do the work ...
bd update <id> --append-notes "MERGE_GATE_PASS at <ts>\n$(git show HEAD --stat)"
bd close <id>         # coordinator only — see CLAUDE.md
bd dolt push          # sync to remote
```

Project rules (`AGENTS.md`):
- Use `bd` for **all** task tracking — do **not** use `TodoWrite`, `TaskCreate`, or markdown TODO lists.
- Use `bd remember "insight"` for persistent knowledge — do not create `MEMORY.md` files.
- Run `bd prime` for the full command reference.

## Multi-agent dispatch (OpenCode)

This project uses Claude Code (CC) as coordinator and dispatches bounded tasks to OpenCode (OC) sub-orchestrators via `/hh-orchestrate` and `/hh-swarm`. See `~/.claude/CLAUDE.md` and `.opencode_hints` for the SOP.

```bash
# Single ticket
cd $(pwd) && opencode run \
  --message "/hh-orchestrate

Dispatched-task mode: work specifically on bd-id <bd-id>.
Do NOT run \`bd ready\` to pick a different task — claim and work this id." \
  --dangerously-skip-permissions

# ≥2 disjoint tickets in parallel
opencode run --message "/hh-swarm <id1> <id2> <id3>" --dangerously-skip-permissions
```

Hard locks for any dispatched agent (`.opencode_hints` — non-negotiable):
1. No `shopify theme push` — coordinator owns deploys.
2. No `git push` to remote — coordinator owns.
3. No `bd close <id>` — coordinator runs merge-gate.
4. No edits to admin-managed JSON in `templates/` / `config/settings_data.json`.
5. No edits to `assets/theme.css` (minified output). Use `snippets/css-overrides.liquid`.
6. Before editing any CSS reservation, grep **both** `snippets/css-overrides.liquid` and `assets/custom-theme.css` for the target selector — the two files often have duplicate rules at different specificities. The 2026-05-13 `hod` fix shipped as a NO-OP initially because OC only edited one file.

## Credentials

Credentials live in `~/.config/` (outside the repo, not gitignored within the repo because they aren't here):

| File | Used by | How to obtain |
|---|---|---|
| `~/.config/hairmnl-ga4-key.json` | GA4 Data API queries (dashboard, web-vitals-report) | Google Cloud service account: `seo-agent-489812 → hairmnl-rum-reader@`. See `scripts/grant-ga4-access.py` for the GA4 admin binding. |
| `~/.config/hairmnl-oauth-client.json` | GTM API OAuth (desktop client) | Google Cloud OAuth 2.0 desktop client. |
| `~/.config/hairmnl-gtm-token.json` | GTM API access token (cached after first auth) | Auto-created on first run of `gtm-audit.py` / `gtm-find-js-error.py`. |

The PSI API key is stored in macOS Keychain:

```bash
security add-generic-password -a $USER -s psi-api-key -w "AIza..."
```

For GitHub Actions, equivalent secrets are set in repo settings:
- `SHOPIFY_CLI_PARTNERS_TOKEN` + `SHOPIFY_FLAG_STORE` (admin-file-sync workflow)
- `PSI_API_KEY` + `GA` (perf-dashboard refresh workflow)

## Documentation map

| File | Purpose |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Single source of truth for architecture, integration inventory, perf instrumentation chain, dashboard replication guide. **Read this after the README.** |
| [`CLAUDE.md`](CLAUDE.md) | Project-specific rules: theme IDs, push protocol, the 2026-04-26 regression history, kt0 CSS containment rule, session-close protocol. |
| [`AGENTS.md`](AGENTS.md) | Beads-driven workflow rules for any agent (CC, OC, Cursor). |
| [`.opencode_hints`](.opencode_hints) | OC sub-orchestrator hard locks: no live push, kt0 rule, CSS reservation parity, push protocol reference. |
| [`docs/handoff-log.md`](docs/handoff-log.md) | Per-session coordinator handoffs. Newest entries at top. |
| [`docs/coordinator-handoff.md`](docs/coordinator-handoff.md) | Coordinator role spec + handoff format. |
| [`docs/baselines/`](docs/baselines/) | Frozen PSI / CrUX baselines from prior sprints. |
| [`vertex-placement-design-brief.md`](vertex-placement-design-brief.md), [`vertex-placement-guide.md`](vertex-placement-guide.md) | Vertex AI recommendations rollout (separate project, replaces LimeSpot — bd `oyw`). |

## Performance work

The active Core Web Vitals improvement loop:

```
RUM (web-vitals-reporter.liquid)
    → GTM (tag 766 "GA4 – Web Vitals", trigger 758)
    → GA4 (custom dimensions: metric_rating, debug_target, template, ...)
    → scripts/web-vitals-report.py / build-perf-dashboard.py
    → dashboard/index.html (hosted on GH Pages)
    → bd issues + Phase 2 fixes
```

Field metric snapshot (CrUX 28-day p75, current as of 2026-05-13):

| Device | LCP | CLS | INP |
|---|---|---|---|
| Mobile | 3185 ms (poor) | **0.060 (good)** | 244 ms (needs-improvement) |
| Desktop | 2720 ms (poor) | 0.190 (needs-improvement) | **143 ms (good)** |

The May 2 / May 12 / May 13 CLS sprints brought mobile CLS from 0.30 → 0.06. Desktop CLS is the active focus (bd `987` + Phase 2 children `hod`, `7i0`, `uj2`).

## License & ownership

Proprietary theme for HairMNL / Creations GDC. Not licensed for redistribution.
