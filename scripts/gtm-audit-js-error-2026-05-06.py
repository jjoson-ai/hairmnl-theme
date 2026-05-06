#!/usr/bin/env python3
"""
gtm-audit-js-error-2026-05-06.py — Targeted audit for hairmnl-theme-l3g.

Confirms:
1. Live container version is 140
2. Tag 776 (GA4 - JS Error Event) current state
3. Trigger 772 exists and is Custom Event hairmnl_js_error
4. DLV variables for error_type/error_message/error_source
5. Tags 12, 415, 94 reference orphan trigger 2147479553
"""
import json
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ACCOUNT_ID = "4702257664"
CONTAINER_ID = "12266146"
TOKEN_PATH = Path.home() / ".config" / "hairmnl-gtm-token.json"
SCOPES = [
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
    "https://www.googleapis.com/auth/tagmanager.publish",
    "https://www.googleapis.com/auth/tagmanager.manage.users",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


def get_svc():
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    return build("tagmanager", "v2", credentials=creds, cache_discovery=False)


def container_path():
    return f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}"


def get_live_version(svc):
    """Get the live container version by fetching the container and looking at LatestVersion."""
    container = svc.accounts().containers().get(
        path=container_path()
    ).execute()
    latest = container.get("latestVersion") or {}
    version_id = latest.get("containerVersionId", "140")
    print(f"  Container path: {container_path()}")
    print(f"  Latest version ID from container: {version_id}")
    fingerprint = latest.get("fingerprint", "?")
    print(f"  Fingerprint: {fingerprint}")

    # Get that specific version
    ver = svc.accounts().containers().versions().get(
        path=f"{container_path()}/versions/{version_id}"
    ).execute()
    return ver, version_id


def main():
    svc = get_svc()

    print("=== GTM Audit for hairmnl-theme-l3g ===\n")

    # 1. Get live container version
    print("Step 1: Finding live container version...")
    live_version, version_id = get_live_version(svc)

    print(f"  Live version: {live_version['containerVersionId']}")
    fingerprint = live_version.get('fingerprint', '?')
    print(f"  Fingerprint: {fingerprint}")

    tags_by_id = {t['tagId']: t for t in live_version.get('tag', [])}
    triggers_by_id = {t['triggerId']: t for t in live_version.get('trigger', [])}
    variables_by_id = {v['variableId']: v for v in live_version.get('variable', [])}

    # Save full audit
    audit = {
        "live_version_id": live_version.get('containerVersionId') or version_id,
        "fingerprint": fingerprint,
        "tag_count": len(tags_by_id),
        "trigger_count": len(triggers_by_id),
        "variable_count": len(variables_by_id),
    }

    # 2. Tag 776
    print("\nStep 2: Tag 776 (GA4 - JS Error Event)...")
    if "776" in tags_by_id:
        t = tags_by_id["776"]
        print(f"  Name: {t['name']}")
        print(f"  Type: {t['type']}")
        print(f"  Firing triggers: {t.get('firingTriggerId', [])}")

        firing_names = []
        for tid in t.get('firingTriggerId', []):
            if tid in triggers_by_id:
                firing_names.append(f"{triggers_by_id[tid].get('name','?')} (id={tid})")
            elif tid == "2147479553":
                firing_names.append(f"ALL PAGES (built-in, id={tid})")
            elif tid == "2147479572":
                firing_names.append(f"DOM READY (built-in, id={tid})")
            elif tid == "2147479573":
                firing_names.append(f"WINDOW LOADED (built-in, id={tid})")
            else:
                firing_names.append(f"id={tid} (ORPHAN)")
        print(f"  Trigger names: {firing_names}")

        # Find eventName and eventSettingsTable
        params = {p['key']: p.get('value', '') for p in t.get('parameter', [])}
        print(f"  eventName: {params.get('eventName', 'NOT SET')}")
        print(f"  eventSettingsTable: {json.dumps(params.get('eventSettingsTable', []), indent=4)}")

        audit["tag_776"] = {
            "name": t["name"],
            "type": t["type"],
            "firing_trigger_ids": t.get("firingTriggerId", []),
            "trigger_names": firing_names,
            "eventName": params.get('eventName'),
            "eventSettingsTable": params.get('eventSettingsTable', []),
        }
    else:
        print("  NOT FOUND")

    # 3. Trigger 772
    print("\nStep 3: Trigger 772 (Custom Event - hairmnl_js_error)...")
    if "772" in triggers_by_id:
        tr = triggers_by_id["772"]
        print(f"  Name: {tr['name']}")
        print(f"  Type: {tr['type']}")
        filter_info = tr.get('filter', [])
        print(f"  Filter: {json.dumps(filter_info)}")
        audit["trigger_772"] = {
            "name": tr["name"],
            "type": tr["type"],
            "filter": filter_info,
        }
    else:
        print("  NOT FOUND")

    # 4. DLV variables for error fields
    print("\nStep 4: DLV variables for error_type/error_message/error_source...")
    dlv_results = {}
    for v in live_version.get('variable', []):
        name = v.get('name', '')
        if 'error' in name.lower() and 'dlv' in name.lower():
            params = {p['key']: p.get('value', '') for p in v.get('parameter', [])}
            print(f"  {name}: type={v['type']}, dataLayerVar={params.get('dataLayerVar', '?')}")
            dlv_results[name] = params.get('dataLayerVar', '?')

    audit["dlv_error_vars"] = dlv_results

    # 5. Orphan trigger tags
    print("\nStep 5: Tags referencing orphan trigger 2147479553...")
    orphan_tags = []
    for tid, t in tags_by_id.items():
        if "2147479553" in t.get('firingTriggerId', []):
            orphan_tags.append({"tagId": tid, "name": t['name'], "type": t['type']})
            print(f"  Tag {tid}: {t['name']} (type={t['type']})")

    audit["orphan_trigger_tags"] = orphan_tags

    print(f"\nAudit complete. Saving to /tmp/gtm-audit-2026-05-06.json")
    Path("/tmp/gtm-audit-2026-05-06.json").write_text(json.dumps(audit, indent=2))
    print(f"  Saved {len(json.dumps(audit))} bytes")


if __name__ == "__main__":
    main()