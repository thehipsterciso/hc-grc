"""
P2 Agent — Control Space Topology.

PURPOSE:
Constructs a directed graph from STRM mappings (controls as nodes, mappings
as edges) and characterizes the network's mathematical properties. Identifies
hub controls, bridge controls, isolated domains, and community structure.

PROTECTED AGENT: Prompts may not be modified autonomously by Agent Evolution.
Any modification requires Escalation approval (ADR-0015 §77).

WORKFLOW POSITION:
  Embedding Agent → P2 → P3 (community assignments), P4 (hub map),
                          Statistical Analyst, Report Agent

EDGE DIRECTIONALITY:
  subset (⊂) and superset (⊃): directed
  equivalence (=) and intersection (∩): undirected (add edges in both directions)
  strength_score: edge weight; imputed at median if missing (document in codebook)

COMMUNITY DETECTION:
  Must run at least Leiden AND Louvain — results reported for both.
  Single-algorithm community structure is not reported as authoritative.

NIST CLUSTER CONSTRAINT:
  NIST 800-53, CSF, 800-171 node attributes tagged as one authorship cluster.
  Community membership spanning all three is NOT evidence of independent convergence.

See AGENT.md: agents/03-analysis/p2-control-topology/AGENT.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ...state import HCGRCState
from ..base import BaseResearchAgent


class P2ControlTopologyAgent(BaseResearchAgent):
    """
    Control space topology agent.

    Inputs (from state + filesystem):
        - STRM mappings: data/splits/train.parquet + val.parquet (exploratory)
        - Control metadata: ara/artifacts/ (node attributes: domain, framework, maturity)

    Produces (written to analysis/):
        EXP_P2_graph.graphml         — directed + undirected graph per edge type
        EXP_P2_topology.parquet      — degree, betweenness centrality, clustering coeff, PageRank
        EXP_P2_communities.parquet   — community ID, size, intra/inter-community density
        EXP_P2_hubs.md               — top 50 most central controls with annotations
        H2.x_results.parquet         — confirmatory results (post-Gate 2)
    """

    PROTECTED = True
    AGENT_ID = "p2-control-topology"

    def __init__(
        self,
        output_dir: Path | str = Path("analysis"),
        community_algorithms: list[str] | None = None,
        centrality_timeout_seconds: int = 1800,
    ) -> None:
        self.output_dir = Path(output_dir)
        # Must include at least Leiden + Louvain — robustness requires both
        self.community_algorithms = community_algorithms or ["leiden", "louvain"]
        # Approximate centrality (sampling) if full computation exceeds timeout
        self.centrality_timeout_seconds = centrality_timeout_seconds

    def run_exploratory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Build graph, compute topology metrics, detect communities.

        Must NOT access test_ids.
        All outputs EXP_-prefixed. No community structure claimed as authoritative
        until Leiden + Louvain agree within tolerance.
        """
        raise NotImplementedError(
            "P2 exploratory topology analysis not yet implemented. "
            "Phase 1 implementation will: (1) load STRM mappings, "
            "(2) construct directed/undirected graph per edge type, "
            "(3) compute centrality metrics (batch if needed for scale), "
            "(4) run Leiden + Louvain community detection, "
            "(5) write EXP_P2_graph.graphml, topology.parquet, communities.parquet, hubs.md."
        )

    def run_confirmatory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Execute one pre-registered confirmatory test on test split graph.

        Gate 2 approval verified by BaseResearchAgent.__call__.
        Requires: state["current_hypothesis_id"] == "H2.[n]"
        """
        raise NotImplementedError(
            "P2 confirmatory analysis not yet implemented. "
            "Requires: Gate 2 approved, hypothesis_id in state."
        )

    def _tag_nist_cluster(self, node_attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Add nist_cluster=True to node attributes for NIST framework nodes.

        Must be applied during graph construction so community detection
        reports can flag NIST-internal communities.
        """
        framework = node_attrs.get("framework", "")
        node_attrs["nist_cluster"] = framework.upper() in {
            "NIST 800-53", "NIST CSF", "NIST 800-171"
        }
        return node_attrs

    def _impute_missing_strength(
        self,
        strength_score: float | None,
        median_strength: float,
    ) -> tuple[float, bool]:
        """
        Impute missing edge weight at median. Returns (value, was_imputed).

        Imputation must be logged in codebook — all imputed edges labeled
        strength_imputed=True in the GraphML output.
        """
        if strength_score is None:
            return median_strength, True
        return strength_score, False
