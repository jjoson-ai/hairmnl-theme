#!/usr/bin/env python3
"""
gtm-fix-cwv-template-vux.py — wire the missing `template` parameter onto
GTM tag 766 (GA4 – Web Vitals).

Background: bd hairmnl-theme-vux. Theme commit 64a0a6b (2026-05-06)
extended snippets/web-vitals-reporter.liquid to push `template:
{{ template | json }}` into the dataLayer for per-template CWV slicing.
But the corresponding GTM tag 766 (and the trigger 758) never had a
`template → {{template}}` mapping added to its eventSettingsTable, AND
no `template` Data Layer Variable was created. So 95.7% of LCP events
in GA4 land with `template = (not set)`.

This script:
  1. Finds-or-creates workspace `fix-cwv-template-2026-05-10`.
  2. Creates a Data Layer Variable named `template` (bare-name
     convention to match metric_rating, page_path, etc.) if missing.
  3. Updates tag 766 to add `template → {{template}}` to the
     eventSettingsTable list (preserves existing 7 entries verbatim).
  4. Creates Container Version V142 with descriptive notes.
  5. PUBLISHES V142. (User authorized autonomous fix.)

Defensive: the script is idempotent — re-running won't double-add
the parameter or duplicate the variable.
"""
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ACCOUNT_ID = "4702257664"
CONTAINER_ID = "12266146"
TAG_ID = "766"  # GA4 – Web Vitals
WORKSPACE_NAME = "fix-cwv-template-2026-05-10"
TOKEN_PATH = Path.home() / ".config" / "hairmnl-gtm-token.json"
SCOPES = [
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
    "https://www.googleapis.com/auth/tagmanager.publish",
    "https://www.googleapis.com/auth/tagmanager.manage.users",
    "https://www.googleapis.com/auth/gmail.compose",
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
                "Add `template` parameter to tag 766 (GA4 – Web Vitals) "
                "eventSettingsTable so per-template CWV slicing works. "
                "References bd hairmnl-theme-vux. "
                "Created 2026-05-10."
            ),
        },
    ).execute()
    print(f"  Created: id={new_ws['workspaceId']}")
    return new_ws


def list_workspace_variables(svc, ws_path):
    """List all variables in the workspace (paginated)."""
    items = []
    next_page = None
    while True:
        kw = {"parent": ws_path}
        if next_page:
            kw["pageToken"] = next_page
        resp = svc.accounts().containers().workspaces().variables().list(**kw).execute()
        items.extend(resp.get("variable", []))
        next_page = resp.get("nextPageToken")
        if not next_page:
            break
    return items


def find_or_create_template_variable(svc, ws_path):
    """Ensure a Data Layer Variable named exactly `template` exists.
    Matches the existing bare-name convention (metric_rating, page_path, etc.)."""
    variables = list_workspace_variables(svc, ws_path)
    for v in variables:
        if v.get("name") == "template" and v.get("type") == "v":
            # Confirm it reads dataLayer key 'template'
            params = {p.get("key"): p.get("value") for p in v.get("parameter", [])}
            if params.get("name") == "template":
                print(f"  Variable `template` already exists: id={v['variableId']}")
                return v
    print("  Creating Data Layer Variable `template` (reads dataLayer key 'template', dlVersion=2)...")
    body = {
        "name": "template",
        "type": "v",
        "parameter": [
            {"type": "integer", "key": "dataLayerVersion", "value": "2"},
            {"type": "boolean", "key": "setDefaultValue", "value": "false"},
            {"type": "template", "key": "name", "value": "template"},
        ],
    }
    new_var = svc.accounts().containers().workspaces().variables().create(
        parent=ws_path,
        body=body,
    ).execute()
    print(f"  ✓ Created: id={new_var['variableId']}  fingerprint={new_var.get('fingerprint')}")
    return new_var


def get_workspace_tag(svc, ws_path, tag_id):
    return svc.accounts().containers().workspaces().tags().get(
        path=f"{ws_path}/tags/{tag_id}"
    ).execute()


def add_template_to_event_settings(tag: dict) -> tuple[dict, bool]:
    """Mutate tag in-place to add `template → {{template}}` to eventSettingsTable.
    Returns (tag, mutated:bool). Idempotent — won't double-add."""
    for p in tag.get("parameter", []):
        if p.get("key") != "eventSettingsTable":
            continue
        if p.get("type") != "list":
            continue
        rows = p.get("list") or []
        # Idempotency check
        for row in rows:
            mp = {kv.get("key"): kv.get("value") for kv in row.get("map", [])}
            if mp.get("parameter") == "template":
                print(f"  Tag already has `template` row → no change needed.")
                return tag, False
        # Add the row
        new_row = {
            "type": "map",
            "map": [
                {"type": "template", "key": "parameter", "value": "template"},
                {"type": "template", "key": "parameterValue", "value": "{{template}}"},
            ],
        }
        rows.append(new_row)
        p["list"] = rows
        print(f"  Added `template → {{{{template}}}}` to eventSettingsTable. Rows now: {len(rows)}")
        return tag, True
    print("  ✗ ERROR: tag has no eventSettingsTable parameter")
    return tag, False


def main():
    svc = get_svc()
    print("=== GTM Fix: tag 766 missing `template` param (bd hairmnl-theme-vux) ===\n")

    print("Step 1: Setting up workspace...")
    ws = find_or_create_workspace(svc)
    ws_id = ws["workspaceId"]
    ws_path = ws["path"]
    print(f"  Workspace: {ws_id} | path: {ws_path}")

    print("\nStep 2: Ensure `template` variable exists...")
    var = find_or_create_template_variable(svc, ws_path)

    print(f"\nStep 3: Fetching tag {TAG_ID} from workspace...")
    tag = get_workspace_tag(svc, ws_path, TAG_ID)
    print(f"  Got tag: {tag['name']} (type={tag['type']}, fingerprint={tag.get('fingerprint')})")

    # Snapshot the current eventSettingsTable rows so we can show the diff
    pre_rows = []
    for p in tag.get("parameter", []):
        if p.get("key") == "eventSettingsTable":
            for row in p.get("list", []):
                mp = {kv.get("key"): kv.get("value") for kv in row.get("map", [])}
                pre_rows.append(mp)
    print(f"  Pre-fix eventSettingsTable parameters: {[r.get('parameter') for r in pre_rows]}")

    print("\nStep 4: Adding `template` mapping...")
    tag, mutated = add_template_to_event_settings(tag)
    if not mutated:
        print("  Tag already has the mapping — no version creation needed.")
        sys.exit(0)

    print("\nStep 5: PUT updated tag back to workspace...")
    updated_tag = svc.accounts().containers().workspaces().tags().update(
        path=tag["path"],
        body=tag,
    ).execute()
    post_rows = []
    for p in updated_tag.get("parameter", []):
        if p.get("key") == "eventSettingsTable":
            for row in p.get("list", []):
                mp = {kv.get("key"): kv.get("value") for kv in row.get("map", [])}
                post_rows.append(mp)
    print(f"  Post-fix eventSettingsTable parameters: {[r.get('parameter') for r in post_rows]}")
    print(f"  New fingerprint: {updated_tag.get('fingerprint')}")
    time.sleep(1)

    print("\nStep 6: Creating Container Version...")
    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M %Z")
    notes = (
        f"Wire missing `template` parameter to tag 766 (GA4 – Web Vitals) — {today}.\n\n"
        f"Issue: hairmnl-theme-vux (P1).\n"
        f"Theme commit 64a0a6b (2026-05-06) added `template` to dataLayer in\n"
        f"snippets/web-vitals-reporter.liquid for per-template CWV slicing, but\n"
        f"the corresponding GTM forwarding (tag 766 + DLV) was never created.\n"
        f"Result: 95.7% of CWV events in GA4 had `template = (not set)`.\n\n"
        f"Changes in this version:\n"
        f"- New Data Layer Variable `template` (var id {var['variableId']}, "
        f"reads dataLayer key 'template', dlVersion=2)\n"
        f"- Tag 766 eventSettingsTable now includes `template → {{{{template}}}}` "
        f"as the 8th row (preserves all 7 existing rows).\n\n"
        f"Verification 24h post-publish: dashboard `top_templates.LCP` should show "
        f"real Liquid template names (index, product, blog, collection.brand.davines-sis, etc.) "
        f"instead of (not set)."
    )
    cv = svc.accounts().containers().workspaces().create_version(
        path=ws_path,
        body={
            "name": "Wire `template` param to GA4 – Web Vitals (bd hairmnl-theme-vux)",
            "notes": notes,
        },
    ).execute()

    if cv.get("compilerError"):
        print(f"  ✗ compiler error: {cv['compilerError']}")
        sys.exit(2)

    version = cv.get("containerVersion") or {}
    version_id = version.get("containerVersionId")
    if not version_id:
        print(f"  ✗ no version_id returned. Response: {cv}")
        sys.exit(3)
    print(f"  ✓ Version created: {version_id}")

    admin_url = (
        f"https://tagmanager.google.com/#/container/accounts/{ACCOUNT_ID}"
        f"/containers/{CONTAINER_ID}/versions/{version_id}"
    )
    print(f"  Admin URL: {admin_url}")

    print(f"\nStep 7: Publishing version {version_id} (user authorized autonomous fix)...")
    pub_path = f"{container_path()}/versions/{version_id}"
    pub = svc.accounts().containers().versions().publish(path=pub_path).execute()
    pub_ver = (pub.get("containerVersion") or {}).get("containerVersionId")
    pub_compiler = pub.get("compilerError")
    print(f"  Publish response: containerVersionId={pub_ver} compilerError={pub_compiler}")
    if pub_compiler:
        print("  ✗ Compiler error during publish. NOT live.")
        sys.exit(4)

    print(f"\n=== ✓ Container Version {version_id} published ===")
    print(f"  Admin URL: {admin_url}")

    summary = {
        "bd": "hairmnl-theme-vux",
        "workspace_id": ws_id,
        "workspace_name": WORKSPACE_NAME,
        "version_id": version_id,
        "admin_url": admin_url,
        "tag_id": TAG_ID,
        "variable_id_created": var["variableId"],
        "pre_event_settings_keys": [r.get("parameter") for r in pre_rows],
        "post_event_settings_keys": [r.get("parameter") for r in post_rows],
        "published": True,
        "publish_response": {"versionId": pub_ver, "compilerError": pub_compiler},
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    out_path = Path("/tmp/gtm-fix-cwv-template-vux-result.json")
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\n  Summary saved to {out_path}")


if __name__ == "__main__":
    main()
