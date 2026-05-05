# HairMNL Theme — Coordinator Handoff

This document hands the **coordinator role** for the HairMNL Shopify theme to a non-Anthropic model running in Claude Code via Ollama Cloud. It is the source of truth for cadence, workflow, data sources, and conventions. The Anthropic Claude Code session that produced it expects to resume later — so iterations done by the Ollama-Cloud coordinator MUST be logged to `docs/handoff-log.md` in append-only fashion.

---

## 1. Recommended coordinator model

**Primary: `minimax-m2.7:cloud`**
Reason: Opus-level SWE engineering and complex agentic judgment. The coordinator role demands triage, prioritization, and verification calls — minimax handles ambiguity well and stays coherent across long sessions.

**Alternatives, in order:**

| Model | When to use |
|---|---|
| `kimi-k2.6:cloud` | Long-horizon, multi-issue sessions; when minimax is rate-limited |
| `deepseek-v4-pro:cloud` | Big-context research (full codebase in 1M ctx); architecture review |
| `glm-5.1:cloud` | Co-executioner for multi-file refactors dispatched by the coordinator |
| `qwen3-coder-next:cloud` | Co-executioner for fast tool-use loops (find-fix-verify) |
| `deepseek-v4-flash:cloud` | One-line mechanical edits, quick lookups |

**Don't use as coordinator:** `devstral-small-2:24b-cloud` (too small for sustained judgment), `nemotron-3-super:cloud` (slow, overkill for a solo dev workflow).

---

## 2. Project context

- **Stack:** Pipeline 6.1.3 Shopify theme (NOT Online Store 2.0 — no auto-sync between draft & live, no settings_data.json polish layer)
- **Repo:** `github.com/jjoson-ai/hairmnl-theme` (private)
- **Storefront:** `creations-gdc.myshopify.com` → `www.hairmnl.com`
- **Theme IDs:**
  - **Live:** `131664707683` ("Pipeline 6 - Fix share image")
  - **Draft:** `140785582179` ("Claude Code")
- **Primary KPIs:** Core Web Vitals (CLS, LCP, INP) p75 for real shoppers; secondary AOV, conversion, accessibility

---

## 3. Cadence

Sessions are **ad-hoc, ~30 min – 2 hr**, driven by the user (operator). The coordinator does NOT need to be on a fixed schedule. Typical loop:

1. User opens a session, asks "what's next?" or names a specific issue
2. Coordinator surfaces `bd ready`, recommends 1–3 issues with rationale
3. User picks one → coordinator drives it through the workflow below
4. Coordinator logs the session in `docs/handoff-log.md` before the user closes the session

**RUM check cadence:** every 7 days post-deploy. If the user mentions "check the dashboard" or "pull RUM," run the dashboard script (see §6) and report the WoW INP/CLS deltas on /cart, /, and /products/*.

---

## 4. Workflow per issue

This is the canonical loop. Skipping steps causes regressions (see CLAUDE.md push regression of 2026-04-26).

```
┌──────────────────────────────────────────────────────────────┐
│  bd ready  →  bd update <id> --claim  →  implement           │
│       ↓                                                       │
│  git diff HEAD <files>   ← MANDATORY pre-push diff check     │
│       ↓                                                       │
│  push to draft theme 140785582179 (--only=<files> --nodelete)│
│       ↓                                                       │
│  smoke test in Brave (Claude-in-Chrome ext) on draft preview │
│       ↓                                                       │
│  push to live 131664707683 (--allow-live)                    │
│       ↓                                                       │
│  git add → commit → git push                                  │
│       ↓                                                       │
│  bd close <id>  →  append entry to docs/handoff-log.md       │
└──────────────────────────────────────────────────────────────┘
```

### Push protocol (immutable — from CLAUDE.md)

1. **NEVER** `shopify theme push` without `--only=<file>` flags
2. **ALWAYS** run `git diff HEAD <file>` before any push — confirm exact intended hunks
3. If diff is unexpected: `git checkout HEAD -- <file>` and re-apply, OR `shopify theme pull --theme=131664707683 --only=<file> --path=/tmp/live-pull` and diff against that
4. For layouts/snippets: push to draft first, smoke test, THEN live
5. After live push: `git add`, `git commit`, `git push` immediately. Drift between git HEAD and live is what enables regressions.

### Bd issue conventions

**Full command reference:**

- **Finding work:** `bd ready` · `bd list --status=open` · `bd list --status=in_progress` · `bd show <id>`
- **Claiming + working:** `bd update <id> --claim` · `bd update <id> --notes "..." --design "..."`
- **Closing:** `bd close <id>` · `bd close <id1> <id2> <id3>` (batch)
- **Creating:** `bd create --title="..." --description="..." --type=task|bug|feature --priority=2`
  - Priority: 0–4 or P0–P4 (NOT high/medium/low). 0 = critical, 2 = medium, 4 = backlog.
- **Cross-session memory:** `bd remember "insight"` to persist · `bd memories <keyword>` to search · DO NOT create MEMORY.md files (they fragment across accounts)
- **Sync:** `bd dolt push` at session end (auto-commits go to local Dolt regardless)
- **Context recovery:** `bd prime` after compaction or new session to load workflow context

**Hard rules:**

- Use bd for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Create the bd issue BEFORE writing code. Mark in_progress when starting. Close only after the deploy is verified.

**Session-close protocol** (mandatory before saying "done"):

```
1. Append entry to docs/handoff-log.md
2. bd close <id> (or batch close)
3. bd remember "<insight>" for any cross-session knowledge worth preserving
4. git status (should be clean)
5. git pull --rebase && bd dolt push && git push
6. git status MUST show "up to date with origin"
```

Work is NOT complete until `git push` succeeds. Never stop before pushing.

---

## 5. Data sources

| Source | What it tells you | How to access |
|---|---|---|
| **GA4 RUM** (property `248106289`) | Real-shopper INP/CLS/LCP with `debug_target` attribution to specific selectors | Via dashboard script (§6) or GA4 Explore |
| **CrUX** | p75 field data, 28-day rolling window, by URL pattern | Dashboard script with `--crux` flag |
| **PageSpeed Insights (PSI)** | Synthetic lab metrics, mobile + desktop | Dashboard script with `--psi` flag, or web UI |
| **Shopify Admin** | Order data, URL redirects, app configs (Smart SEO, LoyaltyLion, BSS B2B, LimeSpot, Vertex) | `creations-gdc.myshopify.com/admin` (operator-only auth) |
| **Beads** | Issue history, decisions, prior memories | `bd ready`, `bd show <id>`, `bd memories <keyword>` |
| **Git history** | What shipped when | `git log --oneline -20` |

---

## 6. Dashboard

Location: `scripts/build-perf-dashboard.py` → renders `dashboard/index.html`.

**Standard pull** (skip slow PSI + CrUX, use GA4 only):
```bash
GA4_PROPERTY_ID=248106289 python3 scripts/build-perf-dashboard.py --no-psi --no-crux
```

**Full pull** (slow, ~5 min, run weekly):
```bash
GA4_PROPERTY_ID=248106289 python3 scripts/build-perf-dashboard.py
```

**Sections to read first:**
1. **Top friction pages → INP** — sorted by poor% × pageviews, identifies highest-leverage targets
2. **INP + CLS Scorecard — Week-over-Week** — confirms whether last week's deploys moved the metric
3. **Attribution table** — `debug_target` selectors that capture poor INPs

After running, view at `dashboard/index.html`.

**Full dashboard handoff (state, roadmap, pending bugs):** `docs/dashboard-handoff.md`. Read this before working on the dashboard itself or before drawing conclusions from a snapshot.

---

## 7. Tools

- **`bd`** (beads) — primary issue tracker. Cheat sheet: `bd ready` / `bd show <id>` / `bd update <id> --claim` / `bd close <id>` / `bd remember "..."`
- **`shopify theme push --theme=<id> --only=<file> --nodelete [--allow-live]`** — only push pattern allowed
- **Claude-in-Chrome MCP (in Brave only)** — smoke tests on the draft preview. NOT installed in Edge.
- **`git`** — source of truth; HEAD must reflect what's on live after every session
- **`opencode`** for sub-task offload (you're already running Ollama Cloud — when you offload, prefer `glm-5.1:cloud` for multi-file refactors and `qwen3-coder-next:cloud` for agentic loops)

---

## 8. Active focus areas (as of 2026-05-05)

In priority order:

1. **INP** — /cart fixed today (issue `gjv`, commit `3a22d94`); next likely target: PDP variant picker
2. **CLS** — homepage now 88% good (up from 69% WoW); below 90% threshold so still on the list
3. **AOV** — pending issues `fw8` (LimeSpot admin tweaks, no code), `bvs` (Snapchat Pixel removal, admin)
4. **Vertex AI rec engine** — `oyw` separate 4-6 week build, NOT this session; design brief in `docs/vertex-placement-guide.md`
5. **A11y** — completed `9ct`, `6cb`, `D4` recently; check for new Lighthouse failures monthly
6. **Tech debt** — `yzk` (vendor.js tree-shake, blocked on build pipeline), `l55` (CRO data layer foundation)

Run `bd ready` for the live queue.

---

## 9. Recently shipped (2026-05 session log)

| Date | Issue | Title | Commit |
|---|---|---|---|
| 2026-05-05 | gjv | /cart INP — scope cart--loading to active row | `3a22d94` |
| 2026-05-04 | 24q | Dashboard INP+CLS WoW scorecard | `b5e4311` |
| 2026-05-04 | 6cb | Image alt schema fields for branded sections | `8e8ea93` |
| 2026-05-04 | y3j | Remove dead node-html-parser bundle code | `2f0a02b` |
| 2026-05-04 | 9ct | 3 Lighthouse a11y failures fixed | `f780939` |
| 2026-05-04 | d6e | Orphan snippet cleanup | `dd9908f` |

Full history: `git log --oneline`

---

## 10. Iteration log protocol

**Every session, before closing**, append an entry to `docs/handoff-log.md` in this exact format:

```markdown
### YYYY-MM-DD HH:MM (model: <model name>)

**Issues touched:** <bd-id>, <bd-id>
**Outcome:** shipped to live | drafted only | investigation only | blocked

**What was done:**
- <one-line bullets>

**Files modified:**
- `path/to/file.liquid:LINE` — what changed

**Verification:**
- diff check: ✓
- draft smoke test: ✓ / ✗ / skipped
- live push: ✓ / pending

**Next-session handoff notes:**
- <anything the next coordinator needs to know>
- <unresolved questions>
- <pending verifications (e.g., "check RUM in 7 days for issue X")>
```

**Why this matters:** the Anthropic Claude Code session that wrote this doc expects to resume later. Without the log, prior decisions and pending verifications are lost. The log is the seam between coordinators.

---

## 11. Resume instructions for the next Anthropic Claude Code session

When the user reopens Claude Code, they will say "resume" or "what's the status?". To pick up where the Ollama-Cloud coordinator left off:

1. Read `docs/handoff-log.md` — last 5 entries
2. Run `bd ready` and `bd list --status=in_progress`
3. Run `git log --oneline -10` to see what's been shipped
4. If a "pending verification" entry says "check RUM in 7 days," check the dashboard
5. Report the state in the standard status format (see CLAUDE.md "Multi-Model Coordination Protocol")

The Ollama-Cloud coordinator is acting as a peer, not a delegate. Trust its judgment but verify the diffs/commits it produced before extending its work.

---

## 12. Hard rules (do NOT violate)

- ❌ Never push without `--only=<file>` flags
- ❌ Never push without a pre-push diff check
- ❌ Never use TodoWrite or markdown TODO lists for task tracking — use `bd`
- ❌ Never use MEMORY.md files — use `bd remember`
- ❌ Never commit without immediately pushing (`git push`)
- ❌ Never end a session with uncommitted changes still in the working tree
- ❌ Never close a `bd` issue before verifying the deploy actually worked
- ❌ Never run smoke tests in Edge (only `read` permission); always Brave (full Claude-in-Chrome access)
