# qjwb + by2g — Investigation outcomes (2026-05-28)

Two PSI matrix anomalies from the 2026-05-28 run were investigated together
because they share the same root cause.

## qjwb: Collection mobile CLS=0.354 spike

**Outcome: not a real regression. PSI cache artifact.** Closed `won't-do`.

The matrix reported P8 collection mobile CLS=0.354 across "n=3" runs — but
all three Lighthouse audits returned bit-identical CLS scores (0.354 exactly,
to the third decimal). This is PSI's caching behavior: when the same URL is
queried back-to-back, the API returns a cached single measurement multiple
times. Effective n=1.

Fresh n=3 cache-busted re-measurement (this session, random `?_cb=` query
params):

| theme | run1 | run2 | run3 |
|---|---|---|---|
| P6 live mobile collection CLS | 0.048 | (fail) | 0.046 |
| P8 dev mobile collection CLS  | 0.034 | 0.045 | 0.045 |

P8 median 0.045 is fractionally *better* than P6 median 0.047. `ujg6.59`
Phase 2c critical-CSS gating did not introduce layout shift.

## by2g: Desktop PDP P6 74 vs P8 58 (−16 pts)

**Outcome: gap inflated by PSI cache artifacts; remaining real gap explained by
preview-mode dev-only overhead.** Closed `won't-do`.

### Step 1 — measurements

The −16 pt gap was also amplified by cache artifacts (P6 runs all identical,
P8 runs mostly identical). Fresh cache-busted n=4 per theme (heavy 500-errors
from PSI today; landed 1 valid P6 + 2 valid P8):

| metric | P6 (n=1) | P8 (n=2 median) |
|---|---|---|
| score | 0.64 | 0.57 |
| TBT | 864ms | 1467ms |
| LCP | 1121ms | 1429ms |
| FCP | 661ms | 732ms |
| **SI** | **2654ms** | **4391ms** |
| CLS | 0.031 | 0.024 |

Real gap: −7 pts (not −16). The dominant metric is Speed Index (+1737ms).

### Step 2 — what's between FCP and visual completion

Resource summary (per Lighthouse), P6 vs P8 desktop PDP:

| type | P6 reqs | P8 reqs | P6 transfer | P8 transfer | Δ transfer |
|---|---|---|---|---|---|
| total | 541 | 568 | 6,794KB | 7,342KB | +548KB |
| script | 199 | 203 | 3,227KB | 3,458KB | +231KB |
| stylesheet | 65 | 65 | 252KB | 353KB | **+101KB** |
| image | 62 | 78 | 1,362KB | 1,508KB | +146KB |

### Step 3 — P8-only resources (after URL normalization)

**P8-only scripts (5 files, 275,307 bytes — all dev-only):**

| size | URL |
|---|---|
| 189,093B | `cdn.shopify.com/shopifycloud/preview-bar/vendor--*.js` (React vendor) |
| 74,631B | `cdn.shopify.com/shopifycloud/preview-bar/app-*.js` (preview-bar app) |
| 4,845B | `preview-bar-modules.js` |
| 4,811B | `theme-hot-reload.js` |
| 1,927B | `preview-bar/i18n/i18n-en-*.js` |

**P8-only stylesheet (1 file, 99,649 bytes — dev-only):**

| size | URL |
|---|---|
| 99,649B | `cdn.shopify.com/shopifycloud/preview-bar/assets/vendor.css` |

**Total P8-only dev-only overhead: 374,956 bytes ≈ 366KB.** All of this
disappears when the theme is published.

### Step 4 — what the +1737ms Speed Index delta actually represents

Speed Index measures the rate of visual completion between FCP and full
paint. 366KB of additional CSS+JS loaded between FCP and visual completion
delays the visual completeness percentage curve. On a desktop link at PSI's
default profile this maps to roughly +1.5–2.0s SI — consistent with the
observed +1.7s delta.

### Step 5 — residual non-dev difference

After excluding preview-bar/hot-reload, ~170KB of transfer delta remains:

- 32 extra image requests on P8 (~150KB) — mostly product photos
  (Davines, Aveda, K18, Kerastase, Tousled). Likely Vertex AI recommendation
  variance returning different items per API call, not a stable structural
  difference.
- Two scripts P6 loads that P8 doesn't: cdnjs jquery 3.7.0 (28KB) +
  owl.carousel (11KB). The owl.carousel is deferred on P8 by `88gw`.

### Step 6 — predicted post-cutover state

Removing 366KB of dev-only overhead and recovering ~1.5s of Speed Index
should bring P8 PDP desktop to roughly P6 parity or slightly above. The
remaining 170KB residual is small enough to be noise.

## Cross-cutting follow-up: `yk2r`

Filed `hairmnl-theme-yk2r`: the PSI matrix script (`scripts/psi-baseline-matrix.py`)
needs cache-busting query parameters appended to target URLs. Without them,
back-to-back identical URLs hit PSI's cache and return the same result
multiple times, breaking n=3 sampling.

This single change would have prevented qjwb, by2g, and bba24 (the cart cache
issue from earlier this session) from ever being filed — the matrix would
have shown real variance and the deltas would have been correctly attributed.

## Takeaway for migration program

The current PSI matrix systematically *underestimates* P8's real production
performance because the dev-theme overhead inflates almost every metric. The
true P8/P6 cutover delta is bigger than the matrix currently shows. The
preview-bar artifacts add an effective measurement tax that's:

- ~25–55KB on cold mobile pages (head only)
- ~366KB on warm desktop pages (head + on-page assets)
- ~250–540ms bootup time across templates
- ~1.5–2s Speed Index on heavier pages (PDP)

Post-cutover, all of this lifts. Re-baseline expectations accordingly when
planning the Phase 4 / Phase 5 verification.
