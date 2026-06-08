#!/usr/bin/env python3
"""
hc-grc stage gate enforcement.

Validates that all required artifacts for a stage are registered and certified
before that stage may merge to main. Enforces Tier B minimum framework count.

Usage:
  python scripts/stage_gate.py --stage S4 --framework scf
  python scripts/stage_gate.py --stage P1 --all
  python scripts/stage_gate.py --validate
  python scripts/stage_gate.py --tier-b-check
"""

import json
import sys
from pathlib import Path
from typing import Any

import jsonschema
import yaml


class StageGateValidator:
    """Validates stage gates against registry and ledger."""

    def __init__(
        self,
        repo_root: Path | None = None,
        gates_file: Path | None = None,
    ):
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.gates_file = gates_file or self.repo_root / "docs" / "STAGE_GATES.yaml"
        self.registry_dir = self.repo_root / "registry"
        self.ledger_dir = self.repo_root / "ledger"

        self.gates = self._load_gates()
        self.frameworks = self.gates.get("frameworks", [])
        self.artifact_types = set(self.gates.get("artifact_types", []))
        self.artifact_schema = self._load_artifact_schema()

    def _load_artifact_schema(self) -> dict[str, Any] | None:
        """Load the artifact JSON schema for validation."""
        schema_path = self.registry_dir / "schema" / "artifact.schema.json"
        try:
            with open(schema_path) as f:
                return json.load(f)
        except Exception:
            return None

    def _load_gates(self) -> dict[str, Any]:
        """Load stage gates definition from YAML."""
        try:
            with open(self.gates_file) as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise RuntimeError(f"Failed to load gates from {self.gates_file}: {e}")

    def _load_registry_artifacts(
        self,
        stage: str,
        framework: str | None = None,
    ) -> list[dict[str, Any]]:
        """Load all registry entries for a stage (+ framework if specified)."""
        artifacts = []
        registry_files = list(self.registry_dir.glob("**/*.json"))

        for fpath in registry_files:
            try:
                with open(fpath) as f:
                    artifact = json.load(f)
            except Exception:
                continue

            # Filter by stage and framework
            if artifact.get("stage_id") != stage:
                continue
            if framework is not None and artifact.get("framework") != framework:
                continue

            artifacts.append(artifact)

        return artifacts

    def _load_certificate(self, cert_ref: str) -> dict[str, Any] | None:
        """Load a certificate from ledger by reference."""
        if not cert_ref:
            return None

        cert_path = self.ledger_dir / "certificates" / f"{cert_ref}.json"
        try:
            with open(cert_path) as f:
                return json.load(f)
        except Exception:
            return None

    def _get_stage_def(self, stage: str) -> dict[str, Any] | None:
        """Get the stage definition from gates."""
        stages = self.gates.get("stages", {})
        return stages.get(stage)

    def validate_stage(
        self,
        stage: str,
        framework: str | None = None,
        verbose: bool = False,
    ) -> tuple[bool, list[str]]:
        """
        Validate a stage. Returns (success, errors).

        If framework is None, validates as a shared/program stage.
        If framework is provided, validates a per-framework stage.
        """
        errors: list[str] = []

        # Load stage definition
        stage_def = self._get_stage_def(stage)
        if not stage_def:
            errors.append(f"Stage {stage} not defined in STAGE_GATES.yaml")
            return False, errors

        # Check applies_to matches
        applies_to = stage_def.get("applies_to")
        if framework is None and applies_to == "per-framework":
            errors.append(f"Stage {stage} is per-framework but no framework specified")
            return False, errors
        if framework is not None and applies_to == "program":
            errors.append(f"Stage {stage} is program-level but framework specified: {framework}")
            return False, errors

        # Check tripwire if required
        tripwire = stage_def.get("tripwire")
        if tripwire:
            tripwire_id = tripwire.get("id")
            tripwire_path = self.repo_root / "docs" / "tripwires" / f"{tripwire_id}.signed"
            if not tripwire_path.exists() or tripwire_path.stat().st_size == 0:
                errors.append(
                    f"Tripwire {tripwire_id} required but not signed "
                    f"(expected: {tripwire_path})"
                )

        # Load all artifacts for this stage + framework
        artifacts = self._load_registry_artifacts(stage, framework)
        registered_types = {a.get("artifact_type") for a in artifacts}

        # Check required artifacts are present
        required_types = stage_def.get("required_artifacts", [])
        for req_type in required_types:
            if req_type not in registered_types:
                errors.append(
                    f"Missing required artifact type '{req_type}' "
                    f"for stage {stage} "
                    f"(framework={framework or 'program'})"
                )

        # Check all registered artifacts have passing certificates
        for artifact in artifacts:
            artifact_id = artifact.get("artifact_id")
            cert_ref = artifact.get("certificate_ref")

            if not cert_ref:
                errors.append(f"Artifact {artifact_id} has no certificate_ref")
                continue

            cert = self._load_certificate(cert_ref)
            if not cert:
                errors.append(f"Certificate {cert_ref} not found for artifact {artifact_id}")
                continue

            verdict = cert.get("verdict")
            if verdict != "ACCEPT":
                errors.append(
                    f"Artifact {artifact_id} has verdict={verdict} "
                    f"(expected ACCEPT from {cert_ref})"
                )

            # D8: check adversary discipline matches required_adversary_disciplines
            required_disciplines = stage_def.get("required_adversary_disciplines", [])
            if required_disciplines:
                adversary_block = cert.get("adversary_block", {})
                # Skip check for self-attested P0 certificates
                if not adversary_block.get("self_attested"):
                    cert_adversary_agent = adversary_block.get("agent", "")
                    if cert_adversary_agent not in required_disciplines:
                        errors.append(
                            f"Artifact {artifact_id}: certificate adversary "
                            f"'{cert_adversary_agent}' is not in stage {stage} "
                            f"required_adversary_disciplines {required_disciplines}"
                        )

        # Check depends_on stages are certified
        depends_on = stage_def.get("depends_on_stages", [])
        for dep_stage in depends_on:
            success, dep_errors = self.validate_stage(dep_stage, framework, verbose=False)
            if not success:
                errors.append(
                    f"Dependency {dep_stage} not certified "
                    f"(framework={framework or 'program'}); "
                    f"cannot proceed with {stage}"
                )
                if verbose:
                    for err in dep_errors:
                        errors.append(f"  └─ {err}")

        if verbose and not errors:
            print(f"✓ Stage {stage} (framework={framework or 'program'}) certified")

        return len(errors) == 0, errors

    def validate_tier_b_gate(self, verbose: bool = False) -> tuple[bool, str]:
        """
        Check if Tier B (synthesis) can open.
        Requires ≥2 frameworks certified through S9.
        """
        certified_frameworks = 0
        for fw in self.frameworks:
            success, _ = self.validate_stage("S9", fw, verbose=False)
            if success:
                certified_frameworks += 1
                if verbose:
                    print(f"  {fw}: ✓ certified through S9")
            else:
                if verbose:
                    print(f"  {fw}: ✗ not yet certified")

        can_open = certified_frameworks >= 2
        message = (
            f"Tier B gate: {certified_frameworks}/{len(self.frameworks)} frameworks "
            f"certified through S9"
        )
        if can_open:
            message += " — X1 may open"
        else:
            message += f" — need {2 - certified_frameworks} more"

        return can_open, message

    def validate_all_stages(self, verbose: bool = False) -> tuple[bool, dict[str, list[str]]]:
        """Validate all stages across all frameworks. Returns (success, errors_by_stage)."""
        all_errors: dict[str, list[str]] = {}

        # Shared program stages
        for stage in ["P0", "P1", "S3"]:
            success, errors = self.validate_stage(stage, None, verbose=verbose)
            if not success:
                all_errors[stage] = errors

        # Per-framework stages
        for fw in self.frameworks:
            for stage in ["S1f", "S4", "S5", "S6", "S7", "S8f", "S9"]:
                stage_key = f"{stage}:{fw}"
                success, errors = self.validate_stage(stage, fw, verbose=verbose)
                if not success:
                    all_errors[stage_key] = errors

        # Synthesis stages
        for stage in ["X1", "X2", "X3", "X4", "X5"]:
            success, errors = self.validate_stage(stage, None, verbose=verbose)
            if not success:
                all_errors[stage] = errors

        return len(all_errors) == 0, all_errors


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate hc-grc stage gates.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --stage S4 --framework scf
  %(prog)s --stage P1 --all
  %(prog)s --validate
  %(prog)s --tier-b-check
  %(prog)s --validate-artifact /path/to/artifact.json
        """,
    )
    parser.add_argument(
        "--stage",
        help="Stage ID to validate (e.g., P0, S4, X1)",
    )
    parser.add_argument(
        "--framework",
        help="Framework name (e.g., scf, nist-800-53). Required if --stage is per-framework.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate --stage as a shared/program stage (not per-framework)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate all stages across all frameworks (dry-run status)",
    )
    parser.add_argument(
        "--tier-b-check",
        action="store_true",
        help="Check if Tier B (synthesis) can open (≥2 frameworks through S9)",
    )
    parser.add_argument(
        "--validate-artifact",
        type=Path,
        help="Validate a single artifact file against schema (for smoke tests)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repository root (default: git root)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    try:
        validator = StageGateValidator(repo_root=args.repo_root)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Validate single artifact file (for smoke tests)
    if args.validate_artifact:
        try:
            with open(args.validate_artifact) as f:
                artifact = json.load(f)
        except Exception as e:
            print(f"ERROR: Failed to load artifact: {e}", file=sys.stderr)
            return 1

        errors = []

        # Fast pre-check: required fields and enum membership
        required_fields = ["artifact_id", "artifact_type", "stage_id", "certificate_ref"]
        for field in required_fields:
            if field not in artifact or not artifact.get(field):
                errors.append(f"Missing or empty required field: {field}")

        if artifact.get("stage_id") not in {
            "P0", "P1", "S1f", "S3", "S4", "S5", "S6", "S7", "S8f", "S9",
            "X1", "X2", "X3", "X4", "X5"
        }:
            errors.append(f"Invalid stage_id: {artifact.get('stage_id')}")

        if artifact.get("artifact_type") not in validator.artifact_types:
            errors.append(f"Invalid artifact_type: {artifact.get('artifact_type')}")

        # D7: JSON schema validation (authoritative, not just the fast pre-check above)
        if validator.artifact_schema is not None:
            try:
                jsonschema.validate(instance=artifact, schema=validator.artifact_schema)
            except jsonschema.ValidationError as exc:
                errors.append(f"Schema validation failed: {exc.message}")
            except jsonschema.SchemaError as exc:
                errors.append(f"Schema itself is invalid: {exc.message}")
        else:
            errors.append(
                "artifact.schema.json could not be loaded; schema validation skipped"
            )

        if errors:
            print("ARTIFACT VALIDATION FAILED:", file=sys.stderr)
            for err in errors:
                print(f"  • {err}", file=sys.stderr)
            return 1

        print(f"✓ Artifact valid: {artifact.get('artifact_id')}")
        return 0

    # Validate --tier-b-check
    if args.tier_b_check:
        can_open, message = validator.validate_tier_b_gate(verbose=args.verbose)
        print(message)
        return 0 if can_open else 1

    # Validate --validate (all stages)
    if args.validate:
        success, errors_by_stage = validator.validate_all_stages(verbose=args.verbose)
        if errors_by_stage:
            print("VALIDATION ERRORS:", file=sys.stderr)
            for stage, errors in sorted(errors_by_stage.items()):
                print(f"\n{stage}:", file=sys.stderr)
                for err in errors:
                    print(f"  • {err}", file=sys.stderr)
            return 1
        print("✓ All stages certified")
        return 0

    # Validate specific stage
    if args.stage:
        if args.all:
            # Shared/program stage
            success, errors = validator.validate_stage(args.stage, None, verbose=args.verbose)
        elif args.framework:
            # Per-framework stage
            success, errors = validator.validate_stage(
                args.stage,
                args.framework,
                verbose=args.verbose,
            )
        else:
            print(
                "ERROR: --stage requires either --framework (per-framework) or --all (shared)",
                file=sys.stderr,
            )
            return 1

        if not success:
            print(f"STAGE GATE FAILED: {args.stage}", file=sys.stderr)
            if args.framework:
                print(f"Framework: {args.framework}", file=sys.stderr)
            print()
            for err in errors:
                print(f"  • {err}", file=sys.stderr)
            return 1

        if args.verbose:
            print(f"✓ Stage {args.stage} certified")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
