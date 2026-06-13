"""
T-00 Orchestrator — run-start grounding + Phase 0 routing.

In Phase 0, T-00 routes the graph through:
  data_split → gate_1 → [approved: phase_1_entry | rejected: end]

What is established here:
  - Run-start grounding: the orchestrator reasons about the run *through the
    framework* (reasoning_client, Tier 2) — see t00_orchestrator_node. This is
    the agency contract: orchestration happens inside the graph, not by hand
    outside it (ADR-0016 / MODEL_TIER_ASSIGNMENTS.md routes the orchestrator
    to Tier 2, escalating to Tier 3 only for hard decisions).
  - Routing function signature that all later phases extend
  - Gate decision inspection pattern

Per ADR-0015 (#72): Agent Evolution monitors failure_events and
autonomously re-optimizes T-00 routing via DSPy between tiers.
Protected agents (P1-P5, statistical-analyst, hypothesis-formalizer)
cannot be modified by Agent Evolution without Escalation approval.
"""

from __future__ import annotations

from typing import Any

from ..reasoning_client import ReasoningError, Tier, complete
from ..state import HCGRCState

# T-00's stakes tier (agents/MODEL_TIER_ASSIGNMENTS.md): routine routing is
# local; only hard escalations invoke Tier 3.
_ORCHESTRATOR_TIER = Tier.T2

_ORCHESTRATOR_SYSTEM = (
    "You are T-00, the orchestrator of the HC-GRC research platform — a "
    "LangGraph agency that empirically tests the Secure Controls Framework's "
    "STRM mappings under a five-gate human-in-the-loop governance topology. "
    "At run start you ground the run: state the immediate objective, the next "
    "structural step in the graph, the gate it leads to, and the preconditions "
    "that must hold before that gate can be approved. Be concise and concrete. "
    "You do not approve gates and you do not fabricate results — you orient the "
    "run. Respond in at most 120 words."
)

# Static description of the graph ahead, fed to the orchestrator so its grounding
# is anchored to the real topology rather than invented.
_PHASE_TOPOLOGY = {
    "phase_0": (
        "Phase 0 (current): data_split (SHA-256 seeded 70/15/15) → Gate 1 "
        "(pre-data checkpoint). Gate 1 preconditions: LangGraph skeleton runs, "
        "data-split idempotency verified, PostgresSaver benchmark logged, "
        "governance dry-run complete. Approval unlocks Phase 1 data ingestion."
    ),
    "phase_1": (
        "Phase 1 (current): data_pipeline → exploratory P1-P5 → "
        "hypothesis_formalize → Gate 2 (exploratory→confirmatory; locks the "
        "pre-registered hypothesis set and unlocks the test split — irreversible)."
    ),
    "phase_2": (
        "Phase 2 (current): confirmatory subgraph → Gate 3/4/5. Test split is "
        "live only after Gate 2 approval; every confirmatory script carries a "
        "SAP header."
    ),
}


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
    T-00 orchestrator node — run-start grounding through the framework.

    The orchestrator reasons about the run via the reasoning_client (Tier 2):
    it produces a concise grounding (objective, next step, the gate ahead, the
    preconditions) that is written to state["run_grounding"] and recorded in
    provenance. This is the agency contract — orchestration is performed by the
    graph, not by a human operating outside it.

    Degrades gracefully: if the Tier 2 backend is unavailable (offline CI,
    dry-run with no Ollama), run_grounding stays None and the run proceeds. The
    graph never depends on a live model to advance.

    Does not modify gate_status (only gate_coordinator_node may do that).
    """
    run_id = state.get("run_id")
    phase = state.get("phase", "phase_0")
    topology = _PHASE_TOPOLOGY.get(phase, _PHASE_TOPOLOGY["phase_0"])

    prompt = (
        f"Run {run_id} is starting in {phase}.\n"
        f"Graph ahead: {topology}\n\n"
        "Ground this run."
    )

    grounding: str | None = None
    try:
        grounding = complete(_ORCHESTRATOR_TIER, prompt, system=_ORCHESTRATOR_SYSTEM)
        note = f"T-00 run-start grounding produced via reasoning_client ({_ORCHESTRATOR_TIER.value})"
    except ReasoningError as exc:
        # Backend unavailable — record the degradation and proceed.
        note = f"T-00 grounding unavailable ({exc}); proceeding without grounding"

    return {
        "run_grounding": grounding,
        "prov_activities": [
            {
                "activity": "t00_orchestration",
                "run_id": run_id,
                "phase": phase,
                "tier": _ORCHESTRATOR_TIER.value,
                "grounded": grounding is not None,
                "note": note,
            }
        ],
    }
