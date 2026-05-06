# GTM JS Error Tag Fix — Coordinator Handoff

**Issue:** `hairmnl-theme-l3g` (P1, open)
**Audience:** Claude Code (Opus 4.7) coordinator — execute the fix
**Created:** 2026-05-06 by minimax-m2.7:cloud via OpenCode

---

## What is broken

GA4 shows ~40K `js_error` events over 7 days with `(not set)` for all three custom dimensions (`error_type`, `error_message`, `error_source`). The dashboard shows only two rows: `(not set)` and `?`.

**Root cause:** The GTM tag `GA4 - JS Error Event` (container GTM-M4NKSBD, **live version 140** published 4 days ago) is misconfigured in two ways:

### Bug 1 — Wrong trigger
- **Current:** fires on `Initialization - All Pages`
- **Problem:** fires at page load (before any error can occur), sending empty dimension values on every pageview
- **Correct trigger:** `Custom Event - hairmnl_js_error` (trigger ID 772) — fires when `hairmnl_js_error` dataLayer event fires

### Bug 2 — Event name mismatch
- **Theme pushes:** `{event: 'hairmnl_js_error', error_type, error_message, error_source}`
- **GTM tag sends to GA4:** `eventName: js_error`
- **Result:** even if the trigger were correct, the event name doesn't match what the theme sends

The `hairmnl_js_error` rename happened 2026-05-02 (commit 5fb4be7) to avoid collision with Elevar's existing `js_error` pushes. The GTM tag was never updated to match.

---

## Fix instructions (execute in this order)

### Phase 1 — GTM (high priority, do first)

**Manual GTM changes required (or API equivalent):**

1. **Update GA4 - JS Error Event tag (tag ID 776, in live v140):**
   - Change trigger from `Initialization - All Pages` → `Custom Event - hairmnl_js_error` (trigger 772)
   - Verify `eventName` parameter is `js_error` (or change to match intended behavior — see decision below)
   - Verify `eventSettingsTable` maps: `error_type` → `{{DLV - js_error_type}}`, `error_message` → `{{DLV - js_error_message}}`, `error_source` → `{{DLV - js_error_source}}`

2. **Fix 3 other tags with orphaned trigger 2147479553:**
   These are high-priority tags that reference a trigger (ID `2147479553`) that **does not exist anywhere in the container**. Without a valid trigger, these tags cannot fire. Investigate and either recreate the original trigger or remap to a valid one:

   | Tag ID | Tag Name | Purpose | Impact of broken trigger |
   |--------|----------|---------|--------------------------|
   | 12 | Conversion Linker | Fires on page loads to set `NID`, `gclid`, cookie for cross-domain GA4 tracking | **All GA4 conversion data broken** — last-click attribution fails, GCLID/braid cookies not set |
   | 415 | Klaviyo - Form Submission Listener | Tracks form submission events for Klaviyo email flows | **Revenue attribution broken** — email automation flows won't fire correctly |
   | 94 | TrafficGuard Tag | Fraud protection — verifies traffic quality before allowing tracking | **Fraud detection disabled** — invalid traffic may inflate GA4 metrics |

   These 3 tags likely all shared the same trigger (probably a custom event trigger that was deleted). The fix is to identify the intended trigger for each tag and reconnect them, then publish.

3. **Publish the container** after making all tag changes

### Phase 2 — Dashboard query (can be done in parallel)

**File:** `scripts/build-perf-dashboard.py`

**Current code (line 503):**
```python
dimension_filter=_and(_eq("eventName", "js_error")),
```

**Change to:**
```python
dimension_filter=_and(_in("eventName", ["js_error", "hairmnl_js_error"])),
```

This captures both:
- `js_error` — Elevar's legacy events (still arriving in GA4)
- `hairmnl_js_error` — theme's corrected events (will grow after GTM fix)

**Verify:** run `python3 scripts/build-perf-dashboard.py --render-only` after the change.

---

## Decision required before GTM fix

**Question: Should the GTM tag send `js_error` or `hairmnl_js_error` to GA4?**

Option A — Keep `eventName: js_error` in GTM tag:
- GA4 continues to receive `js_error` events
- Elevar's events are also captured under `js_error` (mixed source)
- Pros: historical continuity, single event name
- Cons: can't distinguish Elevar vs theme errors in GA4

Option B — Change to `eventName: hairmnl_js_error`:
- GA4 receives only theme errors as `hairmnl_js_error`
- Elevar's events still come in as `js_error` (separate)
- Pros: clean separation, accurate attribution
- Cons: requires GA4 custom event registration for `hairmnl_js_error`

**Recommendation:** Option A — keep `eventName: js_error` in the GTM tag. The theme's error fields (`error_type`, `error_message`, `error_source`) already correctly populate the custom dimensions. The only fix needed is the trigger change from `Initialization - All Pages` → `Custom Event - hairmnl_js_error`.

If Elevar's events also send `error_type`/`error_message`/`error_source`, they will also populate the dimensions. If they send different field names, they will still show `(not set)` — which is informative about Elevar's data quality.

---

## Additional findings

### 4 other broken trigger references (critical)

Trigger ID `2147479553` is used by 4 tags but **does not exist anywhere in the container**:

| Tag ID | Tag Name | Impact if not fixed |
|--------|----------|---------------------|
| 776 | GA4 - JS Error Event | JS error custom dimensions always `(not set)` |
| 12 | Conversion Linker | All GA4 conversion attribution broken |
| 415 | Klaviyo - Form Submission Listener | Email automation revenue tracking broken |
| 94 | TrafficGuard Tag | Fraud detection disabled |

All 4 tags reference the same non-existent trigger. This suggests the trigger was deleted (perhaps a custom event trigger for `dl_*` prefixed events) but the tags were never updated. **All 4 must be fixed together** in the same GTM session.

The trigger that was deleted was likely named something like `Custom Event - dl_*` (old dataLayer naming convention). The 2019 live container may have had this trigger, but it was removed without updating the tags that depended on it.

### Workspace vs live discrepancy
Workspace 197 (Default Workspace) has massive unpublished changes — container fingerprint `1573742594630` vs workspace fingerprint `1777714610172`. The workspace state is stale and does NOT reflect the live version 140. **Do not trust workspace API queries for live container state.** Use the GTM UI or the live version API.

The workspace appears to contain years of unpublished changes from 2019 onwards.

### GA4 custom dimensions are registered (confirmed)
- `error_type` (Event scope, registered 2026-04-28) ✓
- `error_message` (Event scope, registered 2026-04-28) ✓
- `error_source` (Event scope, registered 2026-04-28) ✓
- `template` (Event scope, registered 2026-05-06) ✓

### Credentials available
- GTM OAuth: `~/.config/hairmnl-gtm-token.json` + `~/.config/hairmnl-oauth-client.json`
- GA4 service account: `~/.config/hairmnl-ga4-key.json`
- GTM container: account `4702257664`, container `12266146` (GTM-M4NKSBD), workspace `197`, live version `140`

---

## Handoff file
This file is at `docs/gtm-js-error-handoff-2026-05-06.md`. Also see:
- `dashboard/index.html` (lines 590-593) — current broken state
- `scripts/gtm-fix-js-error-vars.py` — existing script (targets workspace 190, needs updating to 197 for API approach)
- `docs/handoff-log.md` — append this session's work