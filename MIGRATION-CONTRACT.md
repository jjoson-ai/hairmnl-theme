# Migration Contract — Pipeline 6 ↔ Pipeline 8 work

> **READ THIS BEFORE TOUCHING `layout/`, `sections/`, OR `snippets/`.**
> Last updated: 2026-05-18 PM after the cache-shadow escalation (`49ae3dc`).
> Originally added: 2026-05-18 AM after the yxte regression (`b0997d3`).

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

## Hard rules — cache-shadow defense (added 2026-05-18 PM)

The 2026-05-18 escalation revealed that the original wiring lint (Rule 1)
caught `{% render %}` orphans but **missed the silent drops of
`{{ '<file>.js' | asset_url }}` references**. The P4 wave-a port
(`0cd30cf`) commented out `jquery.min.js`, `custom-theme.js`, `shop.js`,
`lazysizes.js`, and `custom-theme.css` loads from `layout/theme.liquid`
— assuming a P8-bundled `theme.js` would replace them. The bundle wasn't
built. For 24 days Shopify's edge page cache served HTML rendered BEFORE
the port, hiding the breakage entirely. Today's Stream A pushes
invalidated the cache progressively and exposed compounding regressions
(no megamenu, no product images, vertical sliders).

Recovery required a full revert of `layout/theme.liquid` to commit
`6d4a246` (commit `49ae3dc`). Rules 5–10 prevent recurrence.

### Rule 5 — Cache-bypass verification is mandatory after every `theme.liquid` push to live.

Wait 60–120s after `shopify theme push --theme=131664707683 --only=layout/theme.liquid`,
then run:

```bash
curl -sL "https://www.hairmnl.com/?_cb=$(date +%s%N)" \
  -H "Cache-Control: no-cache" -H "Pragma: no-cache" \
  > /tmp/post-push.html
```

Diff rendered `<script src>` and `<link rel="stylesheet">` tags against
the expectation from the Wiring delta table (Rule 2). If a tag from the
old `theme.liquid` persists, the cache hasn't rolled — wait longer.
**NEVER stack another push on top until verification passes.** The
cumulative cache-invalidation effect breaks attribution and produces the
compounding regressions seen on 2026-05-18.

### Rule 6 — No "drop-and-pray" commits.

If a commit drops a `{% render %}`, `{{ '<file>' | asset_url }}`, or
`<script src=...>` reference that the live storefront still depends on,
the **replacement must ship in the same commit**. "Pending P8 port" is
not an acceptable justification for dropping a dependency that
Pipeline 6.1.3 still uses today.

The P4 wave-a port (`0cd30cf`) violated this by dropping jquery /
custom-theme.js / shop.js / lazysizes assuming a P8-bundled theme.js
would replace them. The bundle didn't exist. Cost: one full session day
+ a customer-visible live outage window between cache invalidation and
emergency revert.

If the replacement isn't ready: **leave the legacy dependency loaded.**

### Rule 7 — Pre-flight pull before any `theme.liquid` push.

Before `shopify theme push --theme=131664707683 --only=layout/theme.liquid`:

```bash
mkdir -p /tmp/preflight/layout
shopify theme pull --theme=131664707683 --only=layout/theme.liquid \
  --path=/tmp/preflight --nodelete
diff /tmp/preflight/layout/theme.liquid layout/theme.liquid
```

If the live state doesn't match local `main`, the cache has been hiding
a previous regression — **do not push.** Investigate the divergence
first. Pushing over a hidden-divergent state guarantees cache
invalidation will expose whatever was hiding (this is what fired the
2026-05-18 escalation).

### Rule 8 — Live-state HTML diff in every theme.liquid PR.

Any PR touching `layout/theme.liquid` must include in its body the
BEFORE / AFTER diff of rendered `<script src>` and
`<link rel="stylesheet">` tags from a cache-bypass fetch of the staging
or dev theme:

```bash
curl -sL "https://creations-gdc.myshopify.com/?preview_theme_id=141168312419&_cb=$(date +%s%N)" \
  -H "Cache-Control: no-cache" \
  | grep -oE 'src="[^"]*\.js[^"]*"|href="[^"]*\.css[^"]*"' | sort -u
```

Paste the diff in the PR body. Reviewer checks the diff matches the
Wiring delta table (Rule 2). No diff = no review approval.

### Rule 9 — Extended wiring lint covers `asset_url` (not just `render`).

`scripts/check-snippet-wiring.py` is being extended (bd `4brc.lint`) to
detect `{{ '<file>.js' | asset_url }}` and `{{ '<file>.css' | asset_url }}`
orphans alongside `{% render %}` orphans. Any `assets/*.js` or
`assets/*.css` in the repo must be either:

1. Referenced via `asset_url` somewhere, OR
2. Deleted from `assets/`, OR
3. Added to `os2-migration/intentionally-orphan-assets.txt` with bd-id
   + `target_wire_by`.

The pre-push hook and `.github/workflows/snippet-wiring.yml` enforce
this. Bypassing the hook requires explicit operator approval in chat.

### Rule 10 — P8 deployment gate.

The P4 wave-a port (`0cd30cf`) landed on `main`. A "p5-sync" commit
(`c108dc7`) on branch `claude/p4-pathb-cc` re-enabled `custom-theme.js`
+ `custom-theme.css` for visual parity. **That branch never merged.**
The broken P4 state landed on `main` while the parity restore did not.

For any future P8 main-branch push to live theme `131664707683`:

1. **Bundled `theme.js` must be built** and replace every dropped
   dependency (megamenu init, slider init, product card hover, etc.).
2. **Operator runs a side-by-side live diff** (staging vs live) on
   incognito with cache-bypass headers and visually confirms parity.
3. **PR cites the specific assets being removed** AND demonstrates the
   replacement is loaded via Rule 8 diff.
4. **Operator gives explicit `--allow-live` approval in chat.**

This rule is a hard gate. `--allow-live` for Stream B work without
operator approval triggers incident review.

---

## Incident log

### 2026-05-18 morning — yxte regression (`b0997d3`)

- **Root cause**: P4 wave-a port (`0cd30cf`, 2026-05-17) dropped
  `{% render 'css-overrides' %}` and `{% render 'web-vitals-reporter' %}`
  calls. Snippets kept on disk; callsites removed.
- **Detection**: ~24h after P4 wave-a — CLS-fix work appeared to have no
  effect on field data; investigation found `#MainContent` as dominant
  shift target across 422+ events.
- **Fix**: re-add the renders (`b0997d3`).
- **Rule added**: Rule 1 (`scripts/check-snippet-wiring.py`).

### 2026-05-18 afternoon — cache-shadow escalation (`49ae3dc`)

- **Commits in the chain**: `9eea186` → `fffa99d` → `7493108` → (revert)
  `49ae3dc`.
- **Root cause**: Same P4 wave-a port (`0cd30cf`) ALSO commented out
  `custom-theme.css`, `custom-theme.js`, `jquery.min.js`, `shop.js`,
  `lazysizes.js` loads — assuming a P8-bundled `theme.js` would replace
  them. Bundle wasn't ready. Shopify edge page cache
  (etag `page_cache:14124580:*`) served pre-P4 HTML for 24 days,
  hiding the breakage. Today's Stream A pushes progressively
  invalidated the cache and exposed compounding regressions.
- **Symptoms (operator-visible)**: no megamenu, no product images on
  Best Sellers, vertical hero carousel, vertical collection sliders.
- **Fix**: full revert of `layout/theme.liquid` byte-for-byte to commit
  `6d4a246` (1120 lines, last pre-P4 working state). Snippets
  `mbc-bundles.liquid` and `template-swatch.liquid` (deleted from git
  but still on Shopify storage) auto-resolved their renders.
- **Rules added**: Rules 5–10. Lint extension scheduled as bd `4brc.lint`.

### 2026-05-18 evening — coordination-collision pattern (no live impact)

- **Commits affected**: `284de00` (Phase B.1 architecture doc),
  `c60bd87` (TBT investigation doc). Both authored by CC; both also
  bundled OC swarm CSS edits to `snippets/css-overrides.liquid` and/or
  `sections/menu-buttons.liquid` due to bd's `auto-export-git-add`
  behavior staging OC's working-tree modifications during my bd
  commands.
- **Symptoms**: commit attribution mismatched (commit message said
  "no code changes" but a CSS file was modified). Functional state on
  origin/main was correct (OC work was lint-clean + intended). No
  live-site impact (stream:b only).
- **Mitigation**: §5 coordination protocol expanded with point #6
  (pre-commit hygiene rule). Required `git diff --cached` check + use
  `git restore --staged` for foreign files before every CC commit
  when any OC swarm is active.

---

## What MIGRATION ports must preserve

When refactoring `layout/theme.liquid` or any file that contains
`{% render %}` calls, the following are **non-negotiably preserved on live**
until the cutover happens:

### Renders (snippet callsites)

1. **`{% render 'css-overrides' %}`** — 23+ CLS fixes + brand styling.
2. **`{% render 'web-vitals-reporter' %}`** — the entire RUM data pipeline
   feeding the perf dashboard, every CLS investigation, and `bd` issue
   triage. Without this, the team flies blind.
3. **`{% render 'canonical' %}`** — SEO canonical tag.
4. **`{% render 'hairsalon-schema' %}`** — local-business schema (Salon
   branch SEO).
5. **`{% render 'social-meta-tags' %}`** — OG / Twitter card tags.

### Asset loads (script + stylesheet)

The 2026-05-18 PM incident showed these are EQUALLY non-negotiable. The
P4 wave-a port dropped all of them silently. Until a P8-bundled
replacement is built AND verified on staging:

6. **`{{ 'jquery.min.js' | asset_url }}`** — required by P6 megamenu,
   collection sliders, product card hover, and many app snippets.
7. **`{{ 'custom-theme.js' | asset_url }}`** — ~456 KB of P6 brand
   JavaScript (megamenu dropdowns, sliders, sticky filter, etc.).
8. **`{{ 'custom-theme.css' | asset_url }}`** — ~5K LoC of P6 brand
   styling (product card layout, megamenu chrome, button overrides).
9. **`{{ 'shop.js' | asset_url }}`** — product card interactions.
10. **`{{ 'lazysizes.js' | asset_url }}`** — image lazy-load handling
    (the `.fade-in` opacity flip on `.lazy-image` containers depends on
    the `lazyloaded` class lazysizes adds).
11. **`{{ 'pswp.css' | asset_url }}`** — PhotoSwipe zoom modal styling.
12. **`{{ 'vertex-recommendations.css' | asset_url }}`** — Vertex AI
    rec rail styling (scoped to `.hairmnl-theme .vrec-*`).
13. **`{{ 'cart-page.css' | asset_url }}`** — conditional on
    `template == 'cart'`, ~54 `.cart__template` selectors.

### Infrastructure

14. **The 5 preconnect lines** (bd `t8vd`) for cdn.shopify.com,
    googletagmanager, personalizer.io, klaviyo, judge.me.
15. **The CSS deferral block** (bd `ujg6.9`) — preload+onload swap (or
    media=print swap) for the deferred async CSS files. Pattern may
    change but the deferral must remain.

If a port commit changes how any of these are loaded, the PR description
must explain how the new mechanism preserves the same behavior, AND
provide the Rule 8 live-state HTML diff demonstrating it.

---

## Coordination protocol (multi-session)

This repo is worked on by both human engineers and AI sessions (Claude
Code, OpenCode). To prevent stream collisions:

1. **At session start**, every AI session reads:
   - This file (`MIGRATION-CONTRACT.md`) — including the new Rules 5-10
   - `os2-migration/intentionally-orphan.txt` (current dormant snippets)
   - `os2-migration/intentionally-orphan-assets.txt` (asset allowlist,
     once Rule 9 lint lands)
   - The most recent `bd ready -n 20` output
2. **Before claiming a `bd` issue**, check its `stream:` label. If
   `stream:both`, the session must announce in the issue's notes which
   stream owns the change. If unclear, ask the user.
3. **Before pushing a commit that touches `layout/theme.liquid`**:
   - Run `python3 scripts/check-snippet-wiring.py` and confirm exit 0
     (pre-push hook does this, but verify by hand on refactor commits).
   - **Run the pre-flight pull per Rule 7.**
   - **After the push**, do the cache-bypass verify per Rule 5.
   - **Never stack a second push** until verify passes.
4. **At session end**, if the session created or modified a
   `{% render %}` callsite OR an `asset_url` reference in
   `layout/theme.liquid`, update the relevant `bd` issue with the new
   wiring state AND the Rule 8 live-state HTML diff.
5. **Parallel sessions must coordinate**: if two sessions are operating
   on `main` simultaneously and either touches `layout/theme.liquid`,
   neither pushes to live until both have rebased + verified the
   combined diff. Today's cache-shadow escalation happened in part
   because two sessions (Stream A live perf + P8 migration) pushed
   independently and the cumulative effect produced unattributable
   regressions.
6. **Pre-commit hygiene when an OC swarm is in flight**: bd's
   auto-export hooks call `git add` on modified files when bd
   commands run (e.g., `bd update`, `bd close`, `bd export`). If an
   OC swarm has written files to your working tree mid-session, those
   files will be silently bundled into your next commit even when you
   only intended to commit your own work.

   Observed pattern (2026-05-18, twice in AM, then 5 more times in
   one evening session):
   - Commit `284de00` (Phase B.1 doc) silently bundled OC's
     `sections/menu-buttons.liquid` + `snippets/css-overrides.liquid`
     edits from the ujg6.27 + ujg6.29 swarm.
   - Commit `c60bd87` (TBT investigation doc) silently bundled OC's
     `snippets/css-overrides.liquid` edits from the ujg6.17 swarm.
   - 2026-05-18 evening: 5 more strikes in a single CC session despite
     this contract section being already codified — ee522e3 / 5097433
     bundled ujg6.18 OC work; 662cb0d bundled 2i8b.22 brand-collection
     into a Klaviyo-audit-titled commit; 691fa2d bundled `sections/related.liquid`
     into the 2i8b.16 close; ujg6.19 close swept in OC's hairmnl-common.js
     section 8 + sections/section-collection.liquid.

   In every case the functional outcome was harmless (the OC work was
   real, lint-clean, and got pushed). But commit attribution was wrong
   and a reviewer couldn't audit either commit cleanly — the doc
   commit's message said "no code changes" while a CSS file was being
   modified.

   **Mitigation — REQUIRED tooling for every CC commit when any OC
   swarm is active or recently completed.** The 7-strike rate across
   two sessions despite a prose mitigation proves that "remember to
   run git diff --cached" is insufficient discipline. The mitigation
   needs to be a tool:

   1. **Use `scripts/safe-commit.sh`** — explicit-file-list commit
      wrapper. Unstages everything bd touched, stages only the listed
      files, sanity-checks the staged set matches the request, then
      commits. Usage:
      ```
      bash scripts/safe-commit.sh -m "message" path/to/file1 path/to/file2
      # OR for multi-line messages:
      bash scripts/safe-commit.sh -F /tmp/msg.txt path/to/file
      ```
      The script logs any pre-staged foreign files as evidence — if
      it reports a non-empty pre-staged set, that's the §5 #6 pattern
      catching a near-miss.

   2. **If you must use raw `git commit`** (one-off, hooks, etc.),
      run `git diff --cached --stat` IMMEDIATELY before commit and
      verify the file list matches your intended scope. If foreign
      files appear, `git restore --staged <file>` to unstage them
      before committing.

   3. **Never assume your commit-message file list matches reality**
      — write the commit only after `git diff --cached --stat` matches
      what your commit message describes.

   The cheaper alternative for high-coordination periods: pause CC
   commits until the OC swarm has explicitly committed and pushed its
   own work. Then rebase onto OC's commit and commit your work on top.

   **What does NOT work:** a blocking `pre-commit` hook. bd's
   auto-export legitimately runs `git add` on bd-state files; a
   blanket "don't commit multi-file" guard breaks bd's workflow.
   The proactive `safe-commit.sh` wrapper is the right layer.

---

## Recovery if a regression slips through

Two failure modes are now documented (yxte AM + cache-shadow PM, both
2026-05-18). Detection paths:

1. **Daily dashboard check**: `dashboard/data/snapshots.jsonl` should
   show monotonically improving (or stable) CLS p75. Sudden regression
   across multiple templates = check `scripts/check-snippet-wiring.py`
   output (catches `{% render %}` orphans + `asset_url` orphans per
   Rule 9).
2. **Weekly orphan triage**: any allowlisted orphan past its
   `target_wire_by` date emits a STALE warning. Address weekly.
3. **Post-refactor smoke**: after any commit that changes
   `layout/theme.liquid` by >50 lines, draft-push the change, run a
   `psi` baseline against draft + live, fail if median CLS regresses
   >0.05 or LCP regresses >300ms.
4. **Cache-bypass spot-check after every Stream A `theme.liquid` push
   to live**: per Rule 5, 60–120s wait + cache-bypass curl + diff.
   Without this, the 24-day cache shadow can re-form silently.
5. **Pre-flight pull before any `theme.liquid` push** per Rule 7. Stops
   pushes over a hidden-divergent state from forcing cache invalidation
   that exposes latent breakage.

### Emergency revert playbook

When live is broken AND root cause is unclear AND time is critical:

1. Find the last known-good commit for `layout/theme.liquid`:
   `git log --oneline -30 -- layout/theme.liquid`
2. Restore byte-for-byte:
   `git show <commit>:layout/theme.liquid > layout/theme.liquid`
3. Verify the snippet wiring lint still passes (snippets referenced by
   the older `theme.liquid` may have been deleted — but Shopify storage
   often still has them, verify with `shopify theme pull`).
4. Single-file push:
   `shopify theme push --theme=131664707683 --allow-live --only=layout/theme.liquid`
5. Wait 60–120s, then cache-bypass verify per Rule 5.
6. Commit with `revert(stream:a/EMERGENCY): ...` prefix and a full
   Wiring delta table showing what came back. Push to origin/main.

Worked example: commit `49ae3dc` (2026-05-18 PM cache-shadow revert).

---

## Pointers

- Migration epic: `bd show hairmnl-theme-2i8b` (Pipeline 8.1.1)
- Live theme epic context: `CLAUDE.md` (root)
- App TAE migration matrix: `os2-migration/app-compatibility-matrix.md`
- Customization audit (P6 freeze tracking): `os2-migration/customization-audit.md`
- Orphan allowlist: `os2-migration/intentionally-orphan.txt`
- Wiring lint: `scripts/check-snippet-wiring.py`
- CI gate: `.github/workflows/snippet-wiring.yml`
