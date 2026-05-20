#!/usr/bin/env python3
"""Wave B — CSS split emitter (ujg6.42.2).

Reads docs/ujg6.42-buckets.json (the Wave A real-Coverage output) and the
disk source CSS files (assets/theme.css, assets/custom-theme.css).

For each rule in each CSS file, looks up the selector's bucket via
normalized selector matching and routes the rule's DISK source text to the
appropriate output file(s):

    _universal | _unused  ->  assets/theme-core.css
    any other bucket      ->  assets/theme-{T}.css for each template T

Same logic for custom-theme.css -> assets/custom-theme-*.css.

Emission strategy (SAFE — per ujg6.42 analysis doc):
  Multi-template combos are duplicated across per-template chunks
  intentionally. Wave C wiring is then trivial: one {%if template%} per
  template, no shared combo files.

Input files are NOT modified (Wave C can revert by changing theme.liquid).
Output files are created fresh (overwrite if they exist).

Selector normalization:
  CDN-served CSS has whitespace stripped (e.g. "max-width:479px" vs disk's
  "max-width: 479px"). The norm() function collapses whitespace around CSS
  punctuation and strips attribute-selector quotes to reconcile the two.
  Unmatched rules (merged/split across CDN<->disk) fall back to _unused->core.

Usage:
  cd hairmnl-theme && python3 scripts/ujg6.42/wave-b-emit.py
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).parent.parent.parent  # hairmnl-theme root

TEMPLATES = ['home', 'collection', 'product', 'cart', 'search']

# label in buckets.json -> disk source path
SRC_FILES = {
    'theme.css': REPO / 'assets/theme.css',
    'custom-theme.css': REPO / 'assets/custom-theme.css',
}

# label -> output file prefix (without -core/-home/etc)
OUT_PREFIX = {
    'theme.css': REPO / 'assets/theme',
    'custom-theme.css': REPO / 'assets/custom-theme',
}

BUCKETS_JSON = REPO / 'docs/ujg6.42-buckets.json'

# ---------------------------------------------------------------------------
# Selector normalisation (CDN minifier parity)
# ---------------------------------------------------------------------------

def norm(s: str) -> str:
    """Normalise a selector string to match CDN-minified form."""
    # Collapse whitespace runs to single space
    s = re.sub(r'\s+', ' ', s).strip()
    # Remove spaces around CSS punctuation that the Shopify minifier strips
    s = re.sub(r'\s*([{},;:>+~])\s*', r'\1', s)
    s = re.sub(r'\s*([\[\]()])\s*', r'\1', s)
    # Strip quotes from attribute values that are unquoted-safe (no spaces/specials)
    s = re.sub(r'=["\']([^"\'\\s,\\[\\](){}]+)["\']', r'=\1', s)
    # Lower-case the whole thing (CDN doesn't change case but this helps de-dupe)
    return s.lower()


# ---------------------------------------------------------------------------
# CSS rule parser (same logic as bucket.py find_rules)
# ---------------------------------------------------------------------------

def find_rules_with_text(css: str):
    """Yield (full_sel, rule_text, start, end).

    full_sel includes '@@@ <media-query> @@@ ' prefix for @media-nested rules.
    rule_text is the exact disk-source text for the rule (selector + body).
    """
    rules = []
    i = 0
    n = len(css)
    media_stack = []   # stores normalised @media selector texts

    while i < n:
        # Skip whitespace
        while i < n and css[i] in ' \t\n\r':
            i += 1
        if i >= n:
            break

        # Close brace -> pop media stack
        if css[i] == '}':
            if media_stack:
                media_stack.pop()
            i += 1
            continue

        # Strip comments
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
            full_sel = f'<<at-rule>> {sel_text}'
            rules.append((full_sel, css[sel_start:rule_end], sel_start, rule_end))
            continue

        # Regular rule — read until matching }
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

        # Wrap the rule text with any enclosing @media blocks so the emitted
        # output is self-contained valid CSS (responsive rules stay responsive).
        inner_text = css[sel_start:rule_end]
        if media_stack:
            wrapped = inner_text
            for mq in reversed(media_stack):
                wrapped = f'{mq} {{\n{wrapped}\n}}'
            rule_text = wrapped
        else:
            rule_text = inner_text

        rules.append((full_sel, rule_text, sel_start, rule_end))

    return rules


# ---------------------------------------------------------------------------
# Bucket lookup builder
# ---------------------------------------------------------------------------

def build_norm_to_bucket(bucket_data: dict) -> dict:
    """Return {norm(full_sel): bucket_name} from one file's bucket data."""
    mapping = {}
    collisions = 0
    for bucket_name, rule_list in bucket_data.items():
        for rule in rule_list:
            key = norm(rule['sel'])
            if key in mapping and mapping[key] != bucket_name:
                collisions += 1
            mapping[key] = bucket_name
    if collisions:
        print(f'  WARN: {collisions} selector collisions in bucket map '
              f'(last-write wins)', file=sys.stderr)
    return mapping


# ---------------------------------------------------------------------------
# Emission helpers
# ---------------------------------------------------------------------------

def destinations(bucket_name: str, out_prefix: Path) -> list:
    """Return list of output Path objects for this bucket."""
    if bucket_name in ('_universal', '_unused'):
        return [out_prefix.parent / (out_prefix.name + '-core.css')]
    templates = bucket_name.split('+')
    return [out_prefix.parent / (out_prefix.name + f'-{t}.css')
            for t in templates]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f'Loading {BUCKETS_JSON.name} ...', file=sys.stderr)
    buckets_all = json.loads(BUCKETS_JSON.read_text())

    all_stats = {}

    for label, src_path in SRC_FILES.items():
        if not src_path.exists():
            print(f'SKIP: {src_path} not found', file=sys.stderr)
            continue

        css = src_path.read_text()
        print(f'\n=== {label} ({len(css):,} bytes on disk) ===', file=sys.stderr)

        bucket_data = buckets_all.get(label, {})
        sel_map = build_norm_to_bucket(bucket_data)
        print(f'  {len(sel_map):,} selector→bucket entries', file=sys.stderr)

        rules = find_rules_with_text(css)
        print(f'  {len(rules):,} rules parsed from disk source', file=sys.stderr)

        out_prefix = OUT_PREFIX[label]

        # Open all output file handles
        out_names = {out_prefix.parent / (out_prefix.name + '-core.css')}
        for t in TEMPLATES:
            out_names.add(out_prefix.parent / (out_prefix.name + f'-{t}.css'))

        outfiles = {}
        for p in out_names:
            fh = p.open('w')
            fh.write(f'/* Generated by scripts/ujg6.42/wave-b-emit.py'
                     f' — DO NOT EDIT DIRECTLY */\n\n')
            outfiles[str(p)] = fh

        matched = 0
        unmatched = 0
        unmatched_sample = []
        written_bytes = defaultdict(int)

        for full_sel, rule_text, _s, _e in rules:
            key = norm(full_sel)
            bucket_name = sel_map.get(key)

            if bucket_name is None:
                unmatched += 1
                if len(unmatched_sample) < 25:
                    unmatched_sample.append(full_sel[:100])
                # Safe fallback: treat as _unused -> core
                bucket_name = '_unused'
            else:
                matched += 1

            for dest_path in destinations(bucket_name, out_prefix):
                fh = outfiles[str(dest_path)]
                fh.write(rule_text)
                fh.write('\n')
                written_bytes[str(dest_path)] += len(rule_text) + 1

        for fh in outfiles.values():
            fh.close()

        print(f'  matched: {matched:,}  unmatched (->core): {unmatched}',
              file=sys.stderr)
        if unmatched_sample:
            print(f'  unmatched selectors (first {len(unmatched_sample)}):',
                  file=sys.stderr)
            for s in unmatched_sample:
                print(f'    {s}', file=sys.stderr)

        core_key = str(out_prefix.parent / (out_prefix.name + '-core.css'))
        core_kb = written_bytes.get(core_key, 0) / 1024
        print(f'\n  Output sizes:', file=sys.stderr)
        print(f'    core    : {core_kb:7.1f} KB', file=sys.stderr)
        for t in TEMPLATES:
            p = str(out_prefix.parent / (out_prefix.name + f'-{t}.css'))
            kb = written_bytes.get(p, 0) / 1024
            print(f'    {t:<10}: {kb:7.1f} KB', file=sys.stderr)

        all_stats[label] = {
            'rules': len(rules),
            'matched': matched,
            'unmatched': unmatched,
            'written_bytes': {
                Path(k).name: v for k, v in written_bytes.items()
            },
        }

    # Final summary
    print('\n=== Wave B emission complete ===', file=sys.stderr)
    print('\nExpected sizes (from docs/ujg6.42-coverage-analysis.md):', file=sys.stderr)
    print('  theme-core    : ~222 KB  (universal + unused)', file=sys.stderr)
    print('  theme-home    :  ~22 KB', file=sys.stderr)
    print('  theme-coll    :  ~27 KB', file=sys.stderr)
    print('  theme-product :  ~31 KB', file=sys.stderr)
    print('  theme-cart    :  ~11 KB', file=sys.stderr)
    print('  theme-search  :  ~17 KB', file=sys.stderr)
    print('  custom-core   :  ~40 KB', file=sys.stderr)
    print('  custom-home   :  ~10 KB', file=sys.stderr)

    # Verify totals match source (rules should not be lost)
    for label, s in all_stats.items():
        total_emitted = sum(s['written_bytes'].values())
        src_bytes = SRC_FILES[label].stat().st_size
        delta_pct = abs(total_emitted - src_bytes) / src_bytes * 100
        print(f'\n  {label}: {s["rules"]} rules, {s["matched"]} matched, '
              f'{s["unmatched"]} unmatched -> core', file=sys.stderr)
        print(f'    disk source: {src_bytes:,} B  |  total emitted: '
              f'{total_emitted:,} B  |  delta: {delta_pct:.1f}%', file=sys.stderr)
        # NOTE: total emitted > source because multi-template rules are
        # duplicated into each template's chunk. This is expected.

    return 0


if __name__ == '__main__':
    sys.exit(main())
