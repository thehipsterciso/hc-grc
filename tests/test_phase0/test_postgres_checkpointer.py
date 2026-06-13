"""
Checkpointer factory tests (hardening pass 1, #161).

MemorySaver is always exercised. The PostgresSaver path (self-healing pool) is
exercised and round-tripped when Postgres is reachable, else skipped.
"""

from __future__ import annotations

import pytest
from langgraph.checkpoint.memory import MemorySaver

from src.checkpointer import get_checkpointer, get_postgres_connection_string
from src.state import initial_state


def test_memory_checkpointer():
    cp = get_checkpointer(use_memory=True)
    assert isinstance(cp, MemorySaver)


def _postgres_reachable() -> bool:
    try:
        import psycopg
        with psycopg.connect(get_postgres_connection_string(), connect_timeout=2):
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _postgres_reachable(), reason="Postgres not reachable")
def test_postgres_checkpointer_round_trips():
    from langgraph.checkpoint.postgres import PostgresSaver

    cp = get_checkpointer(use_memory=False)
    assert isinstance(cp, PostgresSaver)
    cfg = {"configurable": {"thread_id": "test-cp-roundtrip", "checkpoint_ns": ""}}
    # list() must succeed against the pooled connection (no error == healthy pool).
    assert isinstance(list(cp.list(cfg)), list)


@pytest.mark.skipif(not _postgres_reachable(), reason="Postgres not reachable")
def test_checkpoint_recovers_across_a_fresh_checkpointer():
    # Durability across a process/connection boundary (#224): write a checkpoint
    # with one checkpointer/pool, then read it back through a SEPARATE checkpointer
    # (new pool) — simulating a process restart resuming a parked run.
    from src.graph import build_graph

    run_id = "test-cp-recovery"
    cfg = {"configurable": {"thread_id": run_id}}

    cp_write = get_checkpointer(use_memory=False)
    build_graph(checkpointer=cp_write).invoke(initial_state(run_id=run_id), config=cfg)

    cp_read = get_checkpointer(use_memory=False)  # fresh pool / different connections
    recovered = build_graph(checkpointer=cp_read).get_state(cfg)
    assert recovered.values.get("run_id") == run_id
    assert recovered.next  # still parked at the Gate 1 interrupt
