#!/usr/bin/env python3
"""kt0 lint — catch CSS containing-block creators applied to overlay selectors.

Rule (from CLAUDE.md kt0):
  contain:layout|paint|strict|content, transform, filter, backdrop-filter,
  perspective, and will-change:transform|filter all create a new containing
  block for fixed/absolute-positioned descendants.

  When applied to a parent of an overlay (chat widget, cart drawer, modal,
  sticky header, mobile menu), the overlay's child positioning math breaks
  silently — children end up at coordinates relative to the wrong ancestor.

Regression history this protects against:
  - 2026-05-11: sticky header broke fixed-position descendants (cart icon)
  - 2026-05-12: Reamaze chat icon pushed off-screen by `[id^="reamaze-widget"]`
    + contain:layout in snippets/css-overrides.liquid (bd hairmnl-theme-lki)

How it works:
  Scans *.liquid, *.css, *.scss for CSS rule blocks where:
    (a) the selector matches a known overlay pattern, AND
    (b) the body contains a containing-block-creating property
  Each match exits non-zero unless the body contains the literal token
  `/* kt0-OK */` acknowledging human review.

Usage:
  python3 scripts/check-overlay-css.py             # scan repo, exit 1 on violations
  python3 scripts/check-overlay-css.py --list      # show every match (informational)
  python3 scripts/check-overlay-css.py path/to/file.liquid

Add new overlay selectors to OVERLAY_PATTERNS as the storefront grows.
"""

from __future__ import annotations
import re
import sys
from pathlib import Path

# Known overlay selectors. Conservative — false positives are OK (developer
# adds `/* kt0-OK */` to ack), false negatives are not (regressions slip through).
# Match against the selector text, case-insensitive.
OVERLAY_PATTERNS = re.compile(
    r"""(
        \#?reamaze[-\w]*           # #reamaze-widget, .reamaze-foo
      | cart[-_]?drawer             # .cart-drawer, #CartDrawer
      | \.drawer\b                  # generic .drawer
      | \.modal\b                   # .modal
      | \.popup\b                   # .popup
      | \.overlay\b                 # .overlay
      | \[role=["']dialog          # [role="dialog"]
      | mobile[-_]?nav              # mobile-nav, mobile_nav
      | menu[-_]?mobile             # menu-mobile
      | header[-_]?sticky           # header-sticky
      | site[-_]?header             # site-header (sticky variant)
      | navigation                   # .navigation (broad — most are overlay parents on mobile)
      | \[id\^=                     # [id^="..."] starts-with attribute (catches 7fz pattern)
      # J31 (bd 2i8b.96): overlays the P8 epic itself created — the Quick Buy
      # popover already demonstrated the containing-block trap class in-epic (J24).
      | qb[-_]?popover              # [data-qb-popover], .quick-buy__popover
      | quick-buy__popover
      | vrec-product-sticky-bar     # PDP sticky ATC bar (position:fixed)
      | sticky-cart-bubble          # desktop floating cart (position:fixed)
      | vrec-fly-clone              # fly-to-cart transient clone (position:fixed)
    )""",
    re.IGNORECASE | re.VERBOSE,
)

# Properties that create a new containing block for fixed/absolute descendants.
# Each is matched as a property declaration `prop: value;` (with optional !important).
# transform/filter/perspective with value `none` are NOT containing-block creators,
# so we exclude those.
FORBIDDEN_PROPS = re.compile(
    r"""
    (?:^|\s|;|\{)\s*
    (?:
        contain\s*:\s*(?:layout|paint|strict|content)\b
      # J31 (bd 2i8b.96): lookaheads moved BEFORE \s* — the old `\s*(?!none\b)`
      # form let the regex engine backtrack \s* to zero and match the leading
      # space as part of the value, silently defeating the none/normal
      # exclusions (latent in the original transform/filter/perspective lines).
      | transform\s*:(?!\s*none\b)[^;}\n]+
      | filter\s*:(?!\s*none\b)[^;}\n]+
      | backdrop-filter\s*:(?!\s*none\b)[^;}\n]+
      | perspective\s*:(?!\s*none\b)[^;}\n]+
      | will-change\s*:\s*[^;}\n]*\b(?:transform|filter|perspective)\b
      # J31 (bd 2i8b.96): container queries create layout/style containment —
      # same containing-block trap as contain:layout (J29 introduced the repo's
      # first, verified-safe, use on non-overlay .lazy-image selectors).
      | container-type\s*:(?!\s*normal\b)[^;}\n]+
      | container\s*:(?!\s*(?:none|normal)\b)[^;}\n]+
    )
    """,
    re.IGNORECASE | re.VERBOSE | re.MULTILINE,
)

ACK_TOKEN = "kt0-OK"
ACK_RE = re.compile(r'/\*[^*]*\bkt0-OK\b', re.DOTALL)
"""The literal marker (anywhere inside any /* */ comment in the rule body)
acknowledges that a human/AI has reviewed the kt0-rule implications. Use:
    /* kt0-OK */
or with a justification:
    /* kt0-OK: display:none means containment is moot */
"""


def find_rule_blocks(text: str):
    """Yield (selector_text, body_text, body_start_offset) for each CSS rule.

    Naive parser: tracks brace depth; treats text between `;` or block boundary
    and `{` as the selector. Skips @media, @keyframes, @supports headers (we
    descend into their blocks but don't treat the @-rule as a selector).
    """
    i, n = 0, len(text)
    selector_start = 0
    depth = 0
    block_open = None

    while i < n:
        ch = text[i]

        # Skip /* ... */ comments. When we're at depth 0 (between rules),
        # also advance selector_start so the comment is not absorbed into
        # the next selector text we report.
        if ch == '/' and i + 1 < n and text[i + 1] == '*':
            end = text.find('*/', i + 2)
            new_i = end + 2 if end != -1 else n
            if depth == 0:
                selector_start = new_i
            i = new_i
            continue

        # Skip strings (rare in CSS but possible in url(""))
        if ch in ('"', "'"):
            quote = ch
            i += 1
            while i < n and text[i] != quote:
                if text[i] == '\\':
                    i += 2
                else:
                    i += 1
            i += 1
            continue

        if ch == '{':
            if depth == 0:
                selector_text = text[selector_start:i]
                block_open = i + 1
            depth += 1
            i += 1
            continue

        if ch == '}':
            depth -= 1
            if depth == 0 and block_open is not None:
                body_text = text[block_open:i]
                yield selector_text, body_text, block_open
                selector_start = i + 1
                block_open = None
            i += 1
            continue

        if ch == ';' and depth == 0:
            selector_start = i + 1

        i += 1


def is_at_rule(selector: str) -> bool:
    s = selector.strip().lstrip(';').lstrip()
    return s.startswith('@')


def iter_rules(text: str, base_offset: int = 0):
    """Yield (selector, body, abs_offset) for every rule, DESCENDING into
    @media/@supports blocks.

    J31 (bd 2i8b.96): find_rule_blocks yields TOP-LEVEL blocks only — the whole
    at-rule body used to be attributed to the '@media ...' header (which never
    matches OVERLAY_PATTERNS), so every media-nested rule was silently invisible
    to this lint. Both prior kt0 production incidents happened to be top-level
    rules, which is why the blind spot survived. @keyframes bodies are still
    skipped (frame selectors like 0%/100% are not element selectors)."""
    for selector, body, off in find_rule_blocks(text):
        s = selector.strip().lstrip(';').lstrip()
        if s.startswith('@'):
            low = s.lower()
            if low.startswith('@media') or low.startswith('@supports'):
                yield from iter_rules(body, base_offset + off)
            continue
        yield selector, body, base_offset + off


def line_of(text: str, offset: int) -> int:
    return text.count('\n', 0, offset) + 1


def scan_file(path: Path, list_mode: bool = False) -> list[dict]:
    findings = []
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        print(f"warn: could not read {path}: {e}", file=sys.stderr)
        return findings

    for selector, body, body_start in iter_rules(text):
        if not OVERLAY_PATTERNS.search(selector):
            continue
        if not FORBIDDEN_PROPS.search(body):
            continue
        if ACK_RE.search(body):
            if list_mode:
                findings.append({
                    'path': str(path),
                    'line': line_of(text, body_start),
                    'selector': selector.strip()[:100],
                    'body_excerpt': body.strip()[:120].replace('\n', ' '),
                    'acked': True,
                })
            continue
        findings.append({
            'path': str(path),
            'line': line_of(text, body_start),
            'selector': selector.strip()[:120],
            'body_excerpt': body.strip()[:150].replace('\n', ' '),
            'acked': False,
        })
    return findings


def main(argv: list[str]) -> int:
    list_mode = '--list' in argv
    file_args = [a for a in argv[1:] if not a.startswith('--')]

    # Pipeline 6 vendor base files — we don't edit these; their existing transforms
    # on .drawer__content etc. are the theme's own slide-in animations and have
    # worked unchanged for years. Excluding to keep the signal sharp on the files
    # we actually author.
    VENDOR_EXCLUDE = {
        'assets/theme.css',
        'assets/theme.dev.css',
        'assets/theme.scss.liquid',
        'assets/checkout.css',
        'assets/checkout.scss.liquid',
        # ujg6.42 split the stock theme.css into per-template chunks. They carry
        # the SAME stock Pipeline content (drawer/popup slide-in transforms on
        # .drawer__content etc.) that theme.css does — not hand-authored overlay
        # code — so they inherit theme.css's exclusion. (Without this the lint
        # re-flags the stock transforms that were excluded while in theme.css.)
        # custom-theme*.css are deliberately NOT excluded — those are HairMNL's
        # own overrides, where a real kt0 regression would land.
        'assets/theme-core.css',
        'assets/theme-home.css',
        'assets/theme-collection.css',
        'assets/theme-product.css',
        'assets/theme-cart.css',
        'assets/theme-search.css',
    }

    if file_args:
        paths = [Path(p) for p in file_args]
    else:
        root = Path(__file__).parent.parent
        paths = []
        for sub in ('layout', 'snippets', 'sections', 'templates', 'assets'):
            d = root / sub
            if not d.is_dir():
                continue
            for ext in ('*.liquid', '*.css', '*.scss'):
                paths.extend(d.rglob(ext))
        # Filter out vendor base files
        paths = [
            p for p in paths
            if str(p.relative_to(root)) not in VENDOR_EXCLUDE
        ]

    all_findings = []
    for p in sorted(paths):
        all_findings.extend(scan_file(p, list_mode=list_mode))

    violations = [f for f in all_findings if not f['acked']]
    acked = [f for f in all_findings if f['acked']]

    if list_mode and acked:
        print(f"== {len(acked)} acknowledged kt0 use(s) (kt0-OK) ==")
        for f in acked:
            print(f"  {f['path']}:{f['line']}  selector: {f['selector']}")
        print()

    if violations:
        print(f"FAIL: {len(violations)} kt0 violation(s) — overlay selector with containing-block creator")
        print(f"  Reference: CLAUDE.md kt0 rule + bd hairmnl-theme-lki (Reamaze chat regression 2026-05-12)")
        print()
        for f in violations:
            print(f"  {f['path']}:{f['line']}")
            print(f"    selector: {f['selector']}")
            print(f"    body:     {f['body_excerpt']}")
            print()
        print(f"If intentional, add a comment containing the token  kt0-OK  inside the rule body. Examples:")
        print(f"    /* kt0-OK */")
        print(f"    /* kt0-OK: display:none means containment is moot */")
        return 1

    print(f"OK: scanned {len(paths)} files, no kt0 violations" + (f" ({len(acked)} acked)" if acked else ""))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
