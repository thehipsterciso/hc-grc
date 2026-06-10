"""
T-00 Minimal Orchestrator — Phase 0 routing skeleton.

In Phase 0, T-00 routes the graph through:
  data_split → gate_1 → [approved: phase_1_entry | rejected: end]

Full routing logic (T-00 with Agent Evolution, DSPy optimization) is
deferred to Phase 1. What is established here:
  - Routing function signature that all later phases extend
  - Gate decision inspection pattern
  - Escalation trigger pattern (if gate_5 fires)

Per ADR-0015 (#72): Agent Evolution monitors failure_events and
autonomously re-optimizes T-00 routing via DSPy between tiers.
Protected agents (P1-P5, statistical-analyst, hypothesis-formalizer)
cannot be modified by Agent Evolution without Escalation approval.
"""

from __future__ import annotations

from typing import Any

from ..state import HCGRCState


def route_after_gate_1(state: HCGRCState) -> str:
    """
    Conditional edge after Gate 1.

    Returns the name of the next node based on the Gate 1 decision.
    LangGraph uses this string to select the next node in the graph.
    """
    gate_status = state.get("gate_status", {})
    gate_1 = gate_status.get("gate_1")

    if gate_1 is None:
        # Gate 1 hasn't fired yet — shouldn't happen in normal flow
        return "end"

    decision = gate_1.get("decision", "rejected")

    if decision == "approved":
        return "phase_1_entry"
    elif decision == "deferred":
        # Platform parks; operator will re-trigger when ready
        return "end"
    else:
        # rejected — platform stays in Phase 0
        return "end"


def route_after_gate_2(state: HCGRCState) -> str:
    """Conditional edge after Gate 2."""
    gate_status = state.get("gate_status", {})
    gate_2 = gate_status.get("gate_2")

    if gate_2 is None:
        return "end"

    decision = gate_2.get("decision", "rejected")

    if decision == "approved":
        return "confirmatory_entry"
    elif decision == "deferred":
        return "end"
    else:
        return "exploratory_entry"  # rejected: return to exploratory


def t00_orchestrator_node(state: HCGRCState) -> dict[str, Any]:
    """
    T-00 orchestrator node.

    Phase 0: minimal pass-through that records entry into orchestration.
    Phase 1+: Agent Evolution will optimize this node's routing logic.

    Does not modify gate_status (only GateCoordinatorNode may do that).
    """
    return {
        "prov_activities": [
            {
                "activity": "t00_orchestration",
                "run_id": state.get("run_id"),
                "phase": state.get("phase"),
                "note": "Phase 0 minimal orchestrator — routing skeleton",
            }
        ]
    }
