# lodash/Modernizr Callsite Audit
Generated: 2026-05-18 | bd: 2i8b.13

## Summary
- **Total lodash callsites in theme code (sections/snippets/templates/layout): 0**
- **Total Modernizr callsites in theme code: 0**
- **Total window.theme external references: 0**
- **Verdict: shop.js CAN be dropped** (all lodash/Modernizr usage is internal to shop.js; theme code does not depend on it)

---

## shop.js Internal Callsites — lodash

For reference only — these are internal to shop.js, not theme code.

| Line | Function | Code | Native Replacement | Risk |
|------|----------|------|-------------------|------|
| 636 | _.assignIn | `theme.Sections.prototype = _.assignIn({}, theme.Sections.prototype, {` | Object.assign | Low — _.assignIn maps own+inherited enumerable; Object.assign only own. No inherited props expected on prototype objects here, so safe. |
| 644 | _.assignIn | `return _.assignIn(new constructor(container), {` | Object.assign | Low — same reasoning; constructor instances have own props. |
| 658 | _.filter | `this.instances = _.filter(this.instances, function(instance) {` | Array.prototype.filter | Low — direct 1:1 replacement |
| 662 | _.isFunction | `if (_.isFunction(instance.onUnload)) {` | `typeof instance.onUnload === 'function'` | Low — _.isFunction is slightly more robust for async/generator but not needed here |
| 673 | _.find | `var instance = _.find(this.instances, function(instance) {` | Array.prototype.find | Low — direct 1:1 replacement |
| 677 | _.isUndefined | `if (!_.isUndefined(instance) && _.isFunction(instance.onSelect)) {` | `instance !== undefined` | Low — direct 1:1 replacement |
| 684 | _.find | `var instance = _.find(this.instances, function(instance) {` | Array.prototype.find | Low |
| 688 | _.isUndefined | `if (!_.isUndefined(instance) && _.isFunction(instance.onDeselect)) {` | `instance !== undefined` | Low |
| 695 | _.find | `var instance = _.find(this.instances, function(instance) {` | Array.prototype.find | Low |
| 699 | _.isUndefined | `if (!_.isUndefined(instance) && _.isFunction(instance.onBlockSelect)) {` | `instance !== undefined` | Low |
| 706 | _.find | `var instance = _.find(this.instances, function(instance) {` | Array.prototype.find | Low |
| 710 | _.isUndefined | `if (!_.isUndefined(instance) && _.isFunction(instance.onBlockDeselect)) {` | `instance !== undefined` | Low |
| 739 | _.assignIn | `Banner.prototype = _.assignIn({}, Banner.prototype, {` | Object.assign | Low |
| 782 | _.assignIn | `Video.prototype = _.assignIn({}, Video.prototype, {` | Object.assign | Low |
| 859 | _.assignIn | `Product.prototype = _.assignIn({}, Product.prototype, {` | Object.assign | Low |
| 1196 | _.assignIn | `Variants.prototype = _.assignIn({}, Variants.prototype, {` | Object.assign | Low |
| 1205 | _.map | `var currentOptions = _.map($(this.singleOptionSelector, this.$container), function(element) {` | Array.from(\.\.\.).map | Low — jQuery collection needs Array.from first |
| 1228 | _.compact | `currentOptions = _.compact(currentOptions);` | `.filter(Boolean)` | Low — direct 1:1 replacement |
| 1243 | _.find | `var found = _.find(variants, function(variant) {` | Array.prototype.find | Low |
| 1245 | _.isEqual | `return _.isEqual(variant[values.index], values.value);` | `===` (strict equality) | Low — values are primitive strings/numbers; deep equality not needed |
| 1360 | _.isUndefined | `if( !_.isUndefined( userFeed.options.accessToken) ){` | `userFeed.options.accessToken !== undefined` | Low |
| 1364 | _.assignIn | `Instagram.prototype = _.assignIn({}, Instagram.prototype, {});` | Object.assign | Low — note: empty {} second arg is a no-op merge |
| 1384 | _.assignIn | `Parallax.prototype = _.assignIn({}, Parallax.prototype, {` | Object.assign | Low |
| 1428 | _.assignIn | `Slideshow.prototype = _.assignIn({}, Slideshow.prototype, {` | Object.assign | Low |

**Unique lodash methods used (7):** _.assignIn, _.filter, _.find, _.isFunction, _.isUndefined, _.map, _.compact, _.isEqual

**All have trivial native ES6+ replacements.** No lodash method used requires the full lodash library.

---

## shop.js Internal Callsites — Modernizr

| Line | Function | Code | Native Replacement | Risk |
|------|----------|------|-------------------|------|
| 439 | Modernizr.touch | `if (Modernizr.touch){` | `'ontouchstart' in window \|\| navigator.maxTouchPoints > 0` | Low — simpler alternative: `window.matchMedia('(hover: none)').matches` for touch-primary |
| 1023 | Modernizr.touch | `if ( this.zoomEnable && !Modernizr.touch ){ swipeEnable = false; }` | Same as above, negated | Low |
| 1045 | Modernizr.touch | `if (Modernizr.touch) { return; }` | Same as above | Low |

**Unique Modernizr features used (1):** Modernizr.touch

All three callsites are simple boolean touch-detection checks. Replaceable with a one-liner feature detect or CSS `@media (hover: none)`.

---

## window.theme Namespace

| Location | Line | Code |
|----------|------|------|
| assets/shop.js.liquid | 1 | `window.theme = window.theme \|\| {};` |
| assets/shop.js.liquid | 621 | `window.theme = window.theme \|\| {};` |

**External references (sections/snippets/templates/layout): 0**

Grep for `window.theme.` across `sections/`, `snippets/`, `templates/`, `layout/` returned zero results. The namespace is defined and consumed entirely within shop.js.

---

## shop.js Load Point

layout/theme.liquid line 999:
```html
<script src="{{ 'shop.js' | asset_url }}" defer="defer"></script>
```

Full context (lines 987–999):
```html
      Defer 2026-04-29: shop.js is 177KB and was loaded via Shopify's
      …
      shop.js bundles its own lodash (no jQuery dep) and runs theme
      …
    {%- endcomment -%}
    <script src="{{ 'shop.js' | asset_url }}" defer="defer"></script>
```

---

## Recommendation

**Drop shop.js entirely from theme.liquid.** Zero theme files (sections, snippets, templates, layout) depend on its lodash namespace, Modernizr checks, or `window.theme` stub. The estimated savings:

- **~134–177 KB** of JavaScript removed (bundled lodash + Modernizr + shop.js code)
- **Zero functional regression** in theme code — no external consumer of any lodash/Modernizr/theme exports
- If any shop.js functionality is still needed (e.g., section registration logic), it should be rewritten using native ES6+ equivalents and moved to `theme.js.liquid` or a new module — but based on this audit, the entire file appears to be a legacy artifact with no theme dependencies.

### Conversion Cheat-Sheet (if selective porting is needed later)

| Lodash | Native |
|--------|--------|
| `_.filter(arr, fn)` | `arr.filter(fn)` |
| `_.find(arr, fn)` | `arr.find(fn)` |
| `_.map(arr, fn)` | `Array.from(arr).map(fn)` |
| `_.compact(arr)` | `arr.filter(Boolean)` |
| `_.isEqual(a, b)` | `a === b` (for primitives) |
| `_.isFunction(x)` | `typeof x === 'function'` |
| `_.isUndefined(x)` | `x === undefined` |
| `_.assignIn({}, ...sources)` | `Object.assign({}, ...sources)` |
| `Modernizr.touch` | `'ontouchstart' in window` |