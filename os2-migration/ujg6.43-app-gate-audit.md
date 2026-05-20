# ujg6.43 — App CSS template-gating audit

**Date:** 2026-05-20  **Status:** AUDIT COMPLETE — most candidates won't-do  **Author:** CC (Opus 4.7 / High)

## TL;DR

The ujg6.34 coverage audit identified 5 apps shipping ~260KB of CSS to templates that don't use it. This follow-up (ujg6.43) was meant to gate those apps to their actual-use templates from theme code.

**Audit finding: only 1 of the 5 (LDT Gift Wrap, ~37KB) is theme-code-gatable. The other 4 cannot be gated from theme code, or fail the HairMNL UX-availability rule, or are already being eliminated by a parallel epic.**

Net achievable savings from this ticket: **~37KB** (one app, cart-only), not the headline -260KB.

## Methodology

1. Searched `/tmp/p8-investigate/layout/theme.liquid` (P8 out-of-tree) + working-tree `layout/theme.liquid` for direct `<link>`/`<script>` tags referencing each candidate app's CDN.
2. Searched all `.liquid` files for `{% render %}` / `{% include %}` of each app's snippet.
3. Walked `config/settings_data.json` for TAE app embed blocks (`shopify://apps/...`).
4. For each candidate, traced **how the CSS bundle is actually loaded** and **what would happen if gated**.

## Per-app verdict

### (a) Searchanise — `results_modern.css` + `results_mobile.css` + `recommendation.css` (~153 KB unused)

- **Load mechanism:** `<script src="//www.searchanise.com/widgets/shopify/init.js" defer>` in `layout/theme.liquid:200`. CSS is loaded by init.js after parse — **not render-blocking**.
- **Template usage:** the `init.js` powers the predictive-search dropdown in the site header, which appears on **every template**. Also powers the `/search` results page.
- **Gating proposal in coverage audit:** "Gate to `template == 'search'`."
- **Verdict: WON'T-DO.** Gating to /search alone breaks the header search dropdown sitewide. Per the HairMNL UX-availability rule (codified 2026-05-20 with ujg6.50 / .51 closure), customer-facing search UI must remain available on every template.
- **Note on impact:** CSS is loaded post-parse via defer'd JS, so it's NOT in the critical path. The 153KB "wasted" figure is real (Coverage API shows 100% unused on non-/search templates) but it has **near-zero perf impact** because the load is async and happens post-LCP. The Coverage report overstates the user-visible cost for this app.

### (b) Judge.me — `widget_v3` CSS (~47 KB unused on non-PDP)

- **Load mechanism:** loaded by TAE app embed block at `config/settings_data.json` → `shopify://apps/judge-me-reviews/blocks/judgeme_core/...` (block `14060646107696862457`). Legacy `snippets/judgeme_core.liquid` in working tree is **orphaned** (no callsite anywhere).
- **Template usage:** PDP review widget, collection-card star ratings, cart drawer star ratings, possibly homepage best-sellers badges.
- **Gating proposal in coverage audit:** "Gate via `template contains 'product'`."
- **Verdict: WON'T-DO.** Gating to PDP-only loses collection star ratings, cart drawer star ratings, and any badge shown on non-product templates. Star ratings are a meaningful conversion signal across the site. Operator-decision territory if we want to fight for this one; default is keep-as-is.
- **If operator later approves:** the gating path is `enabled_on` field on the TAE embed block in `settings_data.json`. Requires app manifest support — needs verification per Judge.me TAE schema.

### (c) BOGOS — freegifts CSS (~51 KB unused)

- **Load mechanism:** TAE app embed block `shopify://apps/free-gifts-bogo-buy-x-get-y/blocks/app-embed/...` (block `8605505498557855500`).
- **Existing mitigations:**
  - `tyio.2` / `knz5`: rIC defer guard on `/cart` (stashes BOGOS scripts until requestIdleCallback fires).
  - `ujg6.49`: gated `freegifts-snippet-change` snippet render to product context (P8 `theme.liquid:1523-1530`).
- **Template usage:** "templates with active gift campaigns" — this is **dynamic state**, not template-name-derivable in Liquid. A gift campaign can target a specific product, a specific collection, or sitewide. Liquid `{% if template ... %}` cannot express "this template has an active campaign right now."
- **Gating proposal in coverage audit:** "Gate to templates with active gifts."
- **Verdict: WON'T-DO.** Not statically gatable. The two existing mitigations (`tyio.2` + `ujg6.49`) already cover the realistic surface area. Further reduction requires migrating off BOGOS entirely (tracked separately as `ur0`, P4).

### (d) LDT Gift Wrap — `shopify-giftwrap` CSS (~37 KB unused)

- **Load mechanism:** TAE app embed block `shopify://apps/ldt-gift-wrap/blocks/embed/...` (block `8908507833471942310`).
- **Template usage:** by design, gift-wrap UI appears only on `/cart`. No legitimate use on PDP, collection, or homepage.
- **Gating proposal in coverage audit:** "Gate to `template == 'cart'`."
- **Verdict: DOABLE — but with caveats.**
  - Mechanism: set `enabled_on: { templates: ["cart"] }` on the TAE block in `config/settings_data.json`.
  - Risk 1: the LDT app's TAE manifest must support `enabled_on`; if it doesn't, the field is ignored.
  - Risk 2: the theme editor will overwrite `settings_data.json` if the operator re-saves theme settings — change needs to be re-applied or made via theme-editor UI ("App embeds" panel with template restriction toggle, if LDT supports it).
  - Risk 3: gift-wrap CTA might show in cart drawer (overlay on every page) — verify the LDT block doesn't also inject into the drawer.
- **Recommendation:** **DEFER to operator action.** Filed as an admin-side follow-up (see "Operator follow-up" section below). Editing `settings_data.json` from CC is fragile; operator should use the theme editor's app-embed template-restriction UI if available.

### (e) Smart Add to Cart Button (satcb) — `satcb.min.js` + CSS (~76 KB unused)

- **Load mechanism:** dual injection:
  - Hardcoded `<script>` in `layout/theme.liquid:1486` (`satcb.min.js`, async + defer).
  - TAE app embed block `shopify://apps/stky-sticky-add-to-cart/blocks/satcb/...` (block `12643349056429947648`).
- **Critical context:** The TAE block is the **STKY Sticky Add-to-Cart** app — the very app being replaced by our custom sticky bar in epic `a7av` (a7av.8 already shipped: layout-level sticky bar render gated to collection templates).
- **Verdict: SUPERSEDED.** No new work in ujg6.43 — the work belongs to `a7av.7` (Stky cutover: disable embed, delete stale script, uninstall app). When a7av.7 lands, both the hardcoded script in theme.liquid AND the TAE block disappear, taking the full 76KB with them.
- **Cross-link:** added cross-reference in `a7av.7` notes confirming this audit's finding.

## Summary table

| App | Coverage audit -KB | Actual gatable from theme code? | Disposition |
|---|---|---|---|
| (a) Searchanise | 153 | No — header search needs it sitewide; non-blocking anyway | **Won't-do** (UX-availability + low real impact) |
| (b) Judge.me | 47 | Maybe via TAE `enabled_on` — but star ratings appear on multiple templates | **Won't-do** (UX-availability default; reopen if operator approves) |
| (c) BOGOS | 51 | No — gating predicate is dynamic state, not template name | **Won't-do** (already mitigated by tyio.2 + ujg6.49) |
| (d) LDT Gift Wrap | 37 | Yes via TAE `enabled_on: ["cart"]` if app manifest supports it | **Deferred to operator** (theme-editor admin path safer than hand-editing settings_data.json) |
| (e) satcb / Smart ATC | 76 | N/A — being eliminated by a7av.7 | **Superseded** by a7av.7 |
| **TOTAL gatable from theme code** | — | **~37 KB** (LDT only, contingent on app manifest support + operator action) | — |

## Why the headline -260KB was overstated

The ujg6.34 Coverage audit measured CSS bytes downloaded vs. CSS rules used on the rendered page. That correctly identifies waste, but it conflates several distinct problems:

1. **Render-blocking waste** (true perf cost): CSS in the critical path that blocks LCP.
2. **Post-paint waste** (low perf cost): CSS loaded async after LCP, costs bandwidth but not paint time.
3. **State-dependent loading** (un-gatable): CSS whose load-decision depends on dynamic state (active campaigns, logged-in customer) — can't be predicted at template render time.
4. **App-controlled loading** (un-gatable from theme): CSS loaded by the app's TAE block, where the gating mechanism lives in the app's manifest, not theme code.

The -260KB headline summed all four categories. Only category (1) translates to a real perf win, and most of these apps fall into category (2)–(4).

## Operator follow-up (filed)

- **ujg6.43-fu** (new ticket): Operator action — investigate LDT Gift Wrap template gating in Shopify admin. Open the theme editor's "App embeds" section, find LDT Gift Wrap embed, look for "load on specific templates" or equivalent toggle. If present, restrict to `cart`. ~10 minutes.

## Process lesson

Coverage-audit-driven savings claims need a per-app "is this even reachable from theme code?" pre-flight before they become engineering tickets. The -260KB number was real bytes-on-the-wire but wasn't actionable from theme code. The pre-flight prevented ~6 hours of low-leverage Liquid-wrapping work and identified one real follow-up (LDT) that's correctly an operator-side admin task.

This is the same lesson as the FOUC investigation pre-flight (Mitigation A): always trace the load mechanism back to its source before proposing a gate.
