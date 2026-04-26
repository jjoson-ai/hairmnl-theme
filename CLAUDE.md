# HairMNL Shopify theme — workflow guard

## Theme IDs

- **Live theme**: `131664707683` (" Pipeline 6 - Fix share image")
- **Draft theme**: `140785582179` (Claude Code draft)

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

`stash@{0}` (as of 2026-04-26) holds:

- `snippets/css-overrides.liquid` (LimeSpot prefix-strip rules)
- `snippets/product-grid-item.liquid` (responsive srcset polish)
- `snippets/product-grid-item-branded-subcollection.liquid` (brand-strip)
- `snippets/limespot-prefix-strip.liquid` (new untracked snippet)

`product-grid-item-branded.liquid` was applied from this stash today
(brand-strip on top of live's responsive srcset). When picking from
the stash later, prefer cherry-pick over `git stash pop`, and always
diff against live before pushing.
