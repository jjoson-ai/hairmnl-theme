#!/usr/bin/env python3
"""
build-perf-dashboard.py — Build the self-hosted HairMNL performance dashboard.

Combines two data sources into one HTML file:
  1. PSI Lab (PageSpeed Insights API) — single-run mobile + desktop synthetic
     measurements via Google's free PSI v5 API. Same data as run-psi.sh.
  2. GA4 RUM (Google Analytics 4) — real-shopper Core Web Vitals + JS errors
     last 7 days. Same query pattern as web-vitals-report.py.

Output:
  dashboard/index.html         — single-file HTML dashboard (open in browser)
  dashboard/data/snapshots.jsonl  — historical snapshots, one line per run

Usage:
  ./scripts/build-perf-dashboard.py                      # full snapshot
  ./scripts/build-perf-dashboard.py --no-psi             # skip PSI (faster, GA4 only)
  ./scripts/build-perf-dashboard.py --no-ga4             # skip GA4 (PSI only)
  ./scripts/build-perf-dashboard.py --psi-only-mobile    # skip desktop PSI (~halves PSI time)
  ./scripts/build-perf-dashboard.py --render-only        # don't fetch new data, re-render from existing snapshots
  ./scripts/build-perf-dashboard.py --url URL            # PSI for a specific URL (default: hairmnl.com)

Requires (same as the two source scripts):
  - GA4_PROPERTY_ID env var (e.g. 248106289)
  - ~/.config/hairmnl-ga4-key.json (GA4 service account)
  - PSI_API_KEY in macOS Keychain (`security add-generic-password -a $USER -s psi-api-key -w "AIza..."`)

Cron schedule (recommended): daily 6am Manila time
  0 6 * * * cd /path/to/hairmnl-theme && ./scripts/build-perf-dashboard.py >> ~/.local/log/hairmnl-perf.log 2>&1
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median


REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = REPO_ROOT / "dashboard"
DATA_DIR = DASHBOARD_DIR / "data"
SNAPSHOTS_PATH = DATA_DIR / "snapshots.jsonl"
HTML_OUT_PATH = DASHBOARD_DIR / "index.html"

DEFAULT_URL = "https://www.hairmnl.com/"
VITAL_EVENTS = ["LCP", "CLS", "INP", "FCP", "TTFB"]

# Apr 26, 2026 baseline (from psi_baselines.md memory). Mobile lab.
BASELINE_2026_04_26 = {
    "score": 26,
    "lcp_ms": 11800,
    "tbt_ms": 4340,
    "cls": 0.043,
    "fcp_ms": 3140,
    "si_ms": 23500,
}


# ───────────────────────── PSI ─────────────────────────

def get_psi_key() -> str:
    """Fetch PSI API key from env or macOS Keychain."""
    key = os.environ.get("PSI_API_KEY")
    if key:
        return key
    try:
        out = subprocess.check_output(
            ["security", "find-generic-password", "-a", os.environ["USER"], "-s", "psi-api-key", "-w"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip()
    except Exception:
        print("ERROR: PSI_API_KEY not set and not in Keychain.", file=sys.stderr)
        print("  Set with: security add-generic-password -a $USER -s psi-api-key -w 'AIza...'", file=sys.stderr)
        sys.exit(1)


def run_psi_once(url: str, strategy: str, key: str) -> dict | None:
    """Single PSI run for url+strategy. Returns dict of metrics or None on error."""
    api = (
        "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        f"?url={urllib.parse.quote(url, safe='')}"
        f"&strategy={strategy}"
        "&category=performance"
    )
    req = urllib.request.Request(api, headers={"X-goog-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read())
    except Exception as e:
        print(f"  PSI {strategy} run error: {e}", file=sys.stderr)
        return None
    if "error" in d:
        print(f"  PSI {strategy} API error: {d['error'].get('message')}", file=sys.stderr)
        return None
    audits = d["lighthouseResult"]["audits"]
    cat = d["lighthouseResult"]["categories"]["performance"]
    return {
        "score": round(cat["score"] * 100),
        "fcp_ms": audits["first-contentful-paint"]["numericValue"],
        "lcp_ms": audits["largest-contentful-paint"]["numericValue"],
        "tbt_ms": audits["total-blocking-time"]["numericValue"],
        "cls": audits["cumulative-layout-shift"]["numericValue"],
        "si_ms": audits["speed-index"]["numericValue"],
    }


def run_psi_median(url: str, strategy: str, n: int = 3) -> dict | None:
    """Run PSI n times for url+strategy and return median values across runs."""
    key = get_psi_key()
    print(f"  PSI {strategy} ({n} runs)...", flush=True)
    runs = []
    for i in range(n):
        r = run_psi_once(url, strategy, key)
        if r:
            runs.append(r)
            print(f"    run {i+1}: score {r['score']}  LCP {r['lcp_ms']/1000:.1f}s  TBT {r['tbt_ms']:.0f}ms")
    if not runs:
        return None
    return {k: round(median(r[k] for r in runs), 3) if k == "cls" else int(median(r[k] for r in runs)) for k in runs[0]}


# ───────────────────────── GA4 ─────────────────────────

def get_ga4_client():
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
    except ImportError:
        print("ERROR: pip install --user google-analytics-data", file=sys.stderr)
        sys.exit(1)
    key_path = os.environ.get("GA4_KEY") or os.path.expanduser("~/.config/hairmnl-ga4-key.json")
    if not os.path.exists(key_path):
        print(f"ERROR: GA4 key not found: {key_path}", file=sys.stderr)
        sys.exit(1)
    pid = os.environ.get("GA4_PROPERTY_ID")
    if not pid:
        print("ERROR: GA4_PROPERTY_ID env var required", file=sys.stderr)
        sys.exit(1)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
    return BetaAnalyticsDataClient(), f"properties/{pid}"


def query_ga4_rum(days: int = 7) -> dict:
    """Pull GA4 web-vitals + errors. Returns structured data ready for HTML render."""
    from google.analytics.data_v1beta.types import (
        DateRange, Dimension, Metric, RunReportRequest,
        FilterExpression, FilterExpressionList, Filter, OrderBy,
    )

    def _eq(field, value):
        return Filter(field_name=field, string_filter=Filter.StringFilter(value=value))

    def _in(field, values):
        return Filter(field_name=field, in_list_filter=Filter.InListFilter(values=values))

    def _and(*filters):
        if len(filters) == 1:
            return FilterExpression(filter=filters[0])
        return FilterExpression(and_group=FilterExpressionList(
            expressions=[FilterExpression(filter=f) for f in filters]))

    client, prop = get_ga4_client()
    date_range = [DateRange(start_date=f"{days}daysAgo", end_date="today")]

    # Overall metric distribution by rating
    print(f"  GA4 RUM: querying {days}-day rating distribution...", flush=True)
    r = client.run_report(RunReportRequest(
        property=prop,
        date_ranges=date_range,
        dimensions=[Dimension(name="eventName"), Dimension(name="customEvent:metric_rating")],
        metrics=[Metric(name="eventCount")],
        dimension_filter=_and(_in("eventName", VITAL_EVENTS)),
        limit=200,
    ))
    metrics = {m: {"good": 0, "needs-improvement": 0, "poor": 0} for m in VITAL_EVENTS}
    for row in r.rows:
        ev = row.dimension_values[0].value
        rating = row.dimension_values[1].value or "(no rating)"
        cnt = int(row.metric_values[0].value)
        if ev in metrics and rating in metrics[ev]:
            metrics[ev][rating] += cnt
    for m in metrics:
        total = sum(metrics[m].values())
        metrics[m]["total"] = total
        metrics[m]["p_good"] = (metrics[m]["good"] / total) if total else 0
        metrics[m]["p_poor"] = (metrics[m]["poor"] / total) if total else 0

    # Top pages by poor rate per metric
    print("  GA4 RUM: querying top friction pages per metric...", flush=True)
    top_pages = {}
    for metric_name in ("LCP", "INP", "CLS"):
        r = client.run_report(RunReportRequest(
            property=prop,
            date_ranges=date_range,
            dimensions=[Dimension(name="pagePath"), Dimension(name="customEvent:metric_rating")],
            metrics=[Metric(name="eventCount")],
            dimension_filter=_and(_eq("eventName", metric_name)),
            limit=2000,
        ))
        page_data = defaultdict(lambda: {"good": 0, "needs-improvement": 0, "poor": 0})
        for row in r.rows:
            page = row.dimension_values[0].value or "(not set)"
            rating = row.dimension_values[1].value or "(no rating)"
            cnt = int(row.metric_values[0].value)
            if rating in page_data[page]:
                page_data[page][rating] += cnt
        ranked = []
        for page, ratings in page_data.items():
            total = sum(ratings.values())
            if total < 50:  # filter low-volume pages
                continue
            poor = ratings["poor"]
            ranked.append({
                "page": page,
                "total": total,
                "poor": poor,
                "p_poor": poor / total if total else 0,
            })
        ranked.sort(key=lambda r: (-r["p_poor"], -r["total"]))
        top_pages[metric_name] = ranked[:5]

    # Top INP attribution targets
    print("  GA4 RUM: querying INP attribution targets...", flush=True)
    r = client.run_report(RunReportRequest(
        property=prop,
        date_ranges=date_range,
        dimensions=[Dimension(name="customEvent:debug_target"), Dimension(name="customEvent:metric_rating")],
        metrics=[Metric(name="eventCount")],
        dimension_filter=_and(_eq("eventName", "INP"), _eq("customEvent:metric_rating", "poor")),
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
        limit=10,
    ))
    inp_targets = [{
        "target": row.dimension_values[0].value or "(not set)",
        "count": int(row.metric_values[0].value),
    } for row in r.rows]

    # JS errors
    print("  GA4 RUM: querying JS errors...", flush=True)
    try:
        r = client.run_report(RunReportRequest(
            property=prop,
            date_ranges=date_range,
            dimensions=[
                Dimension(name="customEvent:error_type"),
                Dimension(name="customEvent:error_message"),
                Dimension(name="customEvent:error_source"),
            ],
            metrics=[Metric(name="eventCount")],
            dimension_filter=_and(_eq("eventName", "js_error")),
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
            limit=10,
        ))
        errors = [{
            "type": row.dimension_values[0].value or "?",
            "message": (row.dimension_values[1].value or "(no message)")[:140],
            "source": (row.dimension_values[2].value or "(unknown)")[:80],
            "count": int(row.metric_values[0].value),
        } for row in r.rows]
    except Exception as e:
        print(f"  GA4 RUM: JS error query failed (likely no js_error events yet): {e}", file=sys.stderr)
        errors = []

    return {
        "days": days,
        "metrics": metrics,
        "top_pages": top_pages,
        "top_inp_targets": inp_targets,
        "js_errors": errors,
    }


# ───────────────────────── Snapshot I/O ─────────────────────────

def append_snapshot(snapshot: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SNAPSHOTS_PATH, "a") as f:
        f.write(json.dumps(snapshot) + "\n")


def load_snapshots() -> list[dict]:
    if not SNAPSHOTS_PATH.exists():
        return []
    snapshots = []
    with open(SNAPSHOTS_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    snapshots.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return snapshots


# ───────────────────────── HTML render ─────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HairMNL — Performance Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {
    --navy: #1E2761;
    --navy-light: #3A4A8A;
    --ice: #CADCFC;
    --ice-bg: #F0F4FB;
    --gold: #D4A04C;
    --green: #2F8F3F;
    --amber: #C97A1A;
    --red: #C03A3A;
    --gray: #6B7280;
    --gray-light: #E5E7EB;
    --bg: #FAFBFC;
    --card: #FFFFFF;
    --text: #1F2937;
    --text-muted: #6B7280;
  }
  * { box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
         background: var(--bg); color: var(--text); margin: 0; padding: 0;
         font-size: 14px; line-height: 1.4; }
  .container { max-width: 1400px; margin: 0 auto; padding: 24px; }
  header { padding: 24px 0; border-bottom: 3px solid var(--navy); margin-bottom: 24px; }
  header h1 { margin: 0; font-size: 28px; color: var(--navy); }
  header .meta { color: var(--text-muted); font-size: 13px; margin-top: 6px; }
  h2 { color: var(--navy); font-size: 18px; margin: 32px 0 16px 0; padding-bottom: 8px;
       border-bottom: 1px solid var(--gray-light); }
  h3 { color: var(--navy-light); font-size: 14px; margin: 0 0 12px 0; text-transform: uppercase;
       letter-spacing: 0.05em; font-weight: 700; }

  .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
  .kpi { background: var(--card); border: 1px solid var(--gray-light); border-radius: 8px;
         padding: 18px; }
  .kpi .label { color: var(--text-muted); font-size: 11px; text-transform: uppercase;
                letter-spacing: 0.06em; font-weight: 700; }
  .kpi .value { font-size: 32px; font-weight: 700; color: var(--navy); margin-top: 6px;
                line-height: 1; }
  .kpi .delta { font-size: 12px; margin-top: 6px; color: var(--text-muted); }
  .kpi .delta.up { color: var(--green); }
  .kpi .delta.down { color: var(--red); }
  .kpi.poor .value { color: var(--red); }
  .kpi.warn .value { color: var(--amber); }
  .kpi.good .value { color: var(--green); }

  .card { background: var(--card); border: 1px solid var(--gray-light); border-radius: 8px;
          padding: 18px; margin-bottom: 16px; }

  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
  @media (max-width: 900px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } }

  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { text-align: left; color: var(--text-muted); font-weight: 600; font-size: 11px;
       text-transform: uppercase; letter-spacing: 0.04em; padding: 8px 10px;
       border-bottom: 2px solid var(--gray-light); }
  td { padding: 8px 10px; border-bottom: 1px solid var(--gray-light); }
  tr:last-child td { border-bottom: none; }
  td.num { text-align: right; font-variant-numeric: tabular-nums; }
  td.code { font-family: 'SF Mono', Monaco, Consolas, monospace; font-size: 12px;
            color: var(--navy); max-width: 360px; overflow: hidden; text-overflow: ellipsis;
            white-space: nowrap; }

  .bar { display: inline-block; height: 8px; background: var(--gray-light); border-radius: 4px;
         vertical-align: middle; position: relative; overflow: hidden; min-width: 80px; }
  .bar > span { display: block; height: 100%; }
  .bar.good > span { background: var(--green); }
  .bar.warn > span { background: var(--amber); }
  .bar.poor > span { background: var(--red); }

  .rating-stack { display: flex; height: 24px; border-radius: 4px; overflow: hidden;
                  background: var(--gray-light); margin: 4px 0; }
  .rating-stack > span { display: flex; align-items: center; justify-content: center;
                         color: white; font-size: 11px; font-weight: 600; min-width: 30px; }
  .rating-stack > .good { background: var(--green); }
  .rating-stack > .warn { background: var(--amber); }
  .rating-stack > .poor { background: var(--red); }

  .chart-wrap { position: relative; height: 200px; }
  .empty { color: var(--text-muted); font-style: italic; padding: 12px 0; }

  footer { color: var(--text-muted); font-size: 12px; text-align: center; padding: 32px 0;
           border-top: 1px solid var(--gray-light); margin-top: 48px; }
  footer a { color: var(--navy-light); }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>HairMNL — Performance Dashboard</h1>
    <div class="meta">
      Last updated: <strong>__LAST_UPDATED__</strong>
      &nbsp;·&nbsp; Snapshots collected: <strong>__SNAPSHOT_COUNT__</strong>
      &nbsp;·&nbsp; PSI source: hairmnl.com (mobile slow 4G + desktop)
      &nbsp;·&nbsp; RUM source: GA4 property 248106289, last __RUM_DAYS__ days
    </div>
  </header>

  <h2>Today&#39;s snapshot — PSI Lab (mobile)</h2>
  <div class="kpi-grid">
    __KPI_CARDS_MOBILE__
  </div>

  <h2>Today&#39;s snapshot — PSI Lab (desktop)</h2>
  <div class="kpi-grid">
    __KPI_CARDS_DESKTOP__
  </div>

  <h2>Trend over time — PSI Lab mobile</h2>
  <div class="grid-2">
    <div class="card"><h3>Performance score</h3><div class="chart-wrap"><canvas id="chart-score"></canvas></div></div>
    <div class="card"><h3>Largest Contentful Paint (s)</h3><div class="chart-wrap"><canvas id="chart-lcp"></canvas></div></div>
    <div class="card"><h3>Total Blocking Time (ms)</h3><div class="chart-wrap"><canvas id="chart-tbt"></canvas></div></div>
    <div class="card"><h3>Cumulative Layout Shift</h3><div class="chart-wrap"><canvas id="chart-cls"></canvas></div></div>
  </div>

  <h2>Real-shopper Core Web Vitals — last __RUM_DAYS__ days</h2>
  <div class="card">
    __RUM_RATINGS__
  </div>

  <h2>Top friction pages — by % &quot;poor&quot; rate</h2>
  <div class="grid-3">
    <div class="card"><h3>LCP — slow paint</h3>__TOP_PAGES_LCP__</div>
    <div class="card"><h3>INP — slow interaction</h3>__TOP_PAGES_INP__</div>
    <div class="card"><h3>CLS — layout shift</h3>__TOP_PAGES_CLS__</div>
  </div>

  <h2>Top INP attribution targets — what shoppers tap that&#39;s slow</h2>
  <div class="card">
    __INP_TARGETS__
  </div>

  <h2>JavaScript errors — last __RUM_DAYS__ days</h2>
  <div class="card">
    __JS_ERRORS__
  </div>

  <h2>vs April 26 baseline (mobile lab)</h2>
  <div class="card">
    __BASELINE_TABLE__
  </div>

  <footer>
    Generated by <code>scripts/build-perf-dashboard.py</code>
    &nbsp;·&nbsp; Data: PSI v5 API + GA4 Data API
    &nbsp;·&nbsp; Re-run: <code>./scripts/build-perf-dashboard.py</code>
    &nbsp;·&nbsp; <a href="https://pagespeed.web.dev/analysis?url=https%3A%2F%2Fwww.hairmnl.com">Open hairmnl.com in PSI</a>
  </footer>
</div>

<script>
const CHART_DATA = __CHART_DATA__;

const baseConfig = (label, color, dataset, fmt) => ({
  type: 'line',
  data: {
    labels: CHART_DATA.labels,
    datasets: [{
      label, data: dataset, borderColor: color, backgroundColor: color + '22',
      tension: 0.25, fill: true, pointRadius: 3, pointHoverRadius: 5, borderWidth: 2,
    }]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => fmt ? fmt(ctx.parsed.y) : ctx.parsed.y,
        }
      }
    },
    scales: {
      x: { grid: { display: false }, ticks: { font: { size: 11 } } },
      y: { beginAtZero: false, grid: { color: '#E5E7EB' }, ticks: { font: { size: 11 } } },
    }
  }
});

new Chart(document.getElementById('chart-score'),
  baseConfig('Score', '#1E2761', CHART_DATA.score, v => `${v}/100`));
new Chart(document.getElementById('chart-lcp'),
  baseConfig('LCP', '#C03A3A', CHART_DATA.lcp_s, v => `${v.toFixed(2)} s`));
new Chart(document.getElementById('chart-tbt'),
  baseConfig('TBT', '#C97A1A', CHART_DATA.tbt_ms, v => `${v} ms`));
new Chart(document.getElementById('chart-cls'),
  baseConfig('CLS', '#3A4A8A', CHART_DATA.cls, v => v.toFixed(3)));
</script>
</body>
</html>
"""


def _kpi(label, value, delta=None, klass=""):
    delta_html = ""
    if delta is not None:
        cls = "up" if delta < 0 else ("down" if delta > 0 else "")  # for LCP/TBT/CLS, negative = improvement
        sign = "+" if delta > 0 else ""
        delta_html = f'<div class="delta {cls}">{sign}{delta} vs prev</div>'
    return f'<div class="kpi {klass}"><div class="label">{label}</div><div class="value">{value}</div>{delta_html}</div>'


def _rate_class_lcp(ms):
    if ms is None: return ""
    if ms <= 2500: return "good"
    if ms <= 4000: return "warn"
    return "poor"


def _rate_class_tbt(ms):
    if ms is None: return ""
    if ms <= 200: return "good"
    if ms <= 600: return "warn"
    return "poor"


def _rate_class_cls(v):
    if v is None: return ""
    if v <= 0.1: return "good"
    if v <= 0.25: return "warn"
    return "poor"


def _rate_class_score(v):
    if v is None: return ""
    if v >= 90: return "good"
    if v >= 50: return "warn"
    return "poor"


def render_kpi_cards(psi_now, psi_prev, key_prefix):
    cards = []
    if not psi_now:
        return '<div class="empty">No PSI data captured yet — run with PSI enabled.</div>'

    delta = lambda k: (psi_now[k] - psi_prev[k]) if (psi_prev and k in psi_prev and k in psi_now) else None
    fmt_ms = lambda k: f"{psi_now[k]/1000:.1f}s" if psi_now.get(k) else "n/a"

    cards.append(_kpi("Score", psi_now["score"],
        delta=int(delta("score")) if delta("score") is not None else None,
        klass=_rate_class_score(psi_now["score"])))
    cards.append(_kpi("LCP", fmt_ms("lcp_ms"),
        delta=int(delta("lcp_ms")) if delta("lcp_ms") is not None else None,
        klass=_rate_class_lcp(psi_now["lcp_ms"])))
    cards.append(_kpi("TBT", f"{int(psi_now['tbt_ms'])} ms",
        delta=int(delta("tbt_ms")) if delta("tbt_ms") is not None else None,
        klass=_rate_class_tbt(psi_now["tbt_ms"])))
    cards.append(_kpi("CLS", f"{psi_now['cls']:.3f}",
        delta=round(delta("cls"), 3) if delta("cls") is not None else None,
        klass=_rate_class_cls(psi_now["cls"])))
    cards.append(_kpi("FCP", fmt_ms("fcp_ms"), klass=""))
    cards.append(_kpi("Speed Index", fmt_ms("si_ms"), klass=""))
    return "\n".join(cards)


def render_rum_ratings(metrics):
    if not metrics:
        return '<div class="empty">No RUM data.</div>'
    rows = []
    for m in VITAL_EVENTS:
        d = metrics.get(m, {})
        total = d.get("total", 0)
        if total == 0:
            rows.append(f'<div style="margin: 14px 0"><h3>{m}</h3><div class="empty">No events captured.</div></div>')
            continue
        g = d["good"]; ni = d["needs-improvement"]; p = d["poor"]
        gp = g/total*100; nip = ni/total*100; pp = p/total*100
        passes = gp >= 75
        passes_badge = '<span style="color:var(--green); font-weight:700;">✓ PASS</span>' if passes else \
                       '<span style="color:var(--amber); font-weight:700;">✗ FAIL</span>'
        rows.append(f'''
        <div style="margin: 16px 0;">
          <h3>{m} <span style="color:var(--text-muted); font-weight:400; text-transform:none; letter-spacing:0;">·
            {total:,} pageviews · {gp:.1f}% good · CWV target ≥75% good {passes_badge}</span></h3>
          <div class="rating-stack">
            <span class="good" style="flex: {gp};">{gp:.0f}%</span>
            <span class="warn" style="flex: {nip};">{nip:.0f}%</span>
            <span class="poor" style="flex: {pp};">{pp:.0f}%</span>
          </div>
        </div>''')
    return "\n".join(rows)


def render_top_pages(pages):
    if not pages:
        return '<div class="empty">No data.</div>'
    rows = ['<table><thead><tr><th>Page</th><th class="num">% poor</th><th class="num">N</th></tr></thead><tbody>']
    for p in pages:
        bar_w = min(100, p["p_poor"] * 100)
        rows.append(f'<tr><td class="code">{p["page"][:50]}</td>'
                    f'<td class="num"><span class="bar poor" style="width:60px"><span style="width:{bar_w:.0f}%"></span></span> '
                    f'{p["p_poor"]*100:.1f}%</td>'
                    f'<td class="num">{p["total"]:,}</td></tr>')
    rows.append('</tbody></table>')
    return "\n".join(rows)


def render_inp_targets(targets):
    if not targets:
        return '<div class="empty">No INP "poor" events with debug_target captured.</div>'
    rows = ['<table><thead><tr><th>Attribution target (CSS selector / element)</th><th class="num">Poor INP count</th></tr></thead><tbody>']
    for t in targets:
        target = t["target"]
        if target == "(not set)":
            target_html = '<span style="color:var(--text-muted)">(not set) — interaction during page load</span>'
        else:
            target_html = f'<span class="code">{target[:80]}</span>'
        rows.append(f'<tr><td>{target_html}</td><td class="num">{t["count"]:,}</td></tr>')
    rows.append('</tbody></table>')
    return "\n".join(rows)


def render_js_errors(errors):
    if not errors:
        return '<div class="empty">No js_error events captured. Either no errors (good!) or the js_error tracking isn&#39;t live yet.</div>'
    rows = ['<table><thead><tr><th>Type</th><th>Message</th><th>Source</th><th class="num">Count</th></tr></thead><tbody>']
    for e in errors:
        rows.append(f'<tr><td>{e["type"]}</td><td class="code">{e["message"]}</td>'
                    f'<td class="code">{e["source"]}</td><td class="num">{e["count"]:,}</td></tr>')
    rows.append('</tbody></table>')
    return "\n".join(rows)


def render_baseline_table(psi_now):
    if not psi_now:
        return '<div class="empty">No PSI data to compare.</div>'
    base = BASELINE_2026_04_26
    def diff_pct(now, then):
        if then == 0: return "n/a"
        d = (now - then) / then * 100
        sign = "+" if d > 0 else ""
        return f'{sign}{d:.0f}%'
    rows = [
        ('Score',  base["score"],  psi_now["score"],  False),
        ('LCP (s)', base["lcp_ms"]/1000, psi_now["lcp_ms"]/1000, True),
        ('TBT (ms)', base["tbt_ms"], psi_now["tbt_ms"], True),
        ('CLS', base["cls"], psi_now["cls"], True),
        ('FCP (s)', base["fcp_ms"]/1000, psi_now["fcp_ms"]/1000, True),
        ('Speed Index (s)', base["si_ms"]/1000, psi_now["si_ms"]/1000, True),
    ]
    out = ['<table><thead><tr><th>Metric</th><th class="num">Apr 26 baseline</th>'
           '<th class="num">Now</th><th class="num">Δ</th><th>Direction</th></tr></thead><tbody>']
    for label, then, now, lower_is_better in rows:
        d = now - then
        d_pct = diff_pct(now, then)
        if isinstance(then, float):
            then_s = f"{then:.3f}" if then < 10 else f"{then:.1f}"
            now_s = f"{now:.3f}" if now < 10 else f"{now:.1f}"
        else:
            then_s = f"{int(then)}"
            now_s = f"{int(now)}"
        improved = (d < 0) if lower_is_better else (d > 0)
        arrow = '↓' if d < 0 else ('↑' if d > 0 else '→')
        color = 'var(--green)' if improved else ('var(--red)' if (d != 0) else 'var(--text-muted)')
        verdict = 'better' if improved else ('worse' if d != 0 else 'flat')
        out.append(f'<tr><td><strong>{label}</strong></td><td class="num">{then_s}</td>'
                   f'<td class="num">{now_s}</td>'
                   f'<td class="num" style="color:{color}; font-weight:600">{arrow} {d_pct}</td>'
                   f'<td style="color:{color};">{verdict}</td></tr>')
    out.append('</tbody></table>')
    return "\n".join(out)


def build_chart_data(snapshots, max_points=30):
    """Build trend data from snapshots. Use mobile PSI; only keep snapshots with PSI data."""
    pts = []
    for s in snapshots:
        psi = s.get("psi", {}).get("mobile")
        if not psi:
            continue
        ts = s["timestamp"]
        # short label (MM-DD)
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            label = dt.strftime("%b %d")
        except Exception:
            label = ts[:10]
        pts.append({
            "label": label,
            "score": psi["score"],
            "lcp_s": psi["lcp_ms"] / 1000,
            "tbt_ms": psi["tbt_ms"],
            "cls": psi["cls"],
        })
    pts = pts[-max_points:]
    return {
        "labels": [p["label"] for p in pts],
        "score": [p["score"] for p in pts],
        "lcp_s": [p["lcp_s"] for p in pts],
        "tbt_ms": [p["tbt_ms"] for p in pts],
        "cls": [p["cls"] for p in pts],
    }


def render_html(snapshots: list[dict]) -> str:
    if not snapshots:
        return "<html><body><h1>No snapshots yet — run the script first.</h1></body></html>"

    latest = snapshots[-1]
    prev = snapshots[-2] if len(snapshots) >= 2 else None

    psi_mobile = latest.get("psi", {}).get("mobile")
    psi_desktop = latest.get("psi", {}).get("desktop")
    psi_mobile_prev = prev.get("psi", {}).get("mobile") if prev else None
    psi_desktop_prev = prev.get("psi", {}).get("desktop") if prev else None
    rum = latest.get("ga4") or {}

    chart_data = build_chart_data(snapshots)

    last_dt = latest["timestamp"]
    try:
        last_label = datetime.fromisoformat(last_dt.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        last_label = last_dt

    html = HTML_TEMPLATE
    html = html.replace("__LAST_UPDATED__", last_label)
    html = html.replace("__SNAPSHOT_COUNT__", str(len(snapshots)))
    html = html.replace("__RUM_DAYS__", str(rum.get("days", 7)))
    html = html.replace("__KPI_CARDS_MOBILE__", render_kpi_cards(psi_mobile, psi_mobile_prev, "mobile"))
    html = html.replace("__KPI_CARDS_DESKTOP__", render_kpi_cards(psi_desktop, psi_desktop_prev, "desktop"))
    html = html.replace("__RUM_RATINGS__", render_rum_ratings(rum.get("metrics", {})))
    html = html.replace("__TOP_PAGES_LCP__", render_top_pages(rum.get("top_pages", {}).get("LCP", [])))
    html = html.replace("__TOP_PAGES_INP__", render_top_pages(rum.get("top_pages", {}).get("INP", [])))
    html = html.replace("__TOP_PAGES_CLS__", render_top_pages(rum.get("top_pages", {}).get("CLS", [])))
    html = html.replace("__INP_TARGETS__", render_inp_targets(rum.get("top_inp_targets", [])))
    html = html.replace("__JS_ERRORS__", render_js_errors(rum.get("js_errors", [])))
    html = html.replace("__BASELINE_TABLE__", render_baseline_table(psi_mobile))
    html = html.replace("__CHART_DATA__", json.dumps(chart_data))
    return html


# ───────────────────────── Main ─────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-psi", action="store_true", help="skip PSI lab fetch")
    ap.add_argument("--no-ga4", action="store_true", help="skip GA4 RUM fetch")
    ap.add_argument("--psi-only-mobile", action="store_true", help="skip desktop PSI")
    ap.add_argument("--render-only", action="store_true", help="don't fetch new data, re-render from existing snapshots")
    ap.add_argument("--url", default=DEFAULT_URL, help=f"PSI URL (default: {DEFAULT_URL})")
    ap.add_argument("--psi-runs", type=int, default=3, help="PSI runs per strategy for median (default: 3)")
    ap.add_argument("--ga4-days", type=int, default=7, help="GA4 RUM lookback window (default: 7)")
    args = ap.parse_args()

    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if args.render_only:
        print("--render-only: re-rendering HTML from existing snapshots, no fetch")
        snapshots = load_snapshots()
        html = render_html(snapshots)
        HTML_OUT_PATH.write_text(html)
        print(f"Wrote {HTML_OUT_PATH} ({len(html):,} bytes, {len(snapshots)} snapshots)")
        return

    print(f"Building HairMNL perf dashboard snapshot at {datetime.now(timezone.utc).isoformat()}")
    print(f"  Output: {HTML_OUT_PATH}")
    print(f"  History: {SNAPSHOTS_PATH}")

    snapshot = {"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")}

    if not args.no_psi:
        snapshot["psi"] = {}
        t0 = time.time()
        m = run_psi_median(args.url, "mobile", args.psi_runs)
        if m: snapshot["psi"]["mobile"] = m
        if not args.psi_only_mobile:
            d = run_psi_median(args.url, "desktop", args.psi_runs)
            if d: snapshot["psi"]["desktop"] = d
        print(f"  PSI total: {time.time()-t0:.1f}s")

    if not args.no_ga4:
        t0 = time.time()
        try:
            snapshot["ga4"] = query_ga4_rum(days=args.ga4_days)
            print(f"  GA4 total: {time.time()-t0:.1f}s")
        except Exception as e:
            print(f"  GA4 fetch failed: {e}", file=sys.stderr)

    has_psi = bool(snapshot.get("psi", {}).get("mobile") or snapshot.get("psi", {}).get("desktop"))
    has_ga4 = bool(snapshot.get("ga4"))
    if has_psi or has_ga4:
        append_snapshot(snapshot)
        print(f"  Snapshot appended to {SNAPSHOTS_PATH}")
    else:
        print(f"  Skipping empty snapshot (no PSI mobile/desktop, no GA4)", file=sys.stderr)

    snapshots = load_snapshots()
    html = render_html(snapshots)
    HTML_OUT_PATH.write_text(html)
    print(f"  Wrote {HTML_OUT_PATH} ({len(html):,} bytes, {len(snapshots)} snapshots in history)")
    print(f"\nOpen with: open {HTML_OUT_PATH}")


if __name__ == "__main__":
    main()
