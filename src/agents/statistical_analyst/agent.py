"""
Statistical Analyst Agent.

PURPOSE:
Executes confirmatory statistical tests as specified in the SAP for each
H[module].[n] hypothesis. Receives test inputs from P1-P5, applies the
pre-specified test, and writes a structured result record. Does not interpret
findings — interpretation belongs to Report Agent downstream.

PROTECTED AGENT: Prompts may not be modified autonomously by Agent Evolution.
Any modification requires Escalation approval (ADR-0015 §77).

WORKFLOW POSITION:
  P1-P5 → Statistical Analyst → QA Agent (rigor review) → Report Agent

SAP COMPLIANCE CONTRACT:
  Every test execution must verify that:
    1. hypothesis_id exists in SAP (cross-reference docs/protocol/03_statistical_analysis_plan.md)
    2. named_test matches SAP specification
    3. effect_size_threshold matches SAP specification
    4. test data comes from the pre-specified split (test, not train/val)
  If any check fails, raise SAPComplianceError and halt — do not produce results.

MULTIPLE COMPARISONS:
  Familywise error rate controlled per SAP §6 (comparison families defined there).
  Do not apply Bonferroni unless SAP §6 specifies it for this family.
  Do not apply corrections that are not specified in the SAP.

RESULT RECORD:
  Every confirmed test produces a typed result record with:
    hypothesis_id, test_name, statistic, p_value, effect_size, ci_lower, ci_upper,
    n_obs, decision (supported/not-supported), run_id, timestamp_utc, sap_ref

See AGENT.md: agents/04-statistical/statistical-analyst/AGENT.md
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from ..base import BaseResearchAgent, SAPViolation, assert_gate2_approved
from ...state import HCGRCState


class SAPComplianceError(Exception):
    """Raised when a test request does not match the SAP specification."""
    pass


@dataclass
class ConfirmatoryResult:
    """Typed output record for a single confirmatory hypothesis test."""
    hypothesis_id: str          # H[module].[n] — must exist in SAP
    test_name: str              # named test as specified in SAP
    statistic: float            # test statistic value
    p_value: float              # p-value (one-tailed or two-tailed as specified in SAP)
    effect_size: float          # effect size metric as specified in SAP
    effect_size_metric: str     # e.g., "Cohen's d", "Spearman rho", "ARI"
    ci_lower: float             # lower bound of confidence interval
    ci_upper: float             # upper bound of confidence interval
    n_obs: int                  # number of observations
    decision: Literal["supported", "not_supported"]  # based on pre-specified decision rule
    run_id: str
    timestamp_utc: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    sap_section: str = ""       # e.g., "§1 Primary Analysis" — where this test is specified
    correction_applied: str | None = None  # Bonferroni/FDR/none — must match SAP §6
    corrected_p_value: float | None = None  # p-value after multiple comparisons correction; None if no correction applied
    notes: str = ""             # anomalies, warnings — not interpretation


class StatisticalAnalystAgent(BaseResearchAgent):
    """
    Confirmatory statistical testing agent.

    Does not run in exploratory phase — raises SAPViolation if called before Gate 2.
    All tests are pre-specified in the SAP. Any deviation is a SAP violation.
    """

    PROTECTED = True
    AGENT_ID = "statistical-analyst"

    def __init__(
        self,
        sap_path: Path | str = Path("docs/protocol/03_statistical_analysis_plan.md"),
        output_dir: Path | str = Path("analysis/02-confirmatory"),
    ) -> None:
        self.sap_path = Path(sap_path)
        self.output_dir = Path(output_dir)

    def run_exploratory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Statistical Analyst does not run in exploratory phase.

        Raises SAPViolation — confirmatory testing before Gate 2 is a protocol violation.
        """
        raise SAPViolation(
            "Statistical Analyst may not run before Gate 2 approval. "
            "Confirmatory testing before the exploratory/confirmatory split is locked "
            "constitutes pre-testing and invalidates the confirmatory analysis. "
            "Wait for Gate 2 before calling this agent."
        )

    def run_confirmatory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Execute one pre-registered confirmatory test.

        Gate 2 approval verified by BaseResearchAgent.__call__.
        Requires: state["current_hypothesis_id"] == "H[module].[n]"
        Verifies: hypothesis_id exists in SAP, test matches SAP spec.
        Writes:   analysis/02-confirmatory/H[module].[n]_results.parquet
        """
        raise NotImplementedError(
            "Statistical Analyst confirmatory testing not yet implemented. "
            "Phase 1 implementation will: (1) load SAP from sap_path, "
            "(2) verify hypothesis_id exists and test spec matches, "
            "(3) load test data from test split via DataSteward, "
            "(4) execute named test, (5) write ConfirmatoryResult record to parquet."
        )

    def _verify_sap_compliance(
        self,
        hypothesis_id: str,
        test_name: str,
        effect_size_threshold: float,
    ) -> None:
        """
        Verify test request matches SAP specification.

        Raises SAPComplianceError if:
          - hypothesis_id not found in SAP
          - test_name does not match SAP for this hypothesis
          - effect_size_threshold does not match SAP for this hypothesis

        This check runs before any test data is loaded.
        """
        raise NotImplementedError(
            "SAP compliance verification requires parsing the SAP markdown. "
            "Not implemented until Phase 1."
        )
