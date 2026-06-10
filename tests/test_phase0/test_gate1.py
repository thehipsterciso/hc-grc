"""
test_gate1.py — Gate 1 fires with synthetic payload.

Phase 0 deliverable #2: verify that Gate 1 interrupt() fires correctly
and the graph resumes correctly after an operator response is injected.

Tests:
  1. Gate 1 fires (graph pauses at interrupt) with synthetic state
  2. Graph resumes with 'approved' response → routes to phase_1_entry
  3. Graph resumes with 'rejected' response → routes to END
  4. Gate decision is written to gate_status by gate_coordinator
  5. failure_event is appended on rejection
  6. run_id is preserved through the full flow
"""

from __future__ import annotations

import uuid

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from src.graph import build_graph
from src.state import initial_state


@pytest.fixture
def graph_with_memory():
    """Build graph with MemorySaver — no Postgres required for Phase 0 tests."""
    checkpointer = MemorySaver()
    return build_graph(checkpointer=checkpointer)


@pytest.fixture
def run_id():
    return str(uuid.uuid4())


def _thread_config(run_id: str) -> dict:
    return {"configurable": {"thread_id": run_id}}


class TestGate1Fires:
    """Gate 1 interrupt() fires and surfaces the correct proposal."""

    def test_gate1_interrupt_fires(self, graph_with_memory, run_id):
        """Graph pauses at Gate 1 and returns an interrupt value."""
        state = initial_state(run_id=run_id)
        config = _thread_config(run_id)

        # Run until interrupt
        result = graph_with_memory.invoke(state, config=config)

        # With MemorySaver, invoke returns after interrupt — check snapshot
        snapshot = graph_with_memory.get_state(config)
        assert snapshot is not None

        # The interrupt should have fired — next node is gate_1 resume
        tasks = snapshot.tasks
        assert len(tasks) > 0, "Expected a pending interrupt task"

        # Interrupt value should be the gate proposal
        interrupt_value = tasks[0].interrupts[0].value if tasks[0].interrupts else None
        assert interrupt_value is not None, "Expected interrupt value (gate proposal)"
        assert interrupt_value["gate_id"] == "gate_1"
        assert interrupt_value["title"] == "Gate 1 — Pre-Data Checkpoint"
        assert "checklist" in interrupt_value
        assert len(interrupt_value["checklist"]) >= 6

    def test_gate1_proposal_contains_run_id(self, graph_with_memory, run_id):
        """Gate 1 proposal includes the run_id from state."""
        state = initial_state(run_id=run_id)
        config = _thread_config(run_id)

        graph_with_memory.invoke(state, config=config)
        snapshot = graph_with_memory.get_state(config)

        tasks = snapshot.tasks
        interrupt_value = tasks[0].interrupts[0].value
        assert interrupt_value["run_id"] == run_id

    def test_data_split_runs_before_gate1(self, graph_with_memory, run_id):
        """data_split_node runs before Gate 1 fires."""
        state = initial_state(run_id=run_id)
        config = _thread_config(run_id)

        graph_with_memory.invoke(state, config=config)
        snapshot = graph_with_memory.get_state(config)

        # data_split should have populated state
        current_state = snapshot.values
        assert current_state.get("data_split_verified") is True
        assert current_state.get("data_split_seed") is not None
        assert current_state.get("data_split_manifest_hash") is None  # synthetic — no manifest


class TestGate1Approved:
    """Gate 1 approves → graph routes to phase_1_entry."""

    def test_approved_routes_to_phase1(self, graph_with_memory, run_id):
        """Approved Gate 1 resumes and routes to phase_1_entry."""
        state = initial_state(run_id=run_id)
        config = _thread_config(run_id)

        # Run to Gate 1 interrupt
        graph_with_memory.invoke(state, config=config)

        # Resume with approval
        approved_response = {"decision": "approved", "rationale": "All Phase 0 prerequisites verified."}
        final = graph_with_memory.invoke(
            Command(resume=approved_response),
            config=config,
        )

        final_state = graph_with_memory.get_state(config).values

        # Gate 1 decision should be recorded
        gate_status = final_state.get("gate_status", {})
        assert "gate_1" in gate_status
        assert gate_status["gate_1"]["decision"] == "approved"
        assert gate_status["gate_1"]["run_id"] == run_id

        # Phase should advance
        assert final_state.get("phase") == "phase_1"

    def test_approved_no_failure_event(self, graph_with_memory, run_id):
        """No failure_event on approval."""
        state = initial_state(run_id=run_id)
        config = _thread_config(run_id)

        graph_with_memory.invoke(state, config=config)
        graph_with_memory.invoke(
            Command(resume={"decision": "approved", "rationale": "All good."}),
            config=config,
        )

        final_state = graph_with_memory.get_state(config).values
        gate_failures = [
            e for e in final_state.get("failure_events", [])
            if e.get("gate_id") == "gate_1"
        ]
        assert len(gate_failures) == 0


class TestGate1Rejected:
    """Gate 1 rejects → failure_event appended, graph ends."""

    def test_rejected_appends_failure_event(self, graph_with_memory, run_id):
        """Rejected Gate 1 appends a failure_event for Agent Evolution."""
        state = initial_state(run_id=run_id)
        config = _thread_config(run_id)

        graph_with_memory.invoke(state, config=config)
        graph_with_memory.invoke(
            Command(resume={"decision": "rejected", "rationale": "Diversity anchors not identified."}),
            config=config,
        )

        final_state = graph_with_memory.get_state(config).values
        gate_status = final_state.get("gate_status", {})

        assert "gate_1" in gate_status
        assert gate_status["gate_1"]["decision"] == "rejected"

        failure_events = final_state.get("failure_events", [])
        gate_failures = [e for e in failure_events if e.get("gate_id") == "gate_1"]
        assert len(gate_failures) == 1
        assert gate_failures[0]["event_type"] == "gate_rejection"
        assert "Diversity anchors" in gate_failures[0]["rationale"]

    def test_rejected_records_run_id(self, graph_with_memory, run_id):
        """failure_event carries the run_id for cross-store correlation."""
        state = initial_state(run_id=run_id)
        config = _thread_config(run_id)

        graph_with_memory.invoke(state, config=config)
        graph_with_memory.invoke(
            Command(resume={"decision": "rejected", "rationale": "Not ready."}),
            config=config,
        )

        final_state = graph_with_memory.get_state(config).values
        failure_events = final_state.get("failure_events", [])
        gate_failures = [e for e in failure_events if e.get("gate_id") == "gate_1"]

        assert gate_failures[0]["run_id"] == run_id
