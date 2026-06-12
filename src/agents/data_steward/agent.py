"""
DataStewardAgent — Quality validation, split enforcement, and test-set access lock.

Validates acquired SCF artifacts against a pre-specified quality ruleset, executes
the train/validation/test split (seed from configs/seeds.yaml), and enforces access
control: exploratory agents receive train + val only; test split is unlocked only
after BOTH Gate 2 (SAP lock) AND Gate 3 (EDA review) are confirmed.

Phase 1 stub: run() and get_split_paths() raise NotImplementedError.

Required tools: mcp-dvc, mcp-lab-notebook, mcp-sap-validator
Required skills: ray-data
See: agents/02-data/data-steward/AGENT.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from ..base import BasePipelineAgent, SAPViolation
from ...state import HCGRCState


# ── Result types ──────────────────────────────────────────────────────────────


@dataclass
class QualityReport:
    """
    Output of the Great Expectations validation suite.

    surfaced at Gate 2 for operator review. Critical failures block Gate 2.
    """

    total_controls_validated: int = 0
    total_strm_mappings_validated: int = 0
    expectations_passed: int = 0
    expectations_failed: int = 0
    critical_failures: list[str] = field(default_factory=list)  # referential integrity etc.
    anomalies: list[str] = field(default_factory=list)  # documented in codebook
    quality_report_path: str = ""  # data/03-processed/quality_report.html


@dataclass
class SplitRecord:
    """Metadata for a completed split operation. Immutable after Gate 2."""

    seed: int = 0                  # from configs/seeds.yaml — changing post-Gate-2 is SAP violation
    seed_hash: str = ""            # SHA-256 of seed value — recorded at creation, checked at access
    train_count: int = 0
    val_count: int = 0
    test_count: int = 0
    train_path: str = ""           # data/splits/train/ (DVC tracked)
    val_path: str = ""             # data/splits/val/ (DVC tracked)
    test_path: str = ""            # data/splits/test/ (DVC tracked, access-locked)
    split_dvc_hash: str = ""       # DVC hash covering all three splits
    created_at_utc: str = ""


# ── Agent ─────────────────────────────────────────────────────────────────────


class DataStewardAgent(BasePipelineAgent):
    """
    Validates SCF artifacts, executes split, enforces test-set access lock.

    The split seed in configs/seeds.yaml is the single most consequential
    configuration value in the platform. Changing it after Gate 2 is a
    direct SAP violation (equivalent to switching hypothesis tests after
    seeing the results). The Steward records the seed hash at split creation
    and compares it at every future access.

    Behavioral constraints (per AGENT.md):
      - Never provide test-split access before BOTH Gate 2 AND Gate 3 are confirmed
      - Never silently resolve a quality failure — all anomalies in codebook
      - Never modify the split seed after Gate 2
      - Never re-run the split after Gate 2 without a full protocol amendment
      - Codebook updated before splits distributed to analysis agents
    """

    AGENT_ID = "data-steward"
    PROTECTED = False

    def run(self, state: HCGRCState) -> dict[str, Any]:
        """
        Validate SCF artifacts and execute train/val/test split.

        Phase 1 implementation will:
          1. Run Great Expectations suite against ara/artifacts/ — full validation
          2. Document all anomalies in data/codebook.md
          3. Block on any critical failure (referential integrity, > 1% broken refs)
          4. Load seed from configs/seeds.yaml; compute seed_hash (SHA-256)
          5. Execute stratified split at configured ratios (±2% tolerance)
          6. Write train/val/test to data/splits/ (DVC tracked)
          7. Access-lock test split via DVC pipeline stage with SAP gate check
          8. Update codebook with any split-related variable documentation
          9. Append split record to lab notebook

        Returns partial HCGRCState update:
          data_split_manifest_hash: SHA-256 of MANIFEST.md after split
          data_split_seed: int seed value used
          data_split_verified: True after idempotency assertion passes
          phase_1_ready: True — signals data pipeline complete (after EmbeddingAgent)
          prov_activities: split provenance record
        """
        raise NotImplementedError(
            "DataStewardAgent.run() — Phase 1 implementation pending. "
            "Requires: ARA artifacts from DataAcquisitionAgent, configs/seeds.yaml, "
            "mcp-sap-validator configured. See agents/02-data/data-steward/AGENT.md."
        )

    def get_split_paths(
        self,
        state: HCGRCState,
        split: Literal["train", "val", "test"],
    ) -> list[str]:
        """
        Return file paths for the requested split.

        Test split access requires BOTH gates confirmed — Gate 2 alone is NOT
        sufficient. The Data Steward AGENT.md is explicit: EDA review (Gate 3)
        must complete before the test split is unlocked. This is the mechanism
        that prevents confirmatory tests from inadvertently contaminating EDA.

        Raises SAPViolation if:
          - test split requested before Gate 2 (SAP lock)
          - test split requested before Gate 3 (EDA review)

        Train and val splits are available after phase_1_ready = True.
        """
        if split == "test":
            gate_status = state.get("gate_status", {})

            gate_2 = gate_status.get("gate_2", {})
            if gate_2.get("decision") != "approved":
                raise SAPViolation(
                    "Test split access attempted before Gate 2 (SAP lock). "
                    "Gate 2 must be approved before test split is available. "
                    f"Current gate_2 decision: {gate_2.get('decision', 'not_run')}. "
                    "This is a SAP violation."
                )

            gate_3 = gate_status.get("gate_3", {})
            if gate_3.get("decision") != "approved":
                raise SAPViolation(
                    "Test split access attempted before Gate 3 (EDA review complete). "
                    "Both Gate 2 (SAP lock) AND Gate 3 (EDA review) must be approved "
                    "before the test split is unlocked. "
                    f"Current gate_3 decision: {gate_3.get('decision', 'not_run')}. "
                    "See agents/02-data/data-steward/AGENT.md — 'Never provide test-split "
                    "access to any agent before Gate 3 confirmation.'"
                )

        raise NotImplementedError(
            "DataStewardAgent.get_split_paths() — Phase 1 implementation pending. "
            f"Requested split: {split!r}."
        )

    def _assert_seed_unchanged(self, current_seed_hash: str, recorded_seed_hash: str) -> None:
        """
        Verify the split seed has not changed since Gate 2.

        Changing the seed after Gate 2 is a SAP violation equivalent to selecting
        a different test set after seeing confirmatory results.
        Raises RuntimeError if seed hash has changed.
        """
        if current_seed_hash != recorded_seed_hash:
            raise RuntimeError(
                "Split seed hash mismatch — seed has changed since Gate 2. "
                "This is a SAP violation. The split is frozen at Gate 2. "
                "Any re-split requires a full protocol amendment and new pre-registration. "
                f"Expected: {recorded_seed_hash}, got: {current_seed_hash}"
            )

    def _build_prov_record(
        self, split_record: SplitRecord, run_id: str
    ) -> dict[str, Any]:
        """Build provenance record for the split event."""
        return {
            "activity": "train_val_test_split",
            "agent_id": self.AGENT_ID,
            "run_id": run_id,
            "seed": split_record.seed,
            "seed_hash": split_record.seed_hash,
            "train_count": split_record.train_count,
            "val_count": split_record.val_count,
            "test_count": split_record.test_count,
            "split_dvc_hash": split_record.split_dvc_hash,
            "created_at_utc": split_record.created_at_utc,
        }
