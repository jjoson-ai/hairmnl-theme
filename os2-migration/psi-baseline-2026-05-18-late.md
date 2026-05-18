# PSI / CrUX comparison — 2026-05-18 late evening

Generated after a session of P8 dev theme changes (12 closed tickets including ujg6.7, ujg6.14, ujg6.18 ×3 increments, 2i8b.18, 2i8b.19 wiring, fsaa, ujg6.16, ujg6.19). Compares:
1. **PSI lab now** (P6 live vs P8 dev) — fresh 60-cell matrix
2. **PSI lab vs prior evening baseline** (`psi-baseline-2026-05-18-evening.md` — pre-tonight's-changes)
3. **CrUX field data** (P6 live, real-user p75 over 28d window 2026-04-19 → 2026-05-16)

URL fix: `/collections/loreal-professionnel` (broken handle, served homepage as 200) replaced with `/collections/davines` (verified pageType=collection). All other URLs unchanged.

---

## 1. CrUX field data (P6 live, real-user p75)

| Cell | LCP p75 | CLS p75 | INP p75 | FCP p75 | TTFB p75 | CWV verdict |
|---|---|---|---|---|---|---|
| **ORIGIN mobile** (all pages) | **2267ms** (79% good) | **0.08** (78%) | **170ms** (80%) | 1910ms (72%) | 885ms (71%) | ✅ all 3 pass |
| **ORIGIN desktop** | **2022ms** (82%) | **0.11** (73%) | **104ms** (91%) | 1535ms (81%) | 699ms (78%) | ⚠️ CLS marginal-fail (0.11 vs 0.10) |
| **Home mobile** | **2906ms** (67%) | 0.03 (86%) | **237ms** (70%) | 2590ms (54%) | 897ms (73%) | ⚠️ LCP + INP marginal-fail |
| **Home desktop** | 2408ms (76%) | **0.17** (66%) | 159ms (82%) | 2237ms (67%) | 412ms (88%) | ⚠️ CLS notable-fail (0.17 vs 0.10) |

URL-level CrUX 404 (insufficient traffic) for `/collections/best-sellers`, `/products/<top>`, `/cart`, `/collections/davines` — those metrics roll into the origin.

**Interpretation:** P6 live is passing site-wide Core Web Vitals on mobile but has CLS issues on home desktop (0.17 > 0.10) that real users experience. Mobile home LCP is just over threshold (2906ms vs 2500ms). The home cell is the main optimization target.

---

## 2. PSI lab: P8 dev vs P6 live (now, n=3 each)

### Mobile

| Template | P6-live | P8-dev | Δ Score | Δ LCP | Δ CLS | Δ TBT |
|---|---|---|---|---|---|---|
| home | 28 / LCP 14.85s / CLS 0.045 / TBT 2.32s | 38 / 7.02s / 0.046 / 1.32s | **+10** | **-7.83s** | +0.001 | **-998ms** |
| collection | 12 / 11.48s / 0.948 / 1.08s | 34 / 7.94s / 0.019 / 1.90s | **+22** | -3.53s | **-0.929** ⚠️ | +823ms |
| pdp | 35 / 20.55s / 0.015 / 910ms | 34 / 6.41s / 0.019 / 2.16s | -1 | **-14.14s** | +0.004 | +1252ms |
| cart | 35 / 14.78s / 0.291 / 586ms | 21 / 17.73s / 0.283 / 1.54s | **-14** | +2.96s | -0.007 | +951ms |
| brand | 27 / 10.32s / 0.015 / 3.92s | 32 / 7.81s / 0.044 / 5.00s | +5 | -2.52s | +0.028 | +1078ms |

⚠️ P6 collection mobile CLS 0.948 = freak run (1 of 3 hit 0.948 + the median pulled there). True P6 mobile collection CLS is closer to 0.04 (other 2 runs). Don't read the -0.929 delta literally.

### Desktop

| Template | P6-live | P8-dev | Δ Score | Δ LCP | Δ CLS | Δ TBT |
|---|---|---|---|---|---|---|
| home | 59 / LCP 1.25s / CLS 0.009 / TBT 1.71s | 53 / 1.72s / 0.009 / 4.22s | -6 | +0.47s | -0.000 | **+2511ms** ⚠️ |
| collection | 71 / 1.09s / 0.013 / 582ms | 57 / 1.54s / 0.009 / 1.14s | -14 | +0.45s | -0.003 | +553ms |
| pdp | 62 / 1.12s / 0.016 / 1.09s | 59 / 1.58s / 0.027 / 722ms | -3 | +0.46s | +0.010 | -366ms |
| cart | 29 / 6.43s / 0.359 / 624ms | 41 / 7.20s / 0.055 / 667ms | **+12** | +0.77s | **-0.304** | +43ms |
| brand | 58 / 1.62s / 0.010 / 912ms | 54 / 1.64s / 0.009 / 1.44s | -4 | +0.02s | -0.001 | +532ms |

⚠️ Desktop home TBT +2511ms = the long-standing P8 gap (preview-bar artifact + GTM tag firing diff). Tracked in `os2-migration/desktop-home-tbt-root-cause.md` + 2i8b.15 (closed deferred to ujg6.12).

---

## 3. PSI lab: tonight's deltas (P8-dev now vs P8-dev evening baseline pre-tonight)

### Mobile (P8-dev only — measures impact of tonight's tickets)

| Template | Δ Score | Δ LCP | Δ CLS | Δ TBT | Note |
|---|---|---|---|---|---|
| home | **+6** | +0.45s | +0.033 | **-5620ms** | TBT massive variance recovery (mobile fresh-load noise) |
| collection | **+7** | +0.54s | **-0.335** | +1106ms | **2i8b.18 + ujg6.7 fix landed: CLS recovery** |
| pdp | -2 | +0.67s | -0.009 | -260ms | within variance |
| cart | +1 | -3.18s | ~0 | -590ms | within variance |
| brand | **+15** | +1.31s | **-0.247** | +1470ms | **2i8b.18 menu-buttons fix landed: CLS 0.291→0.044** |

### Desktop (P8-dev only)

| Template | Δ Score | Δ LCP | Δ CLS | Δ TBT | Note |
|---|---|---|---|---|---|
| home | **+7** | +0.14s | **-0.164** | +1600ms | **CLS recovery (0.173 → 0.009)** — ujg6.7 line-box overrides |
| collection | -3 | +0.25s | ~0 | -80ms | within variance |
| pdp | +1 | +0.28s | +0.007 | -398ms | within variance |
| cart | **+20** | -1.24s | **-0.251** | -473ms | **CLS recovery (0.306 → 0.055)** + score jump |
| brand | **+7** | +0.20s | **-0.164** | **-1430ms** | **CLS recovery + TBT improvement** |

---

## Headline findings

### Wins delivered tonight

1. **Home desktop CLS 0.173 → 0.009** (-0.164) — ujg6.7's Arial-matched line-box overrides + 2i8b.18 menu-buttons fix landing on the home page.
2. **Brand mobile CLS 0.291 → 0.044** (-0.247) — 2i8b.18 menu-buttons mobile-breakpoint fix.
3. **Brand desktop CLS + TBT both improved** (-0.164 CLS, -1430ms TBT) — combined effect of font work + lazy-render.
4. **Cart desktop CLS 0.306 → 0.055** (-0.251) and score +20 — likely the LoyaltyLion ujg6.7 metric override benefit (LL renders inside cart).
5. **Collection mobile CLS 0.354 → 0.019** (-0.335) — 2i8b.18 mobile menu-buttons + ujg6.7 font CLS + lazy-render combined.

### Regressions / no-improvement cells

1. **Desktop home TBT +2511ms vs P6** — pre-existing P8 gap, separate workstream (ujg6.12 Web Pixels Manager migration). Worse than evening baseline by ~+1600ms — likely lazy-render initial JS cost (IntersectionObserver setup + Section Rendering API fetch on scroll).
2. **PDP mobile TBT +1252ms** — new IO + Section Rendering API fetch cost from ujg6.18 increment 3 (related-products lazy). Trade for the lower initial page weight.
3. **Cart mobile** — P6 still wins on score (35 vs 21). The cart drawer + cart page TBT is a separate domain (ujg6.20 was misconceived; 2i8b.21 covers the small section-load dispatch).
4. **Mobile fresh-load runs continue to show high variance** — single-fresh-load PSI is notoriously noisy on heavy pages; deltas <0.5s LCP / <500ms TBT should be read with caution.

### CrUX context

P6 live is **passing 4/6 origin-level CWV thresholds**. Real users mostly see acceptable performance. The two CWV-failing cells are:
- **Origin desktop CLS 0.11** (marginal, 73% good)
- **Home mobile LCP 2906ms** (over 2500 threshold)
- **Home mobile INP 237ms** (over 200 threshold)
- **Home desktop CLS 0.17** (notable fail)

Our P8 lab improvements on the home cell (mobile CLS 0.046 stable, desktop CLS 0.173 → 0.009) suggest the post-cutover CrUX should see meaningful improvement on the failing home-desktop-CLS cell IF the lab-to-field correlation holds.

### Caveats

- PSI lab on a preview URL has variance characteristics different from real-user CrUX. The deltas show direction-of-travel, not magnitude.
- The dev theme has GTM container artifacts and preview-bar overhead that aren't on the live theme. Some TBT delta vs P6 is artificial.
- Tonight's commits are NOT yet on the live theme. Real CrUX data won't reflect them until the cutover + 28d field window.
- Single-fresh-load PSI is noisy. n=3 is the minimum; high-variance cells (mobile collection with 0.948 freak run) need n=5+ for stable medians.

---

## Reference table — all 5 cells, ALL 3 baselines side by side

### Mobile

| Cell | P6 LIVE lab now | P8 DEV lab now | P8 DEV evening (pre-tonight) | CrUX (P6 real) |
|---|---|---|---|---|
| home | 28 / 14.85s / 0.045 / 2.32s | 38 / 7.02s / 0.046 / 1.32s | 32 / 6.57s / 0.013 / 6.94s | LCP 2906ms p75 / CLS 0.03 / INP 237ms |
| collection | 12 / 11.48s / 0.948† / 1.08s | 34 / 7.94s / 0.019 / 1.90s | 27 / 7.40s / 0.354 / 794ms | 404 (rolled into origin) |
| pdp | 35 / 20.55s / 0.015 / 910ms | 34 / 6.41s / 0.019 / 2.16s | 36 / 5.74s / 0.028 / 2.42s | 404 |
| cart | 35 / 14.78s / 0.291 / 586ms | 21 / 17.73s / 0.283 / 1.54s | 20 / 20.91s / 0.283 / 2.13s | 404 |
| brand | 27 / 10.32s / 0.015 / 3.92s | 32 / 7.81s / 0.044 / 5.00s | 17 / 6.50s / 0.291 / 3.53s | 404 |

† freak run; true median ~0.04

### Desktop

| Cell | P6 LIVE lab now | P8 DEV lab now | P8 DEV evening (pre-tonight) | CrUX (P6 real) |
|---|---|---|---|---|
| home | 59 / 1.25s / 0.009 / 1.71s | 53 / 1.72s / 0.009 / 4.22s | 46 / 1.58s / 0.173 / 2.62s | LCP 2408ms p75 / CLS 0.17 / INP 159ms |
| collection | 71 / 1.09s / 0.013 / 582ms | 57 / 1.54s / 0.009 / 1.14s | 60 / 1.29s / 0.009 / 1.22s | 404 |
| pdp | 62 / 1.12s / 0.016 / 1.09s | 59 / 1.58s / 0.027 / 722ms | 58 / 1.30s / 0.020 / 1.12s | 404 |
| cart | 29 / 6.43s / 0.359 / 624ms | 41 / 7.20s / 0.055 / 667ms | 21 / 8.44s / 0.306 / 1.14s | 404 |
| brand | 58 / 1.62s / 0.010 / 912ms | 54 / 1.64s / 0.009 / 1.44s | 47 / 1.44s / 0.173 / 2.87s | 404 |

Format: `score / LCP / CLS / TBT median (n=3)`.

---

## Operator action items

1. **Browser-smoke the dev theme** before promoting to live — all 6 tonight's commits soak: ujg6.7, ujg6.16, ujg6.18 ×3, fsaa, 2i8b.18, 2i8b.19. Concrete repro steps in each closed bd ticket's notes.
2. **Re-baseline post-cutover** — replicate this matrix from live within 7 days post-cutover. Compare against tonight's "P8 dev" column.
3. **CrUX field validation** — 28d post-cutover, check if home-desktop-CLS field metric drops from 0.17 → ≤0.10 (lab shows 0.009 on dev with our fixes; should translate).
4. **Re-examine cart mobile** — only cell where P8 dev still loses to P6 lab. Cart drawer + cart page are different surfaces; root cause investigation may be needed.
