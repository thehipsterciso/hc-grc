"""
P1 Agent — SCF NLP Characterization (STRM vs. Computational Similarity).

PURPOSE:
Applies NLP similarity methods to every STRM mapping and compares computational
findings to STRM expert labels. The gap between the two is the primary finding.

PROTECTED AGENT: Prompts may not be modified autonomously by Agent Evolution.
Any modification requires Escalation approval (ADR-0015 §77).

WORKFLOW POSITION:
  Embedding Agent (FAISS + Qdrant) → P1 → Statistical Analyst, QA Agent

PHASE DISCIPLINE:
  Exploratory: train + val splits. All outputs prefixed EXP_. No p-value decisions.
  Confirmatory: test split only, after Gate 2. Every script has SAP header.

NIST CLUSTER CONSTRAINT:
  NIST 800-53, CSF, and 800-171 share authorship — treated as ONE evidence source.
  Cross-framework findings citing all three as independent validation are invalid.

NLP METHOD TIERS (all must run in exploratory phase — no cherry-picking):
  1. Lexical: TF-IDF cosine, BM25
  2. Embedding: cosine similarity over dense embeddings (5 model candidates)
  3. Topic: LDA/BERTopic coherence correlation
  4. Entailment: NLI model on (source, target) pairs
  5. Hybrid: weighted ensemble of tiers 1-4

See AGENT.md: agents/03-analysis/p1-strm-nlp/AGENT.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ...state import HCGRCState
from ..base import BaseResearchAgent


class P1StrmNlpAgent(BaseResearchAgent):
    """
    SCF NLP Characterization agent.

    Inputs (from state):
        - train_ids / val_ids / test_ids: split control ID lists
        - data_split_seed: for reproducibility logging
        - run_id: for MLflow experiment tagging and PROV-DM

    Produces (written to analysis/):
        EXP_P1_similarity.parquet   — all-pairs similarity across NLP method tiers
        EXP_P1_classification.parquet — predicted relationship types vs. STRM labels
        EXP_P1_disagreements.md     — high-disagreement mappings for Gate 3 review
        H1.x_results.parquet       — confirmatory per-hypothesis results (post-Gate 2)
    """

    PROTECTED = True
    AGENT_ID = "p1-strm-nlp"

    def __init__(
        self,
        output_dir: Path | str = Path("analysis"),
        embedding_model_id: str | None = None,
        nist_cluster_ids: set[str] | None = None,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.embedding_model_id = embedding_model_id
        # Controls from NIST 800-53, CSF, 800-171 — one authorship cluster
        self.nist_cluster_ids: set[str] = nist_cluster_ids or set()

    # ── Exploratory phase ─────────────────────────────────────────────────────

    def run_exploratory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Run all 5 NLP method tiers on train + val splits.

        MUST NOT access test_ids.
        All outputs written to analysis/01-exploratory/ with EXP_ prefix.
        No p-value decision language in any output.
        """
        raise NotImplementedError(
            "P1 exploratory analysis not yet implemented. "
            "Phase 1 implementation will: (1) load STRM mappings from "
            "data/splits/train.parquet + val.parquet, (2) run all 5 NLP tiers, "
            "(3) write EXP_P1_similarity.parquet and EXP_P1_classification.parquet, "
            "(4) generate EXP_P1_disagreements.md for Gate 3."
        )

    # ── Confirmatory phase ────────────────────────────────────────────────────

    def run_confirmatory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Execute one pre-registered confirmatory test on the test split.

        Gate 2 approval verified by BaseResearchAgent.__call__ before this runs.
        Requires: state["current_hypothesis_id"] == "H1.[n]"
        Writes:   analysis/02-confirmatory/H1.[n]_results.parquet

        SAP header contract (enforced by Code Review Agent):
            # SAP: hypothesis_id=H1.[n]
            # test=[named test], effect_size_threshold=[value]
            # decision_rule=[criterion]
        """
        raise NotImplementedError(
            "P1 confirmatory analysis not yet implemented. "
            "Requires: Gate 2 approved, hypothesis_id in state, "
            "test split accessible via DataSteward."
        )

    # ── NIST cluster constraint enforcement ───────────────────────────────────

    def _is_nist_cluster(self, framework: str) -> bool:
        """
        Return True if framework is in the NIST authorship cluster.

        NIST 800-53, CSF, and 800-171 share authorship. Citing agreement
        between all three as independent validation is a SAP violation.
        """
        return framework.upper() in {"NIST 800-53", "NIST CSF", "NIST 800-171"}

    def _validate_cross_framework_claim(
        self,
        framework_a: str,
        framework_b: str,
    ) -> None:
        """
        Raise ValueError if claim crosses NIST cluster without disclosing constraint.

        Call before writing any cross-framework similarity finding.
        """
        if self._is_nist_cluster(framework_a) and self._is_nist_cluster(framework_b):
            raise ValueError(
                f"Cross-framework finding between {framework_a!r} and {framework_b!r} "
                "violates NIST Cluster Independence Constraint. These frameworks share "
                "authorship and cannot be cited as independent validation. "
                "Tag finding as NIST_CLUSTER_INTERNAL and exclude from convergence claims."
            )
