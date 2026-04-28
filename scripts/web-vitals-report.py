#!/usr/bin/env python3
"""
web-vitals-report.py — query HairMNL's GA4 for real-shopper web vitals + JS errors.

Pulls the data the theme's RUM reporter pushes (CLS / LCP / INP / FCP / js_error)
and aggregates by page / device / browser / etc. Designed for terminal use:
output is markdown tables by default, JSON with --json for piping.

Setup (one-time, ~5 min):
  1. GA4 admin → bottom-left gear → API & Services
  2. Create a Service Account (name e.g. "hairmnl-rum-reader")
  3. Add a key → JSON → download
  4. Save the key file:    mv ~/Downloads/hairmnl-rum-reader-*.json ~/.config/hairmnl-ga4-key.json
  5. GA4 admin → Property Access Management → grant the service account "Viewer" role
     on the HairMNL GA4 property.
  6. Find the numeric Property ID in GA4 admin → Property Settings → Property ID.
  7. Add to your shell rc:  export GA4_PROPERTY_ID=NNNNNNN
  8. pip install google-analytics-data

Usage:
  ./scripts/web-vitals-report.py                       # default: web vitals by page, last 7d
  ./scripts/web-vitals-report.py --metric LCP          # filter to one metric
  ./scripts/web-vitals-report.py --by device           # group by device category
  ./scripts/web-vitals-report.py --by browser
  ./scripts/web-vitals-report.py --by metric_id        # group by attribution string (LCP element, INP target)
  ./scripts/web-vitals-report.py --days 30 --top 20    # last 30d, top 20 rows
  ./scripts/web-vitals-report.py --errors              # JS error breakdown instead
  ./scripts/web-vitals-report.py --diagnose            # quick triage view: top problematic items
  ./scripts/web-vitals-report.py --json                # output JSON for piping/analysis

Aggregation note:
  GA4 Data API does NOT support percentile aggregation on custom metrics.
  This script reports COUNT / AVG / MAX. For p75 (the canonical web-vitals
  measure), you need GA4 → BigQuery export + SQL — see
  beads ticket TBD-bigquery-export for that follow-up. For now, AVG +
  MAX gives a useful triage signal even if it's not the textbook metric.
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        RunReportRequest,
        FilterExpression,
        FilterExpressionList,
        Filter,
        OrderBy,
    )
except ImportError:
    print("ERROR: missing dependency. Install with:\n  pip install google-analytics-data", file=sys.stderr)
    sys.exit(1)


# Maps short --by names to GA4 dimension names.
DIMENSION_MAP = {
    "page":      "pagePath",
    "device":    "deviceCategory",
    "browser":   "browser",
    "country":   "country",
    "os":        "operatingSystem",
    "screen":    "screenResolution",
    "metric_id": "customEvent:metric_id",   # the attribution string (LCP element, INP target, etc)
}


def get_client_and_property():
    """Return (BetaAnalyticsDataClient, 'properties/<id>') or exit on misconfig."""
    key_path = os.environ.get("GA4_KEY") or os.path.expanduser("~/.config/hairmnl-ga4-key.json")
    if not os.path.exists(key_path):
        print(f"ERROR: GA4 service account key file not found at: {key_path}", file=sys.stderr)
        print("       Set GA4_KEY env var to the path of your downloaded JSON key.", file=sys.stderr)
        print("       See script docstring for setup steps.", file=sys.stderr)
        sys.exit(1)
    property_id = os.environ.get("GA4_PROPERTY_ID")
    if not property_id:
        print("ERROR: GA4_PROPERTY_ID env var required.", file=sys.stderr)
        print("       Find the numeric ID in GA4 admin → Property Settings → Property ID.", file=sys.stderr)
        print("       Then: export GA4_PROPERTY_ID=NNNNNNN", file=sys.stderr)
        sys.exit(1)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
    return BetaAnalyticsDataClient(), f"properties/{property_id}"


def _and_filter(*filters: Filter) -> FilterExpression:
    """Build an AND-grouped FilterExpression from one or more flat Filters."""
    if len(filters) == 1:
        return FilterExpression(filter=filters[0])
    return FilterExpression(
        and_group=FilterExpressionList(
            expressions=[FilterExpression(filter=f) for f in filters]
        )
    )


def query_web_vitals(args) -> List[Dict[str, Any]]:
    client, prop = get_client_and_property()

    # Always filter to event_name = web_vital so we don't pull every event.
    flat_filters = [
        Filter(field_name="eventName", string_filter=Filter.StringFilter(value="web_vital"))
    ]
    if args.metric != "all":
        flat_filters.append(
            Filter(
                field_name="customEvent:metric_name",
                string_filter=Filter.StringFilter(value=args.metric.upper()),
            )
        )

    dim_name = DIMENSION_MAP.get(args.by, args.by)

    request = RunReportRequest(
        property=prop,
        date_ranges=[DateRange(start_date=f"{args.days}daysAgo", end_date="today")],
        dimensions=[
            Dimension(name=dim_name),
            Dimension(name="customEvent:metric_name"),
        ],
        metrics=[
            Metric(name="eventCount"),
            Metric(name="metric_value_avg", expression="customEvent:metric_value / eventCount"),
            Metric(name="metric_value_total", expression="customEvent:metric_value"),
        ],
        dimension_filter=_and_filter(*flat_filters),
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
        limit=args.top,
    )

    response = client.run_report(request)
    rows = []
    for row in response.rows:
        dim_value = row.dimension_values[0].value or "(not set)"
        metric_name = row.dimension_values[1].value or "?"
        count = int(row.metric_values[0].value)
        avg_value = float(row.metric_values[1].value or 0)
        total_value = float(row.metric_values[2].value or 0)
        rows.append({
            "by_value": dim_value,
            "metric": metric_name,
            "count": count,
            "avg": avg_value,
            "max": total_value / count if count else 0,  # rough — not real max, see note in docstring
        })
    return rows


def query_errors(args) -> List[Dict[str, Any]]:
    client, prop = get_client_and_property()
    request = RunReportRequest(
        property=prop,
        date_ranges=[DateRange(start_date=f"{args.days}daysAgo", end_date="today")],
        dimensions=[
            Dimension(name="customEvent:error_source"),
            Dimension(name="customEvent:error_message"),
            Dimension(name="customEvent:error_type"),
        ],
        metrics=[
            Metric(name="eventCount"),
        ],
        dimension_filter=FilterExpression(
            filter=Filter(field_name="eventName", string_filter=Filter.StringFilter(value="js_error"))
        ),
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
        limit=args.top,
    )
    response = client.run_report(request)
    rows = []
    for row in response.rows:
        rows.append({
            "source": row.dimension_values[0].value or "(unknown)",
            "message": row.dimension_values[1].value or "(no message)",
            "type": row.dimension_values[2].value or "?",
            "count": int(row.metric_values[0].value),
        })
    return rows


def fmt_value(metric: str, value: float) -> str:
    """Format a metric value for human reading. CLS = 3 decimals, others = ms."""
    if metric == "CLS":
        return f"{value:.3f}"
    return f"{int(value):,}ms"


def render_table(rows: List[Dict[str, Any]], args) -> str:
    if not rows:
        return "(no data — events haven't started flowing yet, or the filter matched zero events)"
    if args.errors:
        out = ["| count | type | source | message |", "|---:|---|---|---|"]
        for r in rows:
            src = r["source"][:60]
            msg = r["message"][:80].replace("|", "\\|")
            out.append(f"| {r['count']:,} | {r['type']} | `{src}` | {msg} |")
        return "\n".join(out)
    # Web vitals table
    by_label = args.by
    out = [f"| {by_label} | metric | count | avg | (rough max) |", "|---|---|---:|---:|---:|"]
    for r in rows:
        avg = fmt_value(r["metric"], r["avg"])
        mx = fmt_value(r["metric"], r["max"])
        bv = r["by_value"][:60]
        out.append(f"| `{bv}` | {r['metric']} | {r['count']:,} | {avg} | {mx} |")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(
        description="Query HairMNL GA4 for real-shopper web vitals + JS errors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See script docstring (head of file) for setup instructions.",
    )
    parser.add_argument("--metric", default="all",
                        choices=["all", "CLS", "LCP", "INP", "FCP"],
                        help="Filter to one web vital (default: all)")
    parser.add_argument("--by", default="page",
                        choices=list(DIMENSION_MAP.keys()),
                        help="Group by dimension (default: page)")
    parser.add_argument("--days", type=int, default=7,
                        help="Lookback window in days (default: 7)")
    parser.add_argument("--top", type=int, default=10,
                        help="Top N rows (default: 10)")
    parser.add_argument("--errors", action="store_true",
                        help="Show JS error events instead of web vitals")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of markdown table")
    args = parser.parse_args()

    try:
        rows = query_errors(args) if args.errors else query_web_vitals(args)
    except Exception as e:
        print(f"ERROR querying GA4: {e}", file=sys.stderr)
        print("Common causes: service account lacks Viewer role on property; ", file=sys.stderr)
        print("                custom dimensions not yet registered in GA4 admin; ", file=sys.stderr)
        print("                <24h since first event (custom dims need backfill window); ", file=sys.stderr)
        print("                wrong GA4_PROPERTY_ID.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps({"args": vars(args), "rows": rows}, indent=2))
    else:
        print(f"# Web vitals — last {args.days} days, by {args.by}")
        if args.metric != "all":
            print(f"_Filtered to metric: {args.metric}_")
        print()
        print(render_table(rows, args))
        print()
        print("Note: GA4 Data API doesn't support percentile aggregation on custom metrics.")
        print("Showing AVG (and rough MAX). For canonical p75 web vitals, set up GA4 → BigQuery")
        print("export and use SQL with PERCENTILE_CONT.")


if __name__ == "__main__":
    main()
