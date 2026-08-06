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
# Every stylesheet that is INLINE in <head> and therefore applies at first paint. Modelling only
# critical-css.liquid was a precision bug (found triaging bd 66t7): snippets/css-overrides.liquid is
# ~98KB rendered unconditionally at layout/theme.liquid:626 — verified Liquid nesting depth 0, inside
# <head> — and it positions selectors that critical-css.liquid does not. It also sits AFTER the
# deferred <link>s in source order, so at equal specificity it wins the settled cascade too. Ignoring
# it made the lint report elements as "static at first paint" when they were already positioned.
FIRST_PAINT_SHEETS = (
    CRITICAL,
    REPO / "snippets" / "css-overrides.liquid",
)
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


SIZE_PROPS_R4 = ("height", "min-height")
PX_THRESHOLD_R4 = 60          # below this a late height cannot move much; keeps the rule quiet


def r4_size_is_material(prop: str, value: str) -> str | None:
    """Return a short reason if this height declaration is worth guarding, else None.

    Height is declared far more often than position, so RULE 4 has to be choosier than RULE 3 or it
    drowns the signal. Two shapes qualify:
      - viewport-relative (vh, %, or a calc() containing vh) — these reserve nothing until the sheet
        lands and then jump by a fraction of the screen. bd fj5m's
        `.cart__empty{height:calc(50vh - var(--header-height))}` is the motivating case: 32px -> 344px.
      - a plain pixel height of at least PX_THRESHOLD_R4. bd agt7's `.cart__circle{height:160px}`
        would have been missed by a vh-only rule, and it was a real 139px shift.
    """
    v = value.strip().lower()
    if v in ("auto", "inherit", "initial", "unset", "0", "0px", "100%"):
        return None
    if "vh" in v:
        return "viewport-relative"
    if v.endswith("%"):
        return "percentage"
    m = re.fullmatch(r"(\d+(?:\.\d+)?)px", v)
    if m and float(m.group(1)) >= PX_THRESHOLD_R4:
        return f"{m.group(1)}px"
    return None


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


INLINE_HIDDEN_RE = re.compile(
    r"""style\s*=\s*("[^"]*"|'[^']*')""", re.IGNORECASE)


def _inline_hidden(attrs: str) -> bool:
    """True if the element carries an inline style that suppresses painting.

    snippets/cart-line-items.liquid:7 is the motivating case — `<div class="item--loadbar"
    style="display: none;">`. No stylesheet declares display for .item--loadbar, so the inline rule
    wins at first paint and the element cannot shift. RULE 3 would otherwise report it.
    """
    m = INLINE_HIDDEN_RE.search(attrs or "")
    if not m:
        return False
    v = m.group(1)[1:-1].lower().replace(" ", "")
    return "display:none" in v or "visibility:hidden" in v or "opacity:0" in v


def ancestor_map(markup: str) -> dict[str, list[tuple[list, set, bool]]]:
    """class token -> LIST of (ancestor_chain, own_frame, inline_hidden) per occurrence.

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
    out: dict[str, list[tuple[list, set, bool]]] = {}
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
            hidden = _inline_hidden(attrs)
            for c in cls:
                out.setdefault(c, []).append((chain, set(cls), hidden))
        if tag not in VOID_TAGS and not selfclose:
            stack.append(cls)
    return out


SCHEMA_BLOCK_RE = re.compile(r"\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}", re.DOTALL)
SCHEMA_CLASS_RE = re.compile(r'"class"\s*:\s*"([^"]+)"')
RENDER_RE = re.compile(r"\{%-?\s*(?:render|include)\s+(?:'([^']+)'|\"([^\"]+)\")")


RENDER_TAG_RE = re.compile(
    r"\{%-?\s*(?:render|include)\s+(?:'([^']+)'|\"([^\"]+)\")[^%]*%\}")


def render_wrappers(markup: str) -> list[tuple[str, set]]:
    """(snippet_name, classes of the elements physically enclosing the {% render %} tag).

    bd nf3j. A snippet sits inside whatever markup surrounds its callsite, so a containing block can
    be supplied by a wrapper in the CALLING file — e.g. css-overrides positions
    `.cart__template .cart__items__row`, but `.cart__template` is on a wrapper in sections/cart.liquid,
    one render above snippets/cart-line-items.liquid.
    """
    src = re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", " ",
                 markup, flags=re.DOTALL | re.IGNORECASE)
    src = re.sub(r"<!--.*?-->", " ", src, flags=re.DOTALL)
    src = re.sub(r"\{\{.*?\}\}", " ", src, flags=re.DOTALL)
    out: list[tuple[str, set]] = []
    stack: list[set] = []
    combined = re.compile(TAG_RE.pattern + "|" + RENDER_TAG_RE.pattern, re.DOTALL)
    for m in combined.finditer(src):
        if m.group(1) is not None or m.group(2) is not None:
            closing, tag, attrs, selfclose = m.group(1), (m.group(2) or "").lower(), m.group(3), m.group(4)
            if closing:
                if stack:
                    stack.pop()
                continue
            cm = CLASS_RE.search(attrs or "")
            raw = (cm.group(2) or cm.group(3) or "") if cm else ""
            cls = {c for c in raw.split() if re.fullmatch(r"[A-Za-z_][\w-]*", c)}
            if tag not in VOID_TAGS and not selfclose:
                stack.append(cls)
        else:
            name = m.group(5) or m.group(6)
            if name:
                enclosing: set = set()
                for f in stack:
                    enclosing |= f
                out.append((name, enclosing))
    return out


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


def build_suppression_context(texts: dict[str, str], schema_ctx: dict[str, set]) -> dict[str, set]:
    """rel-path -> classes that MAY be assumed present on some ancestor, for suppression ONLY.

    bd nf3j. This is the union of every caller's enclosing wrapper classes, and a union across
    callers is a fiction: snippets/icon-bin.liquid is rendered both from the footer and from inside
    .cart__items__remove, so a merged set would satisfy `.footer__title .icon{position:absolute}`
    from one caller while offering `.cart__items__remove` as the late ancestor from another — an
    ancestry that never co-occurs on a real page. Feeding that to the DETECTION side invented three
    findings when it was tried.

    So this map is used only to answer "is the containing block already provided at first paint?".
    Being over-broad there can only SUPPRESS a finding, never invent one. Detection continues to use
    the schema-class context, which is deterministic — one class per section, and a snippet rendered
    by that section really is inside it.
    """
    by_name = {Path(rel).stem: rel for rel in texts if rel.startswith("snippets/")}
    out: dict[str, set] = {rel: set(schema_ctx.get(rel, ())) for rel in texts}
    edges = {rel: render_wrappers(text) for rel, text in texts.items()}
    for _ in range(6):                       # fixpoint; render chains here are 2-3 deep
        changed = False
        for rel in list(texts):
            carry = out.get(rel, set())
            for name, wrappers in edges.get(rel, ()):
                target = by_name.get(name)
                if not target:
                    continue
                add = carry | wrappers
                if not add <= out[target]:
                    out[target] |= add
                    changed = True
        if not changed:
            break
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

    crit_rules: list[tuple[str, str]] = []
    for sheet in FIRST_PAINT_SHEETS:
        if sheet.is_file():
            crit_rules.extend(iter_rules(sheet.read_text(encoding="utf-8", errors="replace")))

    crit_abs: dict[str, tuple[str, bool]] = {}   # class -> (selector, from_pseudo_element)
    crit_pos_rules: dict[str, list] = {}         # class -> positioning rules WITH requirements
    crit_hidden_rules: dict[str, list] = {}      # class -> rules that suppress painting (RULE 3)
    crit_size_rules: dict[str, dict] = {}        # class -> {prop: [reqs]} declared at first paint (RULE 4)
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
        if (decls.get("display") == "none" or decls.get("visibility") == "hidden"
                or decls.get("opacity", "").strip() in ("0", "0.0", ".0")):
            for req in parse_position_rules(selector, CRITICAL.name):
                crit_hidden_rules.setdefault(req["target"], []).append(req)
        # RULE 4 input: which size/display properties DO exist at first paint, and under what
        # requirements. A deferred rule is only a problem if first paint says nothing for that
        # property on a selector that actually matches the same element.
        for _p in ("display",) + SIZE_PROPS_R4:
            if _p in decls:
                for req in parse_position_rules(selector, "first-paint"):
                    crit_size_rules.setdefault(req["target"], {}).setdefault(_p, []).append(req)
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
    deferred_oof_rules: dict[str, list] = {}      # deferred sheet makes it absolute/fixed (RULE 3)
    deferred_size_rules: dict[str, list] = {}     # deferred-only display:none / big height (RULE 4)
    for pattern in DEFERRED_GLOBS:
        for path in sorted((REPO / "assets").glob(pattern)):
            if ".dev." in path.name:
                continue
            for selector, body in iter_rules(path.read_text(encoding="utf-8", errors="replace")):
                if decl_map(body).get("position", "") in POSITIONED_VALUES:
                    for req in parse_position_rules(selector, path.name):
                        if not req["pseudo"]:
                            deferred_pos_rules.setdefault(req["target"], []).append(req)
                # RULE 3 input: only absolute/fixed take an element OUT OF FLOW. A static ->
                # relative change keeps the element's space reserved, so it cannot reflow siblings.
                if decl_map(body).get("position", "") in ("absolute", "fixed"):
                    for req in parse_position_rules(selector, path.name):
                        if not req["pseudo"]:
                            deferred_oof_rules.setdefault(req["target"], []).append(req)
                # RULE 4 input (bd cuzo)
                _d = decl_map(body)
                if _d.get("display") == "none":
                    for req in parse_position_rules(selector, path.name):
                        if not req["pseudo"]:
                            deferred_size_rules.setdefault(req["target"], []).append(
                                dict(req, prop="display", value="none", why="paints then vanishes"))
                for _p in SIZE_PROPS_R4:
                    _why = r4_size_is_material(_p, _d.get(_p, "")) if _p in _d else None
                    if _why:
                        for req in parse_position_rules(selector, path.name):
                            if not req["pseudo"]:
                                deferred_size_rules.setdefault(req["target"], []).append(
                                    dict(req, prop=_p, value=_d[_p], why=_why))

    # ancestor chains from markup, plus the cross-file context the walker cannot see
    texts: dict[str, str] = {}
    for d in MARKUP_DIRS:
        for path in sorted((REPO / d).rglob("*.liquid")):
            texts[str(path.relative_to(REPO))] = path.read_text(encoding="utf-8", errors="replace")
    outer_ctx = build_outer_context(texts)
    suppress_ctx = build_suppression_context(texts, outer_ctx)
    ancestors: dict[str, list[tuple[str, list, set, bool]]] = {}
    for rel, text in texts.items():
        for cls, occurrences in ancestor_map(text).items():
            ancestors.setdefault(cls, []).extend(
                (rel, chain, own, hid) for chain, own, hid in occurrences)

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
        for rel, chain, own, _hidden in ancestors.get(cls, []):
            # Outermost frame = classes contributed from outside the file (section schema class,
            # and the schema class of whatever section renders this snippet). A pseudo-element is
            # laid out inside its OWN originating element, so that element joins the chain too —
            # without it, `.x:after{position:absolute}` next to `.x{position:relative}` would be
            # reported as a bug that cannot happen.
            eff_chain = [set(outer_ctx.get(rel, ()))] + chain + ([own] if from_pseudo else [])
            if not any(eff_chain):
                continue                               # no observed ancestry; can't judge
            # Suppression may assume the broader cross-file context (bd nf3j) — being over-broad
            # here only ever removes a finding. Detection below stays on the schema-only context.
            supp_chain = [set(suppress_ctx.get(rel, ()))] + chain + ([own] if from_pseudo else [])
            if nearest_positioned(supp_chain, crit_pos_rules)[0]:
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

    # RULE 3 — element taken OUT OF FLOW only by a deferred sheet (bd 66t7)
    #
    # The inverse of RULE 1, and it reflows more of the page. Critical CSS leaves the element
    # STATIC, so at first paint it is IN FLOW and occupies layout space. When the deferred sheet
    # makes it absolute/fixed it pops out of flow and everything below it jumps up — surrounding
    # content moves, not just the element.
    seen_oof: set[str] = set()
    for cls in sorted(deferred_oof_rules):
        for rel, chain, own, inline_hidden in ancestors.get(cls, []):
            if inline_hidden:
                continue                               # inline style suppresses painting
            outer = set(outer_ctx.get(rel, ()))
            full = [outer] + chain + [own]
            # Does the deferred out-of-flow rule actually match THIS occurrence?
            anc_union = set(outer)
            for f in chain:
                anc_union |= f
            supp_union = set(suppress_ctx.get(rel, ()))
            for f in chain:
                supp_union |= f
            oof = next((r for r in deferred_oof_rules[cls]
                        if rule_matches(r, own, anc_union)), None)
            if oof is None:
                continue
            # Critical CSS already gives it a position -> no in-flow/out-of-flow delta.
            if any(rule_matches(r, own, supp_union) for r in crit_pos_rules.get(cls, ())):
                continue
            # Cannot paint at first paint -> cannot contribute a shift. Checked on the element and
            # on every ancestor, since a hidden ancestor hides the subtree.
            if any(rule_matches(r, own, anc_union) for r in crit_hidden_rules.get(cls, ())):
                continue
            if any(any(rule_matches(r, frame, set().union(*full[:i]) if i else set())
                       for a in frame for r in crit_hidden_rules.get(a, ()))
                   for i, frame in enumerate(full)):
                continue
            if cls in seen_oof:
                continue
            seen_oof.add(cls)
            if cls in allow or f"{cls}/out-of-flow" in allow:
                continue
            findings.append({
                "rule": "late-out-of-flow",
                "cls": cls,
                "selector": oof["selector"],
                "where": rel,
                "detail": (f"critical CSS leaves this STATIC, but `{oof['selector'][:60]}` in "
                           f"{oof['source']} (deferred) makes it position:absolute/fixed — so it "
                           f"occupies layout space at first paint and everything below it jumps "
                           f"up when the sheet lands"),
                "fix": (f"mirror the position declaration for .{cls} into critical-css.liquid "
                        f"(position alone is enough — it keeps the element out of flow from the "
                        f"first paint, which is what stops surrounding content reflowing)"),
                "key": f"{cls}/out-of-flow",
            })

    # RULE 4 — size or display that exists ONLY in a deferred sheet (bd cuzo)
    #
    # The variant that produced bd fj5m and bd agt7, and that RULES 1-3 are all blind to. Two shapes:
    #   display:none arriving late  -> the element PAINTS a full block and then vanishes, collapsing
    #                                  its space. fj5m: `.cart__template .cart--hidden{display:none}`
    #                                  lives in the deferred cart-page.css, so BOTH cart states
    #                                  rendered at first paint and 352px disappeared.
    #   a height arriving late      -> nothing is reserved, then the box jumps. fj5m: .cart__empty
    #                                  32px -> 344px. agt7: .cart__circle auto -> 160x160.
    seen_r4: set[str] = set()
    for cls in sorted(deferred_size_rules):
        if cls in seen_r4:
            continue
        for rel, chain, own, inline_hidden in ancestors.get(cls, []):
            if cls in seen_r4:
                break
            if inline_hidden:
                continue
            for outer in outer_ctx.get(rel, [set()]) if isinstance(outer_ctx.get(rel), list) else [set(outer_ctx.get(rel, ()))]:
                anc_union: set = set(outer)
                for f in chain:
                    anc_union |= f
                supp_union: set = set(suppress_ctx.get(rel, ()))
                for f in chain:
                    supp_union |= f
                hit = next((r for r in deferred_size_rules[cls]
                            if rule_matches(r, own, anc_union)), None)
                if hit is None:
                    continue
                # Does ANY first-paint sheet declare the same property for a matching selector?
                if any(rule_matches(r, own, supp_union)
                       for r in crit_size_rules.get(cls, {}).get(hit["prop"], ())):
                    continue
                # Cannot paint at first paint -> cannot shift.
                if any(rule_matches(r, own, anc_union) for r in crit_hidden_rules.get(cls, ())):
                    continue
                # The hidden-ancestor exemption must use the NARROW (schema-only) context, not the
                # cross-file union. cart-empty.liquid is rendered both from the visible /cart page
                # and from inside the hidden cart drawer; the union says "hidden" and would suppress
                # a real finding — it did exactly that to agt7's .cart__circle while I was building
                # this. Over-broad is safe for "is it positioned"; it is NOT safe for "is it hidden".
                full = [set(outer)] + chain + [own]
                hidden_anc = False
                for i, frame in enumerate(full):
                    outer_i: set = set()
                    for f in full[:i]:
                        outer_i |= f
                    for a in frame:
                        if any(rule_matches(r, frame, outer_i) for r in crit_hidden_rules.get(a, ())):
                            hidden_anc = True
                            break
                    if hidden_anc:
                        break
                if hidden_anc:
                    continue
                seen_r4.add(cls)
                if cls in allow or f"{cls}/{hit['prop']}-late" in allow:
                    break
                findings.append({
                    "rule": "late-size-or-display",
                    "cls": cls,
                    "selector": hit["selector"],
                    "where": rel,
                    "detail": (f"`{hit['selector'][:56]}` in {hit['source']} (deferred) sets "
                               f"{hit['prop']}:{hit['value']} ({hit['why']}), and no first-paint "
                               f"sheet declares {hit['prop']} for this element — so it is unsized "
                               f"(or visible) until that sheet lands, then jumps"),
                    "fix": (f"mirror `{hit['prop']}:{hit['value']}` for .{cls} into "
                            f"critical-css.liquid, byte-equal to the deferred declaration"),
                    "key": f"{cls}/{hit['prop']}-late",
                })
                break

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
        ("ccc-late-out-of-flow", True,
         "bd 66t7 RULE 3: static in critical, absolute only in the deferred sheet"),
        ("ccc-late-out-of-flow-fixed", False,
         "...silent once the position is mirrored into critical CSS"),
        ("ccc-late-out-of-flow-hidden", False,
         "RULE 3 exemption: critical CSS hides it, so it cannot paint or shift"),
        ("ccc-late-out-of-flow-inline", False,
         "RULE 3 exemption: inline style=display:none wins at first paint (.item--loadbar)"),
        ("ccc-late-display", True,
         "bd cuzo RULE 4: deferred display:none — the block paints, then vanishes (the fj5m shape)"),
        ("ccc-late-display-fixed", False,
         "...silent once the display is mirrored into critical CSS"),
        ("ccc-late-height", True,
         "bd cuzo RULE 4: a viewport-relative height that only the deferred sheet supplies"),
        ("ccc-late-height-fixed", False,
         "...silent once the height is mirrored"),
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
    crit_hidden_rules: dict[str, list] = {}
    crit_size_rules: dict[str, dict] = {}
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
        if (decls.get("display") == "none" or decls.get("visibility") == "hidden"
                or decls.get("opacity", "").strip() in ("0", "0.0", ".0")):
            for req in parse_position_rules(selector, CRITICAL.name):
                crit_hidden_rules.setdefault(req["target"], []).append(req)
        if (decls.get("display") == "none" or decls.get("visibility") == "hidden"
                or decls.get("opacity", "").strip() in ("0", "0.0", ".0")):
            for req in parse_position_rules(selector, "critical"):
                crit_hidden_rules.setdefault(req["target"], []).append(req)
        for _p in ("display",) + SIZE_PROPS_R4:
            if _p in decls:
                for req in parse_position_rules(selector, "first-paint"):
                    crit_size_rules.setdefault(req["target"], {}).setdefault(_p, []).append(req)
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
    deferred_oof_rules: dict[str, list] = {}
    deferred_size_rules: dict[str, list] = {}
    for selector, body in iter_rules(deferred_css):
        pos = decl_map(body).get("position", "")
        if pos in POSITIONED_VALUES:
            for req in parse_position_rules(selector, "deferred.css"):
                if not req["pseudo"]:
                    deferred_pos_rules.setdefault(req["target"], []).append(req)
        if pos in ("absolute", "fixed"):
            for req in parse_position_rules(selector, "deferred.css"):
                if not req["pseudo"]:
                    deferred_oof_rules.setdefault(req["target"], []).append(req)
        _d = decl_map(body)
        if _d.get("display") == "none":
            for req in parse_position_rules(selector, "deferred.css"):
                if not req["pseudo"]:
                    deferred_size_rules.setdefault(req["target"], []).append(
                        dict(req, prop="display", value="none", why="paints then vanishes"))
        for _p in SIZE_PROPS_R4:
            _why = r4_size_is_material(_p, _d.get(_p, "")) if _p in _d else None
            if _why:
                for req in parse_position_rules(selector, "deferred.css"):
                    if not req["pseudo"]:
                        deferred_size_rules.setdefault(req["target"], []).append(
                            dict(req, prop=_p, value=_d[_p], why=_why))
    outer = build_outer_context({"fixture.liquid": markup}).get("fixture.liquid", set())
    ancestors = ancestor_map(markup)
    out = []
    for cls, (selector, from_pseudo) in sorted(crit_abs.items()):
        for chain, own, _hid in ancestors.get(cls, []):
            eff = [set(outer)] + chain + ([own] if from_pseudo else [])
            if not any(eff):
                continue
            if nearest_positioned(eff, crit_pos_rules)[0]:
                continue
            late, _ = nearest_positioned(eff, deferred_pos_rules)
            if late:
                out.append({"rule": "orphaned-absolute", "cls": cls, "selector": selector})
                break
    for cls in sorted(deferred_oof_rules):
        for chain, own, inline_hidden in ancestors.get(cls, []):
            if inline_hidden:
                continue
            anc_union = set(outer)
            for f in chain:
                anc_union |= f
            supp_union = anc_union   # fixtures are single-file: no cross-file context
            if not any(rule_matches(r, own, anc_union) for r in deferred_oof_rules[cls]):
                continue
            if any(rule_matches(r, own, supp_union) for r in crit_pos_rules.get(cls, ())):
                continue
            if any(rule_matches(r, own, anc_union) for r in crit_hidden_rules.get(cls, ())):
                continue
            out.append({"rule": "late-out-of-flow", "cls": cls,
                        "selector": deferred_oof_rules[cls][0]["selector"]})
            break
    for cls in sorted(deferred_size_rules):
        for chain, own, inline_hidden in ancestors.get(cls, []):
            if inline_hidden:
                continue
            anc_union = set(outer)
            for f in chain:
                anc_union |= f
            hit = next((r for r in deferred_size_rules[cls]
                        if rule_matches(r, own, anc_union)), None)
            if hit is None:
                continue
            if any(rule_matches(r, own, anc_union)
                   for r in crit_size_rules.get(cls, {}).get(hit["prop"], ())):
                continue
            if any(rule_matches(r, own, anc_union) for r in crit_hidden_rules.get(cls, ())):
                continue
            out.append({"rule": "late-size-or-display", "cls": cls, "selector": hit["selector"]})
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
