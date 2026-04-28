#!/usr/bin/env bash
# check-perf-budgets.sh — Pre-push perf-budget guard for HairMNL theme.
#
# Why: prevents accidental regressions where someone (including future me)
# adds a heavy library or balloons critical CSS without realizing it.
# Today's vendor.js is 100KB raw / 29KB gzipped — the budget is set with
# headroom so the script doesn't fire on routine work, only on >10% growth.
#
# Usage: ./scripts/check-perf-budgets.sh
#   exits 0 if all budgets within tolerance, 1 if any exceed.
#
# Run manually before any non-trivial push, OR wire as a git pre-push hook:
#   ln -s ../../scripts/check-perf-budgets.sh .git/hooks/pre-push
#
# Override individual budgets with env vars if a specific change justifies it:
#   BUDGET_VENDOR_JS_GZIP=35000 ./scripts/check-perf-budgets.sh
#
# Each budget is set ~10-15% above current size, so this guard is for genuine
# regressions, not nit-pick alerts.

set -uo pipefail

# Tolerances (gzipped bytes). Update only when intentionally crossing.
: "${BUDGET_VENDOR_JS_GZIP:=33000}"        # current ~29368
: "${BUDGET_THEME_JS_GZIP:=75000}"         # measured fresh, see check below
: "${BUDGET_THEME_CSS_GZIP:=110000}"       # measured fresh
: "${BUDGET_CUSTOM_THEME_CSS_GZIP:=20000}" # measured fresh
: "${BUDGET_CRITICAL_CSS_RAW:=45000}"      # current 39927 inline (NOT gzipped — inline counts raw)
: "${BUDGET_PRECONNECT_COUNT:=4}"          # Lighthouse warns above 4
: "${BUDGET_THEME_LIQUID_RAW:=80000}"      # head bloat guard

GREEN=$'\033[32m'
YELLOW=$'\033[33m'
RED=$'\033[31m'
RESET=$'\033[0m'

failures=0
warnings=0

check() {
  local name="$1"
  local actual="$2"
  local budget="$3"
  local unit="$4"
  if [[ "$actual" -gt "$budget" ]]; then
    pct=$(( (actual - budget) * 100 / budget ))
    printf '%s%s%s  %s = %s %s  (budget %s %s, +%s%% over)\n' \
      "$RED" "FAIL" "$RESET" "$name" "$actual" "$unit" "$budget" "$unit" "$pct"
    failures=$((failures + 1))
  elif [[ "$actual" -gt $(( budget * 90 / 100 )) ]]; then
    pct=$(( actual * 100 / budget ))
    printf '%s%s%s  %s = %s %s  (budget %s %s, %s%% used)\n' \
      "$YELLOW" "WARN" "$RESET" "$name" "$actual" "$unit" "$budget" "$unit" "$pct"
    warnings=$((warnings + 1))
  else
    printf '%s%s%s  %s = %s %s  (budget %s %s)\n' \
      "$GREEN" "OK  " "$RESET" "$name" "$actual" "$unit" "$budget" "$unit"
  fi
}

gzip_size() {
  if [[ -f "$1" ]]; then gzip -c "$1" | wc -c | tr -d ' '; else echo 0; fi
}

raw_size() {
  if [[ -f "$1" ]]; then wc -c < "$1" | tr -d ' '; else echo 0; fi
}

cd "$(dirname "$0")/.."

echo "=== Performance budgets ==="
check "vendor.js (gzip)"        "$(gzip_size assets/vendor.js)"        "$BUDGET_VENDOR_JS_GZIP"        bytes
check "theme.js (gzip)"         "$(gzip_size assets/theme.js)"         "$BUDGET_THEME_JS_GZIP"         bytes
check "theme.css (gzip)"        "$(gzip_size assets/theme.css)"        "$BUDGET_THEME_CSS_GZIP"        bytes
check "custom-theme.css (gzip)" "$(gzip_size assets/custom-theme.css)" "$BUDGET_CUSTOM_THEME_CSS_GZIP" bytes
check "critical-css.liquid (raw, inline-counts)" "$(raw_size snippets/critical-css.liquid)" "$BUDGET_CRITICAL_CSS_RAW" bytes
check "theme.liquid (raw, head bloat guard)"      "$(raw_size layout/theme.liquid)"          "$BUDGET_THEME_LIQUID_RAW" bytes

# Lighthouse warns when >4 preconnects in <head>. Count from theme.liquid.
preconnect_count=$(grep -cE 'rel="preconnect"' layout/theme.liquid 2>/dev/null || echo 0)
check "preconnects in theme.liquid"  "$preconnect_count" "$BUDGET_PRECONNECT_COUNT" hints

echo
if [[ "$failures" -gt 0 ]]; then
  printf '%sBudget exceeded: %d failures, %d warnings.%s Override with env vars if intentional.\n' \
    "$RED" "$failures" "$warnings" "$RESET"
  exit 1
elif [[ "$warnings" -gt 0 ]]; then
  printf '%sWithin budget: %d warnings (>90%%).%s Worth a look before adding more.\n' \
    "$YELLOW" "$warnings" "$RESET"
  exit 0
else
  printf '%sAll budgets healthy.%s\n' "$GREEN" "$RESET"
  exit 0
fi
