#!/usr/bin/env python3
"""ujg6.42.5 Phase 1 — verify-unused.

Walks the deployed `assets/theme-core.css` and `assets/custom-theme-core.css`
chunk files (Wave B+ emitter output), and for each rule determines whether
to KEEP or REMOVE it based on 4 cross-referenced sources of evidence:

  REMOVE_CANDIDATE  — no source provides evidence the rule is needed
  KEEP_EXTENDED     — extended Coverage (10 templates, deep interactions)
                      saw the rule's bytes used
  KEEP_HTML         — HTML class-presence detected the rule's classes in
                      rendered HTML across any of the 5 main templates
  KEEP_FORCED_CORE  — rule matches the forced-core override pattern list
                      from wave-b-emit.py (JS-lib, app-injection, modals,
                      state classes)
  KEEP_AMBIGUOUS    — heuristic flagged it as risky (focus/checked/print/
                      template-customers/sold-out/etc.)

Outputs:
  /tmp/ujg6.42/unused-verification.json  — full per-rule analysis
  docs/ujg6.42.5-unused-verification.md  — human summary

Usage:
  cd hairmnl-theme && python3 scripts/ujg6.42/verify-unused.py

Prerequisites:
  - Wave A+B chunks committed: assets/theme-core.css + custom-theme-core.css
  - Extended Coverage capture done: /tmp/ujg6.42/coverage-extended/*.json
    (matching the deployed chunk filenames)
  - HTML class-presence map: /tmp/ujg6.42/html-corrections/class-presence.json
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).parent.parent.parent

# Disk source chunks (deployed via Wave C)
CORE_FILES = {
    'theme-core.css': REPO / 'assets/theme-core.css',
    'custom-theme-core.css': REPO / 'assets/custom-theme-core.css',
}

EXTENDED_COVERAGE_DIR = Path('/tmp/ujg6.42/coverage-extended')
HTML_PRESENCE = Path('/tmp/ujg6.42/html-corrections/class-presence.json')

OUT_JSON = Path('/tmp/ujg6.42/unused-verification.json')
OUT_MD = REPO / 'docs/ujg6.42.5-unused-verification.md'

TEMPLATES_EXTENDED = [
    'home', 'collection', 'product', 'cart', 'search',
    'blog', 'article', 'page', 'notfound', 'collectionFiltered',
]


# ---------------------------------------------------------------------------
# CSS rule parser (same logic as bucket.py / wave-b-emit.py)
# ---------------------------------------------------------------------------

def find_rules(css: str):
    """Yield (full_sel, start, end) for each top-level rule including rules
    nested in @media."""
    rules = []
    i = 0
    n = len(css)
    media_stack = []

    while i < n:
        while i < n and css[i] in ' \t\n\r':
            i += 1
        if i >= n:
            break

        if css[i] == '}':
            if media_stack:
                media_stack.pop()
            i += 1
            continue

        if css.startswith('/*', i):
            j = css.find('*/', i + 2)
            if j == -1:
                break
            i = j + 2
            continue

        sel_start = i
        while i < n and css[i] not in '{;':
            if css.startswith('/*', i):
                j = css.find('*/', i + 2)
                if j == -1:
                    i = n
                    break
                i = j + 2
            else:
                i += 1

        if i >= n:
            break
        if css[i] == ';':
            i += 1
            continue

        sel_text = css[sel_start:i].strip()
        if not sel_text:
            i += 1
            continue

        i += 1  # consume '{'
        sel_lower = sel_text.lower()

        if sel_lower.startswith('@media'):
            media_stack.append(sel_text)
            continue

        if sel_lower.startswith(('@keyframes', '@-webkit-keyframes',
                                  '@font-face', '@supports',
                                  '@import', '@charset', '@page')):
            depth = 1
            while i < n and depth > 0:
                if css[i] == '{':
                    depth += 1
                elif css[i] == '}':
                    depth -= 1
                i += 1
            rule_end = i
            rules.append((f'<<at-rule>> {sel_text}', sel_start, rule_end))
            continue

        depth = 1
        while i < n and depth > 0:
            if css[i] == '{':
                depth += 1
            elif css[i] == '}':
                depth -= 1
                if depth == 0:
                    i += 1
                    break
            i += 1

        rule_end = i
        prefix = ' && '.join(media_stack)
        full_sel = (f'@@@ {prefix} @@@ ' if prefix else '') + sel_text
        rules.append((full_sel, sel_start, rule_end))

    return rules


# ---------------------------------------------------------------------------
# Coverage data loaders
# ---------------------------------------------------------------------------

def load_extended_used_ranges(file_label: str) -> list:
    """Return merged (start, end) byte ranges of CSS used across ALL
    extended-coverage templates for the given chunk file."""
    if not EXTENDED_COVERAGE_DIR.exists():
        return []
    all_ranges = []
    for t in TEMPLATES_EXTENDED:
        cov_path = EXTENDED_COVERAGE_DIR / f'{t}.json'
        if not cov_path.exists():
            continue
        data = json.loads(cov_path.read_text())
        entry = data.get(file_label)
        if not entry:
            continue
        for r in entry.get('ranges', []):
            all_ranges.append((r['start'], r['end']))
    all_ranges.sort()
    merged = []
    for s, e in all_ranges:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def range_overlaps(rs: int, re_: int, ranges: list) -> bool:
    for s, e in ranges:
        if e < rs:
            continue
        if s >= re_:
            return False
        return True
    return False


# ---------------------------------------------------------------------------
# Forced-core patterns (mirror wave-b-emit.py to avoid heavy import)
# ---------------------------------------------------------------------------

FORCE_CORE_PATTERNS = [
    r'\.swiper(?:-|\b)', r'\.flickity(?:-|\b)',
    r'\.aos(?:-|\b)', r'\[data-aos',
    r'\.lazy-image(?:\b|__)', r'\.lazyload(?:ed|ing)?\b',
    r'\.plyr(?:-|__|\b)',
    r'\.cart--hidden\b', r'\.cart__empty\b',
    r'\[data-cart-loading\]', r'\.cart__loading\b',
    r'\.freegifts(?:-|\b)', r'#freegifts',
    r'\.judgeme(?:-|\b)', r'\.jdgm(?:-|\b)', r'\.spr(?:-|_)',
    r'\.swym(?:-|\b)', r'\.appstle(?:-|\b)', r'\.limespot(?:-|\b)',
    r'\.ufe(?:-|\b)', r'\.bold-(?:upsell|product-options)\b',
    r'\.satcb(?:-|_)',
    r'\.modal(?:-|_|\b)', r'\.micromodal(?:-|\b)',
    r'\.drawer(?:-|__|\b)', r'\.popdown(?:-|__|\b)', r'\.popup(?:-|__|\b)',
    r'\.has-error\b', r'\.errors?\b',
    r'\.btn-state-(?:loading|complete)\b', r'\.is-loading\b',
    r'\.notice\b', r'\.alert\b',
    r'\.hero(?:-|__|\b)', r'\.section(?:-|__|\b)',
    r'\.banner-slider(?:-|\b)', r'\.banner-slide(?:-|\b)',
    r'\.shopify-section(?:-|\b)',
    r'(^|\s|,)\.wrapper(?:\s|,|:|\.|\[|\{|$)',
    r'\.main-content(?:\b|__)',
    r'\.js-grid\b', r'\.js-loaded\b', r'\.js-sticky',
    r'\.product-grid-item\b', r'\.product__grid',
]
FC_RE = [re.compile(p) for p in FORCE_CORE_PATTERNS]


def matches_forced_core(sel: str) -> bool:
    return any(p.search(sel) for p in FC_RE)


# ---------------------------------------------------------------------------
# Ambiguity heuristics — flag rules dormant by design but critical when fired
# ---------------------------------------------------------------------------

AMBIGUOUS_PATTERNS = [
    # CSS definitions referenced by other rules — REMOVING THESE BREAKS THINGS
    # even when Coverage doesn't show them in used ranges. Animation refs +
    # custom-property refs survive in the using rule's bytes, not in the
    # @keyframes / :root rule's bytes.
    r'^<<at-rule>>\s+@keyframes',
    r'^<<at-rule>>\s+@-webkit-keyframes',
    r'^<<at-rule>>\s+@font-face',
    r'^<<at-rule>>\s+@supports',
    r'^<<at-rule>>\s+@page',
    r'(?:^|\s|,):root(?:\s|$|,|\.)',
    r'(?:^|\s|,)html(?:\s|$|,|\.|:)',

    # Template-scoped (we didn't test every template)
    r'\.template-', r'body\.template-',
    r'\.template-customers', r'\.account', r'\.address', r'\.order',

    # Interactive pseudo-classes (Coverage's headless hover/focus is incomplete)
    r':hover\b',
    r':focus(?:-visible)?', r':checked', r':disabled', r':invalid',
    r':valid', r':required', r':placeholder-shown', r':target',
    r':active\b', r':visited\b',

    # Vendor pseudo-elements (scrollbar, spin buttons, search clear)
    r'::-(?:webkit|moz|ms)-',

    # Print + accessibility media queries
    r'@media\s+print',
    r'@media\s+screen\s+and\s+\(-ms-high-contrast',
    r'@media.*prefers-(?:reduced-motion|color-scheme|contrast)',

    # JS-disabled fallback
    r'\.no-js',

    # Inventory / state-driven product labels
    r'sold[-_]out', r'unavailable', r'\.pre-order',
    r'\.product-label(?:-|$|\s|,)', r'\.badge[-_]', r'\.label--',
    r'\.tag[-_]new', r'\.tag[-_]sale',

    # Cart count + status (depends on cart contents)
    r'\[data-header-cart-count', r'\[data-cart-count',
    r'\.cart__status', r'\.cart__icon--tags',
    r'\.cart__count\b', r'\.cart__bubble', r'\.cart__indicator',

    # Filter / sort active states (depend on user interaction we couldn't fully trigger)
    r'\.active__filters', r'\.filter--active', r'\.is-filtered',
    r'\.filter__chip', r'\.sort--active',

    # Tooltip / popout / dropdown states (hidden by default, JS-toggled).
    # BEM children (`__label`, `__title`) intentionally included via `__`.
    r'\.tooltip(?:\b|:|--|__|\s|,)', r'\.poppy(?:__|\b|--|\s|,)',
    r'\.popout(?:\b|:|--|__|\s|,)',
    r'\.dropdown(?:\b|:|--|__|\s|,)',

    # Variant inventory / countdown states (depend on stock + variant selection)
    r'\.variant__(?:countdown|inventory|stock)',

    # Accordion BEM children (modals/drawers cover top-level, this catches
    # nested blocks like `__block-title` that JS toggles on click)
    r'\.accordion__',

    # Share buttons (often hidden, revealed on hover/click)
    r'\.share(?:\b|:|--|__|\s|,|_link)',

    # Shopify-rendered template containers we didn't test
    r'\.shopify-policy', r'\.shopify-email-marketing',
    r'\.shopify-challenge', r'\.shopify-payment',
    r'\.gift-card', r'\.password-page',

    # Localization picker dropdowns (we didn't trigger)
    r'\.localization-form', r'\.disclosure-list',

    # Dark mode / palette switches (not currently enabled but defined)
    r'\.palette--dark', r'\.default--dark', r'\.dark-mode',
]
AMBIG_RE = [re.compile(p) for p in AMBIGUOUS_PATTERNS]


def is_ambiguous(sel: str) -> bool:
    return any(p.search(sel) for p in AMBIG_RE)


# ---------------------------------------------------------------------------
# HTML class presence cross-reference
# ---------------------------------------------------------------------------

CLASS_REF_RE = re.compile(r'\.([a-zA-Z_][a-zA-Z0-9_-]*)')
ID_REF_RE = re.compile(r'#([a-zA-Z_][a-zA-Z0-9_-]*)')


def html_classes_seen(sel: str, class_to_templates: dict) -> set:
    classes = set(CLASS_REF_RE.findall(sel))
    ids = set('#' + m for m in ID_REF_RE.findall(sel))
    seen = set()
    for c in classes:
        if c in class_to_templates:
            seen |= set(class_to_templates[c])
    for i in ids:
        if i in class_to_templates:
            seen |= set(class_to_templates[i])
    return seen


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    class_to_templates = {}
    if HTML_PRESENCE.exists():
        html_data = json.loads(HTML_PRESENCE.read_text())
        class_to_templates = html_data['class_to_templates']
        print(f'HTML classes/ids: {len(class_to_templates):,}', file=sys.stderr)

    all_results = {}

    for chunk_label, chunk_path in CORE_FILES.items():
        print(f'\n=== {chunk_label} ===', file=sys.stderr)
        if not chunk_path.exists():
            print(f'  SKIP: {chunk_path} not found', file=sys.stderr)
            continue

        css = chunk_path.read_text()
        rules = find_rules(css)
        print(f'  {len(rules):,} rules parsed from disk source '
              f'({len(css):,} bytes)', file=sys.stderr)

        ext_ranges = load_extended_used_ranges(chunk_label)
        ext_used_bytes = sum(e - s for s, e in ext_ranges)
        print(f'  extended coverage: {len(ext_ranges)} merged ranges, '
              f'{ext_used_bytes:,} used bytes ({ext_used_bytes/1024:.1f} KB)',
              file=sys.stderr)
        if not ext_ranges:
            print(f'  WARN: no extended coverage data for this chunk',
                  file=sys.stderr)

        verdicts = defaultdict(list)
        verdicts_bytes = defaultdict(int)

        for sel, start, end in rules:
            rule_bytes = end - start

            verdict = None
            evidence = {}

            # Check 1: extended coverage saw the rule's bytes used
            if ext_ranges and range_overlaps(start, end, ext_ranges):
                verdict = 'KEEP_EXTENDED'
                evidence['extended_used'] = True

            # Check 2: forced-core override matches
            if verdict is None and matches_forced_core(sel):
                verdict = 'KEEP_FORCED_CORE'
                evidence['forced_core_match'] = True

            # Check 3: HTML class presence
            if verdict is None:
                seen = html_classes_seen(sel, class_to_templates)
                if seen:
                    verdict = 'KEEP_HTML'
                    evidence['html_templates'] = sorted(seen)

            # Check 4: ambiguity heuristic
            if verdict is None and is_ambiguous(sel):
                verdict = 'KEEP_AMBIGUOUS'
                evidence['ambiguous_pattern'] = True

            if verdict is None:
                verdict = 'REMOVE_CANDIDATE'

            verdicts[verdict].append({
                'sel': sel,
                'bytes': rule_bytes,
                'start': start,
                'end': end,
                'evidence': evidence,
            })
            verdicts_bytes[verdict] += rule_bytes

        total = sum(verdicts_bytes.values())
        print(f'\n  {chunk_label} verdicts:', file=sys.stderr)
        for v in ['REMOVE_CANDIDATE', 'KEEP_EXTENDED', 'KEEP_HTML',
                  'KEEP_FORCED_CORE', 'KEEP_AMBIGUOUS']:
            n = len(verdicts[v])
            b = verdicts_bytes[v]
            pct = (b / total * 100) if total else 0
            print(f'    {v:18}: {n:5} rules  {b:7,} B '
                  f'({b/1024:6.1f} KB, {pct:5.1f}%)', file=sys.stderr)

        all_results[chunk_label] = {
            'verdicts': {k: list(v) for k, v in verdicts.items()},
            'bytes': dict(verdicts_bytes),
        }

    OUT_JSON.write_text(json.dumps(all_results, indent=2))
    print(f'\nJSON  -> {OUT_JSON}', file=sys.stderr)

    write_markdown(all_results)
    print(f'MD    -> {OUT_MD}', file=sys.stderr)

    return 0


def write_markdown(results: dict):
    lines = [
        '# ujg6.42.5 — Verify-and-remove unused CSS',
        '',
        'Date: 2026-05-20',
        '',
        '## Methodology',
        '',
        'Scan the deployed `assets/theme-core.css` and '
        '`assets/custom-theme-core.css` chunk files. For each rule, '
        'classify into one of 5 verdicts based on 4 evidence sources:',
        '',
        '1. **Extended Coverage** — re-run real Chrome CSS Coverage with '
        'deeper interactions (modal opens, hover-all-cards, accordion '
        'clicks, swatch selects, search-drawer-with-type) across **10 '
        'templates**: 5 original (home, collection, product, cart, '
        'search) + 5 new (blog, article, page, 404, collection-filtered).',
        '2. **HTML class presence** — class→templates map from rendered '
        'HTML of the 5 main templates.',
        '3. **Forced-core overrides** — selector patterns from `wave-b-emit'
        '.py` that always land in core (JS-lib bases, app-injection points, '
        'modal/drawer/popup state, form errors, hero/section/wrapper).',
        '4. **Ambiguity heuristics** — patterns that are dormant by design '
        'but critical when triggered: `:focus-visible`, `:checked`, '
        '`.template-customers-*`, `@media print`, `prefers-reduced-motion`, '
        '`sold-out`, etc.',
        '',
        '## Verdict legend',
        '',
        '| Verdict | Action |',
        '|---|---|',
        '| `REMOVE_CANDIDATE` | Safe to strip from chunk (no evidence of use) |',
        '| `KEEP_EXTENDED` | Extended Coverage saw bytes used |',
        '| `KEEP_HTML` | Classes appear in rendered HTML |',
        '| `KEEP_FORCED_CORE` | Always-core pattern match |',
        '| `KEEP_AMBIGUOUS` | Risky-to-remove heuristic match |',
        '',
        '## Per-file results',
        '',
    ]

    for chunk_label, data in results.items():
        verdicts = data['verdicts']
        bytes_by = data['bytes']
        total = sum(bytes_by.values())

        lines.append(f'### {chunk_label}')
        lines.append('')
        lines.append('| Verdict | Rules | Bytes | KB | % |')
        lines.append('|---|---:|---:|---:|---:|')
        for v in ['REMOVE_CANDIDATE', 'KEEP_EXTENDED', 'KEEP_HTML',
                  'KEEP_FORCED_CORE', 'KEEP_AMBIGUOUS']:
            n = len(verdicts.get(v, []))
            b = bytes_by.get(v, 0)
            pct = (b / total * 100) if total else 0
            lines.append(f'| `{v}` | {n} | {b:,} | {b/1024:.1f} | {pct:.1f}% |')
        lines.append('')

        # Sample selectors per verdict
        lines.append('#### Sample selectors per verdict')
        lines.append('')
        for v in ['REMOVE_CANDIDATE', 'KEEP_EXTENDED', 'KEEP_HTML',
                  'KEEP_FORCED_CORE', 'KEEP_AMBIGUOUS']:
            rules = verdicts.get(v, [])
            if not rules:
                continue
            top = sorted(rules, key=lambda r: -r['bytes'])[:15]
            lines.append(f'**`{v}` ({len(rules)} rules) — top 15 by bytes:**')
            lines.append('')
            lines.append('```')
            for r in top:
                sel_short = r['sel'][:120].replace('\n', ' ')
                lines.append(f'  [{r["bytes"]:>4}B] {sel_short}')
            lines.append('```')
            lines.append('')
        lines.append('---')
        lines.append('')

    # Aggregate savings
    lines.append('## Total potential savings')
    lines.append('')
    total_remove = 0
    for chunk_label, data in results.items():
        remove_b = data['bytes'].get('REMOVE_CANDIDATE', 0)
        total_remove += remove_b
        lines.append(f'- **{chunk_label}**: '
                     f'{remove_b:,} B '
                     f'({remove_b/1024:.1f} KB) safe to remove')
    lines.append(f'- **Total**: {total_remove:,} B '
                 f'({total_remove/1024:.1f} KB) safe to remove sitewide')
    lines.append('')
    lines.append('Sitewide because both `*-core.css` files load on every '
                 'pageview. Wave A originally projected ~225 KB of removable '
                 '`_unused` rules; the verification above is conservative '
                 'about which of those can be safely removed.')

    OUT_MD.write_text('\n'.join(lines))


if __name__ == '__main__':
    sys.exit(main())
