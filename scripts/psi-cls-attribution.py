#!/usr/bin/env python3
"""
psi-cls-attribution.py — Phase 0.2 output for bd hairmnl-theme-ujg6.

Reads /tmp/psi-baseline/*.json (output of psi-baseline-matrix.py) and aggregates
the `layout-shifts` audit per (theme, strategy, template) into a ranked CLS
attribution table.

Output: /tmp/psi-baseline/cls-attribution.md (markdown)
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

OUT_DIR = Path("/tmp/psi-baseline")
TARGET = OUT_DIR / "cls-attribution.md"

CELL_RX = re.compile(r"^(?P<theme>[\w-]+)-(?P<strategy>mobile|desktop)-(?P<template>[\w-]+)-run(?P<run>\d+)\.json$")


def short_selector(sel: str, max_len: int = 80) -> str:
    """Trim a CSS selector to a useful short form."""
    if not sel:
        return "(unknown)"
    parts = sel.split(" > ")
    if len(parts) > 3:
        sel = " > ".join(parts[-3:])
    if len(sel) > max_len:
        sel = sel[:max_len - 1] + "…"
    return sel


def classify_node(snippet: str, selector: str, label: str) -> str:
    """Best-effort categorisation of what a shifting DOM node represents."""
    text = f"{snippet} {selector} {label}".lower()
    if "loyaltylion" in text or "lion-notification" in text or "lion-loyalty" in text:
        return "LoyaltyLion widget"
    if "reamaze" in text or "rea-frame" in text:
        return "Re:amaze chat"
    if "klaviyo" in text:
        return "Klaviyo popup"
    if "judge.me" in text or "jdgm" in text:
        return "Judge.me widget"
    if "swiper" in text or "flickity" in text or "slick" in text or "slider" in text:
        return "Carousel/slider"
    if "banner" in text:
        return "Banner section"
    if "header" in text and ("nav" in text or "main-nav" in text):
        return "Header/nav"
    if "footer" in text:
        return "Footer"
    if "product-grid" in text or "product-card" in text:
        return "Product grid card"
    if "<img" in snippet or "<picture" in snippet:
        return "Image (no dimensions?)"
    if "main-content" in text or "id=\"maincontent\"" in text.lower():
        return "Main content (broad)"
    if "main" == selector.split(",")[-1].strip().split("#")[0].strip().lower():
        return "Main content (broad)"
    if "h1" in text or "h2" in text:
        return "Heading text"
    if "<font" in snippet or "font-stack" in text:
        return "Font swap"
    if "popdown" in text or "modal" in text or "drawer" in text:
        return "Modal/drawer/popdown"
    return "Other"


# 404 / wrong-page detection. The PSI bot follows redirects; if a target
# URL 301s or 404s, the bot may end up measuring an error page or homepage
# while the cell's name still says "collection". Selectors in the
# layout-shifts audit reveal this — error pages have a distinctive body id.
# See 2i8b.17 (2026-05-18) for the incident: /collections/cat-best-sellers
# silently measured a 404 footer shift score of 0.632 for weeks before this
# guard caught it. Body-id patterns observed:
#   - body#404-not-found   — Shopify default 404 controller
#   - body#password        — store-locked password page
#   - body#maintenance     — maintenance-mode page
#   - body#customers-login — auth redirect (often when /cart hits a logged-out
#     state on B2B-locked stores)
BAD_BODY_ID_RX = re.compile(
    r"body#(?:404-not-found|password|maintenance|robot-challenge|customers-login)",
    re.IGNORECASE,
)


def detect_404_or_wrong_page(items: list) -> str | None:
    """If any layout-shift selector matches a known error-page body id,
    return that body id (otherwise None). When the result is non-None, the
    cell's CLS measurements are bogus — the PSI bot measured an error page,
    not the cell's actual template."""
    for it in items:
        sel = (it.get("node", {}) or {}).get("selector", "") or ""
        m = BAD_BODY_ID_RX.search(sel)
        if m:
            return m.group(0).split("#", 1)[-1]
    return None


def aggregate_cell(json_files: list[Path]) -> dict:
    """For one (theme, strategy, template), aggregate layout shifts across runs."""
    all_shifts = []
    total_cls_values = []
    bad_page: str | None = None

    for f in json_files:
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        audits = data.get("audits", {}) or {}
        cls = audits.get("cumulative-layout-shift", {}).get("numericValue")
        if cls is not None:
            total_cls_values.append(cls)
        items = (audits.get("layout-shifts", {}) or {}).get("details", {}).get("items", [])
        # 2i8b.17 guard: flag if the PSI bot ended up on an error page
        if bad_page is None:
            bad_page = detect_404_or_wrong_page(items)
        for it in items:
            score = it.get("score", 0)
            node = it.get("node", {})
            all_shifts.append({
                "score": score,
                "selector": short_selector(node.get("selector", "")),
                "snippet": (node.get("snippet") or "")[:140],
                "label": (node.get("nodeLabel") or "")[:80],
                "rect_h": node.get("boundingRect", {}).get("height"),
                "rect_w": node.get("boundingRect", {}).get("width"),
                "category": classify_node(node.get("snippet", ""), node.get("selector", ""), node.get("nodeLabel", "")),
            })

    # Roll up by category (sum scores)
    by_cat = defaultdict(float)
    sample_per_cat = {}
    for s in all_shifts:
        by_cat[s["category"]] += s["score"]
        if s["category"] not in sample_per_cat:
            sample_per_cat[s["category"]] = s

    # Median CLS, top categories
    from statistics import median
    return {
        "n_runs": len(json_files),
        "n_shifts_total": len(all_shifts),
        "median_cls": median(total_cls_values) if total_cls_values else None,
        "categories": sorted(
            [{"category": cat, "total_score": score, "sample": sample_per_cat[cat]}
             for cat, score in by_cat.items()],
            key=lambda r: r["total_score"], reverse=True
        )[:5],
        "bad_page": bad_page,  # body-id string if the PSI bot measured an error page; None if the cell looks legit
    }


def main() -> None:
    files_by_cell = defaultdict(list)
    for f in OUT_DIR.glob("*.json"):
        m = CELL_RX.match(f.name)
        if not m:
            continue
        cell = (m["theme"], m["strategy"], m["template"])
        files_by_cell[cell].append(f)

    if not files_by_cell:
        print("No PSI JSON files found in /tmp/psi-baseline/")
        return

    # Pre-pass: detect bad-page cells before generating the report. These
    # need a prominent warning at the top — silently treating their CLS
    # as legitimate is the 2i8b.17 failure mode this guard exists to
    # prevent.
    bad_cells: dict[tuple[str, str, str], str] = {}
    for cell, files in files_by_cell.items():
        agg = aggregate_cell(files)
        if agg.get("bad_page"):
            bad_cells[cell] = agg["bad_page"]

    lines = []
    lines.append("# CLS attribution (Phase 0.2) — bd hairmnl-theme-ujg6.2")
    lines.append("")
    lines.append("Extracted from `layout-shifts` audit in Lighthouse 13.x via PSI API. "
                 "Scores are summed across all runs per cell, then top-5 categories by total score "
                 "are listed. Categories are best-effort classifications of the shifting DOM node "
                 "(by selector + snippet + label).")
    lines.append("")
    lines.append("**Caveat on `n_runs`**: PSI API caches identical-URL requests within ~30s, so n=3 "
                 "often returns 1 fresh + 2 cached. Treat `n_runs` as upper bound; effective unique "
                 "samples may be 1.")
    lines.append("")

    # 404 / wrong-page warning banner (2i8b.17 guard)
    if bad_cells:
        lines.append("## ⚠️  BAD-PAGE CELLS DETECTED — measurements are bogus")
        lines.append("")
        lines.append("The following cells' CLS measurements are NOT trustworthy. The PSI bot "
                     "ended up on an error/redirect page instead of the intended template — "
                     "the layout-shift attribution selectors match a known bad-page body id "
                     "(e.g., `body#404-not-found`). Per the 2i8b.17 incident (2026-05-18) "
                     "where `/collections/cat-best-sellers` measured 0.632 CLS that turned out "
                     "to be footer shifts on a 404 page.")
        lines.append("")
        lines.append("| Cell | Bad page detected | Fix |")
        lines.append("|---|---|---|")
        for (theme, strat, tpl), body_id in sorted(bad_cells.items()):
            lines.append(f"| {theme} / {strat} / {tpl} | `body#{body_id}` | Verify the URL in `scripts/psi-baseline-matrix.py::TEMPLATES` resolves to the intended page (`curl -sIL <url>` should show pageType matching the cell name) |")
        lines.append("")
        lines.append("**Treat these cells' CLS values as ignored. Re-baseline after fixing URLs.**")
        lines.append("")

    # Order: P6 first then P8, mobile then desktop, by template
    template_order = ["home", "collection", "pdp", "cart", "brand"]
    theme_order = ["p6-live", "p8-dev"]
    strategy_order = ["mobile", "desktop"]

    for strategy in strategy_order:
        lines.append(f"## {strategy.title()}")
        lines.append("")
        for template in template_order:
            lines.append(f"### {template}")
            lines.append("")
            lines.append("| Theme | n | median CLS | shifts | Top categories (score) |")
            lines.append("|---|---|---|---|---|")
            for theme in theme_order:
                cell = (theme, strategy, template)
                files = files_by_cell.get(cell, [])
                if not files:
                    lines.append(f"| {theme} | 0 | — | — | (no data) |")
                    continue
                a = aggregate_cell(files)
                cats = " · ".join(
                    f"{c['category']} ({c['total_score']:.3f})" for c in a["categories"]
                )
                med = a["median_cls"]
                med_str = f"{med:.3f}" if med is not None else "—"
                # 2i8b.17 guard: inline marker for bad-page cells
                if a.get("bad_page"):
                    med_str += f" ⚠️ {a['bad_page']}"
                lines.append(f"| {theme} | {a['n_runs']} | {med_str} | {a['n_shifts_total']} | {cats} |")
            lines.append("")

            # Detail: top shift per cell with selector
            lines.append("**Top shift per cell:**")
            lines.append("")
            for theme in theme_order:
                cell = (theme, strategy, template)
                files = files_by_cell.get(cell, [])
                if not files:
                    continue
                a = aggregate_cell(files)
                if not a["categories"]:
                    lines.append(f"- {theme}: (no shifts recorded)")
                    continue
                top = a["categories"][0]["sample"]
                lines.append(f"- **{theme}**: `{top['selector']}` — "
                             f"`{top['snippet'][:90]}` — {a['categories'][0]['category']} "
                             f"(score {a['categories'][0]['total_score']:.3f}, "
                             f"box {top['rect_w']}×{top['rect_h']})")
            lines.append("")

    TARGET.write_text("\n".join(lines))
    print(f"Wrote {TARGET}")


if __name__ == "__main__":
    main()
