#!/usr/bin/env python3
"""
psi-baseline-matrix.py — Phase 0.1/0.2 data collection for bd hairmnl-theme-ujg6.

Runs PSI against (5 templates × 2 strategies × 2 themes) = 20 cells, n=3 each.
Saves full Lighthouse JSON per cell so downstream tasks (0.2 CLS attribution,
0.4 synthesis) can extract whatever audit data they need.

Output:
  /tmp/psi-baseline/<theme>-<strategy>-<template>-run<N>.json   (raw lighthouseResult)
  /tmp/psi-baseline/summary.json                                (medians + key audits)
  /tmp/psi-baseline/summary.md                                  (human-readable table)

Usage:
  python3 scripts/psi-baseline-matrix.py [--runs N] [--concurrency C]

Defaults: runs=3, concurrency=3.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from statistics import median
from typing import Any

OUT_DIR = Path("/tmp/psi-baseline")
PREVIEW_THEME_ID = "141168312419"

# Five templates, by handle. Top product is from SONNET_HANDOFF.md reference.
TEMPLATES = [
    ("home", "/"),
    ("collection", "/collections/best-sellers"),
    ("pdp", "/products/kerastase-genesis-anti-hair-fall-fortifying-serum"),
    ("cart", "/cart"),
    # 2026-05-18 late: /collections/loreal-professionnel returns 200 but
    # pageType=index (serves homepage content as collection — broken handle).
    # Replaced with /collections/davines (verified pageType=collection).
    ("brand", "/collections/davines"),
]

THEMES = [
    ("p6-live", ""),                                 # bare URL, no preview cookie
    ("p8-dev", f"?preview_theme_id={PREVIEW_THEME_ID}"),
]

STRATEGIES = ["mobile", "desktop"]

API_BASE = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def get_psi_api_key() -> str:
    """Read PSI_API_KEY from env, then macOS Keychain."""
    key = os.environ.get("PSI_API_KEY")
    if key:
        return key
    try:
        r = subprocess.run(
            ["security", "find-generic-password", "-a", os.environ["USER"], "-s", "psi-api-key", "-w"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    raise SystemExit("ERROR: PSI_API_KEY not in env or Keychain.")


def run_psi_once(url: str, strategy: str, api_key: str, timeout: int = 180) -> dict[str, Any] | None:
    """Single PSI call. Returns lighthouseResult dict or None on failure."""
    qs = urllib.parse.urlencode({
        "url": url,
        "strategy": strategy,
        "category": "performance",
    })
    req = urllib.request.Request(f"{API_BASE}?{qs}", headers={"X-goog-api-key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
    if "error" in data:
        return {"error": data["error"].get("message", str(data["error"]))}
    return data.get("lighthouseResult", {"error": "no lighthouseResult"})


def cell_id(theme: str, strategy: str, template: str, run: int) -> str:
    return f"{theme}-{strategy}-{template}-run{run}"


def run_cell(theme: str, theme_qs: str, strategy: str, template: str, template_path: str,
             run: int, api_key: str, runs_total: int) -> dict[str, Any]:
    """One PSI invocation; persists raw + extracted metrics."""
    url = f"https://www.hairmnl.com{template_path}{theme_qs}"
    cid = cell_id(theme, strategy, template, run)
    print(f"  [{cid}] start", flush=True)
    t0 = time.time()
    result = run_psi_once(url, strategy, api_key)
    dt = time.time() - t0

    raw_path = OUT_DIR / f"{cid}.json"
    raw_path.write_text(json.dumps(result, indent=2))

    if not result or "error" in (result or {}):
        err = (result or {}).get("error", "no-data")
        print(f"  [{cid}] FAIL ({dt:.0f}s): {err}", flush=True)
        return {"cell": cid, "ok": False, "error": err, "elapsed_s": round(dt, 1)}

    audits = result.get("audits", {})
    cat = result.get("categories", {}).get("performance", {})

    metrics = {
        "cell": cid,
        "theme": theme,
        "strategy": strategy,
        "template": template,
        "run": run,
        "ok": True,
        "elapsed_s": round(dt, 1),
        "score": round(cat.get("score", 0) * 100) if cat.get("score") is not None else None,
        "fcp_ms": audits.get("first-contentful-paint", {}).get("numericValue"),
        "lcp_ms": audits.get("largest-contentful-paint", {}).get("numericValue"),
        "tbt_ms": audits.get("total-blocking-time", {}).get("numericValue"),
        "cls": audits.get("cumulative-layout-shift", {}).get("numericValue"),
        "si_ms": audits.get("speed-index", {}).get("numericValue"),
        "tti_ms": audits.get("interactive", {}).get("numericValue"),
    }
    print(f"  [{cid}] OK ({dt:.0f}s): score={metrics['score']} CLS={metrics['cls']:.3f} TBT={metrics['tbt_ms']:.0f}ms", flush=True)
    return metrics


def fmt_metric(name: str, v: float | None) -> str:
    if v is None:
        return "n/a"
    if name == "score":
        return f"{v}"
    if name == "cls":
        return f"{v:.3f}"
    if v >= 1000:
        return f"{v/1000:.2f}s"
    return f"{v:.0f}ms"


def aggregate(results: list[dict[str, Any]], runs: int) -> dict[str, Any]:
    """Median across runs per (theme, strategy, template). Skips failed cells."""
    out = {}
    for theme, _ in THEMES:
        for strategy in STRATEGIES:
            for template, _ in TEMPLATES:
                cell_runs = [r for r in results if r.get("ok") and r["theme"] == theme
                             and r["strategy"] == strategy and r["template"] == template]
                if not cell_runs:
                    out[f"{theme}|{strategy}|{template}"] = {"n": 0, "status": "all-failed"}
                    continue
                m = {"n": len(cell_runs)}
                for k in ("score", "fcp_ms", "lcp_ms", "tbt_ms", "cls", "si_ms", "tti_ms"):
                    vals = [r[k] for r in cell_runs if r.get(k) is not None]
                    m[k] = median(vals) if vals else None
                out[f"{theme}|{strategy}|{template}"] = m
    return out


def render_markdown(summary: dict[str, Any], runs: int) -> str:
    lines = []
    lines.append(f"# PSI baseline matrix — bd hairmnl-theme-ujg6.1 / .2")
    lines.append(f"")
    lines.append(f"Generated by `scripts/psi-baseline-matrix.py` (target n={runs} per cell). "
                 f"Sample size shown as `n=N/runs`. Skipped cells are PSI API failures (preview-URL 500s).")
    lines.append("")

    for strategy in STRATEGIES:
        lines.append(f"## {strategy.title()}")
        lines.append("")
        lines.append("| Template | Theme | n | Score | LCP | CLS | TBT | FCP | SI |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for template, _ in TEMPLATES:
            for theme, _ in THEMES:
                m = summary.get(f"{theme}|{strategy}|{template}", {"n": 0})
                if m.get("n", 0) == 0:
                    lines.append(f"| {template} | {theme} | 0 | — | — | — | — | — | — |")
                    continue
                lines.append(
                    f"| {template} | {theme} | {m['n']}/{runs} | "
                    f"{fmt_metric('score', m.get('score'))} | "
                    f"{fmt_metric('lcp_ms', m.get('lcp_ms'))} | "
                    f"{fmt_metric('cls', m.get('cls'))} | "
                    f"{fmt_metric('tbt_ms', m.get('tbt_ms'))} | "
                    f"{fmt_metric('fcp_ms', m.get('fcp_ms'))} | "
                    f"{fmt_metric('si_ms', m.get('si_ms'))} |"
                )
        lines.append("")

        # Delta table: P8 vs P6 for the same strategy
        lines.append(f"### {strategy.title()} delta (P8-dev minus P6-live)")
        lines.append("")
        lines.append("| Template | Δ Score | Δ LCP | Δ CLS | Δ TBT |")
        lines.append("|---|---|---|---|---|")
        for template, _ in TEMPLATES:
            p6 = summary.get(f"p6-live|{strategy}|{template}", {})
            p8 = summary.get(f"p8-dev|{strategy}|{template}", {})
            if p6.get("n", 0) and p8.get("n", 0):
                def d(k, scale=1.0, fmt="%.0f"):
                    v6 = p6.get(k); v8 = p8.get(k)
                    if v6 is None or v8 is None: return "—"
                    delta = (v8 - v6) * scale
                    return fmt % delta
                lines.append(
                    f"| {template} | {d('score', 1, '%+d')} | "
                    f"{d('lcp_ms', 1/1000.0, '%+.2fs')} | "
                    f"{d('cls', 1, '%+.3f')} | "
                    f"{d('tbt_ms', 1, '%+.0fms')} |"
                )
            else:
                lines.append(f"| {template} | (missing data) |  |  |  |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("**Bare P8 reference** (from `os2-migration/perf-baseline-comparison.md` 2026-05-17):")
    lines.append("- Mobile: score 62, CLS 0.000, TBT 175ms")
    lines.append("- Desktop: score 72, CLS 0.000, TBT 225ms")
    lines.append("")
    lines.append("These are NOT re-measured here — the dev theme has changed since the baseline was taken. "
                 "Use them as the 'what bare P8 was capable of' reference.")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--concurrency", type=int, default=3)
    args = p.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    api_key = get_psi_api_key()
    total_cells = len(THEMES) * len(STRATEGIES) * len(TEMPLATES) * args.runs
    print(f"PSI baseline matrix: {len(THEMES)} themes × {len(STRATEGIES)} strategies × "
          f"{len(TEMPLATES)} templates × {args.runs} runs = {total_cells} PSI calls", flush=True)
    print(f"Concurrency: {args.concurrency}. Output: {OUT_DIR}/", flush=True)
    print("", flush=True)

    jobs = []
    for theme, theme_qs in THEMES:
        for strategy in STRATEGIES:
            for template, template_path in TEMPLATES:
                for run in range(1, args.runs + 1):
                    jobs.append((theme, theme_qs, strategy, template, template_path, run))

    results = []
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = [ex.submit(run_cell, *job, api_key, args.runs) for job in jobs]
        for fut in concurrent.futures.as_completed(futs):
            results.append(fut.result())

    dt = time.time() - t0
    ok = sum(1 for r in results if r.get("ok"))
    fail = len(results) - ok
    print(f"\nDone. {ok}/{len(results)} OK ({fail} failed). Total wall: {dt/60:.1f} min.", flush=True)

    summary = aggregate(results, args.runs)
    (OUT_DIR / "summary.json").write_text(json.dumps({"results": results, "summary": summary}, indent=2))
    md = render_markdown(summary, args.runs)
    (OUT_DIR / "summary.md").write_text(md)
    print(f"\nWrote {OUT_DIR}/summary.json and summary.md")


if __name__ == "__main__":
    main()
