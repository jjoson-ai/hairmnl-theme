# OS 2.0 / Pipeline 8+ migration readiness

Working directory for the theme platform readiness program. **No migration is in progress** — these documents prepare us to move quickly *if* a trigger fires.

## Start here

- **[feasibility.html](feasibility.html)** — non-technical rationale + feasibility brief. Stakeholder-facing. Updates in place as research findings land.
  - **Shareable link (post-merge to main):** https://jjoson-ai.github.io/hairmnl-theme/os2-migration/feasibility.html
  - The GH Pages publish workflow (`.github/workflows/pages.yml`) rebuilds the site whenever this directory changes.

## Research outputs (populated as work progresses)

- `app-compatibility-matrix.md` — per-app TAE readiness + current install method.
- `customization-audit.md` — quantified inventory of bespoke Liquid/CSS/JS, tagged by port difficulty.
- `perf-baseline-comparison.md` — side-by-side performance scores: current live theme vs. sandboxed Pipeline 8.
- `target-theme-research.md` — Pipeline 8 vs. Dawn vs. custom evaluation.
- `migration-decision.md` — recommended target + timeline + cost range. The doc we open if a trigger fires.
- `runbook.md` — phase-by-phase migration playbook with rollback steps.
- `migration-triggers.md` — formal definitions and measurement criteria for the five triggers.
- `vendor-monitoring.md` — how we watch app vendors for deprecation announcements.

## Scope boundary

Phase 4 — the actual migration — is **out of scope** for this directory until a trigger fires. If that happens it spins out as a separate program with its own approval.
