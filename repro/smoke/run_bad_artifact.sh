#!/usr/bin/env bash
# Bad-artifact smoke test.
#
# CONTRACT: this script exits 0 if and only if stage_gate.py correctly rejected
# the seeded-bad artifact (exited nonzero AND printed "ARTIFACT VALIDATION FAILED").
# Any other outcome — infrastructure crash, stage_gate.py accepting the artifact,
# missing rejection signature — exits nonzero with a distinct HARNESS ERROR or FAIL
# message. Callers (Makefile, CI) should treat exit 0 as PASS, nonzero as FAIL.
#
# This contract supersedes the previous inversion design where the caller inverted
# the exit code. Do NOT re-invert in the Makefile or CI workflow.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Resolve Python interpreter: honour $PYTHON if set, prefer python3, fall back to python
PYTHON="${PYTHON:-$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)}"
if [ -z "$PYTHON" ]; then
    echo "HARNESS ERROR: no Python interpreter found (tried python3, python)" >&2
    exit 2
fi

# Portable temp file — trailing X's, no suffix, works on both BSD (macOS) and GNU mktemp.
# The extension is irrelevant; stage_gate.py reads by path.
BAD_ARTIFACT_FILE="$(mktemp "${TMPDIR:-/tmp}/bad-artifact.XXXXXX")"
trap 'rm -f "$BAD_ARTIFACT_FILE"' EXIT

cat > "$BAD_ARTIFACT_FILE" <<'JSON'
{
  "artifact_id": "smoke/bad/seeded-bad-artifact-v1",
  "stage": "s7",
  "producer": {
    "agent": "data-scientist",
    "model": ""
  },
  "adversary": {},
  "git_commit": "",
  "depends_on": [],
  "evidence_class": "robust"
}
JSON

echo "Submitting bad artifact to stage_gate.py..."
echo "Artifact contents:"
cat "$BAD_ARTIFACT_FILE"
echo ""

# Capture both exit code and combined output; do not let set -e abort on nonzero.
GATE_OUTPUT="$("$PYTHON" "$REPO_ROOT/scripts/stage_gate.py" \
    --validate-artifact "$BAD_ARTIFACT_FILE" 2>&1)" && GATE_EXIT=0 || GATE_EXIT=$?

echo "stage_gate.py exit code: $GATE_EXIT"
echo "stage_gate.py output:"
echo "$GATE_OUTPUT"
echo ""

# Assert (a): stage_gate.py must have exited nonzero.
if [ "$GATE_EXIT" -eq 0 ]; then
    echo "FAIL: stage_gate.py accepted the bad artifact (exit 0). P0 exit criterion NOT MET."
    exit 1
fi

# Assert (b): output must contain the rejection signature — guards against crashes
# that exit nonzero for reasons unrelated to artifact validation.
REJECTION_SIGNATURE="ARTIFACT VALIDATION FAILED"
if ! echo "$GATE_OUTPUT" | grep -qF "$REJECTION_SIGNATURE"; then
    echo "HARNESS ERROR: stage_gate.py exited nonzero (exit $GATE_EXIT) but output did not" \
         "contain \"$REJECTION_SIGNATURE\". This looks like a crash, not a genuine rejection."
    echo "Full output was:"
    echo "$GATE_OUTPUT"
    exit 2
fi

echo "Bad-artifact smoke test PASSED — stage_gate.py correctly rejected the artifact" \
     "(exit $GATE_EXIT, rejection signature confirmed)."
exit 0
