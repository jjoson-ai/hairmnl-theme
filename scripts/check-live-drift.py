#!/usr/bin/env python3
"""
check-live-drift.py — compare the LIVE Shopify theme against git HEAD and
classify every difference.

WHY THIS EXISTS (bd hairmnl-theme-tvae, 2026-09-04): someone edited
sections/product.liquid directly on the live theme in the code editor, moving
a </div> above the product JSON scripts. Variant selection died on every
multi-variant PDP (customers could only buy the first size) and it was found
by a customer-facing report, not by us. The same editing session left three
other live-only edits that the next --only push from git would have silently
erased. Git HEAD is supposed to be the source of truth (CLAUDE.md "Git as
source of truth"); this script is how we find out when it is not.

WHAT IT DOES
  1. Pulls the live theme to a temp dir (or reuses --pulled-dir).
  2. For every theme file, compares bytes against `git show HEAD:<file>`.
  3. Classifies each difference:
       IDENTICAL       byte-equal (or trailing-newline-only difference)
       GIT AHEAD       live byte-matches an OLDER git commit of the file
                       (git has unpushed changes; live was never hand-edited)
       GIT AHEAD (line) no blob match, but every differing line is git-only
       LIVE EDITED     every differing line is live-only (someone added on live)
       DIVERGED        both sides changed — e.g. a MOVED line shows as one
                       git-only + one live-only line. This is the tvae shape.
       LIVE ONLY       file exists on live, not in git (apps, customizer JSON)
       GIT ONLY        file in git, not on live (draft-only work, deletions)
  4. Customizer state (config/settings_data.json, templates/*.json) is
     reported separately — it drifts by design and is never a code edit.

EXIT CODE: 1 if any LIVE EDITED or DIVERGED file exists outside customizer
state, else 0. Use it as a pre-flight gate before any live --only push, and
weekly on a schedule.

USAGE
  python3 scripts/check-live-drift.py                 # pull live, compare
  python3 scripts/check-live-drift.py --pulled-dir D  # reuse an existing pull
  python3 scripts/check-live-drift.py --json          # machine-readable
  python3 scripts/check-live-drift.py --theme 140785582179   # compare a draft

Requires the Shopify CLI to be logged in to the store (same as `shopify theme
pull`). Historical-blob matching uses `git log --all`, so keep old branches
around — they are what lets us say "live == commit X" instead of guessing.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import subprocess
import sys
import tempfile

# Theme IDs — keep in sync with CLAUDE.md "Theme IDs" (post-cutover 2026-08-04).
LIVE_THEME_ID = "141168312419"
STORE = "creations-gdc.myshopify.com"
THEME_DIRS = ("assets", "config", "layout", "locales", "sections", "snippets", "templates")


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, **kw)


def git_head_bytes(path: str) -> bytes | None:
    r = run(["git", "show", f"HEAD:{path}"])
    return r.stdout if r.returncode == 0 else None


def git_tracked_theme_files() -> set[str]:
    out = run(["git", "ls-tree", "-r", "HEAD", "--name-only"], text=True).stdout.split()
    return {p for p in out if p.split("/")[0] in THEME_DIRS}


def historical_match(path: str, live: bytes) -> str | None:
    """Return 'abc1234 (date subject)' if live byte-matches any past commit of path."""
    hashes = run(["git", "log", "--all", "--format=%h", "--", path], text=True).stdout.split()
    live_n = live.rstrip(b"\n")
    for h in hashes:
        blob = run(["git", "show", f"{h}:{path}"]).stdout
        if blob == live or blob.rstrip(b"\n") == live_n:
            meta = run(["git", "log", "-1", "--format=%ad %s", "--date=short", h], text=True).stdout.strip()
            return f"{h} ({meta[:70]})"
    return None


def line_delta(head: bytes, live: bytes) -> tuple[int, int]:
    """(git-only lines, live-only lines), whitespace-normalised per line."""
    h = [l.strip() for l in head.decode("utf-8", "ignore").splitlines()]
    l = [l.strip() for l in live.decode("utf-8", "ignore").splitlines()]
    git_only = live_only = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, h, l, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        git_only += i2 - i1
        live_only += j2 - j1
    return git_only, live_only


def is_customizer_state(path: str) -> bool:
    return path == "config/settings_data.json" or (path.startswith("templates/") and path.endswith(".json"))


def pull_theme(theme_id: str, dest: str) -> None:
    r = run(["shopify", "theme", "pull", f"--store={STORE}", f"--theme={theme_id}", f"--path={dest}", "--force"], text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:])
        sys.exit(f"shopify theme pull failed (exit {r.returncode})")


def classify(pulled: str) -> list[dict]:
    live_files: set[str] = set()
    for root, _, files in os.walk(pulled):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), pulled)
            if rel.split("/")[0] in THEME_DIRS:
                live_files.add(rel)
    git_files = git_tracked_theme_files()
    rows: list[dict] = []

    for path in sorted(live_files | git_files):
        row = {"file": path, "customizer": is_customizer_state(path)}
        if path not in git_files:
            row.update(status="LIVE ONLY", detail="not tracked in git")
            rows.append(row)
            continue
        if path not in live_files:
            row.update(status="GIT ONLY", detail="not on live")
            rows.append(row)
            continue
        head = git_head_bytes(path) or b""
        with open(os.path.join(pulled, path), "rb") as fh:
            live = fh.read()
        if head == live or head.rstrip(b"\n") == live.rstrip(b"\n"):
            continue  # identical — not reported
        git_only, live_only = line_delta(head, live)
        if row["customizer"]:
            row.update(status="CUSTOMIZER", detail=f"{git_only}/{live_only} lines git/live")
            rows.append(row)
            continue
        match = historical_match(path, live)
        if match:
            status, detail = "GIT AHEAD", f"live == git {match}; {git_only} unpushed line(s)"
        elif live_only == 0:
            status, detail = "GIT AHEAD (line)", f"{git_only} git-only line(s), no live-only lines"
        elif git_only == 0:
            status, detail = "LIVE EDITED", f"{live_only} line(s) added on live"
        else:
            status, detail = "DIVERGED", f"{git_only} git-only + {live_only} live-only line(s) — inspect (a moved line looks like this)"
        row.update(status=status, detail=detail)
        rows.append(row)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--theme", default=LIVE_THEME_ID, help=f"theme id to compare (default live {LIVE_THEME_ID})")
    ap.add_argument("--pulled-dir", help="reuse an existing `shopify theme pull` directory instead of pulling")
    ap.add_argument("--json", action="store_true", help="emit JSON rows instead of a table")
    args = ap.parse_args()

    if args.pulled_dir:
        pulled = args.pulled_dir
    else:
        pulled = tempfile.mkdtemp(prefix="live-drift-")
        print(f"pulling theme {args.theme} to {pulled} …", file=sys.stderr)
        pull_theme(args.theme, pulled)

    rows = classify(pulled)
    code = [r for r in rows if r["status"] in ("LIVE EDITED", "DIVERGED")]
    if args.json:
        print(json.dumps({"theme": args.theme, "pulled_dir": pulled, "rows": rows, "blocking": len(code)}, indent=2))
        return 1 if code else 0

    order = ["DIVERGED", "LIVE EDITED", "GIT AHEAD (line)", "GIT AHEAD", "GIT ONLY", "LIVE ONLY", "CUSTOMIZER"]
    print(f"\nLive theme {args.theme} vs git HEAD — {len(rows)} file(s) differ\n")
    for status in order:
        group = [r for r in rows if r["status"] == status]
        if not group:
            continue
        print(f"== {status} ({len(group)}) ==")
        shown = group if status != "CUSTOMIZER" else group[:8]
        for r in shown:
            print(f"  {r['file']:<58} {r['detail']}")
        if len(group) > len(shown):
            print(f"  … +{len(group) - len(shown)} more customizer-state files (expected drift)")
        print()
    if code:
        print(f"✗ {len(code)} file(s) were changed ON LIVE outside git. Reconcile before any live push:")
        print("  adopt into git if the edit is wanted (see bd 982g for the pattern), or push HEAD's copy if it is not.")
        return 1
    print("✓ no live-side code edits. Remaining differences are git-ahead (unpushed) or customizer state.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
