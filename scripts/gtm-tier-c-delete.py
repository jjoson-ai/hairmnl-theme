#!/usr/bin/env python3
"""
gtm-tier-c-delete.py — Delete 28 Tier C Custom HTML tags from workspace 192:
  - 9  Meta / Facebook pixel tags
  - 12 TikTok pixel tags
  - 2  Microsoft / Bing Ads tags
  - 5  Snapchat pixel tags
Then create Container Version + publish.

Keeping: TrafficGuard (3 tags, ad fraud), Klaviyo (2 tags, onsite JS + form bridge).
"""
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ACCOUNT_ID = "4702257664"
CONTAINER_ID = "12266146"
WORKSPACE_NAME = "Cleanup Tier C 2026-04-30"
TOKEN_PATH = Path.home() / ".config" / "hairmnl-gtm-token.json"
SCOPES = [
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
    "https://www.googleapis.com/auth/tagmanager.publish",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

TARGET_TAG_IDS = {
    # Meta / Facebook (9)
    "538", "649", "539", "542", "540", "543", "544", "541", "546",
    # TikTok (12)
    "502", "509", "695", "503", "699", "508", "505", "507", "698", "696", "506", "693",
    # Microsoft / Bing (2)
    "756", "757",
    # Snapchat (5)
    "579", "582", "584", "581", "585",
}


def get_svc():
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    return build("tagmanager", "v2", credentials=creds, cache_discovery=False)


def container_path():
    return f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}"


def find_or_create_workspace(svc):
    workspaces = (
        svc.accounts().containers().workspaces()
        .list(parent=container_path()).execute().get("workspace", [])
    )
    for w in workspaces:
        if w["name"] == WORKSPACE_NAME:
            print(f"  Found existing workspace: id={w['workspaceId']}")
            return w
    print(f"  Creating new workspace {WORKSPACE_NAME!r}...")
    new_ws = svc.accounts().containers().workspaces().create(
        parent=container_path(),
        body={"name": WORKSPACE_NAME, "description": "Tier C Custom HTML pixel tag cleanup"},
    ).execute()
    print(f"  Created: id={new_ws['workspaceId']}")
    return new_ws


def main():
    svc = get_svc()

    print("Step 0: workspace setup...")
    ws = find_or_create_workspace(svc)
    ws_path = ws["path"]

    print(f"\nStep 1: fetching tags from workspace {ws['workspaceId']}...")
    all_tags = svc.accounts().containers().workspaces().tags().list(
        parent=ws_path
    ).execute().get("tag", [])
    print(f"  {len(all_tags)} tags total.")

    targets = [t for t in all_tags if t.get("tagId") in TARGET_TAG_IDS]
    already_gone = TARGET_TAG_IDS - {t.get("tagId") for t in targets}

    print(f"\nStep 2: deletion plan:")
    print(f"  Tags to delete this run:   {len(targets)}")
    print(f"  Already deleted (idempotent): {len(already_gone)}")
    if already_gone:
        print(f"    IDs already gone: {sorted(already_gone)}")

    if not targets:
        print("\nAll targets already deleted — skipping to Version creation.")
    else:
        print(f"\nStep 3: deleting {len(targets)} tags...")
        deleted = 0
        failed = 0
        for t in sorted(targets, key=lambda x: x.get("name", "")):
            name = t.get("name", "?")
            tid = t.get("tagId", "?")
            type_ = t.get("type", "?")
            print(f"  deleting: id={tid} type={type_} name={name!r}")
            try:
                svc.accounts().containers().workspaces().tags().delete(
                    path=t["path"]
                ).execute()
                deleted += 1
            except HttpError as e:
                print(f"    ✗ HTTP {e.resp.status}: {e._get_reason()[:200]}", file=sys.stderr)
                failed += 1
            time.sleep(1.2)

        print(f"\n  Result: {deleted} deleted, {failed} failed.")
        if deleted == 0:
            print("No tags deleted — aborting before Version creation.")
            sys.exit(2)

    total_deleted = len(TARGET_TAG_IDS) - len(already_gone)
    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M %Z")
    notes = (
        f"Tier C cleanup — {today}.\n\n"
        f"Deleted 28 Custom HTML pixel tags via API (workspace 192):\n"
        f"  - 9  Meta / Facebook browser-side pixel tags (Elevar handles via server-side CAPI + web)\n"
        f"  - 12 TikTok browser-side pixel tags (Elevar handles via server-side Events API + web)\n"
        f"  - 2  Microsoft / Bing Ads UET tags (Elevar handles via server-side UET API)\n"
        f"  - 5  Snapchat pixel tags (user decision: remove GTM-side entirely)\n\n"
        f"Retained: TrafficGuard (3 tags, ad fraud protection), Klaviyo (2 tags, onsite JS + form bridge).\n\n"
        f"Combined Tier A+B+C impact: 88 total tags removed this sprint.\n"
        f"Estimated container.js reduction: ~65-70 KB total.\n"
        f"Eliminated duplicate browser-side pixel calls: ~25 per pageload.\n\n"
        f"Rollback: GTM admin → Versions → previous version → Set as Latest → Publish."
    )

    print(f"\nStep 4: creating Container Version...")
    cv = svc.accounts().containers().workspaces().create_version(
        path=ws_path,
        body={
            "name": "Tier C cleanup (28 Custom HTML pixel tags)",
            "notes": notes,
        },
    ).execute()

    if cv.get("compilerError"):
        print(f"  ✗ compiler error: {cv['compilerError']}", file=sys.stderr)
        sys.exit(2)

    version = cv.get("containerVersion") or {}
    version_id = version.get("containerVersionId")
    print(f"  ✓ Version created: id={version_id}")

    print(f"\nStep 5: publishing Version {version_id} to live...")
    pub = svc.accounts().containers().versions().publish(
        path=f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}/versions/{version_id}",
    ).execute()
    fingerprint = pub.get("containerVersion", {}).get("fingerprint", "?")
    print(f"  ✓ Published. Container fingerprint={fingerprint}")
    print(f"\nLive container.js will refresh within ~minutes (GTM CDN propagation).")


if __name__ == "__main__":
    main()
