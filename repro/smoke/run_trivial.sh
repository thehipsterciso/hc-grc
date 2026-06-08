#!/usr/bin/env bash
# Trivial deterministic smoke test.
# Hashes a fixed input string and writes the result to stdout.
# The repro-smoke workflow captures stdout, sha256s it, and compares
# against repro/smoke/expected_output.sha256.
#
# This task is intentionally minimal — the point is byte-identical
# reproducibility, not scientific content.
set -euo pipefail

FIXED_INPUT="hc-grc-repro-smoke-v1"

# sha256sum output: "<hash>  -\n"
# We print exactly that so the outer check can hash this script's stdout
# and compare against the pre-computed expected hash.
echo -n "$FIXED_INPUT" | sha256sum
