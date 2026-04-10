#!/usr/bin/env bash
# mault-verify-step8.sh — Ralph Loop verification for Step 8: Governance Testing
# 14 CHECKs. Exit 0 only if ALL pass.
set -uo pipefail

PASS_COUNT=0
FAIL_COUNT=0
PENDING_COUNT=0
CHECK_RESULTS=()
TOTAL_CHECKS=14

PROOF_DIR=".mault"
PROOF_FILE="$PROOF_DIR/verify-step8.proof"

record_result() { CHECK_RESULTS+=("CHECK $1: $2 - $3"); }
print_pass()    { echo "[PASS]    CHECK $1: $2"; PASS_COUNT=$((PASS_COUNT + 1)); record_result "$1" "PASS" "$2"; }
print_fail()    { echo "[FAIL]    CHECK $1: $2"; FAIL_COUNT=$((FAIL_COUNT + 1)); record_result "$1" "FAIL" "$2"; }
print_pending() { echo "[PENDING] CHECK $1: $2"; PENDING_COUNT=$((PENDING_COUNT + 1)); record_result "$1" "PENDING" "$2"; }

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: Not a git repository."; exit 1
fi

if [ -f "$PROOF_FILE" ]; then
  PROOF_SHA=$(grep '^GitSHA:' "$PROOF_FILE" 2>/dev/null | awk '{print $2}')
  CURRENT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
  [ "$PROOF_SHA" != "$CURRENT_SHA" ] && rm -f "$PROOF_FILE"
fi

detect_default_branch() {
  local b; b=$(gh repo view --json defaultBranchRef -q '.defaultBranchRef.name' 2>/dev/null) || true
  [ -n "$b" ] && echo "$b" && return; echo "main"
}
DEFAULT_BRANCH=$(detect_default_branch)

echo "========================================"
echo "  MAULT Step 8 Governance Verification"
echo "  Default branch: $DEFAULT_BRANCH"
echo "========================================"
echo ""

# CHECK 1: Step 6 prerequisite
check_1() {
  [ -f ".mault/verify-step6.proof" ] || { print_fail 1 "Step 6 proof missing."; return; }
  local t; t=$(grep '^Token:' .mault/verify-step6.proof 2>/dev/null | awk '{print $2}')
  print_pass 1 "Step 6 proof exists (${t:-unknown})"
}

# CHECK 2: scripts/governance/ exists with scripts
check_2() {
  local count
  count=$(find scripts/governance -name '*.py' 2>/dev/null | wc -l | tr -d ' ')
  [ "${count:-0}" -ge 5 ] && print_pass 2 "scripts/governance/ has ${count} scripts" \
    || print_fail 2 "scripts/governance/ has only ${count} Python scripts (need ≥5)"
}

# CHECK 3: .memory-layer/baselines/ exists with baselines
check_3() {
  local count
  count=$(find .memory-layer/baselines -name '*.json' 2>/dev/null | wc -l | tr -d ' ')
  [ "${count:-0}" -ge 4 ] && print_pass 3 ".memory-layer/baselines/ has ${count} baseline files" \
    || print_fail 3 "Need ≥4 baseline files, found ${count}"
}

# CHECK 4: Silent catch gate passes
check_4() {
  python3 scripts/governance/check_silent_catches.py >/dev/null 2>&1 \
    && print_pass 4 "Silent catch ratchet passes" \
    || print_fail 4 "Silent catch ratchet failed"
}

# CHECK 5: Type hole gate passes
check_5() {
  python3 scripts/governance/check_type_holes.py >/dev/null 2>&1 \
    && print_pass 5 "Type hole ratchet passes" \
    || print_fail 5 "Type hole ratchet failed"
}

# CHECK 6: Lint suppression gate passes
check_6() {
  python3 scripts/governance/check_lint_suppressions.py >/dev/null 2>&1 \
    && print_pass 6 "Lint suppression ratchet passes" \
    || print_fail 6 "Lint suppression ratchet failed"
}

# CHECK 7: Mock tax gate passes
check_7() {
  python3 scripts/governance/check_mock_tax.py >/dev/null 2>&1 \
    && print_pass 7 "Mock tax (2x rule) passes" \
    || print_fail 7 "Mock tax gate failed"
}

# CHECK 8: SRP guardrails gate passes
check_8() {
  python3 scripts/governance/guardrails_check.py >/dev/null 2>&1 \
    && print_pass 8 "SRP guardrails pass" \
    || print_fail 8 "SRP guardrails failed"
}

# CHECK 9: Skipped test gate passes
check_9() {
  python3 scripts/governance/check_skipped_tests.py >/dev/null 2>&1 \
    && print_pass 9 "Skipped test gate passes" \
    || print_fail 9 "Skipped test gate failed"
}

# CHECK 10: CI has governance job
check_10() {
  grep -q 'governance' .github/workflows/ci.yml 2>/dev/null \
    && print_pass 10 "CI workflow has governance job" \
    || print_fail 10 "CI workflow missing governance job"
}

# CHECK 11: Gitleaks configured
check_11() {
  [ -f ".gitleaks.toml" ] && grep -q 'gitleaks' .github/workflows/ci.yml 2>/dev/null \
    && print_pass 11 ".gitleaks.toml exists and CI references gitleaks" \
    || print_fail 11 "Gitleaks configuration incomplete"
}

# CHECK 12: Governance manifest
check_12() {
  [ -f ".mault/governance-manifest.json" ] \
    && print_pass 12 ".mault/governance-manifest.json exists" \
    || print_fail 12 "Governance manifest missing"
}

# CHECK 13: Handshake commit with [mault-step8]
check_13() {
  local log_output match_count
  log_output=$(git log --all --format='%h %s' 2>/dev/null || true)
  match_count=$(printf '%s\n' "$log_output" | grep -c '\[mault-step8\]' || true)
  if [ "${match_count:-0}" -ge 1 ]; then
    local commit; commit=$(printf '%s\n' "$log_output" | grep '\[mault-step8\]' | head -1)
    print_pass 13 "Handshake commit: ${commit}"
  else
    print_fail 13 "No commit with [mault-step8] marker found"
  fi
}

# CHECK 14: Handshake issue
check_14() {
  local url
  url=$(gh issue list --search "[MAULT] Production Readiness: Step 8 Complete" --json url -q '.[0].url' 2>/dev/null) || true
  [ -z "$url" ] && url=$(gh issue list --state closed --search "[MAULT] Production Readiness: Step 8 Complete" --json url -q '.[0].url' 2>/dev/null) || true
  [ -n "$url" ] && print_pass 14 "Handshake issue: ${url}" \
    || print_pending 14 "No handshake issue found"
}

check_1; check_2; check_3; check_4; check_5; check_6; check_7
check_8; check_9; check_10; check_11; check_12; check_13; check_14

echo ""
echo "========================================"
echo "  PASS: ${PASS_COUNT}/${TOTAL_CHECKS}  FAIL: ${FAIL_COUNT}/${TOTAL_CHECKS}  PENDING: ${PENDING_COUNT}/${TOTAL_CHECKS}"
echo "========================================"

if [ "$FAIL_COUNT" -eq 0 ] && [ "$PENDING_COUNT" -eq 0 ]; then
  sha=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
  epoch=$(date +%s); iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date +"%Y-%m-%dT%H:%M:%S")
  token="MAULT-STEP8-${sha}-${epoch}-${TOTAL_CHECKS}/${TOTAL_CHECKS}"
  mkdir -p "$PROOF_DIR"
  { echo "MAULT-STEP8-PROOF"; echo "=================="; echo "Timestamp: $epoch"
    echo "DateTime: $iso"; echo "GitSHA: $sha"; echo "Checks: ${TOTAL_CHECKS}/${TOTAL_CHECKS} PASS"
    for r in "${CHECK_RESULTS[@]}"; do echo "  $r"; done
    echo "=================="; echo "Token: $token"; } > "$PROOF_FILE"
  echo ""; echo "Proof file written: $PROOF_FILE"; echo "Token: $token"
  echo "ALL CHECKS PASSED. Step 8 Governance Testing is complete."; exit 0
elif [ "$FAIL_COUNT" -gt 0 ]; then
  rm -f "$PROOF_FILE"; echo "${FAIL_COUNT} check(s) FAILED."; exit 1
else
  rm -f "$PROOF_FILE"; echo "${PENDING_COUNT} check(s) PENDING."; exit 1
fi
