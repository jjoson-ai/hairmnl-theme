# bba5 investigation outcome (2026-05-28)

## TL;DR

The original "+754ms perf-kit scripting regression" was a **PSI noise outlier**, not a
sustained architectural issue. Re-measuring with n=3 medians across two separate matrix
runs (2026-05-26 and 2026-05-28) shows perf-kit timing is essentially at parity between
P6 and P8 — and PSI's own run-to-run variance on the same theme exceeds the P6↔P8 delta
on most templates.

**Recommendation:** close as `won't-do` (or `resolved`). No P8 code change warranted.
A follow-up observation about preview-bar/theme-hot-reload dev-only artifacts is filed
below for awareness but is not actionable until cutover (they vanish automatically on publish).

## Evidence

### Mobile perf-kit total bootup (median of 3 runs per cell)

| Template   | 05-26 P6 / P8 / Δ  | 05-28 P6 / P8 / Δ  |
|------------|--------------------|---------------------|
| home       | n/a / n/a / n/a    | 147 / 259 / +111    |
| collection | 117 / 206 / +89    | 397 / 195 / **-202** |
| pdp        | 147 / 248 / +101   |  96 / 146 / +51     |
| cart       | 387 / 291 / -96    | 101 / 202 / +101    |
| brand      | 458 / 257 / -201   | 324 / 357 / +33     |

Same-theme variance between matrix runs is larger than the cross-theme delta on most
templates (e.g. P6 collection moved 117 → 397ms, +280ms within 2 days, far exceeding
the +101ms PDP cross-theme delta).

Net sum of all 5 mobile Δs on 2026-05-28: +94ms (P8 slightly slower).
Net sum on 2026-05-26: -107ms (P8 slightly faster).

The original ticket's measurement was based on a single n=1 lopf collection-mobile run
showing P8 perf-kit at 1408ms — which is **7× higher than today's median P8 measurement
on the same cell** (195ms). It was a slow outlier.

### `<head>` diff: P6 live vs P8 dev (same `/collections/best-sellers`, mobile UA)

After fixing the curl methodology (must use `creations-gdc.myshopify.com` domain with
cookie jar to actually get P8 content — see `/tmp/bba5/` for working scripts):

| Metric                          | P6     | P8     | Δ        |
|---------------------------------|--------|--------|----------|
| `<head>` size                   | 269004 | 280133 | **+11129** |
| `<link rel="preload">`          | 8      | 8      | 0        |
| `<link rel="preconnect">`       | 4      | 4      | 0        |
| `<link rel="dns-prefetch">`     | 13     | 13     | 0        |
| `<link rel="prefetch">`         | 0      | 0      | 0        |
| `<link rel="stylesheet">`       | 29     | 29     | 0        |
| inline `<script>`               | 49     | 50     | +1       |
| external `<script src=>`        | 16     | 18     | **+2**   |
| inline `<style>` bytes          | 103992 | 114143 | +10151   |
| speculation-rules scripts       | 0      | 0      | 0        |

**Identical instrumentation surface.** perf-kit's preload/preconnect/prefetch hint
counts are byte-for-byte equal between P6 and P8 — refuting the original hypothesis
that P8 has more navigation hints triggering perf-kit work.

### The 3 unique-to-P8 head artifacts are all preview-mode-only

```
+ <script src="/cdn/shopifycloud/theme-hot-reload/theme-hot-reload.js">       (14,849 B)
+ <script src="https://cdn.shopify.com/shopifycloud/preview-bar/preview-bar-modules.js">  (11,120 B)
+ <script id="OnlineStorePreviewBarNextData" type="application/json">{...}</script>  (511 B)
```

These exist on unpublished themes only and disappear automatically when the theme is
published. Today they cost **+266ms** total bootup on collection mobile, **+544ms** on
home mobile (per Lighthouse). On cutover this overhead vanishes, making production-P8
that much faster than current dev-theme measurements.

### Asset sizes — theme JS bundles are byte-identical between P6 and P8

| Asset              | P6 size | P8 size | Δ      |
|--------------------|---------|---------|--------|
| vendor.js          | 100,029 | 100,029 | 0      |
| jquery.min.js      |  85,659 |  85,659 | 0      |
| theme.js           | 162,827 | 162,827 | 0      |
| hairmnl-common.js  | (404)   |  12,489 | new    |
| hairmnl-collection.js | (404)  | 2,341  | new    |

The `hairmnl-common.js` + `hairmnl-collection.js` split bundles (ujg6.14, ~15KB
combined) are present only on P8 — that's a known intentional architectural change,
not a perf-kit-relevant addition.

## Follow-ups (for awareness, NOT bba5 scope)

1. **Preview-bar overhead measurement** — useful to know that the actual P8 cutover
   delta vs current PSI measurements is `~ +266 to +544ms bootup improvement on
   mobile` from dev-only-artifact removal. Mention this in the migration runbook so
   stakeholders aren't surprised by the production lift.
2. **Home mobile theme-asset bootup spike** — jquery.min.js shows 237ms on P6 vs
   2084ms on P8 on the May 28 matrix. BUT this is n=1 on P6 and n=2 on P8 (PSI
   500-failures elsewhere in the cell). Same binary file. Most likely sample-size
   noise. Worth a targeted n=5 rerun before opening a new ticket. Not a bba5 issue.

## Methodology notes

- Curl-based head diff: must use `creations-gdc.myshopify.com` (not `www.hairmnl.com`)
  with cookie jar for P8 preview. Simple `?preview_theme_id=...` on the apex domain
  302-redirects to live. Scripts saved in `/tmp/bba5/` for reproduction.
- PSI matrix data: `/tmp/psi-baseline/` (2026-05-28) and `/tmp/psi-baseline-2026-05-26/`.
- Median computation: per-cell median of total bootup across all successful runs.

## Acceptance criteria — disposition

| Original criterion | Status |
|---|---|
| Identify which P8-specific declarations trigger more perf-kit work | ✅ Done: none. Hints are identical. |
| Determine if any can be trimmed without functional loss | ✅ N/A. Nothing to trim. |
| Confirm investigation findings with PSI re-measurement | ✅ Done: regression doesn't reproduce with n=3 medians. |

No code changes made. Closing.
