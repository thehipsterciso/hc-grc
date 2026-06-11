"""
HC-GRC research agent library.

Protected agents (PROTECTED = True) may not have their prompts modified
autonomously by Agent Evolution. Modification requires Escalation approval
per ADR-0015 §77.

Phase 1 agents (P1-P5, statistical-analyst, hypothesis-formalizer) are
scaffolded — interfaces and behavioral constraints defined, implementations
raise NotImplementedError until Phase 1 build on the Mac mini.
"""

from .p1_strm_nlp import P1StrmNlpAgent
from .p2_control_topology import P2ControlTopologyAgent
from .p3_regulatory_convergence import P3RegulatoryConvergenceAgent
from .p4_risk_blindspot import P4RiskBlindspotAgent
from .p5_ai_governance import P5AiGovernanceAgent

__all__ = [
    "P1StrmNlpAgent",
    "P2ControlTopologyAgent",
    "P3RegulatoryConvergenceAgent",
    "P4RiskBlindspotAgent",
    "P5AiGovernanceAgent",
]
