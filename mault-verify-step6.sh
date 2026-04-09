#!/usr/bin/env bash
# mault-verify-step6.sh — Ralph Loop verification for Step 6: Pre-commit Hooks
# 12 CHECKs. Exit 0 only if ALL pass.
set -uo pipefail

PASS_COUNT=0
FAIL_COUNT=0
PENDING_COUNT=0
CHECK_RESULTS=()
TOTAL_CHECKS=12

PROOF_DIR=".mault"
PROOF_FILE="$PROOF_DIR/verify-step6.proof"

record_result() { CHECK_RESULTS+=("CHECK $1: $2 - $3"); }
print_pass()    { echo "[PASS]    CHECK $1: $2"; PASS_COUNT=$((PASS_COUNT + 1)); record_result "$1" "PASS" "$2"; }
print_fail()    { echo "[FAIL]    CHECK $1: $2"; FAIL_COUNT=$((FAIL_COUNT + 1)); record_result "$1" "FAIL" "$2"; }
print_pending() { echo "[PENDING] CHECK $1: $2"; PENDING_COUNT=$((PENDING_COUNT + 1)); record_result "$1" "PENDING" "$2"; }

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: Not a git repository."
  exit 1
fi

if [ -f "$PROOF_FILE" ]; then
  PROOF_SHA=$(grep '^GitSHA:' "$PROOF_FILE" 2>/dev/null | awk '{print $2}')
  CURRENT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
  if [ "$PROOF_SHA" != "$CURRENT_SHA" ]; then
    echo "Stale proof detected ($PROOF_SHA vs $CURRENT_SHA). Deleting."
    rm -f "$PROOF_FILE"
  fi
fi

detect_default_branch() {
  local branch
  branch=$(gh repo view --json defaultBranchRef -q '.defaultBranchRef.name' 2>/dev/null) || true
  if [ -n "$branch" ]; then echo "$branch"; return; fi
  echo "main"
}
DEFAULT_BRANCH=$(detect_default_branch)

echo "========================================"
echo "  MAULT Step 6 Pre-commit Verification"
echo "  Default branch: $DEFAULT_BRANCH"
echo "========================================"
echo ""

# --- CHECK 1: Step 5 prerequisite ---
check_1() {
  if [ ! -f ".mault/verify-step5.proof" ]; then
    print_fail 1 "Step 5 not complete. Run mault-verify-step5.sh first."
    return
  fi
  local token
  token=$(grep '^Token:' .mault/verify-step5.proof 2>/dev/null | awk '{print $2}')
  print_pass 1 "Step 5 proof exists (${token:-unknown})"
}

# --- CHECK 2: pre-commit CLI installed ---
check_2() {
  if command -v pre-commit >/dev/null 2>&1; then
    local version
    version=$(pre-commit --version 2>/dev/null)
    print_pass 2 "pre-commit installed (${version})"
  else
    print_fail 2 "pre-commit not installed. Run: pip install pre-commit"
  fi
}

# --- CHECK 3: pre-commit config exists ---
check_3() {
  if [ -f ".pre-commit-config.yaml" ] || [ -f ".pre-commit-config.yml" ]; then
    print_pass 3 "Pre-commit config file exists"
  else
    print_fail 3 "No .pre-commit-config.yaml found."
  fi
}

# --- CHECK 4: Git hook installed ---
check_4() {
  if [ -x ".git/hooks/pre-commit" ] && grep -q 'pre-commit' .git/hooks/pre-commit 2>/dev/null; then
    print_pass 4 "Git pre-commit hook installed and executable"
  else
    print_fail 4 "Git pre-commit hook not installed. Run: pre-commit install"
  fi
}

# --- CHECK 5: detect-secrets baseline exists ---
check_5() {
  if [ -f ".secrets.baseline" ]; then
    print_pass 5 ".secrets.baseline exists"
  else
    print_fail 5 "No .secrets.baseline. Generate with: detect-secrets scan > .secrets.baseline"
  fi
}

# --- CHECK 6: Branch name script exists ---
check_6() {
  if [ -x "scripts/check-branch-name.sh" ]; then
    print_pass 6 "Branch naming script exists and is executable"
  else
    print_fail 6 "scripts/check-branch-name.sh missing or not executable."
  fi
}

# --- CHECK 7: All hooks pass on changed files ---
check_7() {
  if ! command -v pre-commit >/dev/null 2>&1; then
    print_fail 7 "pre-commit not installed (prerequisite for CHECK 7)."
    return
  fi
  if pre-commit run --all-files >/tmp/mault-precommit.log 2>&1; then
    print_pass 7 "pre-commit run --all-files passes cleanly"
  else
    print_fail 7 "pre-commit hooks failed. See /tmp/mault-precommit.log"
  fi
}

# --- CHECK 8: CI has validate-pr-title and validate-branch-name ---
check_8() {
  local ci_file=".github/workflows/ci.yml"
  if [ ! -f "$ci_file" ]; then
    print_fail 8 "No CI workflow found."
    return
  fi
  if ! grep -q 'validate-pr-title' "$ci_file"; then
    print_fail 8 "CI missing validate-pr-title job."
    return
  fi
  if ! grep -q 'validate-branch-name' "$ci_file"; then
    print_fail 8 "CI missing validate-branch-name job."
    return
  fi
  print_pass 8 "CI workflow has validate-pr-title and validate-branch-name jobs"
}

# --- CHECK 9: Both CI jobs are required in branch protection ---
check_9() {
  local owner repo protection
  owner=$(gh repo view --json owner -q '.owner.login' 2>/dev/null) || true
  repo=$(gh repo view --json name -q '.name' 2>/dev/null) || true
  if [ -z "$owner" ] || [ -z "$repo" ]; then
    print_fail 9 "Cannot determine repo owner/name."
    return
  fi
  protection=$(gh api "repos/${owner}/${repo}/branches/${DEFAULT_BRANCH}/protection/required_status_checks" -q '.contexts[]' 2>/dev/null) || true
  if [ -z "$protection" ]; then
    print_fail 9 "No branch protection on ${DEFAULT_BRANCH}."
    return
  fi
  local missing=""
  echo "$protection" | grep -qF "validate-pr-title" || missing="${missing} validate-pr-title"
  echo "$protection" | grep -qF "validate-branch-name" || missing="${missing} validate-branch-name"
  if [ -n "$missing" ]; then
    print_fail 9 "Missing required checks:${missing}"
    return
  fi
  print_pass 9 "validate-pr-title and validate-branch-name required in branch protection"
}

# --- CHECK 10: Handshake commit with [mault-step6] marker ---
check_10() {
  if git log --all --format='%s' 2>/dev/null | grep -q '\[mault-step6\]'; then
    local commit
    commit=$(git log --all --format='%h %s' | grep '\[mault-step6\]' | head -1)
    print_pass 10 "Handshake commit found: ${commit}"
  else
    print_fail 10 "No commit with [mault-step6] marker found."
  fi
}

# --- CHECK 11: Pre-commit manifest exists ---
check_11() {
  if [ -f ".mault/pre-commit-manifest.json" ]; then
    print_pass 11 ".mault/pre-commit-manifest.json exists"
  else
    print_fail 11 "No pre-commit manifest."
  fi
}

# --- CHECK 12: Handshake issue exists ---
check_12() {
  if ! command -v gh >/dev/null 2>&1; then
    print_pending 12 "gh CLI not available."
    return
  fi
  local issue_url
  issue_url=$(gh issue list --search "[MAULT] Production Readiness: Step 6 Complete" --json url -q '.[0].url' 2>/dev/null) || true
  if [ -z "$issue_url" ]; then
    issue_url=$(gh issue list --state closed --search "[MAULT] Production Readiness: Step 6 Complete" --json url -q '.[0].url' 2>/dev/null) || true
  fi
  if [ -n "$issue_url" ]; then
    print_pass 12 "Handshake issue: ${issue_url}"
  else
    print_pending 12 "No handshake issue found."
  fi
}

check_1
check_2
check_3
check_4
check_5
check_6
check_7
check_8
check_9
check_10
check_11
check_12

echo ""
echo "========================================"
echo "  PASS: ${PASS_COUNT}/${TOTAL_CHECKS}  FAIL: ${FAIL_COUNT}/${TOTAL_CHECKS}  PENDING: ${PENDING_COUNT}/${TOTAL_CHECKS}"
echo "========================================"

if [ "$FAIL_COUNT" -eq 0 ] && [ "$PENDING_COUNT" -eq 0 ]; then
  sha=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
  epoch=$(date +%s)
  iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date +"%Y-%m-%dT%H:%M:%S")
  token="MAULT-STEP6-${sha}-${epoch}-${TOTAL_CHECKS}/${TOTAL_CHECKS}"
  mkdir -p "$PROOF_DIR"
  if [ ! -f "$PROOF_DIR/.gitignore" ]; then
    printf '*\n!.gitignore\n' > "$PROOF_DIR/.gitignore"
  fi
  {
    echo "MAULT-STEP6-PROOF"
    echo "=================="
    echo "Timestamp: $epoch"
    echo "DateTime: $iso"
    echo "GitSHA: $sha"
    echo "Checks: ${TOTAL_CHECKS}/${TOTAL_CHECKS} PASS"
    for r in "${CHECK_RESULTS[@]}"; do
      echo "  $r"
    done
    echo "=================="
    echo "Token: $token"
  } > "$PROOF_FILE"
  echo ""
  echo "Proof file written: $PROOF_FILE"
  echo "Token: $token"
  echo "ALL CHECKS PASSED. Step 6 Pre-commit Framework is complete."
  exit 0
elif [ "$FAIL_COUNT" -gt 0 ]; then
  rm -f "$PROOF_FILE"
  echo "${FAIL_COUNT} check(s) FAILED. Fix and re-run."
  exit 1
else
  rm -f "$PROOF_FILE"
  echo "${PENDING_COUNT} check(s) PENDING. Complete work and re-run."
  exit 1
fi
