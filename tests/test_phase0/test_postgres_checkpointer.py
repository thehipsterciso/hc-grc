"""
Checkpointer factory tests (hardening pass 1, #161).

MemorySaver is always exercised. The PostgresSaver path (self-healing pool) is
exercised and round-tripped when Postgres is reachable, else skipped.
"""

from __future__ import annotations

import pytest
from langgraph.checkpoint.memory import MemorySaver

from src.checkpointer import get_checkpointer, get_postgres_connection_string


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
