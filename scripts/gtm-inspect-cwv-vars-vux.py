#!/usr/bin/env python3
"""
gtm-inspect-cwv-vars-vux.py — read-only follow-up to gtm-diff-versions-vux.

Goals:
  1. Show variable definitions for all metric_* / template / debug_target
     Data Layer Variables. Confirms naming convention (bare vs DLV - prefix)
     so the fix script uses the right name.
  2. Show the trigger config for "Web Vitals (LCP/CLS/INP/FCP/TTFB)" — confirms
     it really matches all 5 metric names (the volume asymmetry between
     INP and LCP/CLS/FCP/TTFB might be a trigger filter quirk).
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
    print(f"Workspace: {WORKSPACE_ID}\n")
    variables = list_all(svc, "variables")
    triggers = list_all(svc, "triggers")
    tags = list_all(svc, "tags")

    print(f"Total: {len(variables)} variables, {len(triggers)} triggers, {len(tags)} tags\n")

    # CWV variables
    interesting = ("metric_", "template", "debug_target", "page_path", "web_vital", "event")
    print("=== CWV-related variables ===\n")
    for v in variables:
        name = v.get("name", "")
        nl = name.lower()
        if any(k in nl for k in interesting):
            print(f"  variableId={v['variableId']:>4}  name={name!r}  type={v.get('type')}")
            for p in v.get("parameter", []):
                print(f"    {p.get('key')}={p.get('value')!r}  type={p.get('type')}")
            print()

    # Trigger 766 lookup — by name "Web Vitals"
    print("\n=== CWV-related triggers ===\n")
    for t in triggers:
        n = t.get("name", "").lower()
        if "web vital" in n or "lcp" in n or "cls" in n or "inp" in n or "fcp" in n or "ttfb" in n:
            print(f"  triggerId={t['triggerId']}  name={t.get('name')!r}  type={t.get('type')}")
            for f in t.get("customEventFilter", []):
                print(f"    customEventFilter: {json.dumps(f, indent=2)}")
            for f in t.get("filter", []):
                print(f"    filter: {json.dumps(f, indent=2)}")
            print()

    # Tag 766 — full param dump
    print("\n=== Tag 766 (GA4 – Web Vitals) full parameter dump ===\n")
    for tag in tags:
        if tag.get("tagId") == "766":
            print(json.dumps(tag, indent=2))
            break


if __name__ == "__main__":
    main()
