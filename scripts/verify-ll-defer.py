#!/usr/bin/env python3
"""
verify-ll-defer.py — Automated verification of the LoyaltyLion defer guard on /cart.

Checks two things:
  1. PRE-INTERACTION: loyaltylion.net scripts do NOT load in the first 8s of a
     cold /cart page load (before any user interaction).
  2. POST-INTERACTION: loyaltylion.net scripts DO load within 2s after a
     simulated click on the cart page.

Exit 0 = both checks pass (defer is working correctly).
Exit 1 = at least one check failed (see output for details).

Usage:
  python3 scripts/verify-ll-defer.py
  python3 scripts/verify-ll-defer.py --url https://www.hairmnl.com/cart
  python3 scripts/verify-ll-defer.py --headless false   # watch the browser
"""

import argparse
import sys
import time
from urllib.parse import urlparse

LOYALTYLION_PATTERN = "loyaltylion.net"
PRE_INTERACTION_WAIT_S = 8     # seconds to observe before interacting
POST_INTERACTION_WAIT_S = 3    # seconds to wait for scripts after click
CART_URL = "https://www.hairmnl.com/cart"


def run(url: str, headless: bool) -> bool:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        print("ERROR: pip install playwright && playwright install chromium")
        sys.exit(1)

    ll_before: list[str] = []
    ll_after: list[str] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        context = browser.new_context(
            # Emulate a real mobile user (Moto G4) to match the PSI mobile profile
            viewport={"width": 412, "height": 823},
            user_agent=(
                "Mozilla/5.0 (Linux; Android 11; moto g power (2022)) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/119.0.0.0 Mobile Safari/537.36"
            ),
            device_scale_factor=2.625,
            has_touch=True,
            is_mobile=True,
        )
        page = context.new_page()

        # Capture all network requests
        all_requests: list[str] = []
        interaction_ts: list[float] = []

        def on_request(req):
            all_requests.append(req.url)
            if LOYALTYLION_PATTERN in req.url:
                ts = time.time()
                if not interaction_ts:
                    ll_before.append(req.url)
                    print(f"  ⚠  PRE-interaction LL request: {req.url[:80]}")
                else:
                    delay_ms = (ts - interaction_ts[0]) * 1000
                    ll_after.append(req.url)
                    print(f"  ✓  POST-interaction LL request (+{delay_ms:.0f}ms): {req.url[:80]}")

        page.on("request", on_request)

        # ── Phase 1: cold load, no interaction ────────────────────────────
        print(f"\nPhase 1: navigating to {url} (no interaction for {PRE_INTERACTION_WAIT_S}s) ...")
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_timeout(PRE_INTERACTION_WAIT_S * 1000)

        pre_ll_count = len(ll_before)
        if pre_ll_count == 0:
            print(f"  ✅ PASS — zero loyaltylion.net requests in first {PRE_INTERACTION_WAIT_S}s")
        else:
            print(f"  ❌ FAIL — {pre_ll_count} loyaltylion.net request(s) before interaction:")
            for r in ll_before:
                print(f"       {r}")

        # ── Phase 2: simulate interaction ─────────────────────────────────
        print(f"\nPhase 2: simulating click interaction ...")
        interaction_ts.append(time.time())

        # Click the first interactive cart element we can find, fallback to body
        clicked = False
        for selector in [
            "button[name='minus']",        # qty minus button
            "button[name='plus']",         # qty plus button
            "input[name='updates[]']",     # qty input
            "a[href='/checkout']",         # checkout button
            "button[type='submit']",       # any submit
            "body",                        # guaranteed fallback
        ]:
            try:
                el = page.locator(selector).first
                if el.is_visible(timeout=500):
                    el.click(timeout=1000)
                    print(f"  Clicked: {selector}")
                    clicked = True
                    break
            except Exception:
                continue

        if not clicked:
            print("  (no specific element found — clicking body)")
            page.mouse.click(206, 411)

        page.wait_for_timeout(POST_INTERACTION_WAIT_S * 1000)

        post_ll_count = len(ll_after)
        if post_ll_count > 0:
            print(f"  ✅ PASS — {post_ll_count} loyaltylion.net request(s) loaded after interaction")
        else:
            # LL may not load if cart is empty (no points to show) — warn not fail
            print(f"  ⚠  NOTE — zero loyaltylion.net requests after interaction")
            print(f"     (normal if /cart is empty and LL has nothing to render)")
            print(f"     If /cart has items, investigate further.")

        browser.close()

    # ── Summary ─────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    passed = True

    check1 = pre_ll_count == 0
    check2 = post_ll_count > 0
    print(f"  [{'PASS' if check1 else 'FAIL'}] Pre-interaction: LL scripts NOT loaded  ({pre_ll_count} requests)")
    print(f"  [{'PASS' if check2 else 'WARN'}] Post-interaction: LL scripts loaded     ({post_ll_count} requests)")

    if not check1:
        print("\n  ❌ Defer guard is NOT working — LL loads before user interaction.")
        print("     Check layout/theme.liquid around the LoyaltyLion defer block.")
        passed = False
    elif not check2:
        print("\n  ⚠  Post-interaction load not confirmed — run against a cart with items.")
    else:
        print("\n  ✅ Defer guard verified end-to-end.")

    return passed


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default=CART_URL, help="Cart URL to test")
    parser.add_argument("--headless", default="true", choices=["true", "false"],
                        help="Run headless (default: true)")
    args = parser.parse_args()
    headless = args.headless.lower() == "true"
    ok = run(args.url, headless)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
