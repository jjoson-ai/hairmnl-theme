# Target theme research — Pipeline 8.1.1 vs Dawn vs custom/Hydrogen

> **Status:** Complete. No recommendation in this doc — that's P2.2 (`os2-migration/migration-decision.md`).
> Ticket: `hairmnl-theme-80z0.4` (P2.1).
> **Last updated:** 2026-05-17

---

## Why this doc

If a migration trigger fires (see `migration-triggers.md`), we need to know which target theme to port to. This doc evaluates the three candidates against the same criteria using data from P1.1 (app matrix), P1.2 (customization audit), and P1.3 (perf baseline). The recommendation lives in `migration-decision.md`.

## The three candidates

1. **Pipeline 8.1.1** — Groupthought's next-major version. Same vendor as our current theme (Pipeline 6.1.3). Free download for existing licensees per Groupthought policy (verified 2026-05-16).
2. **Dawn** — Shopify's first-party reference theme. Free, MIT-licensed. Sets the OS 2.0 baseline.
3. **Custom / Hydrogen** — Headless storefront in React + Remix on Shopify's Oxygen hosting. Hybrid options like Skeleton (Shopify's Hydrogen starter) included.

---

## Side-by-side evaluation

| Criterion | Pipeline 8.1.1 | Dawn | Custom / Hydrogen |
|---|---|---|---|
| **License cost** | $0 (free upgrade for licensees; was ~$320 originally) | $0 (MIT) | $0 software; Oxygen hosting free for Shopify merchants |
| **Vendor support posture** | Active, paid commercial support via Groupthought; minor releases every 6–8 weeks | Shopify-maintained, weekly upstream commits, official | Self-supported — we own everything; Shopify maintains the platform but not the storefront code |
| **Long-term EOL risk** | Pipeline 6 still maintained in year 5; Pipeline 8 expected ≥5-year horizon | Lowest — Shopify will not deprecate their own reference theme | Lowest framework risk; highest code-ownership risk (we maintain it) |
| **Performance — bare lab (mobile)** | Score 62, TBT 175ms, CLS 0.000, render-blocking 0 ([P1.3 measured](perf-baseline-comparison.md)) | Public Lighthouse: typically 75–85 mobile on a fresh install (Shopify's published numbers, not measured by us) | Higher ceiling possible (90+) but actual depends entirely on what we build |
| **Performance — with our apps (mobile, est.)** | ~3.31 MB → ~5.04 MB after legacy app re-install (-21% vs live 6.41 MB) | Comparable to Pipeline 8 — most overhead is third-party apps, theme-version-agnostic | Most controlled: can lazy-load app SDKs, skip server-rendered widgets, etc. — but only if we engineer it |
| **OS 2.0 v2 features (theme blocks, section groups, app blocks)** | All present (verified: `blocks/` dir, `group-header.json`, etc.) | All present (Shopify reference implementation) | All present, but you build the storefront from scratch |
| **Feature parity with current site** | Highest — Pipeline 8 ships almost everything Pipeline 6 has: brand-collection sections similar pattern, custom-content sections, hero variants, mosaic, etc. ~70% of section types map 1:1. | Medium — Dawn has structurally different sections. Our custom collection-branded sections (31 variants × ~1,740 LoC) don't have direct Dawn equivalents. | Lowest at start — we rebuild every UI element. Highest after build — exact match for our needs without theme-vendor compromises. |
| **Custom JS architecture fit** | Pipeline 8 still uses a single bundled `theme.js` (similar to Pipeline 6's pattern), making the 9,118-line `custom-theme.js` migration somewhat survivable as a port. | Dawn uses ES modules + section-scoped JS. The 9,118 LoC bundle must be **rewritten**, not ported. | Hydrogen is React + Remix. Total reimplementation. The custom-theme.js logic gets distributed across component lifecycle. |
| **CSS variable mapping** | Pipeline 8 uses similar `---` (triple-hyphen) variable convention; mapping mostly automatic | Dawn uses `--` (double-hyphen) and totally different settings schema; 435 LoC `css-variables.liquid` needs full re-write | N/A — CSS is part of component build, not a separate variable system |
| **App / TAE compatibility (from P1.1)** | All TAE-ready apps install identically; legacy snippet apps (Pro Blogger, MBC, etc.) still need TAE migration | Identical TAE compatibility — TAE blocks are theme-independent | TAEs do **not** apply to headless — apps that depend on theme-injected scripts (Klaviyo onsite form, Reamaze widget, Smart SEO, Searchanise widget) require separate SDK integration |
| **Estimated migration LoC effort** | **~10K LoC ported, ~6K dropped** (per P1.2). Most ports are mechanical due to Pipeline-family lineage. | **~14K LoC ported, ~6K dropped, ~3K rebuilt** (per P1.2 estimate, scaled up ~40% for DOM/selector/variable mismatches) | **~30K+ LoC rebuilt from scratch** — every section, snippet, behavior reimplemented as React components |
| **Estimated wall-clock to launch** | **3–5 weeks** (one operator + Claude, with the runbook from P2.3) | **6–10 weeks** | **3–6 months** (engineering project, not a porting project) |
| **Operational ongoing cost** | Same as today — single theme, Shopify admin edits, Liquid maintenance | Same as today — Liquid maintenance, slightly cleaner architecture | Higher — separate hosting environment, deploy pipeline, framework updates, React patches |
| **Operator familiarity** | Highest — Pipeline 6 idioms carry over, theme editor is familiar | Medium — same Liquid + theme editor, but different section structure | Lowest — React + Remix + Hydrogen + Oxygen + Storefront API; significant ramp-up |
| **Recovery from a bad cutover** | Easiest — flip back to Pipeline 6.1.3 via admin theme publish | Easiest — same admin flow as Pipeline 8 | Hardest — DNS/proxy reconfiguration to revert from headless to standard storefront |
| **Future-proofing** | Pipeline 8 will receive Groupthought updates; if Pipeline 9 ships, another small upgrade | Always current with Shopify's roadmap (theme blocks, AI section copy, etc. land on Dawn first) | Maximum — we adopt anything Shopify publishes plus arbitrary external tech |
| **SEO / SEO-tool risk** | Low — same URL structure, same content model | Low — same URL structure; needs careful redirect map verification | Higher — sitemap, canonical, structured data, and routing all become our problem |
| **Sticky / pinned-to-vendor cost** | Pipeline is paid theme; if Groupthought goes out of business, we'd need to re-platform anyway | None — Dawn is Shopify-maintained reference | Maximum — every component we wrote is on us forever |

---

## Cross-criterion observations

### What the perf data says (P1.3)

The architectural delta (TBT −93%, CLS to zero, render-blocking 0) is **a property of any OS 2.0 theme** — Pipeline 8, Dawn, or a custom build would all show similar wins because the underlying cause is the abandonment of jQuery + single-bundle JS + render-blocking CSS. So the "modern theme = faster" argument applies to all three candidates equally. **The choice between them is therefore not driven by performance.**

After re-installing the legacy apps (estimated +1.16 MB), all three candidates land at roughly the same total page weight (~5 MB). Hydrogen could go lower with engineering investment, but that investment is the cost.

### What the customization audit says (P1.2)

Our largest single porting cost is the **31 brand-collection sections** (~52,500 LoC total). They should be **consolidated into one parameterized section** regardless of target theme — that's a one-time win.

The second largest is **`custom-theme.js` (9,118 lines)**. Pipeline 8's preserved bundled-JS architecture makes this easier than Dawn's per-section modules, which would force decomposition.

CSS overrides (621 LoC, 18 blocks) and CSS variables (435 LoC) require porting under all three targets. Pipeline 8's variable convention is the closest match.

### What the app matrix says (P1.1)

- **TAE-ready apps (10)** install cleanly on any OS 2.0 theme. No differential between Pipeline 8 and Dawn.
- **Legacy snippet apps (10 RED)** need either vendor TAE adoption or manual port. Identical work regardless of target.
- **Headless complicates apps**: Klaviyo onsite, Smart SEO, Reamaze chat, Searchanise widget all depend on theme injection. Hydrogen forces each to be SDK-integrated separately — significantly more app-by-app work than Pipeline 8 or Dawn.

This **slightly favors Pipeline 8 / Dawn over Hydrogen** on the app-integration axis.

---

## Pros / cons summary

### Pipeline 8.1.1

| Pros | Cons |
|---|---|
| Lowest porting cost — same vendor, same idioms | Vendor lock-in to Groupthought |
| Free upgrade for licensees | Less "modern" than Dawn — Pipeline carries some legacy patterns |
| Theme blocks + section groups present | Custom-theme.js carries forward (could be seen as either a pro or technical debt) |
| Largest section-pattern overlap with current site | Pipeline 8 is opinionated about layout; some custom sections may need re-shaping |
| Most familiar to the operator | Periodic paid major upgrades (Pipeline 9, 10) eventually |
| ~3–5 week migration window | |

### Dawn

| Pros | Cons |
|---|---|
| Zero vendor lock-in | Larger porting cost — different DOM, different JS architecture |
| Always current with Shopify's roadmap | 31 brand-collection sections need redesign, not port |
| Cleanest OS 2.0 reference implementation | CSS variable system fully different — every variable re-maps |
| Best long-term EOL story | Custom-theme.js must be rewritten as ES modules |
| Free, MIT-licensed | ~6–10 week migration window |
| | Less section overlap → more design re-decisions |

### Custom / Hydrogen

| Pros | Cons |
|---|---|
| Highest performance ceiling | 3–6 month engineering project, not a port |
| Total UI control | Apps requiring theme injection need bespoke SDK integration |
| Future-proof against any Shopify theme changes | New ops burden: deploy pipeline, framework updates, React expertise |
| | Hardest to revert from |
| | Operator unfamiliarity with React/Remix/Hydrogen |
| | Migration adds significant cost without clear corresponding benefit at our scale |

---

## Open questions / NEED-VERIFY before P2.2

These should be resolved during the P2.2 decision, not in this research doc:

1. **NEED-VERIFY apps from P1.1** (10 rows): Searchanise, Personalizer.io, BookThatApp, VisualQuizBuilder, Pro Blogger, MBC Bundles, PluginSEO, Google Maps, Growave, STKY legacy. Their TAE availability changes the porting cost for Dawn more than Pipeline 8 (because Pipeline 8 can keep legacy snippets working with minor `{% render %}` syntax updates).
2. **Pipeline 8 demo measurements on cached preview** — once a Pipeline 8 install is publishable to a test domain, lab LCP can be properly measured (the current ~17.6s lab number is the preview cache-state artifact, see P1.3).
3. **Dawn performance on our store with our apps** — would require installing Dawn as a separate dev theme and running the same PSI methodology. Not in P1.3 scope; could be filed as a follow-up if P2.2 considers Dawn seriously.
4. **Groupthought roadmap for Pipeline 9** — if a major upgrade is expected within 12 months, that affects the porting-cost ROI calculation for Pipeline 8 vs Dawn.

---

## Inputs used

- `os2-migration/app-compatibility-matrix.md` (P1.1)
- `os2-migration/customization-audit.md` (P1.2)
- `os2-migration/perf-baseline-comparison.md` (P1.3)
- Pipeline 8.1.1 dev theme `141168312419` on creations-gdc.myshopify.com (installed, unpublished)
- Groupthought theme upgrade policy (verified 2026-05-16, free for existing licensees)
- Shopify Dawn public repo + published Lighthouse benchmarks
- Shopify Hydrogen + Oxygen public documentation
