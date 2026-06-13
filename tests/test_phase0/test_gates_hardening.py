"""
Tests for gate interrupt-safety and fault isolation (hardening pass 1, batch 4).

Covers: operator-response validation (#163/#180), the already-decided idempotency
guard (#177), the Gate-2 prerequisite-failure gate_status record (#164/#178), and
the interrupt → resume path (#162).
"""

from __future__ import annotations

import pytest
from langgraph.checkpoint.memory import MemorySaver

from src.graph import build_graph, resume_run
from src.nodes.gates import _already_decided, _parse_operator_response, gate_2_node
from src.state import initial_state

# ── operator response validation (#163 / #180) ────────────────────────────────


def test_parse_valid_response():
    assert _parse_operator_response({"decision": "approved", "rationale": "ok"}, "gate_1") == (
        "approved", "ok")


def test_parse_fills_missing_rationale():
    decision, rationale = _parse_operator_response({"decision": "rejected"}, "gate_1")
    assert decision == "rejected"
    assert rationale  # non-empty default, not a crash


@pytest.mark.parametrize("bad", ["approved", 42, None, ["approved"]])
def test_parse_rejects_non_dict(bad):
    with pytest.raises(ValueError, match="must be a dict"):
        _parse_operator_response(bad, "gate_1")


@pytest.mark.parametrize("bad", [{"decision": "yes"}, {"decision": None}, {"rationale": "x"}])
def test_parse_rejects_bad_decision(bad):
    with pytest.raises(ValueError, match="decision"):
        _parse_operator_response(bad, "gate_1")


# ── idempotency guard (#177) ──────────────────────────────────────────────────


def test_already_decided():
    state = initial_state(run_id="g-001")
    assert _already_decided(state, "gate_1") is False
    state["gate_status"] = {"gate_1": {"decision": "approved"}}
    assert _already_decided(state, "gate_1") is True
    assert _already_decided(state, "gate_2") is False


# ── Gate 2 prerequisite failure writes a visible decision (#164 / #178) ────────


def test_gate2_prereq_failure_writes_gate_status():
    state = initial_state(run_id="g-002")  # data_split_verified is False
    update = gate_2_node(state)
    assert "gate_2" in update["gate_status"]
    assert update["gate_status"]["gate_2"]["decision"] == "rejected"
    assert update["gate_status"]["gate_2"]["reviewer"] == "system"
    assert update["failure_events"][0]["event_type"] == "gate_prerequisite_failure"


# ── interrupt → resume path (#162) ────────────────────────────────────────────


def test_resume_run_approves_gate_1():
    cp = MemorySaver()
    graph = build_graph(checkpointer=cp)
    cfg = {"configurable": {"thread_id": "resume-001"}}
    graph.invoke(initial_state(run_id="resume-001"), config=cfg)  # parks at gate_1

    resume_run("resume-001", "approved", "prerequisites met", cp)

    decision = build_graph(checkpointer=cp).get_state(cfg).values["gate_status"]["gate_1"]["decision"]
    assert decision == "approved"


def test_resume_run_rejects_malformed_decision():
    cp = MemorySaver()
    graph = build_graph(checkpointer=cp)
    cfg = {"configurable": {"thread_id": "resume-002"}}
    graph.invoke(initial_state(run_id="resume-002"), config=cfg)  # parks at gate_1

    with pytest.raises(ValueError, match="decision"):
        resume_run("resume-002", "totally-bogus", "x", cp)
