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

SECOND CHECK — comment integrity (bd hairmnl-theme-w1n6, added 2026-08-05):
  A CSS comment ends at the FIRST terminator sequence. If one is typed inside
  a comment, the comment closes early, the following prose parses as CSS, the
  parser derails, and every rule after that point silently stops applying.
  This is invisible to source review — the CSS text looks perfectly correct.
  Three layered signals, none needing a third-party parser:
    1. a terminator sequence wrapped in quotes (the literal 2026-08-05 defect)
    2. prose reaching selector position after parser-accurate comment stripping
       (the general case — catches an unquoted terminator too)
    3. a markup-injecting Liquid tag inside a CSS comment (Liquid does not
       respect CSS comments and renders anyway — the 6279005 sibling bug)
  Both 2026-08-05 defects are reproduced as fixtures and asserted by --selftest.

Usage:
  python3 scripts/check-overlay-css.py             # scan repo, exit 1 on violations
  python3 scripts/check-overlay-css.py --list      # show every match (informational)
  python3 scripts/check-overlay-css.py --selftest  # assert the lint itself still works
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
      | notify[-_]?tab              # BIS sticky tab, position:fixed (g1n.6)
      | notify[-_]?modal            # BIS notify modal + fields (g1n.6)
      | notify[-_]?when[-_]?available  # BIS modal id/asset selectors (g1n.6)
      # bd 9ms4 (2026-08-13): the LoyaltyLion notification toast is a genuine
      # overlay — its container is position:fixed at z-index 1000000003 — but it
      # was NOT covered here, so a containment mistake on it would have slipped
      # through silently. Its own transform usage carries a kt0-OK note in
      # os2-migration/css-overrides.source.liquid.
      | lion[-_]notification        # LoyaltyLion toast container + toast itself
      | \#loyaltylion               # LL SDK root element
      # bd ioba.1 (2026-08-25): the reward-gift modals use the stock .modal
      # markup (already covered by \.modal\b above), but they are ALSO
      # addressable by id — #reward-gate-modal / #reward-reminder-modal — and
      # an id-based rule would slip past every pattern here.
      | reward[-_]?(gate|reminder)  # reward-gift explainer + redemption reminder
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


# ---------------------------------------------------------------------------
# Comment-integrity check (bd hairmnl-theme-w1n6)
#
# 2026-08-05: a comment in snippets/css-overrides.liquid quoted the CSS
# comment-terminator sequence as an example. A CSS comment ends at the FIRST
# terminator, so the comment closed early, the remaining prose was parsed as
# CSS, the parser derailed, and 180 of 206 rules (74KB, 76%) silently stopped
# applying on live. Four customer-visible symptoms followed: the quick-buy icon
# collapsed, the quick-buy popover leaked variant titles onto every product
# card, the PDP sticky add-to-cart bar lost position:fixed, and the cart bubble
# rendered inline at the top-left.
#
# Source review cannot catch this — the CSS text is present and reads
# correctly. It is only visible by asking what a parser actually ACCEPTED.
# Same failure family as the bug fixed hours earlier the same day (Liquid
# executing inside a CSS comment): css-overrides.liquid is inlined into a
# <style> block, so anything that corrupts comment structure is sitewide.
#
# Two layered signals, both offset-preserving so line numbers stay exact:
#   1. a terminator sequence WRAPPED in quotes  -> the literal 2026-08-05 shape
#   2. prose reaching selector position after parser-accurate comment stripping
#      -> the general case, catches an unquoted terminator too
# ---------------------------------------------------------------------------

STYLE_BLOCK_RE = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE)
LIQUID_TAG_RE = re.compile(r'\{%.*?%\}|\{\{.*?\}\}', re.DOTALL)

# Liquid comment BLOCKS must be blanked before <style> extraction, not merely
# have their tags stripped. Several sections discuss the markup in prose —
# sections/section-banner-slider.liquid:82 contains the literal text "<style>"
# inside a {%- comment -%}. Left in place, that opening tag pairs with the real
# closing tag further down and drags English prose into the CSS region, which
# is a false positive of exactly the kind this lint exists to avoid raising.
# Liquid comments emit nothing, so they can never contribute CSS.
LIQUID_COMMENT_RE = re.compile(
    r'\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}',
    re.DOTALL | re.IGNORECASE,
)

# Liquid tags that INJECT MARKUP. These are the ones that must never appear
# inside a CSS comment (see _liquid_in_comments). Assignment/control-flow tags
# and `{{ }}` outputs are excluded on purpose — commenting out a declaration
# that interpolates a setting is a normal, harmless pattern.
LIQUID_INJECT_RE = re.compile(r'\{%-?\s*(?:render|include|section)\s[^%]*?-?%\}', re.IGNORECASE)

# Four or more consecutive bare alphabetic words separated by plain spaces.
# A real selector essentially always carries . # [ ] : > + ~ or a hyphen.
# NOTE: at-rule preludes DO legitimately read as prose — `@media only screen
# and (min-width: 499px)` is exactly four bare words — so _prose_reason only
# inspects the text BEFORE any `@`. Verified against every CSS-bearing file
# in the repo (7 stylesheets tripped the first version of this rule).
PROSE_RUN_RE = re.compile(r'(?:\b[A-Za-z]{2,}\b[ \t]+){3,}\b[A-Za-z]{2,}\b')


def _blank_like(s: str) -> str:
    """Same-length blank string, newlines preserved so line numbers survive."""
    return ''.join('\n' if c == '\n' else ' ' for c in s)


def css_regions(path: Path, text: str) -> list[tuple[int, int]]:
    """Spans of `text` that are CSS.

    .css/.scss  -> the whole file.
    .liquid     -> only inside <style> blocks (css-overrides.liquid has 5, and
                   ~20 section files carry Liquid-templated <style> blocks).
    """
    if path.suffix.lower() in ('.css', '.scss'):
        return [(0, len(text))]
    return [(m.start(1), m.end(1)) for m in STYLE_BLOCK_RE.finditer(text)]


def _blank_outside(text: str, regions: list[tuple[int, int]]) -> str:
    """Blank everything outside the CSS regions, preserving offsets exactly."""
    out = list(_blank_like(text))
    for start, end in regions:
        out[start:end] = list(text[start:end])
    return ''.join(out)


def _liquid_in_comments(css_only: str) -> list[tuple[int, str]]:
    """Markup-injecting Liquid tags sitting inside a CSS comment.

    Liquid does not respect CSS comments — it renders regardless. On
    2026-08-05 a `{% render 'cart-drawer' %}` left inside a comment in
    css-overrides.liquid executed on every page, injecting the whole
    cart-drawer markup into the inlined <style> block (~5KB/page, fixed in
    6279005). Scoped deliberately to render/include/section: those inject
    markup and are never harmless here, whereas `/* color: {{ x }} */` is a
    normal way to comment a declaration out and must not be flagged.

    Must run BEFORE Liquid tags are blanked, or there is nothing left to see.
    """
    hits: list[tuple[int, str]] = []
    i, n = 0, len(css_only)
    while i < n:
        if css_only.startswith('/*', i):
            close = css_only.find('*/', i + 2)
            end = (close + 2) if close >= 0 else n
            for m in LIQUID_INJECT_RE.finditer(css_only, i, end):
                hits.append((m.start(), ' '.join(m.group(0).split())[:60]))
            i = end
            continue
        i += 1
    return hits


def strip_comments_like_a_parser(masked: str) -> tuple[str, list[int]]:
    """Blank each comment by jumping to the FIRST terminator, as a parser does.

    Returns (stripped_text, quoted_terminator_offsets). The quoted offsets are
    terminators wrapped in quotes (`"*/"`) — an author quoting the sequence as
    an example, which is exactly what happened on 2026-08-05.
    """
    out = list(masked)
    quoted: list[int] = []
    i, n = 0, len(masked)
    while i < n:
        if masked.startswith('/*', i):
            close = masked.find('*/', i + 2)
            end = (close + 2) if close >= 0 else n
            if close >= 0:
                prev_ch = masked[close - 1] if close > 0 else ''
                next_ch = masked[close + 2] if close + 2 < n else ''
                # Require BOTH sides quoted. A comment merely ending after a
                # quote (`/* say "hi" */`) is legitimate and must not trip.
                if prev_ch in '"\'' and next_ch in '"\'':
                    quoted.append(close)
            for k in range(i, end):
                if out[k] != '\n':
                    out[k] = ' '
            i = end
            continue
        i += 1
    return ''.join(out), quoted


def _prose_reason(segment: str) -> str | None:
    """Why this selector-position text cannot be a selector.

    Only the text before any `@` is inspected: at-rule preludes such as
    `@media only screen and (max-width: 500px)` are four bare words and would
    otherwise trip every stylesheet in the repo. A genuine leak still shows,
    because the prose sits BEFORE the at-rule that follows it.
    """
    head = segment.split('@', 1)[0]
    if '`' in head:
        return "backtick — not valid in a CSS selector"
    m = PROSE_RUN_RE.search(head)
    if m:
        return f"English prose — {m.group(0).strip()[:60]!r}"
    return None


def scan_file_comments(path: Path) -> list[dict]:
    """Findings for premature comment termination in `path`."""
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        print(f"warn: could not read {path}: {e}", file=sys.stderr)
        return []

    # Blank Liquid comment blocks FIRST (offset-preserving), so a `<style>`
    # mentioned inside one cannot open a bogus CSS region.
    text_nc = LIQUID_COMMENT_RE.sub(lambda m: _blank_like(m.group(0)), text)

    regions = css_regions(path, text_nc)
    if not regions:
        return []

    # CSS regions only, with Liquid still intact — the Liquid-in-comment check
    # has to see the tags before they are blanked for brace scanning.
    css_only = _blank_outside(text_nc, regions)
    injections = _liquid_in_comments(css_only)

    masked = LIQUID_TAG_RE.sub(lambda m: _blank_like(m.group(0)), css_only)
    stripped, quoted_offsets = strip_comments_like_a_parser(masked)

    total_rules = stripped.count('{')
    findings: list[dict] = []

    for off, tag in injections:
        findings.append({
            'path': str(path),
            'line': line_of(text, off),
            'kind': 'liquid-in-comment',
            'detail': f'{tag} sits inside a CSS comment — Liquid does not respect CSS '
                      'comments and will render this into the <style> block',
            'rules_lost': 0,
            'total_rules': total_rules,
        })

    for off in quoted_offsets:
        findings.append({
            'path': str(path),
            'line': line_of(text, off),
            'kind': 'quoted-terminator',
            'detail': 'a CSS comment terminator appears wrapped in quotes, so the '
                      'comment ends HERE and the prose after it is parsed as CSS',
            'rules_lost': max(0, stripped.count('{', off)),
            'total_rules': total_rules,
        })

    # Prose in selector position: the span between the previous {, } or ; and
    # the next {. Checked at every nesting depth, so a leak inside a media
    # query is caught too.
    seg_start = 0
    for m in re.finditer(r'[{};]', stripped):
        if m.group(0) == '{':
            segment = stripped[seg_start:m.start()]
            reason = _prose_reason(segment)
            if reason:
                lead = len(segment) - len(segment.lstrip())
                findings.append({
                    'path': str(path),
                    'line': line_of(text, seg_start + lead),
                    'kind': 'prose-in-selector',
                    'detail': reason,
                    'excerpt': ' '.join(segment.split())[:110],
                    'rules_lost': max(0, stripped.count('{', seg_start)),
                    'total_rules': total_rules,
                })
        seg_start = m.end()

    # Collapse only the LEAK findings to the first one per file: everything
    # downstream of a derailed parser is a consequence of it, and listing 200
    # lines of fallout buries the cause. Liquid-in-comment findings are
    # independent of each other, so every one is reported.
    leaks = [f for f in findings if f['kind'] != 'liquid-in-comment']
    others = [f for f in findings if f['kind'] == 'liquid-in-comment']
    if leaks:
        leaks = [min(leaks, key=lambda f: f['line'])]
    return sorted(others + leaks, key=lambda f: f['line'])


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


def selftest() -> int:
    """Prove the comment-integrity check both fires and stays quiet.

    Fixtures live in scripts/fixtures/ (outside the scanned theme dirs) so the
    two intentionally-broken ones don't fail the repo-wide run. A lint nobody
    tests is a lint that quietly stops working — this is wired into CI.
    """
    fx = Path(__file__).parent / 'fixtures'
    cases = [
        ('comment-leak-quoted.liquid', True,
         'the literal 2026-08-05 defect (terminator quoted as an example)'),
        ('comment-leak-unquoted.liquid', True,
         'unquoted terminator mid-sentence — caught by the prose signal alone'),
        ('liquid-in-comment.liquid', True,
         'sibling bug 6279005 — a render tag inside a CSS comment still executes'),
        ('comment-clean.liquid', False,
         'legal constructs that must NOT false-positive'),
    ]
    failures = 0
    print("comment-integrity selftest (bd hairmnl-theme-w1n6)")
    for name, should_flag, why in cases:
        path = fx / name
        if not path.is_file():
            print(f"  MISSING  {name} — fixture not found")
            failures += 1
            continue
        found = scan_file_comments(path)
        ok = bool(found) == should_flag
        want = 'flag' if should_flag else 'stay quiet'
        got = f"flagged at line {found[0]['line']} ({found[0]['kind']}, "\
              f"{found[0]['rules_lost']}/{found[0]['total_rules']} rules lost)" if found else 'quiet'
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: expected {want}, got {got}")
        print(f"        {why}")
        if not ok:
            failures += 1
    print(f"\n{'selftest OK' if not failures else f'selftest FAILED ({failures})'}")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if '--selftest' in argv:
        return selftest()
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
    comment_findings = []
    for p in sorted(paths):
        all_findings.extend(scan_file(p, list_mode=list_mode))
        comment_findings.extend(scan_file_comments(p))

    violations = [f for f in all_findings if not f['acked']]
    acked = [f for f in all_findings if f['acked']]

    if comment_findings:
        print(f"FAIL: {len(comment_findings)} premature CSS comment termination(s)")
        print("  A CSS comment ends at the FIRST terminator sequence. Everything after")
        print("  it parses as CSS, the parser derails, and the REST OF THE STYLESHEET")
        print("  silently stops applying — with no error anywhere.")
        print("  Reference: bd hairmnl-theme-w1n6 (2026-08-05, 180/206 rules lost on live)")
        print()
        for f in comment_findings:
            print(f"  {f['path']}:{f['line']}  [{f['kind']}]")
            print(f"    {f['detail']}")
            if f.get('excerpt'):
                print(f"    reached selector position: {f['excerpt']}")
            if f['kind'] != 'liquid-in-comment':
                pct = round(100 * f['rules_lost'] / f['total_rules']) if f['total_rules'] else 0
                print(f"    RULES DROPPED FROM HERE: {f['rules_lost']} of {f['total_rules']} ({pct}%)")
            print()
        print("  Fix: describe the terminator sequence in words; never type it inside")
        print("  a comment. Same for Liquid delimiters — Liquid does not respect CSS")
        print("  comments and will execute inside one.")
        print()

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

    if comment_findings:
        return 1

    print(f"OK: scanned {len(paths)} files, no kt0 violations" + (f" ({len(acked)} acked)" if acked else ""))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
