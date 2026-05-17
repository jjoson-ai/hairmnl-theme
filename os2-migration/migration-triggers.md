# Migration triggers — formal definitions + monitoring

> **Status:** v1.0. This is the doc you check quarterly to answer "are we still in wait-and-see?". When any **two** triggers fire, open `migration-decision.md` and proceed.
> Ticket: `hairmnl-theme-80z0.7` (P3.1).
> **Last updated:** 2026-05-17. Next quarterly review due: **2026-08-17**.

---

## How this works

The mega-epic (`hairmnl-theme-80z0`) and the stakeholder deck (`feasibility.html`) commit us to migrating **if any two of five triggers fire**. This doc operationalizes that rule.

For each trigger, this doc defines:
- **What it means** — plain-English description.
- **How we detect it** — concrete data source.
- **Threshold** — the exact number / event that crosses the line.
- **Persistence requirement** — how long it must hold before counting as "fired".
- **Who watches** — manual checks vs automated alerts.
- **Response** — what happens immediately when the trigger fires.

The 14-day persistence requirement (per `migration-decision.md` § "Decision authority + sign-off") guards against false alarms: an app might break for a day, a vendor might walk back an EOL announcement, a perf regression might be a CDN blip. A trigger only counts toward the "two of five" rule if it persists.

---

## Trigger 1 — Primary app TAE-only breakage

**Plain-English:** A primary app (Klaviyo / Re:amaze / LimeSpot / Elevar) ships an update that removes support for our current installation method and live functionality degrades.

**Why this matters:** Most likely path to forced migration. Vendor deprecation of `content_for_header` injection in favor of TAE-only delivery would silently break our integrations on Pipeline 6.1.3.

### Detection sources

| Source | Cadence | Owner |
|---|---|---|
| Vendor changelog / release notes | Weekly auto-check (per `vendor-monitoring.md` once it lands from P3.2) | Operator |
| Vendor support email announcement | As received | Operator |
| Re:amaze customer-reported breakage | Real-time | Customer-support inbox |
| PSI / CrUX field data showing a sudden INP or LCP regression that traces to a specific app's resource | Per-deploy + weekly | Operator |
| Direct live-site visual inspection (chat widget missing, popup broken, recommendations not rendering) | Ad-hoc / per-cycle | Operator |

### Threshold

**Fired** when any one of the following is true:

- A vendor (Klaviyo, Re:amaze, LimeSpot, Elevar — the "primary four") publishes a deprecation notice with an effective date for legacy `content_for_header` / hardcoded-snippet integration.
- A vendor (any of the primary four) ships an update that, when applied, breaks the integration on Pipeline 6.1.3. "Breaks" = critical functionality stops working (chat doesn't appear, popup doesn't submit, recs render empty, conversion data stops flowing).
- A NEED-VERIFY app from `app-compatibility-matrix.md` (10 of them) is confirmed to require TAE-only and lacks a working snippet/legacy path.

### Persistence

14 days. A transient outage doesn't count; the vendor's stance must hold for two weeks.

### Response when fired

1. Log the firing in this doc's verification log below (date + source).
2. Set a calendar reminder for day 14 to re-verify persistence.
3. If still firing at day 14, the trigger is "armed" — count toward the two-of-five.
4. Notify operator that one trigger is now armed; check status of the other four.

---

## Trigger 2 — Mobile CWV plateau

**Plain-English:** Despite continued performance investment, we can't break past the modern-theme ceiling on real-user metrics.

**Why this matters:** The "performance ceiling" risk in the stakeholder brief. Pipeline 8 (P1.3) shows TBT collapse and CLS-to-zero architectural wins. If our Pipeline 6 lab + field numbers stop improving despite ongoing perf work, the ceiling is hit.

### Detection sources

| Source | Cadence | Owner |
|---|---|---|
| CrUX p75 mobile metrics via PSI API (LCP, INP, CLS, FCP, TTFB) | Weekly (capture into dashboard) | Operator |
| Lab PSI mobile n=3 median | After every perf deploy + monthly anchor run | Operator |
| Internal perf-ticket backlog | Continuous | Operator (via bd) |

### Threshold

**Fired** when ALL THREE of the following hold simultaneously, sustained over a 60-day window:

1. **Mobile CrUX LCP p75 stays within ±5%** of the anchor value (anchor: 3,039ms as of 2026-05-17). I.e., real-user LCP doesn't improve.
2. **Mobile CrUX INP p75 stays within ±10%** of the anchor (anchor: 240ms). I.e., real-user responsiveness doesn't improve.
3. **At least 2 perf-work tickets land** in the 60-day window that we expected to move the needle, but didn't.

This three-pronged threshold ensures we don't count a 60-day window where we simply didn't ship perf work as a "plateau" — the trigger only fires when we tried and the metrics didn't respond.

### Persistence

60 days. The CrUX 28-day rolling window means metrics lag deploys by ~4 weeks; 60 days gives time for two full rolling windows post-attempt.

### Response when fired

1. Log in verification log.
2. Verify the perf-work tickets in the window were substantive (not just style nits).
3. If verified, mark the trigger armed.

---

## Trigger 3 — Pipeline 6 EOL announcement

**Plain-English:** Groupthought formally announces that Pipeline 6 is moving to maintenance-only or end-of-life.

**Why this matters:** Low probability, big blast radius. Forced migration on a vendor timeline rather than ours.

### Detection sources

| Source | Cadence | Owner |
|---|---|---|
| Groupthought customer portal announcements | Quarterly manual check | Operator |
| Groupthought email list (customer-support@groupthought.com or similar) | As received | Operator inbox |
| Pipeline theme listing in Shopify Theme Store (look for "Pipeline 6 — legacy" or similar badge) | Quarterly manual check | Operator |

### Threshold

**Fired** when any one of:
- Groupthought publishes (on customer portal, email, app store listing, or theme listing) an explicit statement that Pipeline 6 is in maintenance-only mode (no new features) or has a scheduled end-of-life date.
- Pipeline 6 is delisted from the Shopify Theme Store while Pipeline 7/8/9 remain available.
- Pipeline 6 stops receiving security patches for 12+ months (verified via release notes).

### Persistence

7 days. Vendor announcements are typically definitive — if Groupthought publishes an EOL, we count it within a week of confirmation.

### Response when fired

1. Log in verification log.
2. Read the EOL terms carefully — there may be a transition window (e.g., 12-month support continuation).
3. The trigger arms immediately on confirmation. If two triggers are armed, proceed to `migration-decision.md`.

---

## Trigger 4 — Onboarding tax crosses threshold

**Plain-English:** A new developer (Claude session, contractor, full-time hire) requires more than two weeks of ramp-up before they can ship safely on the Pipeline 6 codebase.

**Why this matters:** Compounding talent/maintenance cost. Pipeline 6's idioms (`.scss.liquid`, monolithic JS, jQuery, Pipeline-specific Liquid patterns) are increasingly unfamiliar to anyone hired post-2023. If onboarding cost is observably going up, we're paying a maintenance tax.

### Detection sources

| Source | Cadence | Owner |
|---|---|---|
| Onboarding-time tracking — explicit measurement when a new contributor starts | Per onboarding event | Operator |
| Claude session warmup time — how long it takes a new Claude session (without memory) to be productive on a Pipeline 6 task | Per session | Implicit (operator notices ramp-up friction) |

### Threshold

**Fired** when:
- A new contributor takes >2 weeks (10 working days) before their first independent merged PR.
- AND, the operator can attribute the slowness specifically to **Pipeline 6 idiom friction** (not domain complexity, not other code-base friction).
- AND, this has happened **twice within 6 months**.

The two-occurrence requirement keeps a one-off bad fit from triggering a migration.

### Persistence

Both occurrences must hold (not subsequently revised by the contributor catching up faster than expected). Confirm 30 days after the second occurrence.

### Response when fired

1. Log in verification log.
2. Document the two specific onboarding events with attribution.
3. Arm if confirmed.

---

## Trigger 5 — Merchandising feature gated to modern themes

**Plain-English:** The merchandising team needs a Shopify admin feature that only works on modern (OS 2.0 v2) themes and is genuinely blocking a planned campaign.

**Why this matters:** Productivity cost. Shopify is increasingly gating new admin features to modern themes — section group editing, AI section copy, theme blocks beta, drag-drop everywhere.

### Detection sources

| Source | Cadence | Owner |
|---|---|---|
| Shopify admin theme-editor release notes | As released | Operator (track via Shopify Partner emails) |
| Merchandiser-reported friction — "I wanted to do X but the editor says it requires a newer theme" | As reported | Internal Slack / direct conversation |
| Marketing campaign briefs that name a Shopify feature we don't have | Per-campaign | Marketing → Operator handoff |

### Threshold

**Fired** when:
- A merchandiser-driven business goal (campaign, seasonal page, A/B test, etc.) names a specific Shopify admin feature that requires OS 2.0 v2.
- AND, that feature has no acceptable Pipeline 6 workaround (e.g., custom section, app substitute) that can ship within the campaign's timeline.
- AND, the campaign's value justifies migration ahead of normal trigger pacing (i.e., merchandising leadership signals this is genuinely blocking, not nice-to-have).

### Persistence

The block must persist for the campaign's planning window — typically 30 days. If a workaround is found within that window, trigger doesn't fire.

### Response when fired

1. Log in verification log.
2. Validate with merchandising leadership that this is blocking (not "would be nice").
3. Arm if confirmed.

---

## Quarterly review checklist

Every 90 days (next due: **2026-08-17**), spend ~30 minutes:

- ☐ For each of the 5 triggers, check the detection sources for any new signal since last review.
- ☐ For any trigger currently armed: re-verify persistence (still holding? was it a false alarm?).
- ☐ Update the verification log below with the review date + outcome.
- ☐ If **two triggers are armed** after this review, schedule a P2.2 re-read meeting and prepare to execute the runbook.
- ☐ If **one trigger is armed** with another close to firing, add a note in the deck's Update History slide and tighten monitoring on the second.
- ☐ If **zero triggers are armed** after 12 months of monitoring, treat that as "refresh annually" — re-run P1.3 perf baseline to confirm the input data hasn't drifted, then continue wait-and-see.

Add the review reminder to operator calendar at trigger-3 review intervals (quarterly).

---

## Linkage from CLAUDE.md

The project `CLAUDE.md` should reference this doc as a quarterly review item — added in P3.3. The intent: future Claude sessions on this codebase have this doc top-of-mind when adding customizations or evaluating perf work.

---

## Verification log

| Date | Trigger | Action | Status |
|---|---|---|---|
| 2026-05-17 | — | Initial doc shipped; all 5 triggers monitored, 0 armed. | baseline |
| 2026-08-17 | (placeholder for Q3 review) | | |
| 2026-11-17 | (placeholder for Q4 review) | | |
| 2027-02-17 | (placeholder for Q1 2027 review) | | |
| 2027-05-17 | **12-month review** — refresh P1.3 baseline; re-confirm wait-and-see | | |
