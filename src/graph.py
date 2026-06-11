"""
HC-GRC main LangGraph graph — Phase 0 skeleton.

Graph topology (Phase 0):
  orchestrator → data_split → gate_1 → [approved: phase_1_entry | else: END]

Gate nodes use interrupt() to surface proposals to the operator.
All gate decisions are written by gate_coordinator (serialized, no concurrent writes).

Phase 1 additions (not here yet):
  - Exploratory analysis subgraph (P1-P5 agents in parallel)
  - Agent Evolution loop monitoring failure_events
  - gate_2 → confirmatory subgraph

Per ADR-0015: run_id propagates through thread_config to PostgresSaver
and to all four observability stores.
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph

from .nodes.data_split import data_split_node
from .nodes.gates import gate_1_node
from .nodes.orchestrator import route_after_gate_1, t00_orchestrator_node
from .state import HCGRCState, initial_state


# ── Placeholder nodes (Phase 1+) ─────────────────────────────────────────────

def phase_1_entry_node(state: HCGRCState) -> dict[str, Any]:
    """Placeholder: Phase 1 exploratory analysis entry point."""
    return {
        "phase": "phase_1",
        "prov_activities": [
            {
                "activity": "phase_1_entry",
                "run_id": state["run_id"],
                "note": "Phase 1 not yet implemented — stub node",
            }
        ],
    }


# ── Graph builder ─────────────────────────────────────────────────────────────

def build_graph(checkpointer=None) -> StateGraph:
    """
    Build and compile the HC-GRC LangGraph graph.

    Args:
        checkpointer: LangGraph checkpointer (MemorySaver for Phase 0,
                      PostgresSaver for Phase 1+). If None, graph runs
                      without persistence (stateless — for unit tests only).

    Returns:
        Compiled LangGraph graph.
    """
    builder = StateGraph(HCGRCState)

    # ── Nodes ─────────────────────────────────────────────────────────────────
    builder.add_node("orchestrator", t00_orchestrator_node)

    # data_split_node needs synthetic_control_ids in Phase 0.
    # Wrap it to pass synthetic IDs if no manifest is present.
    def _data_split_phase0(state: HCGRCState) -> dict[str, Any]:
        # Phase 0: use 1,400 synthetic control IDs matching SCF scale
        synthetic_ids = [f"SCF-CTRL-{i:04d}" for i in range(1400)]
        return data_split_node(state, synthetic_control_ids=synthetic_ids)

    builder.add_node("data_split", _data_split_phase0)
    builder.add_node("gate_1", gate_1_node)
    builder.add_node("phase_1_entry", phase_1_entry_node)

    # ── Edges ─────────────────────────────────────────────────────────────────
    builder.set_entry_point("orchestrator")
    builder.add_edge("orchestrator", "data_split")
    builder.add_edge("data_split", "gate_1")

    # Conditional routing after Gate 1
    builder.add_conditional_edges(
        "gate_1",
        route_after_gate_1,
        {
            "phase_1_entry": "phase_1_entry",
            "end": END,
        },
    )

    builder.add_edge("phase_1_entry", END)

    # ── Compile ───────────────────────────────────────────────────────────────
    compile_kwargs: dict[str, Any] = {}
    if checkpointer is not None:
        compile_kwargs["checkpointer"] = checkpointer

    return builder.compile(**compile_kwargs)


# ── Convenience runner ────────────────────────────────────────────────────────

def run_phase0_synthetic(run_id: str | None = None, checkpointer=None) -> dict[str, Any]:
    """
    Execute one complete Phase 0 synthetic run.

    The graph will pause at Gate 1 and wait for operator input.
    This function is used in the governance dry-run.

    For tests that need to skip the interrupt, use the graph's
    .invoke() with a pre-configured Command resume.
    """
    graph = build_graph(checkpointer=checkpointer)
    state = initial_state(run_id=run_id)
    thread_config = {"configurable": {"thread_id": state["run_id"]}}
    result = graph.invoke(state, config=thread_config)
    return result
