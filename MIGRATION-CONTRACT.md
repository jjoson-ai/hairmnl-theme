# Migration Contract — Pipeline 6 ↔ Pipeline 8 work

> **READ THIS BEFORE TOUCHING `layout/`, `sections/`, OR `snippets/`.**
> Last updated: 2026-05-18 after the yxte regression (`b0997d3`).

This repository has **two parallel streams of work** on the same `main`
branch — but they push to different Shopify themes:

| Stream | Scope | Shopify theme target | Lifecycle | bd label |
|---|---|---|---|---|
| **LIVE** | Pipeline 6.1.3 storefront optimization (CWV / perf / bug fixes) | **`131664707683`** ("Pipeline 6 - Fix share image") | Ships to customers immediately on push | `stream:a` |
| **MIGRATION** | Pipeline 8.1.1 port (`bd hairmnl-theme-ujg6` + `bd hairmnl-theme-2i8b` epics) | **`141168312419`** ("Pipeline 8 Working Demo") | Ships at the cutover date (TBD) | `stream:b` |
| **INTERFACE** | Work that touches files used by both streams | Both, with coordinated push order | Coordinated review required before merge | `stream:both` |

The two streams **share the same `main` branch** but push to different themes.
That's the collision surface — a file edit on main goes to whatever theme
the next `shopify theme push` targets.

Without coordination, MIGRATION refactors silently undo LIVE optimization
work. That's what happened on 2026-05-17 (commit `0cd30cf`, "P4 wave-a port")
— a 1120→401 line `layout/theme.liquid` rewrite dropped two `{% render %}`
callsites, silently disabling **23 documented CLS fixes** plus the
**Core Web Vitals → GA4 RUM reporter**. Discovered the next day by accident
while debugging bd `yxte`.

---

## Hard rules

### Rule 1 — `scripts/check-snippet-wiring.py` must pass before push.

A pre-push hook and a GitHub Action (`.github/workflows/snippet-wiring.yml`)
run this lint. It enumerates every `snippets/*.liquid` file and verifies
each is referenced by `{% render '<name>' %}` or `{% include '<name>' %}`
somewhere in the codebase. Any orphan must be in
`os2-migration/intentionally-orphan.txt` with a bd-id and a target
wire-by date.

**Why it exists**: catches "file kept on disk, callsite dropped" — the
exact pattern that caused yxte. The dormant snippet's content review
during a port commit can pass code review without anyone noticing the
file no longer has a referrer.

```bash
python3 scripts/check-snippet-wiring.py             # pass/fail report
python3 scripts/check-snippet-wiring.py --json      # machine-readable
python3 scripts/check-snippet-wiring.py --verbose   # show all snippets
```

### Rule 2 — MIGRATION refactors must include a "Wiring delta" in the PR body.

When a Stream B commit touches `layout/theme.liquid`, `layout/*.liquid`,
`sections/*.liquid`, or anything that has `{% render %}` callsites, the
PR description **must** include a table:

```
| Snippet/asset | Action | Replacement |
|---|---|---|
| `css-overrides` | KEPT | rendered after all CSS asset loads |
| `custom-fonts` | DEFERRED | bd 2i8b.4, target_wire_by 2026-06-30 |
| `bold-common` | RETIRED | moved to Theme App Extension |
```

The table proves the author considered each callsite. No table = no review
approval. If the change is mechanical and touches zero callsites, write
"No wiring changes" explicitly.

### Rule 3 — bd label discipline.

| Label | Use when… |
|---|---|
| `stream:a` | Issue's fix ships to live theme `131664707683` ("Pipeline 6 - Fix share image") under current architecture. |
| `stream:b` | Issue's fix only lands at P8 cutover. Belongs to the `2i8b` migration epic. |
| `stream:both` | Fix touches both code paths OR the file is shared (e.g., `layout/theme.liquid`, the css-overrides callsite). **Requires coordinated review before close.** |

Apply via `bd update <id> --add-label <label>`. Existing issues are
backfilled per `os2-migration/bd-stream-labeling.md`.

### Rule 4 — Pipeline 6 customization freeze (already in CLAUDE.md).

This rule pre-existed. It says: don't add new bespoke P6 code without
the three-question check + `os2-migration/customization-audit.md` entry.
This contract reinforces it: any new Stream A code that adds a new
`{% render %}` callsite must also list it in the eventual P8 port plan.

---

## What MIGRATION ports must preserve

When refactoring `layout/theme.liquid` or any file that contains
`{% render %}` calls, the following are **non-negotiably preserved on live**
until the cutover happens:

1. **`{% render 'css-overrides' %}`** — 23+ CLS fixes + brand styling.
2. **`{% render 'web-vitals-reporter' %}`** — the entire RUM data pipeline
   feeding the perf dashboard, every CLS investigation, and `bd` issue
   triage. Without this, the team flies blind.
3. **`{% render 'canonical' %}`** — SEO canonical tag.
4. **`{% render 'hairsalon-schema' %}`** — local-business schema (Salon
   branch SEO).
5. **`{% render 'social-meta-tags' %}`** — OG / Twitter card tags.
6. **The 5 preconnect lines** (bd `t8vd`) for cdn.shopify.com,
   googletagmanager, personalizer.io, klaviyo, judge.me.
7. **The CSS deferral block** (bd `ujg6.9`) — preload+onload swap for the
   6 async CSS files.

If a port commit changes how any of these are loaded, the PR description
must explain how the new mechanism preserves the same behavior.

---

## Coordination protocol (multi-session)

This repo is worked on by both human engineers and AI sessions (Claude
Code, OpenCode). To prevent stream collisions:

1. **At session start**, every AI session reads:
   - This file (`MIGRATION-CONTRACT.md`)
   - `os2-migration/intentionally-orphan.txt` (current dormant snippets)
   - The most recent `bd ready -n 20` output
2. **Before claiming a `bd` issue**, check its `stream:` label. If
   `stream:both`, the session must announce in the issue's notes which
   stream owns the change. If unclear, ask the user.
3. **Before pushing a commit that touches `layout/theme.liquid`** or
   removes any `{% render %}` call, run
   `python3 scripts/check-snippet-wiring.py` and confirm it exits 0.
   The pre-push hook does this automatically, but verify by hand on
   refactor commits.
4. **At session end**, if the session created or modified a
   `{% render %}` callsite, update the relevant `bd` issue with the new
   wiring state.

---

## Recovery if a regression slips through

The 2026-05-18 yxte regression was found by visual symptom (CLS shifts
not improving despite "shipped fixes"). To accelerate detection of the
next one:

1. **Daily dashboard check**: `dashboard/data/snapshots.jsonl` should
   show monotonically improving (or stable) CLS p75. Sudden regression
   across multiple templates = check `scripts/check-snippet-wiring.py`
   output.
2. **Weekly orphan triage**: any allowlisted orphan past its
   `target_wire_by` date emits a STALE warning. Address weekly.
3. **Post-refactor smoke**: after any commit that changes
   `layout/theme.liquid` by >50 lines, draft-push the change, run a
   `psi` baseline against draft + live, fail if median CLS regresses
   >0.05 or LCP regresses >300ms.

---

## Pointers

- Migration epic: `bd show hairmnl-theme-2i8b` (Pipeline 8.1.1)
- Live theme epic context: `CLAUDE.md` (root)
- App TAE migration matrix: `os2-migration/app-compatibility-matrix.md`
- Customization audit (P6 freeze tracking): `os2-migration/customization-audit.md`
- Orphan allowlist: `os2-migration/intentionally-orphan.txt`
- Wiring lint: `scripts/check-snippet-wiring.py`
- CI gate: `.github/workflows/snippet-wiring.yml`
