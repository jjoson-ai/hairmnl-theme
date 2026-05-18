# HairMNL P8 cutover smoke tests — Playwright

Automated behavioral verification of the 7 smoke checks documented in
`os2-migration/p8-cutover-operator-playbook.html`. Pairs with the
static-content suite (`scripts/pre-cutover-smoke.sh`):

- `pre-cutover-smoke.sh` checks **does the code exist on dev?** (grep markers in pulled files)
- This Playwright suite checks **does the code behave correctly when a browser hits it?**

Both should pass before live cutover.

## Quick start

```bash
cd scripts/smoke-tests
npm install
npm run install-browsers
npm test
```

Open the HTML report after the run:

```bash
npm run report
```

## The 8 smoke tests

| # | Spec file | What it verifies | bd ticket |
|---|---|---|---|
| 1 | `smoke-01-font-cls.spec.ts` | Homepage CLS ≤ 0.10; no single shift > 0.05 | ujg6.7 |
| 2 | `smoke-02-mobile-menu-buttons.spec.ts` | Brand-page mobile CLS ≤ 0.10; menu-buttons contribution ≤ 0.05 | 2i8b.18 |
| 3 | `smoke-03-per-template-js.spec.ts` | hairmnl-{common,collection,product}.js loaded only on right templates | ujg6.14 + 2i8b.19 |
| 4 | `smoke-04-reamaze-defer.spec.ts` | cdn.reamaze.com NOT loaded pre-interaction; placeholder visible; click + scroll triggers fire | fsaa |
| 5 | `smoke-05-facet-ajax.spec.ts` | Collection filter checkbox = no page reload + URL update + section_id fetch | ujg6.16 |
| 6 | `smoke-06-lazy-render.spec.ts` | Below-fold placeholders swap to content on scroll; Section Rendering API returns full HTML | ujg6.18 (3 increments) |
| 7 | `smoke-07-font-preloads.spec.ts` | 2 font preload `<link>` tags in head; preloads fetched in first 50 requests; homepage first slide is eager+high | ujg6.19 |
| 8 | `smoke-08-visual-parity.spec.ts` | Visual regression vs committed baseline — 5 templates full-page + 4 regions + cart drawer × 2 viewports | (operator-time reducer) |

## Visual parity workflow (smoke 8)

Smoke 8 is the **operator-time reducer**. It replaces the 2-3 hour manual
parallel-run visual QA in the operator playbook with an automated screenshot diff.

### First-run setup (operator does this once)

```bash
# 1. Verify the dev theme looks the way you want it to (manual eyeball)
# 2. Capture baselines from the current state:
npm run update-baselines

# 3. Commit the baselines
git add __screenshots__/
git commit -m "smoke-8: initial visual-parity baselines"
```

The `__screenshots__/` directory is committed to the repo. Each subsequent
test run compares against these baselines.

### Drift detection (every PR)

```bash
npm run test:visual
```

Any visual change > 1% pixel-ratio threshold fails the test. The HTML
report (`npm run report`) shows:
- The baseline image
- The current screenshot
- A diff image highlighting the changed pixels

### Intentional design changes

When a design change is intentional (new product card layout, etc.):

```bash
# After making the design change + verifying it looks right:
npm run update-baselines

# Commit alongside the design change PR — the reviewer sees the
# new baselines as part of the diff, making intent obvious
git add __screenshots__/ <your-design-files>
git commit -m "feat(design): new product card layout"
```

### What's masked (dynamic regions that shouldn't fail the diff)

The helpers/visual-parity.ts `DYNAMIC_REGIONS` array painted over before
screenshot:
- Reamaze placeholder + open chat widget
- Klaviyo signup modals
- LoyaltyLion points display + notifications
- Cart count badge
- Vertex/LimeSpot personalized recommendations
- Recently-viewed (localStorage-driven)
- Countdown timers, inventory status

Add to the array as new dynamic content surfaces.

## Configuration

Environment variables:

| Var | Default | When to use |
|---|---|---|
| `BASE_URL` | `https://creations-gdc.myshopify.com` | Point at a different Shopify store |
| `PREVIEW_THEME_ID` | `141168312419` | Test against a different dev theme |
| `SHOPIFY_AUTH` | unset | Path to a Playwright storageState.json with Shopify admin cookies |
| `HEADLESS` | `true` | Set to `false` to watch tests run in a visible browser |
| `CI` | unset | Set in CI to enable retries (1 retry per test) |

### Post-cutover mode

After cutover, point at the LIVE URL — no preview_theme_id needed:

```bash
BASE_URL=https://www.hairmnl.com npm test
```

The `helpers/dev-preview.ts` `IS_POST_CUTOVER` flag handles this automatically.

## Authenticating against the dev theme

The Shopify preview URL has a quirk: `?preview_theme_id=N` strips on the
canonical-domain redirect (per the 2i8b.17 finding). Without a Shopify
admin session, Playwright tests will land on the LIVE theme instead of
the dev theme.

**One-time auth setup:**

```bash
npx playwright codegen https://creations-gdc.myshopify.com/admin
# In the opened browser:
#   1. Log in to Shopify admin as a user with theme-editor access
#   2. Visit https://creations-gdc.myshopify.com/?preview_theme_id=141168312419
#   3. Confirm you see the P8 dev theme
#   4. In Playwright Inspector: Click "Save storage state" → save to .auth/storageState.json
# Exit codegen
```

Then on subsequent runs:

```bash
SHOPIFY_AUTH=.auth/storageState.json npm test
```

The `.auth/` dir is gitignored so the cookie file doesn't leak into version control.

## Running individual tests

```bash
npm run test:smoke-1                  # one test by number
npm run test:mobile                    # all tests, mobile project only
npm run test:headed                    # watch tests run in a visible browser
npm run test:debug                     # pause + step through in Playwright Inspector
npx playwright test --grep="reamaze"   # by test name
```

## CI integration

For GitHub Actions, add a workflow that:

1. Installs node + npm deps
2. Runs `npx playwright install --with-deps chromium`
3. Sets `SHOPIFY_AUTH` env var from a repo secret (the storageState.json)
4. Runs `npm test`
5. Uploads `playwright-report/` as a build artifact

See `ujg6.23` bd ticket for the broader Lighthouse-CI workflow spec — the
Playwright suite slots in as the behavioral half of that CI gate.

## What's not in this suite

Some checks are inherently human-eyeball or require infrastructure beyond
Playwright. Documented for honesty:

- **First-time design judgment** ("is this design good?") — there's no machine substitute. Smoke 8 detects DRIFT from a committed baseline; it can't tell you the baseline itself is correct.
- **TAE app verification** (Klaviyo signup form appears, Judge.me badges render) — these load in iframes, async, and depend on app server state. Operator browser smoke is the right gate for these.
- **PSI-quality timing measurement** — Playwright doesn't have PSI's standardized remote runners or Slow-4G throttling fidelity. Use `scripts/psi-baseline-matrix.py` for performance measurement; this suite is for behavior.
- **Reamaze chat actually delivering a message** — requires Reamaze backend; flaky in CI. We assert the SDK starts loading after interaction; full chat flow is operator smoke.

## Debugging a failing test

1. Re-run with `--headed` to watch the failure: `npm run test:headed -- smoke-04`
2. Open the HTML report: `npm run report` — has screenshots + traces + videos for any failure
3. Step through interactively: `npm run test:debug -- smoke-04`
4. Check the network log: failures print a `net.describe('substring')` dump to stderr

For URL-redirect issues (test fails with "landed on hairmnl.com"), it's the auth setup — confirm `SHOPIFY_AUTH` is set and the storageState file isn't expired.

## Cross-references

- Operator-facing equivalent (manual smoke walkthrough): `os2-migration/p8-cutover-operator-playbook.html`
- Static-content automated verification: `scripts/pre-cutover-smoke.sh`
- Performance matrix (PSI lab): `scripts/psi-baseline-matrix.py`
- The bd tickets each test verifies: see table at top of this README
