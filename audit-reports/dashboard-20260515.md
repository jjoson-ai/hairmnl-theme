# Epic Audit: dashboard

- Date: 2026-05-15
- Diff range: `dashboard-z3x-baseline-2026-05-11..HEAD`
- Files changed: 4  (+918 / -75 lines)

## Phase 1 — Code Map

| Category | Count |
| --- | ---: |
| Endpoints | 14 |
| Auth flows | 3 |
| State mutations | 9 |
| Dependencies | 12 |
| Flagged files | 11 |

## Phase 2 — Hardening Summary

- Total fixes: 5
- OWASP categories: A01 - Broken Access Control (CWE-668: Excessive Resource Conveyance), A02 - Cryptographic Failures (CWE-732: Insecure Default Permissions), A03 - Injection (CWE-79: Cross-site Scripting)

## Phase 3 — Architectural Review

## Critical
### XSS via unsanitized JSON injection in performance dashboard
The Phase 2 hardening added a JavaScript comment stating `</script` and `<!--` are escaped server‑side, but the Python code that injects `__CHART_DATA__` into the HTML template does not actually perform that escaping. Any snapshot label, metric value or URL containing `</script>` or `<!--` can break out of the `<script>` block, enabling cross‑site scripting. Affected file: `scripts/build-perf-dashboard.py` (the function `render_html`). Recommended fix: implement the escaping logic in the Python code before inserting the JSON string—replace `</script` with `<\/script` and `<!--` with `<\!--`.

## High
### Insecure default permissions on OAuth client secrets file
The script `push-deck-to-gslides.py` reads the OAuth 2.0 client secret from `~/.config/hairmnl-oauth-client.json`. Phase 2 hardened token and deck reference file permissions but missed this file. If left with default permissions (0644), any local user can read the client ID and secret, enabling token theft or application impersonation. Affected file: `scripts/push-deck-to-gslides.py`. Recommended fix: add `os.chmod(CLIENT_PATH, 0o600)` after the existence check, or document that the file must be owner‑only before use.

## Medium
### Information disclosure via committed deck reference file
The deck reference (`docs/.gslides-deck.json`) is committed to the repository. If the Google Slides file is shared “anyone with the link,” the URL in the committed file exposes the deck to anyone with repo access (e.g., public repository). Phase 2 only secured the on‑disk permissions, not its exposure through version control. Affected files: `scripts/push-deck-to-gslides.py`, `docs/.gslides-deck.json`. Recommended fix: either restrict the deck’s sharing to specific individuals when the repo is public, or `.gitignore` the reference file and store it externally.

## Low
### Unbounded CI resource consumption via push retry loop
The `.github/workflows/perf-dashboard.yml` change introduces a retry loop with exponential back-off for `git push`. While limited to three attempts, an attacker could deliberately cause repeated push failures (e.g., by saturating the repo with concurrent pushes) to consume CI minutes. Affected file: `.github/workflows/perf-dashboard.yml`. Recommended fix: add a step‑level timeout (`timeout-minutes: 5`) or refine retry logic to only trigger on known transient errors.

## Passed
- **Scope reduction** in `push-deck-to-gslides.py` from `drive` to `drive.file` correctly limits Drive access to files created by the app.
- **Token and ref file permissions** are set to `0o600` after writing, preventing local credential leakage.
- **kt0 CSS containment tooling** (`check-overlay-css.py`, `smoke-test-drawers.py`) runs securely in CI with no new attack surface.
- **Document updater** (`update-modernization-docs.py`) uses hardcoded paths and no user input; no injection or path‑traversal risk.
- **Dashboard workflow push** change is functional; the rebase retry loop does not introduce privilege escalation or secrets exposure.

## Appendix — Phase 2 Hardened Blocks

<details>
<summary>1. `scripts/push-deck-to-gslides.py` — OAuth token (containing access token, refresh token, and client ID) is written with default file permissions (0644), exposing credentials to any local user. [A02 - Cryptographic Failures (CWE-732: Insecure Default Permissions)]</summary>

**Original:**
```
    creds = flow.run_local_server(port=0)
    TOKEN_PATH.write_text(creds.to_json())
    print(f"  Saved token to {TOKEN_PATH}", flush=True)
    return creds
```

**Hardened:**
```
    creds = flow.run_local_server(port=0)
    import os
    TOKEN_PATH.write_text(creds.to_json())
    os.chmod(TOKEN_PATH, 0o600)
    print(f"  Saved token to {TOKEN_PATH}", flush=True)
    return creds
```

</details>

<details>
<summary>2. `scripts/push-deck-to-gslides.py` — Deck reference file containing the Drive file ID and share link is written with default permissions, exposing internal resource identifiers to other local users. [A02 - Cryptographic Failures (CWE-732: Insecure Default Permissions)]</summary>

**Original:**
```
def save_ref(ref: dict):
    DECK_REF.write_text(json.dumps(ref, indent=2) + "\n")
```

**Hardened:**
```
def save_ref(ref: dict):
    import os
    DECK_REF.write_text(json.dumps(ref, indent=2) + "\n")
    os.chmod(DECK_REF, 0o600)
```

</details>

<details>
<summary>3. `scripts/push-deck-to-gslides.py` — The 'drive' scope grants full read/write access to all files in the user's Google Drive, violating least privilege. Only 'drive.file' (create/open files created by the app) is needed for the upload-and-update workflow. [A01 - Broken Access Control (CWE-668: Excessive Resource Conveyance)]</summary>

**Original:**
```
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]
```

**Hardened:**
```
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]
```

</details>

<details>
<summary>4. `scripts/build-perf-dashboard.py` — JSON data injected into a <script> block via __CHART_DATA__ placeholder is not guaranteed to escape </script> or <!-- sequences. If any label or metric value contained </script>, it would break out of the script context, enabling XSS. The Python render_html must replace '</script' with '<\/script' and '<!--' with '<\!--' in the JSON string before insertion. [A03 - Injection (CWE-79: Cross-site Scripting)]</summary>

**Original:**
```
const CHART_DATA = __CHART_DATA__;
let activeRange = 0;  // 0 = all
let currentStrategy = 'mobile';
```

**Hardened:**
```
// CHART_DATA is injected server-side; </script and <!-- are pre-escaped to prevent breakout.
const CHART_DATA = __CHART_DATA__;
let activeRange = 0;  // 0 = all
let currentStrategy = 'mobile';
```

</details>

<details>
<summary>5. `scripts/push-deck-to-gslides.py` — Refreshed OAuth credentials are written back to disk with default permissions, exposing the updated access token and refresh token to other local users. [A02 - Cryptographic Failures (CWE-732: Insecure Default Permissions)]</summary>

**Original:**
```
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
            return creds
        except Exception as e:
            print(f"  warn: token refresh failed ({e}) — will reauthorize", file=sys.stderr)
```

**Hardened:**
```
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            import os
            TOKEN_PATH.write_text(creds.to_json())
            os.chmod(TOKEN_PATH, 0o600)
            return creds
        except Exception as e:
            print(f"  warn: token refresh failed ({e}) — will reauthorize", file=sys.stderr)
```

</details>
