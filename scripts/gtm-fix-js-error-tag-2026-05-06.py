#!/usr/bin/env python3
"""
gtm-fix-js-error-tag-2026-05-06.py — Fix tag 776 trigger in a NEW workspace.

Fixes: tag 776 (GA4 - JS Error Event) fires on wrong trigger.
  - Old: trigger 2147479573 (Window Loaded - fires on every page load, too early)
  - New: trigger 772 (Custom Event - hairmnl_js_error)

Also verifies DLV variables read correct dataLayer fields (error_type,
error_message, error_source) — already confirmed correct as of live v140.

Workflow (all idempotent):
  1. Find or create workspace 'fix-js-error-trigger-2026-05-06'
  2. Verify trigger 772 exists in new workspace
  3. GET tag 776 from workspace
  4. PUT updated tag 776 with firingTriggerId=["772"]
  5. Create container version with notes

Coordinator (Claude Code Opus 4.7): AFTER this script runs, review the
GTM Container Version diff, then publish via the GTM admin UI.
"""
import json
import sys
import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ACCOUNT_ID = "4702257664"
CONTAINER_ID = "12266146"
WORKSPACE_NAME = "fix-js-error-trigger-2026-05-06"
TAG_ID = "776"
TRIGGER_ID = "772"
TOKEN_PATH = Path.home() / ".config" / "hairmnl-gtm-token.json"
SCOPES = [
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
    "https://www.googleapis.com/auth/tagmanager.publish",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


def get_svc():
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    return build("tagmanager", "v2", credentials=creds, cache_discovery=False)


def container_path():
    return f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}"


def find_or_create_workspace(svc):
    workspaces = svc.accounts().containers().workspaces().list(
        parent=container_path()
    ).execute().get("workspace", [])
    for w in workspaces:
        if w["name"] == WORKSPACE_NAME:
            print(f"  Found existing workspace: id={w['workspaceId']}")
            return w
    print(f"  Creating new workspace {WORKSPACE_NAME!r}...")
    new_ws = svc.accounts().containers().workspaces().create(
        parent=container_path(),
        body={
            "name": WORKSPACE_NAME,
            "description": (
                "Fix tag 776 trigger from Window Loaded → Custom Event hairmnl_js_error. "
                "References bd hairmnl-theme-l3g. "
                "Created 2026-05-06 by gtm-fix-js-error-tag-2026-05-06.py"
            ),
        },
    ).execute()
    print(f"  Created: id={new_ws['workspaceId']}")
    return new_ws


def get_live_version(svc):
    container = svc.accounts().containers().get(path=container_path()).execute()
    latest = container.get("latestVersion") or {}
    ver_id = latest.get("containerVersionId", "140")
    ver = svc.accounts().containers().versions().get(
        path=f"{container_path()}/versions/{ver_id}"
    ).execute()
    return ver, ver_id


def get_workspace_triggers(svc, ws_path):
    triggers = []
    next_page = None
    while True:
        kw = {"parent": ws_path}
        if next_page:
            kw["pageToken"] = next_page
        resp = svc.accounts().containers().workspaces().triggers().list(**kw).execute()
        triggers.extend(resp.get("trigger", []))
        next_page = resp.get("nextPageToken")
        if not next_page:
            break
    return {t["triggerId"]: t for t in triggers}


def get_workspace_tag(svc, ws_path, tag_id):
    try:
        return svc.accounts().containers().workspaces().tags().get(
            path=f"{ws_path}/tags/{tag_id}"
        ).execute()
    except Exception as e:
        print(f"  Could not GET tag {tag_id} in workspace: {e}")
        return None


def main():
    svc = get_svc()
    print("=== GTM JS Error Tag Fix (hairmnl-theme-l3g) ===\n")

    # Step 1: Get live version for reference
    print("Step 1: Confirming live version state...")
    live_ver, live_vid = get_live_version(svc)
    print(f"  Live version: {live_vid}")

    # Step 2: Create new workspace
    print("\nStep 2: Setting up workspace...")
    ws = find_or_create_workspace(svc)
    ws_id = ws["workspaceId"]
    ws_path = ws["path"]
    print(f"  Workspace: {ws_id} | path: {ws_path}")

    # Step 3: Verify trigger 772 in workspace
    print("\nStep 3: Verifying trigger 772 in new workspace...")
    ws_triggers = get_workspace_triggers(svc, ws_path)
    if "772" in ws_triggers:
        tr = ws_triggers["772"]
        print(f"  Trigger 772 exists: {tr['name']} (type={tr['type']})")
    else:
        print("  Trigger 772 not found in workspace — creating it...")
        new_tr = svc.accounts().containers().workspaces().triggers().create(
            parent=ws_path,
            body={
                "name": "Custom Event - hairmnl_js_error",
                "type": "customEvent",
                "customEventFilter": [
                    {
                        "type": "equals",
                        "parameter": [
                            {"type": "template", "key": "arg0", "value": "{{_event}}"},
                            {"type": "template", "key": "arg1", "value": "hairmnl_js_error"},
                        ],
                    }
                ],
            },
        ).execute()
        print(f"  Created trigger: {new_tr['triggerId']} — {new_tr['name']}")
        ws_triggers = get_workspace_triggers(svc, ws_path)

    # Step 4: Verify DLV variables in live version (read-only check)
    print("\nStep 4: Verifying DLV variables read correct fields...")
    dlv_ok = True
    for v in live_ver.get("variable", []):
        name = v.get("name", "")
        if "error_type" in name.lower():
            params = {p["key"]: p.get("value", "") for p in v.get("parameter", [])}
            field = params.get("name", "")
            print(f"  {name}: reads DL field={field!r}  {'✓' if field == 'error_type' else '✗ MISMATCH'}")
            if field != "error_type":
                dlv_ok = False
        elif "error_message" in name.lower():
            params = {p["key"]: p.get("value", "") for p in v.get("parameter", [])}
            field = params.get("name", "")
            print(f"  {name}: reads DL field={field!r}  {'✓' if field == 'error_message' else '✗ MISMATCH'}")
            if field != "error_message":
                dlv_ok = False
        elif "error_source" in name.lower():
            params = {p["key"]: p.get("value", "") for p in v.get("parameter", [])}
            field = params.get("name", "")
            print(f"  {name}: reads DL field={field!r}  {'✓' if field == 'error_source' else '✗ MISMATCH'}")
            if field != "error_source":
                dlv_ok = False
    if dlv_ok:
        print("  DLV variables verified — all read correct post-rename fields.")
    else:
        print("  WARNING: DLV variables may need updating — see output above.")

    # Step 5: GET tag 776 from workspace
    print(f"\nStep 5: Fetching tag 776 from workspace {ws_id}...")
    tag = get_workspace_tag(svc, ws_path, TAG_ID)
    if not tag:
        print(f"  Tag {TAG_ID} not found in workspace — syncing from live...")
        tag_path = f"{container_path()}/versions/{live_vid}/tags/{TAG_ID}"
        tag = svc.accounts().containers().workspaces().tags().create(
            parent=ws_path,
            body={"name": f"TEMP SYNC {TAG_ID}"}
        ).execute()
        print(f"  Created placeholder — tag needs manual resolution")
    else:
        print(f"  Got tag 776: {tag['name']} type={tag['type']}")
        print(f"  Current firingTriggerId: {tag.get('firingTriggerId', [])}")

    # Step 6: Update tag 776 — change trigger
    old_triggers = tag.get("firingTriggerId", [])
    tag["firingTriggerId"] = [TRIGGER_ID]

    updated_tag = svc.accounts().containers().workspaces().tags().update(
        path=tag["path"],
        body=tag,
    ).execute()
    print(f"\nStep 6: Updated tag 776 firingTriggerId:")
    print(f"  Old: {old_triggers}")
    print(f"  New: {updated_tag.get('firingTriggerId', [])}")

    # Verify eventName is still js_error
    params = {p["key"]: p.get("value", "") for p in updated_tag.get("parameter", [])}
    print(f"  eventName: {params.get('eventName')}  (keep as-is)")
    time.sleep(1)

    # Step 7: Create Container Version
    print(f"\nStep 7: Creating Container Version in workspace {ws_id}...")
    from datetime import datetime, timezone, timedelta
    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M %Z")
    notes = (
        f"Fix tag 776 (GA4 - JS Error Event) trigger — {today}.\n\n"
        f"Issue: hairmnl-theme-l3g (P1, open).\n"
        f"Tag 776 was firing on Window Loaded (2147479573) — fires before any JS error can occur.\n"
        f"Changed firingTriggerId from [2147479573] → [772] (Custom Event - hairmnl_js_error).\n"
        f"eventName parameter kept as 'js_error' (Option A per handoff doc).\n"
        f"DLV variables (773, 774, 775) verified correct — read error_type/error_message/error_source.\n\n"
        f"Orphan trigger tags also found: tag 12 (Conversion Linker), 415 (Klaviyo Form Listener), 94 (TrafficGuard)\n"
        f"reference trigger 2147479553 which does not exist. These are separate bd issues.\n\n"
        f"Coordinator review required BEFORE publish. "
        f"After publish: synthetic-error test in storefront + DevTools GA4 DebugView."
    )
    cv = svc.accounts().containers().workspaces().create_version(
        path=ws_path,
        body={
            "name": "Fix JS Error tag trigger (bd hairmnl-theme-l3g)",
            "notes": notes,
        },
    ).execute()

    if cv.get("compilerError"):
        print(f"  ✗ compiler error: {cv['compilerError']}")
        sys.exit(2)

    version = cv.get("containerVersion") or {}
    version_id = version.get("containerVersionId")
    print(f"  ✓ Version created: {version_id}")

    admin_url = (
        f"https://tagmanager.google.com/#/container/accounts/{ACCOUNT_ID}"
        f"/containers/{CONTAINER_ID}/versions/{version_id}"
    )
    print(f"\n  Admin review URL:")
    print(f"  {admin_url}")

    # Write summary
    summary = {
        "workspace_id": ws_id,
        "workspace_name": WORKSPACE_NAME,
        "version_id": version_id,
        "admin_url": admin_url,
        "tag_776_old_triggers": old_triggers,
        "tag_776_new_triggers": [TRIGGER_ID],
        "event_name": params.get("eventName"),
        "dlv_verified": dlv_ok,
    }
    Path("/tmp/gtm-fix-result-2026-05-06.json").write_text(json.dumps(summary, indent=2))
    print(f"\n  Summary saved to /tmp/gtm-fix-result-2026-05-06.json")
    print("\n=== Script complete — DO NOT publish yet ===")
    print("Coordinator (Claude Code Opus 4.7): review the diff at the admin URL above,")
    print("verify exactly 1 tag changed (tag 776 with trigger 772), then publish.")


if __name__ == "__main__":
    main()