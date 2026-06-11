#!/usr/bin/env python3
"""
AI-assistant referral attribution for HairMNL (GA4) — monthly check.

What it does: trends sessions / purchases / revenue from AI-assistant referrers
(ChatGPT, Gemini, Perplexity, Claude, Copilot) over a trailing 12-month window,
by month and by engine, with AI's share of all purchases.

Run: python3 scripts/ai-referrals.py        (uses ~/.config/hairmnl-ga4-key.json)

CAVEATS (read before interpreting):
  - This is a FLOOR. Many AI clicks arrive with no referrer (in-app / privacy)
    and land in Direct/Unassigned, so true AI influence is larger.
  - Monthly purchase counts are small (single digits) -> month-to-month is noisy;
    trust the quarter-over-quarter trend.
  - Baseline (12mo to 2026-05): 2,971 AI sess / 36 purch / PHP 97,520 = 0.25% of
    all purchases; ChatGPT = 85% sess / 97% purch. Compare new runs to this.
  - bd: hairmnl-theme (GEO AI-referral tracking).
"""
import os, datetime, csv
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', os.path.expanduser('~/.config/hairmnl-ga4-key.json'))
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (RunReportRequest, DateRange, Dimension, Metric, Filter, FilterExpression)

PROP = 'properties/248106289'
# rolling 12 month-buckets ENDING with the current (partial / month-to-date) month
today = datetime.date.today()
first_this = today.replace(day=1)
_y, _mo = first_this.year, first_this.month - 11
while _mo <= 0:
    _mo += 12
    _y -= 1
START = datetime.date(_y, _mo, 1).isoformat()
END = today.isoformat()
# AI-assistant referrer hosts. NOTE: 'you.com' deliberately excluded — it false-matched
# peekyou.com (a people-search site, not AI). Add engines here as they emerge.
AI_RE = r'(?i).*(chatgpt\.com|openai\.com|perplexity\.ai|claude\.ai|copilot|gemini\.google|bard\.google).*'
SF = Filter.StringFilter
c = BetaAnalyticsDataClient()

def engine(s):
    s = (s or '').lower()
    if 'chatgpt' in s or 'openai' in s: return 'ChatGPT'
    if 'perplexity' in s: return 'Perplexity'
    if 'claude' in s: return 'Claude'
    if 'copilot' in s: return 'Copilot'
    if 'gemini' in s or 'bard' in s: return 'Gemini'
    return 'Other-AI'

req = RunReportRequest(property=PROP, date_ranges=[DateRange(start_date=START, end_date=END)],
    dimensions=[Dimension(name='yearMonth'), Dimension(name='sessionSource')],
    metrics=[Metric(name='sessions'), Metric(name='ecommercePurchases'), Metric(name='purchaseRevenue')],
    dimension_filter=FilterExpression(filter=Filter(field_name='sessionSource',
        string_filter=SF(match_type=SF.MatchType.FULL_REGEXP, value=AI_RE))), limit=100000)
rows = [(x.dimension_values[0].value, x.dimension_values[1].value, engine(x.dimension_values[1].value),
         int(float(x.metric_values[0].value)), int(float(x.metric_values[1].value)), float(x.metric_values[2].value))
        for x in c.run_report(req).rows]

rt = c.run_report(RunReportRequest(property=PROP, date_ranges=[DateRange(start_date=START, end_date=END)],
    dimensions=[Dimension(name='yearMonth')], metrics=[Metric(name='ecommercePurchases')], limit=100000))
tot = {x.dimension_values[0].value: int(float(x.metric_values[0].value)) for x in rt.rows}

months = sorted({r[0] for r in rows})
print(f"AI-ASSISTANT REFERRALS -> HairMNL  ({START} .. {END})  [floor estimate]")
print(f"{'month':<9}{'sess':>7}{'purch':>7}{'rev(PHP)':>12}{'%all purch':>12}")
for ym in months:
    sub = [r for r in rows if r[0] == ym]
    s, p, rv = sum(r[3] for r in sub), sum(r[4] for r in sub), sum(r[5] for r in sub)
    share = 100 * p / tot.get(ym, 0) if tot.get(ym) else 0
    print(f"{ym[:4]}-{ym[4:]:<4}{s:>7}{p:>7}{rv:>12,.0f}{share:>11.2f}%")
tp = sum(r[4] for r in rows); trv = sum(r[5] for r in rows); ts = sum(r[3] for r in rows)
print(f"\n12-mo: sess={ts:,}  purch={tp}  rev=PHP {trv:,.0f}  ({100*tp/max(sum(tot.values()),1):.2f}% of all purch)")
eng = {}
for r in rows: eng.setdefault(r[2], [0,0,0.0]); eng[r[2]][0]+=r[3]; eng[r[2]][1]+=r[4]; eng[r[2]][2]+=r[5]
print("by engine:", "  ".join(f"{e}({v[1]}p/{v[0]}s)" for e,v in sorted(eng.items(), key=lambda x:-x[1][1])))
if len(months) >= 6:
    f3, l3 = months[:3], months[-3:]
    fp = sum(r[4] for r in rows if r[0] in f3); lp = sum(r[4] for r in rows if r[0] in l3)
    print(f"trend purch: first-3mo {fp} -> last-3mo {lp}  ({'+%d' % round(100*(lp-fp)/fp) if fp else 'n/a'}%)")

out = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'data', 'ai-referrals-monthly.csv')
with open(out, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['yearMonth','source','engine','sessions','purchases','revenue']); w.writerows(rows)
print(f"\nsaved: {os.path.normpath(out)}")


# bd uyq6.3 (2026-06-11): also emit a self-contained dashboard page from the same data.
_tr = ""
for ym in months:
    _sub = [r for r in rows if r[0] == ym]
    _s, _p, _rv = sum(r[3] for r in _sub), sum(r[4] for r in _sub), sum(r[5] for r in _sub)
    _share = 100 * _p / tot.get(ym, 0) if tot.get(ym) else 0
    _tr += (f"<tr><td style='padding:5px 8px'>{ym[:4]}-{ym[4:]}</td><td style='text-align:right'>{_s}</td>"
            f"<td style='text-align:right'>{_p}</td><td style='text-align:right'>{_rv:,.0f}</td>"
            f"<td style='text-align:right'>{_share:.2f}%</td></tr>")
_el = "".join(f"<li><b>{e}</b>: {v[1]} purchases / {v[0]:,} sessions / PHP {v[2]:,.0f}</li>"
              for e, v in sorted(eng.items(), key=lambda x: -x[1][1]))
_html = f"""<!doctype html><meta charset='utf-8'><title>HairMNL - AI referrals</title>
<body style='font-family:-apple-system,Segoe UI,sans-serif;max-width:760px;margin:32px auto;color:#1c1b18'>
<h1 style='font-size:22px'>AI-assistant referrals &rarr; HairMNL <span style='color:#6b6b6b;font-weight:400'>(floor estimate)</span></h1>
<p style='color:#6b6b6b'>Window: {START} &rarr; {END}. GA4 via scripts/ai-referrals.py (bd v33f, monthly). Many AI clicks arrive referrer-less and land in Direct &mdash; treat as a floor. 12-mo: {ts:,} sessions / {tp} purchases / PHP {trv:,.0f}.</p>
<table style='border-collapse:collapse;width:100%'>
<tr style='background:#6a7a5c;color:#faf6f0;text-align:left'><th style='padding:6px 8px'>month</th><th style='text-align:right'>sessions</th><th style='text-align:right'>purchases</th><th style='text-align:right'>revenue (PHP)</th><th style='text-align:right'>% all purch</th></tr>
{_tr}</table>
<h2 style='font-size:16px;margin-top:20px'>By engine (12 mo)</h2><ul>{_el}</ul>
<p style='color:#6b6b6b;font-size:12px'>Generated {END} &middot; csv: data/ai-referrals-monthly.csv &middot; bd uyq6.3</p></body>"""
_outh = os.path.join(os.path.dirname(__file__), "..", "dashboard", "ai-referrals.html")
with open(_outh, "w") as _f:
    _f.write(_html)
print("saved:", os.path.normpath(_outh))
