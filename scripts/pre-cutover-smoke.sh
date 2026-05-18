#!/usr/bin/env bash
# pre-cutover-smoke.sh — verify the P8 dev theme matches what's in git.
#
# Catches divergence between git HEAD (what was committed) and the actual
# Shopify theme files (what was pushed). The 2026-05-18 evening session
# hit this miss for assets/hairmnl-product.js — OC swarm staged it to git
# but the corresponding shopify theme push only included layout/theme.liquid,
# so the JS file landed in git but never on dev. Pre-cutover smoke would
# have caught the gap.
#
# Mechanism per check:
#   1. `shopify theme pull --only=<file>` to a temp dir
#   2. Grep for expected markers from a ticket's spec
#   3. Pass / fail report
#
# Each smoke check is named with its bd ticket id. Add new tickets to the
# CHECKS array below; the harness handles output formatting.
#
# Usage:
#   bash scripts/pre-cutover-smoke.sh                # run full suite
#   bash scripts/pre-cutover-smoke.sh ujg6.7         # run a single ticket
#   bash scripts/pre-cutover-smoke.sh --theme=N      # override theme id
#   bash scripts/pre-cutover-smoke.sh --verbose      # show all grep results
#   bash scripts/pre-cutover-smoke.sh --no-pull      # use existing /tmp/dev-smoke (faster re-runs)
#
# Exit codes:
#   0 = all checks pass
#   1 = one or more checks failed (see report)
#   2 = pull failed or invocation error
#
# Reference for which markers verify which ticket:
#   - os2-migration/smoke-results-2026-05-18.md
#   - each closed bd ticket's "## Static-content smoke test" notes section

set -uo pipefail

# Default to P8 dev theme; override with --theme=N
THEME_ID="141168312419"
PULL_DIR="/tmp/dev-smoke"
VERBOSE=0
SKIP_PULL=0
SELECTED=""

# Per-ticket checks. Each entry: TICKET|FILE|GREP_PATTERN|MIN_COUNT|DESCRIPTION
# MIN_COUNT is the minimum number of matches required. Use 0 to assert
# absence (e.g., for "no inline scripts").
CHECKS=(
  # ujg6.7 — font CLS overrides
  "ujg6.7|snippets/custom-fonts.liquid|ascent-override: 90.5%|1|Arial-matched ascent-override"
  "ujg6.7|snippets/custom-fonts.liquid|descent-override: 21.2%|1|Arial-matched descent-override"
  "ujg6.7|snippets/custom-fonts.liquid|line-gap-override: 3.3%|1|Arial-matched line-gap-override"
  "ujg6.7|snippets/custom-fonts.liquid|font-display: optional|4|font-display:optional on 4 accent weights (Mono/Bold/Black/Medium)"

  # ujg6.14 — hairmnl-custom.js per-template split (3 new files exist on dev)
  "ujg6.14|assets/hairmnl-common.js|// 7) cart-drawer-on-atc|1|common.js contains section 7"
  "ujg6.14|assets/hairmnl-common.js|// 8) lazy-render|1|common.js contains section 8 IO (added by ujg6.18)"
  "ujg6.14|assets/hairmnl-collection.js|// 1) sticky-filter-bar|1|collection.js contains section 1"
  "ujg6.14|assets/hairmnl-product.js|// 2) product-tabs-v1|1|product.js contains section 2 (CAUGHT MISSING 2026-05-18)"

  # 2i8b.19 — loader wiring in layout/theme.liquid
  "2i8b.19|layout/theme.liquid|hairmnl-common.js|1|hairmnl-common.js script tag wired"
  "2i8b.19|layout/theme.liquid|hairmnl-collection.js|1|hairmnl-collection.js script tag wired"
  "2i8b.19|layout/theme.liquid|hairmnl-product.js|1|hairmnl-product.js script tag wired"

  # 2i8b.18 — mobile menu-buttons CLS fix
  "2i8b.18|sections/menu-buttons.liquid|font-weight: var(---menu-btn-bold|2|font-weight in shared + mobile @media (expect 2)"
  "2i8b.18|sections/menu-buttons.liquid|text-transform: var(---menu-btn-caps|2|text-transform in shared + mobile @media (expect 2)"

  # fsaa — Reamaze defer guard
  "fsaa|layout/theme.liquid|KILL_SWITCH = false|1|Reamaze guard KILL_SWITCH"
  "fsaa|layout/theme.liquid|cdn.reamaze.com|1|BLOCKED array references cdn.reamaze.com"
  "fsaa|layout/theme.liquid|render 'reamaze-placeholder'|1|placeholder render call"
  "fsaa|snippets/reamaze-placeholder.liquid|id=\"reamaze-defer-placeholder\"|1|placeholder id matches guard references"

  # ujg6.16 — facet AJAX in collection.js
  "ujg6.16|assets/hairmnl-collection.js|FACET_FORM_SELECTOR|1|facet form selector const"
  "ujg6.16|assets/hairmnl-collection.js|history.pushState|1|history.pushState call"
  "ujg6.16|assets/hairmnl-collection.js|shopify:section:load|1|section:load event dispatch"

  # ujg6.18 — lazy-render on 3 sections (section-collection, brand-collection, related)
  "ujg6.18|sections/section-collection.liquid|request.design_mode|1|lazy-render conditional in section-collection"
  "ujg6.18|sections/section-collection.liquid|data-lazy-render|1|placeholder in section-collection"
  "ujg6.18|sections/brand-collection.liquid|request.design_mode|1|lazy-render conditional in brand-collection"
  "ujg6.18|sections/brand-collection.liquid|data-lazy-render|1|placeholder in brand-collection"
  "ujg6.18|sections/related.liquid|request.design_mode|1|lazy-render conditional in related"
  "ujg6.18|sections/related.liquid|data-lazy-render|1|placeholder in related"

  # ujg6.19 — font preloads + slideshow eager
  "ujg6.19|layout/theme.liquid|BasisGrotesquePro-Regular.woff2|1|Basis font preload"
  "ujg6.19|layout/theme.liquid|SelfModern.woff2|1|SelfModern font preload"
  "ujg6.19|sections/section-slideshow.liquid|forloop.first|1|slideshow first-slide eager:true gate"
  "ujg6.19|sections/section-slideshow.liquid|eager: hero_eager|2|eager passed to desktop + mobile hero renders"
)

# Add new checks above this line. Format: TICKET|FILE|GREP_PATTERN|MIN_COUNT|DESCRIPTION

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
for arg in "$@"; do
    case "$arg" in
        --theme=*)
            THEME_ID="${arg#*=}";;
        --verbose|-v)
            VERBOSE=1;;
        --no-pull)
            SKIP_PULL=1;;
        --help|-h)
            sed -n '2,30p' "$0"; exit 0;;
        -*)
            echo "✗ Unknown option: $arg" >&2; exit 2;;
        *)
            SELECTED="$arg";;
    esac
done

# ---------------------------------------------------------------------------
# Pull the dev theme files
# ---------------------------------------------------------------------------
if (( ! SKIP_PULL )); then
    # Build a unique --only list from CHECKS.
    # bash 3.2 (macOS default) doesn't support `declare -A`; use a
    # space-delimited string as a poor-man's set.
    SEEN_FILES=""
    PULL_ARGS=()
    for check in "${CHECKS[@]}"; do
        IFS='|' read -r ticket file pattern min desc <<<"$check"
        if [[ -n "$SELECTED" && "$ticket" != "$SELECTED" ]]; then continue; fi
        if [[ " $SEEN_FILES " != *" $file "* ]]; then
            SEEN_FILES="$SEEN_FILES $file"
            PULL_ARGS+=("--only=$file")
        fi
    done

    if (( ${#PULL_ARGS[@]} == 0 )); then
        echo "✗ No checks matched '$SELECTED'. Available tickets:" >&2
        printf '%s\n' "${CHECKS[@]}" | cut -d'|' -f1 | sort -u | sed 's/^/  /' >&2
        exit 2
    fi

    rm -rf "$PULL_DIR"
    mkdir -p "$PULL_DIR"

    echo "→ Pulling ${#PULL_ARGS[@]} files from dev theme $THEME_ID …" >&2
    if ! shopify theme pull --theme="$THEME_ID" --path="$PULL_DIR" "${PULL_ARGS[@]}" >/tmp/pre-cutover-pull.log 2>&1; then
        echo "✗ shopify theme pull failed. See /tmp/pre-cutover-pull.log" >&2
        tail -20 /tmp/pre-cutover-pull.log >&2
        exit 2
    fi
    echo "  ✓ pulled to $PULL_DIR" >&2
    echo "" >&2
fi

# ---------------------------------------------------------------------------
# Run the checks
# ---------------------------------------------------------------------------
TOTAL=0
PASSED=0
FAILED=0
# bash 3.2 compatible: track ticket→status via a newline-delimited string.
# Format per line: "TICKET STATUS". STATUS is FAIL (sticky once set) else PASS.
TICKET_STATUS_LINES=""
FAILURES=()

ticket_get_status() {
    local t="$1"
    # Get latest status for this ticket (last line wins)
    printf '%s\n' "$TICKET_STATUS_LINES" | awk -v t="$t" '$1==t {s=$2} END {print s}'
}
ticket_set_status() {
    local t="$1" s="$2"
    TICKET_STATUS_LINES="$TICKET_STATUS_LINES
$t $s"
}

for check in "${CHECKS[@]}"; do
    IFS='|' read -r ticket file pattern min desc <<<"$check"
    if [[ -n "$SELECTED" && "$ticket" != "$SELECTED" ]]; then continue; fi
    TOTAL=$((TOTAL+1))

    fpath="$PULL_DIR/$file"
    if [[ ! -f "$fpath" ]]; then
        FAILED=$((FAILED+1))
        ticket_set_status "$ticket" "FAIL"
        FAILURES+=("$ticket: FILE MISSING — $file (was the file pushed to dev?)")
        continue
    fi

    # Count matches (literal-string grep so users don't need to escape regex)
    count=$(grep -F -c -- "$pattern" "$fpath" 2>/dev/null || echo 0)
    count="${count:-0}"

    if (( count >= min )); then
        PASSED=$((PASSED+1))
        if (( VERBOSE )); then
            echo "  ✓ $ticket | $file | '$pattern' = $count (expect ≥$min) — $desc" >&2
        fi
        # Mark ticket PASS only if it isn't already FAIL (FAIL is sticky)
        if [[ "$(ticket_get_status "$ticket")" != "FAIL" ]]; then
            ticket_set_status "$ticket" "PASS"
        fi
    else
        FAILED=$((FAILED+1))
        ticket_set_status "$ticket" "FAIL"
        FAILURES+=("$ticket: pattern '$pattern' found $count times in $file (expected ≥$min) — $desc")
    fi
done

# ---------------------------------------------------------------------------
# Validate the ticket filter actually matched something
# ---------------------------------------------------------------------------
if (( TOTAL == 0 )) && [[ -n "$SELECTED" ]]; then
    echo "✗ No checks matched '$SELECTED'. Available tickets:" >&2
    printf '%s\n' "${CHECKS[@]}" | cut -d'|' -f1 | sort -u | sed 's/^/  /' >&2
    exit 2
fi

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
echo "════════════════════════════════════════════════════════════════════════" >&2
echo "PRE-CUTOVER SMOKE REPORT — theme $THEME_ID" >&2
echo "════════════════════════════════════════════════════════════════════════" >&2
echo "" >&2

# Per-ticket roll-up (sorted). Compute final per-ticket status by taking
# the LAST line for each ticket in TICKET_STATUS_LINES.
TICKET_FINAL=$(printf '%s\n' "$TICKET_STATUS_LINES" | awk 'NF==2 {st[$1]=$2} END {for (t in st) print t, st[t]}' | sort)
while IFS=' ' read -r ticket status; do
    [[ -z "$ticket" ]] && continue
    if [[ "$status" == "PASS" ]]; then
        echo "  ✓ $ticket" >&2
    else
        echo "  ✗ $ticket" >&2
    fi
done <<< "$TICKET_FINAL"

echo "" >&2
echo "$PASSED / $TOTAL individual checks passed" >&2

if (( FAILED > 0 )); then
    echo "" >&2
    echo "FAILURES:" >&2
    for f in "${FAILURES[@]}"; do
        echo "  ✗ $f" >&2
    done
    echo "" >&2
    echo "Common causes:" >&2
    echo "  - File in git but not pushed to dev: shopify theme push --theme=$THEME_ID --only=<file>" >&2
    echo "  - Marker pattern changed: update CHECKS array in this script" >&2
    echo "  - Dev theme has stale content: re-pull and re-verify" >&2
    exit 1
fi

echo "" >&2
echo "✓ All $TOTAL checks passed. Dev theme $THEME_ID is in sync with git state for verified tickets." >&2
echo "" >&2
echo "Remaining for operator browser smoke:" >&2
echo "  - Visual regression (lazy-render swap, font-swap)" >&2
echo "  - Interactive flow (Reamaze placeholder click, facet AJAX, cart drawer)" >&2
echo "  - DevTools Network: confirm cdn.reamaze.com NOT loaded on first paint" >&2
echo "  - TAE side-effects (Klaviyo signup form, Judge.me badges)" >&2
exit 0
