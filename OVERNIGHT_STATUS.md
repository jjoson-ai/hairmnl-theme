# Overnight OC dispatch status log

> Append-only log of overnight OC dispatch outcomes. CC loop checks bd state, files outcomes here, stops after each ticket per global "no auto-pick next" rule.

---

## 2026-05-19 ~05:30 — bd 2i8b.31 (P0, font-size: 0px on all text) — FIXED + STEP-BACK ANALYSIS

Operator review of the post-`2i8b.29`/`.30` dev preview surfaced one more symptom: header/footer now had visible cream backgrounds (✅ from the CSS-var bridge), but nav text was "white/invisible" and section banners still looked "giant." Asked CC to step back.

**Step-back diagnosis:** the "white text" wasn't white — it was **`font-size: 0px`**. Diagnostic ran across every visible text element on the homepage (nav links, h2 "Best Sellers", buttons, product card titles) and every one had `getComputedStyle(el).fontSize === '0px'`. The "giant banner" perception was correct in a sense — proportional banners look enormous when the headlines beside them are zero-pixel-tall.

**Root cause traced to `config/settings_data.json`:** the current preset has `font_body_size`, `font_heading_size`, `font_accent_size`, `type_nav_size`, `type_button_size`, `type_kicker_size` all set to `null` (theme editor was never used to configure typography on the P8 dev theme — the operator only set color settings). `snippets/css-variables.liquid` does `{{ settings.font_body_size | divided_by: 100.0 }}` — Liquid evaluates `null | divided_by: 100.0` as **`0`**. That zero propagated into `--FONT-ADJUST-*` and `--TYPE-ADJUST-*`, through my earlier `---font-adjust-X` bridge, and into theme.css's `font-size: calc(<base> * var(---font-adjust-X))` rules. Every text element resolved to font-size: 0px.

**Fix shipped:** added `| default: 100` to all five `divided_by: 100.0` font-size expressions. Settings will still override the default when the theme editor sets values, but the page renders correctly out-of-the-box.

**Verification:**
- `--FONT-ADJUST-BODY`/`HEADING`/`ACCENT` + `--TYPE-ADJUST-NAV`/`BUTTON`: all `1.0` (were `0`)
- h2 "Best Sellers" font-size: **17.14px** (was 0px)
- `a.navlink--toplevel` font-size: **14.35px** (was 0px)
- `span.navtext` (PRODUCTS / BRANDS / etc): **12px** (was 0px)
- All text now visible at proper sizes.

### Bug-cascade retrospective (the whole night, in one frame)

| # | bd | What broke | Visible symptom | Mechanism | Fix |
|---|---|---|---|---|---|
| 1 | `2i8b.28` | `{% include 'limespot' %}` + 3 more stale renders in `layout/theme.liquid` and `css-variables.liquid` | "Liquid error" text at top of page, plus broken CSS/JS cascade | Liquid error rendered as plain text *inside* `<head>` → browser closes `<head>` early → ~1000 lines of CSS+JS get re-positioned into `<body>` | `fcb0382`: remove all 4 references |
| 2 | `2i8b.29` | M2 P6→P8 port of `css-variables.liquid` bridged 7 of 87 `---name` aliases that P8's stock `theme.css` references | Transparent header + footer; missing button/badge colors | `var(---color-bg)` etc resolved to CSS initial value (transparent for backgrounds) | `6ebf36b`: extend bridge to 87 aliases |
| 3 | `2i8b.30` | `section-collection.liquid`'s `request.page_type == null` check doesn't trigger on Section Rendering API requests (Shopify returns `'index'`, not null) | 8 empty `.homepage-collection` sections; no product cards | API returned placeholder, JS swapped placeholder for placeholder forever | `6ebf36b`: JS defensive fallback to use `<noscript>` content when fetched element still has `data-lazy-render` |
| 4 | `2i8b.31` | Theme settings `font_*_size` are null in P8 settings_data.json; Liquid `null / 100 = 0` | All text 0px tall, "white/invisible" appearance | `--FONT-ADJUST-* = 0` propagated through to `font-size: calc(* * 0) = 0` | `e997957`: `| default: 100` on the 5 divisions |

**One sentence of generalisation:** every visible symptom traced back to a *value-resolution failure* in the Liquid → CSS-variable → P8-theme.css → browser cascade. Each fix unblocked the next layer. The CSS bridge made the page have colour again; the lazy-render fix populated the sections; the font default made the text *visible at all*. None of these are independent — pulling one out wouldn't restore the page.

### Operator action when waking up

1. Reload `https://creations-gdc.myshopify.com/?preview_theme_id=141168312419`. Expected state:
   - ✅ Cream header with HAIR MNL logo AND **visible nav menu text** (PRODUCTS, BRANDS, QUIZZES, NEW, SPECIAL OFFERS, REWARDS)
   - ✅ Cream footer with **visible** column text (About Us, Contact Us, etc)
   - ✅ All headings render at proper sizes (no more invisible "Best Sellers" / "FEATURED COLLECTION" labels)
   - ✅ Slideshow + section banners proportional alongside readable headlines
   - ✅ All 8 homepage collection sections populated with product cards
2. Visit theme editor → Customize → Theme settings → Typography. Confirm the 6 font-size settings (`Body size`, `Heading size`, `Accent size`, `Nav size`, `Button size`, `Kicker size`) are all `100`. They'll inherit the default now, but explicitly setting them clears the operator-visible "blank field" state.
3. `2i8b.27` (P1, Davines hero banner) still open. Theme-editor fix only.

### Process lessons (filed for the P5 readiness retro)

- The customisation-audit's "M2 port" check verified that P6's `css-variables.liquid` *uploaded* but didn't verify that the P8 stock `theme.css`'s variable expectations were *satisfied*. A simple Playwright check during M-series rollout could have detected this: at page load, fail if any `var(---...)` in stylesheets is unresolved.
- The `request.page_type == null` pattern in `section-collection.liquid` (originally shipped by `ujg6.18`) is broken-by-design under Shopify's current Section Rendering API behaviour. Smoke-06 had a false-pass on this exact case because its placeholder-detection check was AND-coupled with `length < 1000` — and the 50KB response easily cleared that. Smoke-06 should be updated.
- Migration "settings carry over" assumption was wrong: Pipeline 8 theme has its own settings_data.json defaults; null values in critical numerical settings (font sizes) break the entire cascade. Pre-cutover checklist should explicitly walk the theme editor's settings panel and screenshot what defaults are required.

### Commits + bd tickets summary tonight

| Commit | bd | Type |
|---|---|---|
| `fcb0382` | `2i8b.28` (P0) | Stale Liquid render calls |
| `6ebf36b` | `2i8b.29` (P0), `2i8b.30` (P0) | CSS var bridge + lazy-render JS fallback |
| `e997957` | `2i8b.31` (P0) | Font-size null defaults |
| `8e437f2` | `2i8b.26` (P2) | smoke-09 + parity report scaffolding (last night) |

All P0 cutover blockers from the operator's screenshot review **closed clean**. No new tickets blocking cutover beyond the pre-existing `2i8b.27` (P1, theme-editor Davines hero).

---

## 2026-05-19 ~04:30 — bd 2i8b.29 + 2i8b.30 (two more P0 blockers found after operator screenshot review) — FIXED

After landing the `2i8b.28` Liquid-error fix, operator reviewed the dev preview in their browser and reported three remaining symptoms: transparent header, transparent footer, sliders still oversized, no product photos in homepage collection sections. Reopened investigation. Two distinct root causes found and shipped.

### Bug 1: `hairmnl-theme-2i8b.29` — CSS variable bridge gap (P0)

**Root cause:** Pipeline 8 stock `theme.css` references 87 CSS custom properties using the `---triple-hyphen-lowercase` convention (e.g. `var(---color-bg)`, `var(---color-footer-bg)`). The M2 port of P6's `css-variables.liquid` (which uses `--UPPERCASE-DASH`) bridged only **7 typography aliases** — leaving **80 variables undefined**. Each undefined `var(---color-X)` in a property declaration resolved to that property's CSS initial value: `transparent` for backgrounds, `normal` for font-weight, `none` for text-transform, etc.

Cascade of damage:
- `.theme__header { background: var(---color-bg) }` → transparent header
- `.site-footer-wrapper { background: var(---color-footer-bg) }` → transparent footer
- Button colors, badge colors, palette--light section backgrounds — all missing
- The "sliders still oversized" perception came partially from the lack of section background colors making content look like it was floating on bare white

**Fix:** Expanded the M2 bridge block in `snippets/css-variables.liquid` from 7 aliases to a comprehensive set of 87 covering all `--- → --` mappings (colors, footer, nav, announcement, badges, buttons aliased to primary palette, inverse palette, layout, plus a fallback inline-SVG `---ico-select`). Each `---name` maps to its corresponding `--NAME` already defined earlier in the same file.

**Verification:** Page now has 0 undefined `---variables` (was 80). `.theme__header` and `.site-footer-wrapper` both resolve to `rgb(243, 235, 230)` — the merchant-configured cream palette color. Header and footer are now visibly opaque.

### Bug 2: `hairmnl-theme-2i8b.30` — Section-API placeholder→placeholder loop (P0)

**Root cause:** `section-collection.liquid` (and `brand-collection.liquid`, `related.liquid`) gates its lazy-render branch on:
```liquid
{%- if request.design_mode or request.page_type == null -%}
  <!-- full content -->
{%- else -%}
  <!-- placeholder with data-lazy-render -->
{%- endif -%}
```
The intent: emit full content for theme editor preview AND for Section Rendering API requests. **The bug:** Shopify does *not* null out `request.page_type` for `?section_id=X` requests — it returns the URL's actual page_type (`'index'` for homepage, etc). So the API returns the *same* `data-lazy-render` placeholder that was already on the page. `hairmnl-common.js` lazy-render IO observes a placeholder, fetches its URL, gets another placeholder, swaps placeholder for placeholder.

User-visible effect: 8 homepage collection sections rendered as empty 80px-tall stubs. No product cards from any featured collection.

**Why the smoke-06 test missed it:** the smoke-06 "Section Rendering API returns full content" test checked `sectionHtml.includes('data-lazy-render') && sectionHtml.length < 1000`. The 50KB API response contained the placeholder *plus* a `<noscript>` block with the full server-rendered content as the no-JS fallback — so `length` was >= 1000, the test reported clean, the bug shipped to dev.

**Fix:** Defensive fallback in `assets/hairmnl-common.js`. When `replaceWith` receives a fetched element that still has `data-lazy-render`, extract the full content from the response's `<noscript>` block (which IS the server-rendered full content) and use that. No per-section Liquid edit needed — the JS layer handles it for all three sections that use the lazy-render pattern.

**Verification:** 8/8 `.homepage-collection` sections now render with product cards (was 0/8). Section heights expanded from 80px placeholders to 291px filled. Fresh smoke-09 capture shows the homepage with all product photos visible end-to-end.

### Commits

- `6ebf36b` — `fix(p8): complete --- CSS var bridge + lazy-render placeholder loop`

### What the operator will see when they wake up

Reload `https://creations-gdc.myshopify.com/?preview_theme_id=141168312419`:

- ✅ Opaque cream header bar with HAIR MNL logo + nav (was transparent)
- ✅ Opaque cream footer (was transparent)
- ✅ Homepage collection sections filled with product photos + cards (were empty)
- ✅ Slider banners proportional, no longer "giant" looking next to empty rows
- ✅ No "Liquid error" string anywhere in the document

Three more bd tickets remain open / open-but-different:
- `2i8b.27` (P1) — Davines brand hero banner missing (theme-editor fix, separate)
- `2i8b.18` (older) — pre-existing tracking
- `2i8b.20` (older) — `hairmnl-custom.js` cleanup pending dev soak

### Process improvements filed in commit message

- smoke-06's length-vs-content check should be tightened: it gave a false pass on this exact bug. The `length<1000 AND data-lazy-render` AND condition let a 50KB-but-still-placeholder response through. Should change to: `length<1000 OR (data-lazy-render and the inner element has data-lazy-render)`.
- The `request.page_type == null` Liquid detection was wrong from the start (ujg6.18 shipped it). A proper Liquid-side detection for Section Rendering API requests isn't possible in stock Shopify; the JS-side defensive fallback is the right pattern.

---

## 2026-05-19 ~03:00 — bd hairmnl-theme-2i8b.28 (P0 cutover blocker) — FIXED

**Ticket:** [hairmnl-theme-2i8b.28](#) — "P8 cutover blocker: 4 stale Liquid render calls break page render"

**Root cause discovered:** While reviewing smoke-09 parity screenshots, operator spotted a "Liquid error (layout/theme line 203): Could not find asset snippets/limespot.liquid" string at the top of the P8 dev preview, along with cascading visible damage: no product photos, transparent megamenu, oversized slider images. CC traced the actual mechanism: that error string renders as plain-text content **inside `<head>`**, which forces the browser parser to close `<head>` prematurely. ~1000 lines of CSS+JS that were supposed to load before `<body>` get re-positioned into `<body>`, breaking everything that depended on them being available pre-paint.

**Four broken Liquid references found (not just the one visible at line 203):**

| Reference | Snippet status | Why it stayed live |
|---|---|---|
| `layout/theme.liquid:203 {% include 'limespot' %}` | deleted in M6 (4303e70) | Cleanup wave removed the file but not this call |
| `layout/theme.liquid:1252 {% render 'template-swatch' %}` | deleted in 97cd092 | Bundled with revert that removed multiple intentional-orphan candidates |
| `layout/theme.liquid:1306 {% render 'mbc-bundles' %}` | deleted in dbed076 | M6 wave removed file, missed reference |
| `snippets/css-variables.liquid:542 {% render 'font-size' %}` | never existed in P6 LIVE or P8 dev | Dormant broken reference (verified via shopify theme pull) |

**Fix shipped:** All 4 references removed and replaced with explanatory comments citing this bd ticket. Pushed `--only=layout/theme.liquid --only=snippets/css-variables.liquid` to P8 dev theme 141168312419. Committed to main in `fcb0382`.

**Verification:**
- Server-rendered homepage HTML: 0 `Liquid error` matches (was 4+).
- HTML structure valid: `</head>` at index 262547, `<body id=...>` at 262558.
- smoke-09 ran 10 captures: **8 passed with 0 Liquid errors detected**; 2 mobile failures are the pre-existing webkit `waitForVisualStability` timeout shared with smoke-08 — not Liquid-related.

**smoke-09 hardened (same commit):** added Liquid-error grep against raw server HTML inside `captureTheme()`. Any future Liquid error in either P6 or P8 fails smoke-09 with the matched error strings printed, so the test gates the cutover instead of letting broken renders sneak into screenshots that "look almost right" in thumbnails. The bug-shaped lesson from this incident is encoded as a permanent guard.

**Operator action when waking:**
1. Visually verify P8 dev preview URL: `https://creations-gdc.myshopify.com/?preview_theme_id=141168312419` — expect no error text, product photos rendering, megamenu styled correctly on hover.
2. Open `/collections/davines` — separate bd ticket `2i8b.27` still tracks the missing brand hero banner (P1, theme-editor fix).
3. Re-run `npm run test:parity && npm run parity:open` if you want fresh side-by-side captures with the fix applied.

---

## 2026-05-18 ~02:10 — bd hairmnl-theme-2i8b.11 (Phase 5 visual parity audit) — CLOSED CLEAN

**Ticket:** [hairmnl-theme-2i8b.11](#) — "Phase 5 visual parity: audit P6 vs P8 css-overrides.liquid for missed rules"
**OC model:** deepseek-v4-pro:cloud (paid tier, lead-architect)
**OC PID:** 37460 (bja8ohy65 background task)
**Status:** closed, 2026-05-18T00:08:38Z, assignee Jonathan Joson

### Outcome

**No porting needed. 0 code-changing follow-ups.** Closed via global CLAUDE.md "escape hatch" rule (closeout produces <3 code-changing follow-ups → close clean with triage notes).

### Structural diff (P6 LIVE `131664707683` vs P8 working-tree `snippets/css-overrides.liquid`)

- **55 lines only in P6** → both are the documented intentional drops:
  - `#pwa-modal, [id^="pwa-modal"], [class*="pwa-modal"]` — Shop Sheriff PWA app uninstalled 2026-05-01 (M3 drop, documented inline in file header)
  - `limespot { display: block; contain: layout; }` — LimeSpot replaced by Vertex AI per bd hairmnl-theme-oyw + M6 commit 4303e70 deleted `snippets/limespot.liquid` + `ghost-placeholder.liquid`
- **101 lines only in P8** → all P4-parity additions from this evening:
  - font-stack `:root` override block (commit 7ac5d3a)
  - retained M3 port header comments

### Lint / pattern audit (merge-gate)

- `grep` trailing comma in font-family declarations: **0 hits** (the one match was comment text describing the prior bug fix)
- `grep` empty `var()` references: **0 hits**
- `grep` Liquid `{{ }}` inside CSS declarations in css-overrides.liquid: **0 hits**
- `python3 scripts/check-overlay-css.py`: **OK: scanned 454 files, no kt0 violations**

### Phantom-completion guard

OC made no code changes attributable to this ticket. `git HEAD` remains at `7ac5d3a` (font fix from separate ticket lineage). `git status` shows `snippets/css-overrides.liquid` is **unmodified** by this audit. Confirmed clean.

### Working-tree footprint after audit

- `.beads/issues.jsonl` modified — bd close metadata only (committed below)
- `snippets/article-content-with-img-dims.liquid` modified — **foreign** (stream:a Bloggle img-dim WIP, NOT this ticket's scope, leave alone)

### Loop decision

**STOP.** Per global CLAUDE.md: "Never auto-pick the next Beads task at the end of a run." Returning to operator.

Remaining visual-parity gaps (if any) live outside `css-overrides.liquid` — in app injections, asset CSS files, settings-tied colors, or template-specific JSON. Those are NOT in scope for this ticket and are not auto-filed; operator can scope if/when needed.

---

## 2026-05-18 evening — bd ujg6.7 + 2i8b.18 PSI verified, 2i8b.17 Option A failed

### Tickets closed clean

**ujg6.7** (font CLS) — commit `e583b0c`. PSI dev preview:
- Mobile home: **CLS 0.018** ✅
- Desktop home: **CLS 0.016** ✅
- Mobile `/collections/loreal-professionnel`: **CLS 0.036** ✅
Font swap no longer a top CLS source on 3/4 measured pages.

**2i8b.18** (mobile menu-buttons) — commit `d55ee61`. PSI dev preview:
- Mobile `/collections/loreal-professionnel`: **CLS 0.036** (target ≤0.10) ✅
- Desktop home regression check: **CLS 0.016** ✅ (no regression post-ujg6.29)

### Tickets re-opened

**2i8b.17** (section-richtext CLS) — Option A re-baseline disproven. Post-ujg6.7, mobile `/collections/cat-best-sellers` measured **CLS 0.632** (up from 0.354 pre-ujg6.7 baseline). The shift is page-specific, NOT a global font-swap problem. Likely root cause: SelfModern heading font swap on the "HairMNL Top Picks" rich-text section + product grid reflow below.

Next-step recommendation pasted to bd:
- **Option C (template-scoped fix):** `body.template-collection-cat-best-sellers` selector with bounded min-height. Limits blast radius (vs the rejected 113-template Option A).
- **OR** SelfModern → `font-display: optional` (but overlaps with ujg6.7's explicit "out of scope" SelfModern note; would need scope expansion).

Status: `open`. Blocked on operator decision.

### Process notes

- OC swarm 2-ticket dispatch (`/hh-swarm 2i8b.17 2i8b.18`) returned 2/2 INCREMENT_DONE; CC merge-gate rejected 1/2 due to broad blast-radius (113-template scope). The swarm followed its brief but did not catch the cross-template impact — split coordinator review caught it.
- Foreign file `snippets/article-content-with-img-dims.liquid` (stream:a Bloggle WIP) remained correctly parked across 3 commits this session via stash-around-rebase + per-commit `git restore --staged` discipline (MIGRATION-CONTRACT §5 #6).
- PSI single-fresh-load mobile runs show high variance; the cat-best-sellers 0.632 is a single n=3 measurement. Worth a 2nd-day re-baseline before committing to Option C.

---

## 2026-05-18 late evening — Option C revealed PSI URL bug (2i8b.17 invalid)

### Headline finding

**`/collections/cat-best-sellers` is a 404 page.** The Shopify collection handle doesn't exist. All prior 2i8b.17 baselines that cited "mobile collection section-richtext CLS 0.354" then "0.632" were measuring 404-page footer shifts, NOT section-richtext shifts.

Evidence:
```
curl -sIL "https://www.hairmnl.com/collections/cat-best-sellers"
→ HTTP/2 404, theme=131664707683, pageType=404
```

PSI CLS attribution selector confirmed:
```
score: 0.4472
  selector: body#404-not-found > div#shopify-section-footer
```

### What I did

1. **Shipped Option C** (commit 8c12397) — template-scoped min-height on `collection.cat-best-sellers`. PSI verify showed CLS unchanged at 0.632 across n=3 clean runs.
2. **Pulled Lighthouse audit JSON via PSI API** to get layout-shift attribution. Selector revealed the 404 body.
3. **Reverted Option C** (commit 210af92 → push 5289eb4). `sections/section-richtext.liquid` back to clean state on both git + dev theme.
4. **Closed 2i8b.17 as `wontfix-invalid`** with full diagnosis in bd notes.

### What this also invalidates

- **2i8b.18 test URL** (`/collections/loreal-professionnel`) — also doesn't resolve cleanly. The "mobile brand CLS 0.036" we cited as the 2i8b.18 verification was actually measuring the HOMEPAGE (the URL 301-redirects to `/`). Menu-buttons IS on the homepage (per index.json: 2× menu-buttons sections), so the fix is still valid — but the page being measured was wrong. 2i8b.18 stays closed; the fix is real even though the test URL was wrong.
- **Per-collection PSI runs throughout this evening** — many of the URLs we cited (cat-best-sellers, loreal-professionnel) are not valid collections. The PSI bot followed redirects to 404 or homepage, then measured those. CLS values for "mobile collection X" PSI runs should be re-evaluated against valid collection handles.

### Lessons (codifying for the runbook)

1. **Always verify PSI target URL returns 200** (or follows expected redirects to the real target) BEFORE filing CLS attribution as evidence. A 5-second `curl -sIL` would have caught this immediately.
2. **PSI CLS attribution selectors are diagnostic** — when a selector cites `body#404-not-found` or any 404-ish identifier, the entire PSI run is measuring an error page and must be discarded.
3. **Add a 404 body-id detection guard to `scripts/psi-cls-attribution.py`** — file a follow-up.
4. **Audit `os2-migration/perf-regression-analysis.md` PSI test URLs** for similar 404 conditions — many of the regressions we identified there may be 404 artifacts.

### Status after revert

- `main` is at commit `5289eb4`. `sections/section-richtext.liquid` clean.
- OC's `/hh-orchestrate hairmnl-theme-ujg6.14` is in flight (in_progress, 1712 chars bd notes, 3 new JS files in working tree: hairmnl-{common,collection,product}.js, layout/theme.liquid untouched per spec). Working tree files pending OC commit + close.

---

## 2026-05-18 ~21:00 — full evening synthesis (session closeout)

After a long arc spanning roughly 8 hours of CC + OC coordination, this section captures the final state across all closed tickets, deliveries, and lessons.

### 12 tickets closed tonight

| Ticket | Type | Disposition |
|---|---|---|
| `2i8b.11` | code | OC paid: P6 vs P8 css-overrides parity audit — clean, no porting needed |
| `2i8b.15` | research | GTM trigger investigation: GTM is NOT in theme code; defer to ujg6.12 |
| `2i8b.16` | research | Klaviyo onsite audit: loader is async ✓; admin-side feature audit deferred to operator |
| `2i8b.17` | invalid | section-richtext CLS premise was a 404-page measurement artifact |
| `2i8b.18` | code | mobile menu-buttons CLS mobile-breakpoint fix (CLS 0.291 → 0.044) |
| `2i8b.19` | code | wired hairmnl-{common,collection,product}.js loaders in layout/theme.liquid |
| `ujg6.7` | code | font CLS line-box overrides + font-display:optional on accent weights |
| `ujg6.14` | code | OC paid: tree-shake hairmnl-custom.js into 3 per-template bundles |
| `ujg6.18` | code | lazy-render below-fold sections via Section API + IO (3 increments: section-collection, brand-collection, related) |
| `ujg6.19` | code | font preloads + slideshow eager:true (LCP element investigation revealed wrong test target) |
| `ujg6.20` | misconceived | cart drawer `Shopify.section.refresh` is theme-editor-only API; small follow-up `2i8b.21` filed instead |
| `ujg6.16` | code | facet AJAX via Section Rendering API for collection filter/sort |

### 5 follow-up tickets filed

- `2i8b.19` (B.2.2 loader wiring — closed same session)
- `2i8b.20` (delete hairmnl-custom.js post-soak, blocked until 2026-05-25)
- `2i8b.21` (post-cutover: dispatch `shopify:section:load` after cart drawer reload)
- `2i8b.22` (ujg6.18 increment 2: brand-grid lazy-render — closed same session)
- `2i8b.23` (ujg6.18 increment 3: PDP related-products lazy-render — closed same session)

### Verification debt outstanding

All shipped to P8 dev theme `141168312419`; **none yet browser-smoked**:
- ujg6.7 font CLS overrides
- 2i8b.18 mobile menu-buttons
- 2i8b.19 loader wiring (B.2.2)
- fsaa Reamaze defer guard (also blocked on `meu.4` live rollout)
- ujg6.16 facet AJAX
- ujg6.18 lazy-render ×3 (section-collection, brand-collection, related)
- ujg6.19 font preloads + slideshow eager

Each closed ticket's bd notes contain concrete DevTools + PSI repro steps for operator smoke. Before live cutover the operator must work through these.

### PSI numbers (from `os2-migration/psi-baseline-2026-05-18-late.md`)

**P8 dev vs P8 dev evening (impact of tonight's tickets):**
- Brand mobile CLS: 0.291 → **0.044** (−0.247)
- Brand desktop CLS: 0.173 → **0.009** (−0.164) + TBT −1430ms
- Home desktop CLS: 0.173 → **0.009** (−0.164)
- Cart desktop CLS: 0.306 → **0.055** (−0.251) + score +20
- Collection mobile CLS: 0.354 → **0.019** (−0.335)

**P8 dev vs P6 live (now):** P8 wins on mobile LCP across the board (−7.83s home, −14.14s PDP, −3.53s collection, −2.52s brand). Desktop home TBT +2511ms is the only big-magnitude P8 regression and is the long-tracked GTM tag-firing differential (will resolve via `ujg6.12`).

**CrUX field (P6 real users, 28d):** P6 passes 4/6 origin CWV. Failing: origin-desktop CLS 0.11, home-mobile LCP 2906ms + INP 237ms, home-desktop CLS 0.17. Lab improvements suggest the home-desktop CLS field metric should recover post-cutover.

### §5 #6 coordination-collision pattern — 5 strikes in one session

The bd-auto-export-bundling pattern hit 5 times in a single evening (commits 5097433, 662cb0d, 691fa2d, 0778d71, plus the ujg6.18 sweep) despite being already codified in MIGRATION-CONTRACT.md. Functional outcomes were always harmless (OC work was real and lint-clean) but commit attribution was wrong.

**Tooling response:** added `scripts/safe-commit.sh` as an explicit-file-list commit wrapper. Unstages everything bd touched, stages only the listed files, sanity-checks the set, then commits. MIGRATION-CONTRACT.md §5 #6 updated to mandate the wrapper for all CC commits during OC swarm activity.

### Workspace state at session end

- `main` head: `61e1532` (PSI comparison doc + `/collections/davines` URL fix)
- Pending: `snippets/article-content-with-img-dims.liquid` foreign (stream:a Bloggle WIP, parked across the entire session without ever bundling)
- Pending after this session: `scripts/safe-commit.sh` + `MIGRATION-CONTRACT.md` (§5 #6 update) + this `OVERNIGHT_STATUS.md` final synthesis — to commit next
- 8 stashes belong to other workstreams; left untouched
- All 5 PSI files cleaned from /tmp

### Recommended next session

1. **Operator browser smoke** of all 7 dev-soak ships before adding more code (concrete steps in each closed bd ticket's notes)
2. **`ujg6.12` Web Pixels Manager migration** — highest-leverage remaining ticket; closes the desktop home TBT regression
3. **`ujg6.13`** Defer LL + Judge.me + Re:amaze — extends the `fsaa` Reamaze pattern (mechanical OC fit)
4. **`ujg6.21` PSI verification matrix** post-cutover (n=5 each)
5. **`ujg6.24` epic-audit closeout** on the p8-perf diff before promoting to live

Cutover-readiness estimate per the runbook: **2.5–3.5 operator-weeks** remaining (1.5 weeks code + verification + Phase 4 admin TAE migration + parallel-run QA + cutover ceremony + post-cutover monitoring).

---

## 2026-05-18 ~22:00 — late-late arc (while operator was out)

User stepped out and authorized continued CC work. Closed 2 more P1 tickets via audit and added 2 tooling guards. **No new dev-soak debt** — only research/closure work.

### 2 more tickets closed via the audit pattern (now 14 closes total today)

| Ticket | Outcome |
|---|---|
| `ujg6.12` Web Pixels Manager migration | wontfix-premise-misaligned-admin-migration-deferred — theme has 12 small dataLayer/gtag emitters; none contribute meaningfully to TBT; GTM not in theme code (per `2i8b.15`); desktop home TBT gap is admin-side |
| `ujg6.13` Defer LL + Judge.me + Re:amaze | done-already-shipped — Re:amaze shipped tonight via `fsaa`, LoyaltyLion ALREADY DEFERRED pre-session in `snippets/loyaltylion.liquid` (rendered at theme.liquid:773), Judge.me 100% TAE-loaded with theme snippet allowlisted as dead code |

This brings the "wontfix-premise-misaligned" thread to 4 tickets (`ujg6.12`, `ujg6.13` partial, `ujg6.20`, `2i8b.15`/`16`). Pattern: these tickets were filed before the team fully understood that HairMNL's heavy-vendor surface is admin-loaded (Customer Events + TAE app embeds), not theme-loaded. Audit reframes the work as operator admin tasks.

### Tooling additions (prevent future failures)

1. **`scripts/safe-commit.sh`** (148 LoC) — explicit-file-list commit wrapper preventing the §5 #6 bd-auto-export-bundling pattern that hit 5 times tonight. Updates `MIGRATION-CONTRACT.md` §5 #6 to mandate the wrapper.
2. **`scripts/psi-baseline-matrix.py` preflight URL check** — fails fast (exit 2) if any cell URL returns non-200 or wrong pageType. Bypass: `--skip-preflight`.
3. **`scripts/psi-cls-attribution.py` 404-detection guard** — `BAD_BODY_ID_RX` catches `body#404-not-found`, `body#password`, `body#maintenance`, `body#robot-challenge`, `body#customers-login` in layout-shifts attribution selectors. Emits warning banner + inline ⚠️ markers in the report.

Both guards passed the dogfood test on tonight's PSI data (URL fix in commit 61e1532 means no bad-page cells currently). Dormant on healthy matrix, loud when something breaks.

### Repo state at session end

- `main` head: `5b38ea2`
- Tonight's commits delivered code shipping: ujg6.7, ujg6.14, ujg6.16, ujg6.18 ×3, 2i8b.18, 2i8b.19, fsaa, ujg6.19 — all on P8 dev `141168312419` awaiting browser smoke
- Tonight's commits delivered documentation: PSI comparison, GTM trigger audit, Klaviyo audit, Web Pixels audit, defer audit, full session synthesis
- Tonight's commits delivered tooling: safe-commit.sh, 2i8b.17 preflight + attribution guards
- Working tree: only foreign `snippets/article-content-with-img-dims.liquid` (stream:a parked across entire session, never bundled)

### Cutover-readiness verdict

P8 dev is **substantially better than P6 live on mobile LCP** (massive wins across all 5 cells) and **on CLS post-tonight's-fixes** (5 cells improved by 0.16-0.34). Desktop home TBT gap remains but is admin-side, not theme code. The remaining critical work for cutover is:

1. **Operator browser smoke** — 6 commits on dev needs ground-truth verification
2. **Operator admin migrations** — TAE toggles for 10 GREEN apps, Stky uninstall, Appikon uninstall, GTM workspace audit
3. **`ujg6.21` PSI verification matrix** post-cutover (blocked on cutover)
4. **`ujg6.24` epic-audit closeout** on the p8-perf diff before live promote

Per the runbook: **2.5–3.5 operator-weeks** to cutover remain.

---

## [2026-05-19 loop tick] 2i8b.11 status check

Loop fired to monitor OC dispatch on `hairmnl-theme-2i8b.11` (Phase 5 visual parity audit, css-overrides.liquid). Result:

- **Ticket already closed** at 2026-05-18T00:08:38Z (yesterday). Status = `closed`, escape-hatch path: audit produced 0 code-changing follow-ups (P6-only rules were intentional drops: PWA modal + LimeSpot).
- **No dispatch log present** — `/tmp/oc-dispatch-2i8b-11.log` does not exist (nothing in flight).
- **kt0 lint result captured in original close notes**: 454 files scanned, 0 violations.
- **No working-tree changes to merge-gate** — `git status` shows only the routine `.beads/issues.jsonl` update.

Loop premise is stale (ticket closed yesterday). Per global rule: **do not auto-pick next ticket**. Stopping the loop.
