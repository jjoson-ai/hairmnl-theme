#!/usr/bin/env python3
"""
gtm-fix-js-error-vars.py — Update the 3 DLV variables in the HairMNL GTM
container that the "GA4 - JS Error Event" tag depends on, so they read
the renamed dataLayer fields:
  js_error_type    → error_type
  js_error_message → error_message
  js_error_source  → error_source

Then create a new container Version and publish it.

Two-phase: (1) DRY-RUN prints intended changes, (2) --apply does them.
"""
import argparse
import json
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ACCOUNT_ID = "4702257664"
CONTAINER_ID = "12266146"
WORKSPACE_ID = "190"
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

# Mapping: variable display-name → new dataLayer field path (without prefix)
RENAMES = {
    "DLV - js_error_type":    "error_type",
    "DLV - js_error_message": "error_message",
    "DLV - js_error_source":  "error_source",
}


def get_svc():
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    return build("tagmanager", "v2", credentials=creds, cache_discovery=False)


def workspace_path():
    return f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}/workspaces/{WORKSPACE_ID}"


def find_target_variables(svc):
    """Returns dict of {display_name: variable_resource}."""
    resp = svc.accounts().containers().workspaces().variables().list(parent=workspace_path()).execute()
    vs = resp.get("variable", [])
    found = {}
    for v in vs:
        if v.get("name") in RENAMES:
            found[v["name"]] = v
    return found


def update_variable(svc, var: dict, new_dl_field: str, dry_run: bool = True):
    """Update a v variable's `name` parameter (the dataLayer field reference)."""
    print(f"\n--- {var['name']!r} (id={var['variableId']}, type={var['type']}) ---")
    # Show current parameter setting
    current_dl_name = None
    for p in var.get("parameter", []):
        if p.get("key") == "name":
            current_dl_name = p.get("value")
    print(f"  current dataLayer field = {current_dl_name!r}")
    print(f"  proposed dataLayer field = {new_dl_field!r}")

    if current_dl_name == new_dl_field:
        print("  ✓ already correct, no change needed")
        return False

    if dry_run:
        print("  ⚪ DRY-RUN — no changes applied")
        return False

    # Build updated variable resource
    updated = json.loads(json.dumps(var))  # deep copy
    for p in updated["parameter"]:
        if p.get("key") == "name":
            p["value"] = new_dl_field
    # Remove read-only / auto-managed fields
    for k in ("path", "fingerprint", "tagManagerUrl"):
        updated.pop(k, None)

    print("  → applying update via API...")
    r = svc.accounts().containers().workspaces().variables().update(
        path=var["path"], body=updated,
    ).execute()
    print(f"  ✓ updated. New fingerprint={r.get('fingerprint')}")
    return True


def create_version_and_publish(svc, name: str, notes: str, dry_run: bool = True):
    if dry_run:
        print("\n⚪ DRY-RUN — skipping version creation + publish")
        return None
    print(f"\nCreating new version: {name}")
    cv = svc.accounts().containers().workspaces().create_version(
        path=workspace_path(),
        body={"name": name, "notes": notes},
    ).execute()
    if cv.get("compilerError"):
        print(f"  ✗ compiler error: {cv['compilerError']}", file=sys.stderr)
        return None
    version = cv.get("containerVersion") or {}
    version_id = version.get("containerVersionId")
    print(f"  ✓ version created: id={version_id} name={version.get('name')!r}")
    print(f"\nPublishing version {version_id} to live...")
    pub = svc.accounts().containers().versions().publish(
        path=f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}/versions/{version_id}",
    ).execute()
    print(f"  ✓ published. fingerprint={pub.get('containerVersion', {}).get('fingerprint')}")
    return version_id


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually apply changes (default: dry-run)")
    ap.add_argument("--no-publish", action="store_true", help="apply variable changes but don't create Version + publish")
    args = ap.parse_args()

    svc = get_svc()
    found = find_target_variables(svc)

    print(f"Found {len(found)}/{len(RENAMES)} target variables:")
    for name in RENAMES:
        if name in found:
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ MISSING: {name}")

    if len(found) < len(RENAMES):
        print("\nERROR: not all expected variables exist. Aborting.", file=sys.stderr)
        sys.exit(2)

    for name, new_field in RENAMES.items():
        update_variable(svc, found[name], new_field, dry_run=not args.apply)

    # Always publish on --apply: even if no vars changed THIS run, prior run
    # may have updated the workspace without successfully publishing (e.g.,
    # auth scope error). The publish path is idempotent — if workspace has
    # no diff vs current live version, GTM rejects with a no-op error which
    # we'll surface clearly.
    if args.apply and not args.no_publish:
        create_version_and_publish(
            svc,
            name="js_error tag dataLayer var rename (theme migrated to error_*)",
            notes=("Updated DLV - js_error_type/message/source variables to read from "
                   "dataLayer fields error_type/error_message/error_source instead of the "
                   "previous js_error_* names. Theme.liquid was migrated 2026-04-29 (commit "
                   "5fb4be7) — the theme now emits the new names; this GTM update reconnects "
                   "the GA4 event tag to those names so error params populate again."),
            dry_run=False,
        )


if __name__ == "__main__":
    main()
