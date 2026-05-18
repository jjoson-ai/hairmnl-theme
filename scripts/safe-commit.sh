#!/usr/bin/env bash
# safe-commit.sh — explicit-file-list commit wrapper to prevent
# MIGRATION-CONTRACT §5 #6 coordination-collision bundling.
#
# THE PROBLEM
#
# `bd` (beads) auto-runs `git add` on modified files when any bd command
# runs (`bd update`, `bd close`, `bd export`, etc.). If an OC swarm is
# writing files to the working tree while CC is editing bd state, those
# OC-written files get staged silently. A subsequent CC `git commit` —
# even one preceded by a targeted `git add <my-file>` — will sweep them
# all into the commit because they were already staged.
#
# This pattern hit 5 separate times in the 2026-05-18 evening session
# (commits 5097433, 662cb0d, 691fa2d, 0778d71, ujg6.19 close).
#
# THE FIX
#
# Stage explicitly. This wrapper:
#   1. Runs `git restore --staged .` (unstages everything bd touched)
#   2. Runs `git add <files>` with ONLY the files you list
#   3. Shows `git diff --cached --stat` for visual confirmation
#   4. Runs `git commit -m "<message>"` with the verified staging set
#
# USAGE
#
#   bash scripts/safe-commit.sh -m "message" file1 file2 file3
#
#   # With multi-line message via heredoc:
#   bash scripts/safe-commit.sh -F <(cat <<'EOF'
#   fix: something
#
#   Long description.
#   EOF
#   ) sections/foo.liquid snippets/bar.liquid
#
# OPTIONS
#
#   -m "<msg>"  Single-line commit message (required if -F not used)
#   -F <file>   Read commit message from file (use /dev/stdin or heredoc)
#   --dry-run   Show what would be staged + the diff, do not commit
#   --force     Skip the diff confirmation pause (for fully-automated runs)
#
# EXIT CODES
#
#   0   commit created successfully
#   1   argument / usage error
#   2   no files staged after the explicit add (nothing to commit)
#   3   the staged diff included files NOT in the requested list (sanity-
#       check failure — should never happen unless `git add` is itself
#       triggering hooks that mutate the index)
#
# WHY NOT A PRE-COMMIT HOOK
#
# bd legitimately runs `git add` as part of its auto-export workflow.
# A blocking pre-commit hook would break that. This wrapper is the
# proactive tool — call it instead of `git commit` when you care about
# precise staging. The hook layer stays for the wiring-lint pre-push
# guard (.githooks/pre-push) where blocking is appropriate.

set -euo pipefail

usage() {
    cat <<EOF >&2
Usage: $0 (-m "msg" | -F msg-file) [--dry-run] [--force] <file1> [<file2> ...]

See script header for full documentation. The MIGRATION-CONTRACT §5 #6
section explains the bundling-collision pattern this prevents.
EOF
    exit 1
}

MESSAGE=""
MESSAGE_FILE=""
DRY_RUN=0
FORCE=0
FILES=()

while (( $# > 0 )); do
    case "$1" in
        -m)
            MESSAGE="$2"; shift 2;;
        -F)
            MESSAGE_FILE="$2"; shift 2;;
        --dry-run)
            DRY_RUN=1; shift;;
        --force)
            FORCE=1; shift;;
        -h|--help)
            usage;;
        --)
            shift; FILES+=("$@"); break;;
        -*)
            echo "✗ Unknown option: $1" >&2; usage;;
        *)
            FILES+=("$1"); shift;;
    esac
done

if [[ -z "$MESSAGE" && -z "$MESSAGE_FILE" ]]; then
    echo "✗ Need -m \"message\" OR -F message-file" >&2
    usage
fi

if (( ${#FILES[@]} == 0 )); then
    echo "✗ No files specified. List the files to commit explicitly." >&2
    usage
fi

REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"

# Sanity: every requested file must exist (uncommitted or committed; we
# allow new files staged for add)
for f in "${FILES[@]}"; do
    if [[ ! -e "$f" ]]; then
        echo "✗ File does not exist: $f" >&2
        exit 1
    fi
done

# Step 1: snapshot the current staging set for diagnostic + show what
# bd / external processes had pre-staged. We log this — it's the
# evidence of the collision pattern if anything was there.
PRE_STAGED="$(git diff --cached --name-only)"
if [[ -n "$PRE_STAGED" ]]; then
    echo "→ Note: the following files were pre-staged (likely by bd auto-export):" >&2
    echo "$PRE_STAGED" | sed 's/^/    /' >&2
    echo "  These will be unstaged. They remain modified in the working tree." >&2
    echo "" >&2
fi

# Step 2: unstage everything
git restore --staged . 2>/dev/null || true

# Step 3: stage explicitly
echo "→ Staging only the requested files:" >&2
for f in "${FILES[@]}"; do
    git add -- "$f"
    echo "    + $f" >&2
done
echo "" >&2

# Step 4: sanity-check the staged set
STAGED_AFTER="$(git diff --cached --name-only | sort -u)"
EXPECTED="$(printf '%s\n' "${FILES[@]}" | sort -u)"
if [[ "$STAGED_AFTER" != "$EXPECTED" ]]; then
    echo "✗ Sanity-check failed: staged set does not match requested file list." >&2
    echo "  Requested:" >&2; echo "$EXPECTED" | sed 's/^/    /' >&2
    echo "  Actually staged:" >&2; echo "$STAGED_AFTER" | sed 's/^/    /' >&2
    echo "  (If you see EXTRA files, a git hook in this repo is mutating the index;" >&2
    echo "   if files are MISSING, check the requested paths.)" >&2
    exit 3
fi

# Step 5: show the diff stat for confirmation
echo "→ Staged diff:" >&2
git diff --cached --stat | sed 's/^/    /' >&2
echo "" >&2

if (( DRY_RUN )); then
    echo "→ --dry-run: not committing." >&2
    exit 0
fi

if (( ! FORCE )); then
    # Brief readable pause — not interactive (don't break automation)
    # but gives a visual marker between staging and commit.
    echo "→ Committing in 0.5s …" >&2
    sleep 0.5
fi

# Step 6: commit
if [[ -n "$MESSAGE_FILE" ]]; then
    git commit -F "$MESSAGE_FILE"
else
    git commit -m "$MESSAGE"
fi
