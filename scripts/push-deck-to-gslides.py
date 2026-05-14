#!/usr/bin/env python3
"""push-deck-to-gslides.py — Upload docs/HairMNL-Theme-Modernization-Deck.pptx to
Google Slides via the Drive API. Auto-converts .pptx → Slides format on upload.

First run:
  - Opens browser for OAuth consent (Drive scope).
  - Uploads the .pptx as a new Google Slides file in your Drive root.
  - Saves the resulting file ID to docs/.gslides-deck.json for future runs.

Subsequent runs:
  - Reuses the cached OAuth token (~/.config/hairmnl-drive-token.json).
  - Reads docs/.gslides-deck.json to find the existing file ID.
  - Replaces the existing Slides file's content with the latest .pptx.
  - File ID stays the same → share link, collaborators, comments all preserved.

If docs/.gslides-deck.json is deleted (or the referenced file ID was deleted in
Drive), the script falls back to creating a new file.

Usage:
  python3 scripts/push-deck-to-gslides.py
  python3 scripts/push-deck-to-gslides.py --rename "New Name"  # also rename the file
"""

import argparse
import json
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


REPO = Path(__file__).resolve().parent.parent
DECK_PPTX = REPO / "docs" / "HairMNL-Theme-Modernization-Deck.pptx"
DECK_REF = REPO / "docs" / ".gslides-deck.json"

CLIENT_PATH = Path.home() / ".config" / "hairmnl-oauth-client.json"
TOKEN_PATH = Path.home() / ".config" / "hairmnl-drive-token.json"

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

PPTX_MIME = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
SLIDES_MIME = "application/vnd.google-apps.presentation"

DEFAULT_NAME = "HairMNL Theme Modernization Deck"


def get_creds():
    """Get user OAuth credentials, prompting browser consent if needed."""
    creds = None
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        except Exception as e:
            print(f"  warn: could not load cached token ({e}) — will reauthorize", file=sys.stderr)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
            return creds
        except Exception as e:
            print(f"  warn: token refresh failed ({e}) — will reauthorize", file=sys.stderr)
    if not CLIENT_PATH.exists():
        print(f"ERROR: OAuth client file missing at {CLIENT_PATH}", file=sys.stderr)
        print("  Create a Desktop OAuth client in Google Cloud Console + save the JSON here.", file=sys.stderr)
        sys.exit(1)
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_PATH), SCOPES)
    print("  Opening browser for OAuth consent (Drive scope)…", flush=True)
    creds = flow.run_local_server(port=0)
    TOKEN_PATH.write_text(creds.to_json())
    print(f"  Saved token to {TOKEN_PATH}", flush=True)
    return creds


def load_existing_ref():
    if not DECK_REF.exists():
        return None
    try:
        return json.loads(DECK_REF.read_text())
    except Exception:
        return None


def save_ref(ref: dict):
    DECK_REF.write_text(json.dumps(ref, indent=2) + "\n")


def file_exists(service, file_id: str) -> bool:
    try:
        service.files().get(fileId=file_id, fields="id, trashed").execute()
        return True
    except HttpError as e:
        if e.resp.status in (403, 404):
            return False
        raise


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rename", help="Rename the Slides file (also sets the name on a new file)")
    parser.add_argument("--name", default=DEFAULT_NAME, help=f"Name for new files (default: {DEFAULT_NAME!r})")
    parser.add_argument("--force-new", action="store_true", help="Ignore existing ref + create a new file")
    args = parser.parse_args(argv[1:])

    if not DECK_PPTX.exists():
        print(f"ERROR: deck not found at {DECK_PPTX}", file=sys.stderr)
        return 1

    print(f"Source: {DECK_PPTX.relative_to(REPO)} ({DECK_PPTX.stat().st_size:,} bytes)")

    creds = get_creds()
    service = build("drive", "v3", credentials=creds, cache_discovery=False)

    # Decide create vs update
    existing_ref = None if args.force_new else load_existing_ref()
    existing_id = existing_ref.get("file_id") if existing_ref else None
    will_update = existing_id is not None and file_exists(service, existing_id)

    media = MediaFileUpload(str(DECK_PPTX), mimetype=PPTX_MIME, resumable=True)

    if will_update:
        body = {}
        if args.rename:
            body["name"] = args.rename
        action = "Updated"
        try:
            file = service.files().update(
                fileId=existing_id,
                body=body or None,
                media_body=media,
                fields="id, webViewLink, name, modifiedTime",
            ).execute()
        except HttpError as e:
            print(f"  warn: update failed ({e}) — falling back to create new file", file=sys.stderr)
            will_update = False

    if not will_update:
        name = args.rename or args.name
        meta = {"name": name, "mimeType": SLIDES_MIME}
        file = service.files().create(
            body=meta,
            media_body=media,
            fields="id, webViewLink, name, modifiedTime",
        ).execute()
        action = "Created (new)" if not existing_id else "Recreated (previous file missing)"

    ref = {
        "file_id": file["id"],
        "url": file.get("webViewLink"),
        "name": file.get("name"),
        "last_updated": file.get("modifiedTime"),
    }
    save_ref(ref)

    print()
    print(f"{action} Google Slides:")
    print(f"  Name:    {ref['name']}")
    print(f"  URL:     {ref['url']}")
    print(f"  File ID: {ref['file_id']}")
    print(f"  Modified: {ref['last_updated']}")
    print(f"  Ref saved → {DECK_REF.relative_to(REPO)} (commit to repo so future runs find it)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
