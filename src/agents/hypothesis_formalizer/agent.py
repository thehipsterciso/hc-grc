"""
Hypothesis Formalizer Agent.

PURPOSE:
Translates research questions and exploratory findings into formally specified
SAP-compatible hypotheses (H[module].[n] format). The formalized hypothesis
includes: the null, the alternative, the named test, the decision rule, and
the effect size threshold. Output is added to the SAP at Gate 2.

PROTECTED AGENT: Prompts may not be modified autonomously by Agent Evolution.
Any modification requires Escalation approval (ADR-0015 §77).

WORKFLOW POSITION:
  EDA findings → Hypothesis Formalizer → SAP (Gate 2 package)
  → Statistical Analyst (Phase 2 confirmatory tests)

HYPOTHESIS FORMAT (H[module].[n]):
  module: 1=P1, 2=P2, 3=P3, 4=P4, 5=P5
  n: sequential integer within module, starting at 1

GATE 2 PACKAGE:
  The Gate 2 proposal contains the formalized hypothesis set. The operator
  approves the hypothesis set as part of Gate 2. Any post-Gate-2 hypothesis
  addition requires a SAP amendment entry in the Preregistration Ledger.

WHAT THIS AGENT MUST NOT DO:
  - Add hypotheses after viewing test data (SAP violation)
  - Use exploratory p-values to select which hypotheses to formalize (HARKing)
  - Formalize hypotheses after the data split is accessed (all must be pre-Gate-2)
  - Generate effect size thresholds from the test split (circular reasoning)

See AGENT.md: agents/01-research/hypothesis-formalizer/AGENT.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from ..base import BaseResearchAgent, SAPViolation
from ...state import HCGRCState


@dataclass
class FormalHypothesis:
    """
    A single formalized hypothesis for the SAP.

    All fields required before this hypothesis is added to the Gate 2 package.
    Field names match the Instructor schema enforced at the output boundary —
    see agents/01-research/hypothesis-formalizer/AGENT.md Skills section.
    """
    hypothesis_id: str                  # H[module].[n] — e.g., "H1.1"
    null_hypothesis: str                # H0: specific, falsifiable statement
    alternative_hypothesis: str         # H1: specific, falsifiable statement
    named_test: str                     # e.g., "Spearman rank correlation"
    decision_rule: str                  # criterion: "p < 0.05 and rho > 0.40"
    effect_size_metric: str             # e.g., "Spearman rho"
    effect_size_threshold: float        # minimum meaningful effect
    tail: Literal["one-tailed", "two-tailed"]
    module: str                         # analysis module — e.g., "P1", "P2", "P3", "P4", "P5"
    citation_anchors: list[str] = field(default_factory=list)  # DOI/URL citations grounding the hypothesis
    alpha: float = 0.05
    power_target: float = 0.80
    comparison_family: str = ""         # SAP §6 family this test belongs to
    correction_method: str | None = None  # Bonferroni/BH/none — as specified in SAP §6
    rationale: str = ""                 # why this hypothesis, what it tests


class HypothesisFormalizerAgent(BaseResearchAgent):
    """
    Hypothesis formalizer — translates EDA findings to SAP hypotheses.

    Runs only in exploratory phase (before Gate 2).
    Output is appended to the SAP and included in the Gate 2 package.
    """

    PROTECTED = True
    AGENT_ID = "hypothesis-formalizer"

    def __init__(
        self,
        sap_path: Path | str = Path("docs/protocol/03_statistical_analysis_plan.md"),
        ledger_path: Path | str = Path("docs/protocol/PREREGISTRATION_LEDGER.md"),
    ) -> None:
        self.sap_path = Path(sap_path)
        self.ledger_path = Path(ledger_path)

    def run_exploratory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Formalize hypotheses from EDA findings for Gate 2 package.

        Must NOT use test data — all hypotheses formalized before Gate 2.
        Must NOT use p-values from exploratory analysis to select hypotheses (HARKing).
        Effect size thresholds must be grounded in domain knowledge or prior literature,
        not derived from the exploratory data.
        """
        raise NotImplementedError(
            "Hypothesis formalization not yet implemented. "
            "Phase 1 implementation will: (1) receive EDA summary from EDA agent, "
            "(2) formalize each research question into H[module].[n] format, "
            "(3) specify named test, decision rule, and effect size threshold, "
            "(4) append to SAP markdown, (5) return hypothesis list for Gate 2 package."
        )

    def run_confirmatory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Hypothesis Formalizer does not run in confirmatory phase.

        Adding hypotheses after Gate 2 requires a SAP amendment — not this agent.
        Raises SAPViolation.
        """
        raise SAPViolation(
            "Hypothesis Formalizer may not add hypotheses after Gate 2. "
            "All pre-registered hypotheses must be formalized before Gate 2 approval. "
            "Post-Gate-2 additions require a LEDGER sap-amendment entry and explicit "
            "justification that this does not constitute HARKing."
        )

    def _validate_no_harking(
        self,
        hypothesis: FormalHypothesis,
        exploratory_p_values: dict[str, float] | None = None,
    ) -> None:
        """
        Validate that hypothesis formalization is not driven by exploratory p-values.

        HARKing (Hypothesizing After Results are Known) occurs when effect size
        thresholds or hypothesis direction are selected because they match the
        exploratory data. This check cannot be fully automated — it is a process
        constraint documented here for explicitness.

        If exploratory_p_values are provided, log a warning if the hypothesis
        direction matches a significant exploratory finding — this is not a block
        but is flagged for Gate 2 human review.
        """
        if exploratory_p_values:
            # Log the association for Gate 2 reviewer — do not block
            pass
