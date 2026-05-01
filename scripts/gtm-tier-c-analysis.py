#!/usr/bin/env python3
"""
gtm-tier-c-analysis.py — Inspect all Custom HTML tags in workspace 192
and cross-reference against HairMNL's confirmed Elevar destinations.

Active Elevar destinations (confirmed from admin screenshot 2026-04-30):
  - GA4           (Server + Web)
  - Meta/Facebook (Server + Web)
  - TikTok        (Server + Web)
  - Google Ads    (Server, Beta)
  - Klaviyo       (Server)
  - Microsoft Advertising / Bing (Server)
  - Reddit        (Offline, Server + Web)

Output: full tag bodies + signal markers for proposal generation.
"""
import json
import re
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ACCOUNT_ID = "4702257664"
CONTAINER_ID = "12266146"
WORKSPACE_ID = "192"
TOKEN_PATH = Path.home() / ".config" / "hairmnl-gtm-token.json"
SCOPES = [
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
    "https://www.googleapis.com/auth/tagmanager.publish",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

# Signal patterns → Elevar destination label
ELEVAR_SIGNALS = {
    "GA4 / Google Analytics": [
        r"gtag\(",
        r"GA_MEASUREMENT_ID",
        r"G-[A-Z0-9]{6,}",
        r"googletagmanager\.com/gtag",
        r"google-analytics\.com",
        r"gtag/js",
    ],
    "Meta / Facebook Pixel": [
        r"fbq\(",
        r"connect\.facebook\.net",
        r"facebook\.com/tr",
        r"fbevents\.js",
        r"FB\.init",
    ],
    "TikTok Pixel": [
        r"ttq\.",
        r"tiktok\.com",
        r"analytics\.tiktok",
        r"TiktokAnalyticsObject",
    ],
    "Google Ads / Conversion": [
        r"AW-[0-9]{8,}",
        r"google_conversion",
        r"googleadservices\.com",
        r"googlesyndication\.com",
        r"google_conversion_id",
        r"gtag.*AW-",
    ],
    "Klaviyo": [
        r"klaviyo",
        r"a\.klaviyo\.com",
        r"KlaviyoSubscribe",
        r"_learnq",
    ],
    "Microsoft / Bing Ads": [
        r"uetq\b",
        r"bing\.com",
        r"bat\.bing\.com",
        r"UET\b",
        r"microsoft\.com.*ads",
    ],
    "Reddit Pixel": [
        r"rdt\(",
        r"reddit\.com/ads",
        r"redditstatic\.com",
        r"RedditInit",
    ],
    "Criteo": [
        r"criteo",
        r"events\.criteo",
        r"CriteoQ",
    ],
    "Pinterest": [
        r"pintrk\(",
        r"pinterest\.com",
        r"ct\.pinterest\.com",
    ],
    "Snapchat": [
        r"snaptr\(",
        r"sc-static\.net",
    ],
    "Twitter / X": [
        r"twq\(",
        r"static\.ads-twitter\.com",
        r"analytics\.twitter\.com",
    ],
    "Hotjar": [
        r"hotjar",
        r"hj\(",
        r"static\.hotjar\.com",
    ],
    "Intercom": [
        r"intercomSettings",
        r"widget\.intercom\.io",
        r"intercom\.io",
    ],
    "Heap Analytics": [
        r"heap\b",
        r"heapanalytics\.com",
    ],
    "Segment": [
        r"analytics\.load\(",
        r"segment\.com",
        r"cdn\.segment",
    ],
    "Shopify / Internal": [
        r"shopify",
        r"Shopify\.",
        r"shop\.app",
    ],
}

ELEVAR_COVERED = {
    "GA4 / Google Analytics",
    "Meta / Facebook Pixel",
    "TikTok Pixel",
    "Google Ads / Conversion",
    "Klaviyo",
    "Microsoft / Bing Ads",
    "Reddit Pixel",
}


def get_svc():
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    return build("tagmanager", "v2", credentials=creds, cache_discovery=False)


def workspace_path():
    return f"accounts/{ACCOUNT_ID}/containers/{CONTAINER_ID}/workspaces/{WORKSPACE_ID}"


def detect_signals(html: str) -> dict[str, list[str]]:
    """Return {vendor: [matched_patterns]} for each vendor detected in html."""
    found = {}
    for vendor, patterns in ELEVAR_SIGNALS.items():
        hits = []
        for pat in patterns:
            if re.search(pat, html, re.IGNORECASE):
                hits.append(pat)
        if hits:
            found[vendor] = hits
    return found


def classify(signals: dict) -> str:
    covered = [v for v in signals if v in ELEVAR_COVERED]
    not_covered = [v for v in signals if v not in ELEVAR_COVERED]
    if not signals:
        return "KEEP (no known vendor)"
    if covered and not not_covered:
        return "DELETE (Elevar covers: " + ", ".join(covered) + ")"
    if covered and not_covered:
        return "REVIEW (Elevar covers " + ", ".join(covered) + "; NOT covered: " + ", ".join(not_covered) + ")"
    return "KEEP (vendor not on Elevar: " + ", ".join(not_covered) + ")"


def main():
    svc = get_svc()
    print("Fetching all tags from workspace 192...")
    all_tags = svc.accounts().containers().workspaces().tags().list(
        parent=workspace_path()
    ).execute().get("tag", [])

    custom_html = [t for t in all_tags if t.get("type") == "html"]
    print(f"  {len(all_tags)} tags total, {len(custom_html)} Custom HTML\n")

    results = []
    for t in sorted(custom_html, key=lambda x: x.get("name", "")):
        name = t.get("name", "?")
        tag_id = t.get("tagId", "?")
        html_body = ""
        # Custom HTML tag body is in parameter key "html"
        for param in t.get("parameter", []):
            if param.get("key") == "html":
                html_body = param.get("value", "")
                break

        signals = detect_signals(html_body)
        verdict = classify(signals)

        results.append({
            "id": tag_id,
            "name": name,
            "path": t.get("path", ""),
            "html": html_body,
            "signals": signals,
            "verdict": verdict,
        })

        print(f"  [{tag_id}] {name}")
        print(f"    → {verdict}")
        if signals:
            for vendor, pats in signals.items():
                print(f"       {vendor}: {pats[0]}")
        print()

    # Write full report
    out_path = Path.home() / "Downloads" / "HairMNL-GTM-TierC-Analysis-2026-04-30.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nFull analysis written to: {out_path}")

    # Summary
    from collections import Counter
    verdicts = Counter()
    for r in results:
        cat = r["verdict"].split("(")[0].strip()
        verdicts[cat] += 1
    print("\nSummary:")
    for cat, count in sorted(verdicts.items()):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
