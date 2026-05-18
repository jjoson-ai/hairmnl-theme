#!/usr/bin/env bash
# smoke-against-dev-server.sh — orchestrate `shopify theme dev` + Playwright suite.
#
# Why this exists
# ---------------
# The Shopify preview URL (`?preview_theme_id=N` on the canonical domain)
# strips the query param on the canonical-domain redirect and serves LIVE
# content (per the 2i8b.17 finding). Without authenticated cookies, smoke
# tests against the preview URL hit LIVE instead of the dev theme.
#
# Workaround: `shopify theme dev` starts a local proxy that serves the
# dev theme directly from http://127.0.0.1:9292, bypassing the redirect
# entirely. Tests run against the local proxy and exercise the actual
# dev theme bytes.
#
# Known limitation (2026-05-19)
# -----------------------------
# `shopify theme dev` syncs LOCAL files to a development theme on Shopify
# before proxying. On the HairMNL codebase, this fails with "Failed to
# Upload Theme Files" errors on ~30+ legacy per-brand collection liquid
# files (e.g., collection-absolutrepair.liquid, collection-blondabsolu.liquid,
# etc.) that are still in the working tree but have upload issues with
# the current Shopify CLI version. The proxy then serves a 500 error
# page instead of the theme.
#
# Workaround options (in order of preference):
#   1. Use the storageState auth flow instead (see README "Quick start")
#   2. Add a .shopifyignore file excluding the problematic files (TODO)
#   3. Run dev-server against a freshly-pulled clean copy of the dev
#      theme (TODO: needs --path argument refinement)
#
# Until one of those workarounds lands, this wrapper is provided as
# infrastructure but the auth-flow path in the README is the canonical
# pre-cutover testing approach.
#
# Usage
# -----
#   ./bin/smoke-against-dev-server.sh                    # full suite
#   ./bin/smoke-against-dev-server.sh smoke-03           # one suite
#   ./bin/smoke-against-dev-server.sh --grep="Reamaze"   # filter
#   THEME_ID=141168312419 ./bin/smoke-against-dev-server.sh
#   STORE=my-store.myshopify.com ./bin/smoke-against-dev-server.sh
#
# All extra args after the script name are forwarded verbatim to
# `npm test`.
#
# Prerequisites
# -------------
# - Shopify CLI installed + authenticated (`shopify version` works,
#   `shopify theme list` shows themes — you've used this CLI all session
#   already, so it's already set up)
# - Playwright installed: `npm install` (run once in scripts/smoke-tests/)
# - Browsers installed: `npm run install-browsers`
#
# Exit codes
# ----------
#   0   suite passed
#   1   suite failed (one or more tests)
#   2   dev server failed to start within timeout
#   3   missing dependencies

set -euo pipefail

STORE="${STORE:-creations-gdc.myshopify.com}"
THEME_ID="${THEME_ID:-141168312419}"
PORT="${PORT:-9292}"
HOST="${HOST:-127.0.0.1}"
READY_TIMEOUT="${READY_TIMEOUT:-90}"   # seconds to wait for proxy to come up

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SMOKE_DIR="$REPO_ROOT/scripts/smoke-tests"
LOG_FILE="${LOG_FILE:-/tmp/shopify-theme-dev-$$.log}"

# --- dependency checks -------------------------------------------------------

if ! command -v shopify >/dev/null 2>&1; then
    echo "✗ shopify CLI not found in PATH. Install via: npm install -g @shopify/cli@latest" >&2
    exit 3
fi

if [[ ! -f "$SMOKE_DIR/node_modules/.package-lock.json" ]]; then
    echo "✗ Playwright deps not installed. Run: cd scripts/smoke-tests && npm install" >&2
    exit 3
fi

# --- start dev server in background ------------------------------------------

echo "→ Starting shopify theme dev proxy …" >&2
echo "    store:    $STORE" >&2
echo "    theme:    $THEME_ID" >&2
echo "    port:     $PORT" >&2
echo "    log:      $LOG_FILE" >&2

# Start in background; pipe both stdout + stderr to log file so we can grep
# for ready signal and surface errors on failure.
(
    cd "$REPO_ROOT"
    shopify theme dev \
        --theme="$THEME_ID" \
        --store="$STORE" \
        --port="$PORT" \
        --host="$HOST" \
        --live-reload=off \
        --no-color \
        --notify=/dev/null \
        --error-overlay=silent \
        </dev/null >"$LOG_FILE" 2>&1
) &
SERVER_PID=$!

# Trap to ensure we always tear down the dev server, even on failures
cleanup() {
    if kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "" >&2
        echo "→ Stopping shopify theme dev (pid=$SERVER_PID) …" >&2
        kill "$SERVER_PID" 2>/dev/null || true
        # Give it a moment to clean up gracefully
        sleep 2
        kill -9 "$SERVER_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

# --- wait for proxy to be ready ---------------------------------------------

URL="http://${HOST}:${PORT}/"
echo "→ Waiting for $URL to come up (max ${READY_TIMEOUT}s) …" >&2

elapsed=0
while (( elapsed < READY_TIMEOUT )); do
    # Check if process died
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "" >&2
        echo "✗ shopify theme dev exited prematurely. Last 30 lines of log:" >&2
        tail -30 "$LOG_FILE" >&2 || true
        exit 2
    fi

    # Probe the endpoint
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "$URL" 2>/dev/null || echo "000")
    if [[ "$status" =~ ^[23] ]]; then
        echo "  ✓ proxy responding ($status) after ${elapsed}s" >&2
        break
    fi

    sleep 2
    elapsed=$((elapsed + 2))
done

if (( elapsed >= READY_TIMEOUT )); then
    echo "" >&2
    echo "✗ Timed out waiting for proxy. Last 30 lines of log:" >&2
    tail -30 "$LOG_FILE" >&2 || true
    exit 2
fi

# --- run the smoke suite ----------------------------------------------------

echo "" >&2
echo "→ Running smoke suite against $URL …" >&2
echo "" >&2

cd "$SMOKE_DIR"

# In dev-server mode, no auth needed + no preview_theme_id query param.
# The proxy serves the dev theme directly.
SUITE_EXIT=0
BASE_URL="$URL" PREVIEW_THEME_ID="" npm test -- "$@" || SUITE_EXIT=$?

# --- summary ----------------------------------------------------------------

echo "" >&2
if (( SUITE_EXIT == 0 )); then
    echo "✓ Smoke suite passed against dev theme $THEME_ID via local proxy." >&2
else
    echo "✗ Smoke suite failed (exit $SUITE_EXIT). Review the HTML report:" >&2
    echo "    cd scripts/smoke-tests && npm run report" >&2
fi

# Cleanup happens via trap

exit $SUITE_EXIT
