#!/usr/bin/env python3
"""critical-CSS coverage lint — catch first-paint geometry that depends on DEFERRED CSS.

WHY THIS EXISTS (bd hairmnl-theme-958r.6)
-----------------------------------------
This theme inlines `snippets/critical-css.liquid` into <style> in <head>, and defers every
other stylesheet via `media="print" onload="this.media='all'"` (layout/theme.liquid ~L537+).
So at FIRST PAINT the page is styled by critical CSS *alone*.

That split has now produced three separate live CLS bugs in one week, all the same shape:
a rule that first paint needs lives only in a deferred sheet.

  - dh8x (2026-08-05, CLS 2.011 on brand mobile): critical CSS inlined
    `.hero__content__wrapper{position:absolute;top:0;left:0;width:100%;height:100%}` but the
    ONLY rule positioning its ancestor, `.brick__block{position:relative}`, shipped in the
    deferred assets/theme-collection.css. Until that sheet applied, the wrapper had no
    positioned ancestor, resolved against the INITIAL CONTAINING BLOCK, and painted
    full-viewport at (0,0) — then snapped to its real place. impact 1.0 x distance 1.0 = a
    layout-shift score of exactly 1.0000.
  - wscl (2026-08-05): the header points-box reservation was `min-width: 6ch`. `ch` is
    FONT-relative, and `.navtext`'s font-family/font-size live only in deferred
    theme-core.css — so 1ch was the UA serif at 16px (6ch = 48px) until the sheet landed,
    then Questrial at 12px (6ch = 39.6px). The reservation itself shrank ~8px every cold load.
  - nahn.4 (2026-08-05): blog `.center` alignment + `.rte` font scale lived only in deferred
    sheets, so above-fold article text reflowed when they applied.

WHAT IT CHECKS (deliberately narrow — two mechanisms, not "all geometry")
-------------------------------------------------------------------------
A generic "any geometry rule missing from critical CSS" check would flag thousands of rules
and be ignored within a week. These two rules encode the exact failure modes above and are
meant to stay near-zero-noise:

  RULE 1 — ORPHANED ABSOLUTE POSITIONING (the dh8x shape)
    For every selector that critical CSS gives `position:absolute`, walk the theme markup to
    find that element's ancestors (same file). If NO ancestor is positioned by critical CSS,
    but SOME ancestor is positioned by a DEFERRED sheet, the containing block does not exist
    at first paint => flag.

    Pseudo-element rules (::before/::after) are chained through their ORIGINATING element, which
    is where their box is laid out — `.x:after{position:absolute}` is safe whenever `.x` itself is
    positioned by critical CSS.

  RULE 2 — FONT-RELATIVE SIZING WITHOUT A FONT (the wscl shape)
    For every critical-CSS sizing declaration (width/height/min-/max-) whose value uses a
    font-relative unit that depends on the ELEMENT's own font (`ch`, `em`, `ex`), require that
    critical CSS also sets font-size (and, for `ch`/`ex`, font-family) on that same selector.
    `rem`/`vw`/`vh`/`%`/`px` are exempt — `rem` keys off html{font-size}, which critical CSS
    does declare.

Acknowledging a finding
-----------------------
Some hits are legitimate (e.g. an element that is genuinely below the fold and can afford to
settle late). Acknowledge inline, in the rule body, with the literal token `ccc-OK`:

    .thing { /* ccc-OK: below the fold, never in the first viewport */
      position: absolute;
    }

or allowlist it in os2-migration/critical-css-coverage-allow.txt with a bd id and reason.
Allowlist keys are SCOPED, not per-class:
    hero__content__wrapper/brick__block   rule 1 — this class under this late-positioned ancestor
    navtext/min-width                     rule 2 — this class's declaration of this property
A bare class token still works as a deliberate blanket entry, but prefer the scoped form: the
same class is often broken in one context and fine in another (`.hero__content__wrapper` is the
dh8x bug under `.brick__block` and perfectly safe under `.section--image`), and a blanket entry
would silently un-guard the broken context. Always give a justification.

Usage:
    python3 scripts/check-critical-css-coverage.py            # scan the repo
    python3 scripts/check-critical-css-coverage.py --selftest # prove it fires and stays quiet
    python3 scripts/check-critical-css-coverage.py --verbose  # show what was parsed

Exit 0 = clean, 1 = at least one unacknowledged finding.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CRITICAL = REPO / "snippets" / "critical-css.liquid"
ALLOWLIST = REPO / "os2-migration" / "critical-css-coverage-allow.txt"
ACK_TOKEN = "ccc-OK"

# Stylesheets that are DEFERRED by layout/theme.liquid (media=print + onload swap).
# theme.css / custom-theme.css are the pre-split monoliths, kept for reference.
DEFERRED_GLOBS = ("theme-*.css", "custom-theme-*.css", "theme.css", "custom-theme.css")

# Markup we walk for ancestor chains. Layout + sections + snippets is where this theme's
# server-rendered structure lives.
MARKUP_DIRS = ("layout", "sections", "snippets")

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}

# Font-relative units that resolve against the ELEMENT's own font. `rem` is excluded on
# purpose: it keys off html{font-size}, which critical CSS declares.
ELEMENT_FONT_UNITS = ("ch", "ex", "em")
SIZING_PROPS = ("width", "min-width", "max-width", "height", "min-height", "max-height")

POSITIONED_VALUES = ("relative", "absolute", "fixed", "sticky")


# --------------------------------------------------------------------------- CSS parsing

def strip_comments(css: str) -> str:
    """Remove /* ... */ comments but keep byte offsets stable-ish (replace with spaces)."""
    return re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), css, flags=re.DOTALL)


def iter_rules(css: str):
    """Yield (selector_text, body_text) for each declaration block.

    Naive brace walker, same spirit as check-overlay-css.py. Descends into @media/@supports
    (their bodies contain real rules) and skips @keyframes (percentage 'selectors' are not
    element selectors and would produce noise).
    """
    src = strip_comments(css)
    i, n = 0, len(src)
    sel_start = 0
    while i < n:
        ch = src[i]
        if ch == "{":
            selector = src[sel_start:i].strip()
            depth = 1
            j = i + 1
            while j < n and depth:
                if src[j] == "{":
                    depth += 1
                elif src[j] == "}":
                    depth -= 1
                j += 1
            body = src[i + 1:j - 1]
            at = selector.lstrip().lower()
            if at.startswith("@keyframes") or at.startswith("@-webkit-keyframes"):
                pass                                    # ignore keyframe stops entirely
            elif at.startswith("@"):
                yield from iter_rules(body)             # descend into media/supports
            else:
                yield selector, body
            i = j
            sel_start = i
            continue
        if ch == "}":
            sel_start = i + 1
        i += 1


def classes_in_selector(selector: str) -> set[str]:
    """Class tokens targeted by the RIGHTMOST compound of each comma-separated selector.

    `.a .b { }` styles `.b`, not `.a` — taking every class in the string would badly
    over-attribute (and would have made dh8x look already-covered).
    """
    out: set[str] = set()
    for part in selector.split(","):
        part = part.strip()
        if not part:
            continue
        # rightmost compound: split on descendant/child/sibling combinators
        last = re.split(r"\s+|>|\+|~", part)[-1]
        out.update(re.findall(r"\.([A-Za-z_][\w-]*)", last))
    return out


# Pseudo-ELEMENTS only. Pseudo-CLASSES (:hover, :focus, :not(...)) still target the element
# itself and change nothing about containing blocks, so they must NOT match here.
PSEUDO_ELEMENT_RE = re.compile(
    r"::[a-zA-Z-]+"
    r"|:(?:before|after|first-line|first-letter|marker|placeholder|selection|backdrop)\b",
    re.IGNORECASE)


def classes_in_selector_scoped(selector: str) -> list[tuple[str, bool]]:
    """(class, targets_a_pseudo_element) per rightmost compound of each comma-separated part.

    A ::before/::after box is laid out INSIDE its originating element, so its containing block is
    that element whenever the element is itself positioned. `.home__subtitle:after{position:absolute}`
    is therefore perfectly safe next to `.home__subtitle{position:relative}` — and reporting it was a
    false positive in the first version of this lint, which stripped `:after` and attributed the
    pseudo's `position:absolute` to the class.
    """
    out: list[tuple[str, bool]] = []
    for part in selector.split(","):
        part = part.strip()
        if not part:
            continue
        last = re.split(r"\s+|>|\+|~", part)[-1]
        is_pseudo = bool(PSEUDO_ELEMENT_RE.search(last))
        for c in re.findall(r"\.([A-Za-z_][\w-]*)", last):
            out.append((c, is_pseudo))
    return out


def positioning_classes(selector: str) -> set[str]:
    """Classes that a `position:` declaration on this selector actually makes into a containing
    block — i.e. excluding pseudo-element rules, which position the pseudo box, not the element.
    """
    return {c for c, is_pseudo in classes_in_selector_scoped(selector) if not is_pseudo}


def decl_map(body: str) -> dict[str, str]:
    """property -> value (last wins), lowercased property."""
    out: dict[str, str] = {}
    for decl in body.split(";"):
        if ":" not in decl:
            continue
        prop, _, val = decl.partition(":")
        p = prop.strip().lower()
        if p and not p.startswith("--"):
            out[p] = val.strip().lower()
    return out


# ----------------------------------------------------------------------- markup ancestry

def strip_liquid(markup: str) -> str:
    """Remove liquid tags/output and HTML comments so the tag walker sees plain markup."""
    markup = re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", " ",
                    markup, flags=re.DOTALL | re.IGNORECASE)
    markup = re.sub(r"<!--.*?-->", " ", markup, flags=re.DOTALL)
    markup = re.sub(r"\{%.*?%\}", " ", markup, flags=re.DOTALL)
    markup = re.sub(r"\{\{.*?\}\}", " ", markup, flags=re.DOTALL)
    return markup


TAG_RE = re.compile(r"<(/?)([a-zA-Z][\w-]*)([^>]*?)(/?)>", re.DOTALL)
CLASS_RE = re.compile(r"""class\s*=\s*("([^"]*)"|'([^']*)')""", re.IGNORECASE)


def ancestor_map(markup: str) -> dict[str, list[set[str]]]:
    """class token -> LIST of ancestor-class sets, one entry per occurrence in this file.

    A tag-stack walker. Cross-file nesting is invisible (a snippet's root is a child of
    whatever rendered it), which is a known blind spot — but the bugs this targets have all
    been same-file, because the wrapper and its positioned parent live in one section.

    PER-OCCURRENCE, NOT UNIONED — this distinction is the whole point. `.hero__content__wrapper`
    appears both inside `.article__card.section--image` (which critical CSS positions, so it is
    fine) and inside `.brick__block` (which only the deferred sheet positions — the dh8x bug).
    Unioning the two contexts let the safe one mask the broken one, and an early version of this
    lint consequently failed to reproduce dh8x. Every occurrence is now judged on its own.
    """
    out: dict[str, list[set[str]]] = {}
    stack: list[set[str]] = []
    for m in TAG_RE.finditer(strip_liquid(markup)):
        closing, tag, attrs, selfclose = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        if closing:
            if stack:
                stack.pop()
            continue
        cm = CLASS_RE.search(attrs)
        raw = (cm.group(2) or cm.group(3) or "") if cm else ""
        cls = {c for c in raw.split() if re.fullmatch(r"[A-Za-z_][\w-]*", c)}
        if cls:
            inherited: set[str] = set()
            for frame in stack:
                inherited |= frame
            for c in cls:
                out.setdefault(c, []).append(inherited)
        if tag not in VOID_TAGS and not selfclose:
            stack.append(cls)
    return out


# ---------------------------------------------------------------------------- allowlist

def load_allowlist() -> dict[str, str]:
    allow: dict[str, str] = {}
    if not ALLOWLIST.is_file():
        return allow
    for raw in ALLOWLIST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 2)
        if len(parts) < 3:
            print(f"warn: {ALLOWLIST.name}: skipping malformed row: {raw!r}", file=sys.stderr)
            continue
        allow[parts[0]] = f"{parts[1]} — {parts[2]}"
    return allow


# --------------------------------------------------------------------------------- scan

def scan(verbose: bool = False):
    if not CRITICAL.is_file():
        print(f"ERROR: {CRITICAL} not found", file=sys.stderr)
        return [], {}

    critical_css = CRITICAL.read_text(encoding="utf-8", errors="replace")
    crit_rules = list(iter_rules(critical_css))

    crit_abs: dict[str, tuple[str, bool]] = {}   # class -> (selector, from_pseudo_element)
    crit_positioned: set[str] = set()
    crit_font_size: set[str] = set()
    crit_font_family: set[str] = set()
    crit_font_shorthand: set[str] = set()
    font_unit_hits: list[tuple[str, str, str, str]] = []   # class, prop, value, selector

    for selector, body in crit_rules:
        decls = decl_map(body)
        cls = classes_in_selector(selector)
        acked = ACK_TOKEN in body or ACK_TOKEN in selector
        pos = decls.get("position", "")
        if pos in POSITIONED_VALUES:
            crit_positioned |= positioning_classes(selector)
        if pos == "absolute" and not acked:
            for c, is_pseudo in classes_in_selector_scoped(selector):
                prev = crit_abs.get(c)
                if prev is None or (prev[1] and not is_pseudo):
                    crit_abs[c] = (selector.strip(), is_pseudo)
        if "font-size" in decls:
            crit_font_size |= cls
        if "font-family" in decls:
            crit_font_family |= cls
        if "font" in decls:
            crit_font_shorthand |= cls
        if not acked:
            for prop in SIZING_PROPS:
                val = decls.get(prop)
                if not val:
                    continue
                if re.search(r"\d\s*(" + "|".join(ELEMENT_FONT_UNITS) + r")\b", val):
                    for c in cls:
                        font_unit_hits.append((c, prop, val, selector.strip()))

    # deferred sheets: which classes get positioned there
    deferred_positioned: dict[str, str] = {}
    for pattern in DEFERRED_GLOBS:
        for path in sorted((REPO / "assets").glob(pattern)):
            if ".dev." in path.name:
                continue
            for selector, body in iter_rules(path.read_text(encoding="utf-8", errors="replace")):
                if decl_map(body).get("position", "") in POSITIONED_VALUES:
                    for c in positioning_classes(selector):
                        deferred_positioned.setdefault(c, path.name)

    # ancestor chains from markup
    ancestors: dict[str, list[tuple[str, set[str]]]] = {}
    for d in MARKUP_DIRS:
        for path in sorted((REPO / d).rglob("*.liquid")):
            rel = str(path.relative_to(REPO))
            for cls, occurrences in ancestor_map(
                path.read_text(encoding="utf-8", errors="replace")
            ).items():
                ancestors.setdefault(cls, []).extend((rel, anc) for anc in occurrences)

    if verbose:
        print(f"  critical rules parsed      : {len(crit_rules)}")
        print(f"  critical position:absolute : {len(crit_abs)}")
        print(f"  critical positioned classes: {len(crit_positioned)}")
        print(f"  deferred positioned classes: {len(deferred_positioned)}")
        print(f"  classes with ancestry      : {len(ancestors)}")

    allow = load_allowlist()
    findings = []

    # RULE 1 — orphaned absolute positioning
    seen_pairs: set[tuple[str, str]] = set()
    for cls, (selector, from_pseudo) in sorted(crit_abs.items()):
        for rel, anc in ancestors.get(cls, []):
            # A pseudo-element is contained by its OWN originating element, so that element joins
            # the containing-block chain. Without this, `.x:after{position:absolute}` next to
            # `.x{position:relative}` reports a bug that cannot happen.
            chain = anc | ({cls} if from_pseudo else set())
            if not chain:
                continue                               # no observed ancestry; can't judge
            if chain & crit_positioned:
                continue                               # containing block exists at first paint
            late = sorted(a for a in chain if a in deferred_positioned)
            if not late:
                continue
            # Key on the PAIR, not the class. `.hero__content__wrapper` is broken under
            # `.brick__block` (dh8x) but fine elsewhere — a bare-class allowlist entry for one
            # occurrence would silently un-guard the other.
            if (cls, late[0]) in seen_pairs:
                continue
            seen_pairs.add((cls, late[0]))
            if cls in allow or f"{cls}/{late[0]}" in allow:
                continue
            findings.append({
                "rule": "orphaned-absolute",
                "cls": cls,
                "selector": selector,
                "where": rel,
                "detail": (f"position:absolute in critical CSS, but at this occurrence its "
                           f"containing block comes from .{late[0]} {{position:…}} which ships "
                           f"only in {deferred_positioned[late[0]]} (deferred)"),
                "fix": (f"add a matching position rule for .{late[0]} to critical-css.liquid "
                        f"(mirror the deferred declaration exactly so final rendering is unchanged)"),
                "key": f"{cls}/{late[0]}",
            })

    # RULE 2 — font-relative sizing without a font in critical CSS
    for cls, prop, val, selector in sorted(set(font_unit_hits)):
        if cls in allow or f"{cls}/{prop}" in allow:
            continue
        has_size = cls in crit_font_size or cls in crit_font_shorthand
        has_family = cls in crit_font_family or cls in crit_font_shorthand
        unit = next((u for u in ELEMENT_FONT_UNITS
                     if re.search(r"\d\s*" + u + r"\b", val)), "?")
        needs_family = unit in ("ch", "ex")
        if has_size and (has_family or not needs_family):
            continue
        missing = []
        if not has_size:
            missing.append("font-size")
        if needs_family and not has_family:
            missing.append("font-family")
        findings.append({
            "rule": "font-relative-sizing",
            "cls": cls,
            "selector": selector,
            "detail": (f"{prop}: {val} uses '{unit}', which resolves against the element's own "
                       f"font, but critical CSS does not set {' and '.join(missing)} for .{cls} "
                       f"— so this size changes when the deferred sheet lands"),
            "fix": (f"either use an absolute unit (px) or also declare "
                    f"{' and '.join(missing)} for .{cls} in critical-css.liquid"),
            "key": f"{cls}/{prop}",
        })

    return findings, allow


# ----------------------------------------------------------------------------- selftest

def selftest() -> int:
    """Prove both rules fire on the real historical defects and stay quiet on the fix.

    A lint nobody tests is a lint that quietly stops working. These fixtures are literal
    reductions of dh8x and wscl.
    """
    fx = Path(__file__).parent / "fixtures"
    cases = [
        ("ccc-orphan-absolute", True,
         "dh8x: .hero__content__wrapper absolute in critical, .brick__block relative only in deferred"),
        ("ccc-orphan-absolute-fixed", False,
         "same markup once the containing block is mirrored into critical CSS"),
        ("ccc-font-relative", True,
         "wscl: min-width in ch with no font-size/font-family in critical CSS"),
        ("ccc-font-relative-fixed", False,
         "same reservation expressed in px"),
        ("ccc-pseudo-element", False,
         "a ::after is contained by its own originating element — must NOT be reported"),
        ("ccc-pseudo-element-orphan", True,
         "...but a ::after whose base element is unpositioned IS genuinely orphaned"),
    ]
    failures = 0
    print("critical-css coverage selftest (bd hairmnl-theme-958r.6)")
    for name, should_flag, why in cases:
        crit = fx / f"{name}.critical.css"
        defr = fx / f"{name}.deferred.css"
        mark = fx / f"{name}.markup.liquid"
        if not crit.is_file():
            print(f"  MISSING  {name} — fixture not found")
            failures += 1
            continue
        found = scan_fixture(
            crit.read_text(encoding="utf-8"),
            defr.read_text(encoding="utf-8") if defr.is_file() else "",
            mark.read_text(encoding="utf-8") if mark.is_file() else "",
        )
        ok = bool(found) == should_flag
        got = f"flagged ({found[0]['rule']} on .{found[0]['cls']})" if found else "quiet"
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: expected "
              f"{'flag' if should_flag else 'stay quiet'}, got {got}")
        print(f"        {why}")
        if not ok:
            failures += 1
    print(f"\n{'selftest OK' if not failures else f'selftest FAILED ({failures})'}")
    return 1 if failures else 0


def scan_fixture(critical_css: str, deferred_css: str, markup: str):
    """Same logic as scan(), over in-memory strings. Kept in step with scan() by selftest."""
    crit_abs, crit_positioned = {}, set()
    crit_font_size, crit_font_family, crit_font_shorthand = set(), set(), set()
    font_unit_hits = []
    for selector, body in iter_rules(critical_css):
        decls, cls = decl_map(body), classes_in_selector(selector)
        acked = ACK_TOKEN in body or ACK_TOKEN in selector
        pos = decls.get("position", "")
        if pos in POSITIONED_VALUES:
            crit_positioned |= positioning_classes(selector)
        if pos == "absolute" and not acked:
            for c, is_pseudo in classes_in_selector_scoped(selector):
                prev = crit_abs.get(c)
                if prev is None or (prev[1] and not is_pseudo):
                    crit_abs[c] = (selector.strip(), is_pseudo)
        if "font-size" in decls:
            crit_font_size |= cls
        if "font-family" in decls:
            crit_font_family |= cls
        if "font" in decls:
            crit_font_shorthand |= cls
        if not acked:
            for prop in SIZING_PROPS:
                val = decls.get(prop)
                if val and re.search(r"\d\s*(" + "|".join(ELEMENT_FONT_UNITS) + r")\b", val):
                    for c in cls:
                        font_unit_hits.append((c, prop, val, selector.strip()))
    deferred_positioned = {}
    for selector, body in iter_rules(deferred_css):
        if decl_map(body).get("position", "") in POSITIONED_VALUES:
            for c in positioning_classes(selector):
                deferred_positioned.setdefault(c, "deferred.css")
    ancestors = ancestor_map(markup)
    out = []
    for cls, (selector, from_pseudo) in sorted(crit_abs.items()):
        for anc in ancestors.get(cls, []):
            chain = anc | ({cls} if from_pseudo else set())
            if chain and not (chain & crit_positioned) and any(a in deferred_positioned for a in chain):
                out.append({"rule": "orphaned-absolute", "cls": cls, "selector": selector})
                break
    for cls, prop, val, selector in sorted(set(font_unit_hits)):
        has_size = cls in crit_font_size or cls in crit_font_shorthand
        has_family = cls in crit_font_family or cls in crit_font_shorthand
        unit = next((u for u in ELEMENT_FONT_UNITS if re.search(r"\d\s*" + u + r"\b", val)), "?")
        if has_size and (has_family or unit not in ("ch", "ex")):
            continue
        out.append({"rule": "font-relative-sizing", "cls": cls, "selector": selector})
    return out


# --------------------------------------------------------------------------------- main

def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    verbose = "--verbose" in argv
    findings, allow = scan(verbose=verbose)

    if not findings:
        print(f"OK: critical-CSS coverage clean "
              f"({len(allow)} allowlisted selector(s))")
        return 0

    print(f"FAIL: {len(findings)} unacknowledged critical-CSS coverage finding(s)\n")
    print("These break FIRST PAINT only: the page is styled by snippets/critical-css.liquid")
    print("alone until the deferred sheets swap in, so anything below settles late and shifts.\n")
    for f in findings:
        print(f"  [{f['rule']}] .{f['cls']}")
        print(f"      selector : {f['selector'][:110]}")
        if f.get("where"):
            print(f"      seen in  : {f['where']}")
        print(f"      problem  : {f['detail']}")
        print(f"      fix      : {f['fix']}")
        print(f"      or ack   : add a /* {ACK_TOKEN}: <why it is safe> */ comment in the rule body,")
        print(f"                 or allowlist `{f['key']}` in {ALLOWLIST.name}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
