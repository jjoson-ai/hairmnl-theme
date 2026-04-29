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


# ───────────────────────── CrUX ─────────────────────────

def query_crux(url: str, form_factor: str, key: str) -> dict | None:
    """
    Query Chrome UX Report API for real-shopper p75 values + rating distribution.
    form_factor: 'PHONE' | 'DESKTOP' | 'TABLET' | 'ALL_FORM_FACTORS'

    Returns None on 403 (API key restriction) or 404 (insufficient CrUX data).
    Returns dict like:
      {"lcp_ms": 3812, "cls": 0.30, "inp_ms": 277, "fcp_ms": 3140, "ttfb_ms": 737,
       "histograms": {"lcp": {...}, ...}}
    """
    api = f"https://chromeuxreport.googleapis.com/v1/records:queryRecord?key={key}"
    payload = json.dumps({
        "url": url,
        "formFactor": form_factor,
        "metrics": [
            "largest_contentful_paint", "cumulative_layout_shift",
            "interaction_to_next_paint", "first_contentful_paint",
            "experimental_time_to_first_byte",
        ],
    }).encode()
    req = urllib.request.Request(api, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"  CrUX {form_factor} 403 — PSI API key has API-restrictions allowlist that blocks CrUX. "
                  f"Fix: GCP Console → Credentials → click key → 'API restrictions' → "
                  f"add 'Chrome UX Report API' OR set 'Don't restrict key'.", file=sys.stderr)
        elif e.code == 404:
            print(f"  CrUX {form_factor} 404 — insufficient real-shopper data (need ~28 days of Chrome traffic).", file=sys.stderr)
        else:
            print(f"  CrUX {form_factor} HTTP {e.code}: {e.read()[:200].decode(errors='replace')}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  CrUX {form_factor} error: {e}", file=sys.stderr)
        return None

    metrics = d.get("record", {}).get("metrics", {})
    out = {"collection_period": d.get("record", {}).get("collectionPeriod", {}), "histograms": {}}

    def _extract(name, key_out, multiplier=1):
        m = metrics.get(name)
        if not m:
            return None
        p75 = m.get("percentiles", {}).get("p75")
        if p75 is not None:
            try:
                out[key_out] = float(p75) * multiplier
            except (ValueError, TypeError):
                pass
        # Capture histogram (rating buckets) for charting
        if "histogram" in m:
            buckets = []
            for b in m["histogram"]:
                buckets.append({
                    "start": b.get("start"),
                    "end": b.get("end"),
                    "density": b.get("density", 0),
                })
            out["histograms"][key_out] = buckets

    _extract("largest_contentful_paint", "lcp_ms")
    # CrUX HTTP API returns CLS p75 as a decimal string ("0.30"), NOT scaled.
    # The BigQuery dataset uses int×100; the HTTP API uses real decimals.
    _extract("cumulative_layout_shift", "cls")
    _extract("interaction_to_next_paint", "inp_ms")
    _extract("first_contentful_paint", "fcp_ms")
    _extract("experimental_time_to_first_byte", "ttfb_ms")
    return out


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
    # 180s timeout: PSI on a slow site (LCP 14s+) can legitimately take >120s
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
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
    --navy-2: #2C3A7A;
    --navy-light: #3A4A8A;
    --ice: #CADCFC;
    --ice-bg: #F0F4FB;
    --gold: #D4A04C;
    --green: #2F8F3F;
    --green-bg: #E8F5EA;
    --amber: #C97A1A;
    --amber-bg: #FBF1E0;
    --red: #C03A3A;
    --red-bg: #FBE8E8;
    --gray: #6B7280;
    --gray-light: #E5E7EB;
    --gray-bg: #F4F6F8;
    --bg: #F7F8FA;
    --card: #FFFFFF;
    --text: #1F2937;
    --text-muted: #6B7280;
  }
  * { box-sizing: border-box; }
  html { -webkit-text-size-adjust: 100%; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
         background: var(--bg); color: var(--text); margin: 0; padding: 0;
         font-size: 14px; line-height: 1.45; }
  .container { max-width: 1400px; margin: 0 auto; padding: 16px; }
  @media (min-width: 700px) { .container { padding: 24px; } }

  header { padding: 16px 0 20px; border-bottom: 3px solid var(--navy); margin-bottom: 20px; }
  header .row { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px;
                flex-wrap: wrap; }
  header h1 { margin: 0; font-size: 22px; color: var(--navy); line-height: 1.2; }
  @media (min-width: 700px) { header h1 { font-size: 28px; } }
  header .meta { color: var(--text-muted); font-size: 12px; margin-top: 6px; line-height: 1.5; }
  header .meta strong { color: var(--text); }
  .live-link { background: var(--navy); color: white; text-decoration: none; padding: 6px 12px;
               border-radius: 6px; font-size: 12px; font-weight: 600; white-space: nowrap; }
  .live-link:hover { background: var(--navy-2); }

  h2 { color: var(--navy); font-size: 16px; margin: 28px 0 12px 0; padding-bottom: 8px;
       border-bottom: 1px solid var(--gray-light); display: flex; align-items: center;
       justify-content: space-between; flex-wrap: wrap; gap: 8px; }
  @media (min-width: 700px) { h2 { font-size: 18px; } }
  h2 .h2-help { font-weight: 400; font-size: 11px; color: var(--text-muted);
                text-transform: none; letter-spacing: 0; }
  h3 { color: var(--navy-light); font-size: 13px; margin: 0 0 10px 0; text-transform: uppercase;
       letter-spacing: 0.05em; font-weight: 700; }

  /* Tab switcher */
  .tabs { display: inline-flex; background: var(--gray-bg); border-radius: 8px; padding: 4px;
          gap: 0; margin-bottom: 14px; }
  .tab { background: transparent; border: 0; padding: 6px 14px; border-radius: 6px;
         font-size: 13px; font-weight: 600; color: var(--text-muted); cursor: pointer;
         font-family: inherit; }
  .tab.active { background: var(--card); color: var(--navy); box-shadow: 0 1px 2px rgba(0,0,0,0.06); }
  .tab:hover:not(.active) { color: var(--navy-light); }
  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* KPI cards */
  .kpi-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
  @media (min-width: 700px) { .kpi-grid { grid-template-columns: repeat(3, 1fr); gap: 14px; } }
  @media (min-width: 1100px) { .kpi-grid { grid-template-columns: repeat(6, 1fr); } }
  .kpi { background: var(--card); border: 1px solid var(--gray-light); border-radius: 8px;
         padding: 14px; }
  .kpi .label { color: var(--text-muted); font-size: 10px; text-transform: uppercase;
                letter-spacing: 0.05em; font-weight: 700; }
  .kpi .value { font-size: 26px; font-weight: 700; color: var(--navy); margin-top: 4px;
                line-height: 1; }
  @media (min-width: 700px) { .kpi .value { font-size: 28px; } }
  .kpi .delta { font-size: 11px; margin-top: 4px; color: var(--text-muted); }
  .kpi .delta.improve { color: var(--green); font-weight: 600; }
  .kpi .delta.regress { color: var(--red); font-weight: 600; }
  .kpi.poor { background: var(--red-bg); border-color: #F0C8C8; }
  .kpi.poor .value { color: var(--red); }
  .kpi.warn { background: var(--amber-bg); border-color: #ECD9B6; }
  .kpi.warn .value { color: var(--amber); }
  .kpi.good { background: var(--green-bg); border-color: #C6E2CC; }
  .kpi.good .value { color: var(--green); }

  .card { background: var(--card); border: 1px solid var(--gray-light); border-radius: 8px;
          padding: 16px; margin-bottom: 14px; }

  .grid-2 { display: grid; grid-template-columns: 1fr; gap: 12px; }
  .grid-3 { display: grid; grid-template-columns: 1fr; gap: 12px; }
  @media (min-width: 800px) { .grid-2 { grid-template-columns: 1fr 1fr; } }
  @media (min-width: 1100px) { .grid-3 { grid-template-columns: 1fr 1fr 1fr; } }

  /* RUM CWV cards */
  .cwv-grid { display: grid; grid-template-columns: 1fr; gap: 10px; }
  @media (min-width: 700px) { .cwv-grid { grid-template-columns: repeat(2, 1fr); } }
  @media (min-width: 1100px) { .cwv-grid { grid-template-columns: repeat(5, 1fr); } }
  .cwv { background: var(--card); border: 1px solid var(--gray-light); border-radius: 8px;
         padding: 14px; }
  .cwv .name { font-size: 12px; color: var(--text-muted); text-transform: uppercase;
               font-weight: 700; letter-spacing: 0.05em; }
  .cwv .pct { font-size: 32px; font-weight: 700; color: var(--green); line-height: 1; margin: 4px 0; }
  .cwv.fail .pct { color: var(--amber); }
  .cwv .total { font-size: 11px; color: var(--text-muted); margin-bottom: 8px; }
  .cwv .badge { display: inline-block; padding: 2px 8px; border-radius: 4px;
                font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }
  .cwv .badge.pass { background: var(--green-bg); color: var(--green); }
  .cwv .badge.fail { background: var(--amber-bg); color: var(--amber); }
  .rating-stack { display: flex; height: 8px; border-radius: 4px; overflow: hidden;
                  background: var(--gray-light); margin: 6px 0 4px 0; }
  .rating-stack > span { display: block; height: 100%; }
  .rating-stack > .good { background: var(--green); }
  .rating-stack > .warn { background: var(--amber); }
  .rating-stack > .poor { background: var(--red); }
  .stack-legend { font-size: 10px; color: var(--text-muted); margin-top: 4px; line-height: 1.4; }

  /* Page friction rows — readable, not truncated */
  .page-row { padding: 10px 0; border-bottom: 1px solid var(--gray-light); }
  .page-row:last-child { border-bottom: none; }
  .page-row .path { font-family: 'SF Mono', Monaco, Consolas, monospace; font-size: 12px;
                    color: var(--navy); word-break: break-all; line-height: 1.3; display: block;
                    margin-bottom: 6px; text-decoration: none; }
  .page-row .path:hover { text-decoration: underline; }
  .page-row .stats { display: flex; align-items: center; gap: 12px; font-size: 12px;
                     flex-wrap: wrap; }
  .page-row .pct-poor { font-weight: 700; min-width: 56px; }
  .page-row .pct-poor.poor-high { color: var(--red); }
  .page-row .pct-poor.poor-mid { color: var(--amber); }
  .page-row .pct-poor.poor-low { color: var(--text-muted); }
  .page-row .meta { color: var(--text-muted); font-size: 11px; }
  .page-row .deeplinks { display: flex; gap: 8px; margin-left: auto; }
  .page-row .deeplinks a { color: var(--navy-light); text-decoration: none; font-size: 11px;
                            font-weight: 600; padding: 2px 6px; background: var(--ice-bg);
                            border-radius: 4px; }
  .page-row .deeplinks a:hover { background: var(--ice); }

  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { text-align: left; color: var(--text-muted); font-weight: 600; font-size: 11px;
       text-transform: uppercase; letter-spacing: 0.04em; padding: 8px 10px;
       border-bottom: 2px solid var(--gray-light); }
  td { padding: 8px 10px; border-bottom: 1px solid var(--gray-light); vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  td.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
  td.code { font-family: 'SF Mono', Monaco, Consolas, monospace; font-size: 12px;
            color: var(--navy); word-break: break-all; }

  .chart-wrap { position: relative; height: 200px; }
  .empty { color: var(--text-muted); font-style: italic; padding: 12px 0; font-size: 13px; }
  .note { background: var(--ice-bg); border-left: 3px solid var(--navy-light);
          padding: 10px 14px; border-radius: 4px; font-size: 12px; color: var(--text);
          margin-bottom: 12px; }
  .note strong { color: var(--navy); }

  /* Trend chart range filter */
  .range-filter { display: inline-flex; gap: 4px; }
  .range-btn { background: var(--gray-bg); border: 0; padding: 4px 10px; border-radius: 4px;
               font-size: 11px; font-weight: 600; color: var(--text-muted); cursor: pointer;
               font-family: inherit; }
  .range-btn.active { background: var(--navy); color: white; }
  .range-btn:hover:not(.active) { background: var(--gray-light); }

  /* Collapsible source detail */
  details { margin-top: 8px; }
  summary { cursor: pointer; font-size: 11px; color: var(--text-muted); }

  footer { color: var(--text-muted); font-size: 12px; text-align: center; padding: 24px 0;
           border-top: 1px solid var(--gray-light); margin-top: 32px; line-height: 1.6; }
  footer a { color: var(--navy-light); text-decoration: none; }
  footer a:hover { text-decoration: underline; }
</style>
</head>
<body>
<div class="container">
  <header>
    <div class="row">
      <div>
        <h1>HairMNL — Performance Dashboard</h1>
        <div class="meta">
          Last updated: <strong>__LAST_UPDATED__</strong>
          &nbsp;·&nbsp; Snapshots: <strong>__SNAPSHOT_COUNT__</strong>
          &nbsp;·&nbsp; RUM window: <strong>last __RUM_DAYS__ days</strong>
        </div>
      </div>
      <a class="live-link" href="https://pagespeed.web.dev/analysis?url=https%3A%2F%2Fwww.hairmnl.com" target="_blank" rel="noopener">Open in PSI ↗</a>
    </div>
  </header>

  <h2>Today&#39;s snapshot
    <span class="h2-help">CrUX = real-shopper p75 (28-day) · PSI = single-run lab simulation</span>
  </h2>
  <div class="tabs" role="tablist">
    <button class="tab active" data-tab="snapshot-mobile" onclick="switchTab(this)">📱 Mobile</button>
    <button class="tab" data-tab="snapshot-desktop" onclick="switchTab(this)">🖥 Desktop</button>
  </div>
  <div class="tab-content active" id="snapshot-mobile">
    __SNAPSHOT_MOBILE__
  </div>
  <div class="tab-content" id="snapshot-desktop">
    __SNAPSHOT_DESKTOP__
  </div>

  <h2>Trend over time — PSI Lab mobile
    <span class="range-filter">
      <button class="range-btn" data-range="7" onclick="setRange(7)">7d</button>
      <button class="range-btn" data-range="30" onclick="setRange(30)">30d</button>
      <button class="range-btn" data-range="90" onclick="setRange(90)">90d</button>
      <button class="range-btn active" data-range="0" onclick="setRange(0)">All</button>
    </span>
  </h2>
  <div class="grid-2">
    <div class="card"><h3>Performance score</h3><div class="chart-wrap"><canvas id="chart-score"></canvas></div></div>
    <div class="card"><h3>Largest Contentful Paint (s)</h3><div class="chart-wrap"><canvas id="chart-lcp"></canvas></div></div>
    <div class="card"><h3>Total Blocking Time (ms)</h3><div class="chart-wrap"><canvas id="chart-tbt"></canvas></div></div>
    <div class="card"><h3>Cumulative Layout Shift</h3><div class="chart-wrap"><canvas id="chart-cls"></canvas></div></div>
  </div>

  <h2>Real-shopper Core Web Vitals
    <span class="h2-help">GA4 last __RUM_DAYS__ days · ≥75% good = PASS the CWV threshold</span>
  </h2>
  <div class="cwv-grid">
    __RUM_RATINGS__
  </div>

  <h2>Top friction pages
    <span class="h2-help">≥50 pageviews · click any path to open in PSI</span>
  </h2>
  <div class="grid-3">
    <div class="card"><h3>LCP — slow paint</h3>__TOP_PAGES_LCP__</div>
    <div class="card"><h3>INP — slow interaction</h3>__TOP_PAGES_INP__</div>
    <div class="card"><h3>CLS — layout shift</h3>__TOP_PAGES_CLS__</div>
  </div>

  <h2>Top INP attribution targets
    <span class="h2-help">CSS selectors / elements causing slow taps</span>
  </h2>
  <div class="card">
    __INP_TARGETS__
  </div>

  <h2>JavaScript errors
    <span class="h2-help">last __RUM_DAYS__ days</span>
  </h2>
  <div class="card">
    __JS_ERRORS__
  </div>

  <h2>vs April 26 baseline
    <span class="h2-help">PSI mobile lab · cumulative project impact</span>
  </h2>
  <div class="card">
    __BASELINE_TABLE__
  </div>

  <footer>
    Data sources: PSI v5 API · CrUX HTTP API · GA4 Data API (property 248106289)<br>
    Refresh: <code>./scripts/build-perf-dashboard.py</code>
    &nbsp;·&nbsp; <a href="https://github.com/jjoson-ai/hairmnl-theme/tree/main/dashboard">Source on GitHub</a>
  </footer>
</div>

<script>
const CHART_DATA = __CHART_DATA__;
let activeRange = 0;  // 0 = all
let charts = {};

function filterByRange(allLabels, allData, days) {
  if (days === 0) return { labels: allLabels, data: allData };
  const n = allLabels.length;
  const sliceStart = Math.max(0, n - days);
  return { labels: allLabels.slice(sliceStart), data: allData.slice(sliceStart) };
}

const baseConfig = (label, color, allData, fmt) => {
  const filtered = filterByRange(CHART_DATA.labels, allData, activeRange);
  return {
    type: 'line',
    data: {
      labels: filtered.labels,
      datasets: [{
        label, data: filtered.data, borderColor: color, backgroundColor: color + '22',
        tension: 0.25, fill: true, pointRadius: 3, pointHoverRadius: 5, borderWidth: 2,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (ctx) => fmt ? fmt(ctx.parsed.y) : ctx.parsed.y } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 10 } } },
        y: { beginAtZero: false, grid: { color: '#E5E7EB' }, ticks: { font: { size: 10 } } },
      }
    }
  };
};

function buildCharts() {
  Object.values(charts).forEach(c => c.destroy());
  charts.score = new Chart(document.getElementById('chart-score'),
    baseConfig('Score', '#1E2761', CHART_DATA.score, v => `${v}/100`));
  charts.lcp = new Chart(document.getElementById('chart-lcp'),
    baseConfig('LCP', '#C03A3A', CHART_DATA.lcp_s, v => `${v.toFixed(2)} s`));
  charts.tbt = new Chart(document.getElementById('chart-tbt'),
    baseConfig('TBT', '#C97A1A', CHART_DATA.tbt_ms, v => `${v} ms`));
  charts.cls = new Chart(document.getElementById('chart-cls'),
    baseConfig('CLS', '#3A4A8A', CHART_DATA.cls, v => v.toFixed(3)));
}

function setRange(days) {
  activeRange = days;
  document.querySelectorAll('.range-btn').forEach(b =>
    b.classList.toggle('active', parseInt(b.dataset.range, 10) === days));
  buildCharts();
}

function switchTab(btn) {
  const target = btn.dataset.tab;
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t === btn));
  document.querySelectorAll('.tab-content').forEach(tc => tc.classList.toggle('active', tc.id === target));
}

buildCharts();
</script>
</body>
</html>
"""


def _kpi_v2(label, value, source, klass="", delta_html=""):
    """Single KPI card. Source = 'CrUX p75', 'PSI lab', or empty."""
    src = f'<div style="font-size:9px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;margin-top:4px;">{source}</div>' if source else ""
    return (f'<div class="kpi {klass}"><div class="label">{label}</div>'
            f'<div class="value">{value}</div>{delta_html}{src}</div>')


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


def _rate_class_inp(ms):
    if ms is None: return ""
    if ms <= 200: return "good"
    if ms <= 500: return "warn"
    return "poor"


def _rate_class_fcp(ms):
    if ms is None: return ""
    if ms <= 1800: return "good"
    if ms <= 3000: return "warn"
    return "poor"


def _rate_class_ttfb(ms):
    if ms is None: return ""
    if ms <= 800: return "good"
    if ms <= 1800: return "warn"
    return "poor"


def _rate_class_score(v):
    if v is None: return ""
    if v >= 90: return "good"
    if v >= 50: return "warn"
    return "poor"


def _delta_html(curr, prev, lower_is_better=True, fmt=lambda v: f"{v:+.0f}"):
    if prev is None or curr is None:
        return ""
    d = curr - prev
    if d == 0:
        return f'<div class="delta">no change vs prev</div>'
    improved = (d < 0) if lower_is_better else (d > 0)
    klass = "improve" if improved else "regress"
    arrow = "↓" if d < 0 else "↑"
    return f'<div class="delta {klass}">{arrow} {fmt(abs(d))} vs prev</div>'


def render_snapshot_section(form_factor: str, snapshot: dict, prev_snapshot: dict | None) -> str:
    """Render KPI cards for one form factor (mobile|desktop). Combines CrUX + PSI."""
    crux = snapshot.get("crux", {}).get(form_factor)
    psi = snapshot.get("psi", {}).get(form_factor)
    crux_prev = prev_snapshot.get("crux", {}).get(form_factor) if prev_snapshot else None
    psi_prev = prev_snapshot.get("psi", {}).get(form_factor) if prev_snapshot else None

    if not crux and not psi:
        return ('<div class="empty">No data captured for this form factor yet. '
                'CrUX needs ~28 days of Chrome traffic; PSI mobile sometimes fails for slow sites '
                '(<a href="https://chromeuxreport.googleapis.com" target="_blank">enable CrUX API</a> for the most reliable signal).</div>')

    cards = []

    # SCORE — PSI only (CrUX has no aggregate score)
    if psi and "score" in psi:
        cards.append(_kpi_v2("Score", str(psi["score"]), "PSI lab",
            klass=_rate_class_score(psi["score"]),
            delta_html=_delta_html(psi["score"], (psi_prev or {}).get("score"), lower_is_better=False)))

    # LCP — prefer CrUX
    lcp = crux.get("lcp_ms") if crux else None
    lcp_src = "CrUX p75" if lcp else None
    if not lcp and psi: lcp = psi.get("lcp_ms"); lcp_src = "PSI lab"
    if lcp:
        prev = (crux_prev or {}).get("lcp_ms") if crux else (psi_prev or {}).get("lcp_ms")
        cards.append(_kpi_v2("LCP", f"{lcp/1000:.2f} s", lcp_src,
            klass=_rate_class_lcp(lcp),
            delta_html=_delta_html(lcp, prev, fmt=lambda v: f"{v/1000:.2f}s")))

    # CLS — prefer CrUX
    cls = crux.get("cls") if crux else None
    cls_src = "CrUX p75" if cls is not None else None
    if cls is None and psi: cls = psi.get("cls"); cls_src = "PSI lab"
    if cls is not None:
        prev = (crux_prev or {}).get("cls") if crux else (psi_prev or {}).get("cls")
        cards.append(_kpi_v2("CLS", f"{cls:.3f}", cls_src,
            klass=_rate_class_cls(cls),
            delta_html=_delta_html(cls, prev, fmt=lambda v: f"{v:.3f}")))

    # INP — CrUX only (PSI lab doesn't measure INP)
    if crux and crux.get("inp_ms") is not None:
        inp = crux["inp_ms"]
        prev = (crux_prev or {}).get("inp_ms")
        cards.append(_kpi_v2("INP", f"{inp:.0f} ms", "CrUX p75",
            klass=_rate_class_inp(inp),
            delta_html=_delta_html(inp, prev, fmt=lambda v: f"{v:.0f}ms")))

    # TBT — PSI only (CrUX has no TBT)
    if psi and "tbt_ms" in psi:
        tbt = psi["tbt_ms"]
        prev = (psi_prev or {}).get("tbt_ms")
        cards.append(_kpi_v2("TBT", f"{tbt:.0f} ms", "PSI lab",
            klass=_rate_class_tbt(tbt),
            delta_html=_delta_html(tbt, prev, fmt=lambda v: f"{v:.0f}ms")))

    # FCP — prefer CrUX
    fcp = crux.get("fcp_ms") if crux else None
    fcp_src = "CrUX p75" if fcp else None
    if not fcp and psi: fcp = psi.get("fcp_ms"); fcp_src = "PSI lab"
    if fcp:
        prev = (crux_prev or {}).get("fcp_ms") if crux else (psi_prev or {}).get("fcp_ms")
        cards.append(_kpi_v2("FCP", f"{fcp/1000:.2f} s", fcp_src,
            klass=_rate_class_fcp(fcp),
            delta_html=_delta_html(fcp, prev, fmt=lambda v: f"{v/1000:.2f}s")))

    # TTFB — CrUX only
    if crux and crux.get("ttfb_ms"):
        ttfb = crux["ttfb_ms"]
        prev = (crux_prev or {}).get("ttfb_ms")
        cards.append(_kpi_v2("TTFB", f"{ttfb:.0f} ms", "CrUX p75",
            klass=_rate_class_ttfb(ttfb),
            delta_html=_delta_html(ttfb, prev, fmt=lambda v: f"{v:.0f}ms")))

    return f'<div class="kpi-grid">{"".join(cards)}</div>'


def render_rum_cwv_cards(metrics):
    """5 compact cards in a row, one per CWV metric."""
    if not metrics:
        return '<div class="empty">No RUM data.</div>'
    cards = []
    for m in VITAL_EVENTS:
        d = metrics.get(m, {})
        total = d.get("total", 0)
        if total == 0:
            cards.append(f'<div class="cwv"><div class="name">{m}</div><div class="empty">No events</div></div>')
            continue
        g = d["good"]; ni = d["needs-improvement"]; p = d["poor"]
        gp = g/total*100; nip = ni/total*100; pp = p/total*100
        passes = gp >= 75
        badge = '<span class="badge pass">✓ PASS</span>' if passes else '<span class="badge fail">✗ FAIL</span>'
        klass = "" if passes else "fail"
        cards.append(f'''
        <div class="cwv {klass}">
          <div class="name">{m}</div>
          <div class="pct">{gp:.0f}%</div>
          <div class="total">good · {total:,} events {badge}</div>
          <div class="rating-stack">
            <span class="good" style="flex: {gp};"></span>
            <span class="warn" style="flex: {nip};"></span>
            <span class="poor" style="flex: {pp};"></span>
          </div>
          <div class="stack-legend">{gp:.0f}% good · {nip:.0f}% NI · {pp:.0f}% poor</div>
        </div>''')
    return "\n".join(cards)


def render_top_pages(pages, metric_name):
    """Page rows with full URLs (no truncation), deep-links to PSI + GA4."""
    if not pages:
        return '<div class="empty">No pages with ≥50 events.</div>'
    rows = []
    for p in pages:
        path = p["page"]
        # Build absolute URL for deep-links
        full_url = f"https://www.hairmnl.com{path}" if path.startswith("/") else path
        psi_link = f"https://pagespeed.web.dev/analysis?url={urllib.parse.quote(full_url, safe='')}"
        # Color-coded poor%
        pct_poor = p["p_poor"] * 100
        if pct_poor >= 25: pct_class = "poor-high"
        elif pct_poor >= 10: pct_class = "poor-mid"
        else: pct_class = "poor-low"
        rows.append(f'''
        <div class="page-row">
          <a class="path" href="{full_url}" target="_blank" rel="noopener">{path}</a>
          <div class="stats">
            <span class="pct-poor {pct_class}">{pct_poor:.1f}% poor</span>
            <span class="meta">{p["total"]:,} events · {p["poor"]:,} poor</span>
            <span class="deeplinks">
              <a href="{psi_link}" target="_blank" rel="noopener" title="Open in PageSpeed Insights">PSI ↗</a>
            </span>
          </div>
        </div>''')
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
    html = html.replace("__SNAPSHOT_MOBILE__", render_snapshot_section("mobile", latest, prev))
    html = html.replace("__SNAPSHOT_DESKTOP__", render_snapshot_section("desktop", latest, prev))
    html = html.replace("__RUM_RATINGS__", render_rum_cwv_cards(rum.get("metrics", {})))
    html = html.replace("__TOP_PAGES_LCP__", render_top_pages(rum.get("top_pages", {}).get("LCP", []), "LCP"))
    html = html.replace("__TOP_PAGES_INP__", render_top_pages(rum.get("top_pages", {}).get("INP", []), "INP"))
    html = html.replace("__TOP_PAGES_CLS__", render_top_pages(rum.get("top_pages", {}).get("CLS", []), "CLS"))
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
    ap.add_argument("--no-crux", action="store_true", help="skip CrUX real-shopper p75 fetch")
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

    if not args.no_crux:
        # CrUX is fast (~1-2s/call) and gives REAL real-shopper p75 values.
        # Always try CrUX before PSI — it's the more reliable lab-quality source.
        try:
            crux_key = get_psi_key()  # CrUX shares the PSI Google Cloud API key
            print("  CrUX: fetching real-shopper p75 (mobile + desktop)...", flush=True)
            t0 = time.time()
            snapshot["crux"] = {}
            for form_factor, label in [("PHONE", "mobile"), ("DESKTOP", "desktop")]:
                r = query_crux(args.url, form_factor, crux_key)
                if r:
                    snapshot["crux"][label] = r
                    print(f"    {label}: LCP {r.get('lcp_ms', 0):.0f}ms · CLS {r.get('cls', 0):.3f} · INP {r.get('inp_ms', 0):.0f}ms")
            print(f"  CrUX total: {time.time()-t0:.1f}s")
            if not snapshot["crux"]:
                del snapshot["crux"]
        except SystemExit:
            print("  CrUX: skipped (no API key)", file=sys.stderr)

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
    has_crux = bool(snapshot.get("crux"))
    if has_psi or has_ga4 or has_crux:
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
