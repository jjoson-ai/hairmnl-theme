#!/usr/bin/env python3
"""Wave A bucketer using REAL Chrome CSS Coverage byte-range data.

For each CSS file:
  1. Walk the source file and identify each rule's byte span.
  2. Walk each template's used-byte ranges (from coverage/*.json).
  3. A rule is 'used' by a template if ANY byte of the rule falls in
     that template's used ranges.
  4. Bucket each rule by which templates use it:
       _universal       — all 5
       _unused          — 0
       <combo>          — non-empty subset (sorted, +-joined)
  5. Report bucket sizes + selectors.

Outputs:
  /tmp/ujg6.42/buckets-theme.json
  /tmp/ujg6.42/buckets-custom-theme.json
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

TEMPLATES = ['home', 'collection', 'product', 'cart', 'search']
CSS_FILES = [
    # (label-matching-coverage, path-on-disk-to-byte-aligned-source)
    ('theme.css', '/tmp/ujg6.42/cdn-theme.css'),
    ('custom-theme.css', '/tmp/ujg6.42/cdn-custom-theme.css'),
]
COV_DIR = Path('/tmp/ujg6.42/coverage')


def load_used_ranges(file_label):
    """Return {template: [(start, end), ...]} for the given CSS file."""
    out = {}
    for t in TEMPLATES:
        data = json.loads((COV_DIR / f'{t}.json').read_text())
        entry = data.get(file_label)
        if not entry:
            out[t] = []
            continue
        ranges = [(r['start'], r['end']) for r in entry['ranges']]
        ranges.sort()
        out[t] = ranges
    return out


def overlaps(a_start, a_end, ranges):
    """Does (a_start, a_end) overlap any range in `ranges` (sorted list)?"""
    # Binary search would be faster but linear works (a few hundred ranges).
    for s, e in ranges:
        if e < a_start:
            continue
        if s >= a_end:
            return False
        return True
    return False


def find_rules(css: str):
    """Yield (selector_text, start_byte, end_byte) for each top-level rule
    including rules inside @media. Skips @keyframes / @font-face wrappers
    (treating them as universal at-rules by yielding once).

    Note: byte positions are relative to the served file. The file Coverage
    measures is the served CSS — must match what we read from disk.
    """
    rules = []
    i = 0
    n = len(css)
    media_stack = []

    while i < n:
        # Skip whitespace
        while i < n and css[i] in ' \t\n\r':
            i += 1
        if i >= n:
            break

        if css[i] == '}':
            if media_stack:
                media_stack.pop()
            i += 1
            continue

        # Strip /* ... */ comments inline (don't yield as rules)
        if css.startswith('/*', i):
            j = css.find('*/', i + 2)
            if j == -1:
                break
            i = j + 2
            continue

        sel_start = i
        # Read until { or ;
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

        body_start = i  # at {
        i += 1

        if sel_text.lower().startswith('@media'):
            media_stack.append(sel_text)
            continue

        if sel_text.lower().startswith(('@keyframes', '@-webkit-keyframes',
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
            rules.append((f"<<at-rule>> {sel_text}", sel_start, rule_end))
            continue

        # Regular rule: read until matching }
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
        full_sel = (f"@@@ {prefix} @@@ " if prefix else "") + sel_text
        rules.append((full_sel, sel_start, rule_end))

    return rules


def main():
    for label, fname in CSS_FILES:
        css = Path(fname).read_text()
        rules = find_rules(css)
        used_by_template = load_used_ranges(label)

        # Verify file sizes match coverage's total
        cov_total = None
        for t in TEMPLATES:
            data = json.loads((COV_DIR / f'{t}.json').read_text())
            entry = data.get(label)
            if entry:
                cov_total = entry['total_bytes']
                break

        print(f'\n=== {fname} ===', file=sys.stderr)
        print(f'  source bytes:   {len(css):>8}', file=sys.stderr)
        print(f'  coverage total: {cov_total:>8}', file=sys.stderr)
        print(f'  rules found:    {len(rules):>8}', file=sys.stderr)
        if cov_total != len(css):
            print(f'  WARN: size mismatch — coverage byte indices may not align '
                  f'with source. Diff: {cov_total - len(css)}', file=sys.stderr)

        buckets = defaultdict(lambda: {'count': 0, 'bytes': 0,
                                       'rules': []})
        for sel, s, e in rules:
            usage = set()
            rule_bytes = e - s
            for t in TEMPLATES:
                if overlaps(s, e, used_by_template[t]):
                    usage.add(t)

            if not usage:
                key = '_unused'
            elif len(usage) == 5:
                key = '_universal'
            else:
                key = '+'.join(sorted(usage))

            b = buckets[key]
            b['count'] += 1
            b['bytes'] += rule_bytes
            if len(b['rules']) < 30:
                short = sel if len(sel) < 140 else sel[:137] + '...'
                b['rules'].append({'sel': short, 'bytes': rule_bytes,
                                   'start': s, 'end': e})

        for key in sorted(buckets):
            b = buckets[key]
            print(f'  {key:50} {b["count"]:>5} rules  '
                  f'{b["bytes"]//1024:>6} KB ({b["bytes"]:>7} B)',
                  file=sys.stderr)

        out = Path(f'/tmp/ujg6.42/buckets-{label.replace(".css", "")}.json')
        out.write_text(json.dumps(dict(buckets), indent=2))


if __name__ == '__main__':
    main()
