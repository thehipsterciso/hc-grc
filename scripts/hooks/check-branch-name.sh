#!/bin/bash
# Validate branch name format on push.
#
# Allowed patterns:
#   stage/<stage-slug>          (e.g., stage/P0-setup, stage/S3-method-validation)
#   <framework>/<stage-slug>    (e.g., scf/S4-corpus, nist-800-53/S5-embedding)
#
# Invalid:
#   feature/foo (wrong pattern)
#   SCF/S4 (uppercase)
#   scf/S4_corpus (underscore)
#   scf/s4-corpus (lowercase stage number)

set -euo pipefail

BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Allow main and other special branches
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ] || [ "$BRANCH" = "HEAD" ]; then
  exit 0
fi

# Pattern: stage/<slug> or <framework>/<slug>
PATTERN='^(stage|scf|nist-800-53|nist-800-171|nist-csf-2\.0|cis-v8)/[a-z0-9]([a-z0-9-]*[a-z0-9])?$'

if ! [[ "$BRANCH" =~ $PATTERN ]]; then
  echo "ERROR: Invalid branch name: '$BRANCH'"
  echo ""
  echo "Branch names must match: <scope>/<stage-slug>"
  echo "  scope: stage, scf, nist-800-53, nist-800-171, nist-csf-2.0, cis-v8"
  echo "  stage-slug: lowercase, hyphen-separated (e.g., S4-corpus, X1-alignment)"
  echo ""
  echo "Examples of valid names:"
  echo "  stage/P0-setup"
  echo "  scf/S4-corpus"
  echo "  nist-800-53/S5-embedding"
  echo "  synthesis/X1-alignment"
  exit 1
fi

exit 0
