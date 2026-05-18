# P8 mobile cart score regression — investigation

**Question:** Why does P8 mobile cart score 21 vs P6's 35?
**Captured:** 2026-05-18 late
**Data sources:** `/tmp/psi-baseline/p[68]-*-mobile-cart-run*.json` (3 runs each)

## Headline

**P8 mobile cart's main-thread work is +3908ms (+75%) vs P6.** That extra main-thread time is what drags every metric:

| metric | P6 | P8 | Δ |
|---|---|---|---|
| score | 35 | **21** | **−14** |
| FCP | 2.19s | 2.52s | +324ms |
| LCP | 14.78s | **17.73s** | **+2958ms** |
| TBT | 586ms | **1537ms** | **+951ms** |
| CLS | 0.291 | 0.283 | −0.007 |
| SI | 8.66s | 14.60s | +5.94s |
| TTI | 31.67s | 34.19s | +2516ms |

Note: BOTH themes show 14-17s LCP and 30s+ TTI — this is PSI Slow-4G measurement on a heavy cart page. Real-user LCP is much faster (cart CrUX URL-level returns 404 = insufficient traffic for field data, so we can't confirm). The P8−P6 DELTA is the real concern, not the absolute numbers.

## Root cause: main-thread breakdown

| category | P6 | P8 | Δ | % of regression |
|---|---|---|---|---|
| **scriptEvaluation** | 2594ms | 4867ms | **+2273ms** | 58% |
| other | 824ms | 1449ms | +625ms | 16% |
| scriptParseCompile | 890ms | 1320ms | +430ms | 11% |
| styleLayout | 513ms | 851ms | +338ms | 9% |
| garbageCollection | 184ms | 344ms | +160ms | 4% |
| parseHTML | 70ms | 154ms | +84ms | 2% |
| paintCompositeRender | 103ms | 102ms | 0 | — |
| **TOTAL** | **5178ms** | **9086ms** | **+3908ms** | 100% |

The regression is **scriptEvaluation-dominated**. P8 is running 2.27 seconds more JavaScript than P6 on the same cart page.

## Where is the extra JavaScript coming from?

Top bootup-time contributors (P8 vs P6):

| Script | P6 ms | P8 ms | Δ | Status |
|---|---|---|---|---|
| **`shopify-perf-kit-3.3.1.min.js`** | 0 | **545ms** | **+545ms** | 🔒 STOCK P8 — cannot remove |
| **`vendor--61rXTEhfnWH.js`** (P8 stock vendor bundle) | 0 | **343ms** | **+343ms** | 🔒 STOCK P8 — cannot remove |
| GTM `gtm.js` | 240ms | 545ms | +305ms | ✅ recoverable (admin-side) |
| Judge.me `widget_base.js` | (not top 10) | 213ms | +213ms | ⚠️ partial (admin toggle) |
| Cart inline template JS | 695ms | 1028ms | +333ms | ⚠️ partial (P8 stock cart drawer init) |
| Other ~14 small scripts | varies | varies | +~500ms | mostly stock-P8 baseline drift |
| **Total accounted** | | | **~+2240ms** | matches +2273ms scriptEvaluation delta |

Network requests + transfer:
- P6: 378 requests, 5.5MB
- P8: 414 requests, 6.1MB
- **Δ +36 requests, +600KB** — driven by stock P8 bundles + 13 more scripts

## The 4 cost categories explained

### 🔒 Structural floor: `shopify-perf-kit` (545ms) + `vendor--*` (343ms) = **~888ms unavoidable**

These are stock Shopify P8 ships. We can't remove them:
- **`shopify-perf-kit-3.3.1.min.js`** — Shopify's framework providing Web Pixels Manager runtime, Customer Privacy API, bfcache hooks. Ironic that the perf kit itself costs ~545ms of main-thread time but it's what enables OS 2.0 features.
- **`vendor--*`** — Stock P8 vendor bundle (Flickity, MicroModal, Choices.js). Loads on every page including cart.

**Implication:** even with all recoverable optimizations done, P8 mobile cart will retain ~600-800ms TBT vs P6 baseline. Score will likely floor at ~25-28 (vs P6's 35).

### ✅ GTM container drift (+305ms) — admin-side recoverable

Per `2i8b.15` audit closed earlier tonight: GTM is loaded by Shopify Customer Events (admin-side sandboxed iframe), not theme code. The container has drifted since P6 baseline was captured (AW-877099019 was added then removed; other admin-side tag additions still resident).

**Recovery path: `ujg6.12` admin audit.** Operator audits Shopify admin → Settings → Customer Events → list active sources + GTM workspace tags. Remove redundant. Estimated recovery: 200-400ms.

### ⚠️ Judge.me widget_base.js (+213ms) — partially recoverable

Judge.me v3 widget bundle (TAE-loaded per `2i8b.16` finding). The base bundle loads on every page including cart, even though cart doesn't display reviews.

**Recovery path:** Judge.me admin → "Load on demand" / per-template enable. If admin offers per-template gating, exclude cart from the load. Or per-template `data-jdgm-*` opt-out at the theme level.

Estimated recovery: 100-200ms IF the admin toggle exists. Operator must verify in Judge.me dashboard.

### ⚠️ Cart inline JS (+333ms) — partially recoverable

P8's stock cart template emits more inline JS than P6: bulk-sections POST init, cart drawer event hooks, customer privacy bridges. Some of this is required for cart functionality (quantity update, remove); some is OS 2.0 infrastructure (Web Pixels publish surface).

**Recovery path:** limited theme-side options. Could potentially defer non-critical cart inline JS via requestIdleCallback wrapper. Risk: breaks cart UX if not careful. Estimated recovery: 100-200ms.

## What's NOT the cause

Common suspects ruled out:
- **CLS regression** — actually IMPROVED (0.291 → 0.283, marginal)
- **Image load** — same 19 images, 487KB transfer on both themes (no image change)
- **Font load** — only 79KB heavier on P8 (the BasisGrotesque/SelfModern preloads added in `ujg6.19`); negligible at 30-50ms
- **HTML parse** — only +84ms, smaller than the run-to-run variance
- **Network latency** — TTFB is roughly equal (P6 8ms, P8 43ms server response — both fast)

## Net recoverable estimate

| Cost | ms | Recoverable | Owner |
|---|---|---|---|
| `shopify-perf-kit` | 545 | 🔒 NO | structural |
| `vendor--*` | 343 | 🔒 NO | structural |
| GTM container drift | 305 | ✅ ~200-400ms | operator (admin) |
| Judge.me widget_base | 213 | ⚠️ ~100-200ms | operator (Judge.me admin) |
| Cart inline JS | 333 | ⚠️ ~100-200ms | theme (risky) |
| Other stock drift | ~530 | ⚠️ ~100-200ms | mixed |
| **Total recoverable** | | **~400-1000ms** | |

**Best case after recovery:** P8 mobile cart score ~28-32 (vs P6's 35, vs current 21). Still a slight regression but materially closer.

**Worst case (no admin work):** P8 mobile cart stays at score 21. Real customer impact debatable — cart page is post-engagement (users already committed to buy); CrUX 28d field measurement can't sample cart (insufficient traffic for URL-level data).

## Recommendation for cutover

**Don't block cutover on this.** Three reasons:

1. **The biggest cost is structural** (`shopify-perf-kit` + `vendor--*` = ~888ms STOCK P8). We can't remove them without breaking P8. Waiting won't change this floor.

2. **Cart traffic is post-conversion-decision.** Users arrive at cart with intent. The +3s LCP delta in lab matters less here than it does on home (where it's an SEO ranking + first-impression cost). Cart's score change matters more for OPERATOR PSI dashboards than for customer behavior.

3. **CrUX can't validate or refute.** Cart URL-level CrUX returns 404 (insufficient traffic). The only field-data validation is rolled into origin-level CrUX, which is dominated by home/PDP/collection traffic, not cart.

**Post-cutover work:**

- **Filed P2 follow-up:** investigate cart inline JS defer + Judge.me cart-page disable + GTM admin cleanup. ~1 operator-day + admin work. Realistic recovery: 400-1000ms.
- **Monitor RUM** (not CrUX since cart URL-level 404s): GA4 cart add-to-checkout completion rate week-over-week post-cutover. If conversion drops measurably, escalate. If not, accept the structural floor.

## Cross-references

- `2i8b.15` GTM trigger audit (closed wontfix-premise-misaligned, admin-side audit deferred to operator)
- `2i8b.16` Klaviyo onsite audit (closed — Klaviyo loader is async ✓; not a cart factor)
- `ujg6.12` Web Pixels Manager migration (closed wontfix-premise-misaligned — GTM not in theme)
- `ujg6.20` cart drawer `section.shopify.refresh` (closed wontfix-misconceived — API doesn't exist for storefront)
- `2i8b.21` post-cutover `shopify:section:load` dispatch (blocked on cutover) — small piece of the cart-drawer puzzle
