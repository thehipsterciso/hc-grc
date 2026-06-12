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
        from psycopg import Connection
        from psycopg.rows import dict_row
    except ImportError as e:
        raise ImportError(
            "langgraph-checkpoint-postgres and psycopg are required for PostgresSaver. "
            "Run: pip install 'langgraph-checkpoint-postgres' 'psycopg[binary,pool]'"
        ) from e

    conn_str = get_postgres_connection_string()
    try:
        # PostgresSaver.from_conn_string is a @contextmanager that closes the
        # connection on exit — unsuitable for a factory that returns a long-lived
        # saver. Open a persistent connection configured exactly as PostgresSaver
        # requires (autocommit, no prepared-statement threshold, dict rows) and
        # hand it to the saver directly. The connection lives for the process.
        conn = Connection.connect(
            conn_str,
            autocommit=True,
            prepare_threshold=0,
            row_factory=dict_row,
        )
        checkpointer = PostgresSaver(conn)
        checkpointer.setup()  # creates checkpoint tables if they don't exist
        return checkpointer
    except Exception as e:
        raise RuntimeError(
            f"PostgresSaver connection failed. Is Postgres running on {conn_str}? "
            f"Error: {e}\n"
            "For Phase 0 testing without Postgres, use get_checkpointer(use_memory=True)."
        ) from e
