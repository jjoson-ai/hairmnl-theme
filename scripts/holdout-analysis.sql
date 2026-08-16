-- Vertex rec incrementality holdout — analysis (bd cji.9)
--
-- Run against the seo-platform prod Postgres:
--   railway run --service Postgres bash -c 'psql "$DATABASE_PUBLIC_URL" -f scripts/holdout-analysis.sql'
--
-- Design: 50/50 deterministic split on the last hex char of visitor_id
-- (== the `_shopify_y` cookie). 0-7 = treatment (sees rails), 8-f = holdout.
-- Suppression lives in snippets/vertex-recommendations.liquid; this file
-- re-derives the same bucket from the visitor_id stamped on each event.
--
-- Only well-formed lowercase UUIDs participate. The pixel's
-- `anon-<random><Date.now()>` fallback id is regenerated per event, so those
-- rows are neither stably bucketed nor real distinct visitors (~18% of events).
--
-- POWER (measured pre-cutover: 8.37% PDP->ATC, ~2,956 PDP viewers/wk):
--   +20% relative lift detectable in ~3wk, +15% ~5wk, +10% ~12wk, +5% ~47wk.
-- So this test answers "do the rails do something MEANINGFUL", not "do they do
-- 3%". A null result bounds the effect below ~15%; it does not prove zero.

-- Window start = the day the holdout shipped. Override per run with
--   psql -v start_date=2026-08-12 -f scripts/holdout-analysis.sql
-- The guard matters: a bare `\set` here would SILENTLY override any -v passed
-- on the command line (psql executes \set when it reads the file), which is
-- exactly how a first run of this script reported a window nobody asked for.
\if :{?start_date}
\else
  \set start_date '2026-08-14'
\endif
\echo 'Holdout analysis — window starts:' :start_date
-- Default is 2026-08-14, NOT the 2026-08-11 deploy date: Shopify's page cache
-- kept serving pre-deploy HTML (no suppression, no instrumentation guard) for
-- ~2 days. Measured decay of unstamped impressions: Aug 12 = 19,527, Aug 13 =
-- 13,522, Aug 14 = 480, Aug 15+ = ~150/day. Aug 12-13 are contaminated and
-- must not be analysed as test data.

-- ── 0. Integrity gate — run FIRST, believe nothing until this passes ────────
-- (a) split_balance: must be ~50/50. Derived from PIXEL events ONLY. The first
--     version derived it from ALL events and reported 64/36 — an artifact, not
--     broken randomization: ad-blocked browsers block the sandboxed pixel but
--     run inline theme JS, so they appear ONLY via impressions, and only when
--     in treatment (holdout fires nothing). Rec events must never define the
--     population.
-- (b) holdout_contamination_pct: share of holdout PDP viewers who saw a rail
--     anyway. NOT "must be 0" — a ~6% residual is structural and known: a
--     first-time visitor has no _shopify_y when the inline bucket script runs,
--     defaults to treatment for that one page, then buckets correctly once the
--     cookie exists. Dilutes measured lift by ~x0.94. INVALID above ~10%:
--     that level means suppression is actually broken (or cache washout is
--     incomplete — check the unstamped-impression decay).
-- (c) bucket_mismatch: stamped bucket vs SQL re-bucket, on STAMPED rows only
--     (unstamped rows are pre-deploy cached pages, excluded by the window).
--     'treatment vs sql:holdout' rows are the (b) cookie race. Any OTHER
--     combination (holdout-stamped impressions at all, or holdout vs
--     sql:treatment) means the theme cookie and pixel clientId diverged —
--     that DOES invalidate the test.
WITH pixel_participants AS (
  SELECT DISTINCT visitor_id,
         CASE WHEN position(right(visitor_id, 1) in '01234567') > 0
              THEN 'treatment' ELSE 'holdout' END AS bucket
  FROM vertex_events
  WHERE occurred_at >= :'start_date'
    AND event_type IN ('detail-page-view', 'add-to-cart', 'purchase-complete',
                       'home-page-view', 'search', 'shopping-cart-page-view')
    AND visitor_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
)
SELECT 'split_balance (pixel visitors)' AS check, bucket AS detail, count(*)::text AS value
FROM pixel_participants GROUP BY bucket
UNION ALL
SELECT 'holdout_contamination_pct (warn >6, invalid >10)', 'pdp viewers w/ rail',
       round(100.0 * count(DISTINCT e.visitor_id) FILTER (
               WHERE e.event_type = 'vertex-rec-impression')
             / NULLIF(count(DISTINCT e.visitor_id) FILTER (
               WHERE e.event_type = 'detail-page-view'), 0), 1)::text
FROM vertex_events e JOIN pixel_participants p USING (visitor_id)
WHERE e.occurred_at >= :'start_date' AND p.bucket = 'holdout'
UNION ALL
SELECT 'bucket_mismatch (stamped rows; treatment-vs-holdout = cookie race)',
       (e.event_metadata->>'vx_bucket') || ' vs sql:' || p.bucket,
       count(*)::text
FROM vertex_events e JOIN pixel_participants p USING (visitor_id)
WHERE e.occurred_at >= :'start_date'
  AND e.event_type = 'vertex-rec-impression'
  AND e.event_metadata->>'vx_bucket' IS NOT NULL
  AND e.event_metadata->>'vx_bucket' <> p.bucket
GROUP BY 2;

-- ── 1. Primary metric: PDP -> add-to-cart rate, with a 95% CI on the lift ───
-- Denominator is PDP VIEWERS, not all visitors: the PDP rails can only
-- influence someone who reached a PDP, and the tighter population raises the
-- base rate (8.37% vs 2.64% sitewide conversion) and therefore the power.
WITH participants AS (
  SELECT DISTINCT visitor_id,
         CASE WHEN position(right(visitor_id, 1) in '01234567') > 0
              THEN 'treatment' ELSE 'holdout' END AS bucket
  FROM vertex_events
  WHERE occurred_at >= :'start_date'
    AND visitor_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
),
funnel AS (
  SELECT p.bucket, p.visitor_id,
         bool_or(e.event_type = 'detail-page-view')   AS saw_pdp,
         bool_or(e.event_type = 'add-to-cart')        AS did_atc,
         bool_or(e.event_type = 'purchase-complete')  AS did_buy
  FROM participants p JOIN vertex_events e USING (visitor_id)
  WHERE e.occurred_at >= :'start_date'
  GROUP BY p.bucket, p.visitor_id
),
agg AS (
  SELECT bucket,
         count(*) FILTER (WHERE saw_pdp)                        AS pdp_viewers,
         count(*) FILTER (WHERE saw_pdp AND did_atc)            AS atc,
         count(*) FILTER (WHERE saw_pdp AND did_buy)            AS buyers
  FROM funnel GROUP BY bucket
),
rates AS (
  SELECT bucket, pdp_viewers, atc, buyers,
         atc::numeric / NULLIF(pdp_viewers, 0)    AS p_atc,
         buyers::numeric / NULLIF(pdp_viewers, 0) AS p_buy
  FROM agg
)
SELECT bucket, pdp_viewers, atc,
       round(100 * p_atc, 2)  AS atc_rate_pct,
       buyers,
       round(100 * p_buy, 2)  AS conv_rate_pct,
       -- 95% CI half-width on this arm's ATC rate (normal approx)
       round(100 * 1.96 * sqrt(p_atc * (1 - p_atc) / NULLIF(pdp_viewers, 0)), 2) AS atc_ci95_pm
FROM rates ORDER BY bucket DESC;

-- ── 2. The verdict line: relative lift + whether the CI excludes zero ───────
WITH participants AS (
  SELECT DISTINCT visitor_id,
         CASE WHEN position(right(visitor_id, 1) in '01234567') > 0
              THEN 'treatment' ELSE 'holdout' END AS bucket
  FROM vertex_events
  WHERE occurred_at >= :'start_date'
    AND visitor_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
),
funnel AS (
  SELECT p.bucket, p.visitor_id,
         bool_or(e.event_type = 'detail-page-view') AS saw_pdp,
         bool_or(e.event_type = 'add-to-cart')      AS did_atc
  FROM participants p JOIN vertex_events e USING (visitor_id)
  WHERE e.occurred_at >= :'start_date'
  GROUP BY p.bucket, p.visitor_id
),
s AS (
  SELECT
    count(*) FILTER (WHERE saw_pdp AND bucket = 'treatment')            AS n_t,
    count(*) FILTER (WHERE saw_pdp AND did_atc AND bucket = 'treatment') AS x_t,
    count(*) FILTER (WHERE saw_pdp AND bucket = 'holdout')              AS n_c,
    count(*) FILTER (WHERE saw_pdp AND did_atc AND bucket = 'holdout')   AS x_c
  FROM funnel
),
calc AS (
  SELECT n_t, x_t, n_c, x_c,
         x_t::numeric / NULLIF(n_t, 0) AS pt,
         x_c::numeric / NULLIF(n_c, 0) AS pc
  FROM s
)
SELECT n_t AS treat_pdp_viewers, n_c AS hold_pdp_viewers,
       round(100 * pt, 2) AS treat_atc_pct,
       round(100 * pc, 2) AS hold_atc_pct,
       round(100 * (pt - pc) / NULLIF(pc, 0), 1) AS relative_lift_pct,
       round(100 * 1.96 * sqrt(pt * (1 - pt) / NULLIF(n_t, 0)
                             + pc * (1 - pc) / NULLIF(n_c, 0)), 2) AS abs_diff_ci95_pm,
       CASE WHEN abs(pt - pc) > 1.96 * sqrt(pt * (1 - pt) / NULLIF(n_t, 0)
                                          + pc * (1 - pc) / NULLIF(n_c, 0))
            THEN 'SIGNIFICANT at 95%'
            ELSE 'not significant — effect is smaller than this test can resolve'
       END AS verdict
FROM calc;

-- ── 3. AOV by bucket (secondary; n = orders only, so it is slow to converge) ─
WITH participants AS (
  SELECT DISTINCT visitor_id,
         CASE WHEN position(right(visitor_id, 1) in '01234567') > 0
              THEN 'treatment' ELSE 'holdout' END AS bucket
  FROM vertex_events
  WHERE occurred_at >= :'start_date'
    AND visitor_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
)
SELECT p.bucket, count(*) AS orders,
       round(sum(e.revenue))  AS revenue,
       round(avg(e.revenue))  AS aov,
       round(stddev_samp(e.revenue) * 1.96 / sqrt(count(*))) AS aov_ci95_pm
FROM vertex_events e JOIN participants p USING (visitor_id)
WHERE e.event_type = 'purchase-complete' AND e.occurred_at >= :'start_date'
GROUP BY p.bucket ORDER BY p.bucket DESC;
