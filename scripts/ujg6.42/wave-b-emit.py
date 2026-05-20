#!/usr/bin/env python3
"""Wave B — CSS split emitter (ujg6.42.2 / ujg6.42.5 --strict).

Reads docs/ujg6.42-buckets.json (the Wave A real-Coverage output), the
disk source CSS files (assets/theme.css, assets/custom-theme.css), AND
the HTML class-presence map at /tmp/ujg6.42/html-corrections/class-presence.json.

For each rule:
  1. Start with the Coverage-determined bucket (set of templates).
  2. Extract class/id refs from the rule's selector.
  3. Look up which templates have any of those classes in their rendered HTML.
  4. UNION the HTML-detected templates with the Coverage bucket.
  5. The expanded bucket determines the output destination.

This corrects for Coverage's blind spots — rules that only fire during
JS hydration, user interaction, or app injection (Swiper init, Flickity init,
cart-loading state, modal/drawer open, error states, etc.) that Coverage's
headless session didn't trigger.

Routing:
    _universal (all 5)  ->  assets/theme-core.css
    _unused    (0 of 5) ->  assets/theme-core.css   (kept as safe default)
    any combo  ->  assets/theme-{T}.css for each T in expanded bucket

Same logic for custom-theme.css.

Input files are NOT modified (Wave C can revert by changing theme.liquid).
Output files are created fresh (overwrite if they exist).

Usage:
  cd hairmnl-theme && python3 scripts/ujg6.42/wave-b-emit.py
  cd hairmnl-theme && python3 scripts/ujg6.42/wave-b-emit.py --strict

--strict mode (ujg6.42.5 Phase 2):
  Reads /tmp/ujg6.42/unused-verification.json produced by verify-unused.py.
  Any rule whose normalised selector appears in the REMOVE_CANDIDATE verdict
  list is silently skipped — it is not emitted to any output chunk.
  Requires verify-unused.py to have been run first.
"""
import argparse
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
CLASS_PRESENCE_JSON = Path('/tmp/ujg6.42/html-corrections/class-presence.json')
UNUSED_VERIFICATION_JSON = Path('/tmp/ujg6.42/unused-verification.json')

# Maps src-file label (key in SRC_FILES) -> chunk label in unused-verification.json
SRC_TO_CHUNK_LABEL = {
    'theme.css': 'theme-core.css',
    'custom-theme.css': 'custom-theme-core.css',
}


def _verify_tempdir_perms(path: Path):
    """ujg6.42.4 (audit hardening): verify the pipeline tempdir is owner-only
    before trusting its contents to influence the emitted chunk files. A
    swapped class-presence.json could otherwise push selectors into wrong
    template chunks, e.g. injecting hostile CSS into a per-template chunk."""
    if not path.exists():
        return  # caller will fail naturally; no perms to check
    mode = path.stat().st_mode & 0o777
    if mode != 0o700:
        print(f'WARN: {path} has mode {oct(mode)} (expected 0o700). '
              f'Run: chmod 700 {path}', file=sys.stderr)
        try:
            path.chmod(0o700)
        except PermissionError:
            print('ERROR: cannot tighten perms — refusing to read possibly-'
                  'tampered files.', file=sys.stderr)
            sys.exit(2)


_verify_tempdir_perms(Path('/tmp/ujg6.42'))
if CLASS_PRESENCE_JSON.parent.exists():
    _verify_tempdir_perms(CLASS_PRESENCE_JSON.parent)


# Selector pattern -> extracts class names and ids
_CLASS_RE = re.compile(r'\.([a-zA-Z_][a-zA-Z0-9_-]*)')
_ID_RE = re.compile(r'#([a-zA-Z_][a-zA-Z0-9_-]*)')

# ---------------------------------------------------------------------------
# Forced-core selectors (JS-library bases, app injections, ATF layout-critical)
# ---------------------------------------------------------------------------
# These selectors are FORCED to _universal regardless of Coverage bucket or
# HTML presence. They cover:
#   - JS-init-dependent classes (Swiper, Flickity, AOS) - DOM gets these
#     AFTER JS hydration, so HTML scrape misses them, but pre-hydration
#     layout needs them.
#   - App-injection state classes (FreeGifts, LimeSpot, etc.) - DOM
#     populated by app JS, scrape misses, but ATF layout depends on them.
#   - Cart loading states - shown briefly before AJAX completes.
#   - Modal/drawer state classes - hidden by default, only visible on
#     user interaction Coverage didn't trigger.
#   - Section/layout wrappers used everywhere.
#
# When any class/id in the selector matches one of these patterns, the
# whole rule moves to core.
_FORCE_CORE_PATTERNS = [
    # JS carousel libraries
    re.compile(r'\.swiper(?:-|\b)'),
    re.compile(r'\.flickity(?:-|\b)'),
    # AOS / scroll animation library
    re.compile(r'\.aos(?:-|\b)'),
    re.compile(r'\[data-aos'),
    # Lazy-image library
    re.compile(r'\.lazy-image(?:\b|__)'),
    re.compile(r'\.lazyload(?:ed|ing)?\b'),
    # Plyr video player
    re.compile(r'\.plyr(?:-|__|\b)'),
    # Cart state classes (loading, hidden, empty)
    re.compile(r'\.cart--hidden\b'),
    re.compile(r'\.cart__empty\b'),
    re.compile(r'\[data-cart-loading\]'),
    re.compile(r'\.cart__loading\b'),
    # App injection containers (these render late, layout depends on them)
    re.compile(r'\.freegifts(?:-|\b)'),
    re.compile(r'#freegifts'),
    re.compile(r'\.judgeme(?:-|\b)'),
    re.compile(r'\.jdgm(?:-|\b)'),
    re.compile(r'\.spr(?:-|_)'),  # Shopify Product Reviews
    re.compile(r'\.swym(?:-|\b)'),
    re.compile(r'\.appstle(?:-|\b)'),
    re.compile(r'\.limespot(?:-|\b)'),
    re.compile(r'\.ufe(?:-|\b)'),
    re.compile(r'\.bold-(?:upsell|product-options)\b'),
    re.compile(r'\.satcb(?:-|_)'),
    # Modal / drawer / popup state classes (hidden, only visible on JS)
    re.compile(r'\.modal(?:-|_|\b)'),
    re.compile(r'\.micromodal(?:-|\b)'),
    re.compile(r'\.drawer(?:-|__|\b)'),
    re.compile(r'\.popdown(?:-|__|\b)'),
    re.compile(r'\.popup(?:-|__|\b)'),
    # Cart upsell ("Buy It With") widget — appears on cart page + cart drawer,
    # AND on product page recommendations. Coverage bucketed it to product-only
    # (regression fixed 2026-05-20 after user-reported cart-page breakage).
    re.compile(r'\.upsell(?:__|\b)'),
    # Cart-footer layout grid + nested elements (cart-page.css cascade dependency)
    re.compile(r'\.template__cart(?:__|\b)'),
    re.compile(r'\.cart__footer(?:__|\b)'),
    # Form error/loading states (only triggered on submit)
    re.compile(r'\.has-error\b'),
    re.compile(r'\.errors?\b'),
    re.compile(r'\.btn-state-(?:loading|complete)\b'),
    re.compile(r'\.is-loading\b'),
    re.compile(r'\.notice\b'),
    re.compile(r'\.alert\b'),
    # Hero / section layout (above-fold critical on multiple templates)
    re.compile(r'\.hero(?:-|__|\b)'),
    re.compile(r'\.section(?:-|__|\b)'),
    re.compile(r'\.banner-slider(?:-|\b)'),
    re.compile(r'\.banner-slide(?:-|\b)'),
    re.compile(r'\.shopify-section(?:-|\b)'),
    # Universal layout wrappers (used in every template's first paint)
    re.compile(r'(^|\s|,)\.wrapper(?:\s|,|:|\.|\[|\{|$)'),
    re.compile(r'\.main-content(?:\b|__)'),
    # JS-toggled class state markers
    re.compile(r'\.js-grid\b'),
    re.compile(r'\.js-loaded\b'),
    re.compile(r'\.js-sticky'),
    # Product grid base layout (used in featured collections on every template)
    re.compile(r'\.product-grid-item\b'),
    re.compile(r'\.product__grid'),
]


def force_core_match(sel: str) -> bool:
    """Return True if this selector matches a forced-core pattern."""
    for pat in _FORCE_CORE_PATTERNS:
        if pat.search(sel):
            return True
    return False

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


def load_class_to_templates() -> dict:
    """Return {class_name: set(templates)} from HTML scrape map.

    Class names DON'T have a leading '.' here; IDs have a leading '#'.
    Returns {} if the file is missing (graceful degradation — same behavior
    as Coverage-only Wave B).
    """
    if not CLASS_PRESENCE_JSON.exists():
        print(f'  NOTE: {CLASS_PRESENCE_JSON} not found — using Coverage '
              f'only (no HTML-presence expansion)', file=sys.stderr)
        return {}
    data = json.loads(CLASS_PRESENCE_JSON.read_text())
    return {c: set(ts) for c, ts in data['class_to_templates'].items()}


def bucket_from_coverage(bucket_name: str) -> set:
    """Convert a Coverage bucket name to a set of templates."""
    if bucket_name == '_universal':
        return set(TEMPLATES)
    if bucket_name == '_unused':
        return set()
    return set(bucket_name.split('+'))


def templates_to_bucket(tmpls: set) -> str:
    """Convert a set of templates back to a bucket name."""
    if not tmpls:
        return '_unused'
    if len(tmpls) == len(TEMPLATES):
        return '_universal'
    return '+'.join(sorted(tmpls))


def expand_bucket_via_html(sel: str, cov_bucket: str,
                            class_to_templates: dict) -> str:
    """Take a Coverage bucket + selector text + HTML presence map.

    Returns the (possibly expanded) bucket name. If the selector references
    any class/id that appears in additional templates' HTML, those templates
    are unioned into the bucket.

    Special case: '_unused' rules are expanded only if HTML presence is found
    AND that presence covers >= 1 template (otherwise stays in _unused -> core).
    """
    if not class_to_templates:
        return cov_bucket

    cov_set = bucket_from_coverage(cov_bucket)

    classes = set(_CLASS_RE.findall(sel))
    ids = set('#' + m for m in _ID_RE.findall(sel))

    html_set = set()
    for c in classes:
        if c in class_to_templates:
            html_set |= class_to_templates[c]
    for i in ids:
        if i in class_to_templates:
            html_set |= class_to_templates[i]

    expanded = cov_set | html_set
    return templates_to_bucket(expanded)


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
# --strict mode: load REMOVE_CANDIDATE sets from verify-unused output
# ---------------------------------------------------------------------------

def load_remove_candidates() -> dict:
    """Load REMOVE_CANDIDATE normalised selector sets from verify-unused.py output.

    Returns {src_label: frozenset(norm_sel)} e.g.:
        {'theme.css': frozenset({'...', ...}), 'custom-theme.css': frozenset({...})}

    The selector strings in the JSON use the same '@@@ @media ... @@@ selector'
    format as full_sel in this script, so norm() maps them to the same keys.
    """
    if not UNUSED_VERIFICATION_JSON.exists():
        print(
            f'ERROR: --strict requires {UNUSED_VERIFICATION_JSON}\n'
            f'       Run: python3 scripts/ujg6.42/verify-unused.py first.',
            file=sys.stderr,
        )
        sys.exit(1)

    data = json.loads(UNUSED_VERIFICATION_JSON.read_text())
    result = {}
    for src_label, chunk_label in SRC_TO_CHUNK_LABEL.items():
        chunk_data = data.get(chunk_label, {})
        rc_rules = chunk_data.get('verdicts', {}).get('REMOVE_CANDIDATE', [])
        normed = frozenset(norm(r['sel']) for r in rc_rules)
        result[src_label] = normed
        print(
            f'  --strict: {len(normed):,} REMOVE_CANDIDATE selectors loaded '
            f'for {src_label} (from {chunk_label})',
            file=sys.stderr,
        )
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Wave B CSS split emitter. See module docstring for full usage.')
    parser.add_argument(
        '--strict', action='store_true',
        help='ujg6.42.5: skip REMOVE_CANDIDATE rules from verify-unused.py output '
             '(omits ~102 KB of dead CSS from core chunks).')
    args = parser.parse_args()

    if args.strict:
        print('--strict mode: loading REMOVE_CANDIDATE sets ...', file=sys.stderr)
        remove_candidates = load_remove_candidates()
    else:
        remove_candidates = {}

    print(f'Loading {BUCKETS_JSON.name} ...', file=sys.stderr)
    buckets_all = json.loads(BUCKETS_JSON.read_text())

    print(f'Loading HTML class-presence map ...', file=sys.stderr)
    class_to_templates = load_class_to_templates()
    print(f'  {len(class_to_templates):,} unique classes/ids '
          f'across templates', file=sys.stderr)

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
        expanded_count = 0
        forced_core_count = 0
        skipped_strict = 0
        unmatched_sample = []
        written_bytes = defaultdict(int)

        # Per-label remove-candidate set (empty if not --strict)
        remove_set = remove_candidates.get(label, frozenset())

        for full_sel, rule_text, _s, _e in rules:
            key = norm(full_sel)

            # --strict: skip REMOVE_CANDIDATE rules entirely (do not emit to any chunk)
            if remove_set and key in remove_set:
                skipped_strict += 1
                continue

            cov_bucket = sel_map.get(key)

            if cov_bucket is None:
                unmatched += 1
                if len(unmatched_sample) < 25:
                    unmatched_sample.append(full_sel[:100])
                cov_bucket = '_unused'
            else:
                matched += 1

            # Expand bucket via HTML class presence
            bucket_name = expand_bucket_via_html(full_sel, cov_bucket,
                                                   class_to_templates)
            if bucket_name != cov_bucket:
                expanded_count += 1

            # Override: forced-core selectors always go to core (regardless
            # of Coverage or HTML expansion). Catches JS-library bases and
            # app-injection classes that scrape methods miss.
            if force_core_match(full_sel):
                if bucket_name != '_universal':
                    forced_core_count += 1
                bucket_name = '_universal'

            for dest_path in destinations(bucket_name, out_prefix):
                fh = outfiles[str(dest_path)]
                fh.write(rule_text)
                fh.write('\n')
                written_bytes[str(dest_path)] += len(rule_text) + 1

        for fh in outfiles.values():
            fh.close()

        print(f'  matched: {matched:,}  unmatched (->core): {unmatched}',
              file=sys.stderr)
        print(f'  HTML-expanded buckets: {expanded_count:,}',
              file=sys.stderr)
        print(f'  Forced-to-core (JS-lib/app/state): {forced_core_count:,}',
              file=sys.stderr)
        if args.strict:
            print(f'  --strict skipped (REMOVE_CANDIDATE): {skipped_strict:,}',
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
    mode_tag = ' [--strict]' if args.strict else ''
    print(f'\n=== Wave B emission complete{mode_tag} ===', file=sys.stderr)
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
