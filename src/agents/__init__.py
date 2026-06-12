"""
HC-GRC research agent library.

Protected agents (PROTECTED = True) may not have their prompts modified
autonomously by Agent Evolution. Modification requires Escalation approval
per ADR-0015 §77.

Phase 1 research agents (P1-P5, statistical-analyst, hypothesis-formalizer):
  Interfaces and behavioral constraints defined; implementations raise
  NotImplementedError until Phase 1 runs on the Mac mini with real SCF data.

Phase 1 pipeline agents (data-acquisition, data-curation, data-steward, embedding-agent):
  Interfaces, behavioral constraints, and error guards defined; run() raises
  NotImplementedError until data pipeline is live.
"""

# ── Research agents (PROTECTED) ───────────────────────────────────────────────
from .p1_strm_nlp import P1StrmNlpAgent
from .p2_control_topology import P2ControlTopologyAgent
from .p3_regulatory_convergence import P3RegulatoryConvergenceAgent
from .p4_risk_blindspot import P4RiskBlindspotAgent
from .p5_ai_governance import P5AiGovernanceAgent
from .statistical_analyst import StatisticalAnalystAgent
from .hypothesis_formalizer import HypothesisFormalizerAgent

# ── Data pipeline agents (not PROTECTED) ─────────────────────────────────────
from .data_acquisition import DataAcquisitionAgent
from .data_curation import DataCurationAgent
from .data_steward import DataStewardAgent
from .embedding_agent import EmbeddingAgent

__all__ = [
    # Research agents
    "P1StrmNlpAgent",
    "P2ControlTopologyAgent",
    "P3RegulatoryConvergenceAgent",
    "P4RiskBlindspotAgent",
    "P5AiGovernanceAgent",
    "StatisticalAnalystAgent",
    "HypothesisFormalizerAgent",
    # Pipeline agents
    "DataAcquisitionAgent",
    "DataCurationAgent",
    "DataStewardAgent",
    "EmbeddingAgent",
]
