"""
P4 Agent — Risk Blindspot Engine.

PURPOSE:
Maps the 39 SCF risk categories against actual control coverage across all
framework combinations. Quantifies which risk categories are over-controlled,
under-controlled, or absent for a given framework set. Compliance ≠ security —
this agent measures the gap.

PROTECTED AGENT: Prompts may not be modified autonomously by Agent Evolution.
Any modification requires Escalation approval (ADR-0015 §77).

WORKFLOW POSITION:
  P2 (topology, isolated domains) + P3 (convergence atlas, false coverage flags)
  → P4 → Statistical Analyst, Report Agent

FALSE COVERAGE HANDLING:
  P3 flags controls that appear to cover a risk category but are classified as
  TERMINOLOGICAL convergence. P4 must exclude these from coverage density counts —
  including them would overstate coverage and understate blindspot severity.

RISK CONSTITUTION:
  The 39 SCF risk categories are defined in docs/charter/RISK_CONSTITUTION.md.
  P4 does not define or modify risk categories — it only measures coverage
  against the pre-defined 39.

FRAMEWORK COMBINATIONS:
  Pre-specified in configs/analysis.yaml (framework_combinations section).
  P4 does not select which combinations to analyze — this is pre-registered.

See AGENT.md: agents/03-analysis/p4-risk-blindspot/AGENT.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..base import BaseResearchAgent
from ...state import HCGRCState

# Coverage density threshold below which a risk category is a "blindspot"
# Pre-registered value — do not change after Gate 2
BLINDSPOT_COVERAGE_THRESHOLD = 0.30  # 30% of applicable controls cover the risk


class P4RiskBlindspotAgent(BaseResearchAgent):
    """
    Risk blindspot engine agent.

    Inputs (from state + filesystem):
        - Risk categories: docs/charter/RISK_CONSTITUTION.md (39 categories)
        - Control-to-risk mappings: ara/artifacts/ (SCF native risk assignments)
        - P2 topology: EXP_P2_topology.parquet (isolated domain flags)
        - P3 convergence: EXP_P3_atlas.json (false convergence flags)
        - Framework combinations: configs/analysis.yaml

    Produces:
        EXP_P4_coverage.parquet      — risk category × framework combo: coverage density
        EXP_P4_blindspots.json       — risk categories below threshold, by framework combo
        EXP_P4_false_coverage.parquet — controls appearing to cover a risk but flagged by P3
        H4.x_results.parquet          — confirmatory results (post-Gate 2)
    """

    PROTECTED = True
    AGENT_ID = "p4-risk-blindspot"

    N_RISK_CATEGORIES = 39  # SCF RISK_CONSTITUTION.md — fixed, do not modify

    def __init__(
        self,
        output_dir: Path | str = Path("analysis"),
        blindspot_threshold: float = BLINDSPOT_COVERAGE_THRESHOLD,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.blindspot_threshold = blindspot_threshold

    def run_exploratory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Compute risk coverage matrix across all framework combinations.

        Must NOT access test_ids.
        All outputs EXP_-prefixed.
        False coverage flags from P3 must be loaded and applied before
        computing coverage density — do not count terminological matches.
        """
        raise NotImplementedError(
            "P4 exploratory risk blindspot analysis not yet implemented. "
            "Phase 1 implementation will: (1) load 39 risk categories from "
            "RISK_CONSTITUTION.md, (2) load P3 false coverage flags, "
            "(3) compute coverage density per risk category × framework combination "
            "(excluding false coverage), (4) identify blindspots below threshold, "
            "(5) write coverage.parquet, blindspots.json, false_coverage.parquet."
        )

    def run_confirmatory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Execute one pre-registered confirmatory blindspot test on test split.

        Gate 2 approval verified by BaseResearchAgent.__call__.
        Requires: state["current_hypothesis_id"] == "H4.[n]"
        """
        raise NotImplementedError(
            "P4 confirmatory analysis not yet implemented. "
            "Requires: Gate 2 approved, hypothesis_id in state."
        )

    def _exclude_false_coverage(
        self,
        control_ids: list[str],
        false_coverage_control_ids: set[str],
    ) -> list[str]:
        """
        Remove controls flagged by P3 as terminological convergence from coverage count.

        Including these would overstate how well a framework covers a risk category.
        The exclusion must be logged in the codebook entry for each affected risk category.
        """
        return [cid for cid in control_ids if cid not in false_coverage_control_ids]

    def _compute_coverage_density(
        self,
        applicable_controls: list[str],
        covering_controls: list[str],
    ) -> float:
        """
        Coverage density = covering_controls / applicable_controls.

        Returns 0.0 if applicable_controls is empty (underpopulated risk category —
        log as coverage gap, not as a blindspot finding).
        """
        if not applicable_controls:
            return 0.0
        return len(set(covering_controls) & set(applicable_controls)) / len(applicable_controls)
