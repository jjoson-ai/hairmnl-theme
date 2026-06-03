# Epic Audit: reamaze-defer

- Date: 2026-06-04
- Diff range: `audit/reamaze-defer/baseline..HEAD`
- Files changed: 2  (+362 / -0 lines)

## Phase 1 — Code Map

| Category | Count |
| --- | ---: |
| Endpoints | 0 |
| Auth flows | 0 |
| State mutations | 0 |
| Dependencies | 6 |
| Flagged files | 3 |

## Phase 2 — Hardening Summary

- Total fixes: 1
- OWASP categories: A03:2021-Injection

## Phase 3 — Architectural Review

## Summary
Phase 2 fixed the image‑preload injection bug (the one that let someone with article editing privileges run JavaScript in a visitor’s browser) by checking for dangerous URL schemes and HTML‑escaping the output.  That fix works.  The new CSS‑defer and Reamaze‑defer scripts, added at the same time, overwrite core browser functions globally.  While not directly exploitable today, these overrides can break other apps or future theme changes and need tighter scoping.

## Critical
None.

## High
None.

## Medium
### Global `document.createElement` overrides can interfere with other scripts
Both the CSS‑defer and Reamaze‑defer scripts overwrite the browser’s built‑in function that creates new HTML elements (`document.createElement`).  The CSS version intercepts every `link` element that is ever created, even those that have nothing to do with ProBlogger, and the Reamaze version intercepts every `script` element.  If any other Shopify app or analytics snippet uses `document.createElement` to add a stylesheet or a script, its behaviour may change unexpectedly — a stylesheet could be put into “print” mode, a script could silently fail to load, or a timing assumption could be invalidated.  This is a stability and interoperability risk, not a direct security hole today, but it becomes a very hard bug to diagnose when something breaks in production a few months from now.

**Affected files:**
- `layout/theme.liquid` — both deferred CSS script block and Reamaze guard block (the `document.createElement` reassignments).

**Fix:** Scope each override so it applies only during the initial page‑load phase (e.g. by running it once and then restoring the original function, or by wrapping it inside a flag that is cleared after all known injections are handled).  Use a more targeted approach like observing the specific container where Shopify inserts app embeds instead of patching the global method.

## Low
### Consent‑unaware GA4 telemetry on Reamaze load
The Reamaze guard sends `reamaze_load_path` and `reamaze_load_latency_ms` events to Google Analytics as soon as the widget loads (when the user clicks, scrolls, or the timer fires).  If the shop uses a consent‑management banner, those events may fire before the visitor has given analytics consent.  That can violate privacy regulations or internal data‑privacy rules.

**Affected files:**
- `layout/theme.liquid` — the `dl()` calls inside the `disarm()` function.

**Fix:** Wrap each `dl()` call with a check for an existing consent flag (e.g. `if (window.consentState && window.consentState.analytics)`) or defer the pushes until the consent‑management platform signals approval.

### Placeholder click handler may fire after disarm (cosmetic)
If the placeholder button is clicked while the real Reamaze widget is already loading, the click handler calls `disarm()` a second time.  The `disarmed` flag prevents replaying the scripts again, but the `e.preventDefault()` call could still swallow the click event.  In practice the button is hidden as soon as the widget begins loading, so this is unlikely, but it’s a small state‑management edge case.

**Affected files:**
- `layout/theme.liquid` — the `document.addEventListener('click', ...)` block.

**Fix:** Remove the event listener on disarm (e.g. store a reference and call `removeEventListener`) so no further clicks get captured.

## Passed
### Image‑preload script injection (A03 Injection)
The original extraction of the first image `src` from `article.content` was unescaped, allowing a crafted article to inject arbitrary HTML attributes (and therefore JavaScript) into the preload `<link>` tag.  The hardened version now:
- rejects URLs that start with `javascript:` or `data:`,
- HTML‑escapes the extracted URL before inserting it into the `href` attribute.

Even if the extraction picks up extra characters, the escaping makes the output safe.  Real‑world impact is prevented.  No further action needed.

## Appendix — Phase 2 Hardened Blocks

<details>
<summary>1. `layout/theme.liquid` — The URL extracted from article.content is inserted into the href attribute using unescaped Liquid output ({{ _first_body_img_url }} instead of {{ _first_body_img_url | escape }}). Because the extraction relies on naive string splitting, a crafted article can produce a URL containing a double-quote character — for example, an img tag with src='x" onclick="alert(1)' yields the extracted value x" onclick="alert(1), which breaks out of the href attribute and injects arbitrary HTML attributes or event handlers onto the <link> element. Any store staff member or third-party app with article-editing privileges can exploit this to execute JavaScript in visitors' browsers. Additionally, the only validation (contains '/') does not block javascript: or data: URL schemes. [A03:2021-Injection]</summary>

**Original:**
```
      {%- if _first_body_img_url and _first_body_img_url != '' and _first_body_img_url contains '/' -%}
        <link rel="preload" as="image" href="{{ _first_body_img_url }}" fetchpriority="high">
      {%- endif -%}
```

**Hardened:**
```
      {%- if _first_body_img_url and _first_body_img_url != '' and _first_body_img_url contains '/' -%}
        {%- assign _unsafe_proto = false -%}
        {%- if _first_body_img_url | slice: 0, 11 == 'javascript:' -%}{%- assign _unsafe_proto = true -%}{%- endif -%}
        {%- if _first_body_img_url | slice: 0, 5 == 'data:' -%}{%- assign _unsafe_proto = true -%}{%- endif -%}
        {%- unless _unsafe_proto -%}
          <link rel="preload" as="image" href="{{ _first_body_img_url | escape }}" fetchpriority="high">
        {%- endunless -%}
      {%- endif -%}
```

</details>
