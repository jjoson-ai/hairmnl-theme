#!/usr/bin/env python3
"""check-snippet-wiring.py — detect orphaned Liquid snippets.

Today's class of regression (bd hairmnl-theme-yxte, 2026-05-18): a P4 wave-a
refactor (commit 0cd30cf) shrank layout/theme.liquid by 64% and silently
dropped `{% render 'css-overrides' %}` + `{% render 'custom-fonts' %}`. The
files were carefully ported on disk, but nothing referenced them anymore.
23 documented CLS fixes went no-op on live for ~24 hours.

This lint catches that pattern: any `snippets/*.liquid` file in the repo
must be referenced by `{% render '<name>' %}` or `{% include '<name>' %}`
somewhere in layout/, sections/, templates/, snippets/, or assets/*.liquid.

Snippets that are intentionally orphan during the P4 → P8 migration
(custom-theme.liquid, 7 deferred custom-theme.js wrappers, etc.) are
allowlisted in os2-migration/intentionally-orphan.txt with a bd-id and
target wire-by date. Entries past their target date emit a warning but
don't fail the lint (the deadline is a soft signal, not a hard gate).

Exit codes:
  0 — clean (no un-allowlisted orphans)
  1 — at least one orphan snippet not in the allowlist
  2 — invocation error (missing allowlist, etc.)

Usage:
  python3 scripts/check-snippet-wiring.py             # report + exit code
  python3 scripts/check-snippet-wiring.py --json      # machine-readable
  python3 scripts/check-snippet-wiring.py --verbose   # show every snippet
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
ALLOWLIST = REPO / "os2-migration" / "intentionally-orphan.txt"

# Directories that may reference a snippet via {% render '<name>' %}
SEARCH_DIRS = [
    REPO / "layout",
    REPO / "sections",
    REPO / "templates",
    REPO / "snippets",
    REPO / "blocks",
    REPO / "assets",  # *.liquid asset files can call render too
]

# Regex matches both `render 'foo'` and `render "foo"` and `include 'foo'`.
# Liquid permits whitespace and optional `-` for whitespace trimming inside
# the tag opener; the snippet name is always a literal string in our codebase
# (we don't dynamically resolve `render snippet_name_var` anywhere — verified
# via `grep -rE "render [a-z_]+\b" snippets/ sections/ layout/` returning 0
# rows. If that ever changes, dynamic renders need an allowlist exception.)
REFERENCE_RE = re.compile(r"""\{%-?\s*(?:render|include)\s+['"]([^'"]+)['"]""")


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


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON report")
    ap.add_argument("--verbose", action="store_true", help="show every snippet with its references")
    args = ap.parse_args(argv[1:])

    snippets = discover_snippets()
    refs = discover_references()
    allow = load_allowlist()

    orphans_blocking: list[dict] = []   # not in allowlist → fail
    orphans_allowed: list[dict] = []    # in allowlist → ok (maybe with stale warning)
    used: list[dict] = []
    today = datetime.date.today()

    for snippet in snippets:
        name = snippet.stem  # filename without .liquid
        referrers = refs.get(name, [])
        # Self-reference doesn't count — a snippet rendering itself isn't enough
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

    # Compose report
    if args.json:
        print(json.dumps({
            "snippets_total": len(snippets),
            "used": len(used),
            "orphans_blocking": orphans_blocking,
            "orphans_allowed": orphans_allowed,
            "passed": len(orphans_blocking) == 0,
        }, indent=2))
    else:
        print(f"Snippet wiring lint — scanned {len(snippets)} snippets")
        print(f"  ✓ wired:           {len(used)}")
        print(f"  ⚠ allowed orphans: {len(orphans_allowed)}")
        print(f"  ✗ BLOCKING orphans: {len(orphans_blocking)}")
        print()
        if orphans_blocking:
            print("BLOCKING — snippets that exist but are not rendered/included anywhere:")
            print("  These are most likely the result of a refactor that dropped a {% render %}")
            print("  callsite. Either (a) re-add the render call, (b) delete the snippet, or")
            print("  (c) add the snippet to os2-migration/intentionally-orphan.txt with a")
            print("  bd-id + target_wire_by date.")
            print()
            for o in orphans_blocking:
                print(f"    ✗ {o['path']}")
            print()
        if orphans_allowed:
            stale_n = sum(1 for o in orphans_allowed if o["stale"])
            print(f"Allowlisted orphans ({len(orphans_allowed)} total, {stale_n} past target date):")
            for o in sorted(orphans_allowed, key=lambda x: (not x["stale"], x["name"])):
                marker = "STALE " if o["stale"] else "      "
                print(f"    {marker}{o['name']:35s} bd={o['bd_id']:10s} wire_by={o['target_wire_by']}  {o['reason']}")
            print()
        if args.verbose:
            print("Wired snippets (for reference):")
            for u in used:
                print(f"    ✓ {u['name']:40s} {u['referrer_count']} referrers")

    return 1 if orphans_blocking else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
