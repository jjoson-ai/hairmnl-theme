#!/usr/bin/env python3
"""
gtm-diff-versions-vux.py — diff GTM container versions to find what broke
the web-vitals → GA4 instrumentation between V140 and V141.

Background: bd issue hairmnl-theme-vux. Dashboard LCP-good fell from 84%
to 66% between May 7 and May 8, coincident with publishing Container
Version 141 (the l3g JS-error tag fix). Volume on load-time CWV metrics
(LCP/CLS/FCP/TTFB) halved; INP volume stayed flat. 95.7% of LCP events
now show template="(not set)". Hypothesis: V141 publish inadvertently
broke the eventSettingsTable param mapping on web-vitals tag(s).

This script is READ-ONLY. It:
  1. Lists all container versions; identifies V140 + V141.
  2. Fetches both versions' tags/triggers/variables.
  3. Diffs them.
  4. Reports any tag whose name contains "web vitals", "LCP", "CLS",
     "INP", "FCP", "TTFB", "metric", or whose firing trigger references
     a Custom Event with one of those metric names.
  5. For each candidate tag, prints firingTriggerId + parameter blob
     side-by-side V140 / V141 so the regression is obvious.
"""
import json
import sys
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
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

CWV_KEYWORDS = (
    "web vitals", "web-vitals", "webvitals",
    "core web", "cwv",
    "metric_rating", "metric-rating",
    "lcp", "cls", "inp", "fcp", "ttfb",
)


def get_svc():
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    return build("tagmanager", "v2", credentials=creds, cache_discovery=False)


def container_path():
    return f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}"


def list_versions(svc):
    """List all container versions (paginated)."""
    versions = []
    next_page = None
    while True:
        kw = {"parent": container_path()}
        if next_page:
            kw["pageToken"] = next_page
        resp = svc.accounts().containers().version_headers().list(**kw).execute()
        versions.extend(resp.get("containerVersionHeader", []))
        next_page = resp.get("nextPageToken")
        if not next_page:
            break
    return versions


def fetch_version(svc, version_id: str) -> dict:
    """Fetch a complete container version (tags, triggers, variables)."""
    path = f"{container_path()}/versions/{version_id}"
    return svc.accounts().containers().versions().get(path=path).execute()


def looks_cwv_relevant(tag: dict, triggers_by_id: dict) -> tuple[bool, str]:
    """Return (is_relevant, why) — flag tags that might be the web-vitals reporter."""
    name = tag.get("name", "").lower()
    for kw in CWV_KEYWORDS:
        if kw in name:
            return True, f"name contains '{kw}'"
    # Check firing triggers — Custom Event triggers with cwv metric name as event
    for tid in tag.get("firingTriggerId", []):
        trig = triggers_by_id.get(tid)
        if not trig:
            continue
        tname = trig.get("name", "").lower()
        for kw in CWV_KEYWORDS:
            if kw in tname:
                return True, f"trigger '{trig.get('name')}' contains '{kw}'"
        # Inspect the trigger's customEventFilter parameter for metric names
        ttype = trig.get("type", "")
        if ttype == "customEvent":
            for p in trig.get("customEventFilter", []):
                if not isinstance(p, dict):
                    continue
                for nested in p.get("parameter", []):
                    val = (nested.get("value") or "").lower()
                    for kw in ("lcp", "cls", "inp", "fcp", "ttfb"):
                        if kw in val:
                            return True, f"trigger fires on customEvent matching '{kw}'"
    # Check parameter blob for metric_rating
    blob = json.dumps(tag.get("parameter", []))
    if "metric_rating" in blob.lower() or "metric_id" in blob.lower():
        return True, "parameters reference metric_rating / metric_id"
    return False, ""


def summarize_tag(tag: dict, triggers_by_id: dict) -> dict:
    """Compact representation of a tag for diffing."""
    return {
        "tagId": tag.get("tagId"),
        "name": tag.get("name"),
        "type": tag.get("type"),
        "paused": tag.get("paused", False),
        "firingTriggerId": sorted(tag.get("firingTriggerId", [])),
        "firingTriggerNames": [
            triggers_by_id.get(tid, {}).get("name", f"id={tid}")
            for tid in tag.get("firingTriggerId", [])
        ],
        "blockingTriggerId": sorted(tag.get("blockingTriggerId", [])),
        "parameter": tag.get("parameter", []),
        "fingerprint": tag.get("fingerprint"),  # GTM updates fingerprint on every edit
    }


def diff_tags(v140: dict, v141: dict):
    triggers_140 = {t["triggerId"]: t for t in v140.get("trigger", [])}
    triggers_141 = {t["triggerId"]: t for t in v141.get("trigger", [])}
    tags_140 = {t["tagId"]: t for t in v140.get("tag", [])}
    tags_141 = {t["tagId"]: t for t in v141.get("tag", [])}

    print(f"\n=== Tag count: V140={len(tags_140)}  V141={len(tags_141)}")

    only_140 = set(tags_140) - set(tags_141)
    only_141 = set(tags_141) - set(tags_140)
    common = set(tags_140) & set(tags_141)

    if only_140:
        print(f"\n--- Tags REMOVED in V141 ({len(only_140)}):")
        for tid in only_140:
            print(f"   {tid}: {tags_140[tid].get('name')}")
    if only_141:
        print(f"\n--- Tags ADDED in V141 ({len(only_141)}):")
        for tid in only_141:
            print(f"   {tid}: {tags_141[tid].get('name')}")

    # Diff fingerprints — fingerprint changes mean the tag was edited
    changed = []
    for tid in common:
        a = tags_140[tid]
        b = tags_141[tid]
        if a.get("fingerprint") != b.get("fingerprint"):
            changed.append(tid)

    print(f"\n--- Tags MODIFIED in V141 ({len(changed)}):")
    for tid in changed:
        a = tags_140[tid]
        b = tags_141[tid]
        print(f"\n  Tag {tid}: {a.get('name')!r}")
        print(f"    fingerprint V140 → V141: {a.get('fingerprint')} → {b.get('fingerprint')}")
        # Compare key fields
        for field in ("type", "paused", "firingTriggerId", "blockingTriggerId"):
            va = a.get(field)
            vb = b.get(field)
            if va != vb:
                # Resolve trigger IDs to names
                if field in ("firingTriggerId", "blockingTriggerId"):
                    na = [triggers_140.get(t, {}).get("name", f"id={t}") for t in (va or [])]
                    nb = [triggers_141.get(t, {}).get("name", f"id={t}") for t in (vb or [])]
                    print(f"    {field}: {va} → {vb}")
                    print(f"      names: {na} → {nb}")
                else:
                    print(f"    {field}: {va!r} → {vb!r}")
        # Diff parameter list (structurally, JSON comparison)
        pa = a.get("parameter", [])
        pb = b.get("parameter", [])
        if json.dumps(pa, sort_keys=True) != json.dumps(pb, sort_keys=True):
            print(f"    parameter changed:")
            print(f"      V140: {json.dumps(pa, indent=2)[:1500]}")
            print(f"      V141: {json.dumps(pb, indent=2)[:1500]}")

    # CWV-relevance scan in V141 specifically
    print(f"\n=== CWV-relevant tags in V141 ===")
    for tid, tag in tags_141.items():
        is_rel, why = looks_cwv_relevant(tag, triggers_141)
        if is_rel:
            tnames = [triggers_141.get(t, {}).get("name", f"id={t}") for t in tag.get("firingTriggerId", [])]
            print(f"\n  {tid}: {tag.get('name')!r}  (relevance: {why})")
            print(f"    type: {tag.get('type')}")
            print(f"    paused: {tag.get('paused', False)}")
            print(f"    firingTriggers: {tnames}")
            # Print param keys + a short value preview
            for p in tag.get("parameter", []):
                k = p.get("key")
                v = p.get("value", "")
                t = p.get("type", "")
                if t == "list":
                    print(f"    param[{k}] (list, type={t}):")
                    for item in (p.get("list") or [])[:10]:
                        item_summary = {pp.get("key"): pp.get("value", "") for pp in item.get("map", [])}
                        print(f"        {item_summary}")
                else:
                    val_preview = (v or "")[:120]
                    print(f"    param[{k}] = {val_preview!r}  (type={t})")


def main():
    svc = get_svc()
    print("Fetching version headers...", file=sys.stderr)
    versions = list_versions(svc)
    # Sort by versionId (string but numeric-ish)
    by_id = {v["containerVersionId"]: v for v in versions}
    print(f"Found {len(versions)} versions. Latest 6:", file=sys.stderr)
    for v in sorted(versions, key=lambda x: int(x["containerVersionId"]))[-6:]:
        print(f"  V{v['containerVersionId']:>3}  name={v.get('name','')!r:<40}  deleted={v.get('deleted',False)}  numTags={v.get('numTags','?')}  numTriggers={v.get('numTriggers','?')}  numVariables={v.get('numVariables','?')}", file=sys.stderr)

    if "140" not in by_id or "141" not in by_id:
        print(f"\nERROR: V140 or V141 missing from versions list. Available: {sorted(by_id.keys(), key=lambda x: int(x))[-10:]}", file=sys.stderr)
        sys.exit(2)

    print("\nFetching V140...", file=sys.stderr)
    v140 = fetch_version(svc, "140")
    print("Fetching V141...", file=sys.stderr)
    v141 = fetch_version(svc, "141")

    diff_tags(v140, v141)


if __name__ == "__main__":
    main()
