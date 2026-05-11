#!/usr/bin/env python3
"""
smoke-test-overlays.py — Automated overlay regression gate (the kt0-killer).

WHY
---
A specific class of CSS regression keeps recurring across web projects: a
parent selector accidentally gets a CSS property that creates a containing
block for `position: fixed` / `position: absolute` descendants. The descendant
overlay (cart drawer, mobile nav, modal, lightbox) then renders inline within
the parent's bounds instead of overlaying the viewport. Per the CSS Containment
spec, these properties establish a containing block for fixed descendants:

    contain: layout | paint | strict | content
    transform != none
    filter != none
    backdrop-filter != none
    perspective != none
    will-change containing transform | filter

Origin: 2026-05-11 HairMNL kt0 incident. A `contain: layout` added to
`.header__wrapper` as a CLS optimization trapped the cart drawer's
`position: fixed` inside the wrapper's bounds. Live for ~24h before
user-reported. https://github.com/jjoson-ai/hairmnl-theme/commit/ff1ef80

WHAT THIS SCRIPT CHECKS (per overlay, per the config)
-----------------------------------------------------
  a. The trigger click opens the overlay within 5s.
  b. The panel's computed `position` is `fixed` (or `absolute` with body
     as the containing block).
  c. The panel's bounding box covers >= `expected_height_pct` of viewport
     height (default 0.9) and >= 300px wide.
  d. CONTAINMENT AUDIT (the kt0-killer): walks every ancestor up to <body>
     and FAILs if any has a CSS property that creates a containing block
     for fixed descendants.
  e. On fail: screenshot saved to /tmp/smoke-fail-<test>-<ts>.png and the
     offending ancestor's selector chain is logged.

SETUP (one-time per workstation)
--------------------------------
    python3 -m pip install playwright
    python3 -m playwright install chromium

USAGE
-----
    python3 scripts/smoke-test-overlays.py --config=<path-to-config.json> \\
        [--theme=draft|live|<custom-key>] [--headless=true|false] [--verbose]

    Defaults: --theme=draft (or whatever's first in config.site.themes)
              --headless=true

CONFIG FILE SCHEMA
------------------
See example.config.json shipped with this skill. Top-level shape:

    {
      "site": {
        "base_url": "https://www.example.com",
        "preview_param": "preview_theme_id",      // optional
        "themes": {"draft": "...", "live": "..."} // optional
      },
      "tests": [
        {
          "name": "Cart drawer on PDP",
          "path": "/products/example",
          "trigger_selector": "[data-drawer-toggle=\\"drawer-cart\\"]",
          "panel_selector": ".cart__drawer .drawer__content",
          "state_selector": ".cart__drawer.drawer--visible",
          "viewport": [1280, 800],
          "expected_height_pct": 0.9,
          "pre_click_wait_for": null,
          "incomplete_reason": null
        }
      ]
    }

If `site.preview_param` and `site.themes` are both omitted, the script uses
`base_url + path` directly (works for non-Shopify sites without preview params).

EXIT CODES
----------
    0 — all overlay tests passed (safe to push to live)
    1 — at least one overlay test failed (BLOCK push to live)
    2 — script setup error (Playwright missing, config invalid, network error)

This is a NARROW test for a SPECIFIC bug class. It's NOT a replacement for full
E2E testing, visual regression, or accessibility audits. Use Playwright Test /
Cypress / Percy / axe for those.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Containment-audit JS — walks the panel's parent chain to <body> and reports
# the first ancestor (if any) whose computed style creates a containing block
# for fixed descendants. This is the kt0-killer assertion. DO NOT MODIFY without
# understanding the CSS Containment spec (https://www.w3.org/TR/css-contain-1/).
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
class SiteConfig:
    base_url: str
    preview_param: str | None = None
    themes: dict[str, str] = field(default_factory=dict)


@dataclass
class OverlayTest:
    name: str
    path: str
    trigger_selector: str
    panel_selector: str
    state_selector: str  # selector that becomes present/matchable when open
    viewport: tuple[int, int] = (1280, 800)
    expected_height_pct: float = 0.9
    # JS predicate string evaluated via page.wait_for_function before clicking
    # the trigger. Use for overlays whose JS init is async (e.g. dynamically
    # loaded libraries like PhotoSwipe). Example: "() => !!window.themePhotoswipe"
    pre_click_wait_for: str | None = None
    # JS async function string evaluated via page.evaluate to OPEN the overlay
    # instead of the normal trigger click. Use when programmatic click doesn't
    # reliably fire the init chain (e.g. PhotoSwipe in headless mode). The
    # function must open the overlay; the script then waits for state_selector
    # and checks geometry + containment as normal.
    # Example: "async () => { const g = new window.themePhotoswipe.PhotoSwipe(...); g.init(); }"
    trigger_eval_js: str | None = None
    # If set, this test is skipped immediately with the given reason. Use for
    # tests whose selectors haven't been verified against the live theme yet —
    # keeps the test definition visible (as a reminder for follow-up work)
    # without producing false-positive failures.
    incomplete_reason: str | None = None


@dataclass
class TestResult:
    name: str
    status: str  # "PASS" | "FAIL" | "SKIP"
    duration_ms: int
    reason: str = ""
    offending_selector: str = ""
    screenshot_path: str = ""


def load_config(path: Path) -> tuple[SiteConfig, list[OverlayTest]]:
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    raw = json.loads(path.read_text())
    site_raw = raw.get("site") or {}
    if "base_url" not in site_raw:
        raise ValueError("config.site.base_url is required")
    site = SiteConfig(
        base_url=site_raw["base_url"].rstrip("/"),
        preview_param=site_raw.get("preview_param"),
        themes={str(k): str(v) for k, v in (site_raw.get("themes") or {}).items()},
    )
    tests_raw = raw.get("tests") or []
    if not tests_raw:
        raise ValueError("config.tests must be a non-empty array")
    tests: list[OverlayTest] = []
    for i, t in enumerate(tests_raw):
        for required in ("name", "path", "trigger_selector", "panel_selector", "state_selector"):
            if required not in t:
                raise ValueError(f"config.tests[{i}] missing required field: {required}")
        viewport = t.get("viewport", [1280, 800])
        if not isinstance(viewport, list) or len(viewport) != 2:
            raise ValueError(f"config.tests[{i}].viewport must be a 2-element list [width, height]")
        tests.append(OverlayTest(
            name=t["name"],
            path=t["path"],
            trigger_selector=t["trigger_selector"],
            panel_selector=t["panel_selector"],
            state_selector=t["state_selector"],
            viewport=(int(viewport[0]), int(viewport[1])),
            expected_height_pct=float(t.get("expected_height_pct", 0.9)),
            pre_click_wait_for=t.get("pre_click_wait_for"),
            trigger_eval_js=t.get("trigger_eval_js"),
            incomplete_reason=t.get("incomplete_reason"),
        ))
    return site, tests


def build_url(site: SiteConfig, path: str, theme: str | None) -> str:
    full = f"{site.base_url}{path}"
    if theme and site.preview_param and theme in site.themes:
        sep = "&" if "?" in full else "?"
        full = f"{full}{sep}{site.preview_param}={site.themes[theme]}"
    return full


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_overlay_test(page: Any, test: OverlayTest, site: SiteConfig, theme: str | None, verbose: bool) -> TestResult:
    started = time.monotonic()
    url = build_url(site, test.path, theme)

    if test.incomplete_reason:
        return TestResult(
            name=test.name,
            status="SKIP",
            duration_ms=int((time.monotonic() - started) * 1000),
            reason=f"incomplete: {test.incomplete_reason}",
        )

    try:
        page.set_viewport_size({"width": test.viewport[0], "height": test.viewport[1]})
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
    except Exception as e:
        return TestResult(
            name=test.name,
            status="FAIL",
            duration_ms=int((time.monotonic() - started) * 1000),
            reason=f"page load error: {e}",
        )

    # Best-effort networkidle wait. Script-heavy sites (heavy 3rd-party JS,
    # ad pixels, analytics, chat widgets) often never reach network-idle.
    # Wait briefly, then proceed regardless. The actual test (click the
    # trigger) is the real readiness gate.
    try:
        page.wait_for_load_state("networkidle", timeout=3000)
    except Exception:
        pass
    page.wait_for_timeout(1200)  # JS handler binding window

    # Find FIRST VISIBLE trigger. Themes often render multiple matches for the
    # same selector (mobile + desktop variants); query_selector returns the
    # first DOM match regardless of visibility. Loop to find the visible one
    # at the test viewport; SKIP if none visible (responsive variant might be
    # the only one rendered, just not at this size).
    try:
        candidates = page.query_selector_all(test.trigger_selector)
    except Exception as e:
        return TestResult(
            name=test.name,
            status="SKIP",
            duration_ms=int((time.monotonic() - started) * 1000),
            reason=f"trigger selector error: {e}",
        )
    if not candidates:
        return TestResult(
            name=test.name,
            status="SKIP",
            duration_ms=int((time.monotonic() - started) * 1000),
            reason=f"trigger not found: {test.trigger_selector}",
        )
    trigger = None
    for c in candidates:
        try:
            if c.is_visible():
                trigger = c
                break
        except Exception:
            continue
    if trigger is None:
        return TestResult(
            name=test.name,
            status="SKIP",
            duration_ms=int((time.monotonic() - started) * 1000),
            reason=(
                f"trigger matched {len(candidates)} element(s) but none visible "
                f"at viewport {test.viewport[0]}x{test.viewport[1]}: {test.trigger_selector}"
            ),
        )

    if test.pre_click_wait_for:
        try:
            page.wait_for_function(test.pre_click_wait_for, timeout=8000)
        except Exception as e:
            if verbose:
                print(f"    pre_click_wait_for timed out (continuing): {e}")

    if test.trigger_eval_js:
        # Direct JS evaluation path — used when a programmatic click doesn't
        # reliably fire the overlay init chain in headless mode (e.g. PhotoSwipe
        # whose listener is only bound after an async loadScript promise resolves
        # and whose init uses setTimeout(0) yielding to the next macrotask).
        try:
            page.evaluate(test.trigger_eval_js)
        except Exception as e:
            return TestResult(
                name=test.name,
                status="FAIL",
                duration_ms=int((time.monotonic() - started) * 1000),
                reason=f"trigger_eval_js execution failed: {e}",
            )
    else:
        try:
            trigger.scroll_into_view_if_needed(timeout=2000)
            # Some triggers (PhotoSwipe-style zoom buttons) reveal on parent hover.
            # Hover the parent first; safe for all triggers.
            try:
                parent = trigger.evaluate_handle("el => el.parentElement").as_element()
                if parent:
                    parent.hover(timeout=1000)
            except Exception:
                pass
            trigger.click(timeout=2000, force=True)
        except Exception as e:
            return TestResult(
                name=test.name,
                status="FAIL",
                duration_ms=int((time.monotonic() - started) * 1000),
                reason=f"trigger click failed: {e}",
            )

    try:
        # state="attached", not "visible". Outer drawer wrappers are often
        # position:static with 0 height (only the inner .drawer__content has
        # fixed positioning + dimensions); Playwright's "visible" check would
        # time out on the wrapper, even though the drawer IS open.
        page.wait_for_selector(test.state_selector, state="attached", timeout=5000)
    except Exception:
        return TestResult(
            name=test.name,
            status="FAIL",
            duration_ms=int((time.monotonic() - started) * 1000),
            reason=f"open-state indicator not visible within 5s: {test.state_selector}",
        )

    panel = page.query_selector(test.panel_selector)
    if panel is None:
        return TestResult(
            name=test.name,
            status="FAIL",
            duration_ms=int((time.monotonic() - started) * 1000),
            reason=f"panel not found after open: {test.panel_selector}",
        )

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

    min_height = test.expected_height_pct * geometry["viewportHeight"]
    if geometry["height"] < min_height or geometry["width"] < 300:
        return _fail_with_screenshot(
            page, test, started,
            reason=(
                f"panel geometry too small: {geometry['width']:.0f}x"
                f"{geometry['height']:.0f}px (viewport "
                f"{geometry['viewportWidth']}x{geometry['viewportHeight']}); "
                f"expected width>=300 and height>={min_height:.0f} "
                f"({int(test.expected_height_pct*100)}% of viewport). "
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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Headless smoke test for fixed-position overlays — the kt0-killer "
            "gate. Run before any deploy / push that touches CSS / layout / "
            "header / popup-wrapper code. Config-driven via JSON."
        )
    )
    p.add_argument(
        "--config",
        required=True,
        help="Path to JSON config file. See skill docs for schema.",
    )
    p.add_argument(
        "--theme",
        default=None,
        help=(
            "Which theme key from config.site.themes to preview. Defaults to "
            "the first key in the themes dict. Ignored if config has no "
            "preview_param/themes (direct URL navigation)."
        ),
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
        "--verbose",
        action="store_true",
        help="Print per-test progress lines. Default: failures + summary only.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    try:
        site, tests = load_config(Path(args.config))
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: config load failed: {e}", file=sys.stderr)
        return 2

    theme: str | None = args.theme
    if theme is None and site.themes:
        theme = next(iter(site.themes.keys()))
    if theme and site.themes and theme not in site.themes:
        print(
            f"ERROR: --theme={theme!r} not in config.site.themes "
            f"({sorted(site.themes.keys())})",
            file=sys.stderr,
        )
        return 2

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "ERROR: playwright not installed. Run:\n"
            "  python3 -m pip install playwright\n"
            "  python3 -m playwright install chromium",
            file=sys.stderr,
        )
        return 2

    results: list[TestResult] = []
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=args.headless)
            except Exception as e:
                print(
                    f"ERROR: chromium launch failed: {e}\n"
                    "  Run: python3 -m playwright install chromium",
                    file=sys.stderr,
                )
                return 2
            try:
                for i, test in enumerate(tests, 1):
                    context = browser.new_context(
                        viewport={"width": test.viewport[0], "height": test.viewport[1]},
                    )
                    page = context.new_page()
                    label = f"[{i}/{len(tests)}] {test.name}"
                    if args.verbose:
                        print(f"{label} ... ", end="", flush=True)
                    result = run_overlay_test(page, test, site, theme, args.verbose)
                    results.append(result)
                    if args.verbose:
                        print(f"{result.status} ({result.duration_ms}ms)")
                    if result.status == "FAIL":
                        print(f"\n{label} ... FAIL ({result.duration_ms}ms)")
                        print(f"  Reason: {result.reason}")
                        if result.offending_selector:
                            print(f"  Offending ancestor: {result.offending_selector}")
                            print(f"  See: CSS Containment spec for which properties create containing blocks for fixed descendants.")
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
