#!/usr/bin/env python3
"""
weekly-game-plan.py — Autonomous Monday morning perf review.

Runs on a launchd schedule (~/Library/LaunchAgents/com.hairmnl.weekly-perf.plist),
every Monday at 1:00 AM Manila time. Captures a fresh dashboard snapshot,
diffs against the snapshot from ~7 days ago, identifies the worst-trending
metrics + pages, cross-references with the Beads ready stack, and writes
a markdown game plan to:

  /Users/y9378348c/Downloads/HairMNL-Weekly-Game-Plan-YYYY-MM-DD.md

Then opens the file (so it's the first thing you see Monday morning) and
fires a macOS notification with the top-1 task. Optionally creates a Gmail
draft if Gmail OAuth is configured (skipped silently if not).

The script does the data collection + heuristic ranking. The final
"approve / veto / modify" judgment is left to Jonathan in chat — he reads
the markdown, replies in chat, Claude executes.

Manual run:
  GA4_PROPERTY_ID=248106289 ./scripts/weekly-game-plan.py
  ./scripts/weekly-game-plan.py --dry-run   # don't open file or notify
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path('/Users/y9378348c/Projects/hairmnl-theme')
SNAPSHOTS = REPO_ROOT / 'dashboard/data/snapshots.jsonl'
DOWNLOADS = Path.home() / 'Downloads'
MANILA = timezone(timedelta(hours=8))

# CrUX/CWV good thresholds
GOOD = {
    'lcp_ms': 2500, 'cls': 0.10, 'inp_ms': 200, 'fcp_ms': 1800, 'ttfb_ms': 800,
}


def run_dashboard_snapshot():
    """Fetch fresh CrUX + GA4 RUM data, append to snapshots.jsonl."""
    print('  → running ./scripts/build-perf-dashboard.py --no-psi ...')
    env = {**os.environ, 'GA4_PROPERTY_ID': os.environ.get('GA4_PROPERTY_ID', '248106289')}
    r = subprocess.run(
        ['./scripts/build-perf-dashboard.py', '--no-psi'],
        cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        print(f'  ⚠ dashboard build returncode={r.returncode}', file=sys.stderr)
        print(r.stderr[-1000:], file=sys.stderr)


def load_snapshots():
    if not SNAPSHOTS.exists():
        return []
    out = []
    for line in SNAPSHOTS.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def parse_ts(s: dict) -> datetime:
    return datetime.fromisoformat(s['timestamp'].replace('Z', '+00:00'))


def find_prior_week(snaps: list, latest: dict, target_days: int = 7) -> dict | None:
    """Find the snapshot closest to N days before latest. Returns None if no
    good candidate (e.g., history shorter than 3 days)."""
    target = parse_ts(latest) - timedelta(days=target_days)
    earliest = parse_ts(snaps[0])
    if parse_ts(latest) - earliest < timedelta(days=3):
        return None
    candidates = [s for s in snaps if s is not latest]
    return min(candidates, key=lambda s: abs(parse_ts(s) - target))


def metric_status(metric_key: str, value: float | None) -> str:
    """Returns 'good' / 'warn' / 'poor' / '?' based on Google CWV thresholds."""
    if value is None:
        return '?'
    if metric_key not in GOOD:
        return '?'
    g = GOOD[metric_key]
    # poor threshold is roughly 2x good (for ms metrics) or 2.5x (for CLS).
    poor_mult = 2.5 if metric_key == 'cls' else (2.0 if metric_key in ('inp_ms', 'tbt_ms') else 1.6)
    poor = g * poor_mult
    if value <= g:
        return 'good'
    if value <= poor:
        return 'warn'
    return 'poor'


def fmt_metric(metric_key: str, value: float | None) -> str:
    if value is None:
        return 'n/a'
    if metric_key == 'cls':
        return f'{value:.3f}'
    if metric_key == 'score':
        return f'{value:.0f}'
    if value >= 1000:
        return f'{value/1000:.2f} s'
    return f'{value:.0f} ms'


def fmt_delta(metric_key: str, now_v: float | None, then_v: float | None) -> tuple[str, str]:
    """Returns (delta_str, direction) where direction is 'better'/'worse'/'flat'/'?'."""
    if now_v is None or then_v is None:
        return ('—', '?')
    d = now_v - then_v
    pct = (d / then_v * 100) if then_v else 0
    if metric_key == 'cls':
        d_str = f'{d:+.3f} ({pct:+.0f}%)'
    elif metric_key == 'score':
        d_str = f'{d:+.0f}'
    elif abs(d) >= 100:
        d_str = f'{d/1000:+.2f}s ({pct:+.0f}%)'
    else:
        d_str = f'{d:+.0f}ms ({pct:+.0f}%)'
    if abs(pct) < 1:
        return (d_str, 'flat')
    # For all CWV: lower is better (except score which is higher-is-better, but score isn't in CrUX)
    return (d_str, 'better' if d < 0 else 'worse')


def diff_crux(now: dict, prior: dict, form_factor: str) -> list[dict]:
    """Returns list of {metric, now, prior, delta_str, direction, status_now}."""
    rows = []
    n = (now.get('crux') or {}).get(form_factor) or {}
    p = (prior.get('crux') or {}).get(form_factor) or {}
    for key in ('lcp_ms', 'cls', 'inp_ms', 'fcp_ms', 'ttfb_ms'):
        nv, pv = n.get(key), p.get(key)
        d_str, direction = fmt_delta(key, nv, pv)
        rows.append({
            'metric': key.upper().replace('_MS', '').replace('_', ' '),
            'now': fmt_metric(key, nv),
            'prior': fmt_metric(key, pv),
            'delta': d_str,
            'direction': direction,
            'status_now': metric_status(key, nv),
        })
    return rows


def diff_rum_ratings(now: dict, prior: dict) -> list[dict]:
    rows = []
    n_metrics = ((now.get('ga4') or {}).get('metrics')) or {}
    p_metrics = ((prior.get('ga4') or {}).get('metrics')) or {}
    for m in ('LCP', 'CLS', 'INP', 'FCP', 'TTFB'):
        n = n_metrics.get(m, {})
        p = p_metrics.get(m, {})
        n_pg = n.get('p_good', 0) * 100
        p_pg = p.get('p_good', 0) * 100
        d = n_pg - p_pg
        rows.append({
            'metric': m,
            'now_pct_good': f'{n_pg:.1f}%',
            'prior_pct_good': f'{p_pg:.1f}%',
            'delta_pp': f'{d:+.1f} pp',
            'now_events': n.get('total', 0),
            'pass_now': n_pg >= 75,
            'pass_prior': p_pg >= 75,
        })
    return rows


def diff_top_pages(now: dict, prior: dict, metric: str) -> dict:
    """Returns {now_top: [...], prior_top: [...], new_in_top: [...], exited_top: [...]}."""
    n_pages = (((now.get('ga4') or {}).get('top_pages')) or {}).get(metric, []) or []
    p_pages = (((prior.get('ga4') or {}).get('top_pages')) or {}).get(metric, []) or []
    n_paths = {p['page'] for p in n_pages}
    p_paths = {p['page'] for p in p_pages}
    return {
        'now_top': n_pages,
        'prior_top': p_pages,
        'new_in_top': sorted(n_paths - p_paths),
        'exited_top': sorted(p_paths - n_paths),
    }


def get_bd_ready() -> str:
    """Run `bd ready` and return its output (or fallback message)."""
    try:
        r = subprocess.run(['bd', 'ready'], cwd=str(REPO_ROOT),
                           capture_output=True, text=True, timeout=15)
        return r.stdout.strip() or '(no output)'
    except Exception as e:
        return f'(bd ready failed: {e})'


def get_bd_recent_closed(days: int = 7) -> list[str]:
    """Closed beads in last N days — to surface what shipped this week."""
    try:
        # bd list --status=closed sorted by closed_at would be ideal, but
        # bd doesn't expose that filter directly. Approximation: list all
        # closed and parse JSONL output if available.
        r = subprocess.run(['bd', 'list', '--status=closed'],
                           cwd=str(REPO_ROOT),
                           capture_output=True, text=True, timeout=15)
        # Just return last 10 lines — they tend to be most recent
        lines = [l for l in r.stdout.splitlines() if l.strip().startswith('●') or l.strip().startswith('✓')]
        return lines[:10]
    except Exception:
        return []


def js_error_pipeline_health(latest: dict) -> str:
    errors = ((latest.get('ga4') or {}).get('js_errors')) or []
    if not errors:
        return 'NO_DATA'
    # Look for at least one error with a real (non-fallback) error_type
    real = [e for e in errors if e.get('type') not in ('?', '(not set)', '', None)]
    if real:
        return 'WORKING'
    return 'STILL_BROKEN'


def needle_movers(now: dict, prior: dict | None) -> list[dict]:
    """Heuristic ranking of what to work on next week."""
    hits = []

    # 1. Worst RUM regressions
    if prior:
        rum_rows = diff_rum_ratings(now, prior)
        for r in rum_rows:
            try:
                d = float(r['delta_pp'].split()[0])
            except (ValueError, IndexError):
                d = 0
            if d <= -1.5:  # >1.5pp drop in % good
                hits.append({
                    'priority_score': abs(d) * (50 if not r['pass_now'] else 10),
                    'kind': 'rum_regression',
                    'title': f'{r["metric"]} % good dropped {r["delta_pp"]} this week ({r["prior_pct_good"]} → {r["now_pct_good"]})',
                    'why': f'Real-shopper field metric is moving the wrong direction over {r["now_events"]:,} events',
                    'actionable': r['metric'] in ('CLS', 'LCP', 'INP'),
                })

    # 2. Pages newly entering the top 5 friction (per metric)
    if prior:
        for metric in ('LCP', 'INP', 'CLS'):
            d = diff_top_pages(now, prior, metric)
            for path in d['new_in_top']:
                # Find the now-row for this path
                row = next((p for p in d['now_top'] if p['page'] == path), None)
                if row:
                    hits.append({
                        'priority_score': row.get('p_poor', 0) * 200 + min(row.get('total', 0), 500) * 0.1,
                        'kind': 'new_friction_page',
                        'title': f'NEW in top-5 {metric} friction: {path} ({row.get("p_poor", 0)*100:.1f}% poor, n={row.get("total", 0):,})',
                        'why': f'Page entered the {metric} worst-5 list this week — investigate before it spreads',
                        'actionable': True,
                    })

    # 3. CrUX p75 mobile metrics still in POOR
    crux_mobile = (now.get('crux') or {}).get('mobile') or {}
    for key in ('lcp_ms', 'cls', 'inp_ms', 'fcp_ms'):
        v = crux_mobile.get(key)
        if v is not None and metric_status(key, v) == 'poor':
            hits.append({
                'priority_score': 30,
                'kind': 'crux_poor',
                'title': f'CrUX mobile {key.upper().replace("_MS","")} = {fmt_metric(key, v)} (POOR)',
                'why': 'Real-shopper p75 in the POOR band — Google ranking signal degraded',
                'actionable': key != 'ttfb_ms',  # TTFB largely Shopify-server-side
            })

    # 4. Persistently failing CWV (in case prior was None — first run)
    n_metrics = ((now.get('ga4') or {}).get('metrics')) or {}
    for m, d in n_metrics.items():
        pg = d.get('p_good', 0) * 100
        if pg < 75 and pg > 0:  # FAIL the 75% threshold
            hits.append({
                'priority_score': (75 - pg) * 5,
                'kind': 'rum_fail',
                'title': f'{m} % good = {pg:.1f}% (below 75% PASS threshold, n={d.get("total", 0):,})',
                'why': 'Failing the Google Core Web Vitals criterion for this metric',
                'actionable': m in ('LCP', 'CLS', 'INP'),
            })

    # 5. JS error pipeline health check
    if js_error_pipeline_health(now) == 'STILL_BROKEN':
        hits.append({
            'priority_score': 80,
            'kind': 'gtm_pipeline',
            'title': 'GA4 js_error event params still null (GTM tag config not yet updated)',
            'why': 'Theme dataLayer correct (verified in browser), but GTM not forwarding error_type/error_message/error_source. Blocks all error visibility.',
            'actionable': False,  # Admin task in GTM
        })

    # Dedup & rank
    seen_titles = set()
    hits.sort(key=lambda h: -h['priority_score'])
    out = []
    for h in hits:
        if h['title'] in seen_titles:
            continue
        seen_titles.add(h['title'])
        out.append(h)
        if len(out) >= 10:
            break
    return out


def render_markdown(now: dict, prior: dict | None) -> str:
    today_local = datetime.now(MANILA)
    week_label = today_local.strftime('%Y-%m-%d')
    parts = [
        f'# HairMNL — Weekly Perf Game Plan — week of {week_label}',
        '',
        f'**Generated:** {today_local.strftime("%Y-%m-%d %H:%M %Z")}  ',
        f'**Snapshot:** {now["timestamp"]}  ',
        f'**Comparison baseline:** {"none — first week, no prior snapshot" if not prior else prior["timestamp"]}',
        '',
        '---',
        '',
        '## TL;DR',
        '',
    ]

    movers = needle_movers(now, prior)
    if movers:
        top = movers[0]
        parts.append(f'**Top priority this week:** {top["title"]}')
        parts.append('')
        parts.append(f'_{top["why"]}_')
    else:
        parts.append('No new needle-movers this week. CWV looks stable. Could use the week to chip at the deferred follow-ups (see `bd ready`).')

    parts.extend(['', '---', '', '## Metric movement'])

    if prior:
        parts.append('')
        parts.append('### CrUX mobile p75 (real-shopper, 28-day)')
        parts.append('')
        parts.append('| Metric | This week | Last week | Δ | Direction |')
        parts.append('|---|---|---|---|---|')
        for r in diff_crux(now, prior, 'mobile'):
            arrow = '↓' if r['direction'] == 'better' else ('↑' if r['direction'] == 'worse' else '→')
            parts.append(f'| **{r["metric"]}** ({r["status_now"].upper()}) | {r["now"]} | {r["prior"]} | {arrow} {r["delta"]} | {r["direction"]} |')

        parts.append('')
        parts.append('### CrUX desktop p75')
        parts.append('')
        parts.append('| Metric | This week | Last week | Δ | Direction |')
        parts.append('|---|---|---|---|---|')
        for r in diff_crux(now, prior, 'desktop'):
            arrow = '↓' if r['direction'] == 'better' else ('↑' if r['direction'] == 'worse' else '→')
            parts.append(f'| **{r["metric"]}** ({r["status_now"].upper()}) | {r["now"]} | {r["prior"]} | {arrow} {r["delta"]} | {r["direction"]} |')

        parts.append('')
        parts.append('### GA4 RUM (% good, last 7 days)')
        parts.append('')
        parts.append('| Metric | This week | Last week | Δ | Status |')
        parts.append('|---|---|---|---|---|')
        for r in diff_rum_ratings(now, prior):
            status = ('✓ PASS' if r['pass_now'] else '✗ FAIL')
            if r['pass_now'] != r['pass_prior']:
                status += (' (NEW: just crossed threshold)' if r['pass_now'] else ' (REGRESSED below threshold)')
            parts.append(f'| **{r["metric"]}** | {r["now_pct_good"]} | {r["prior_pct_good"]} | {r["delta_pp"]} | {status} |')
    else:
        parts.append('')
        parts.append('_(No prior snapshot to compare — this is the first week of the weekly cadence. Future runs will diff vs the snapshot from ~7 days ago.)_')
        # Still show current state
        parts.append('')
        parts.append('### Current CrUX p75 mobile')
        parts.append('')
        parts.append('| Metric | Value | Status |')
        parts.append('|---|---|---|')
        crux_m = (now.get('crux') or {}).get('mobile') or {}
        for key in ('lcp_ms', 'cls', 'inp_ms', 'fcp_ms', 'ttfb_ms'):
            v = crux_m.get(key)
            parts.append(f'| **{key.upper().replace("_MS","")}** | {fmt_metric(key, v)} | {metric_status(key, v).upper()} |')

    parts.extend(['', '---', '', '## Top friction watch'])

    if prior:
        any_changes = False
        for metric in ('LCP', 'INP', 'CLS'):
            d = diff_top_pages(now, prior, metric)
            if d['new_in_top'] or d['exited_top']:
                any_changes = True
                parts.append('')
                parts.append(f'**{metric} — top-5 changes vs last week**')
                if d['new_in_top']:
                    for path in d['new_in_top']:
                        row = next((p for p in d['now_top'] if p['page'] == path), {})
                        parts.append(f'- ⚠️ NEW: `{path}` — {row.get("p_poor", 0)*100:.1f}% poor (n={row.get("total", 0):,})')
                if d['exited_top']:
                    for path in d['exited_top']:
                        parts.append(f'- ✓ EXITED: `{path}` (no longer in worst-5)')
        if not any_changes:
            parts.append('')
            parts.append('_(Top-5 friction lists unchanged vs last week. Same pages still need attention.)_')
    else:
        parts.append('')
        parts.append('_(Friction watch becomes meaningful next week once we have a baseline to diff against.)_')

    # Always show current top-5 for actionability
    parts.append('')
    parts.append('### Current top friction (this week)')
    for metric in ('LCP', 'INP', 'CLS'):
        pages = (((now.get('ga4') or {}).get('top_pages')) or {}).get(metric, []) or []
        if not pages:
            continue
        parts.append('')
        parts.append(f'**{metric}**')
        for p in pages[:5]:
            parts.append(f'- `{p["page"][:80]}` — {p.get("p_poor", 0)*100:.1f}% poor · n={p.get("total", 0):,}')

    parts.extend(['', '---', '', '## Proposed game plan (top 5)'])

    # Top 5 needle-movers, formatted as approve/veto/modify items
    if movers:
        for i, m in enumerate(movers[:5], 1):
            tag = '✅ codable' if m.get('actionable') else '⚠️ needs decision/admin'
            parts.append('')
            parts.append(f'### {i}. {m["title"]}  ·  {tag}')
            parts.append('')
            parts.append(f'**Why:** {m["why"]}')
            parts.append('')
            parts.append(f'**Reply with:** `approve {i}` / `veto {i}` / `modify {i}: <change>`')
    else:
        parts.append('')
        parts.append('_No urgent needle-movers detected. Use the week to clear backlog from `bd ready`._')

    parts.extend([
        '', '---', '',
        '## Open Beads queue (bd ready snapshot)',
        '',
        '```',
        get_bd_ready()[:2500],
        '```',
        '',
        '## Recent closures (work shipped)',
        '',
    ])
    closed = get_bd_recent_closed()
    if closed:
        parts.extend(closed[:10])
    else:
        parts.append('_(no recent closures captured)_')

    parts.extend([
        '', '---', '',
        '## Blocked on you (admin / decision)',
        '',
    ])
    if js_error_pipeline_health(now) == 'STILL_BROKEN':
        parts.append('- **GTM tag fix for js_error event** — theme dataLayer is correct (verified live), but GTM tag isn\'t forwarding `error_type` / `error_message` / `error_source` to GA4. Without this, all client-side error visibility is dark.')
    parts.append('- **Anything new from your side?** Reply with admin updates and I\'ll incorporate.')

    parts.extend([
        '', '---', '',
        f'_Generated by `scripts/weekly-game-plan.py`. Live dashboard: <https://jjoson-ai.github.io/hairmnl-theme/>. To refresh manually: `GA4_PROPERTY_ID=248106289 ./scripts/build-perf-dashboard.py --no-psi`._',
    ])

    return '\n'.join(parts)


def macos_notify(title: str, body: str):
    """Best-effort Mac desktop notification. Silently no-op if unavailable."""
    try:
        # Escape double-quotes in body for AppleScript
        body_clean = body.replace('"', "'").replace('\n', ' ')[:200]
        title_clean = title.replace('"', "'")
        subprocess.run(
            ['osascript', '-e',
             f'display notification "{body_clean}" with title "{title_clean}" sound name "Glass"'],
            check=False, timeout=5,
        )
    except Exception:
        pass


def open_file(path: Path):
    try:
        subprocess.run(['open', str(path)], check=False, timeout=5)
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help="don't open file or notify")
    ap.add_argument('--no-fetch', action='store_true', help="don't capture a fresh snapshot first")
    args = ap.parse_args()

    if not args.no_fetch:
        run_dashboard_snapshot()

    snaps = load_snapshots()
    if not snaps:
        print('No snapshots — run ./scripts/build-perf-dashboard.py at least once first.', file=sys.stderr)
        sys.exit(1)

    latest = snaps[-1]
    prior = find_prior_week(snaps, latest, target_days=7)

    today_local = datetime.now(MANILA)
    out_path = DOWNLOADS / f'HairMNL-Weekly-Game-Plan-{today_local:%Y-%m-%d}.md'
    md = render_markdown(latest, prior)
    out_path.write_text(md)
    print(f'  ✓ Wrote {out_path} ({len(md):,} bytes)')

    movers = needle_movers(latest, prior)
    top_line = movers[0]['title'] if movers else 'No urgent needle-movers — clear backlog'

    if not args.dry_run:
        macos_notify('HairMNL Weekly Plan', f'Top: {top_line}')
        open_file(out_path)

    print(f'  ✓ Top task: {top_line}')


if __name__ == '__main__':
    main()
