"""
P5 Agent — AI Governance Cluster Analysis.

PURPOSE:
Applies HDBSCAN+UMAP clustering to the 1,400 SCF control embeddings to discover
whether the official 33-domain taxonomy is empirically grounded. Does the SCF
domain structure reflect how controls actually cluster by semantic content and
co-occurrence? This is asked per-domain (33 × HDBSCAN) and cross-domain.

PROTECTED AGENT: Prompts may not be modified autonomously by Agent Evolution.
Any modification requires Escalation approval (ADR-0015 §77).

WORKFLOW POSITION:
  Embedding Agent → P5 (largely independent of P1-P4 in exploratory phase)
  P1-P4 outputs → P5 cross-domain synthesis (confirmatory phase)
  → Statistical Analyst, Report Agent

UMAP PARAMETERS:
  n_neighbors=15, min_dist=0.1, metric=cosine (defaults in configs/platform.yaml)
  Parameters are tuned during exploratory phase — final values logged to MLflow
  before any confirmatory clustering runs. Parameter decisions are logged to
  the Preregistration Ledger at Gate 2 (part of the model/parameter lock).

HDBSCAN PARAMETERS:
  min_cluster_size=10, min_samples=5, metric=euclidean (on UMAP-reduced embeddings)
  Noise points (label = -1) are reported as unclustered, not assigned to clusters.

TAXONOMY COMPARISON:
  Empirical cluster assignments are compared to SCF's 33 official domains using
  Adjusted Rand Index (ARI) and Normalized Mutual Information (NMI). These are
  the primary H5.x test statistics.

See AGENT.md: agents/03-analysis/p5-ai-governance/AGENT.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ...state import HCGRCState
from ..base import BaseResearchAgent

N_SCF_DOMAINS = 33  # Official SCF taxonomy — fixed
N_SCF_CONTROLS = 1400  # Expected SCF control count per SAP §7


class P5AiGovernanceAgent(BaseResearchAgent):
    """
    AI governance cluster analysis agent.

    Inputs (from state + filesystem):
        - Control embeddings: Qdrant collection hcgrc_controls (all 1,400 controls)
        - Control metadata: ara/artifacts/ (domain, framework, maturity, MCR/DSR)
        - STRM co-occurrence patterns: data/splits/ (for cross-domain synthesis)
        - P1-P4 outputs: used in cross-domain synthesis only (confirmatory)
        - SCF domain definitions: docs/charter/SCF_CONSTITUTION.md

    Produces:
        EXP_P5_domain_clusters.parquet  — 33 files × (cluster_id, control_id, label)
        EXP_P5_cross_domain.parquet     — latent governance groups spanning domains
        EXP_P5_umap.parquet             — 2D + 3D UMAP projections
        EXP_P5_taxonomy_comparison.md   — ARI/NMI: empirical clusters vs. SCF domains
        H5.x_results.parquet            — confirmatory results (post-Gate 2)
    """

    PROTECTED = True
    AGENT_ID = "p5-ai-governance"

    def __init__(
        self,
        output_dir: Path | str = Path("analysis"),
        umap_n_neighbors: int = 15,
        umap_min_dist: float = 0.1,
        umap_metric: str = "cosine",
        hdbscan_min_cluster_size: int = 10,
        hdbscan_min_samples: int = 5,
    ) -> None:
        self.output_dir = Path(output_dir)
        # UMAP parameters — from configs/platform.yaml defaults
        self.umap_n_neighbors = umap_n_neighbors
        self.umap_min_dist = umap_min_dist
        self.umap_metric = umap_metric
        # HDBSCAN parameters — applied on UMAP-reduced embeddings
        self.hdbscan_min_cluster_size = hdbscan_min_cluster_size
        self.hdbscan_min_samples = hdbscan_min_samples

    def run_exploratory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Run per-domain clustering (33 × HDBSCAN) and cross-domain synthesis.

        Must NOT access test_ids.
        All outputs EXP_-prefixed.
        UMAP parameters tuned here — final values logged to MLflow before Gate 2.
        Noise points (HDBSCAN label = -1) reported as unclustered, never force-assigned.
        """
        raise NotImplementedError(
            "P5 exploratory cluster analysis not yet implemented. "
            "Phase 1 implementation will: (1) load all 1,400 control embeddings "
            "from Qdrant, (2) run UMAP dimensionality reduction, (3) run HDBSCAN "
            "per domain (33 runs) + cross-domain, (4) compute ARI/NMI against "
            "SCF 33-domain taxonomy, (5) write domain_clusters.parquet, "
            "cross_domain.parquet, umap.parquet, taxonomy_comparison.md."
        )

    def run_confirmatory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Execute one pre-registered confirmatory clustering test on test split embeddings.

        Gate 2 approval verified by BaseResearchAgent.__call__.
        Requires: state["current_hypothesis_id"] == "H5.[n]"
        UMAP + HDBSCAN parameters locked at Gate 2 — must not re-tune on test split.
        """
        raise NotImplementedError(
            "P5 confirmatory analysis not yet implemented. "
            "Requires: Gate 2 approved, parameters locked in state, hypothesis_id set."
        )

    def _report_noise_points(
        self,
        cluster_labels: list[int],
        control_ids: list[str],
    ) -> tuple[list[str], float]:
        """
        Return (noise_control_ids, noise_fraction).

        HDBSCAN label = -1 indicates noise (no cluster assignment).
        Noise points are reported separately — do not assign to nearest cluster.
        High noise fraction (> 0.20) is a finding, not a failure.
        """
        noise_ids = [cid for cid, label in zip(control_ids, cluster_labels) if label == -1]
        noise_fraction = len(noise_ids) / len(control_ids) if control_ids else 0.0
        return noise_ids, noise_fraction
