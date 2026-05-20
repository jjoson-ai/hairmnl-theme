#!/usr/bin/env python3
"""ujg6.42 Wave A — static coverage analysis.

For each CSS file, parse rules, extract anchor classes/ids/tags from each
selector, then test against the rendered HTML of 5 templates. Bucket each
rule into:
  - universal: selectors that match at least one element on ALL 5 templates
  - template-specific: matches only a subset (named by template combo)
  - unused: matches none of the 5

This is a static-purge approximation of Chrome DevTools Coverage. It misses
JS-injected classes (hover popdowns, dynamically-added DOM) but is good
enough to draw common-vs-specific buckets. Final FOUC verification in Wave
C catches any false-negatives by visual smoke test.
"""

import re
import sys
import json
from pathlib import Path
from collections import defaultdict

HTML_DIR = Path('/tmp/ujg6.42/html')
TEMPLATES = ['home', 'collection', 'product', 'cart', 'search']
CSS_FILES = ['assets/theme.css', 'assets/custom-theme.css']


def extract_html_tokens(html: str) -> dict:
    """Pull class names, ids, and tag names from rendered HTML.
    Returns {'classes': set, 'ids': set, 'tags': set}."""
    classes = set()
    for m in re.finditer(r'class\s*=\s*["\']([^"\']*)["\']', html):
        for c in m.group(1).split():
            if c:
                classes.add(c)

    ids = set()
    for m in re.finditer(r'id\s*=\s*["\']([^"\']*)["\']', html):
        for i in m.group(1).split():
            if i:
                ids.add(i)

    tags = set()
    for m in re.finditer(r'<([a-zA-Z][a-zA-Z0-9-]*)', html):
        tags.add(m.group(1).lower())

    # Also detect data-* attributes used in selectors like [data-foo]
    data_attrs = set()
    for m in re.finditer(r'\b(data-[a-zA-Z0-9-]+)\s*=', html):
        data_attrs.add(m.group(1).lower())

    return {'classes': classes, 'ids': ids, 'tags': tags, 'data_attrs': data_attrs}


def parse_css_rules(css: str):
    """Yield (selector_text, rule_size_bytes) for each top-level rule.

    Handles @media wrappers by yielding their child rules (with the @media
    context kept on the selector). Skips @keyframes / @font-face / @import
    since those are universal.
    """
    # Strip comments
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)

    # Tokenize by braces, respecting nesting
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

        # Closing brace? Pop @media if any
        if css[i] == '}':
            if media_stack:
                media_stack.pop()
            i += 1
            continue

        # Find next { or ;
        start = i
        depth = 0
        while i < n:
            ch = css[i]
            if ch == '{':
                break
            if ch == ';':
                # @import / @charset etc — single-line at-rules
                i += 1
                break
            i += 1

        if i >= n:
            break
        if css[i] != '{':
            continue

        selector_text = css[start:i].strip()
        if not selector_text:
            i += 1
            continue

        i += 1  # past {

        if selector_text.lower().startswith('@media'):
            media_stack.append(selector_text)
            continue

        if selector_text.lower().startswith('@keyframes') or \
           selector_text.lower().startswith('@-webkit-keyframes') or \
           selector_text.lower().startswith('@font-face') or \
           selector_text.lower().startswith('@supports'):
            # Walk past the entire block (with nesting)
            depth = 1
            block_start = i
            while i < n and depth > 0:
                if css[i] == '{':
                    depth += 1
                elif css[i] == '}':
                    depth -= 1
                i += 1
            # Record as "universal" at-rule (yield with marker)
            rules.append((f"<<at-rule>>{selector_text}", i - block_start + len(selector_text)))
            continue

        # Regular rule — find closing brace at depth 1
        depth = 1
        block_start = i
        while i < n and depth > 0:
            if css[i] == '{':
                depth += 1
            elif css[i] == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1

        if i >= n:
            break

        rule_size = (i - block_start) + len(selector_text) + 2  # +braces

        prefix = '@@'.join(media_stack)
        full_sel = (f"{prefix}@@" if prefix else "") + selector_text
        rules.append((full_sel, rule_size))

        i += 1  # past }

    return rules


# Regex to extract anchors from a single selector (one of N comma-separated)
def selector_anchors(sel: str) -> dict:
    """For a CSS selector, return its anchor tokens:
    {classes, ids, tags, data_attrs, has_universal}
    Universal selectors (*, just :pseudo) are flagged."""
    # Strip pseudo classes/elements for anchor extraction
    # but keep them for the final test (some need element_query later)
    classes = set(re.findall(r'\.([\w-]+)', sel))
    ids = set(re.findall(r'#([\w-]+)', sel))
    data_attrs = set(re.findall(r'\[(data-[\w-]+)', sel.lower()))

    # Tag extraction — leading word that's not a pseudo
    # Match the first identifier in each compound, stripped of leading combinator
    # Compounds split on space/>/+/~
    tags = set()
    for compound in re.split(r'[\s>+~]+', sel):
        m = re.match(r'^([a-zA-Z][a-zA-Z0-9-]*)(?:[\.\#\[\:]|$)', compound)
        if m:
            tag = m.group(1).lower()
            if tag not in ('and', 'or', 'not', 'is', 'where', 'has'):
                tags.add(tag)

    has_universal = '*' in sel and not (classes or ids)
    return {'classes': classes, 'ids': ids, 'tags': tags,
            'data_attrs': data_attrs, 'has_universal': has_universal}


def rule_matches_template(selector: str, tokens: dict) -> bool:
    """Does any comma-separated branch of this selector have ALL its anchors
    present in the template's tokens? True if at least one branch matches."""
    # Strip @media prefix
    if '@@' in selector:
        selector = selector.rsplit('@@', 1)[-1]

    # @-rules — treat as universal
    if selector.startswith('@'):
        return True

    branches = [s.strip() for s in selector.split(',')]
    for branch in branches:
        if not branch:
            continue
        a = selector_anchors(branch)
        if a['has_universal']:
            return True
        # Strategy: if branch has classes or ids → ALL must be present
        # If only tag selectors → tag must be present
        # If has data-attr → data-attr must be present
        ok = True
        if a['classes']:
            if not a['classes'].issubset(tokens['classes']):
                ok = False
        if ok and a['ids']:
            if not a['ids'].issubset(tokens['ids']):
                ok = False
        if ok and a['data_attrs']:
            if not a['data_attrs'].issubset(tokens['data_attrs']):
                ok = False
        if ok and not (a['classes'] or a['ids'] or a['data_attrs']):
            # Pure tag selector — check tag presence
            if a['tags']:
                if not a['tags'].issubset(tokens['tags']):
                    ok = False
            else:
                # Empty branch (e.g. just :root, ::placeholder) — universal
                ok = True
        if ok:
            return True
    return False


def main():
    # Load template HTMLs and tokens
    tokens = {}
    for t in TEMPLATES:
        html = (HTML_DIR / f'{t}.html').read_text(errors='replace')
        tokens[t] = extract_html_tokens(html)
        print(f'[{t}] {len(tokens[t]["classes"])} classes, '
              f'{len(tokens[t]["ids"])} ids, '
              f'{len(tokens[t]["tags"])} tags, '
              f'{len(tokens[t]["data_attrs"])} data-attrs',
              file=sys.stderr)

    summary = {}
    for css_file in CSS_FILES:
        css = Path(css_file).read_text()
        rules = parse_css_rules(css)
        print(f'\n=== {css_file}: {len(rules)} rules, '
              f'{len(css)//1024} KB ===', file=sys.stderr)

        buckets = defaultdict(lambda: {'count': 0, 'bytes': 0,
                                       'examples': []})
        for sel, rsize in rules:
            usage = set()
            for t in TEMPLATES:
                if rule_matches_template(sel, tokens[t]):
                    usage.add(t)

            if not usage:
                key = '_unused'
            elif len(usage) == 5:
                key = '_universal'
            else:
                key = '+'.join(sorted(usage))

            b = buckets[key]
            b['count'] += 1
            b['bytes'] += rsize
            if len(b['examples']) < 5:
                # Trim long selectors
                ex = sel if len(sel) < 120 else sel[:117] + '...'
                b['examples'].append(ex)

        summary[css_file] = dict(buckets)

        for key in sorted(buckets):
            b = buckets[key]
            print(f'  {key:60} {b["count"]:>5} rules  {b["bytes"]//1024:>5} KB',
                  file=sys.stderr)

    # Write summary JSON for the doc generator
    out = Path('/tmp/ujg6.42/coverage-summary.json')
    out.write_text(json.dumps(summary, indent=2))
    print(f'\nWrote {out}', file=sys.stderr)


if __name__ == '__main__':
    main()
