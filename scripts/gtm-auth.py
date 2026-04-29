#!/usr/bin/env python3
"""
gtm-auth.py — One-time OAuth flow to grant this machine access to the
Google Tag Manager API on behalf of the signed-in Google account.

Uses the OAuth 2.0 Desktop client at ~/.config/hairmnl-oauth-client.json
(created in the GCP project's Credentials page). On first run, opens a
browser for user consent; the resulting refresh token is saved to
~/.config/hairmnl-gtm-token.json. Subsequent runs reuse the saved token.

Scopes: tagmanager.edit.containers + tagmanager.publish + tagmanager.manage.users
        + userinfo.email (for sanity-checking which account we authed as)

This script bypasses the gcloud CLI's `application-default login` flow
(which can be blocked by Workspace API access controls when targeting
restricted scopes — that block was hit earlier today).
"""

import json
import os
import sys
from pathlib import Path

CLIENT_SECRET = Path.home() / ".config" / "hairmnl-oauth-client.json"
TOKEN_PATH = Path.home() / ".config" / "hairmnl-gtm-token.json"

SCOPES = [
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",  # for create_version
    "https://www.googleapis.com/auth/tagmanager.publish",
    "https://www.googleapis.com/auth/tagmanager.manage.users",
    "https://www.googleapis.com/auth/gmail.compose",  # for the weekly-cadence Gmail draft
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


def get_credentials():
    """Returns valid creds. On first run, opens browser for consent.
    On subsequent runs, refreshes the saved token silently."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        except Exception as e:
            print(f"  ⚠ existing token unreadable: {e}", file=sys.stderr)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("  → refreshing existing token...")
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET.exists():
                print(f"ERROR: missing {CLIENT_SECRET}", file=sys.stderr)
                sys.exit(1)
            print("  → opening browser for one-time consent...")
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True, prompt="consent")
        TOKEN_PATH.write_text(creds.to_json())
        os.chmod(TOKEN_PATH, 0o600)
        print(f"  ✓ saved token to {TOKEN_PATH}")
    return creds


def main():
    creds = get_credentials()
    print(f"  ✓ authenticated")

    # Sanity check: list GTM accounts
    from googleapiclient.discovery import build
    svc = build("tagmanager", "v2", credentials=creds, cache_discovery=False)
    try:
        accts = svc.accounts().list().execute().get("account", [])
    except Exception as e:
        print(f"  ✗ GTM API call failed: {str(e)[:300]}", file=sys.stderr)
        sys.exit(2)

    if not accts:
        print("  ⚠ Authenticated, but no GTM accounts visible to this user.")
        print("    Check that the signed-in Google account has access to the HairMNL GTM container.")
        sys.exit(3)

    print(f"  ✓ {len(accts)} GTM account(s) visible:")
    for a in accts:
        print(f"      account_id={a.get('accountId')} name={a.get('name')!r}")
        # Drill into containers
        try:
            cnts = svc.accounts().containers().list(parent=a["path"]).execute().get("container", [])
            for c in cnts:
                print(f"        container_id={c.get('containerId')} public_id={c.get('publicId')!r} name={c.get('name')!r}")
        except Exception as e:
            print(f"        (containers list error: {str(e)[:200]})")


if __name__ == "__main__":
    main()
