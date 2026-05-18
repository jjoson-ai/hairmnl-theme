#!/usr/bin/env python3
"""check-snippet-wiring.py — detect orphaned Liquid snippets AND assets.

TWO REGRESSION CLASSES this lint covers:

(1) Orphaned snippets (yxte, 2026-05-18 AM):
A P4 wave-a refactor (commit 0cd30cf) shrank layout/theme.liquid by 64% and
silently dropped `{% render 'css-overrides' %}` + `{% render 'custom-fonts' %}`.
The files were carefully ported on disk, but nothing referenced them anymore.
23 documented CLS fixes went no-op on live for ~24 hours.

Caught by: any `snippets/*.liquid` file must be referenced by
`{% render '<name>' %}` or `{% include '<name>' %}` somewhere in layout/,
sections/, templates/, snippets/, or assets/*.liquid.

(2) Orphaned assets (cache-shadow escalation, 2026-05-18 PM):
The SAME P4 wave-a refactor also dropped `{{ 'jquery.min.js' | asset_url }}`,
`{{ 'custom-theme.js' | asset_url }}`, `{{ 'shop.js' | asset_url }}`,
`{{ 'lazysizes.js' | asset_url }}`, and `{{ 'custom-theme.css' | asset_url }}`
loads from layout/theme.liquid. Shopify edge page cache hid this for 24 days.
When the cache invalidated, the homepage broke: no megamenu, no product
images, vertical sliders. Emergency revert at commit 49ae3dc.

The original lint covered (1) but NOT (2) — it only looked at
`{% render %}` callsites. Per MIGRATION-CONTRACT.md Rule 9, this script
now ALSO covers (2): any `assets/*.js` or `assets/*.css` file must be
referenced via `{{ '<file>' | asset_url ... }}` somewhere.

Allowlists:
- Snippet orphans: `os2-migration/intentionally-orphan.txt`
- Asset orphans:   `os2-migration/intentionally-orphan-assets.txt`

Both use the same format: <path> <bd-id> <target_wire_by> <reason>.
Entries past their target_wire_by emit STALE warnings but don't fail
the lint.

Exit codes:
  0 — clean (no un-allowlisted orphans in either category)
  1 — at least one orphan (snippet OR asset) not in the allowlist
  2 — invocation error (missing allowlist file format, etc.)

Usage:
  python3 scripts/check-snippet-wiring.py             # report + exit code
  python3 scripts/check-snippet-wiring.py --json      # machine-readable
  python3 scripts/check-snippet-wiring.py --verbose   # show every snippet
  python3 scripts/check-snippet-wiring.py --snippets-only  # skip asset check
  python3 scripts/check-snippet-wiring.py --assets-only    # skip snippet check
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
SNIPPETS_DIR = REPO / "snippets"
ASSETS_DIR = REPO / "assets"
ALLOWLIST = REPO / "os2-migration" / "intentionally-orphan.txt"
ASSET_ALLOWLIST = REPO / "os2-migration" / "intentionally-orphan-assets.txt"

# Directories that may reference a snippet via {% render '<name>' %}
# OR an asset via {{ '<file>' | asset_url ... }}
SEARCH_DIRS = [
    REPO / "layout",
    REPO / "sections",
    REPO / "templates",
    REPO / "snippets",
    REPO / "blocks",
    REPO / "assets",  # *.liquid asset files can call render or asset_url too
]

# Regex matches both `render 'foo'` and `render "foo"` and `include 'foo'`.
# Liquid permits whitespace and optional `-` for whitespace trimming inside
# the tag opener; the snippet name is always a literal string in our codebase
# (we don't dynamically resolve `render snippet_name_var` anywhere — verified
# via `grep -rE "render [a-z_]+\b" snippets/ sections/ layout/` returning 0
# rows. If that ever changes, dynamic renders need an allowlist exception.)
REFERENCE_RE = re.compile(r"""\{%-?\s*(?:render|include)\s+['"]([^'"]+)['"]""")

# Regex matches asset_url usage: {{ 'file.js' | asset_url }} or
# {{ "file.css" | asset_url | stylesheet_tag }} etc. Captures the filename.
# Only catches .js and .css extensions — image assets (.png/.jpg/.svg/etc.)
# are content assets with many legitimate orphans (deleted products leave
# files behind) and aren't appropriate for this lint.
#
# Handles query-string suffixes like
# `{{ 'custom.js?enable_js_minification=1' | asset_url }}` (the suffix is
# stripped after the .js/.css extension; matches that pattern to the bare
# filename `custom.js`).
#
# Variable-name lookups like `{{ filename_var | asset_url }}` are NOT caught;
# our codebase uses literal filenames only (verified by spot-check). If that
# changes, dynamic asset_url references would need allowlist entries.
ASSET_REFERENCE_RE = re.compile(
    r"""\{\{-?\s*['"]([^'"?]+\.(?:js|css))(?:\?[^'"]*)?['"]\s*\|\s*asset_url\b""",
)


def discover_snippets() -> list[Path]:
    if not SNIPPETS_DIR.is_dir():
        return []
    return sorted(p for p in SNIPPETS_DIR.glob("*.liquid"))


def discover_references() -> dict[str, list[Path]]:
    """Returns {snippet_name: [paths-that-reference-it]} for every render/include."""
    refs: dict[str, list[Path]] = {}
    for root in SEARCH_DIRS:
        if not root.is_dir():
            continue
        for path in root.rglob("*.liquid"):
            # Skip files under hidden / worktree / vendor dirs
            if any(part.startswith(".") for part in path.parts):
                continue
            if "worktrees" in path.parts or "node_modules" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for m in REFERENCE_RE.finditer(text):
                name = m.group(1).strip()
                refs.setdefault(name, []).append(path)
    return refs


def load_allowlist() -> dict[str, dict]:
    """Parse os2-migration/intentionally-orphan.txt.

    Format per row (whitespace-separated, comments via #):
      <snippet-path-or-name>  <bd-id>  <target-wire-by-YYYY-MM-DD>  <reason...>

    Example:
      snippets/custom-theme.liquid    2i8b.4    2026-06-30    P4-deferred port
    """
    if not ALLOWLIST.is_file():
        return {}
    result: dict[str, dict] = {}
    for lineno, raw in enumerate(ALLOWLIST.read_text().splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 3)
        if len(parts) < 3:
            print(
                f"warn: {ALLOWLIST.name}:{lineno}: skipping malformed row: {raw!r}",
                file=sys.stderr,
            )
            continue
        path, bd_id, wire_by = parts[0], parts[1], parts[2]
        reason = parts[3] if len(parts) > 3 else ""
        # Normalize to bare snippet name (without `snippets/` prefix or `.liquid` suffix)
        if path.startswith("snippets/"):
            path = path[len("snippets/"):]
        if path.endswith(".liquid"):
            path = path[: -len(".liquid")]
        result[path] = {
            "bd_id": bd_id,
            "target_wire_by": wire_by,
            "reason": reason,
            "lineno": lineno,
        }
    return result


def discover_assets() -> list[Path]:
    """Return all assets/*.js and assets/*.css files in the repo."""
    if not ASSETS_DIR.is_dir():
        return []
    result: list[Path] = []
    for ext in ("*.js", "*.css"):
        result.extend(ASSETS_DIR.glob(ext))
    # Exclude .liquid files (these are dynamic assets, treated as snippets
    # by the existing logic since they contain Liquid markup).
    return sorted(p for p in result if not p.name.endswith(".liquid"))


def discover_asset_references() -> dict[str, list[Path]]:
    """Returns {asset_filename: [paths-that-reference-it]} for every
    `{{ 'file.js' | asset_url }}` or `{{ 'file.css' | asset_url ... }}`
    in Liquid files under SEARCH_DIRS.

    Filename key includes the extension (e.g., "jquery.min.js") but no path
    prefix — the asset_url filter resolves all filenames against assets/.
    """
    refs: dict[str, list[Path]] = {}
    for root in SEARCH_DIRS:
        if not root.is_dir():
            continue
        for path in root.rglob("*.liquid"):
            if any(part.startswith(".") for part in path.parts):
                continue
            if "worktrees" in path.parts or "node_modules" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for m in ASSET_REFERENCE_RE.finditer(text):
                name = m.group(1).strip()
                refs.setdefault(name, []).append(path)
    return refs


def load_asset_allowlist() -> dict[str, dict]:
    """Parse os2-migration/intentionally-orphan-assets.txt.

    Same format as snippet allowlist. Paths are normalized to bare
    filenames (asset_url resolves against assets/, not the full path).

    Example row:
      assets/legacy-vendor.js   2i8b   2026-09-30   [VENDOR-LIB] kept for app X
    """
    if not ASSET_ALLOWLIST.is_file():
        return {}
    result: dict[str, dict] = {}
    for lineno, raw in enumerate(ASSET_ALLOWLIST.read_text().splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 3)
        if len(parts) < 3:
            print(
                f"warn: {ASSET_ALLOWLIST.name}:{lineno}: skipping malformed row: {raw!r}",
                file=sys.stderr,
            )
            continue
        path, bd_id, wire_by = parts[0], parts[1], parts[2]
        reason = parts[3] if len(parts) > 3 else ""
        # Normalize to bare filename (strip `assets/` prefix if present;
        # asset_url resolves against assets/, so the key matches the filename
        # produced by discover_assets()).
        if path.startswith("assets/"):
            path = path[len("assets/"):]
        result[path] = {
            "bd_id": bd_id,
            "target_wire_by": wire_by,
            "reason": reason,
            "lineno": lineno,
        }
    return result


def check_snippets(verbose: bool = False) -> tuple[list[dict], list[dict], list[dict]]:
    """Run the snippet wiring check.

    Returns (orphans_blocking, orphans_allowed, used).
    """
    snippets = discover_snippets()
    refs = discover_references()
    allow = load_allowlist()

    orphans_blocking: list[dict] = []
    orphans_allowed: list[dict] = []
    used: list[dict] = []
    today = datetime.date.today()

    for snippet in snippets:
        name = snippet.stem
        referrers = refs.get(name, [])
        external_referrers = [p for p in referrers if p.resolve() != snippet.resolve()]
        if external_referrers:
            used.append({"name": name, "referrer_count": len(external_referrers)})
            continue

        if name in allow:
            entry = allow[name]
            stale = False
            try:
                target = datetime.date.fromisoformat(entry["target_wire_by"])
                stale = today > target
            except ValueError:
                pass
            orphans_allowed.append({
                "name": name,
                "bd_id": entry["bd_id"],
                "target_wire_by": entry["target_wire_by"],
                "reason": entry["reason"],
                "stale": stale,
            })
        else:
            orphans_blocking.append({"name": name, "path": str(snippet.relative_to(REPO))})

    return orphans_blocking, orphans_allowed, used


def check_assets(verbose: bool = False) -> tuple[list[dict], list[dict], list[dict]]:
    """Run the asset wiring check (assets/*.js + assets/*.css).

    Returns (orphans_blocking, orphans_allowed, used).
    """
    assets = discover_assets()
    refs = discover_asset_references()
    allow = load_asset_allowlist()

    orphans_blocking: list[dict] = []
    orphans_allowed: list[dict] = []
    used: list[dict] = []
    today = datetime.date.today()

    for asset in assets:
        name = asset.name  # filename including extension (e.g., "jquery.min.js")
        referrers = refs.get(name, [])
        # An asset can't reference itself the way snippets can (no render-self),
        # but to be safe we exclude self-references (e.g., a .css that imports
        # itself via Liquid asset_url — unlikely but cheap to guard).
        external_referrers = [p for p in referrers if p.resolve() != asset.resolve()]
        if external_referrers:
            used.append({"name": name, "referrer_count": len(external_referrers)})
            continue

        if name in allow:
            entry = allow[name]
            stale = False
            try:
                target = datetime.date.fromisoformat(entry["target_wire_by"])
                stale = today > target
            except ValueError:
                pass
            orphans_allowed.append({
                "name": name,
                "bd_id": entry["bd_id"],
                "target_wire_by": entry["target_wire_by"],
                "reason": entry["reason"],
                "stale": stale,
            })
        else:
            orphans_blocking.append({"name": name, "path": str(asset.relative_to(REPO))})

    return orphans_blocking, orphans_allowed, used


def _report_section(title: str, total: int, used: list, allowed: list, blocking: list,
                    blocking_hint: str, allowlist_path: str, verbose: bool) -> None:
    """Print a report section for one check (snippets or assets)."""
    print(f"{title} — scanned {total} files")
    print(f"  ✓ wired:           {len(used)}")
    print(f"  ⚠ allowed orphans: {len(allowed)}")
    print(f"  ✗ BLOCKING orphans: {len(blocking)}")
    print()
    if blocking:
        print(f"BLOCKING — files that exist but are not referenced anywhere:")
        print(f"  {blocking_hint}")
        print(f"  Either (a) re-add the reference, (b) delete the file, or")
        print(f"  (c) add it to {allowlist_path} with a bd-id + target_wire_by date.")
        print()
        for o in blocking:
            print(f"    ✗ {o['path']}")
        print()
    if allowed:
        stale_n = sum(1 for o in allowed if o["stale"])
        print(f"Allowlisted orphans ({len(allowed)} total, {stale_n} past target date):")
        for o in sorted(allowed, key=lambda x: (not x["stale"], x["name"])):
            marker = "STALE " if o["stale"] else "      "
            print(f"    {marker}{o['name']:40s} bd={o['bd_id']:10s} wire_by={o['target_wire_by']}  {o['reason']}")
        print()
    if verbose and used:
        print("Wired files (for reference):")
        for u in used:
            print(f"    ✓ {u['name']:45s} {u['referrer_count']} referrers")
        print()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON report")
    ap.add_argument("--verbose", action="store_true", help="show every snippet/asset with its references")
    ap.add_argument("--snippets-only", action="store_true", help="skip asset check (default runs both)")
    ap.add_argument("--assets-only", action="store_true", help="skip snippet check (default runs both)")
    args = ap.parse_args(argv[1:])

    if args.snippets_only and args.assets_only:
        print("error: --snippets-only and --assets-only are mutually exclusive", file=sys.stderr)
        return 2

    run_snippets = not args.assets_only
    run_assets = not args.snippets_only

    snippet_blocking: list[dict] = []
    snippet_allowed: list[dict] = []
    snippet_used: list[dict] = []
    asset_blocking: list[dict] = []
    asset_allowed: list[dict] = []
    asset_used: list[dict] = []

    if run_snippets:
        snippet_blocking, snippet_allowed, snippet_used = check_snippets(args.verbose)
    if run_assets:
        asset_blocking, asset_allowed, asset_used = check_assets(args.verbose)

    if args.json:
        out: dict = {"passed": True}
        if run_snippets:
            out["snippets"] = {
                "total": len(snippet_used) + len(snippet_allowed) + len(snippet_blocking),
                "used": len(snippet_used),
                "orphans_blocking": snippet_blocking,
                "orphans_allowed": snippet_allowed,
                "passed": len(snippet_blocking) == 0,
            }
            out["passed"] = out["passed"] and out["snippets"]["passed"]
        if run_assets:
            out["assets"] = {
                "total": len(asset_used) + len(asset_allowed) + len(asset_blocking),
                "used": len(asset_used),
                "orphans_blocking": asset_blocking,
                "orphans_allowed": asset_allowed,
                "passed": len(asset_blocking) == 0,
            }
            out["passed"] = out["passed"] and out["assets"]["passed"]
        print(json.dumps(out, indent=2))
    else:
        if run_snippets:
            _report_section(
                "Snippet wiring lint",
                total=len(snippet_used) + len(snippet_allowed) + len(snippet_blocking),
                used=snippet_used, allowed=snippet_allowed, blocking=snippet_blocking,
                blocking_hint="These are most likely the result of a refactor that dropped a {% render %} callsite.",
                allowlist_path="os2-migration/intentionally-orphan.txt",
                verbose=args.verbose,
            )
        if run_assets:
            _report_section(
                "Asset wiring lint (.js / .css via asset_url)",
                total=len(asset_used) + len(asset_allowed) + len(asset_blocking),
                used=asset_used, allowed=asset_allowed, blocking=asset_blocking,
                blocking_hint="These are most likely the result of a refactor that dropped a {{ 'file.js' | asset_url }} reference. This is the regression class that caused the 2026-05-18 PM cache-shadow escalation (commit 49ae3dc emergency revert).",
                allowlist_path="os2-migration/intentionally-orphan-assets.txt",
                verbose=args.verbose,
            )

    failed = (run_snippets and snippet_blocking) or (run_assets and asset_blocking)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
