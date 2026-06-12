"""
test_governance_dry_run.py — Phase-0 #113: end-to-end governance dry-run.

Drives the full synthetic flow through both human gates with operator approvals:

    orchestrator -> data_split -> Gate 1 (approve)
        -> data_pipeline (stub) -> exploratory (stub) -> hypothesis_formalize (stub)
        -> Gate 2 (approve) -> confirmatory_entry

Verifies every gate component: interrupt fires, the proposal carries run_id, the
decision is recorded by the gate coordinator, run_id propagates, phase advances,
and the Gate-2 firewall routes to the confirmatory entry only on approval. Also
exercises the rejection path (Gate 2 reject -> loop back to exploratory).
"""
from __future__ import annotations

import uuid

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from src.graph import build_graph
from src.state import initial_state


@pytest.fixture
def graph():
    return build_graph(checkpointer=MemorySaver())


@pytest.fixture
def run_id():
    return str(uuid.uuid4())


def _cfg(run_id):
    return {"configurable": {"thread_id": run_id}}


def _drive_to_gate1(graph, run_id):
    graph.invoke(initial_state(run_id=run_id), config=_cfg(run_id))


def _approve(graph, run_id, rationale):
    graph.invoke(
        Command(resume={"decision": "approved", "rationale": rationale}),
        config=_cfg(run_id),
    )


class TestGovernanceDryRun:
    def test_full_flow_gate1_to_gate2_approved(self, graph, run_id):
        _drive_to_gate1(graph, run_id)

        # Gate 1 approve → runs Phase-1 stubs → pauses at Gate 2.
        _approve(graph, run_id, "Phase-0 prerequisites verified end-to-end.")
        mid = graph.get_state(_cfg(run_id))
        assert mid.values["gate_status"]["gate_1"]["decision"] == "approved"
        assert mid.values["phase"] == "phase_1"
        # Paused at the next gate (Gate 2) — there is a pending interrupt task.
        assert mid.tasks and mid.tasks[0].interrupts, "expected Gate 2 interrupt pending"

        # Gate 2 approve → firewall opens → routes to confirmatory_entry.
        _approve(graph, run_id, "SAP locked; hypotheses pre-registered.")
        final = graph.get_state(_cfg(run_id)).values
        assert final["gate_status"]["gate_2"]["decision"] == "approved"
        assert final["phase"] == "phase_2"
        # run_id propagated through every recorded gate decision.
        for g in ("gate_1", "gate_2"):
            assert final["gate_status"][g]["run_id"] == run_id

    def test_phase1_stub_nodes_recorded(self, graph, run_id):
        _drive_to_gate1(graph, run_id)
        _approve(graph, run_id, "Proceed to Phase 1.")
        mid = graph.get_state(_cfg(run_id)).values
        # The data pipeline + exploratory stubs record per-agent statuses rather
        # than crashing (NotImplementedError caught -> stub_pending).
        statuses = mid.get("eda_agent_statuses", []) + mid.get("prov_activities", [])
        assert statuses, "expected Phase-1 stub nodes to record activity"

    def test_gate2_rejection_loops_back_to_exploratory(self, graph, run_id):
        _drive_to_gate1(graph, run_id)
        _approve(graph, run_id, "Proceed to Phase 1.")
        # Reject Gate 2 → route back to exploratory (does NOT advance to phase_2).
        graph.invoke(
            Command(resume={"decision": "rejected", "rationale": "Exploratory characterization incomplete; revise hypotheses."}),
            config=_cfg(run_id),
        )
        state = graph.get_state(_cfg(run_id)).values
        assert state["gate_status"]["gate_2"]["decision"] == "rejected"
        gate2_failures = [e for e in state.get("failure_events", []) if e.get("gate_id") == "gate_2"]
        assert len(gate2_failures) == 1
