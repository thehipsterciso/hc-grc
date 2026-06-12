"""
DataCurationAgent — Governed deduplication, normalization, and quality scoring.

Applies pre-specified curation rules from configs/data_curation.yaml to the
validated SCF splits. Records every transformation in a lineage map. Produces
the curated dataset that feeds Embedding Agent and all Team 03 analysis agents.

Phase 1 stub: run() raises NotImplementedError.

Required tools: mcp-dvc, mcp-lab-notebook
Required skills: nemo-curator
See: agents/02-data/data-curation/AGENT.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..base import BasePipelineAgent
from ...state import HCGRCState


# ── Result type ───────────────────────────────────────────────────────────────


@dataclass
class CurationReport:
    """Summary produced by a curation run. Surfaces in lab notebook and Gate 2 review."""

    records_before: int = 0
    records_after: int = 0
    duplicates_removed: int = 0
    below_quality_threshold_removed: int = 0
    normalization_transformations: int = 0
    removal_fraction: float = 0.0  # duplicates_removed / records_before
    lineage_path: str = ""         # path to data/lineage.md
    curated_dvc_hash: str = ""     # DVC hash of curated dataset artifact
    rule_config_hash: str = ""     # SHA-256 of configs/data_curation.yaml — rules immutable
    splits_processed: list[str] = field(default_factory=list)  # ["train", "val", "test"]


# Halts curation if more than this fraction of STRM mappings removed
_MAX_REMOVAL_FRACTION = 0.05


# ── Agent ─────────────────────────────────────────────────────────────────────


class DataCurationAgent(BasePipelineAgent):
    """
    Applies governed curation rules to SCF splits — dedup, normalization, quality scoring.

    Behavioral constraints (per AGENT.md):
      - Never remove a record without a lineage entry documenting the removal rule
      - Never apply a curation rule not pre-specified in configs/data_curation.yaml
      - Curated dataset is a separate DVC artifact — raw validated splits never overwritten
      - Identical rules applied to train, val, and test splits — no split-specific curation
      - Never make semantic judgments about which controls are 'correct'
      - SCF CC BY-ND 4.0: curated dataset and all derivatives stay local
    """

    AGENT_ID = "data-curation"
    PROTECTED = False

    def run(self, state: HCGRCState) -> dict[str, Any]:
        """
        Apply curation rules to validated splits from DataStewardAgent.

        Phase 1 implementation will:
          1. Load validated splits from data/splits/ (DVC tracked)
          2. Load curation rules from configs/data_curation.yaml — hash config first
          3. Run NeMo Curator: exact + fuzzy deduplication of STRM mappings
          4. Apply normalization (control ID standardization, framework acronym resolution)
          5. Quality-filter below minimum length/informativeness thresholds
          6. Apply same rules identically to all three splits
          7. Verify removal fraction < _MAX_REMOVAL_FRACTION — halt if exceeded
          8. Write curated dataset to data/03-processed/curated/ (DVC versioned)
          9. Write lineage map to data/lineage.md
          10. Append curation report to lab notebook

        If > 5% of STRM mappings removed: halt and surface to human before analysis
        proceeds. This is a Gate 2 blocker.

        Returns partial HCGRCState update:
          prov_activities: curation provenance record
        """
        raise NotImplementedError(
            "DataCurationAgent.run() — Phase 1 implementation pending. "
            "Requires: validated splits from DataStewardAgent, NeMo Curator, "
            "configs/data_curation.yaml with pre-specified rules. "
            "See agents/02-data/data-curation/AGENT.md."
        )

    def _check_removal_fraction(self, report: CurationReport) -> None:
        """
        Halt if removal fraction exceeds maximum threshold.

        Per AGENT.md: > 5% removed triggers human review before analysis proceeds.
        Raises ValueError — calling node must propagate to Gate 2 blocker.
        """
        if report.removal_fraction > _MAX_REMOVAL_FRACTION:
            raise ValueError(
                f"Curation removal fraction {report.removal_fraction:.1%} exceeds "
                f"maximum {_MAX_REMOVAL_FRACTION:.0%}. Potential SCF data quality issue. "
                "Halt — human review required before analysis proceeds. "
                f"Records removed: {report.duplicates_removed + report.below_quality_threshold_removed}"
            )

    def _assert_rule_config_unchanged(
        self, config_hash_at_run: str, config_hash_expected: str
    ) -> None:
        """
        Verify curation rule config has not changed since it was first applied.

        Curation rules must be identical across all runs for reproducibility.
        Raises RuntimeError if config hash has changed.
        """
        if config_hash_at_run != config_hash_expected:
            raise RuntimeError(
                "Curation rule config hash mismatch — rules have changed since "
                "initial application. This violates the requirement for identical "
                "rules across all splits and all runs. "
                f"Expected: {config_hash_expected}, got: {config_hash_at_run}"
            )

    def _build_prov_record(self, report: CurationReport, run_id: str) -> dict[str, Any]:
        """Build provenance record for the curation event."""
        return {
            "activity": "data_curation",
            "agent_id": self.AGENT_ID,
            "run_id": run_id,
            "records_before": report.records_before,
            "records_after": report.records_after,
            "duplicates_removed": report.duplicates_removed,
            "removal_fraction": report.removal_fraction,
            "curated_dvc_hash": report.curated_dvc_hash,
            "rule_config_hash": report.rule_config_hash,
            "splits_processed": report.splits_processed,
            "lineage_path": report.lineage_path,
        }
