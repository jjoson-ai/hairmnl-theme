#!/usr/bin/env python3
"""
web-vitals-report.py — query HairMNL's GA4 for real-shopper Core Web Vitals
+ JS errors. Reads from the existing snippets/web-vitals-reporter.liquid
pipeline (shipped 2 days before this script was written, commit 367f920),
which uses Google's official web-vitals.js v4 attribution build.

Pipeline schema being queried:
  Event names: LCP | CLS | INP | FCP | TTFB (each metric is its own event)
  Custom dimensions:
    customEvent:metric_rating          'good' | 'needs-improvement' | 'poor'
    customEvent:metric_id              unique-per-pageview ID for dedup
    customEvent:metric_navigation_type 'navigate' | 'reload' | 'back-forward' | 'prerender'
    customEvent:debug_target           CSS selector / element tag for attribution

Why we report on RATING buckets, not raw values:
  The custom `metric_value` metric registered in this property doesn't
  populate via the API (likely a GTM tag wiring quirk — `value` flows to
  GA4's standard event_value field but the named custom metric doesn't
  capture). We query `metric_rating` instead, which is what the official
  Core Web Vitals reporting model uses anyway: a page is "passing" if
  ≥75% of pageviews land in 'good' for ALL metrics. Bucketed counts give
  better signal than means — a page with avg LCP 2.4s might still have
  20% of pageviews in 'poor' (>4s) which an average hides.

  CrUX rating thresholds (used by web-vitals.js v4):
    LCP:  good ≤ 2500 ms, poor > 4000 ms
    CLS:  good ≤ 0.10,    poor > 0.25
    INP:  good ≤ 200 ms,  poor > 500 ms
    FCP:  good ≤ 1800 ms, poor > 3000 ms
    TTFB: good ≤ 800 ms,  poor > 1800 ms

JS errors (from inline tracking added 2026-04-28):
  Event name: js_error
  Custom dimensions: customEvent:error_type, error_message, error_source

Setup (one-time, ~5 min):
  1. GA4 admin → API & Services → Service Account → Download JSON key
  2. mv ~/Downloads/<key>.json ~/.config/hairmnl-ga4-key.json
  3. GA4 admin → Property Access → grant service account Viewer
     (UI may reject — workaround: OAuth Playground POST to
      /v1alpha/properties/<id>/accessBindings with analytics.manage.users scope)
  4. export GA4_PROPERTY_ID=248106289
  5. pip install --user google-analytics-data

Usage:
  ./scripts/web-vitals-report.py                       # all CWV by page, last 7d
  ./scripts/web-vitals-report.py --metric LCP          # one metric only
  ./scripts/web-vitals-report.py --by device           # group by device
  ./scripts/web-vitals-report.py --by debug_target     # by attribution element
  ./scripts/web-vitals-report.py --rating poor --by page # only "poor" pages
  ./scripts/web-vitals-report.py --diagnose            # combined triage view
  ./scripts/web-vitals-report.py --errors              # JS error breakdown
  ./scripts/web-vitals-report.py --json                # JSON output for piping
  ./scripts/web-vitals-report.py --days 30 --top 25
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any
from collections import defaultdict

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange, Dimension, Metric, RunReportRequest,
        FilterExpression, FilterExpressionList, Filter, OrderBy,
    )
except ImportError:
    print("ERROR: pip install --user google-analytics-data", file=sys.stderr)
    sys.exit(1)


DIMENSION_MAP = {
    "page":         "pagePath",
    "device":       "deviceCategory",
    "browser":      "browser",
    "country":      "country",
    "os":           "operatingSystem",
    "screen":       "screenResolution",
    "debug_target": "customEvent:debug_target",
    "nav_type":     "customEvent:metric_navigation_type",
    "metric_id":    "customEvent:metric_id",
}

VITAL_EVENTS = ["LCP", "CLS", "INP", "FCP", "TTFB"]
RATING_ORDER = ["good", "needs-improvement", "poor"]


def get_client_and_property():
    key_path = os.environ.get("GA4_KEY") or os.path.expanduser("~/.config/hairmnl-ga4-key.json")
    if not os.path.exists(key_path):
        print(f"ERROR: GA4 key file not found: {key_path}", file=sys.stderr)
        sys.exit(1)
    pid = os.environ.get("GA4_PROPERTY_ID")
    if not pid:
        print("ERROR: GA4_PROPERTY_ID env var required (e.g. export GA4_PROPERTY_ID=248106289)", file=sys.stderr)
        sys.exit(1)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
    return BetaAnalyticsDataClient(), f"properties/{pid}"


def _and(*filters: Filter) -> FilterExpression:
    if len(filters) == 1:
        return FilterExpression(filter=filters[0])
    return FilterExpression(and_group=FilterExpressionList(
        expressions=[FilterExpression(filter=f) for f in filters]))


def _in(field: str, values: List[str]) -> Filter:
    return Filter(field_name=field, in_list_filter=Filter.InListFilter(values=values))


def _eq(field: str, value: str) -> Filter:
    return Filter(field_name=field, string_filter=Filter.StringFilter(value=value))


def query_vitals(args) -> Dict[str, Dict[str, Dict[str, int]]]:
    """Returns: {by_value: {metric: {rating: count}}}"""
    client, prop = get_client_and_property()

    flat = []
    if args.metric != "all":
        flat.append(_eq("eventName", args.metric))
    else:
        flat.append(_in("eventName", VITAL_EVENTS))
    if args.rating:
        flat.append(_eq("customEvent:metric_rating", args.rating))

    dim_name = DIMENSION_MAP.get(args.by, args.by)

    req = RunReportRequest(
        property=prop,
        date_ranges=[DateRange(start_date=f"{args.days}daysAgo", end_date="today")],
        dimensions=[
            Dimension(name=dim_name),
            Dimension(name="eventName"),
            Dimension(name="customEvent:metric_rating"),
        ],
        metrics=[Metric(name="eventCount")],
        dimension_filter=_and(*flat),
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
        limit=10000,
    )
    r = client.run_report(req)

    nested: Dict[str, Dict[str, Dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for row in r.rows:
        by_val = row.dimension_values[0].value or "(not set)"
        ev = row.dimension_values[1].value or "?"
        rating = row.dimension_values[2].value or "(no rating)"
        cnt = int(row.metric_values[0].value)
        nested[by_val][ev][rating] += cnt
    return nested


def query_errors(args):
    client, prop = get_client_and_property()
    req = RunReportRequest(
        property=prop,
        date_ranges=[DateRange(start_date=f"{args.days}daysAgo", end_date="today")],
        dimensions=[
            Dimension(name="customEvent:error_source"),
            Dimension(name="customEvent:error_message"),
            Dimension(name="customEvent:error_type"),
        ],
        metrics=[Metric(name="eventCount")],
        dimension_filter=FilterExpression(filter=_eq("eventName", "js_error")),
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
        limit=args.top,
    )
    r = client.run_report(req)
    return [{
        "source": row.dimension_values[0].value or "(unknown)",
        "message": row.dimension_values[1].value or "(no message)",
        "type": row.dimension_values[2].value or "?",
        "count": int(row.metric_values[0].value),
    } for row in r.rows]


def render_vitals(nested, args) -> str:
    if not nested:
        return "(no data)"

    rows_summary = []
    for by_val, by_metrics in nested.items():
        total = sum(sum(ratings.values()) for ratings in by_metrics.values())
        rows_summary.append((by_val, by_metrics, total))
    rows_summary.sort(key=lambda r: -r[2])
    rows_summary = rows_summary[:args.top]

    if args.metric != "all":
        out = [f"| {args.by} | total | good | needs-improv | poor | %good | %poor |",
               "|---|---:|---:|---:|---:|---:|---:|"]
        for by_val, by_metrics, total in rows_summary:
            ratings = by_metrics.get(args.metric, {})
            g = ratings.get("good", 0)
            n = ratings.get("needs-improvement", 0)
            p = ratings.get("poor", 0)
            t = g + n + p
            if t == 0:
                continue
            pg = 100 * g / t
            pp = 100 * p / t
            mark = "🚨 " if pg < 75 else ""
            out.append(f"| `{by_val[:60]}` | {t:,} | {g:,} | {n:,} | {p:,} | {mark}{pg:.1f}% | {pp:.1f}% |")
        return "\n".join(out)
    else:
        # Multi-metric: one column per metric showing %good
        all_metrics = sorted({m for _, by_metrics, _ in rows_summary for m in by_metrics.keys()})
        header = f"| {args.by} | total |" + "".join(f" {m} %good |" for m in all_metrics)
        sep = "|---|---:|" + "---:|" * len(all_metrics)
        out = [header, sep]
        for by_val, by_metrics, total in rows_summary:
            cells = [f"`{by_val[:60]}`", f"{total:,}"]
            for m in all_metrics:
                ratings = by_metrics.get(m, {})
                g = ratings.get("good", 0)
                t = sum(ratings.values())
                if t == 0:
                    cells.append("—")
                else:
                    pg = 100 * g / t
                    cells.append(f"{'🚨 ' if pg < 75 else ''}{pg:.0f}% ({t})")
            out.append("| " + " | ".join(cells) + " |")
        return "\n".join(out)


def render_errors(rows) -> str:
    if not rows:
        return "(no JS error events captured — either no errors yet, or js_error event not flowing through GTM)"
    out = ["| count | type | source | message |", "|---:|---|---|---|"]
    for r in rows:
        msg = r['message'][:80].replace('|', '\\|')
        out.append(f"| {r['count']:,} | {r['type']} | `{r['source'][:60]}` | {msg} |")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(
        description="HairMNL Core Web Vitals — real-shopper data from GA4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See script docstring for setup + schema notes.",
    )
    parser.add_argument("--metric", default="all", choices=["all"] + VITAL_EVENTS)
    parser.add_argument("--by", default="page", choices=list(DIMENSION_MAP.keys()))
    parser.add_argument("--rating", default="", choices=["", "good", "needs-improvement", "poor"])
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--errors", action="store_true", help="Show JS error breakdown")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        if args.errors:
            data = query_errors(args)
        else:
            data = query_vitals(args)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        if args.errors:
            print(json.dumps({"args": vars(args), "errors": data}, indent=2))
        else:
            # Convert defaultdicts → plain dicts for JSON
            plain = {k: {m: dict(r) for m, r in v.items()} for k, v in data.items()}
            print(json.dumps({"args": vars(args), "by_value": plain}, indent=2))
        return

    print(f"# {'JS errors' if args.errors else 'Core Web Vitals'} — last {args.days}d, by `{args.by}`")
    if args.metric != "all":
        print(f"_Filter: metric = {args.metric}_")
    if args.rating:
        print(f"_Filter: rating = {args.rating}_")
    print()
    print(render_errors(data) if args.errors else render_vitals(data, args))
    print()
    print("CrUX target: ≥75% of pageviews land in 'good' for each metric. 🚨 marks pages below that.")


if __name__ == "__main__":
    main()
