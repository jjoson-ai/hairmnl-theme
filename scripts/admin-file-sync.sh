#!/usr/bin/env bash
# Pulls admin-managed JSON from live Shopify theme into a branch + PR when drift
# is detected. Spec: bd hairmnl-theme-4dw (do not hand-edit target files in normal
# theme work — this job mirrors live only).
set -euo pipefail

THEME_ID="${SHOPIFY_THEME_ID:-131664707683}"
STORE="${SHOPIFY_FLAG_STORE:?SHOPIFY_FLAG_STORE must be set}"
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

FILES=(
  templates/index.json
  templates/product.json
  templates/collection.json
  templates/cart.json
  config/settings_data.json
  config/settings_schema.json
)

body_file=""
PULL_ROOT="$(mktemp -d)"
cleanup() {
  rm -f "${body_file}"
  rm -rf "${PULL_ROOT}"
}
trap cleanup EXIT

only_args=()
for f in "${FILES[@]}"; do
  only_args+=(--only="$f")
done

shopify theme pull \
  --theme="${THEME_ID}" \
  --store="${STORE}" \
  --path="${PULL_ROOT}" \
  --nodelete \
  "${only_args[@]}"

changed=()
for f in "${FILES[@]}"; do
  pulled="${PULL_ROOT}/${f}"
  current="${REPO_ROOT}/${f}"
  if [[ ! -f "${pulled}" ]]; then
    echo "::error::Expected pulled file missing from theme: ${f}"
    exit 1
  fi
  if [[ ! -f "${current}" ]] || ! cmp -s "${pulled}" "${current}"; then
    changed+=("${f}")
  fi
done

if [[ ${#changed[@]} -eq 0 ]]; then
  echo "No differences vs repo HEAD — nothing to sync."
  exit 0
fi

echo "Files that differ from live: ${changed[*]}"

sync_date="$(date -u +%Y-%m-%d)"
branch="admin-sync/${sync_date}"

git config user.email "github-actions[bot]@users.noreply.github.com"
git config user.name "github-actions[bot]"

default_branch="${SYNC_DEFAULT_BRANCH:-main}"
git fetch origin "${default_branch}"
git checkout -B "${branch}" "origin/${default_branch}"

for f in "${changed[@]}"; do
  mkdir -p "$(dirname "${REPO_ROOT}/${f}")"
  cp -f "${PULL_ROOT}/${f}" "${REPO_ROOT}/${f}"
done

git add "${changed[@]}"
git commit -m "chore: sync admin-managed theme files from live (${sync_date})"

git push -u origin "${branch}"

list_md=""
for f in "${changed[@]}"; do
  list_md="${list_md}- \`${f}\`"$'\n'
done

body_file="$(mktemp)"
cat >"${body_file}" <<EOF
Automated sync of **admin-managed** Shopify Theme Editor files from **live** theme \`${THEME_ID}\` (store: \`${STORE}\`).

## Files updated

${list_md}
> These paths are edited in Shopify admin (Theme Editor), not in local theme PRs. Merge this PR to refresh git mirrors after admin changes.

Workflow: \`.github/workflows/admin-file-sync.yml\` (bd \`hairmnl-theme-4dw\`).
EOF

gh pr create \
  --base "${default_branch}" \
  --head "${branch}" \
  --title "chore: sync admin-managed theme files from live (${sync_date})" \
  --body-file "${body_file}"
