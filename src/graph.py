"""
HC-GRC main LangGraph graph — Phase 0 + Phase 1 exploratory subgraph.

Graph topology (Phase 0 + Phase 1):

  orchestrator
      ↓
  data_split          ← SHA-256 seeded 70/15/15 split (synthetic in Phase 0)
      ↓
  gate_1              ← interrupt() — pre-data checkpoint
      ↓ [approved]
  data_pipeline       ← DataAcquisitionAgent → DataCurationAgent
      ↓                  → DataStewardAgent → EmbeddingAgent
  exploratory_phase   ← P1 → P2 → P3 → P4 → P5 (sequential; TODO: Send() fan-out)
      ↓
  hypothesis_formalize ← HypothesisFormalizerAgent
      ↓
  gate_2              ← interrupt() — SAP lock, hypothesis pre-registration
      ↓ [approved]
  confirmatory_entry  ← Phase 2 stub (route_after_gate_2 → "confirmatory_entry")
      ↓ [rejected]
  exploratory_phase   ← loop back to re-run EDA with revised hypotheses

  gate_3, gate_4, gate_5 are Phase 2 mechanism work — nodes registered here
  so routing functions can reference them, but edges from confirmatory subgraph
  are deferred.

Gate nodes use interrupt() to surface proposals to the operator.
All gate decisions are written by gate_coordinator (serialized, no concurrent writes).

Per ADR-0015: run_id propagates through thread_config to PostgresSaver
and to all four observability stores.
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph
from langgraph.types import Command, RetryPolicy

from .infrastructure.observability.phoenix_setup import (
    bootstrap_observability,
    run_trace_context,
)
from .nodes.data_split import data_split_node
from .nodes.gates import gate_1_node, gate_2_node, gate_3_node, gate_4_node, gate_5_node
from .nodes.orchestrator import route_after_gate_1, route_after_gate_2, t00_orchestrator_node
from .nodes.phase1 import (
    confirmatory_entry_node,
    data_pipeline_node,
    exploratory_phase_node,
    hypothesis_formalize_node,
)
from .state import HCGRCState, initial_state

# Upper bound on graph super-steps per run. Bounds the Gate-2-rejected loop back
# to exploratory analysis so a non-converging run fails loudly (#179).
GRAPH_RECURSION_LIMIT = 50

# Exceptions that must NOT be retried by node RetryPolicy: governance violations
# and deterministic logic errors. Anything else (transient infra) is retryable.
_NON_RETRYABLE = (
    NotImplementedError,
    ValueError,
    KeyError,
    TypeError,
    AssertionError,
)


def _is_transient_node_error(exc: BaseException) -> bool:
    """RetryPolicy predicate: retry transient faults, never governance/logic errors."""
    from .agents.base import SAPViolationError
    if isinstance(exc, SAPViolationError):
        return False
    return not isinstance(exc, _NON_RETRYABLE)

# ── Graph builder ─────────────────────────────────────────────────────────────

def build_graph(checkpointer=None) -> StateGraph:
    """
    Build and compile the HC-GRC LangGraph graph.

    Args:
        checkpointer: LangGraph checkpointer (MemorySaver for Phase 0/1,
                      PostgresSaver for production). If None, graph runs
                      without persistence (stateless — for unit tests only).

    Returns:
        Compiled LangGraph graph.
    """
    builder = StateGraph(HCGRCState)

    # Retry only TRANSIENT node failures (network blips, checkpoint write hiccups,
    # backend stalls) with backoff — ADR-0011 resilience (#165). Governance and
    # logic errors must NEVER be retried: re-running a SAPViolationError would
    # re-execute the pre-registration-firewall violation up to 3x instead of
    # halting immediately (pass-2 #186/#188/#3/#5), and retrying NotImplementedError
    # / ValueError just wastes backoff on a deterministic failure (#201/#18). Gate
    # nodes are excluded entirely because they use interrupt().
    agent_retry = RetryPolicy(
        max_attempts=3, initial_interval=0.5, backoff_factor=2.0,
        retry_on=_is_transient_node_error,
    )

    # ── Phase 0 nodes ─────────────────────────────────────────────────────────
    builder.add_node("orchestrator", t00_orchestrator_node, retry=agent_retry)

    # data_split_node needs synthetic_control_ids in Phase 0.
    # In Phase 1, DataStewardAgent writes real splits to disk.
    # Phase 0 wrapper: synthetic IDs matching SCF scale for gate dry-runs.
    def _data_split_phase0(state: HCGRCState) -> dict[str, Any]:
        synthetic_ids = [f"SCF-CTRL-{i:04d}" for i in range(1400)]
        return data_split_node(state, synthetic_control_ids=synthetic_ids)

    builder.add_node("data_split", _data_split_phase0)
    builder.add_node("gate_1", gate_1_node)

    # ── Phase 1 nodes ─────────────────────────────────────────────────────────
    builder.add_node("data_pipeline", data_pipeline_node, retry=agent_retry)
    builder.add_node("exploratory_phase", exploratory_phase_node, retry=agent_retry)
    builder.add_node("hypothesis_formalize", hypothesis_formalize_node, retry=agent_retry)
    builder.add_node("gate_2", gate_2_node)

    # ── Phase 2 stubs (nodes registered; edges from confirmatory subgraph deferred) ──
    builder.add_node("confirmatory_entry", confirmatory_entry_node)
    builder.add_node("gate_3", gate_3_node)
    builder.add_node("gate_4", gate_4_node)
    builder.add_node("gate_5", gate_5_node)

    # ── Edges — Phase 0 ───────────────────────────────────────────────────────
    builder.set_entry_point("orchestrator")
    builder.add_edge("orchestrator", "data_split")
    builder.add_edge("data_split", "gate_1")

    builder.add_conditional_edges(
        "gate_1",
        route_after_gate_1,
        {
            "phase_1_entry": "data_pipeline",  # approved → Phase 1 data pipeline
            "end": END,
        },
    )

    # ── Edges — Phase 1 exploratory ───────────────────────────────────────────
    builder.add_edge("data_pipeline", "exploratory_phase")
    builder.add_edge("exploratory_phase", "hypothesis_formalize")
    builder.add_edge("hypothesis_formalize", "gate_2")

    builder.add_conditional_edges(
        "gate_2",
        route_after_gate_2,
        {
            "confirmatory_entry": "confirmatory_entry",  # approved → Phase 2
            "exploratory_entry": "exploratory_phase",    # rejected → re-run EDA
            "end": END,                                   # deferred → park
        },
    )

    # ── Phase 2 stub edges ────────────────────────────────────────────────────
    # confirmatory_entry → gate_3 → gate_4 → gate_5 will be wired in Phase 2.
    # For now, confirmatory_entry routes to END so the graph compiles.
    builder.add_edge("confirmatory_entry", END)

    # gate_3, gate_4, gate_5 are reachable (registered) but not yet wired
    # into the confirmatory subgraph. They connect to END to keep graph valid.
    builder.add_edge("gate_3", END)
    builder.add_edge("gate_4", END)
    builder.add_edge("gate_5", END)

    # ── Compile ───────────────────────────────────────────────────────────────
    compile_kwargs: dict[str, Any] = {}
    if checkpointer is not None:
        compile_kwargs["checkpointer"] = checkpointer

    return builder.compile(**compile_kwargs)


# ── Convenience runners ───────────────────────────────────────────────────────

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
    bootstrap_observability(state["run_id"])
    # Explicit recursion_limit bounds the Gate-2-rejected → exploratory loop so a
    # run that never converges terminates with GraphRecursionError instead of
    # looping unbounded (#179).
    thread_config = {
        "configurable": {"thread_id": state["run_id"]},
        "recursion_limit": GRAPH_RECURSION_LIMIT,
    }
    with run_trace_context(state["run_id"]):
        result = graph.invoke(state, config=thread_config)
    return result


def resume_run(run_id: str, decision: str, rationale: str, checkpointer,
               *, checkpoint_id: str | None = None) -> dict[str, Any]:
    """
    Resume a run parked at a gate interrupt with the operator's decision.

    The runners invoke the graph once and return when a gate's interrupt() parks
    it; this is the other half of the loop (#162). The operator's decision is
    delivered via the ADR-0014 governance channel and injected here as the
    interrupt's resume value, so the gate node observes
    {'decision': ..., 'rationale': ...} and the graph continues from the
    checkpoint.

    Requires the SAME checkpointer the run was started with (thread_id == run_id),
    so the parked state can be loaded.
    """
    graph = build_graph(checkpointer=checkpointer)
    bootstrap_observability(run_id)
    config: dict[str, Any] = {
        "configurable": {"thread_id": run_id},
        "recursion_limit": GRAPH_RECURSION_LIMIT,
    }
    if checkpoint_id:
        config["configurable"]["checkpoint_id"] = checkpoint_id
    resume_value = {"decision": decision, "rationale": rationale}
    with run_trace_context(run_id):
        return graph.invoke(Command(resume=resume_value), config=config)


def run_phase1_dry_run(run_id: str | None = None, checkpointer=None) -> dict[str, Any]:
    """
    Execute a Phase 1 dry run through Gate 2.

    Gate 1 and Gate 2 will pause for operator input. Data pipeline and P1-P5
    nodes will record stub_pending statuses (NotImplementedError caught). This
    verifies the Phase 1 graph topology before real SCF data is loaded.
    """
    graph = build_graph(checkpointer=checkpointer)
    state = initial_state(run_id=run_id)
    bootstrap_observability(state["run_id"])
    # Explicit recursion_limit bounds the Gate-2-rejected → exploratory loop so a
    # run that never converges terminates with GraphRecursionError instead of
    # looping unbounded (#179).
    thread_config = {
        "configurable": {"thread_id": state["run_id"]},
        "recursion_limit": GRAPH_RECURSION_LIMIT,
    }
    with run_trace_context(state["run_id"]):
        result = graph.invoke(state, config=thread_config)
    return result
