#!/bin/bash
# Enforce independence rule: a per-framework stage branch must not contain
# commits from another framework's stage branch before it merges to main.
#
# This hook validates that the current branch (if a per-framework stage) has no
# commits that were authored on a different framework's stage branch.
#
# Rationale: per-framework studies are parallel and independent by design.
# Cross-framework commits break independence and must be resolved via rebase,
# not merge.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Only check per-framework stage branches
if ! [[ "$CURRENT_BRANCH" =~ ^(scf|nist-[a-z0-9-]+|cis-v8)/ ]]; then
  exit 0
fi

# Extract framework from branch name
CURRENT_FRAMEWORK="${CURRENT_BRANCH%%/*}"

# Get all commits in current branch not yet in main
COMMITS=$(git rev-list main..HEAD 2>/dev/null || echo "")

if [ -z "$COMMITS" ]; then
  exit 0
fi

# For each commit, check if it belongs to another framework's branch
VIOLATIONS=0
for commit in $COMMITS; do
  # Get all branches that contain this commit (excluding main and current branch)
  BRANCHES=$(
    git branch -r --contains "$commit" 2>/dev/null |
      grep -v '^.*main$' |
      grep -v "^.*$CURRENT_BRANCH$" ||
      true
  )

  # Check if any branch is from a different framework
  for branch in $BRANCHES; do
    # Extract framework from branch name (format: scope/stage-slug)
    branch_clean="${branch##*/}"  # Remove remote origin
    branch_scope="${branch_clean%%/*}"

    # If a different framework's stage branch contains this commit, flag it
    if [[ "$branch_scope" =~ ^(scf|nist-[a-z0-9-]+|cis-v8)$ ]]; then
      if [ "$branch_scope" != "$CURRENT_FRAMEWORK" ]; then
        echo "ERROR: Cross-framework commit detected"
        echo "  Commit: $commit"
        echo "  Current branch: $CURRENT_BRANCH (framework: $CURRENT_FRAMEWORK)"
        echo "  Also in: $branch (framework: $branch_scope)"
        echo ""
        echo "Per-framework stages must remain independent. Resolve by:"
        echo "  1. Rebase this branch onto main (not merge): git rebase main"
        echo "  2. Force-push if needed: git push --force-with-lease"
        VIOLATIONS=$((VIOLATIONS + 1))
      fi
    fi
  done
done

exit $VIOLATIONS
