#!/usr/bin/env python3
"""
gtm-fix-metric-rating-2026-05-11.py — Add `metric_rating` event parameter to
tag 771 (GA4 - Web Vital Event) in the HairMNL GTM container.

Issue:      bd hairmnl-theme-d00
Container:  GTM-M4NKSBD (account 4702257664, container 12266146)
Workspace:  fix-metric-rating-2026-05-11 (workspace id 200)
Version:    143 (created, NOT published — coordinator must review)

Background:
  Tag 766 (GA4 – Web Vitals) already correctly maps metric_rating → {{metric_rating}}.
  Tag 771 (GA4 - Web Vital Event) was missing this mapping.
  The "web_vital" event name path fires for ALL CWV events (LCP/CLS/INP/FCP/TTFB)
  when triggered by the Custom Event - web_vital trigger (767).
  Without metric_rating on tag 771, ~50-60% of CWV events land with metric_rating=(not set).

Audit findings (live container v142):
  Tag 766 (GA4 – Web Vitals):
    - Trigger: Web Vitals (LCP/CLS/INP/FCP/TTFB) — trigger id 758
    - eventName: {{Event}}
    - eventSettingsTable (8 params): metric_rating, metric_value, metric_delta,
      metric_id, metric_navigation_type, debug_target, page_path, template
    - ✓ metric_rating IS mapped

  Tag 771 (GA4 - Web Vital Event):
    - Trigger: Custom Event - web_vital — trigger id 767
    - eventName: web_vital
    - eventSettingsTable (3 params BEFORE fix): metric_name, metric_value, metric_id
    - ✗ metric_rating was MISSING

  Variable metric_rating (id=759, dl_name=metric_rating, dlVersion=2) already existed.

Fix applied in workspace 200:
  - Tag 771 eventSettingsTable now includes metric_rating → {{metric_rating}}
    (adds as 4th param; preserves existing 3)

Verification:
  1. Get version 143: https://tagmanager.google.com/#/container/accounts/4702257664/containers/12266146/versions/143
  2. Confirm tag 771 has 4 eventSettingsTable params including metric_rating
  3. Publish version 143
  4. 24h post-publish: dashboard 'CWV Rating' pie should show good/needs-improvement/poor
     vs previous ~50-60% unknown/(not set)
"""

import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ACCOUNT_ID = "4702257664"
CONTAINER_ID = "12266146"
TAG_ID = "771"
WORKSPACE_NAME = "fix-metric-rating-2026-05-11"
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


def workspace_path(ws_id):
    return f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}/workspaces/{ws_id}"


def find_or_create_workspace(svc):
    """Find existing workspace or create fresh from live container."""
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
                "Add `metric_rating` parameter to tag 771 (GA4 - Web Vital Event). "
                "Tag 766 already has it; tag 771 was missing it. "
                "References bd hairmnl-theme-d00. Created 2026-05-11."
            ),
        },
    ).execute()
    print(f"  Created: id={new_ws['workspaceId']}")
    return new_ws


def get_tag(svc, ws_path, tag_id):
    return svc.accounts().containers().workspaces().tags().get(
        path=f"{ws_path}/tags/{tag_id}"
    ).execute()


def add_metric_rating_to_tag(svc, ws_path, tag: dict) -> tuple[dict, bool]:
    """Mutate tag in-place to add metric_rating → {{metric_rating}} to eventSettingsTable.
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
            if mp.get("parameter") == "metric_rating":
                print("  metric_rating already present in eventSettingsTable — no change needed.")
                return tag, False
        # Add the row
        new_row = {
            "type": "map",
            "map": [
                {"type": "template", "key": "parameter", "value": "metric_rating"},
                {"type": "template", "key": "parameterValue", "value": "{{metric_rating}}"},
            ],
        }
        rows.append(new_row)
        p["list"] = rows
        print(f"  Added metric_rating → {{{{metric_rating}}}} to eventSettingsTable. Rows now: {len(rows)}")
        return tag, True
    print("  ✗ ERROR: tag has no eventSettingsTable parameter")
    return tag, False


def create_version(svc, ws_path, name: str, notes: str):
    cv = svc.accounts().containers().workspaces().create_version(
        path=ws_path,
        body={"name": name, "notes": notes},
    ).execute()
    if cv.get("compilerError"):
        print(f"  ✗ compiler error: {cv['compilerError']}")
        return None
    version = cv.get("containerVersion") or {}
    version_id = version.get("containerVersionId")
    print(f"  ✓ Version created: id={version_id}")
    return version_id


def publish_version(svc, version_id: str):
    pub_path = f"{container_path()}/versions/{version_id}"
    pub = svc.accounts().containers().versions().publish(path=pub_path).execute()
    pub_ver = (pub.get("containerVersion") or {}).get("containerVersionId")
    pub_err = pub.get("compilerError")
    print(f"  Publish response: versionId={pub_ver} compilerError={pub_err}")
    if pub_err:
        print("  ✗ Compiler error during publish. NOT live.")
        return False
    print(f"  ✓ Version {version_id} published to live.")
    return True


def main():
    svc = get_svc()
    print("=== GTM Fix: tag 771 missing metric_rating param (bd hairmnl-theme-d00) ===\n")

    print("Step 1: Setting up workspace...")
    ws = find_or_create_workspace(svc)
    ws_id = ws["workspaceId"]
    ws_path = ws["path"]
    print(f"  Workspace: {ws_id} | path: {ws_path}")

    print(f"\nStep 2: Fetching tag {TAG_ID} from workspace...")
    tag = get_tag(svc, ws_path, TAG_ID)
    print(f"  Got tag: {tag['name']} (type={tag['type']}, fingerprint={tag.get('fingerprint')})")

    # Show current eventSettingsTable
    pre_rows = []
    for p in tag.get("parameter", []):
        if p.get("key") == "eventSettingsTable":
            for row in p.get("list", []):
                mp = {kv.get("key"): kv.get("value") for kv in row.get("map", [])}
                pre_rows.append(mp)
    print(f"  Pre-fix eventSettingsTable params: {[r.get('parameter') for r in pre_rows]}")

    print(f"\nStep 3: Adding metric_rating mapping...")
    tag, mutated = add_metric_rating_to_tag(svc, ws_path, tag)

    if not mutated:
        print("  Tag already has the mapping — skipping version creation.")
        sys.exit(0)

    print(f"\nStep 4: PUT updated tag back to workspace...")
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
    print(f"  Post-fix eventSettingsTable params: {[r.get('parameter') for r in post_rows]}")
    print(f"  New fingerprint: {updated_tag.get('fingerprint')}")
    time.sleep(1)

    print(f"\nStep 5: Creating Container Version...")
    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M %Z")
    notes = (
        f"Fix metric_rating param on CWV tag 771 — {today}.\n\n"
        f"Issue: hairmnl-theme-d00 (P2).\n"
        f"Tag 766 (GA4 – Web Vitals) correctly maps metric_rating → {{metric_rating}}.\n"
        f"Tag 771 (GA4 - Web Vital Event) was missing this mapping, causing\n"
        f"~50-60% of CWV events to show metric_rating = (not set) in GA4.\n\n"
        f"Changes in this version:\n"
        f"- Tag 771 eventSettingsTable now includes metric_rating → {{{{metric_rating}}}}\n"
        f"  (adds 4th param; preserves existing metric_name, metric_value, metric_id).\n\n"
        f"Variable metric_rating (id=759) already existed — no new variable needed.\n\n"
        f"Verification 24h post-publish: dashboard 'CWV Rating' pie should show\n"
        f"good/needs-improvement/poor buckets vs the previous ~50-60% unknown split."
    )
    version_id = create_version(
        svc, ws_path,
        name="Fix metric_rating param on CWV tags (bd hairmnl-theme-d00)",
        notes=notes,
    )

    if not version_id:
        sys.exit(1)

    admin_url = (
        f"https://tagmanager.google.com/#/container/accounts/{ACCOUNT_ID}"
        f"/containers/{CONTAINER_ID}/versions/{version_id}"
    )
    print(f"\n  Admin URL: {admin_url}")

    # Summary output for handoff
    summary = {
        "bd": "hairmnl-theme-d00",
        "workspace_id": ws_id,
        "workspace_name": WORKSPACE_NAME,
        "workspace_path": ws_path,
        "version_id": version_id,
        "admin_url": admin_url,
        "tag_id": TAG_ID,
        "pre_event_settings_params": [r.get("parameter") for r in pre_rows],
        "post_event_settings_params": [r.get("parameter") for r in post_rows],
        "published": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    print(f"\nSummary: {json.dumps(summary, indent=2)}")


if __name__ == "__main__":
    main()