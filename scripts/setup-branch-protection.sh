#!/usr/bin/env bash
# setup-branch-protection.sh
#
# Configures GitHub branch protection rules for hc-grc using the gh CLI.
# Enforces the required status checks documented in docs/CI.md.
#
# Usage:
#   bash scripts/setup-branch-protection.sh            # apply rules
#   bash scripts/setup-branch-protection.sh --dry-run  # print what would be configured
#
# Requirements:
#   - gh CLI installed and authenticated (gh auth status)
#   - Write access to the repository (admin for branch protection)

set -euo pipefail

REPO="thehipsterciso/hc-grc"
DRY_RUN=false

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "[DRY-RUN] No changes will be applied."
fi

run_or_print() {
  if $DRY_RUN; then
    echo "[DRY-RUN] Would run: $*"
  else
    "$@"
  fi
}

echo ""
echo "=== hc-grc branch protection setup ==="
echo "Repository: $REPO"
echo ""

# ---------------------------------------------------------------------------
# Required checks for main
# ---------------------------------------------------------------------------
# All 9 CI workflows must pass before merging to main.
# certificate-completeness/validate-all-for-main is the job name for PRs to main.

MAIN_REQUIRED_CHECKS=(
  "registry-validate / validate"
  "provenance-integrity / provenance"
  "independence-lint / independence"
  "python-quality / quality"
  "lint-docs / required-docs"
  "lint-docs / markdown-links"
  "repro-smoke / smoke"
  "agent-sync-check / agent-sync"
  "certificate-completeness / validate-all-for-main"
)

echo "--- Configuring main branch protection ---"
echo "Required status checks:"
for check in "${MAIN_REQUIRED_CHECKS[@]}"; do
  echo "  - $check"
done
echo "Required reviews: 1"
echo "Direct push: blocked"
echo ""

# Build the required-checks JSON array
CHECKS_JSON=$(printf '%s\n' "${MAIN_REQUIRED_CHECKS[@]}" | jq -R . | jq -s .)

run_or_print gh api \
  --method PUT \
  "repos/${REPO}/branches/main/protection" \
  --field "required_status_checks[strict]=true" \
  --field "required_status_checks[contexts]=$(echo "$CHECKS_JSON")" \
  --field "enforce_admins=false" \
  --field "required_pull_request_reviews[required_approving_review_count]=1" \
  --field "required_pull_request_reviews[dismiss_stale_reviews]=true" \
  --field "restrictions=null"

echo "Main branch protection configured."
echo ""

# ---------------------------------------------------------------------------
# Required checks for stage/framework/synthesis branches
# ---------------------------------------------------------------------------
# These branches also require certificate-completeness / stage-gate (per-stage check).

STAGE_EXTRA_CHECK="certificate-completeness / stage-gate"

STAGE_REQUIRED_CHECKS=(
  "${MAIN_REQUIRED_CHECKS[@]}"
  "$STAGE_EXTRA_CHECK"
)

STAGE_PATTERNS=(
  "stage/*"
  "scf/*"
  "nist-800-53/*"
  "nist-csf-2.0/*"
  "nist-800-171/*"
  "cis-v8/*"
  "synthesis/*"
)

echo "--- Configuring stage/framework/synthesis branch protection ---"
echo "Branch patterns: ${STAGE_PATTERNS[*]}"
echo "Required status checks (all main checks + certificate-completeness / stage-gate):"
for check in "${STAGE_REQUIRED_CHECKS[@]}"; do
  echo "  - $check"
done
echo ""

STAGE_CHECKS_JSON=$(printf '%s\n' "${STAGE_REQUIRED_CHECKS[@]}" | jq -R . | jq -s .)

for PATTERN in "${STAGE_PATTERNS[@]}"; do
  echo "  Applying to pattern: $PATTERN"
  # gh CLI branch protection requires exact branch names; for wildcards use rulesets API
  run_or_print gh api \
    --method POST \
    "repos/${REPO}/rulesets" \
    --field "name=stage-branch-protection-${PATTERN//\//-}" \
    --field "target=branch" \
    --field "enforcement=active" \
    --field "conditions[ref_name][include][]=$PATTERN" \
    --field "conditions[ref_name][exclude][]=" \
    --field "rules[0][type]=required_status_checks" \
    --field "rules[0][parameters][required_status_checks]=$(echo "$STAGE_CHECKS_JSON")" \
    --field "rules[0][parameters][strict_required_status_checks_policy]=false" \
    2>/dev/null || echo "  Note: ruleset for $PATTERN may already exist or require admin access."
done

echo ""
echo "--- Configuring all-branch minimum checks ---"
echo "All branches require:"
echo "  - registry-validate / validate"
echo "  - provenance-integrity / provenance"
echo "  - python-quality / quality"
echo ""

# All-branch ruleset (including feature branches)
ALL_BRANCH_CHECKS='["registry-validate / validate","provenance-integrity / provenance","python-quality / quality"]'
run_or_print gh api \
  --method POST \
  "repos/${REPO}/rulesets" \
  --field "name=all-branch-minimum-checks" \
  --field "target=branch" \
  --field "enforcement=active" \
  --field "conditions[ref_name][include][]=~ALL" \
  --field "conditions[ref_name][exclude][]=main" \
  --field "rules[0][type]=required_status_checks" \
  --field "rules[0][parameters][required_status_checks]=${ALL_BRANCH_CHECKS}" \
  --field "rules[0][parameters][strict_required_status_checks_policy]=false" \
  2>/dev/null || echo "Note: all-branch ruleset may already exist or require admin access."

echo ""
if $DRY_RUN; then
  echo "[DRY-RUN] Done. No changes applied."
else
  echo "Branch protection configuration complete."
  echo "Verify at: https://github.com/${REPO}/settings/branches"
fi
