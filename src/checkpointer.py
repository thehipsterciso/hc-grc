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

import atexit
import os

from langgraph.checkpoint.memory import MemorySaver

# Arbitrary fixed key for the Postgres session advisory lock that serializes
# checkpoint schema migrations across concurrent initializers (get_checkpointer).
_MIGRATION_LOCK_KEY = 0x4843_4752  # "HCGR"

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
        from psycopg.rows import dict_row
        from psycopg_pool import ConnectionPool
    except ImportError as e:
        raise ImportError(
            "langgraph-checkpoint-postgres and psycopg[pool] are required for PostgresSaver. "
            "Run: pip install 'langgraph-checkpoint-postgres' 'psycopg[binary,pool]'"
        ) from e

    conn_str = get_postgres_connection_string()
    try:
        # A single raw Connection has no recovery: when the Postgres backend goes
        # away (node sleep/restart, idle timeout, network blip) the cached
        # connection is permanently broken and every subsequent checkpoint op
        # raises — silent loss of durability exactly during interrupt/resume across
        # the approval gates. Use a self-healing ConnectionPool instead: it runs a
        # liveness check on checkout and discards/replaces dead connections.
        # PostgresSaver natively accepts a ConnectionPool. (Hardening pass 1, #4.)
        pool = ConnectionPool(
            conn_str,
            min_size=1,
            max_size=8,
            kwargs={
                "autocommit": True,
                "prepare_threshold": 0,
                "row_factory": dict_row,
            },
            check=ConnectionPool.check_connection,
            open=True,
        )
        # PostgresSaver does not own the pool, so close it cleanly at process exit
        # (otherwise the pool's worker thread cannot be joined during interpreter
        # finalization, raising a noisy PythonFinalizationError).
        atexit.register(pool.close)
        checkpointer = PostgresSaver(pool)

        # Serialize schema migrations across processes with a session advisory
        # lock so concurrent initializers don't race on checkpoint_migrations
        # (Hardening pass 1, #33).
        with pool.connection() as conn:
            conn.execute("SELECT pg_advisory_lock(%s)", (_MIGRATION_LOCK_KEY,))
            try:
                checkpointer.setup()  # creates checkpoint tables if they don't exist
            finally:
                conn.execute("SELECT pg_advisory_unlock(%s)", (_MIGRATION_LOCK_KEY,))
        return checkpointer
    except Exception as e:
        raise RuntimeError(
            f"PostgresSaver connection failed. Is Postgres running on {conn_str}? "
            f"Error: {e}\n"
            "For Phase 0 testing without Postgres, use get_checkpointer(use_memory=True)."
        ) from e
