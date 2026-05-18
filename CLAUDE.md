# HairMNL Shopify theme — workflow guard

## Theme IDs

- **Live theme**: `131664707683` (" Pipeline 6 - Fix share image")
- **Draft theme**: `140785582179` (Claude Code draft)

## START HERE: Migration Contract (read before touching layout / sections / snippets)

This repo runs **two parallel streams of work** on the same `main` branch:

| Stream | Scope | bd label |
|---|---|---|
| LIVE | Pipeline 6.1.3 storefront optimization (CWV / perf / bugs) | `stream:a` |
| MIGRATION | Pipeline 8.1.1 port (`bd hairmnl-theme-2i8b` epic) | `stream:b` |
| INTERFACE | Touches both — coordinated review required | `stream:both` |

**Full contract: `MIGRATION-CONTRACT.md`** at the repo root. It governs
how refactors in one stream avoid silently undoing work in the other.

The contract enforces three guards:

1. **CI lint** — `scripts/check-snippet-wiring.py` catches the
   "file kept, callsite dropped" regression class (this is what caused
   bd `yxte` on 2026-05-18 — a P4 refactor silently disabled 23 CLS fixes
   + the entire RUM data pipeline). Runs in `.github/workflows/snippet-wiring.yml`
   and as a `.githooks/pre-push` hook.
2. **bd label discipline** — every issue gets `stream:a`, `stream:b`, or
   `stream:both` so cross-stream changes get the right review.
3. **PR "Wiring delta" table** — MIGRATION refactors that touch
   `layout/theme.liquid` (or any file with `{% render %}` callsites) must
   list every callsite and its disposition (KEPT / DEFERRED-with-bd-id /
   RETIRED-to-TAE).

### Pre-push hook setup (one-time per clone)

```bash
git config core.hooksPath .githooks
```

The hook runs `scripts/check-snippet-wiring.py` automatically before every
push. Bypassing with `--no-verify` requires explicit user approval.

### Snippets known to be dormant during migration

See `os2-migration/intentionally-orphan.txt` — each entry has a bd-id and
`target_wire_by` date. Entries past their date emit a STALE warning
(weekly triage recommended).

---

## Pipeline 6 customization freeze — ask before adding bespoke code

The store is on Pipeline 6.1.3 (transitional OS 2.0). A future migration to Pipeline 8.1.1 is on the trigger watchlist at `os2-migration/migration-triggers.md` (quarterly review). Every new Pipeline-6-specific customization is migration debt — porting cost on day-zero of any future migration.

**Before adding any new Pipeline 6 customization (any new bespoke Liquid, new custom snippet, new `.scss.liquid` file, new CSS override block, new `custom-theme.js` behavior, new layout/theme.liquid edit beyond what an app embed handles), ask these three questions in order:**

1. **Can this be a no-op for migration?** Could the same outcome be achieved by:
   - A Shopify theme setting (color, font, layout choice exposed by the theme editor)?
   - A Shopify app (existing app's TAE block, or a small app install)?
   - A theme-independent intervention (GTM tag, Klaviyo block, Smart SEO config)?
   - A merchandising change (collection setup, product metafield, content edit)?
   - If yes to any: do that instead. No code customization added.
2. **If code is required, is it a stock OS-2.0 pattern?** Section block, JSON template, theme app extension hook, app embed block. These survive migration as-is. Prefer them over bespoke Pipeline 6 snippets.
3. **If bespoke Pipeline 6 code is genuinely required**, document the migration cost explicitly:
   - Tag the new code with a comment: `{# MIGRATION-DEBT: will need port to OS 2.0; reason = ... #}` (or equivalent for CSS / JS).
   - Add a row to `os2-migration/customization-audit.md` § "Recent additions" (create the section if missing) with: file path, LoC, what it does, port difficulty (easy / medium / hard), and why the no-op alternatives in step 1 weren't sufficient.
   - This makes the cost visible to the next migration-decision review and to the operator at the time of cutover.

**Exceptions that don't require this process:**
- **Critical bug fixes** to existing customizations (the bug already exists, the fix just makes it work).
- **CLS / perf fixes** that the kt0 / customization-audit table already counts as `need-port` — these are continuations of known migration debt, not new debt.
- **Removing** Pipeline 6 customizations (subtraction is always free).

**Why this rule exists:** P1.2 (`os2-migration/customization-audit.md`) inventoried ~19,000 bespoke LoC across ~75 files. ~46 of those need porting on migration. Every new bespoke line widens that porting surface. The cost of asking the three questions is seconds; the cost of porting an unnecessary customization through Phase 3 of the runbook is hours per file. The freeze isn't "stop all work" — it's "be deliberate about whether code is the right tool."

**Reference:** `os2-migration/` directory contains the full migration program. Quarterly trigger review per `migration-triggers.md`.

## CSS containment kt0 rule (regression history: 2026-05-11 header, 2026-05-12 Reamaze)

These CSS properties create a new containing block for **fixed/absolute-positioned
descendants**:

- `contain: layout | paint | strict | content`
- `transform: <anything-but-none>`
- `filter: <anything-but-none>`
- `backdrop-filter: <anything-but-none>`
- `perspective: <anything-but-none>`
- `will-change: transform | filter | perspective`

When applied to an overlay container (chat widget, cart drawer, modal, sticky
header, mobile nav, body-injected popup), Reamaze/Pipeline/LL/etc. internal
positioning math silently breaks — children end up at coordinates relative to
the wrong ancestor (off-screen, zero-size, etc.). Two visible regressions this
caused already:

- **2026-05-11** — sticky header got `contain:layout`; cart icon dropdown
  positioned wrong.
- **2026-05-12** — `[id^="reamaze-widget"] { contain:layout }` (bd 7fz)
  pushed the Reamaze chat icon to `right:-58px` and the chat container to
  `bottom:-16914.5px`, hiding the live-chat bubble from customers for ~10
  days (bd hairmnl-theme-lki).

### Automated check

`scripts/check-overlay-css.py` scans the repo for any of these properties
applied to a known-overlay selector. Runs in CI on every push touching
`*.liquid`/`*.css`/`*.scss` (`.github/workflows/kt0-css-lint.yml`).

**Run locally before any CSS push**:

```sh
python3 scripts/check-overlay-css.py
```

Exit 0 = clean. Exit 1 = at least one new violation.

### Acknowledging intentional uses

If you genuinely need one of these properties on an overlay selector
(e.g. `display:none` makes containment moot, or your overlay has no
absolute-positioned descendants), add a comment containing the literal
token `kt0-OK` inside the rule body:

```css
.my-overlay {
  /* kt0-OK: display:none means containment is moot */
  display: none !important;
  contain: layout !important;
}
```

The lint accepts any `/* ... kt0-OK ... */` comment as acknowledgment.
Always include a one-line justification — future readers (and future AI
sessions) need to know why you decided it was safe.

### Adding new overlay selectors

The lint's selector list is in `OVERLAY_PATTERNS` near the top of
`scripts/check-overlay-css.py`. When the store gains a new overlay
(new chat tool, new modal app, etc.) add its selector pattern there
so containment regressions on the new overlay get caught.

---

## The push regression that triggered this guard (2026-04-26)

`shopify theme push --only=<file>` uploads the **local working tree**
content of `<file>` — not git HEAD, not the live version. If the
working tree has stale or reverted content for that file, the push
overwrites a good live version with old code.

Today this happened with `layout/theme.liquid`. The working tree had
been reverted (probably during an earlier hang investigation) to a
state without jquery defer, with duplicated Judge.me, and without
several other perf optimizations that **were already live**. The
`--only=layout/theme.liquid` push silently regressed all of them.

## The rule

**Before any `shopify theme push --only=<file>`, always:**

1. Inspect `git diff HEAD <file>` — confirm the diff is exactly the
   intended hunks. If you see unexpected changes, stop.
2. If the diff is unexpected, decide:
   - Restore from HEAD: `git checkout HEAD -- <file>`, then re-apply
     just the intended edit.
   - Or pull from live: `shopify theme pull --theme=131664707683
     --only=<file> --path=/tmp/live-pull` and diff against that.
3. Only push after the diff matches the intended change.

**Never** `shopify theme push` without `--only=<file>` flags. A
no-filter push uploads the entire working tree, which is almost
guaranteed to drag stale or WIP content into live.

## Git as source of truth

Git HEAD should reflect what's on live. After any push:

- Stage the pushed files: `git add <file1> <file2> ...`
- Commit with a description of the change.
- If anything in the working tree was *not* pushed but contains
  forward edits, stash it: `git stash push -u -m "WIP: ..." <files>`.

Drift between git HEAD and live is what enables the regression bug.

## Pre-push verification (recommended)

For higher-stakes pushes (layouts, snippets, anything in `layout/` or
`snippets/`):

1. Push to the **draft theme** first:
   `shopify theme push --theme=140785582179 --only=<file> --nodelete`
2. Preview the draft via the Shopify admin preview URL.
3. Once verified, push the same file to live with `--allow-live`.

## Known stash

`stash@{0}` (as of 2026-04-26 — index re-verified after housekeeping
2026-05-14) holds the April 26 prefix-strip + srcset work:

- `snippets/css-overrides.liquid` (LimeSpot prefix-strip rules)
- `snippets/product-grid-item.liquid` (responsive srcset polish)
- `snippets/product-grid-item-branded-subcollection.liquid` (brand-strip)
- `snippets/limespot-prefix-strip.liquid` (new untracked snippet)

`product-grid-item-branded.liquid` was applied from this stash on
2026-04-26 (brand-strip on top of live's responsive srcset). The other
three files are still parked — partial overlap with subsequent changes
makes a clean apply risky. When picking from the stash later, prefer
cherry-pick over `git stash pop`, and always diff against live before
pushing. Verify the stash index with `git stash list` before referring
to it by index (this file's reference can drift if other stashes are
pushed on top of it).


<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:ca08a54f -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->

## Companion tools

This project has access to three globally-registered Claude Code companion tools. Use them when relevant:
- **context7** — live library/framework docs. Include `use context7` in your prompt when asking about external library APIs (React, Next.js, etc.). Avoids hallucinated API signatures.
- **memory** — knowledge-graph MCP. Use the `create_entities`, `add_observations`, `create_relations`, and `search_nodes` tools to persist facts that should outlive a session (people, decisions, project state). Memory file: ~/.claude/memory.jsonl. This is cross-project, complementary to Beads (which is per-project structured issues).
- **claude-trace** — record sessions for review. Run `claude-trace` instead of `claude` when you want a transcript; logs go to `./.claude-trace/` in cwd.
