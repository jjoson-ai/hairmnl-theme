# HairMNL Performance Dashboard

Self-hosted PWI/CWV dashboard. Renders to a single static HTML file. No SaaS, no admin UI clicks, no server running.

## View it

```bash
open dashboard/index.html
```

That's it. The HTML is self-contained (CSS inline, Chart.js from a public CDN), so it works opened directly from the filesystem.

## Refresh it

```bash
GA4_PROPERTY_ID=248106289 ./scripts/build-perf-dashboard.py
```

What this does:
1. Runs PSI Lab (3 runs each on mobile + desktop) and takes the median per metric.
2. Pulls 7 days of GA4 RUM data (real shoppers): CWV ratings, top friction pages, INP attribution targets, JS errors.
3. Appends the snapshot to `dashboard/data/snapshots.jsonl`.
4. Re-renders `dashboard/index.html` from the full snapshot history.

Total time: ~6 minutes (PSI is the slow part — 3 runs × 2 strategies × ~30–60s each).

## Useful flags

```bash
./scripts/build-perf-dashboard.py --no-psi           # GA4 only, ~10s
./scripts/build-perf-dashboard.py --no-ga4           # PSI only
./scripts/build-perf-dashboard.py --psi-only-mobile  # skip desktop PSI (~halves PSI time)
./scripts/build-perf-dashboard.py --psi-runs=1       # single PSI run per strategy (faster, noisier)
./scripts/build-perf-dashboard.py --render-only      # don't fetch new data, just re-render HTML from existing snapshots
./scripts/build-perf-dashboard.py --ga4-days 30      # change RUM lookback window
```

## Daily cron (recommended)

```cron
0 6 * * * cd /Users/y9378348c/Projects/hairmnl-theme && GA4_PROPERTY_ID=248106289 ./scripts/build-perf-dashboard.py >> ~/.local/log/hairmnl-perf.log 2>&1
```

6am Manila time = roughly when overnight CDN cache settles, before the morning traffic peak. PSI lab numbers are most representative when the site has settled.

## Required setup (already done locally)

- `GA4_PROPERTY_ID=248106289` env var
- `~/.config/hairmnl-ga4-key.json` — GA4 service account key
- `PSI_API_KEY` in macOS Keychain: `security add-generic-password -a "$USER" -s "psi-api-key" -w "AIza..."`
- `pip install --user google-analytics-data`

## Optional: free public hosting via GitHub Pages

The repo's `dashboard/` directory can be served as a static site:

1. Repo Settings → Pages → Source: `main` branch, folder: `/dashboard`
2. Your dashboard URL becomes `https://<org>.github.io/<repo>/`
3. Each commit that updates `dashboard/index.html` auto-deploys (≤1 min).

Combined with a GitHub Action that runs the dashboard build daily and commits the result, this gives you a free, public, always-up-to-date dashboard.

(If you don't want it public: skip Pages, the local file works fine. Or push to a private gh-pages branch with auth gate.)

## What's in each section

- **Today's snapshot — PSI Lab (mobile / desktop)** — The 6 Lighthouse mobile/desktop scores for the most recent run. Δ vs previous snapshot shown when ≥2 snapshots exist. Color-coded by Google's PASS/NEEDS-IMPROV/POOR thresholds.
- **Trend over time — PSI Lab mobile** — 4 line charts (Score, LCP, TBT, CLS) across the most recent 30 snapshots. Shows whether perf is trending up or down over weeks.
- **Real-shopper Core Web Vitals — last 7 days** — % of pageviews in good / needs-improvement / poor for each of the 5 CWV metrics (LCP, CLS, INP, FCP, TTFB), pulled from the live GA4 web-vitals.js v4 pipeline. Each metric tagged ✓ PASS / ✗ FAIL based on Google's "≥75% good" CWV criterion.
- **Top friction pages** — 5 worst pages per metric (LCP, INP, CLS) by % poor rate. Filtered to pages with ≥50 pageviews to avoid low-volume noise. **This is the primary input for picking what to optimize next.**
- **Top INP attribution targets** — Which CSS selectors / elements caused poor interactions. `(not set)` = interaction during page load (TBT-bound, not handler-bound).
- **JavaScript errors — last 7 days** — Top 10 js_error events from the inline error-tracking snippet.
- **vs April 26 baseline** — Hard-coded comparison row showing today's mobile lab numbers vs the early-April baseline. Captures the cumulative perf project impact.

## Data file: `dashboard/data/snapshots.jsonl`

One JSON object per line, append-only. Each snapshot has:

```json
{
  "timestamp": "2026-04-29T12:07:28Z",
  "psi": {
    "mobile":  {"score": 27, "fcp_ms": 4400, "lcp_ms": 14700, "tbt_ms": 3350, "cls": 0.025, "si_ms": 14500},
    "desktop": {"score": 55, ...}
  },
  "ga4": {
    "days": 7,
    "metrics": {"LCP": {"good": 8758, "needs-improvement": 1225, "poor": 765, "total": 10748, "p_good": 0.81, "p_poor": 0.07}, ...},
    "top_pages": {"LCP": [...], "INP": [...], "CLS": [...]},
    "top_inp_targets": [...],
    "js_errors": [...]
  }
}
```

Safe to inspect with `jq`:

```bash
jq -c '{ts: .timestamp, mobile_tbt: .psi.mobile.tbt_ms, lcp_pct_good: .ga4.metrics.LCP.p_good}' dashboard/data/snapshots.jsonl
```

## Sister tool

This dashboard is the self-hosted complement to the Looker Studio dashboard tracked in beads `24q`. Use whichever is easier to share with the audience:

| | Self-hosted (this) | Looker Studio (24q) |
|---|---|---|
| Cost | Free | Free |
| Hosting | Local file or GH Pages | Google Cloud (auto) |
| Refresh | Manual or cron | Auto every 12h via GA4 connector |
| Customizable by Claude | ✓ Yes (Python + HTML) | ✗ No (admin UI only) |
| Good for | Daily ops, trend tracking, automation feed | Team-wide sharing, slice-and-dice |
