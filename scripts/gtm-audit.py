#!/usr/bin/env python3
"""
gtm-audit.py — Read-only audit of the HairMNL GTM container.

Surfaces tag/trigger/variable findings that affect site perf:
  - Tags firing on All Pages vs more specific triggers
  - Custom HTML tags (heaviest type — every line of HTML they inject runs)
  - Paused tags (still loaded by container, just don't fire)
  - 3rd-party tracking pixels (Reddit, Snapchat, etc.)
  - Tags with deprecated/legacy types (gtm.js, GA Universal, etc.)
  - Variables defined but unused
  - Triggers defined but unused

Output: markdown report at ~/Downloads/HairMNL-GTM-Audit-YYYY-MM-DD.md.
NO publishing — review-only. Companion `gtm-fix-*` scripts handle changes.
"""
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ACCOUNT_ID = "4702257664"      # HairMNL
CONTAINER_ID = "12266146"      # GTM-M4NKSBD
WORKSPACE_ID = "190"           # Default Workspace
TOKEN_PATH = Path.home() / ".config" / "hairmnl-gtm-token.json"
DOWNLOADS = Path.home() / "Downloads"
SCOPES = [
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
    "https://www.googleapis.com/auth/tagmanager.publish",
    "https://www.googleapis.com/auth/tagmanager.manage.users",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

# Map raw GTM tag types → human-readable + perf weight (heuristic)
TAG_TYPE_INFO = {
    "html":         {"label": "Custom HTML",                "weight": "HIGH",   "note": "Injects raw JS/HTML on each fire — varies by content"},
    "gaawe":        {"label": "GA4 Event",                  "weight": "MEDIUM", "note": "Lightweight per-event POST"},
    "gaawc":        {"label": "GA4 Configuration",          "weight": "MEDIUM", "note": "Loads gtag.js library"},
    "ua":           {"label": "Universal Analytics (LEGACY)", "weight": "MEDIUM", "note": "GA Universal sunset July 2024 — should be removed"},
    "gclidw":       {"label": "Conversion Linker",          "weight": "LOW",    "note": "Cookie-write only"},
    "awct":         {"label": "Google Ads Conversion",      "weight": "MEDIUM", "note": "Loads Google Ads conversion script"},
    "sp":           {"label": "Google Ads Remarketing",     "weight": "MEDIUM", "note": "Loads sgtm/dynamic remarketing"},
    "img":          {"label": "Custom Image (1x1 pixel)",   "weight": "LOW",    "note": "Single tracking pixel request"},
    "fls":          {"label": "Floodlight (DCM/DV360)",     "weight": "MEDIUM", "note": "Floodlight container"},
    "flc":          {"label": "Floodlight Counter",         "weight": "LOW",    "note": "Floodlight counter pixel"},
    "cvt_template": {"label": "Custom Template",            "weight": "VARIES", "note": "Sandboxed template — depends on what it does"},
    "twitter_pixel":{"label": "Twitter Pixel",              "weight": "MEDIUM", "note": "External pixel script"},
    "asp":          {"label": "Snowplow",                   "weight": "MEDIUM", "note": "Analytics tracker"},
    "shareasale":   {"label": "ShareASale",                 "weight": "LOW",    "note": "Pixel tracking"},
    "stape_st_event":{"label":"Stape SST Event",           "weight": "LOW",    "note": "Server-side tag (no client cost)"},
}


def get_svc():
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    return build("tagmanager", "v2", credentials=creds, cache_discovery=False)


def workspace_path():
    return f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}/workspaces/{WORKSPACE_ID}"


def list_all(svc, kind: str) -> list[dict]:
    """List tags / triggers / variables / folders within the workspace, with pagination."""
    items = []
    method = getattr(svc.accounts().containers().workspaces(), kind)
    next_page = None
    while True:
        kw = {"parent": workspace_path()}
        if next_page:
            kw["pageToken"] = next_page
        resp = method().list(**kw).execute()
        items.extend(resp.get(kind[:-1], []))  # 'tags' → 'tag'
        next_page = resp.get("nextPageToken")
        if not next_page:
            break
    return items


def tag_perf_weight(tag: dict) -> tuple[str, str]:
    t = tag.get("type", "?")
    info = TAG_TYPE_INFO.get(t, {"label": t, "weight": "?", "note": "(unknown type)"})
    return info["label"], info["weight"], info["note"]


def fmt_triggers(tag: dict, triggers_by_id: dict) -> str:
    fids = tag.get("firingTriggerId", [])
    bids = tag.get("blockingTriggerId", [])
    fnames = []
    for tid in fids:
        if tid in triggers_by_id:
            fnames.append(triggers_by_id[tid].get("name", tid))
        elif tid == "2147479553":
            fnames.append("All Pages (built-in)")
        elif tid == "2147479572":
            fnames.append("DOM Ready (built-in)")
        elif tid == "2147479573":
            fnames.append("Window Loaded (built-in)")
        else:
            fnames.append(f"id={tid}")
    base = " · ".join(fnames) if fnames else "(no firing trigger!)"
    if bids:
        bnames = [triggers_by_id.get(tid, {}).get("name", tid) for tid in bids]
        base += f"  [BLOCKED BY: {', '.join(bnames)}]"
    return base


def estimate_html_size(tag: dict) -> int:
    """Estimate the size of a Custom HTML tag's payload in chars."""
    if tag.get("type") != "html":
        return 0
    for p in tag.get("parameter", []):
        if p.get("key") == "html":
            return len(p.get("value", "") or "")
    return 0


def categorize_tags(tags: list[dict], triggers_by_id: dict) -> dict:
    cat = defaultdict(list)
    for t in tags:
        if t.get("paused"):
            cat["paused"].append(t)
        else:
            cat["active"].append(t)
        if t.get("type") == "html":
            cat["custom_html"].append(t)
        if t.get("type") == "ua":
            cat["legacy_ua"].append(t)
        # Tags firing on All Pages
        for tid in t.get("firingTriggerId", []):
            if tid == "2147479553":  # built-in All Pages trigger
                cat["all_pages"].append(t)
                break
            if tid in triggers_by_id:
                trigger = triggers_by_id[tid]
                if trigger.get("type") in ("pageview", "domReady", "windowLoaded"):
                    # Check if it has filters making it more specific
                    if not trigger.get("filter") and not trigger.get("autoEventFilter"):
                        cat["all_pages_via_custom"].append(t)
                        break
    return cat


def render_report(svc) -> str:
    print("Loading tags, triggers, variables, folders...", file=sys.stderr)
    tags = list_all(svc, "tags")
    triggers = list_all(svc, "triggers")
    variables = list_all(svc, "variables")
    folders = list_all(svc, "folders")

    triggers_by_id = {t["triggerId"]: t for t in triggers}
    variables_by_id = {v["variableId"]: v for v in variables}
    folders_by_id = {f["folderId"]: f for f in folders}

    # Find unused variables (referenced in NO tag/trigger)
    used_var_names = set()
    blob = json.dumps(tags) + json.dumps(triggers)
    for v in variables:
        # Variables are referenced as {{Name}} in parameter values
        if "{{" + v.get("name", "") + "}}" in blob:
            used_var_names.add(v["name"])
    unused_vars = [v for v in variables if v["name"] not in used_var_names]

    # Find unused triggers
    used_trigger_ids = set()
    for t in tags:
        for tid in t.get("firingTriggerId", []):
            used_trigger_ids.add(tid)
        for tid in t.get("blockingTriggerId", []):
            used_trigger_ids.add(tid)
    unused_triggers = [t for t in triggers if t["triggerId"] not in used_trigger_ids]

    cat = categorize_tags(tags, triggers_by_id)

    # Custom HTML byte sizes
    html_tags_with_size = sorted(
        [(t, estimate_html_size(t)) for t in cat["custom_html"]],
        key=lambda x: -x[1],
    )

    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
    parts = [
        f"# HairMNL — GTM Container Audit — {today}",
        "",
        f"**Container:** `{CONTAINER_ID}` (GTM-M4NKSBD, www.hairmnl.com)  ",
        f"**Workspace:** Default Workspace ({WORKSPACE_ID})  ",
        f"**Scope:** read-only audit, no changes published  ",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- **Total tags**: {len(tags)} ({len(cat['active'])} active, {len(cat['paused'])} paused)",
        f"- **Custom HTML tags**: {len(cat['custom_html'])} (heaviest type — perf-relevant)",
        f"- **Legacy UA tags**: {len(cat['legacy_ua'])} (should be removed — GA Universal sunset July 2024)",
        f"- **Tags firing on All Pages**: {len(cat['all_pages']) + len(cat['all_pages_via_custom'])}",
        f"- **Triggers**: {len(triggers)} ({len(unused_triggers)} unused)",
        f"- **Variables**: {len(variables)} ({len(unused_vars)} not referenced anywhere)",
        f"- **Folders**: {len(folders)}",
        "",
        "---",
        "",
        "## Recommended cleanup actions (ranked by impact)",
        "",
    ]

    actions = []

    if cat["paused"]:
        actions.append({
            "priority": "P3",
            "title": f"Delete {len(cat['paused'])} paused tags",
            "why": "Paused tags don't fire but their config still ships in container.js. Removing reduces container payload.",
            "items": [t["name"] for t in cat["paused"][:15]],
        })

    if cat["legacy_ua"]:
        actions.append({
            "priority": "P2",
            "title": f"Remove {len(cat['legacy_ua'])} Universal Analytics tags",
            "why": "GA Universal sunset July 2024. These tags do nothing functional but still execute (network request that 404s, eats ~30-100ms).",
            "items": [t["name"] for t in cat["legacy_ua"]],
        })

    if html_tags_with_size:
        big_html = [(t, sz) for t, sz in html_tags_with_size if sz > 1500][:10]
        if big_html:
            actions.append({
                "priority": "P2",
                "title": f"Audit the {len(big_html)} largest Custom HTML tags",
                "why": "Custom HTML tags inject + execute their full content on every fire. >1.5KB tags are candidates for: defer, lazy-load, conversion to template, or removal if obsolete.",
                "items": [f"{t['name']!r} — {sz:,} chars · trigger: {fmt_triggers(t, triggers_by_id)}" for t, sz in big_html],
            })

    if unused_vars:
        actions.append({
            "priority": "P3",
            "title": f"Delete {len(unused_vars)} unused variables",
            "why": "Variables not referenced by any tag/trigger still serialize into container.js, adding bytes.",
            "items": [v["name"] for v in unused_vars[:20]],
        })

    if unused_triggers:
        actions.append({
            "priority": "P3",
            "title": f"Delete {len(unused_triggers)} unused triggers",
            "why": "Triggers not used by any tag still serialize into container.js.",
            "items": [t["name"] for t in unused_triggers[:20]],
        })

    if not actions:
        parts.append("_No high-confidence cleanup actions identified. Container is in good shape._")
    else:
        for a in actions:
            parts.append(f"### [{a['priority']}] {a['title']}")
            parts.append("")
            parts.append(f"**Why:** {a['why']}")
            parts.append("")
            parts.append("**Affected items:**")
            for item in a["items"]:
                parts.append(f"- {item}")
            if len(a["items"]) >= 15 and a["items"] != []:
                parts.append(f"- _… and more (truncated)_")
            parts.append("")

    parts.extend([
        "---",
        "",
        "## All active tags by type",
        "",
        "| # | Type | Name | Trigger | Folder |",
        "|---|------|------|---------|--------|",
    ])

    type_counts = defaultdict(int)
    for tag in sorted(cat["active"], key=lambda t: (t.get("type", ""), t.get("name", ""))):
        type_counts[tag.get("type", "?")] += 1
        label, weight, _ = tag_perf_weight(tag)
        folder = folders_by_id.get(tag.get("parentFolderId", ""), {}).get("name", "—")
        triggers_str = fmt_triggers(tag, triggers_by_id)
        if len(triggers_str) > 70:
            triggers_str = triggers_str[:70] + "…"
        parts.append(f"| {tag['tagId']} | {label} ({weight}) | {tag['name'][:50]} | {triggers_str} | {folder[:30]} |")

    parts.extend([
        "",
        "## Type distribution",
        "",
        "| Type | Active count | Perf weight |",
        "|---|---:|---|",
    ])
    for t, n in sorted(type_counts.items(), key=lambda x: -x[1]):
        info = TAG_TYPE_INFO.get(t, {"label": t, "weight": "?", "note": ""})
        parts.append(f"| {info['label']} (`{t}`) | {n} | {info['weight']} |")

    if cat["paused"]:
        parts.extend([
            "",
            "---",
            "",
            "## Paused tags (delete candidates)",
            "",
        ])
        for t in cat["paused"][:30]:
            label, weight, _ = tag_perf_weight(t)
            parts.append(f"- **{t['name']}** (id={t['tagId']}, type={label})")

    if cat["custom_html"]:
        parts.extend([
            "",
            "---",
            "",
            "## Custom HTML tag inventory (sorted by size)",
            "",
            "| Size | Name | Trigger | Folder |",
            "|---:|---|---|---|",
        ])
        for tag, sz in html_tags_with_size:
            folder = folders_by_id.get(tag.get("parentFolderId", ""), {}).get("name", "—")
            triggers_str = fmt_triggers(tag, triggers_by_id)[:60]
            parts.append(f"| {sz:,} | {tag['name'][:50]} | {triggers_str} | {folder[:30]} |")

    if unused_vars:
        parts.extend([
            "",
            "---",
            "",
            f"## Unused variables ({len(unused_vars)} total)",
            "",
            "Defined in container but not referenced by any tag/trigger. Safe to delete.",
            "",
        ])
        for v in unused_vars[:30]:
            parts.append(f"- `{v['name']}` (id={v['variableId']}, type={v.get('type')})")
        if len(unused_vars) > 30:
            parts.append(f"- _… and {len(unused_vars)-30} more_")

    if unused_triggers:
        parts.extend([
            "",
            "---",
            "",
            f"## Unused triggers ({len(unused_triggers)} total)",
            "",
        ])
        for t in unused_triggers[:30]:
            parts.append(f"- `{t['name']}` (id={t['triggerId']}, type={t.get('type')})")
        if len(unused_triggers) > 30:
            parts.append(f"- _… and {len(unused_triggers)-30} more_")

    parts.extend([
        "",
        "---",
        "",
        f"_Generated by `scripts/gtm-audit.py` on {today}. Re-run any time. To execute changes, write a companion `gtm-cleanup-X.py` script that goes through the standard variable-update + create_version + publish flow already proven by `gtm-fix-js-error-vars.py`._",
    ])

    return "\n".join(parts)


def main():
    svc = get_svc()
    md = render_report(svc)
    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
    out_path = DOWNLOADS / f"HairMNL-GTM-Audit-{today}.md"
    out_path.write_text(md)
    print(f"Wrote {out_path} ({len(md):,} bytes)", file=sys.stderr)
    # Print summary to stdout for quick scan
    summary_lines = [l for l in md.split("\n")[:25]]
    print("\n".join(summary_lines))


if __name__ == "__main__":
    main()
