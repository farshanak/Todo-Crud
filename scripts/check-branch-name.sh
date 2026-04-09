#!/usr/bin/env bash
# Enforces branch naming convention: <type>/<description>
# Allowed types: feat, fix, docs, chore, refactor, test, deps, ci, style, perf
# Default branches (main/master/develop) are always allowed so that hooks
# run cleanly on the trunk.

set -euo pipefail

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

# Allow default branches and detached HEAD (e.g. during rebase / merge)
case "$BRANCH" in
  main|master|develop|HEAD|"")
    exit 0
    ;;
esac

# Allow Mault kit branches (step<N>/...)
if [[ "$BRANCH" =~ ^step[0-9]+/.+ ]]; then
  exit 0
fi

PATTERN='^(feat|fix|docs|chore|refactor|test|deps|ci|style|perf)/.+'

if [[ ! "$BRANCH" =~ $PATTERN ]]; then
  echo "Invalid branch name: $BRANCH" >&2
  echo "Branch must match: feat|fix|docs|chore|refactor|test|deps|ci|style|perf/<description>" >&2
  echo "Example: feat/add-login, fix/timeout-bug" >&2
  exit 1
fi

exit 0
