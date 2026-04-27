#!/usr/bin/env bash
# run-psi.sh — Quick PSI runner for HairMNL perf benchmarking.
#
# Usage:
#   ./scripts/run-psi.sh <url> [strategy] [num_runs]
#
# Examples:
#   ./scripts/run-psi.sh https://hairmnl.com/ mobile 3
#   ./scripts/run-psi.sh https://hairmnl.com/collections/all desktop 2
#   ./scripts/run-psi.sh https://hairmnl.com/products/davines-momo-shampoo
#
# Defaults: strategy=mobile, num_runs=3
#
# Requires PSI_API_KEY env var (Google Cloud Console → PageSpeed Insights API).
# Recommended: store key in ~/.zshrc or in /tmp/.psi_env (chmod 600) and source it.
#
# The key is sent via X-goog-api-key header (NOT URL query string) so it doesn't
# leak into shell history or HTTP access logs.

set -euo pipefail

URL="${1:?Usage: $0 <url> [strategy] [num_runs]}"
STRATEGY="${2:-mobile}"
N="${3:-3}"

if [[ -z "${PSI_API_KEY:-}" ]]; then
  if [[ -r /tmp/.psi_env ]]; then source /tmp/.psi_env; fi
fi

if [[ -z "${PSI_API_KEY:-}" ]]; then
  echo "ERROR: PSI_API_KEY env var not set."
  echo "Either: export PSI_API_KEY=AIzaSy..."
  echo "Or:     write it to /tmp/.psi_env (chmod 600) as 'export PSI_API_KEY=...'"
  exit 1
fi

python3 - "$URL" "$STRATEGY" "$N" <<'PYEOF'
import json, urllib.request, urllib.parse, os, sys, time
from statistics import median

URL = sys.argv[1]
STRATEGY = sys.argv[2]
N = int(sys.argv[3])
KEY = os.environ['PSI_API_KEY']

api = (
    'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
    f'?url={urllib.parse.quote(URL, safe="")}'
    f'&strategy={STRATEGY}'
    '&category=performance'
)

print(f'URL:      {URL}')
print(f'Strategy: {STRATEGY}')
print(f'Runs:     {N}\n')

results = []
for i in range(1, N + 1):
    print(f'  run {i}...', end=' ', flush=True)
    req = urllib.request.Request(api, headers={'X-goog-api-key': KEY})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read())
    except Exception as e:
        print(f'ERR: {e}')
        continue
    dt = time.time() - t0
    if 'error' in d:
        print(f'API ERR: {d["error"].get("message", d["error"])}')
        continue
    audits = d['lighthouseResult']['audits']
    cat = d['lighthouseResult']['categories']['performance']
    r = {
        'score': round(cat['score'] * 100),
        'fcp': audits['first-contentful-paint']['numericValue'],
        'lcp': audits['largest-contentful-paint']['numericValue'],
        'tbt': audits['total-blocking-time']['numericValue'],
        'cls': audits['cumulative-layout-shift']['numericValue'],
        'si':  audits['speed-index']['numericValue'],
    }
    results.append(r)
    print(f'score {r["score"]}  LCP {r["lcp"]/1000:.1f}s  TBT {r["tbt"]:.0f}ms  ({dt:.1f}s)')

def fmt(m, v):
    if v is None: return 'n/a'
    if m == 'score': return f'{v}'
    if m == 'cls':   return f'{v:.3f}'
    return f'{v/1000:.2f}s' if v >= 100 else f'{v:.0f}ms'

if len(results) >= 2:
    print(f'\n══ Medians (n={len(results)}) ══')
    for m in ('score', 'fcp', 'lcp', 'tbt', 'cls', 'si'):
        print(f'  {m.upper():<5} {fmt(m, median([r[m] for r in results]))}')
PYEOF
