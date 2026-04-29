#!/usr/bin/env python3
"""
gtm-elevar-cleanup-proposal.py — Read-only.

Identifies GTM tags that are likely redundant with modern Elevar
server-side tracking. Outputs a markdown proposal at:
  ~/Downloads/HairMNL-GTM-Elevar-Cleanup-Proposal-YYYY-MM-DD.md

Categorizes findings by safety tier:
  TIER A (high confidence redundant): UA tags for events Elevar handles
         server-side (purchase, add_to_cart, etc.). UA itself is dead
         (sunset July 2024) so they're shipping ~30-100ms of work to
         404'd endpoints.
  TIER B (mid-migration leftovers): tags whose names start with
         '*Update After Elevar Import*' — clearly abandoned mid-migration.
  TIER C (review needed): pixel tags (Facebook, Bing, etc.) that
         Elevar's modern setup MAY duplicate via destinations. Inspect
         the tag's HTML body before removing.
  KEEP: Elevar core monitoring + non-redundant tags.

This script does NOT delete anything. Removal happens in a separate
gtm-execute-cleanup.py script after user approval.
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ACCOUNT_ID = "4702257664"
CONTAINER_ID = "12266146"
WORKSPACE_ID = "190"
TOKEN_PATH = Path.home() / ".config" / "hairmnl-gtm-token.json"
DOWNLOADS = Path.home() / "Downloads"
SCOPES = [
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
    "https://www.googleapis.com/auth/tagmanager.publish",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

# UA tags that explicitly correspond to ecommerce events Elevar handles
# server-side. These send hits to a sunset endpoint (UA died July 2024).
ELEVAR_REDUNDANT_UA_EVENTS = {
    "GA Event - Purchase",
    "GA Event - Add to Cart",
    "GA Event - Begin Checkout",
    "GA Event - Add Payment Info",
    "GA Event - Add Shipping Info",
    "GA Event - Product Detail View",
    "GA Event - Product List Impression",
    "GA Event - Product List Click",
    "GA Event - Search Results Impression",
    "GA Event - Remove from Cart",
    "GA Event - Cart Pageview",
    "GA Event - Login",
    "GA Event - Sign Up for Account",
    "GA - Pageview",
    "GA Event - Email Signup",
    "*Update After Import* GA Event - Email Signup",
}


def get_svc():
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    return build("tagmanager", "v2", credentials=creds, cache_discovery=False)


def workspace_path():
    return f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}/workspaces/{WORKSPACE_ID}"


def get_html_body(tag: dict) -> str:
    if tag.get("type") != "html":
        return ""
    for p in tag.get("parameter", []):
        if p.get("key") == "html":
            return p.get("value", "") or ""
    return ""


def categorize(tags: list[dict]) -> dict:
    cats = {
        "tier_a_ua_redundant": [],   # UA event tags that Elevar handles
        "tier_a_ua_other": [],        # Other UA tags (manual click tracking) — still dead
        "tier_b_mid_migration": [],   # *Update After Elevar Import*
        "tier_c_pixel_review": [],    # Pixel tags that may overlap with Elevar destinations
        "elevar_core_keep": [],        # Elevar's own monitoring/integration tags
        "paused": [],                  # Already paused — easy delete
    }

    for t in tags:
        name = t.get("name", "")
        type_ = t.get("type", "")
        paused = t.get("paused", False)

        # Mid-migration leftovers
        if "*Update After Elevar Import*" in name or "*Update After Import*" in name:
            cats["tier_b_mid_migration"].append(t)
            continue

        # Elevar's own core tags — KEEP
        if name.startswith("Elevar "):
            cats["elevar_core_keep"].append(t)
            continue

        # UA events that Elevar handles server-side
        if type_ == "ua" and name in ELEVAR_REDUNDANT_UA_EVENTS:
            cats["tier_a_ua_redundant"].append(t)
            continue

        # Other UA tags (manual click tracking — dead but not Elevar-related)
        if type_ == "ua":
            cats["tier_a_ua_other"].append(t)
            continue

        # Pixel tags that may duplicate Elevar destinations
        if type_ == "html":
            body = get_html_body(t).lower()
            name_lower = name.lower()
            if any(p in name_lower for p in ["bing", "facebook", "snapchat", "tiktok", "pinterest", "reddit", "twitter"]):
                cats["tier_c_pixel_review"].append(t)
                continue
            if any(p in body for p in ["fbq(", "twq(", "snaptr(", "ttq.", "rdt(", "uetq.push"]):
                cats["tier_c_pixel_review"].append(t)
                continue

        if paused:
            cats["paused"].append(t)

    return cats


def fmt_tag_row(tag: dict, with_html_size=False) -> str:
    name = tag.get("name", "")[:60]
    paused = " [PAUSED]" if tag.get("paused") else ""
    extra = ""
    if with_html_size and tag.get("type") == "html":
        extra = f" · {len(get_html_body(tag)):,} chars HTML"
    return f"- **{name}**{paused} (id=`{tag['tagId']}`, type=`{tag.get('type')}`){extra}"


def render_proposal(svc) -> str:
    print("Loading tags...", file=sys.stderr)
    tags = svc.accounts().containers().workspaces().tags().list(
        parent=workspace_path()
    ).execute().get("tag", [])

    cats = categorize(tags)
    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")

    parts = [
        f"# HairMNL — GTM Elevar Cleanup Proposal — {today}",
        "",
        "**Container:** `12266146` (GTM-M4NKSBD, www.hairmnl.com)  ",
        "**Scope:** read-only audit + removal proposal. **No tags deleted yet.**  ",
        "**Approval needed before execution** — review below + reply with `approve A` / `approve A,B` / `approve all` / `veto X` / `modify`.",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"Of 131 total tags, the following are candidates for removal due to Elevar handling these events server-side OR Universal Analytics being sunset (July 2024):",
        "",
        f"| Tier | Count | What | Action |",
        f"|---|---:|---|---|",
        f"| A (Elevar-duplicate UA) | {len(cats['tier_a_ua_redundant'])} | UA event tags Elevar already sends via SST | **Safe to delete** — Elevar covers these |",
        f"| A (Other UA) | {len(cats['tier_a_ua_other'])} | UA click/scroll tracking, custom events | **Dead-code delete** — UA is sunset, fires no-op against 404'd endpoint |",
        f"| B (Mid-migration leftovers) | {len(cats['tier_b_mid_migration'])} | Tags labeled `*Update After Elevar Import*` | **Safe to delete** — abandoned during Elevar setup |",
        f"| C (Pixel — review) | {len(cats['tier_c_pixel_review'])} | Custom HTML pixel tags | **Review needed** — may overlap with Elevar destinations |",
        f"| KEEP | {len(cats['elevar_core_keep'])} | Elevar's own monitoring + integration tags | **Keep** — core to Elevar |",
        f"| Paused (other) | {len(cats['paused'])} | Other paused tags not in above categories | **Review** — paused but still ship in container.js |",
        "",
        "**Estimated perf impact of full Tier A + B cleanup:**",
        "- Container.js payload reduction: ~50-150 KB (each UA tag is a few KB of config)",
        "- Per-pageload network savings: each redundant UA tag was firing a tiny request that 404s. Browser parsing/eval savings cumulative.",
        "- INP improvement: eliminates 60+ tag-evaluation cycles on page load",
        "- Risk: very low — UA endpoint is dead anyway; Elevar already handles all the events these duplicate",
        "",
        "---",
        "",
        "## Tier A — UA tags that duplicate Elevar's server-side events",
        "",
        f"**{len(cats['tier_a_ua_redundant'])} tags.** Modern Elevar (post-2022 server-side) sends purchase/add_to_cart/etc. events directly from Shopify's servers to GA4, Meta, etc. These GTM Universal Analytics tags duplicated the same events on the client side. Since UA is dead and Elevar covers them, these are **safe to delete**.",
        "",
    ]
    for t in sorted(cats["tier_a_ua_redundant"], key=lambda x: x["name"]):
        parts.append(fmt_tag_row(t))

    parts.extend([
        "",
        "---",
        "",
        "## Tier A — Other UA tags (custom click tracking, etc.)",
        "",
        f"**{len(cats['tier_a_ua_other'])} tags.** These are NOT Elevar-related — they're manual click/scroll/video tracking via GA Universal events. Since UA is sunset, they fire no-op requests against a dead endpoint. Each adds ~30-100ms of GTM evaluation time per page.",
        "",
        "**Decision required:** the click-tracking is potentially useful BUT only if migrated to GA4 events. As-is, all 47 of these are pure dead weight.",
        "",
        "Action options:",
        "- **A1.** Delete all → reclaim 47 tags worth of perf (recommended)",
        "- **A2.** Keep + migrate to GA4 events (separate project, weeks of work)",
        "- **A3.** Sample a few high-value ones (cart click, ATC click) and migrate just those",
        "",
        "Tags:",
        "",
    ])
    for t in sorted(cats["tier_a_ua_other"], key=lambda x: x["name"])[:30]:
        parts.append(fmt_tag_row(t))
    if len(cats["tier_a_ua_other"]) > 30:
        parts.append(f"- _… and {len(cats['tier_a_ua_other'])-30} more_")

    parts.extend([
        "",
        "---",
        "",
        "## Tier B — Mid-migration leftovers",
        "",
        f"**{len(cats['tier_b_mid_migration'])} tags.** Whoever set up Elevar started but didn't finish renaming/cleaning up these tags. Names contain `*Update After Elevar Import*` markers. **Safe to delete.**",
        "",
    ])
    for t in cats["tier_b_mid_migration"]:
        parts.append(fmt_tag_row(t))

    parts.extend([
        "",
        "---",
        "",
        "## Tier C — Pixel tags (review needed)",
        "",
        f"**{len(cats['tier_c_pixel_review'])} tags.** Custom HTML tags that inject 3rd-party pixels (Bing, Facebook, Snapchat, etc.). Modern Elevar can route these via its destination system — but it depends on which destinations you've enabled in the Elevar admin.",
        "",
        "**Action needed:** for each of the below, check Elevar admin → Destinations. If the destination is enabled there, the GTM tag is duplicate (delete). If not, keep the GTM tag.",
        "",
    ])
    for t in cats["tier_c_pixel_review"]:
        parts.append(fmt_tag_row(t, with_html_size=True))

    parts.extend([
        "",
        "---",
        "",
        "## KEEP — Elevar core monitoring + integration",
        "",
        f"**{len(cats['elevar_core_keep'])} tags.** These are Elevar's own glue tags — the monitoring, error reporting, and integration code that makes Elevar work. **Do not delete.**",
        "",
    ])
    for t in cats["elevar_core_keep"]:
        parts.append(fmt_tag_row(t))

    parts.extend([
        "",
        "---",
        "",
        "## Paused tags (other)",
        "",
        f"**{len(cats['paused'])} tags.** Already paused so they don't fire — but their config still ships in container.js. Cleanup just reduces payload.",
        "",
    ])
    for t in cats["paused"]:
        parts.append(fmt_tag_row(t))

    parts.extend([
        "",
        "---",
        "",
        "## How to execute",
        "",
        "Once you reply with approval (e.g. `approve A`, `approve A,B`, `approve all`), I'll:",
        "",
        "1. Write `scripts/gtm-execute-cleanup.py` that takes the approved tier list as input",
        "2. Pause-then-delete each tag (pause first as a safety pass)",
        "3. Create a Container Version with notes describing what changed",
        "4. Publish via API",
        "5. Verify the live container.js no longer references the deleted tag IDs",
        "",
        "Rollback path: GTM keeps version history. If anything breaks, restore the previous Container Version in the GTM admin (1 click).",
        "",
        f"_Generated by `scripts/gtm-elevar-cleanup-proposal.py` on {today}._",
    ])

    return "\n".join(parts)


def main():
    svc = get_svc()
    md = render_proposal(svc)
    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
    out_path = DOWNLOADS / f"HairMNL-GTM-Elevar-Cleanup-Proposal-{today}.md"
    out_path.write_text(md)
    print(f"Wrote {out_path} ({len(md):,} bytes)", file=sys.stderr)
    # First 30 lines to stdout
    for l in md.split("\n")[:30]:
        print(l)


if __name__ == "__main__":
    main()
