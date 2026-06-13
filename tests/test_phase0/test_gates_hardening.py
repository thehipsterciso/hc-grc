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


def test_gate_node_is_noop_when_already_approved():
    # pass-4 #6: re-entering a gate that already holds a terminal decision must be
    # a no-op (no re-fired interrupt, no re-run side effects).
    from src.nodes.gates import gate_1_node
    state = initial_state(run_id="idem-001")
    state["gate_status"] = {"gate_1": {"decision": "approved", "rationale": "r"}}
    assert gate_1_node(state) == {}


def test_only_approved_is_terminal():
    # pass-2 #184/#187 + pass-3 #5: rejected re-reviews and deferred is re-triggerable,
    # so only 'approved' is terminal (stops the gate re-firing on re-entry).
    state = initial_state(run_id="g-rej")
    for non_terminal in ("rejected", "deferred"):
        state["gate_status"] = {"gate_2": {"decision": non_terminal}}
        assert _already_decided(state, "gate_2") is False
    state["gate_status"] = {"gate_2": {"decision": "approved"}}
    assert _already_decided(state, "gate_2") is True


def test_gate_id_correlation_rejects_mismatched_decision():
    # pass-4 #3/#5: a resume decision targeted at a different gate must NOT finalize
    # the parked gate — it re-prompts. resume_run now carries gate_id end to end.
    cp = MemorySaver()
    graph = build_graph(checkpointer=cp)
    cfg = {"configurable": {"thread_id": "corr-001"}}
    graph.invoke(initial_state(run_id="corr-001"), config=cfg)  # parks at gate_1

    # Decision aimed at gate_2 while gate_1 is parked → ignored, gate_1 undecided.
    resume_run("corr-001", "approved", "x", cp, gate_id="gate_2")
    assert "gate_1" not in build_graph(checkpointer=cp).get_state(cfg).values.get("gate_status", {})

    # Correctly targeted decision finalizes.
    resume_run("corr-001", "approved", "ok", cp, gate_id="gate_1")
    assert build_graph(checkpointer=cp).get_state(cfg).values["gate_status"]["gate_1"]["decision"] == "approved"


# ── Gate 2 prerequisite failure writes a visible decision (#164 / #178) ────────


def test_gate2_prereq_failure_writes_gate_status():
    state = initial_state(run_id="g-002")  # prerequisites unmet
    update = gate_2_node(state)
    assert "gate_2" in update["gate_status"]
    # Deferred (a park), not rejected — a prereq failure must not feed the
    # reject→re-review loop (pass-3 #20).
    assert update["gate_status"]["gate_2"]["decision"] == "deferred"
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


def test_resume_run_recovers_from_malformed_decision():
    # pass-3 #3: a malformed resume must NOT brick the gate — it re-prompts, and a
    # subsequent well-formed resume finalizes the gate (recovery actually works).
    cp = MemorySaver()
    graph = build_graph(checkpointer=cp)
    cfg = {"configurable": {"thread_id": "resume-002"}}
    graph.invoke(initial_state(run_id="resume-002"), config=cfg)  # parks at gate_1

    # Malformed decision: does not raise, does not record a terminal decision.
    resume_run("resume-002", "totally-bogus", "x", cp)
    parked = build_graph(checkpointer=cp).get_state(cfg).values
    assert "gate_1" not in parked.get("gate_status", {})

    # Well-formed decision now recovers and finalizes.
    resume_run("resume-002", "approved", "ok", cp)
    decided = build_graph(checkpointer=cp).get_state(cfg).values
    assert decided["gate_status"]["gate_1"]["decision"] == "approved"
