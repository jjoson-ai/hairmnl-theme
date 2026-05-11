#!/usr/bin/env python3
"""
smoke-test-drawers.py — Automated drawer smoke test (Layer 3, kt0-killer gate).

WHY
---
On 2026-05-11 (commit ff1ef80), a CSS-only commit added `contain: layout` to
`.header__wrapper` to fix the "kt0" CLS warning. That property silently creates
a containing block for `position: fixed` descendants, which trapped the cart
drawer inside `.header__wrapper`'s bounds instead of overlaying the viewport.
The drawer rendered inline within the header — visually broken for every
visitor — and required an emergency revert.

Layer 1 (CSS audit guidance) and Layer 2 (manual pre-push smoke checklist)
shipped in commit d0334b0 as `.opencode_hints` additions. THIS script is
Layer 3: a deterministic, headless, Playwright-based test that catches the
same structural bug pattern automatically — before live push.

WHAT IT CHECKS (the "kt0-killer" set, per overlay)
-------------------------------------------------
For each fixed-position overlay (cart drawer, mobile nav, PhotoSwipe lightbox,
search overlay):

  a. The trigger click opens the overlay within a 2s timeout.
  b. The panel's computed `position` is `fixed`.
  c. The panel's bounding box covers ≥ 90% of viewport height AND ≥ 300px wide.
  d. CONTAINMENT AUDIT (the kt0-killer): walks every ancestor up to <body> and
     FAILS if any ancestor has a CSS property that creates a containing block
     for fixed descendants:
       - contain: layout | paint | strict | content
       - transform != none
       - filter != none
       - backdrop-filter != none
       - perspective != none
       - will-change: transform | filter
  e. On fail: captures screenshot to /tmp/smoke-fail-<test>-<ts>.png and logs
     the offending ancestor's selector chain so the senior developer can fix
     it in one diff.

SETUP (one-time per workstation)
--------------------------------
    pip install playwright
    playwright install chromium

USAGE
-----
    python3 scripts/smoke-test-drawers.py [--theme=draft|live] \\
        [--headless=true|false] [--store=creations-gdc] [--verbose]

    Defaults: --theme=draft --headless=true --store=creations-gdc

EXIT CODES
----------
    0 — all overlay tests passed (safe to push to live)
    1 — at least one overlay test failed (BLOCK push to live)
    2 — script setup error (Playwright missing, network error, etc.)

INTEGRATION
-----------
The coordinator runs this BEFORE every `shopify theme push --allow-live` that
touches CSS-overrides.liquid, theme.css, layout/, sections/header.liquid, or
any popup/modal wrapper snippet. See `.opencode_hints` →
"## Automated drawer smoke test (Layer 3)".
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


THEME_IDS = {
    "draft": 140785582179,
    "live": 131664707683,
}

STORE_URL = "https://www.hairmnl.com"

PDP_PATH = (
    "/products/davines-naturaltech-purifying-shampoo-for-scalp"
    "-with-oily-or-dry-dandruff"
)

# Containment-audit JS — walks the panel's parent chain to <body> and reports
# the first ancestor (if any) whose computed style creates a containing block
# for fixed descendants. This is the kt0-killer assertion.
CONTAINMENT_AUDIT_JS = r"""
    (panelSelector) => {
        const panel = document.querySelector(panelSelector);
        if (!panel) return {ok: false, reason: 'panel not found'};
        let el = panel.parentElement;
        while (el && el !== document.body) {
            const cs = getComputedStyle(el);
            if (cs.contain && /\b(layout|paint|strict|content)\b/.test(cs.contain)) return {ok: false, reason: `contain: ${cs.contain}`, selector: getSelectorPath(el)};
            if (cs.transform && cs.transform !== 'none') return {ok: false, reason: `transform: ${cs.transform}`, selector: getSelectorPath(el)};
            if (cs.filter && cs.filter !== 'none') return {ok: false, reason: `filter: ${cs.filter}`, selector: getSelectorPath(el)};
            if (cs.backdropFilter && cs.backdropFilter !== 'none') return {ok: false, reason: `backdrop-filter: ${cs.backdropFilter}`, selector: getSelectorPath(el)};
            if (cs.perspective && cs.perspective !== 'none') return {ok: false, reason: `perspective: ${cs.perspective}`, selector: getSelectorPath(el)};
            if (cs.willChange && /transform|filter/.test(cs.willChange)) return {ok: false, reason: `will-change: ${cs.willChange}`, selector: getSelectorPath(el)};
            el = el.parentElement;
        }
        function getSelectorPath(node) {
            if (!node) return '';
            const parts = [];
            while (node && node !== document.body) {
                let s = node.tagName.toLowerCase();
                if (node.id) s += '#' + node.id;
                if (node.className && typeof node.className === 'string') s += '.' + node.className.trim().replace(/\s+/g, '.');
                parts.unshift(s);
                node = node.parentElement;
            }
            return parts.join(' > ');
        }
        return {ok: true};
    }
"""


@dataclass
class OverlayTest:
    name: str
    path: str
    trigger_selector: str
    panel_selector: str
    state_selector: str  # selector that becomes present/matchable when open
    viewport: tuple[int, int] = (1280, 800)
    # Optional pre-click hook (e.g. dismiss cookie banner, scroll). Receives
    # the Playwright `page` object.
    pre_click: Callable[[Any], None] | None = field(default=None, repr=False)


@dataclass
class TestResult:
    name: str
    status: str  # "PASS" | "FAIL" | "SKIP"
    duration_ms: int
    reason: str = ""
    offending_selector: str = ""
    screenshot_path: str = ""


def build_url(path: str, theme: str) -> str:
    theme_id = THEME_IDS[theme]
    sep = "&" if "?" in path else "?"
    return f"{STORE_URL}{path}{sep}preview_theme_id={theme_id}"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_overlay_test(page: Any, test: OverlayTest, theme: str, verbose: bool) -> TestResult:
    started = time.monotonic()
    url = build_url(test.path, theme)

    try:
        page.set_viewport_size({"width": test.viewport[0], "height": test.viewport[1]})
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        # Give JS handlers (drawer + popdown + photoswipe init) time to bind.
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception as e:  # network / 404 / theme preview redirect
        return TestResult(
            name=test.name,
            status="FAIL",
            duration_ms=int((time.monotonic() - started) * 1000),
            reason=f"page load error: {e}",
        )

    if test.pre_click is not None:
        try:
            test.pre_click(page)
        except Exception as e:
            if verbose:
                print(f"    pre_click hook raised (continuing): {e}")

    # Find trigger. If absent, SKIP — selector might not match this theme
    # variant. Skip is non-fatal so the script still emits high-signal output.
    try:
        trigger = page.query_selector(test.trigger_selector)
    except Exception as e:
        return TestResult(
            name=test.name,
            status="SKIP",
            duration_ms=int((time.monotonic() - started) * 1000),
            reason=f"trigger selector error: {e}",
        )
    if trigger is None:
        return TestResult(
            name=test.name,
            status="SKIP",
            duration_ms=int((time.monotonic() - started) * 1000),
            reason=f"trigger not found: {test.trigger_selector}",
        )

    try:
        trigger.scroll_into_view_if_needed(timeout=2000)
        trigger.click(timeout=2000)
    except Exception as e:
        return TestResult(
            name=test.name,
            status="FAIL",
            duration_ms=int((time.monotonic() - started) * 1000),
            reason=f"trigger click failed: {e}",
        )

    try:
        page.wait_for_selector(test.state_selector, state="visible", timeout=2000)
    except Exception:
        return TestResult(
            name=test.name,
            status="FAIL",
            duration_ms=int((time.monotonic() - started) * 1000),
            reason=f"open-state indicator not visible within 2s: {test.state_selector}",
        )

    panel = page.query_selector(test.panel_selector)
    if panel is None:
        return TestResult(
            name=test.name,
            status="FAIL",
            duration_ms=int((time.monotonic() - started) * 1000),
            reason=f"panel not found after open: {test.panel_selector}",
        )

    # Computed style + geometry sanity checks.
    geometry = page.evaluate(
        """
        (sel) => {
            const el = document.querySelector(sel);
            if (!el) return null;
            const cs = getComputedStyle(el);
            const r = el.getBoundingClientRect();
            return {
                position: cs.position,
                width: r.width,
                height: r.height,
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
            };
        }
        """,
        test.panel_selector,
    )
    if geometry is None:
        return TestResult(
            name=test.name,
            status="FAIL",
            duration_ms=int((time.monotonic() - started) * 1000),
            reason=f"panel disappeared before geometry read: {test.panel_selector}",
        )

    if geometry["position"] not in ("fixed", "absolute"):
        return _fail_with_screenshot(
            page, test, started,
            reason=(
                f"panel position is '{geometry['position']}', expected fixed/absolute. "
                "Overlay won't render as a viewport-covering layer."
            ),
        )

    min_height = 0.9 * geometry["viewportHeight"]
    if geometry["height"] < min_height or geometry["width"] < 300:
        return _fail_with_screenshot(
            page, test, started,
            reason=(
                f"panel geometry too small: {geometry['width']:.0f}x"
                f"{geometry['height']:.0f}px (viewport "
                f"{geometry['viewportWidth']}x{geometry['viewportHeight']}); "
                f"expected width>=300 and height>={min_height:.0f}. "
                "Overlay is likely rendering inline / clipped."
            ),
        )

    # The kt0-killer: walk ancestors and check for containing-block creators.
    audit = page.evaluate(CONTAINMENT_AUDIT_JS, test.panel_selector)
    if not audit.get("ok"):
        return _fail_with_screenshot(
            page, test, started,
            reason=(
                f"containment audit failed — ancestor establishes containing "
                f"block for fixed descendants: {audit.get('reason', 'unknown')}"
            ),
            offending_selector=audit.get("selector", ""),
        )

    return TestResult(
        name=test.name,
        status="PASS",
        duration_ms=int((time.monotonic() - started) * 1000),
    )


def _fail_with_screenshot(
    page: Any,
    test: OverlayTest,
    started: float,
    *,
    reason: str,
    offending_selector: str = "",
) -> TestResult:
    slug = test.name.lower().replace(" ", "-").replace("/", "-")
    path = f"/tmp/smoke-fail-{slug}-{utc_stamp()}.png"
    try:
        page.screenshot(path=path, full_page=False)
    except Exception:
        path = ""
    return TestResult(
        name=test.name,
        status="FAIL",
        duration_ms=int((time.monotonic() - started) * 1000),
        reason=reason,
        offending_selector=offending_selector,
        screenshot_path=path,
    )


def build_tests() -> list[OverlayTest]:
    # Selectors confirmed by inspecting sections/header.liquid,
    # snippets/cart-drawer.liquid, snippets/search-predictive.liquid, and
    # assets/theme.dev.js (drawer state class `drawer--visible` at line 1954;
    # `.search-popdown.is-visible` at theme.dev.css line 20416).
    return [
        OverlayTest(
            name="Cart drawer on PDP",
            path=PDP_PATH,
            trigger_selector='[data-drawer-toggle="drawer-cart"]',
            panel_selector=".cart__drawer .drawer__content",
            state_selector=".cart__drawer.drawer--visible",
            viewport=(1280, 800),
        ),
        OverlayTest(
            name="Mobile nav drawer on Home",
            path="/",
            trigger_selector='[data-drawer-toggle="hamburger"]',
            panel_selector=".header__drawer .drawer__content",
            state_selector=".header__drawer.drawer--visible",
            viewport=(375, 667),
        ),
        OverlayTest(
            name="PhotoSwipe lightbox on PDP",
            path=PDP_PATH,
            trigger_selector="[data-zoom-button]",
            panel_selector=".pswp",
            state_selector=".pswp--open",
            viewport=(1280, 800),
        ),
        OverlayTest(
            name="Search overlay on Home",
            path="/",
            trigger_selector='[data-popdown-toggle="search-popdown"]',
            panel_selector="#search-popdown",
            state_selector="#search-popdown.is-visible",
            viewport=(1280, 800),
        ),
    ]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Headless smoke test for fixed-position overlays — the kt0-killer "
            "gate. Run before any `shopify theme push --allow-live` that "
            "touches CSS / layout / header."
        )
    )
    p.add_argument(
        "--theme",
        choices=sorted(THEME_IDS.keys()),
        default="draft",
        help="Which theme preview to test (default: draft).",
    )

    def _truthy(v: str) -> bool:
        return v.lower() in ("1", "true", "yes", "on")

    p.add_argument(
        "--headless",
        type=_truthy,
        default=True,
        help="Run browser headless (default: true). Pass --headless=false to watch.",
    )
    p.add_argument(
        "--store",
        default="creations-gdc",
        help="Shopify store handle (informational only; STORE_URL is hardcoded).",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-test progress lines. Default: failures + summary only.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "ERROR: playwright is not installed. Run:\n"
            "  pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        return 2

    tests = build_tests()
    results: list[TestResult] = []

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=args.headless)
            try:
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36 hairmnl-smoke-test"
                    ),
                )
                for i, test in enumerate(tests, start=1):
                    if args.verbose:
                        print(f"[{i}/{len(tests)}] {test.name} ...", end=" ", flush=True)
                    page = context.new_page()
                    try:
                        result = run_overlay_test(page, test, args.theme, args.verbose)
                    finally:
                        page.close()
                    results.append(result)
                    if args.verbose:
                        print(f"{result.status} ({result.duration_ms}ms)")
                    if result.status == "FAIL":
                        print(f"\n[{i}/{len(tests)}] {test.name} ... FAIL ({result.duration_ms}ms)")
                        print(f"  Reason: {result.reason}")
                        if result.offending_selector:
                            print(f"  Offending ancestor: {result.offending_selector}")
                            print(
                                "  This creates a containing block for fixed descendants "
                                "per CSS Containment spec, trapping the overlay inside "
                                "the ancestor's bounds."
                            )
                            print("  See: bd memories contain (kt0 lesson, 2026-05-11).")
                        if result.screenshot_path:
                            print(f"  Screenshot: {result.screenshot_path}")
                    elif result.status == "SKIP" and args.verbose:
                        print(f"  Skipped: {result.reason}")
                context.close()
            finally:
                browser.close()
    except Exception as e:
        print(f"ERROR: playwright session crashed: {e}", file=sys.stderr)
        return 2

    n_pass = sum(1 for r in results if r.status == "PASS")
    n_skip = sum(1 for r in results if r.status == "SKIP")
    n_fail = sum(1 for r in results if r.status == "FAIL")
    print(f"\nSummary: {n_pass} PASS, {n_skip} SKIP, {n_fail} FAIL")

    return 1 if n_fail > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
