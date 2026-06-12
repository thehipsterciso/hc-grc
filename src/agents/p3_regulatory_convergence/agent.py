"""
P3 Agent — Regulatory Convergence Atlas.

PURPOSE:
Measures pairwise cross-framework semantic and structural convergence across
all 33 SCF domains. Distinguishes GENUINE convergence (semantic alignment)
from TERMINOLOGICAL convergence (similar words, different meaning). Produces
the Convergence Atlas — a quantified map of where frameworks actually agree.

PROTECTED AGENT: Prompts may not be modified autonomously by Agent Evolution.
Any modification requires Escalation approval (ADR-0015 §77).

WORKFLOW POSITION:
  P2 (community assignments) → P3 → P4 (convergence gaps inform blindspot detection),
                                     Statistical Analyst, Report Agent

CONVERGENCE TYPES (must classify every finding):
  - GENUINE:          semantic alignment — embeddings agree, STRM labels confirm
  - TERMINOLOGICAL:   similar words, different semantic content — must never be
                      reported as genuine convergence
  - STRUCTURAL:       same position in graph topology without semantic agreement

NIST CLUSTER CONSTRAINT (MANDATORY):
  NIST 800-53, CSF, 800-171 are ONE authorship cluster.
  Convergence between them is NIST_CLUSTER_INTERNAL — excluded from cross-framework
  convergence claims. This constraint applies to every framework pair computation.

CLASSIFIER CONFIDENCE THRESHOLD:
  Convergence type classification (LLM via Instructor/Pydantic) requires
  confidence ≥ 0.70. Below threshold → human review flag; do not auto-classify.

See AGENT.md: agents/03-analysis/p3-regulatory-convergence/AGENT.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from ...state import HCGRCState
from ..base import BaseResearchAgent

# Convergence classification types
ConvergenceType = Literal["genuine", "terminological", "structural", "nist_cluster_internal"]


class P3RegulatoryConvergenceAgent(BaseResearchAgent):
    """
    Regulatory convergence atlas agent.

    Inputs (from state + filesystem):
        - P2 community assignments: analysis/01-exploratory/EXP_P2_communities.parquet
        - Qdrant: framework-tagged control embeddings
        - STRM equivalence mappings: data/splits/ (relationship_type == "equal")

    Produces:
        EXP_P3_convergence.parquet  — framework × framework × domain convergence scores
        EXP_P3_atlas.json           — structured atlas: genuine, terminological, divergence
        EXP_P3_heatmap.parquet      — input to Visualization Agent
        H3.x_results.parquet        — confirmatory results (post-Gate 2)
    """

    PROTECTED = True
    AGENT_ID = "p3-regulatory-convergence"

    # Classifier confidence threshold — below this, flag for human review
    CLASSIFIER_CONFIDENCE_THRESHOLD = 0.70

    # False convergence prevalence threshold — above this, Gate 3 discussion item
    FALSE_CONVERGENCE_GATE3_THRESHOLD = 0.05  # 5%

    def __init__(
        self,
        output_dir: Path | str = Path("analysis"),
        classifier_model: str | None = None,
    ) -> None:
        self.output_dir = Path(output_dir)
        # LLM used for convergence type classification (Instructor/Pydantic)
        # Must be local — no SaaS inference
        self.classifier_model = classifier_model

    def run_exploratory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Compute pairwise framework convergence across all 33 domains.

        Must NOT access test_ids.
        All outputs EXP_-prefixed.
        NIST cluster constraint applied to every framework pair.
        Terminological convergence classified and never reported as genuine.
        """
        raise NotImplementedError(
            "P3 exploratory convergence analysis not yet implemented. "
            "Phase 1 implementation will: (1) load P2 community assignments, "
            "(2) compute pairwise cosine similarity between framework-specific "
            "control embeddings per domain, (3) classify convergence type via "
            "Instructor+Pydantic (confidence >= 0.70), (4) apply NIST cluster "
            "constraint to all framework pairs, (5) write convergence.parquet, "
            "atlas.json, heatmap.parquet."
        )

    def run_confirmatory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Execute one pre-registered confirmatory convergence test on test split.

        Gate 2 approval verified by BaseResearchAgent.__call__.
        Requires: state["current_hypothesis_id"] == "H3.[n]"
        """
        raise NotImplementedError(
            "P3 confirmatory analysis not yet implemented. "
            "Requires: Gate 2 approved, hypothesis_id in state."
        )

    def _is_nist_cluster_pair(self, fw_a: str, fw_b: str) -> bool:
        """
        Return True if both frameworks are in the NIST authorship cluster.

        Pairs that return True must be tagged NIST_CLUSTER_INTERNAL and
        excluded from cross-framework convergence claims.
        """
        nist = {"NIST 800-53", "NIST CSF", "NIST 800-171"}
        return fw_a.upper() in nist and fw_b.upper() in nist

    def _classify_convergence(
        self,
        similarity_score: float,
        strm_relationship: str,
        linguistic_overlap: float,
    ) -> tuple[ConvergenceType, float]:
        """
        Classify convergence type and return (type, confidence).

        In Phase 1 implementation: calls local LLM via Instructor with a
        typed Pydantic ConvergenceClassification output schema.

        If confidence < CLASSIFIER_CONFIDENCE_THRESHOLD, returns
        ("terminological", confidence) and flags for human review —
        do NOT auto-classify uncertain cases.
        """
        raise NotImplementedError(
            "Convergence classification requires Instructor + local LLM. "
            "Not implemented until Phase 1 LLM infrastructure is available."
        )
