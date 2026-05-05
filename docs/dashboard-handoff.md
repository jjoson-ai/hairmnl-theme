# PWI / CWV Dashboard — Handoff

State of the self-hosted performance dashboard as of 2026-05-05. Companion to `docs/coordinator-handoff.md` — read that for the broader project workflow.

---

## 1. What it is

A self-hosted PWI/CWV dashboard rendered to a single static HTML file. No SaaS, no admin UI, no server.

- **Live URL:** https://jjoson-ai.github.io/hairmnl-theme/
- **Source:** `scripts/build-perf-dashboard.py` (1,363 lines, single file)
- **Output:** `dashboard/index.html` (self-contained — CSS inline, Chart.js from CDN)
- **Data store:** `dashboard/data/snapshots.jsonl` (append-only, JSON-per-line)
- **Auto-deploy:** GitHub Action `.github/workflows/pages.yml` on push to `main` touching `dashboard/**`
- **Daily cron:** macOS launchd plist at `scripts/launchd/com.hairmnl.daily-perf.plist` (6am Manila time)
- **Sister tool:** Looker Studio dashboard (issue `24q`) — auto-refresh, less customizable. Use whichever fits the audience.

Full README: `dashboard/README.md`.

---

## 2. What has been done

### Data sources wired up

| Source | Function | What it pulls |
|---|---|---|
| **PSI Lab** | `run_psi_median()` | Mobile + desktop, 3 runs each, median per metric. Score, FCP, LCP, TBT, CLS, SI |
| **GA4 RUM** | `query_ga4_rum()` | Real-shopper CWV (LCP, CLS, INP, FCP, TTFB), top friction pages, INP attribution selectors, JS errors. 7-day rolling default |
| **CrUX** | `query_crux()` | Field p75, 28-day rolling — for ground-truth comparison vs GA4 RUM and PSI Lab |

### Sections rendered (in HTML order)

1. **Today's snapshot — PSI Lab** (mobile + desktop) with Δ vs previous snapshot, color-coded by Google PASS/NIP/POOR thresholds
2. **Trend over time — PSI Lab mobile** — 4 line charts (Score, LCP, TBT, CLS) across last 30 snapshots
3. **Real-shopper CWV — last 7 days** — % good / NIP / poor per metric, ✓ PASS / ✗ FAIL on the 75% rule
4. **INP + CLS Scorecard — Week-over-Week** *(added in `b5e4311`, issue `24q`)* — confirms whether last week's deploys moved the needle
5. **90-day targets** *(added with WoW scorecard)* — top-of-page goals for INP/CLS/LCP good%
6. **Top friction pages** — 5 worst per metric by % poor × pageviews, ≥50 pageview filter; **primary input for picking the next optimization**
7. **Top INP attribution targets** — `debug_target` selector → poor-rate; `(not set)` = page-load TBT (not handler-bound)
8. **JavaScript errors** — top 10 `js_error` events from inline error-tracking snippet
9. **vs April 26 baseline** — hardcoded comparison to early-April lab numbers; captures cumulative impact of the perf project

### Polish work shipped

- Per-metric tooltips with plain-English explanations + action guidance (`c90d97d`)
- CrUX CLS scaling fix (HTTP API returns decimals, not int×100) (`2d721dc`)
- Python 3.9 compatibility (`f9b1ea6`)
- PSI HTTP timeout 120→180s (`57c05c6`)
- Tabbed mobile/desktop view, readable URLs, GitHub Pages publishing (`71c9abc`)
- Daily auto-refresh via launchd (`d0dc3f6`)
- Stripped duplicate "Fix:" prefix in tooltip action text (`80cde54`)

### Snapshot history

- **17 snapshots** logged (since 2026-04-26 baseline, ~daily cadence)
- **Latest (2026-05-05 03:00 UTC):**
  - PSI mobile: score 28, LCP 13.4s, TBT 3.9s, CLS 0.02
  - GA4 RUM (7d): LCP 85% good / 8% poor · CLS 88% good / 7% poor · INP 84% good / 6% poor

---

## 3. Roadmap

### Near-term (within 2 weeks)

- **Verify gjv fix in RUM (≥7 days post-deploy → after 2026-05-12):** /cart poor INP should drop from 21% toward <10%. Run `--no-psi --no-crux` and read the WoW scorecard.
- **Add bot filter for /pages/privacy-policy** — bd memory `ga4-privacy-policy-bot-2026-05-01` documents ~538k bot events / 14 days (49× homepage volume) skewing the friction-page list. The signature is confirmed; add a filter in `query_ga4_rum()`.
- **Document Looker Studio vs self-hosted decision** — when does each get used, who's the audience? Add a one-paragraph guide to `dashboard/README.md` "Sister tool" section.

### Medium-term (1–2 months)

- **Per-template CWV slicing** — currently friction-pages are by URL. Add a slice by Shopify template (`product`, `collection`, `cart`, `index`) to spot template-level regressions. Requires GA4 custom dimension on `Shopify.template`.
- **Third-party script weight tracker** — chart bundle bytes by origin (LimeSpot, Klaviyo, BSS B2B, Elevar, GTM) over time. Catch silent bloat from app updates.
- **CrUX-only "production truth" view** — currently buried; promote to its own card. CrUX is the p75 metric that actually matters for SEO; GA4 RUM is sample-of-1 from us.
- **Slack/email alert on threshold breach** — e.g. INP poor% > 15% or LCP regression > 10pp WoW. Wire via launchd post-script hook into Slack webhook.

### Long-term / nice-to-have

- **Refactor `build-perf-dashboard.py`** — single file is at 1,363 lines. If it grows past ~2k, split into `psi.py`, `ga4.py`, `crux.py`, `render.py`, `main.py`. Not urgent; the script is readable.
- **Snapshot rotation policy** — `snapshots.jsonl` is append-only. 17 lines now, but will grow indefinitely. Consider archiving snapshots older than 365 days to `dashboard/data/archive/YYYY.jsonl` to keep the active file scannable.
- **Mobile responsive HTML** — currently desktop-first; on phones the trend charts compress awkwardly.
- **A/B comparison mode** — diff two arbitrary snapshots side-by-side (not just current vs previous).

---

## 4. Bugs & improvements pending

### Direct dashboard bugs

| Severity | Description | Location | Notes |
|---|---|---|---|
| Low | Snapshot file grows unboundedly | `dashboard/data/snapshots.jsonl` | 17 lines today; not urgent |
| Low | Privacy-policy bot traffic skews top-friction lists | `query_ga4_rum()` ~line 267 | Bot signature documented in `bd memories ga4-privacy-policy-bot` |
| Low | No automated regression alert | `main()` | Manual WoW scorecard reading only |
| Low | Mobile HTML not responsive | `render_html()` ~line 1231 | Trend charts compress on phones |

### Related bd issues that affect dashboard interpretation

| ID | Priority | Title | Why it matters |
|---|---|---|---|
| `15f` | P2 | Elevar /a/elevar tracking endpoint takes 2.6s on every PSI run | Skews TBT consistently in PSI lab numbers; treat lab TBT as "with Elevar tax" until fixed |
| `06u` | P3 | Re-run PSI to verify CDN+Klaviyo cache fully settled | One-shot verification task; may reveal that recent PSI dips are cold-cache artifacts |
| `b5f` | P3 | Reamaze chat WINDOW body shift — confirm via GA4 + DevTools | Candidate CLS culprit; verify in dashboard's CLS friction pages before broadening fix |
| `gjv` | closed 2026-05-05 | /cart INP fix | **Pending RUM verification after 2026-05-12** |

### Improvements queued (no bd issue yet — file when picked up)

- Tooltip text for the WoW scorecard explaining what "good%" means and why >75% matters
- Add a "data freshness" badge — stale snapshot warning if newest is >48h old
- Surface CrUX vs GA4 RUM divergence — they should be close; large drift = sampling bias to investigate

---

## 5. Operational quick-reference

### Refresh commands

```bash
# Fast (GA4 only, ~10s) — for daily ops
GA4_PROPERTY_ID=248106289 ./scripts/build-perf-dashboard.py --no-psi --no-crux

# Full (~6 min)
GA4_PROPERTY_ID=248106289 ./scripts/build-perf-dashboard.py

# Render-only (no fetch, just rebuild HTML from existing snapshots)
./scripts/build-perf-dashboard.py --render-only
```

### Required env / secrets

- `GA4_PROPERTY_ID=248106289`
- `~/.config/hairmnl-ga4-key.json` — GA4 service account key
- `PSI_API_KEY` in macOS Keychain: `security find-generic-password -a "$USER" -s "psi-api-key" -w`
- `pip install --user google-analytics-data`

### Daily cron

`launchctl load ~/Library/LaunchAgents/com.hairmnl.daily-perf.plist` — fires at 6am Manila, logs to `~/.local/log/hairmnl-perf.log`.

### Inspect snapshots

```bash
# One-line summary of every snapshot
jq -c '{ts: .timestamp, mob_score: .psi.mobile.score, lcp_good: .ga4.metrics.LCP.p_good, inp_good: .ga4.metrics.INP.p_good}' dashboard/data/snapshots.jsonl
```

### Where to look first when "the dashboard looks wrong"

1. `dashboard/data/snapshots.jsonl` — is the latest snapshot present and well-formed?
2. `~/.local/log/hairmnl-perf.log` — did last cron run error?
3. `query_ga4_rum()` — most rendering bugs trace back to RUM payload shape changes
4. `_rate_class_*()` helpers (lines 833–875) — color thresholds; tweak only after confirming Google's official ranges haven't shifted

---

## 6. For the next coordinator

When working on the dashboard:

- **Don't break the snapshot schema** — `snapshots.jsonl` is the historical record. Adding fields is safe; renaming/removing breaks all rendering of older snapshots.
- **PSI is slow and rate-limited** — develop with `--no-psi`. Only run the full pull when actually publishing.
- **CrUX requires API key + URL must be in the dataset** — if `query_crux()` returns None, that's expected for low-traffic URLs.
- **The dashboard is the primary input for picking what to optimize next** — when in doubt about priority, point the user to "Top friction pages" and let the data drive.
- **Log dashboard work to `docs/handoff-log.md`** like any other project work. Pending verifications (e.g., "check RUM after X date") are especially important to carry over.
