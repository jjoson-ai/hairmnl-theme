#!/usr/bin/env python3
"""
gtm-find-js-error.py — Locate the js_error tag in the HairMNL GTM container
and show its current parameter mapping. Read-only inspection.
"""
import json
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ACCOUNT_ID = "4702257664"        # HairMNL
CONTAINER_ID = "12266146"        # GTM-M4NKSBD (client-side)
TOKEN_PATH = Path.home() / ".config" / "hairmnl-gtm-token.json"
SCOPES = [
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.publish",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


def main():
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    svc = build("tagmanager", "v2", credentials=creds, cache_discovery=False)

    container_path = f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}"

    # Find or create a workspace (we typically use "Default Workspace" or create new)
    ws_list = svc.accounts().containers().workspaces().list(parent=container_path).execute()
    workspaces = ws_list.get("workspace", [])
    print(f"Workspaces in container {CONTAINER_ID}:")
    for w in workspaces:
        print(f"  workspace_id={w['workspaceId']} name={w['name']!r}")

    # Use Default Workspace (always present, named "Default Workspace")
    default_ws = next((w for w in workspaces if w["name"] == "Default Workspace"), workspaces[0])
    ws_path = default_ws["path"]
    print(f"\nUsing workspace: {default_ws['name']} (id={default_ws['workspaceId']})")

    # List tags
    tags_resp = svc.accounts().containers().workspaces().tags().list(parent=ws_path).execute()
    tags = tags_resp.get("tag", [])
    print(f"\n{len(tags)} tags in workspace.")

    # Find js_error related tags
    matches = [t for t in tags if "js_error" in (t.get("name") or "").lower() or "js error" in (t.get("name") or "").lower() or "javascript error" in (t.get("name") or "").lower() or "error" in (t.get("name") or "").lower()]
    print(f"\nTags matching 'error' (any case):")
    for t in matches:
        print(f"  --- {t['name']!r} (id={t['tagId']}, type={t['type']}) ---")
        print(json.dumps(t, indent=2)[:2000])
        print()


if __name__ == "__main__":
    main()
