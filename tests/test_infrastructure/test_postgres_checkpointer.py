"""
Phase-0 #110: PostgresSaver checkpointing confirmed on the compute node.

Runs the Phase-0 graph through the real local PostgresSaver (hcgrc DB) and
verifies state is checkpointed and retrievable by thread_id (== run_id, per
ADR-0015 #79). Skips cleanly if Postgres is unreachable.
"""
from __future__ import annotations

import pytest

from src.checkpointer import get_checkpointer
from src.graph import build_graph
from src.state import initial_state


@pytest.fixture(scope="module")
def pg_checkpointer():
    try:
        return get_checkpointer(use_memory=False)
    except Exception as exc:  # noqa: BLE001 — skip rather than fail if no Postgres
        pytest.skip(f"PostgresSaver unavailable: {exc}")


def test_postgres_checkpoint_persists_and_replays(pg_checkpointer):
    run_id = "test-pg-checkpoint-110"
    config = {"configurable": {"thread_id": run_id}}
    graph = build_graph(checkpointer=pg_checkpointer)

    # Runs orchestrator -> data_split -> gate_1 (interrupt). Checkpoint is written.
    graph.invoke(initial_state(run_id=run_id), config=config)

    snap = graph.get_state(config)
    assert snap is not None, "no checkpoint persisted to Postgres"
    assert snap.values.get("run_id") == run_id          # thread_id == run_id
    assert snap.values.get("data_split_verified") is True  # data_split ran pre-gate
    # Paused at gate_1 — there is a next node to resume into (proves replayability).
    assert snap.next, "expected a pending node (gate_1 interrupt) in the checkpoint"


def test_run_id_propagates_as_thread_id(pg_checkpointer):
    run_id = "test-pg-thread-110"
    config = {"configurable": {"thread_id": run_id}}
    graph = build_graph(checkpointer=pg_checkpointer)
    graph.invoke(initial_state(run_id=run_id), config=config)

    snap = graph.get_state(config)
    assert snap.config["configurable"]["thread_id"] == run_id
