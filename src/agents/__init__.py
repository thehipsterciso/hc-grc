"""
HC-GRC research agent library.

Protected agents (PROTECTED = True) may not have their prompts modified
autonomously by Agent Evolution. Modification requires Escalation approval
per ADR-0015 §77.

Phase 1 agents (P1-P5, statistical-analyst, hypothesis-formalizer) are
scaffolded — interfaces and behavioral constraints defined, implementations
raise NotImplementedError until Phase 1 build on the Mac mini.

NOTE: Importable modules use snake_case directory names. The hyphenated
directories (statistical-analyst/, hypothesis-formalizer/) are dead weight
and should be removed (tracked in git cleanup).
"""

from .p1_strm_nlp import P1StrmNlpAgent
from .p2_control_topology import P2ControlTopologyAgent
from .p3_regulatory_convergence import P3RegulatoryConvergenceAgent
from .p4_risk_blindspot import P4RiskBlindspotAgent
from .p5_ai_governance import P5AiGovernanceAgent
from .statistical_analyst import StatisticalAnalystAgent
from .hypothesis_formalizer import HypothesisFormalizerAgent

__all__ = [
    "P1StrmNlpAgent",
    "P2ControlTopologyAgent",
    "P3RegulatoryConvergenceAgent",
    "P4RiskBlindspotAgent",
    "P5AiGovernanceAgent",
    "StatisticalAnalystAgent",
    "HypothesisFormalizerAgent",
]
