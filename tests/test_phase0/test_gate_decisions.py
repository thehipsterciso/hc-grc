"""
Decision-path coverage for every gate node (hardening pass 1, #152 / #155).

Each gate uses interrupt(), so it is exercised inside a minimal single-node graph
with a checkpointer: invoke parks at the interrupt, a Command(resume=...) delivers
the operator decision, and we assert the recorded gate_status. Covers approved /
rejected / deferred for all five gates, including the previously-untested
deferred path.
"""

from __future__ import annotations

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import Command

from src.nodes.gates import (
    gate_1_node,
    gate_2_node,
    gate_3_node,
    gate_4_node,
    gate_5_node,
)
from src.nodes.orchestrator import route_after_gate_1, route_after_gate_2
from src.state import HCGRCState, initial_state


def _single_gate_graph(node, cp):
    builder = StateGraph(HCGRCState)
    builder.add_node("g", node)
    builder.set_entry_point("g")
    builder.add_edge("g", END)
    return builder.compile(checkpointer=cp)


@pytest.mark.parametrize("gid,node", [
    ("gate_1", gate_1_node),
    ("gate_3", gate_3_node),
    ("gate_4", gate_4_node),
    ("gate_5", gate_5_node),
])
@pytest.mark.parametrize("decision", ["approved", "rejected", "deferred"])
def test_gate_records_decision(gid, node, decision):
    cp = MemorySaver()
    graph = _single_gate_graph(node, cp)
    tid = f"{gid}-{decision}"
    cfg = {"configurable": {"thread_id": tid}}
    graph.invoke(initial_state(run_id=tid), config=cfg)  # parks at interrupt
    graph.invoke(Command(resume={"decision": decision, "rationale": "r"}), config=cfg)

    rec = graph.get_state(cfg).values["gate_status"][gid]
    assert rec["decision"] == decision
    # Non-approval must leave a failure_event for the Agent-Evolution monitor.
    events = graph.get_state(cfg).values.get("failure_events", [])
    if decision != "approved":
        assert any(e.get("gate_id") == gid for e in events)


@pytest.mark.parametrize("decision", ["approved", "rejected", "deferred"])
def test_gate_2_records_decision(decision):
    cp = MemorySaver()
    graph = _single_gate_graph(gate_2_node, cp)
    cfg = {"configurable": {"thread_id": f"gate_2-{decision}"}}
    state = initial_state(run_id=f"gate_2-{decision}")
    state["data_split_verified"] = True  # clear the hard prerequisite
    graph.invoke(state, config=cfg)
    graph.invoke(Command(resume={"decision": decision, "rationale": "r"}), config=cfg)
    assert graph.get_state(cfg).values["gate_status"]["gate_2"]["decision"] == decision


def test_routing_deferred_paths_park():
    state = initial_state(run_id="route-deferred")
    state["gate_status"] = {"gate_1": {"decision": "deferred"}}
    assert route_after_gate_1(state) == "end"
    state["gate_status"] = {"gate_2": {"decision": "deferred"}}
    assert route_after_gate_2(state) == "end"


def test_routing_rejected_gate_2_loops_to_exploratory():
    state = initial_state(run_id="route-rej")
    state["gate_status"] = {"gate_2": {"decision": "rejected"}}
    assert route_after_gate_2(state) == "exploratory_entry"
