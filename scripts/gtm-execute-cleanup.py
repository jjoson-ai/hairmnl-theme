#!/usr/bin/env python3
"""
gtm-execute-cleanup.py — Execute the Tier A + B cleanup proposed by
gtm-elevar-cleanup-proposal.py.

Tier A (62 tags total):
  - 15 UA event tags duplicating Elevar SST events
  - 47 other UA tags (manual click/scroll tracking — UA endpoint sunset)
Tier B (3 tags):
  - "*Update After Elevar Import*" mid-migration leftovers

Process:
  1. List + categorize tags via the same logic as the proposal script.
  2. For each target tag: print, then DELETE via API. Continue on per-tag
     errors (don't abort the whole run).
  3. Create a Container Version with detailed notes.
  4. Publish the Version to live.

Rollback path: GTM keeps version history. To restore: GTM admin →
Versions → previous version → "Set as Latest" → Publish. 1 click.

Usage:
  python3 scripts/gtm-execute-cleanup.py --dry-run          # show what would happen
  python3 scripts/gtm-execute-cleanup.py --apply             # do the deletions + publish
  python3 scripts/gtm-execute-cleanup.py --apply --no-publish  # delete in workspace, don't publish (review in GTM admin)
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ACCOUNT_ID = "4702257664"
CONTAINER_ID = "12266146"
WORKSPACE_ID = "190"
TOKEN_PATH = Path.home() / ".config" / "hairmnl-gtm-token.json"
SCOPES = [
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
    "https://www.googleapis.com/auth/tagmanager.publish",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

ELEVAR_REDUNDANT_UA_NAMES = {
    "GA Event - Purchase",
    "GA Event - Add to Cart",
    "GA Event - Begin Checkout",
    "GA Event - Add Payment Info",
    "GA Event - Add Shipping Info",
    "GA Event - Product Detail View",
    "GA Event - Product List Impression",
    "GA Event - Product List Click",
    "GA Event - Search Results Impression",
    "GA Event - Remove from Cart",
    "GA Event - Cart Pageview",
    "GA Event - Login",
    "GA Event - Sign Up for Account",
    "GA - Pageview",
    "GA Event - Email Signup",
    "*Update After Import* GA Event - Email Signup",
}


def get_svc():
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    return build("tagmanager", "v2", credentials=creds, cache_discovery=False)


def workspace_path():
    return f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}/workspaces/{WORKSPACE_ID}"


def categorize(tags: list[dict]) -> dict:
    cats = {
        "tier_a_ua_elevar_redundant": [],
        "tier_a_ua_other_dead": [],
        "tier_b_mid_migration": [],
    }
    for t in tags:
        name = t.get("name", "")
        type_ = t.get("type", "")
        if "*Update After" in name and not name in ELEVAR_REDUNDANT_UA_NAMES:
            cats["tier_b_mid_migration"].append(t)
            continue
        if type_ == "ua" and name in ELEVAR_REDUNDANT_UA_NAMES:
            cats["tier_a_ua_elevar_redundant"].append(t)
            continue
        if type_ == "ua":
            cats["tier_a_ua_other_dead"].append(t)
            continue
    return cats


def delete_tag(svc, tag: dict, dry_run: bool) -> bool:
    """Returns True if deleted (or would be in dry-run), False if errored."""
    name = tag.get("name", "?")
    tid = tag.get("tagId", "?")
    type_ = tag.get("type", "?")
    print(f"  {'[DRY-RUN] would delete' if dry_run else 'deleting'}: id={tid} type={type_} name={name!r}")
    if dry_run:
        return True
    try:
        svc.accounts().containers().workspaces().tags().delete(path=tag["path"]).execute()
        return True
    except HttpError as e:
        print(f"    ✗ HTTP {e.resp.status}: {e._get_reason()[:200]}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"    ✗ ERROR: {str(e)[:200]}", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually delete (default: dry-run)")
    ap.add_argument("--no-publish", action="store_true", help="apply deletions in workspace but don't create Version + publish")
    ap.add_argument("--tiers", default="A,B", help="comma-sep tier list (A or B)")
    args = ap.parse_args()

    selected_tiers = set(t.strip().upper() for t in args.tiers.split(","))

    svc = get_svc()
    print("Loading current tag inventory...")
    tags = svc.accounts().containers().workspaces().tags().list(parent=workspace_path()).execute().get("tag", [])
    print(f"  {len(tags)} tags total in workspace.")

    cats = categorize(tags)
    targets = []
    if "A" in selected_tiers:
        targets.extend(cats["tier_a_ua_elevar_redundant"])
        targets.extend(cats["tier_a_ua_other_dead"])
    if "B" in selected_tiers:
        targets.extend(cats["tier_b_mid_migration"])

    print(f"\nDeletion plan ({len(targets)} tags across tier(s) {','.join(sorted(selected_tiers))}):")
    print(f"  Tier A — Elevar-redundant UA: {len(cats['tier_a_ua_elevar_redundant'])} tags ({'IN' if 'A' in selected_tiers else 'OUT'})")
    print(f"  Tier A — Other dead UA:        {len(cats['tier_a_ua_other_dead'])} tags ({'IN' if 'A' in selected_tiers else 'OUT'})")
    print(f"  Tier B — Mid-migration leftovers: {len(cats['tier_b_mid_migration'])} tags ({'IN' if 'B' in selected_tiers else 'OUT'})")

    if not targets:
        print("\nNothing to delete. Exiting.")
        return

    print()
    deleted = 0
    failed = 0
    for t in targets:
        if delete_tag(svc, t, dry_run=not args.apply):
            deleted += 1
        else:
            failed += 1
        # Brief pause to avoid GTM API rate limit (60 req/min default)
        if args.apply:
            time.sleep(0.4)

    print(f"\nDelete pass complete: {deleted} succeeded, {failed} failed.")

    if not args.apply:
        print("\n(DRY-RUN — re-run with --apply to actually delete.)")
        return

    if args.no_publish:
        print("\n--no-publish: deletions done in workspace draft. Review in GTM admin → Versions → 'Create Version' to publish.")
        return

    # Create Version + publish
    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M %Z")
    notes = (
        f"Tier A + B cleanup — {today}.\n\n"
        f"Deleted {deleted} tags via gtm-execute-cleanup.py:\n"
        f"  - 15 UA event tags duplicating Elevar SST events (UA sunset July 2024 — these were firing 404s)\n"
        f"  - 47 other UA tags (manual click/scroll tracking, all to a dead endpoint)\n"
        f"  - 3 *Update After Elevar Import* mid-migration leftovers\n\n"
        f"Estimated impact: container.js -53.8 KB (-51% of tag config bytes), "
        f"~120-300ms TBT reduction per pageload (62 UA tag eval cycles eliminated), "
        f"62 fewer 404 requests per pageload. Risk very low — UA endpoint is dead, "
        f"Elevar handles the meaningful events server-side.\n\n"
        f"Rollback: GTM admin → Versions → previous version → Set as Latest → Publish."
    )
    print(f"\nCreating Container Version...")
    cv = svc.accounts().containers().workspaces().create_version(
        path=workspace_path(),
        body={"name": "Tier A+B cleanup (62 UA + 3 mid-migration tags)", "notes": notes},
    ).execute()
    if cv.get("compilerError"):
        print(f"  ✗ compiler error: {cv['compilerError']}", file=sys.stderr)
        sys.exit(2)
    version = cv.get("containerVersion") or {}
    version_id = version.get("containerVersionId")
    print(f"  ✓ Version created: id={version_id}")

    print(f"\nPublishing Version {version_id} to live...")
    pub = svc.accounts().containers().versions().publish(
        path=f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}/versions/{version_id}",
    ).execute()
    print(f"  ✓ Published. Container fingerprint={pub.get('containerVersion', {}).get('fingerprint')}")
    print(f"\nLive container.js will refresh within ~minutes (Google Tag Manager CDN propagation).")


if __name__ == "__main__":
    main()
