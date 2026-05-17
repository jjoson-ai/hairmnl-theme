# Migration decision — recommendation, timeline, cost

> **Status:** Final v1.0. Re-open if any P1 inputs are materially superseded, or if a trigger fires and the cost-benefit calc has shifted.
> Ticket: `hairmnl-theme-80z0.5` (P2.2). Inputs: P1.1, P1.2, P1.3, P2.1.
> **Decision date:** 2026-05-17

> **This is the doc to open when a migration trigger fires** (see `migration-triggers.md`). It tells you which target, on what timeline, with what budget, and what risk.

---

## TL;DR

| Field | Value |
|---|---|
| **Recommended target** | **Pipeline 8.1.1** (Groupthought) |
| **Recommended timeline** | 5-week sprint, starting within 2 weeks of trigger firing |
| **Estimated total cost** | 3.5–5.5 operator-weeks (one operator + Claude on Opus 4.7 / High), 90% confidence range |
| **Estimated wall-clock window** | 5 weeks (parallel-run + cutover included), plus 4 weeks of post-cutover CrUX field monitoring |
| **Reversibility** | High — flip back to Pipeline 6.1.3 via admin publish, ~5 minutes |
| **Top three risks** | 1) `custom-theme.js` rewrite landmines, 2) Legacy snippet apps without TAE versions, 3) Custom-theme.css selector misses for Dawn-style DOM |

---

## Recommendation: Pipeline 8.1.1

### Why this target (vs Dawn, vs Hydrogen)

From `target-theme-research.md`, the three candidates trade differently along the same axes. The ranking:

| Axis | Best | Why |
|---|---|---|
| Porting cost | **Pipeline 8** | Same vendor, ~70% section-pattern overlap, bundled-JS architecture preserved |
| Performance gain | Three-way tie | All deliver the same architectural wins (TBT -93%, CLS 0) — choice is not perf-driven |
| Long-term vendor risk | Dawn | Shopify-maintained; Pipeline 8 is acceptable (5+ year Pipeline-6 record) |
| Feature parity with current site | **Pipeline 8** | Brand-collection patterns, hero variants, custom-content sections all map closely |
| Operational fit | **Pipeline 8** | Operator familiarity; familiar Pipeline editor; same Liquid idioms |
| Migration risk | **Pipeline 8** | Smallest porting surface = smallest blast radius |

**Tiebreaker:** Pipeline 8 wins 4 of the 6 axes that we actually pay a cost on (porting cost, feature parity, operational fit, migration risk). Dawn is theoretically cleaner long-term but the porting-cost delta (3–5 weeks vs 6–10 weeks) is substantial and the Dawn long-term advantage is contingent on us not migrating *again* later — at which point we'd save the cost differential. Hydrogen is ruled out at our current scale; it's a 3–6 month engineering project, not a port, and pays for itself only at much larger AOV / traffic numbers than HairMNL operates at.

### The case for not picking Dawn

Dawn is the technically purest choice. It loses on the cost axis: roughly **double the wall-clock** (6–10 weeks vs 3–5) and adds two significant risks our P1 data confirms:

- 31 brand-collection sections (~52K LoC) have no Dawn equivalent — Dawn's section primitives are different shape. We'd be redesigning, not porting.
- `custom-theme.js` (9,118 lines) must be **rewritten** as ES modules for Dawn. On Pipeline 8 it can be **ported**.

If we picked Dawn, the migration would land closer to 8 weeks and carry more design re-decisions than this initiative is scoped for. Pipeline 8 is the pragmatic move; we revisit Dawn if Groupthought EOLs Pipeline 8 (which is years out, see trigger 3 in `migration-triggers.md`).

### The case for not picking Custom/Hydrogen

Headless makes sense when (a) you've outgrown theme limitations on UI, (b) you operate at a scale where the perf ceiling on themed Shopify is genuinely binding, or (c) you have engineering capacity to support a React app indefinitely. None of these apply to HairMNL today. The P1.3 perf data confirms the perceived perf ceiling is mostly third-party-app weight, not the theme. Going headless to escape app weight would replace one problem (slow apps) with a bigger one (we now own all the integration glue and a separate hosting + deploy pipeline).

---

## Timeline — 5-week sprint

This is the **planned shape**, not a commitment. Actual wall-clock varies with what NEED-VERIFY apps turn up during Phase 0. Detailed phase steps in `runbook.md`.

```
Trigger fires
  │
  ▼
Week 0   ─┬─  Phase 0: Backup + freeze (2 days)
          │   Phase 1: Install Pipeline 8 on dev (1 day)
          │   Phase 2: Settings + branding config (2 days)
          │
Weeks 1–2 ┼─  Phase 3: Port customizations (8–10 working days)
          │     • Day 1–2:  Layout + theme.liquid port
          │     • Day 3–4:  CSS variables + css-overrides port
          │     • Day 5–7:  Consolidate 31 brand-collection sections → 1 parameterized
          │     • Day 8–10: custom-theme.js port (9K LoC → 5K LoC target after dead-code removal)
          │
Week 3    ─┼─  Phase 4: App re-integration (5 working days)
          │     • Day 1–2: TAE-ready apps (toggle + verify each, 10 apps)
          │     • Day 3–5: Legacy snippet apps (port to TAE where available, manual port for the rest)
          │
Week 4    ─┼─  Phase 5: Parallel-run + visual QA (5 working days)
          │     • Day 1–3: Side-by-side template comparisons (product / collection / cart / blog / account / search)
          │     • Day 4–5: Edge-case testing (LimeSpot recs, Klaviyo popups, Reamaze chat, cart drawer)
          │
Week 5    ─┴─  Phase 6: Cutover (1 day) + Phase 7: Post-cutover verification (4 days)
                 • Cutover during low-traffic window
                 • Real-time PSI + CrUX monitoring for 24h
                 • Rollback trigger criteria locked in (see runbook §7.4)

Weeks 6–9 ─────  Post-cutover CrUX field-data window (no theme changes; just watch)
```

### Why 5 weeks (not 3, not 8)

- **Phase 3 (port customizations) is the dominant cost driver — 8–10 working days.** The 31 brand-collection sections require consolidation (one-time win, but real work), and `custom-theme.js` is the wild card.
- **Phase 4 (app re-integration) is uncertain** because of 10 NEED-VERIFY apps (P1.1). If most of those have TAEs, the phase compresses to 3 days. If several lack TAEs and need manual ports, it stretches to 7 days. The 5-day estimate is the median.
- **Phase 5 (parallel-run) is non-compressible.** Visual QA against a complex site with many templates and apps takes a working week of focused attention. Skipping or compressing this is where most migrations break.

### Why "starting within 2 weeks of trigger firing"

The runbook + decision doc give us a 2-week head start because the inputs are pre-built. The 2-week window lets us:
- Confirm the trigger isn't transient (most triggers should be reviewed once more before commitment).
- Refresh PSI baselines, CrUX field data, and the app matrix in case they've drifted since 2026-05-17.
- Re-validate Pipeline 8's `141168312419` install (or do a fresh install if vendor has shipped a newer version).
- Negotiate calendar with merchandising team for the cutover window.

---

## Cost estimate

### Operator effort

| Phase | Working days (90% range) | Confidence |
|---|---|---|
| Phase 0 — Backup + freeze | 1–2 | High |
| Phase 1 — Install dev theme | 0.5–1 | High |
| Phase 2 — Settings + branding | 1–3 | Medium |
| Phase 3 — Port customizations | 7–12 | **Low** (depends on custom-theme.js + brand-collection consolidation) |
| Phase 4 — App re-integration | 3–7 | Medium (depends on NEED-VERIFY outcomes) |
| Phase 5 — Parallel-run + visual QA | 4–6 | High |
| Phase 6 — Cutover | 0.5–1 | High |
| Phase 7 — Post-cutover verification | 2–5 | High |
| **Total** | **19–37 working days** | |
| **Median wall-clock** | **5 weeks** | |
| **Operator-weeks** | **3.5–5.5** | |

The Phase 3 estimate carries the most uncertainty. If `custom-theme.js` reveals deeper Pipeline-6 coupling than the audit found, Phase 3 stretches.

### Tooling / external costs

| Item | Cost |
|---|---|
| Pipeline 8 license | $0 (free upgrade for existing licensee) |
| Dawn license | n/a (not selected) |
| Shopify Plus / app costs | $0 change — same plan, same apps |
| PSI / Lighthouse | $0 (existing API key) |
| Test theme installs | $0 (count against Shopify's 20-theme limit but we have headroom) |
| **Tooling total** | **$0** |

### Lost-merchandising-time cost

Phase 5 (parallel-run + QA) overlaps with normal merchandising work but Phase 6 (cutover) requires a planned non-merchandising window of 24–48 hours. Schedule for low-traffic weekday (Tuesday or Wednesday morning, Asia/Manila timezone).

---

## Risk register

| # | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| 1 | `custom-theme.js` (9,118 LoC) port reveals deeper Pipeline-6 coupling than audit found | Medium | High — could extend Phase 3 by 5+ working days | Phase 3 starts with a 1-day spike to test-port 10% of `custom-theme.js`; re-estimate before continuing |
| 2 | A NEED-VERIFY app (Searchanise / Personalizer.io / BookThatApp / VisualQuizBuilder / Pro Blogger) lacks a TAE and requires manual port that's harder than expected | Medium | Medium — Phase 4 stretches | Resolve all 10 NEED-VERIFY rows in Phase 0 (verify via Shopify admin + vendor docs) before Phase 4 starts |
| 3 | CSS overrides (621 LoC, 18 blocks) miss Pipeline-8 DOM class names; CLS regressions slip into post-cutover | Medium | Medium — partial CLS regression visible to users until fixed | Phase 5 visual QA must specifically test each of the 18 CLS-fix scenarios on Pipeline 8 dev |
| 4 | Vertex AI recommendation system (303 + 134 LoC) requires `vertex.recs` metafield schema preserved through migration | Low | High — could break the rec engine on cutover | Verify metafield schema is theme-independent (it should be — metafields are store-level); test rec render on dev theme before cutover |
| 5 | Brand-collection consolidation breaks an unanticipated section variant (one of the 31 has a unique setting we missed) | Low | Medium — one branded landing page renders incorrectly | Phase 5 explicitly QAs all 31 brand collection pages, not just a sample |
| 6 | Cutover hits a customer mid-checkout, causing cart abandonment | Low | Low — checkout is theme-independent | Schedule cutover during minimum-cart-activity window; no checkout code touched |
| 7 | Post-cutover PSI lab numbers regress (e.g., because real production traffic has different cache profile than preview) | Medium | Low — lab numbers are noise; field is the ground truth | Wait 4 weeks for CrUX field data before declaring success/failure |
| 8 | Groupthought ships Pipeline 8.1.2 or 8.2 mid-migration with breaking changes | Low | Low — we pin to 8.1.1 at install time | Use the specific Pipeline 8.1.1 install; don't auto-upgrade during the sprint |
| 9 | Trigger turns out to be transient or false alarm; we cut over and lose the trigger's "forcing function" benefit | Low | Low — migration is still net positive even without the trigger | Trigger-review checklist in `migration-triggers.md` requires 14 days of trigger persistence before commitment |
| 10 | Rollback is needed after some merchandising changes have been made only on the new theme | Medium | Low — merch changes are admin-side, mostly survive a rollback | Phase 5 includes a "freeze new theme settings 48h before cutover" gate |

---

## Decision authority + sign-off

This decision was synthesized from P1.1 + P1.2 + P1.3 + P2.1 by Claude (Opus 4.7 / High) for the operator (jjoson@clickcommerce.digital). The operator is the sole sign-off — no external stakeholders required.

Re-confirmation criteria before committing the 5-week sprint:
1. The trigger that fired is in `migration-triggers.md` and has held for ≥14 days.
2. P1.3 perf delta has not narrowed (i.e., Pipeline 6 hasn't somehow caught up).
3. Groupthought hasn't published a Pipeline 9 announcement that would change the target.
4. The 10 NEED-VERIFY apps from P1.1 have been resolved.

If any of these fail, re-open this doc and re-decide before sprinting.

---

## What this doc commits us to

- **One target theme:** Pipeline 8.1.1. We will not parallel-evaluate Dawn during the sprint.
- **A 5-week wall-clock budget.** If Phase 3 exceeds estimate by >50%, pause and re-plan rather than racing through.
- **The runbook in `runbook.md`** is the authoritative phase-by-phase playbook. Deviations must be explicit (log in the runbook's verification section).
- **CrUX field data, not lab PSI**, is the success metric for the migration. Lab improvements are confirming evidence, not the goal.

## What this doc does NOT commit us to

- Migrating at all. This doc is the decision *if a trigger fires*. The triggers are documented separately in `migration-triggers.md`.
- A specific calendar date. The 5-week sprint timing is relative to the trigger firing, not absolute.
- Replacing apps that are flagged for replacement (LimeSpot, Appikon, BSS B2B) — those happen on their own ticket timelines, not during the migration sprint. The migration ports what's installed at trigger-time.
