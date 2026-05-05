# Required GitHub repository secrets

These secrets must be added via the GitHub UI before the `perf-dashboard.yml` workflow can run.

Navigate to: **Settings → Secrets and variables → Actions → New repository secret**
URL: https://github.com/jjoson-ai/hairmnl-theme/settings/secrets/actions

| Secret name | Value | How to get it |
|---|---|---|
| `GA4_SERVICE_ACCOUNT_KEY` | Full JSON contents of `~/.config/hairmnl-ga4-key.json` | `cat ~/.config/hairmnl-ga4-key.json` |
| `PSI_API_KEY` | PageSpeed Insights API key | `security find-generic-password -a "$USER" -s "psi-api-key" -w` |
| `GA4_PROPERTY_ID` | `248106289` | Hardcoded — just paste this value |

After adding all three secrets, manually trigger the workflow:
1. Go to https://github.com/jjoson-ai/hairmnl-theme/actions/workflows/perf-dashboard.yml
2. Click "Run workflow" → "Run workflow"
3. Watch the run; if it succeeds, a new commit `chore: auto-refresh dashboard [skip ci]` will appear on `main`