# OS 2.0 Migration — App Deprecation Monitoring

| Field    | Value                                                                                      |
|----------|--------------------------------------------------------------------------------------------|
| Date     | 2026-05-17                                                                                 |
| Status   | Active                                                                                     |
| Bead     | hairmnl-theme-80z0.8                                                                       |
| Scope    | Monitoring plan for the 6 highest-risk apps per the compatibility matrix (bd hairmnl-theme-80z0.1). Covers how we'll detect vendor deprecation announcements before they become customer-facing breaks. |

## 1. Approach

**Hybrid — email-alias subscription for vendors with changelog mailing lists + quarterly manual review for vendors without.** Email subscriptions are zero-maintenance and surface changes within days of publication, which is fast enough to act before any deprecation deadline. Quarterly manual review catches vendors with less structured release processes at acceptable latency (~90 days max delay). No scraper is deployed — scraping depends on vendor page structure and adds ongoing maintenance burden that outweighs the benefit when email + manual already covers the risk surface.

## 2. Monitoring Target Selection

These 6 apps were selected from the full compatibility matrix as the highest **dependency × deprecation risk** cohort. Each is either a high-traffic customer-touching integration (Klaviyo, Re:amaze, Searchanise), a significant performance drag (Elevar, Personalizer.io), or a legacy snippet burden (Pro Blogger). LimeSpot was excluded: it is targeted for full replacement with Vertex AI (bd oyw), so monitoring its deprecation trajectory is moot.

| # | App            | Risk | Embed Type                | TAE Status       | Footprint          |
|---|----------------|------|---------------------------|------------------|--------------------|
| 1 | Klaviyo        | High | App embed block           | 🟢 TAE-ready     | ~120 KB always-on  |
| 2 | Re:amaze       | High | App embed block           | 🟡 Mixed          | 213 KB             |
| 3 | Personalizer.io| High | DNS prefetch only          | 🔴 Legacy only    | 249 KB always-on   |
| 4 | Elevar         | High | App embed block           | 🟡 Mixed          | 2.6 s PSI latency  |
| 5 | Pro Blogger    | High | Multiple legacy snippets  | 🔴 Legacy only    | ~950 LoC in theme  |
| 6 | Searchanise    | High | Hardcoded script           | 🔴 NEED-VERIFY   | Unknown            |

## 3. Monitoring Table

| # | App            | Vendor Changelog URL                                    | Email List Signup URL                        | Monitoring Mechanism       | Review Cadence | Owner     |
|---|----------------|---------------------------------------------------------|----------------------------------------------|----------------------------|----------------|-----------|
| 1 | Klaviyo        | https://www.klaviyo.com/changelog                      | https://www.klaviyo.com/changelog (subscribe) | Email subscription         | As-received    | Dev team  |
| 2 | Re:amaze       | https://support.reamaze.com/releases                   | n/a (check releases page)                   | Email + manual fallback   | As-received    | Dev team  |
| 3 | Personalizer.io| n/a (no known changelog URL)                           | n/a                                          | Quarterly manual check    | Quarterly      | Dev team  |
| 4 | Elevar         | https://elevar.app/updates                              | https://elevar.app/updates (subscribe)       | Email subscription         | As-received    | Dev team  |
| 5 | Pro Blogger    | n/a (no known changelog URL)                            | n/a                                          | Quarterly manual check    | Quarterly      | Dev team  |
| 6 | Searchanise    | https://www.searchanise.com/news                        | n/a                                          | Quarterly manual check    | Quarterly      | Dev team  |

## 4. First Quarterly Review

**Date:** 2026-08-17 (~90 days from this doc's landing date).

**Check each vendor changelog for these deprecation keywords:**

- "legacy embed"
- "Theme App Extension only"
- "end of support"
- "deprecated"
- "migration required"
- "sunset"

Document findings in `os2-migration/app-compatibility-matrix.md` and update this monitoring table if URLs change.

## 5. Escalation Criteria

Any of the following observations fires migration **Trigger #1** (primary app breaks) or **Trigger #3** (vendor end-of-life) per `os2-migration/migration-triggers.md`:

1. Vendor announces removal of legacy embed support with an explicit deprecation date.
2. App update requires an OS 2.0 Theme App Extension (TAE) — legacy snippet/include no longer works.
3. Vendor sends a "last version supporting legacy themes" notification.
4. App silently breaks on Pipeline 6 after an automatic update.

If any criterion is met, escalate immediately: do not wait for the quarterly review cycle.

## 6. Maintenance

- **URL changes:** Update this doc immediately when a vendor changes their changelog or release-notes URL.
- **Quarterly cross-reference:** During each review, cross-check apps against `os2-migration/app-compatibility-matrix.md` for TAE status changes.
- **App additions/removals:** If an app is added to or removed from the store, update the monitoring table in Section 3 accordingly.
- **LimeSpot:** Remove this note once LimeSpot is fully replaced by Vertex AI.

## 7. Appendix — Known Vendor URLs

```
Klaviyo        https://www.klaviyo.com/changelog
Re:amaze       https://support.reamaze.com/releases
Elevar         https://elevar.app/updates
Searchanise    https://www.searchanise.com/news
```

## 8. Action items for operator (not in scope of this doc)

These require human action beyond writing this plan:

- ☐ Register `migration-alerts@hairmnl.com` (or chosen alias) and configure forwarding.
- ☐ Subscribe the alias to Klaviyo and Elevar changelog email lists.
- ☐ Re:amaze: bookmark the releases page and confirm whether email-subscribe is available; fall back to quarterly manual if not.
- ☐ Add a recurring calendar event "OS2 migration vendor changelog review" for 2026-08-17, repeating quarterly.
