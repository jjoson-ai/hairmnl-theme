#!/usr/bin/env python3
"""
grant-ga4-access.py — one-shot script to grant a service account Viewer
access on a GA4 property, bypassing the buggy GA4 admin UI that rejects
service account emails as "not a Google Account".

Workaround for the GA4 access-management UI bug we hit on 2026-04-28
(seo-agent-489812 service account → HairMNL GA4 property 248106289).
The UI rejected the email even though it's a valid service account; the
Admin API accepts it fine.

Setup:
  1. gcloud auth application-default login \
       --scopes='openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/analytics.edit'
     (signs in as YOU — the human admin; needs analytics.edit scope so
     gcloud's default token isn't enough)
  2. Run this script with the property ID + service account email as args.

Usage:
  ./scripts/grant-ga4-access.py 248106289 hairmnl-rum-reader@seo-agent-489812.iam.gserviceaccount.com
"""

import sys
import json

try:
    from google.auth import default as google_auth_default
    from google.auth.transport.requests import Request
except ImportError:
    print("ERROR: pip install --user google-auth google-auth-oauthlib", file=sys.stderr)
    sys.exit(1)

import urllib.request
import urllib.error


def main():
    if len(sys.argv) != 3:
        print("Usage: grant-ga4-access.py <property_id> <service_account_email>", file=sys.stderr)
        sys.exit(1)
    property_id = sys.argv[1]
    service_account_email = sys.argv[2]

    # Get user's ADC credentials with analytics.edit scope
    try:
        credentials, project = google_auth_default(scopes=[
            'https://www.googleapis.com/auth/analytics.edit'
        ])
    except Exception as e:
        print(f"ERROR: failed to load ADC credentials: {e}", file=sys.stderr)
        print("Run: gcloud auth application-default login --scopes='openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/analytics.edit'", file=sys.stderr)
        sys.exit(1)

    # Refresh to get a token
    credentials.refresh(Request())
    token = credentials.token

    # Call the Admin API to create accessBinding
    url = f"https://analyticsadmin.googleapis.com/v1alpha/properties/{property_id}/accessBindings"
    body = json.dumps({
        "user": service_account_email,
        "roles": ["predefinedRoles/viewer"],
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body_resp = resp.read().decode("utf-8")
            print(f"SUCCESS ({resp.status}):")
            print(body_resp)
    except urllib.error.HTTPError as e:
        print(f"ERROR {e.code} {e.reason}:", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
