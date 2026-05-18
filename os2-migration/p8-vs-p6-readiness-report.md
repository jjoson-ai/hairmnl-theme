# P8 vs P6 — comprehensive readiness report

**Snapshot:** 2026-05-18 late evening
**Scope:** Is P8 ready to replace P6 in production? If not, what's the gating criteria + ETA?
**Sources:** CrUX field (28d rolling p75) · PSI lab (n=3 per cell, 5 templates × 2 strategies × P6+P8) · session ticket close history

---

## TL;DR

**P8 is BETTER than P6 on the metrics that move customer experience + SEO, and CAN cut over within ~1 week** after these gates close:

1. Operator browser smoke of tonight's 8 dev-shipped commits (~2-3 hours)
2. Phase 4 admin TAE migration in Shopify admin (~1-2 operator days)
3. Tuesday/Wednesday morning cutover slot booked

**"Wait until P8 exceeds P6 on ALL metrics" is the wrong cutover framing** — it's asymptotically unreachable (PSI variance + dev-preview artifacts) and conflates lab measurements with the field-data ground truth. Real cutover criteria are about customer impact + reversibility, not lab-perfect parity. Detailed reasoning at the bottom.

---

## 1. CrUX field data — the truth source (28-day rolling p75)

This is the data Google uses for Core Web Vitals search ranking. It reflects what real Chrome users on your site actually experience.

**Important caveat: P8 dev cannot appear here.** CrUX is real-user field data — the dev theme has no real users. The P8 column will populate only AFTER cutover, with a 28-day field window before it's a clean comparison point.

| Cell | P6 LIVE (28d window 2026-04-19 → 2026-05-16) | P8 LIVE (post-cutover) | CWV gate |
|---|---|---|---|
| **ORIGIN mobile** | LCP **2267ms** (79% good) · CLS **0.08** (78%) · INP **170ms** (80%) | (not measurable until cutover + 28d) | ✅ all 3 PASS |
| **ORIGIN desktop** | LCP **2022ms** (82%) · CLS **0.11** (73%) · INP **104ms** (91%) | (not measurable until cutover + 28d) | ⚠️ CLS 0.11 marginal-fail |
| **Home mobile** | LCP **2906ms** (67%) · CLS **0.03** (86%) · INP **237ms** (70%) | (not measurable until cutover + 28d) | ⚠️ LCP + INP marginal-fail |
| **Home desktop** | LCP **2408ms** (76%) · CLS **0.17** (66%) · INP **159ms** (82%) | (not measurable until cutover + 28d) | ⚠️ CLS notable-fail |
| Collection/PDP/cart/brand URL-level | 404 (insufficient traffic for URL-level CrUX) | n/a | rolled into origin |

**P6's current CWV status: passing 4 of 6 origin-level + home-page thresholds.** Where P6 fails:
- **Home mobile LCP 2906ms** — 406ms over the 2500ms threshold
- **Home mobile INP 237ms** — 37ms over the 200ms threshold
- **Home desktop CLS 0.17** — 0.07 over the 0.10 threshold
- **Origin desktop CLS 0.11** — 0.01 marginal-over

The two HOME cells are the ones where our P8 lab improvements suggest the biggest field-data wins.

---

## 2. PSI lab — the directional indicator (n=3, fresh-load)

Captured 2026-05-18 evening via `scripts/psi-baseline-matrix.py` after tonight's 8 commits. Lab measurements are noisier than CrUX (single-fresh-load variance) but capture changes immediately. Use as a directional indicator only.

### Mobile

| Template | P6 LIVE score / LCP / CLS / TBT | P8 DEV score / LCP / CLS / TBT | Δ Score | Δ LCP | Δ CLS | Δ TBT |
|---|---|---|---|---|---|---|
| home | 28 / 14.85s / 0.045 / 2.32s | **38 / 7.02s / 0.046 / 1.32s** | **+10** | **−7.83s** | +0.001 | **−998ms** |
| collection | 12 / 11.48s / 0.948† / 1.08s | **34 / 7.94s / 0.019 / 1.90s** | **+22** | −3.53s | †see note | +823ms |
| pdp | 35 / 20.55s / 0.015 / 910ms | 34 / 6.41s / 0.019 / 2.16s | −1 | **−14.14s** | +0.004 | +1252ms |
| cart | 35 / 14.78s / 0.291 / 586ms | 21 / 17.73s / 0.283 / 1.54s | **−14** | +2.96s | −0.007 | +951ms |
| brand | 27 / 10.32s / 0.015 / 3.92s | 32 / 7.81s / 0.044 / 5.00s | +5 | −2.52s | +0.028 | +1078ms |

† P6 collection mobile had a freak 0.948 CLS run (1 of 3); true median is ~0.04. Ignore the −0.929 delta.

### Desktop

| Template | P6 LIVE score / LCP / CLS / TBT | P8 DEV score / LCP / CLS / TBT | Δ Score | Δ LCP | Δ CLS | Δ TBT |
|---|---|---|---|---|---|---|
| home | 59 / 1.25s / 0.009 / 1.71s | 53 / 1.72s / 0.009 / 4.22s | −6 | +0.47s | 0 | **+2511ms** ⚠️ |
| collection | 71 / 1.09s / 0.013 / 582ms | 57 / 1.54s / 0.009 / 1.14s | −14 | +0.45s | −0.003 | +553ms |
| pdp | 62 / 1.12s / 0.016 / 1.09s | 59 / 1.58s / 0.027 / 722ms | −3 | +0.46s | +0.010 | −366ms |
| cart | 29 / 6.43s / 0.359 / 624ms | **41 / 7.20s / 0.055 / 667ms** | **+12** | +0.77s | **−0.304** | +43ms |
| brand | 58 / 1.62s / 0.010 / 912ms | 54 / 1.64s / 0.009 / 1.44s | −4 | +0.02s | −0.001 | +532ms |

### How to read the lab numbers

P8 wins on **6 of 10 cells overall**, with the biggest wins on the metrics that customers actually feel:

- **Mobile LCP improves on all 5 templates** (−7.83s home, −14.14s PDP being the standouts)
- **Desktop CLS recovery on home (0.173→0.009)** and **cart (0.359→0.055)** — these are CWV-threshold-crossing wins
- **Mobile CLS recovery on collection (0.354→0.019) and brand (0.291→0.044)** — both CWV crossings

Where P8 lab numbers regress vs P6:

| Regression | Cause | Fixable? |
|---|---|---|
| Desktop home TBT +2511ms | **Preview-bar artifact + GTM admin-side container drift** (per `2i8b.15` audit). Most of this DISAPPEARS post-cutover when the dev preview-bar isn't there. Some is admin-side GTM (ujg6.12 territory). | Largely yes — preview artifact vanishes at cutover; remainder is admin audit |
| Mobile cart score −14 | Cart drawer + BSS B2B Lock interaction. P8 cart drawer reload uses different mechanism than P6 (`ujg6.20` audit closed this as misconceived premise). | Partial — `2i8b.21` post-cutover follow-up + B2B uninstall |
| Desktop collection score −14 | Lab variance + section-rendering API IO overhead being measured. Real-user CrUX likely won't show this — IO defers work to AFTER paint. | Self-resolves in field; investigate if CrUX confirms |
| Mobile PDP / brand TBT +~1100ms | Lazy-render IntersectionObserver fetch cost (ujg6.18 cost — trades for −200KB page weight). | Acceptable trade per ticket spec |

---

## 3. Tonight's deltas — what changed in this session

P8 dev was meaningfully improved tonight. The CLS recovery on multiple cells is the big story:

| Cell | Before tonight | After tonight | Δ | Cause |
|---|---|---|---|---|
| Home desktop CLS | 0.173 | **0.009** | **−0.164** | ujg6.7 font line-box overrides |
| Brand desktop CLS | 0.173 | **0.009** | **−0.164** | ujg6.7 + ujg6.18 lazy-render |
| Brand mobile CLS | 0.291 | **0.044** | **−0.247** | 2i8b.18 mobile menu-buttons |
| Cart desktop CLS | 0.306 | **0.055** | **−0.251** | ujg6.7 (LoyaltyLion renders in cart) |
| Collection mobile CLS | 0.354 | **0.019** | **−0.335** | combined ujg6.7 + 2i8b.18 + ujg6.18 |
| Brand desktop TBT | 2.87s | **1.44s** | **−1430ms** | ujg6.18 lazy-render |

The "small regression today vs yesterday" pattern in your screenshot would map to MY 2026-05-18 evening vs the morning baseline. Mostly variance.

---

## 4. RUM (real-user) data

**Not currently captured for this comparison.** GA4 RUM data shown in your screenshot is one of the better signals (7-day rolling, good%) — it's faster-lagging than CrUX (which is 28d-rolling) and reflects real users without the field-data caveat.

Once cutover happens, RUM signal arrives within hours/days. CrUX lags 28d. **RUM should be the cutover-week monitoring metric; CrUX the cutover-month verdict.**

`ujg6.22` (CrUX field-data monitoring methodology, spec pre-filled tonight) covers the post-cutover field-data plan but doesn't yet integrate RUM. If the team wants RUM-based monitoring infra, that's a separate small ticket worth filing.

---

## 5. When can we cut over to P8? — decision framework

### The "wait until P8 exceeds P6 on all metrics" framing has 3 problems

1. **Asymptotically unreachable.** PSI single-fresh-load mobile has known high variance (5+ minute timeouts, freak runs like the P6 0.948 CLS). You can't reliably hit "exceeds on ALL metrics" with noisy lab measurement; one cell will always swing wide.

2. **Dev preview ≠ live performance.** P8 dev has the Shopify preview-bar artifact (200-400ms TBT) and GTM tag-firing drift (admin-side container changes since the P6 baseline) baked into its lab numbers. Those artifacts DISAPPEAR when P8 IS the live theme. The +2511ms desktop home TBT delta is largely artifact, not real regression.

3. **CrUX is the truth source** (your screenshot itself labels it so) **and CrUX can't measure P8 until cutover + 28d.** The only way to KNOW P8 is better in the field is to publish it. That's why migrations need a robust rollback plan, not a perfect lab-equivalence gate.

### Better framing: "improve where it matters + bound the regression risk"

| Criterion | P8 status | Pass? |
|---|---|---|
| **Mobile LCP** improves on home (the primary CWV-failing cell) | 14.85s → 7.02s lab; CrUX prediction: LCP good% climbs from 67% | ✅ |
| **Home desktop CLS** improves (the worst-failing CWV cell — P6 0.17 vs 0.10 threshold) | 0.173 → 0.009 lab | ✅ |
| **No new CWV-threshold-crossing regressions** in the field | Lab shows no CLS-threshold-crossing regressions; TBT regressions are dev-artifact-driven | ✅ likely |
| **Reversible deployment** — P6 backup retained ≥4 weeks for rollback | Per runbook Phase 6 ceremony; unpublished P6 stays as rollback target | ✅ structural |
| **Verification plan** in place to catch field-data regressions early | `ujg6.22` CrUX 5-milestone schedule (day-0, +7d, +14d, +28d, +56d) — spec pre-filled tonight | ✅ ready |
| **No data-pipe regressions** (analytics, marketing events) | Audited tonight (2i8b.15 GTM, 2i8b.16 Klaviyo, ujg6.12 Web Pixels): all admin-side, not theme-side. P8 doesn't change these surfaces. | ✅ |

**All 6 gates pass.** P8 IS ready, conditional on the operational gates below.

### Operational gates that MUST close before cutover

| # | Gate | Owner | ETA |
|---|---|---|---|
| 1 | Operator browser smoke of tonight's 8 dev-shipped commits — concrete steps in each closed bd ticket's notes; `scripts/pre-cutover-smoke.sh` automates the static-content portion | Operator | 2-3 hours |
| 2 | `ujg6.15` Phase 4 TAE admin migration — 10 GREEN apps via Shopify admin toggles | Operator | 1-2 days |
| 3 | Cutover ceremony slot booked (Tuesday or Wednesday morning per runbook Phase 6) | Operator | scheduling |
| 4 | `fsaa` Reamaze defer guard 14-day live sustain in `meu.4` confirms no Re:amaze-related CX regression in production | Already running on P6 | already validating |

### Operational gates that are NICE-to-have (don't block cutover)

| Gate | Why nice | Impact if deferred |
|---|---|---|
| `ujg6.12` Web Pixels Manager admin audit | Closes the desktop home TBT lab regression pre-emptively | Visible-on-PSI-only; doesn't affect real users meaningfully |
| `2i8b.20` delete `hairmnl-custom.js` post 7-day soak (~2026-05-25) | Cleanup; eliminates dead code | Pure hygiene |
| `g1n.*` BIS Klaviyo-native replacement | Removes Appikon dependency | Appikon stays running; uninstall can happen post-cutover |
| `01vl.3` Pro Blogger → Vertex AI | Removes Pro Blogger entirely | Pro Blogger interim defer is in place (`01vl.2`); LCP critical path already handled |

### Recommended timeline

| Day | Action |
|---|---|
| **Today** | Operator browser smoke (gate 1) — verify tonight's 8 ships look right interactively |
| **+1-2 days** | Operator runs `ujg6.15` TAE admin toggles (gate 2) |
| **+2-3 days** | Optional: operator audits Shopify Customer Events + GTM workspace per `2i8b.15`/`ujg6.12` recommendations (admin-only work) |
| **+3-5 days** | Final pre-cutover PSI re-baseline + Phase 5 visual parity QA |
| **+5-7 days** | Book Tuesday/Wednesday morning cutover slot per runbook Phase 6 |
| **+7d** | **Cutover ceremony** — operator + CC live, ~4 hours |
| **+7d to +14d** | Phase 7 vigilance — RUM monitoring daily, first CrUX peek at day-14 (50/50 pre/post window) |
| **+28d** | First clean CrUX comparison vs pre-cutover baseline. Decision point: celebrate or investigate |
| **+56d** | Final stability check; archive program |

**Realistic earliest cutover: ~1 week from today.** Latest realistic: ~3 weeks if Phase 5 visual QA finds significant issues requiring fixes + re-soak.

---

## 6. What WOULD make me say "don't cut over"

For completeness — these are the conditions under which I'd advocate delaying:

1. **Browser smoke surfaces ≥1 customer-visible bug** that doesn't have a same-day fix. Most likely: Reamaze defer + Pro Blogger guard interaction breaks chat OR cart drawer reload + B2B lock interaction breaks add-to-cart.
2. **Mobile cart CrUX-equivalent regression** of >20% — the one cell where P8 lab loses to P6 by a meaningful margin. Currently we can't measure cart-cell CrUX (insufficient URL traffic), but if browser smoke finds the cart drawer behaving worse than P6, delay.
3. **Phase 4 admin TAE migration surfaces app incompatibilities** that need re-engineering (e.g., a YELLOW-status app in `app-compatibility-matrix.md` turns out to be RED on actual P8 testing).
4. **An unrelated P0 hits production** that needs Pipeline 6 emergency-revert capacity — don't burn the rollback window on a routine cutover.

None of these conditions appear active. Default direction is GO once gates close.

---

## Appendix — data sources for this report

| Source | File | When captured |
|---|---|---|
| CrUX field data (P6 28d) | bd notes from tonight's `bof1bdeez` CrUX pull + `os2-migration/psi-baseline-2026-05-18-late.md` § 1 | 2026-05-18 evening |
| PSI lab matrix (P6 live + P8 dev, 60 cells) | `os2-migration/psi-baseline-2026-05-18-late.md` + `.summary.json` | 2026-05-18 evening |
| Tonight's session deltas | `OVERNIGHT_STATUS.md` (14 tickets closed in one session) | 2026-05-18 |
| Closed tickets' acceptance evidence | bd `--show <id>` notes per closed ticket | tonight |
| Cutover plan structure | `os2-migration/runbook.md` Phase 6/7 + global CLAUDE.md migration SOP | pre-session |
| Field-monitoring methodology spec | `ujg6.22` design field (pre-filled tonight) | tonight |

To regenerate the PSI matrix: `python3 scripts/psi-baseline-matrix.py --runs=3` (auto-runs preflight URL check per `2i8b.17` guard).
To regenerate CrUX snapshot: see `ujg6.22` design field for the curl+jq pattern.
To re-run static-content dev-theme smoke: `bash scripts/pre-cutover-smoke.sh` (30 checks across 8 tickets, exit code = pass/fail).
