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

    Selectors are matched with their QUALIFIERS, not by rightmost class token (bd gmrm):
    `.text-link.uppercase` does not position a bare `.uppercase`, `.collection-slider .wrapper`
    does not position every `.wrapper`, and `.grid__item[class*="push-"]` does not position a plain
    grid__item. The section schema's `class` is resolved through {% render %} edges so the
    cross-file ancestry Shopify injects on #shopify-section is visible too.

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



# Functional pseudo-classes whose ARGUMENTS must not be read as requirements.
# `.rte:not(.rte--column)` would otherwise parse as "requires class rte--column" — the exact
# inverse of what it means. Stripping :is()/:where()/:has() too is merely permissive.
FUNCTIONAL_PSEUDO_RE = re.compile(r":[a-zA-Z-]+\([^()]*\)")
CLASS_ATTR_RE = re.compile(r"""\[\s*class\s*[*^$~|]?=\s*["']([^"']+)["']\s*\]""", re.I)
COMBINATOR_SPLIT_RE = re.compile(r"\s*[>+~]\s*|\s+")


def parse_position_rules(selector: str, source: str) -> list[dict]:
    """Break a selector into per-target-class REQUIREMENTS.

    The lint's original sin was reducing `.collection-slider .wrapper` to the bare token `wrapper`
    and concluding that every .wrapper in the theme has a containing block. Six of the eleven false
    positives in the 3q2e triage came from exactly that — `.text-link.uppercase`,
    `.grid__item[class*="push-"]` and `.cross-post-blogs .swiper-container` were all read as bare
    class tokens. Every target now carries what else must hold for the rule to match:

      own        other classes required on the SAME element      .text-link.uppercase
      ancestors  classes required on some ANCESTOR               .collection-slider .wrapper
      subs       [class*="..."] fragments required                .grid__item[class*="push-"]
    """
    out: list[dict] = []
    for part in selector.split(","):
        part = part.strip()
        if not part:
            continue
        compounds = [c for c in COMBINATOR_SPLIT_RE.split(part) if c]
        if not compounds:
            continue
        target = compounds[-1]
        is_pseudo = bool(PSEUDO_ELEMENT_RE.search(target))   # before stripping functional pseudos
        subs = CLASS_ATTR_RE.findall(target)
        own_all = set(re.findall(r"\.([A-Za-z_][\w-]*)", FUNCTIONAL_PSEUDO_RE.sub("", target)))
        anc: set[str] = set()
        for comp in compounds[:-1]:
            anc |= set(re.findall(r"\.([A-Za-z_][\w-]*)", FUNCTIONAL_PSEUDO_RE.sub("", comp)))
        for t in own_all:
            out.append({"target": t, "own": own_all - {t}, "ancestors": anc, "subs": subs,
                        "pseudo": is_pseudo, "selector": selector.strip(), "source": source})
    return out


def rule_matches(req: dict, frame: set, outer: set) -> bool:
    """Does this positioning rule match an element with classes `frame` under ancestors `outer`?

    Sibling combinators (+ ~) are folded into `outer`, which is permissive — it can only suppress a
    finding, never invent one.
    """
    if not req["own"] <= frame:
        return False
    if not req["ancestors"] <= outer:
        return False
    return all(any(sub in k for k in frame) for sub in req["subs"])


def nearest_positioned(chain: list, rules_by_class: dict):
    """Walk ancestors innermost -> outermost; return (class, req) of the first one a positioning
    rule genuinely matches, else (None, None)."""
    for i in range(len(chain) - 1, -1, -1):
        frame = chain[i]
        outer: set = set()
        for f in chain[:i]:
            outer |= f
        for c in sorted(frame):
            for req in rules_by_class.get(c, ()):
                if rule_matches(req, frame, outer):
                    return c, req
    return None, None


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


def ancestor_map(markup: str) -> dict[str, list[tuple[list, set]]]:
    """class token -> LIST of (ancestor_chain, own_frame), one entry per occurrence in this file.

    `ancestor_chain` is ordered OUTERMOST -> innermost and excludes the element itself; `own_frame`
    is the element's own class set. Both are needed now that rules carry requirements: `own` is
    evaluated against the element's own frame (`.text-link.uppercase`) and `ancestors` against the
    frames outside it (`.collection-slider .wrapper`).

    A tag-stack walker. Cross-file nesting is invisible here and is supplied separately by
    build_outer_context().

    PER-OCCURRENCE, NOT UNIONED — this distinction is the whole point. `.hero__content__wrapper`
    appears both inside `.article__card.section--image` (which critical CSS positions, so it is
    fine) and inside `.brick__block` (which only the deferred sheet positions — the dh8x bug).
    Unioning the two contexts let the safe one mask the broken one, and an early version of this
    lint consequently failed to reproduce dh8x. Every occurrence is judged on its own.
    """
    out: dict[str, list[tuple[list, set]]] = {}
    stack: list[set] = []
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
            chain = [set(f) for f in stack]
            for c in cls:
                out.setdefault(c, []).append((chain, set(cls)))
        if tag not in VOID_TAGS and not selfclose:
            stack.append(cls)
    return out


SCHEMA_BLOCK_RE = re.compile(r"\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}", re.DOTALL)
SCHEMA_CLASS_RE = re.compile(r'"class"\s*:\s*"([^"]+)"')
RENDER_RE = re.compile(r"\{%-?\s*(?:render|include)\s+(?:'([^']+)'|\"([^\"]+)\")")


def build_outer_context(texts: dict[str, str]) -> dict[str, set]:
    """rel-path -> class tokens contributed by ancestors that live OUTSIDE the file.

    Two sources the tag walker cannot see:
      1. Shopify wraps each section in <div id="shopify-section-..." class="shopify-section {the
         schema's "class"}">. That wrapper is an ancestor of everything in the file.
      2. A snippet is nested inside whichever section renders it.

    This matters for correctness in BOTH directions. Without it `.collection-slider .wrapper` looks
    unsatisfiable inside snippets/collection-slider.liquid, and the REAL swiper-button-*/wrapper
    finding (fixed under 3q2e) would come back as a false positive. With it,
    sections/collection-branded.liquid — which copies the same markup but declares no schema class —
    correctly does NOT get the containing block.

    A snippet inherits the UNION of the schema classes of every section that can reach it. That is
    permissive by construction: it can suppress a finding for a caller that does not carry the
    class, never invent one.
    """
    own: dict[str, set] = {}
    renders: dict[str, set] = {}
    for rel, text in texts.items():
        tokens: set = set()
        m = SCHEMA_BLOCK_RE.search(text)
        if m:
            for cm in SCHEMA_CLASS_RE.finditer(m.group(1)):
                tokens |= {t for t in cm.group(1).split()
                           if re.fullmatch(r"[A-Za-z_][\w-]*", t)}
        own[rel] = tokens
        renders[rel] = {a or b for a, b in RENDER_RE.findall(text)}

    by_name = {Path(rel).stem: rel for rel in texts if rel.startswith("snippets/")}
    ctx: dict[str, set] = {rel: set(own.get(rel, ())) for rel in texts}
    for rel, tokens in own.items():
        if not tokens:
            continue
        seen: set = set()
        stack = list(renders.get(rel, ()))
        while stack:                                  # transitive: section -> snippet -> snippet
            target = by_name.get(stack.pop())
            if not target or target in seen:
                continue
            seen.add(target)
            ctx[target] |= tokens
            stack.extend(renders.get(target, ()))
    return ctx


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
    crit_pos_rules: dict[str, list] = {}         # class -> positioning rules WITH requirements
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
            for req in parse_position_rules(selector, CRITICAL.name):
                if not req["pseudo"]:      # a pseudo box is positioned, not its originating element
                    crit_pos_rules.setdefault(req["target"], []).append(req)
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

    # deferred sheets: which classes get positioned there, and under what conditions
    deferred_pos_rules: dict[str, list] = {}
    for pattern in DEFERRED_GLOBS:
        for path in sorted((REPO / "assets").glob(pattern)):
            if ".dev." in path.name:
                continue
            for selector, body in iter_rules(path.read_text(encoding="utf-8", errors="replace")):
                if decl_map(body).get("position", "") in POSITIONED_VALUES:
                    for req in parse_position_rules(selector, path.name):
                        if not req["pseudo"]:
                            deferred_pos_rules.setdefault(req["target"], []).append(req)

    # ancestor chains from markup, plus the cross-file context the walker cannot see
    texts: dict[str, str] = {}
    for d in MARKUP_DIRS:
        for path in sorted((REPO / d).rglob("*.liquid")):
            texts[str(path.relative_to(REPO))] = path.read_text(encoding="utf-8", errors="replace")
    outer_ctx = build_outer_context(texts)
    ancestors: dict[str, list[tuple[str, list, set]]] = {}
    for rel, text in texts.items():
        for cls, occurrences in ancestor_map(text).items():
            ancestors.setdefault(cls, []).extend(
                (rel, chain, own) for chain, own in occurrences)

    if verbose:
        print(f"  critical rules parsed      : {len(crit_rules)}")
        print(f"  critical position:absolute : {len(crit_abs)}")
        print(f"  critical positioned classes: {len(crit_pos_rules)}")
        print(f"  deferred positioned classes: {len(deferred_pos_rules)}")
        print(f"  files with outer context   : "
              f"{sum(1 for v in outer_ctx.values() if v)}")
        print(f"  classes with ancestry      : {len(ancestors)}")

    allow = load_allowlist()
    findings = []

    # RULE 1 — orphaned absolute positioning
    seen_pairs: set[tuple[str, str]] = set()
    for cls, (selector, from_pseudo) in sorted(crit_abs.items()):
        for rel, chain, own in ancestors.get(cls, []):
            # Outermost frame = classes contributed from outside the file (section schema class,
            # and the schema class of whatever section renders this snippet). A pseudo-element is
            # laid out inside its OWN originating element, so that element joins the chain too —
            # without it, `.x:after{position:absolute}` next to `.x{position:relative}` would be
            # reported as a bug that cannot happen.
            eff_chain = [set(outer_ctx.get(rel, ()))] + chain + ([own] if from_pseudo else [])
            if not any(eff_chain):
                continue                               # no observed ancestry; can't judge
            if nearest_positioned(eff_chain, crit_pos_rules)[0]:
                continue                               # containing block exists at first paint
            late, req = nearest_positioned(eff_chain, deferred_pos_rules)
            if not late:
                continue
            # Key on the PAIR, not the class. `.hero__content__wrapper` is broken under
            # `.brick__block` (dh8x) but fine elsewhere — a bare-class allowlist entry for one
            # occurrence would silently un-guard the other.
            if (cls, late) in seen_pairs:
                continue
            seen_pairs.add((cls, late))
            if cls in allow or f"{cls}/{late}" in allow:
                continue
            findings.append({
                "rule": "orphaned-absolute",
                "cls": cls,
                "selector": selector,
                "where": rel,
                "detail": (f"position:absolute in critical CSS, but at this occurrence its "
                           f"containing block comes from `{req['selector'][:70]}` which ships "
                           f"only in {req['source']} (deferred)"),
                "fix": (f"add a matching position rule for .{late} to critical-css.liquid "
                        f"(mirror the deferred declaration exactly so final rendering is unchanged)"),
                "key": f"{cls}/{late}",
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
        ("ccc-qualified-compound", False,
         "bd gmrm: `.text-link.uppercase` must not position a plain `.uppercase` element"),
        ("ccc-qualified-descendant", False,
         "bd gmrm: `.cross-post-blogs .swiper-container` must not match without that ancestor"),
        ("ccc-qualified-descendant-hit", True,
         "...but the same rule MUST fire once the qualifying ancestor is present"),
        ("ccc-qualified-attribute", False,
         'bd gmrm: `.grid__item[class*="push-"]` must not match a plain grid__item'),
        ("ccc-schema-class", True,
         "bd gmrm: the containing block comes from the section schema `class`, unseen by the walker"),
        ("ccc-schema-class-fixed", False,
         "...and is silent once that ancestor is positioned by critical CSS"),
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
    crit_abs: dict[str, tuple[str, bool]] = {}
    crit_pos_rules: dict[str, list] = {}
    crit_font_size, crit_font_family, crit_font_shorthand = set(), set(), set()
    font_unit_hits = []
    for selector, body in iter_rules(critical_css):
        decls, cls = decl_map(body), classes_in_selector(selector)
        acked = ACK_TOKEN in body or ACK_TOKEN in selector
        pos = decls.get("position", "")
        if pos in POSITIONED_VALUES:
            for req in parse_position_rules(selector, "critical"):
                if not req["pseudo"]:
                    crit_pos_rules.setdefault(req["target"], []).append(req)
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
    deferred_pos_rules: dict[str, list] = {}
    for selector, body in iter_rules(deferred_css):
        if decl_map(body).get("position", "") in POSITIONED_VALUES:
            for req in parse_position_rules(selector, "deferred.css"):
                if not req["pseudo"]:
                    deferred_pos_rules.setdefault(req["target"], []).append(req)
    outer = build_outer_context({"fixture.liquid": markup}).get("fixture.liquid", set())
    ancestors = ancestor_map(markup)
    out = []
    for cls, (selector, from_pseudo) in sorted(crit_abs.items()):
        for chain, own in ancestors.get(cls, []):
            eff = [set(outer)] + chain + ([own] if from_pseudo else [])
            if not any(eff):
                continue
            if nearest_positioned(eff, crit_pos_rules)[0]:
                continue
            late, _ = nearest_positioned(eff, deferred_pos_rules)
            if late:
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
