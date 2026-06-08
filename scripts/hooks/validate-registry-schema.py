#!/usr/bin/env python3
"""
Validate registry and ledger JSON files against schema.

Run as a pre-commit hook to catch schema errors before they're committed.
Validates:
  - registry/*.json (artifact entries)
  - ledger/certificates/*.json (certificate entries)
"""

import json
import subprocess
import sys
from pathlib import Path


def get_staged_registry_files() -> list[str]:
    """Get staged registry and ledger files."""
    try:
        output = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only"],
            text=True,
        )
        return [
            f
            for f in output.strip().split("\n")
            if f and (f.startswith("registry/") or f.startswith("ledger/")) and f.endswith(".json")
        ]
    except subprocess.CalledProcessError:
        return []


def validate_artifact_schema(artifact: dict) -> list[str]:
    """Validate artifact entry against expected schema."""
    errors = []

    required_fields = ["artifact_id", "artifact_type", "stage_id", "certificate_ref"]
    for field in required_fields:
        if field not in artifact:
            errors.append(f"Missing required field: {field}")

    # Validate artifact_type is known
    artifact_type = artifact.get("artifact_type")
    valid_types = {
        "orchestration-harness",
        "test-automation-suite",
        "agent-roster",
        "preregistration-document",
        "research-questions",
        "analysis-plans",
        "decision-rules",
        "synthetic-corpus",
        "method-validation-results",
        "validated-methods-registry",
        "framework-instantiation",
        "control-taxonomy",
        "question-bindings",
        "control-assets",
        "corpus-metadata",
        "lineage-record",
        "crosswalk",
        "enriched-control-text",
        "embedding-model-1",
        "embedding-model-2",
        "embedding-model-3",
        "embedding-selection-criterion",
        "construct-validity-report",
        "cross-model-cka",
        "dimensionality-analysis",
        "cluster-tendency",
        "statistical-investigation",
        "bootstrap-confidence-intervals",
        "robust-finding-certificate",
        "provisional-finding-certificate",
        "evidence-dependency-graph",
        "triangulation-report",
        "robustness-classification",
        "replication-study-results",
        "replication-certificate",
        "alignment-mapping",
        "crosswalk-quality-report",
        "aligned-control-sets",
        "replication-matrix",
        "intrinsic-findings",
        "framework-specific-findings",
        "crosswalk-dependent-findings",
        "insight-and-gap-report",
        "evidence-classification-map",
        "limitation-report",
        "stance-document",
        "evidence-traceability-map",
        "overclaim-resistance-report",
        "scientific-record",
        "leadership-summary",
        "reproducibility-package",
        "run-instructions",
    }
    if artifact_type and artifact_type not in valid_types:
        errors.append(f"Unknown artifact_type: {artifact_type}")

    # Validate stage_id format
    stage_id = artifact.get("stage_id")
    valid_stages = {"P0", "P1", "S1f", "S3", "S4", "S5", "S6", "S7", "S8f", "S9",
                    "X1", "X2", "X3", "X4", "X5"}
    if stage_id and stage_id not in valid_stages:
        errors.append(f"Invalid stage_id: {stage_id}")

    # Validate framework if present
    framework = artifact.get("framework")
    valid_frameworks = {"scf", "nist-800-53", "nist-800-171", "nist-csf-2.0", "cis-v8"}
    if framework and framework not in valid_frameworks:
        errors.append(f"Invalid framework: {framework}")

    return errors


def validate_certificate_schema(cert: dict) -> list[str]:
    """Validate certificate entry against expected schema."""
    errors = []

    required_fields = ["artifact_id", "producer", "adversary", "verdict", "stance"]
    for field in required_fields:
        if field not in cert:
            errors.append(f"Missing required field: {field}")

    # Validate verdict
    verdict = cert.get("verdict")
    if verdict and verdict not in {"ACCEPT", "REJECT", "DEFER"}:
        errors.append(f"Invalid verdict: {verdict}")

    # Validate stance
    stance = cert.get("stance")
    valid_stances = {
        "independent-reconstruction",
        "falsification-probe",
        "competing-hypotheses",
        "assumption-ledger",
        "premortem",
    }
    if stance and stance not in valid_stances:
        errors.append(f"Invalid stance: {stance}")

    return errors


def main():
    """Validate staged registry/ledger files."""
    repo_root = Path(__file__).parent.parent.parent
    staged_files = get_staged_registry_files()

    if not staged_files:
        return 0

    all_errors = []

    for fpath_str in staged_files:
        fpath = repo_root / fpath_str

        if not fpath.exists():
            continue

        try:
            with open(fpath) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            all_errors.append(f"{fpath_str}: Invalid JSON: {e}")
            continue

        # Validate schema based on file type
        if "registry/" in fpath_str:
            errors = validate_artifact_schema(data)
        elif "ledger/certificates/" in fpath_str:
            errors = validate_certificate_schema(data)
        else:
            # Unknown registry/ledger file; skip
            continue

        if errors:
            all_errors.append(f"{fpath_str}:")
            for err in errors:
                all_errors.append(f"  • {err}")

    if all_errors:
        for msg in all_errors:
            print(msg, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
