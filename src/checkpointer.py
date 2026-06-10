"""
PostgresSaver configuration for HC-GRC.

LangGraph uses the checkpointer to persist graph state between turns,
enabling interrupt/resume across the operator approval gates.

Per ADR-0015 (#79): run_id propagates to PostgresSaver as thread_id.
Cross-store query procedure in RUNBOOK.md §5.

LOCAL-FIRST CONSTRAINT: PostgreSQL instance runs on-device.
No state leaves the machine. SaaS checkpointers are disqualified.

Connection config:
  Database: hcgrc
  Host: localhost (default)
  Port: 5432 (default)

For Phase 0 testing: use MemorySaver (no Postgres required).
For Phase 1+: use PostgresSaver with the connection string below.
"""

from __future__ import annotations

import os

from langgraph.checkpoint.memory import MemorySaver


# ── Connection string ─────────────────────────────────────────────────────────

def get_postgres_connection_string() -> str:
    """
    Return the PostgreSQL connection string.
    Reads from HCGRC_POSTGRES_URL env var or falls back to localhost default.
    Never logged, never committed.
    """
    return os.environ.get(
        "HCGRC_POSTGRES_URL",
        "postgresql://localhost:5432/hcgrc",
    )


# ── Checkpointer factory ──────────────────────────────────────────────────────

def get_checkpointer(use_memory: bool = False):
    """
    Return a configured checkpointer.

    Args:
        use_memory: If True, return MemorySaver (Phase 0 testing, no Postgres needed).
                    If False, return PostgresSaver (Phase 1+ production).

    Returns:
        MemorySaver | PostgresSaver
    """
    if use_memory:
        return MemorySaver()

    try:
        from langgraph.checkpoint.postgres import PostgresSaver
        conn_str = get_postgres_connection_string()
        checkpointer = PostgresSaver.from_conn_string(conn_str)
        checkpointer.setup()  # creates tables if they don't exist
        return checkpointer
    except ImportError:
        raise ImportError(
            "langgraph-checkpoint-postgres is required for PostgresSaver. "
            "Run: pip install langgraph-checkpoint-postgres"
        )
    except Exception as e:
        raise RuntimeError(
            f"PostgresSaver connection failed. Is Postgres running on localhost:5432/hcgrc? "
            f"Error: {e}\n"
            "For Phase 0 testing without Postgres, use get_checkpointer(use_memory=True)."
        ) from e
