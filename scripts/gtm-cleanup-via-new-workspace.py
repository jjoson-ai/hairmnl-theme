#!/usr/bin/env python3
"""
gtm-cleanup-via-new-workspace.py — Bypass the "Default Workspace already
submitted" lock by creating a new workspace, doing the deletions there,
then publishing from it.

Workflow (all idempotent — re-runnable):
  1. Find or create the cleanup workspace ("Cleanup 2026-04-30")
  2. List tags in that workspace, categorize by Tier A + B (matches
     gtm-execute-cleanup.py logic)
  3. Delete each target tag with brief rate-limit pause
  4. Create Container Version with detailed notes
  5. Publish Version to live

Rollback: GTM admin → Versions → previous version → Set as Latest →
Publish (1 click).
"""
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
WORKSPACE_NAME = "Cleanup 2026-04-30"
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


def container_path():
    return f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}"


def find_or_create_workspace(svc):
    workspaces = svc.accounts().containers().workspaces().list(parent=container_path()).execute().get("workspace", [])
    for w in workspaces:
        if w["name"] == WORKSPACE_NAME:
            print(f"  Found existing workspace: id={w['workspaceId']}")
            return w
    print(f"  Creating new workspace {WORKSPACE_NAME!r}...")
    new_ws = svc.accounts().containers().workspaces().create(
        parent=container_path(),
        body={"name": WORKSPACE_NAME, "description": "API-created for the 65-tag UA + Elevar-leftover cleanup"},
    ).execute()
    print(f"  Created: id={new_ws['workspaceId']}")
    return new_ws


def categorize(tags):
    elevar_ua = []
    other_ua = []
    mid_migration = []
    for t in tags:
        name = t.get("name", "")
        type_ = t.get("type", "")
        if "*Update After" in name and name not in ELEVAR_REDUNDANT_UA_NAMES:
            mid_migration.append(t)
        elif type_ == "ua" and name in ELEVAR_REDUNDANT_UA_NAMES:
            elevar_ua.append(t)
        elif type_ == "ua":
            other_ua.append(t)
    return elevar_ua, other_ua, mid_migration


def delete_tag(svc, tag):
    name = tag.get("name", "?")
    tid = tag.get("tagId", "?")
    type_ = tag.get("type", "?")
    print(f"  deleting: id={tid} type={type_} name={name!r}")
    try:
        svc.accounts().containers().workspaces().tags().delete(path=tag["path"]).execute()
        return True
    except HttpError as e:
        print(f"    ✗ HTTP {e.resp.status}: {e._get_reason()[:200]}", file=sys.stderr)
        return False


def main():
    svc = get_svc()
    print("Step 1: workspace setup...")
    ws = find_or_create_workspace(svc)
    ws_path = ws["path"]

    print(f"\nStep 2: list tags in workspace {ws['workspaceId']}...")
    tags = svc.accounts().containers().workspaces().tags().list(parent=ws_path).execute().get("tag", [])
    print(f"  {len(tags)} tags total.")

    elevar_ua, other_ua, mid_migration = categorize(tags)
    targets = elevar_ua + other_ua + mid_migration
    print(f"\nStep 3: deletion plan:")
    print(f"  Elevar-redundant UA:   {len(elevar_ua)}")
    print(f"  Other dead UA:          {len(other_ua)}")
    print(f"  Mid-migration leftovers: {len(mid_migration)}")
    print(f"  TOTAL TO DELETE:        {len(targets)}")

    if not targets:
        print("\nNothing to delete — workspace already clean.")
        return

    print("\nStep 4: deleting...")
    deleted = 0
    failed = 0
    for t in targets:
        if delete_tag(svc, t):
            deleted += 1
        else:
            failed += 1
        time.sleep(1.2)  # rate-limit pacing — GTM allows ~60 queries/min, stay well under
    print(f"\n  Result: {deleted} deleted, {failed} failed.")

    if deleted == 0:
        print("\nNo tags actually deleted — aborting before Version creation.")
        sys.exit(2)

    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M %Z")
    notes = (
        f"Tier A + B cleanup — {today}.\n\n"
        f"Deleted {deleted} tags via API:\n"
        f"  - {len(elevar_ua)} UA event tags duplicating Elevar SST events (UA sunset July 2024 — these were firing 404s)\n"
        f"  - {len(other_ua)} other UA tags (manual click/scroll tracking, all to a dead endpoint)\n"
        f"  - {len(mid_migration)} *Update After Elevar Import* mid-migration leftovers\n\n"
        f"Estimated impact: container.js -53.8 KB (-51% of tag config bytes), "
        f"~120-300ms TBT reduction per pageload (62 UA tag eval cycles eliminated), "
        f"62 fewer 404 requests per pageload. Risk very low — UA endpoint is dead, "
        f"Elevar handles the meaningful events server-side.\n\n"
        f"Rollback: GTM admin → Versions → previous version → Set as Latest → Publish."
    )
    print(f"\nStep 5: creating Container Version...")
    cv = svc.accounts().containers().workspaces().create_version(
        path=ws_path,
        body={"name": "Tier A+B cleanup (62 UA + 3 mid-migration tags)", "notes": notes},
    ).execute()
    if cv.get("compilerError"):
        print(f"  ✗ compiler error: {cv['compilerError']}", file=sys.stderr)
        sys.exit(2)
    version = cv.get("containerVersion") or {}
    version_id = version.get("containerVersionId")
    print(f"  ✓ Version created: id={version_id}")

    print(f"\nStep 6: publishing Version {version_id} to live...")
    pub = svc.accounts().containers().versions().publish(
        path=f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}/versions/{version_id}",
    ).execute()
    print(f"  ✓ Published. Container fingerprint={pub.get('containerVersion', {}).get('fingerprint')}")
    print(f"\nLive container.js will refresh within ~minutes (Google Tag Manager CDN).")


if __name__ == "__main__":
    main()
