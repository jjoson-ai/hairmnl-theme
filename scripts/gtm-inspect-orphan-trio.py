#!/usr/bin/env python3
"""
gtm-inspect-orphan-trio.py — read-only inspection of the 3 tags whose
firingTriggerId references the deleted trigger 2147479553.

Outputs full configuration for tags 12 (Conversion Linker), 415 (Klaviyo
Form Submission Listener), 94 (TrafficGuard) so we can decide which
existing trigger to point each at — informed by vendor docs.

Also lists ALL triggers in the workspace, with key-points (type, name,
customEventFilter), so we can pick the right one for each tag.
"""
import json
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ACCOUNT_ID = "4702257664"
CONTAINER_ID = "12266146"
WORKSPACE_ID = "190"  # Default Workspace
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
TAG_IDS = ["12", "415", "94"]


def get_svc():
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    return build("tagmanager", "v2", credentials=creds, cache_discovery=False)


def workspace_path():
    return f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}/workspaces/{WORKSPACE_ID}"


def list_all(svc, kind):
    items = []
    method = getattr(svc.accounts().containers().workspaces(), kind)
    next_page = None
    while True:
        kw = {"parent": workspace_path()}
        if next_page:
            kw["pageToken"] = next_page
        resp = method().list(**kw).execute()
        items.extend(resp.get(kind[:-1], []))
        next_page = resp.get("nextPageToken")
        if not next_page:
            break
    return items


def main():
    svc = get_svc()
    tags = list_all(svc, "tags")
    triggers = list_all(svc, "triggers")
    triggers_by_id = {t["triggerId"]: t for t in triggers}
    tags_by_id = {t["tagId"]: t for t in tags}

    print(f"Total: {len(tags)} tags, {len(triggers)} triggers in workspace {WORKSPACE_ID}\n")

    # Dump each broken tag in full
    for tid in TAG_IDS:
        if tid not in tags_by_id:
            print(f"\n!! Tag {tid} not found in workspace !!\n")
            continue
        tag = tags_by_id[tid]
        print(f"\n========================================")
        print(f"Tag {tid}: {tag.get('name')!r}")
        print(f"  type: {tag.get('type')}")
        print(f"  paused: {tag.get('paused', False)}")
        print(f"  firingTriggerId: {tag.get('firingTriggerId', [])}")
        print(f"  blockingTriggerId: {tag.get('blockingTriggerId', [])}")
        print(f"  fingerprint: {tag.get('fingerprint')}")
        # Resolve trigger names where possible
        for trig_id in tag.get("firingTriggerId", []):
            if trig_id in triggers_by_id:
                tr = triggers_by_id[trig_id]
                print(f"    → trigger {trig_id} EXISTS: {tr.get('name')!r} (type={tr.get('type')})")
            else:
                print(f"    → trigger {trig_id} ORPHAN (does not exist)")
        # Full param dump
        print(f"  parameter:")
        for p in tag.get("parameter", []):
            k = p.get("key")
            t = p.get("type", "")
            v = p.get("value", "")
            if t == "list":
                print(f"    {k} (list):")
                for item in p.get("list", []):
                    summary = {kv.get("key"): kv.get("value") for kv in item.get("map", [])}
                    print(f"      {summary}")
            else:
                snippet = (v or "")[:200]
                print(f"    {k} = {snippet!r}  (type={t})")
        # Print HTML body if Custom HTML
        if tag.get("type") == "html":
            for p in tag.get("parameter", []):
                if p.get("key") == "html":
                    body = p.get("value", "")
                    print(f"\n  --- Custom HTML body ({len(body)} chars) ---")
                    print(body)
                    print(f"  --- end body ---")

    # Now list all triggers, summarized
    print(f"\n\n========================================")
    print(f"All {len(triggers)} triggers in workspace (for trigger-picking):\n")
    for t in sorted(triggers, key=lambda x: (x.get("type", ""), x.get("name", ""))):
        cef_summary = ""
        for f in t.get("customEventFilter", []):
            params = {p.get("key"): p.get("value") for p in f.get("parameter", [])}
            cef_summary = f"  match: {params}"
            break
        flt_summary = ""
        for f in t.get("filter", []):
            params = {p.get("key"): p.get("value") for p in f.get("parameter", [])}
            flt_summary = f"  filter: {params}"
            break
        print(f"  {t['triggerId']:>4}  type={t.get('type'):<14}  name={t.get('name')!r}{cef_summary}{flt_summary}")


if __name__ == "__main__":
    main()
