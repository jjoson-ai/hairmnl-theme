# Sonnet handoff — overnight P6→P8 visual parity loop

You (Sonnet 4.6) are taking over from Opus 4.7 mid-session. Same conversation context, same worktree, same active dev theme. Auto mode is on; you execute autonomously while the operator sleeps.

## First wake-up special case (READ FIRST)

A pre-existing `ScheduleWakeup` will fire at ~02:26 with the prompt "Check OC dispatch progress for bd ticket hairmnl-theme-2i8b.11". That OC dispatch is already CLOSED (Opus closed it before handoff — bd ticket status=closed, full notes attached). The wake-up prompt is stale.

When that wakeup fires:
1. Skip the OC check — `bd show hairmnl-theme-2i8b.11 --json | jq '.[0].status'` will say `closed`. Note that and move on.
2. **Do NOT stop** as that wakeup's prompt instructs. Instead, this brief takes precedence: start the per-template parity loop.
3. Begin Iteration 1 (homepage) immediately.

## What's already done tonight (don't re-do)

- ✅ Cart drawer slides open on ATC — commit `e81459f`, `assets/hairmnl-custom.js` section 7.
- ✅ Sitewide typography fix — commit `7ac5d3a`, `:root` font-stack overrides at the top of `snippets/css-overrides.liquid`. Body now BasisGrotesquePro-Regular sans-serif; headings remain SelfModern serif by design.
- ✅ Phase 5 audit of `snippets/css-overrides.liquid` (bd `hairmnl-theme-2i8b.11` CLOSED): structural diff vs P6 LIVE shows only 2 expected drops (`#pwa-modal`, `limespot`) — no missed ports. No invalid CSS patterns. kt0 lint clean.

## What's confirmed identical between P6 LIVE and P8 dev

- `assets/theme.css` (md5 match)
- `snippets/cart-drawer.liquid` (md5 match)
- `snippets/css-variables.liquid` (md5 match — both have the trailing-comma Liquid bug; tonight's override compensates)
- `snippets/custom-fonts.liquid` (md5 match)
- Cart-related settings in `config/settings_data.json` (identical)
- `snippets/css-overrides.liquid` is structurally complete vs P6 (audit closed clean)

## Where the remaining diffs likely live (your hunt territory)

- **App-injected styles**: Free Gifts ECOM (FGSECOMAPP), LoyaltyLion, Klaviyo, Reamaze, Judge.me, Smart SEO. Each app injects its own CSS that interacts with theme classes differently between P6 and P8.
- **Asset CSS files** loaded alongside theme.css: `vertex-recommendations.css`, `judge.me/*.css`, `problogger*.css`, `custom-theme.css`. These can have rules that conflict with or extend theme.css.
- **Template-specific JSON sections**: `templates/index.json`, `templates/product.json`, `templates/collection.json`, etc. — section types or block configurations may differ.
- **Liquid snippets unique to specific templates**: `snippets/product-grid-item.liquid`, `snippets/product-grid-item-branded*.liquid`, etc.

## The overnight loop — per-template pattern

For each template, one iteration takes ~15–25 min. Pace via `ScheduleWakeup` between iterations (delaySeconds 1200–1800 → stays just outside cache window but keeps you focused).

### Iteration steps

1. **Pick the next template** (priority order below; if last template found no diffs, skip ahead to next).
2. **Browser side-by-side**:
   - Navigate Edge to `https://www.hairmnl.com/<path>?preview_theme_id=141168312419` (P8 dev).
   - Take screenshot, save with `save_to_disk: true` for visual reference.
   - Navigate to `https://www.hairmnl.com/<path>` (LIVE P6 — drops preview cookie).
   - Take screenshot.
   - Compare visually (you're a multimodal model — you can see the screenshots).
3. **For each clear visual diff**, identify the element via JS `document.elementFromPoint` or `querySelector`. Read its computed style on BOTH themes; diff the styles.
4. **Write a CSS override** in `snippets/css-overrides.liquid` under a new section:
   ```
   /* ============================================================
    * P5 overnight parity (Sonnet, 2026-05-18) — <template name>
    * ============================================================ */
   ```
   Each rule needs a one-line comment explaining the diff it fixes.
5. **Push**: `shopify theme push --theme=141168312419 --only=snippets/css-overrides.liquid --nodelete`.
6. **kt0 lint**: `python3 scripts/check-overlay-css.py` must exit 0 before commit.
7. **Verify**: reload the P8 preview, screenshot, compare against the P6 screenshot from step 2.
8. **Commit + push**: `git add snippets/css-overrides.liquid && git commit -m "p5-parity: <template> <one-line summary>" && git push`.
9. **Log to `OVERNIGHT_STATUS.md`**: one line — `[HH:MM] <template>: <N> rules added; commit <sha>; verified ✓` or `[HH:MM] <template>: no diffs found, skipped`.
10. **ScheduleWakeup** for the next template (1500s ≈ 25 min default).

### Template priority order

1. Homepage (`/`) — hero, best sellers row, brand collection blocks, "For Frizz" / category tile grid.
2. Product page (`/products/kerastase-genesis-anti-hair-fall-fortifying-serum`) — gallery, variant selector, ATC area, Free Gift section, reviews carousel, description block, "Buy It With" row.
3. Collection page (`/collections/best-sellers`) — filter sidebar, product grid card layout, pagination.
4. Cart page (`/cart`) — standalone page, NOT the drawer (drawer was done tonight).
5. Header — top bar, announcement bar, mobile menu (if you can trigger it).
6. Footer — newsletter signup, link columns, payment icons, copyright bar.
7. Search results (`/search?q=davines`).
8. Blog index (`/blogs/tousled-magazine`) + sample article.
9. Account login page (`/account/login`).
10. Brand pages if reachable (e.g., `/collections/davines`).

If none of these surface diffs, you've hit parity. Stop and write the summary.

### What "no diff" looks like

If two screenshots show no visible differences (allowing for app-injected content like Free Gifts popdowns which vary by session), write `no diffs found, skipped` to the log and move to the next template. Do not invent rules.

## Hard rules (don't violate)

- **Never push to live theme `131664707683`**. All pushes go to dev `141168312419`.
- **Never modify** `assets/theme.js`, `assets/custom-theme.js`, `assets/vendor.js`, `snippets/theme.liquid`, `config/settings_data.json`, `config/settings_schema.json`.
- **Never** `git push --force`, `git reset --hard`, `git checkout .` , or `--no-verify`.
- **Never create new sections, templates, or layouts** to fix a parity diff — write CSS overrides only.
- **Never** invoke `/oc-swarm` or `/offload` overnight (OC paid weekly quota usage).
- **Don't pick up other bd tickets** between iterations — focus is parity only.

## Soft stop conditions (one wake → exit gracefully)

Stop the loop and write a summary if ANY of these trigger:
- `git push` or `shopify theme push` fails with non-zero exit code → don't retry; document and stop.
- `python3 scripts/check-overlay-css.py` exits non-zero → revert the offending hunk, push the revert, document the kt0 violation, stop.
- Auto-mode classifier blocks any tool call twice in the same iteration → stop, document why.
- Browser extension stays broken (`Cannot access chrome-extension://`) after 3 consecutive recovery attempts (tabs_create_mcp + close old) → document and stop the loop; visual verification is no longer possible.
- 3 templates in a row show "no diffs found" → parity reached, stop and write summary.
- Working tree has unexpected changes you didn't make → STOP immediately; do not commit; document.

No time cap, no LoC cap, no template-count cap, no commit-count cap. Run until the operator wakes up or one of the above safety stops triggers. The operator explicitly said: continue as long as you can.

When you exhaust the priority template list, expand: cycle through brand collections (`/collections/davines`, `/collections/kerastase`, `/collections/loreal`, etc.), check the gift card landing page, the rewards page, the magazine articles. There's always one more diff somewhere.

## Browser tool workarounds (learned tonight)

- The Edge/Chrome MCP extension enters a stuck state every ~5–10 minutes. Symptom: `Cannot access a chrome-extension:// URL of different extension`.
- **Recovery that works**: `tabs_create_mcp` to make a fresh tab, then `tabs_close_mcp` on the old one. The fresh tab usually works for the next 5–10 min.
- **Avoid**: long-running JS Promises in `javascript_tool` (`new Promise(r => setTimeout(r, 1500))`). Use shorter checks; split sequential reads into multiple short JS calls.
- **The `preview_theme_id` parameter is preserved across navigation if you click app-internal links**, but dropped when you click anchor tags that already point to the bare URL (e.g., from `creations-gdc.myshopify.com` redirecting to `hairmnl.com`). Use full `?preview_theme_id=141168312419&t=N` URLs with incrementing `t` to bust the URL cache.
- `getComputedStyle(el).fontFamily` works after `document.readyState === 'interactive'`, you don't need `complete`.

## Output expectations

- Per template: 0–1 commits to `snippets/css-overrides.liquid`. NEVER bundle multiple templates in one commit — keeps rollback granular.
- Commit message format: `p5-parity: <template-noun-phrase> — <short fix summary>`.
- Each iteration appends ONE line to `OVERNIGHT_STATUS.md` under an `## Overnight loop log` heading (create the heading if missing).
- On final stop: append a `## Final summary` section with: templates touched, total commits, total rules added, kt0 status, any unresolved items the operator should look at first.

## Operator wake-up handoff

- The operator will check `OVERNIGHT_STATUS.md` first thing — make sure it's the source of truth.
- If any commit has been pushed, make sure `git status` shows `up to date with origin` before you stop.
- Leave the working tree clean. Stash anything unfinished with `git stash push -u -m "WIP: <reason>"`.
- Don't leave a dangling ScheduleWakeup that fires after the operator wakes up.

## Tooling reference

- Worktree path: `/Users/y9378348c/Projects/hairmnl-theme/.claude/worktrees/sleepy-volhard-7bf010`
- Active branch: `claude/p4-pathb-cc`
- Dev theme ID: `141168312419`
- Live theme ID (DO NOT TOUCH): `131664707683`
- Status log: `OVERNIGHT_STATUS.md` (already exists with prior session notes)
- kt0 lint: `python3 scripts/check-overlay-css.py`
- P6 reference snapshot (read-only): `/tmp/p6-snippets/` (snippets/css-overrides.liquid, snippets/custom-fonts.liquid, layout/theme.liquid)
- P6 theme.css snapshot: `/tmp/p6-snippets/assets/theme.css` (md5-identical to P8's at `/tmp/p8-themecss/assets/theme.css`)
- P8 theme.css snapshot (read-only): `/tmp/p8-themecss/assets/theme.css`

## When to wake the operator vs continue silently

Continue silently for: routine iteration, expected wake-up cycles, "no diffs" findings.

Stop and let the operator find your summary in the morning for: any soft-stop trigger, structural mystery that warrants discussion, or a finding that affects more than one template (e.g., another invalid-CSS-variable bug like the one Opus found tonight).

---

**Final note from Opus**: tonight's two fixes were diagnostic root-causes, not pattern matches. If you spot a symptom that smells weird (e.g., "this color is wrong everywhere"), pause and diagnose — don't just write 50 overrides. The trailing-comma bug was exactly that kind of trap.

Good luck. Sleep tight, operator.
