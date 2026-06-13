"""
bench_checkpointer.py — PostgresSaver throughput benchmark.

Phase 0 deliverable #4: measure checkpoint write/read throughput on target hardware.
Uses the graph's public API (.invoke, .get_state) — NOT the internal checkpointer.put()
API, which is unstable across LangGraph minor versions.

Results are logged to MLflow (local tracking, no SaaS).

Run with:
    python -m pytest tests/benchmarks/bench_checkpointer.py -v -s
    -- or --
    python tests/benchmarks/bench_checkpointer.py

Prerequisites (PostgresSaver path):
    - PostgreSQL running on localhost:5432/hcgrc
    - HCGRC_POSTGRES_URL env var (optional, defaults to localhost)

If Postgres is not available, the PostgresSaver benchmark is skipped (pytest) or
reports "unavailable" (standalone runner); the MemorySaver baseline always runs.
MemorySaver results are not representative of production throughput.
"""

from __future__ import annotations

import math
import time
import uuid
import warnings
from typing import Any

import pytest

from src.checkpointer import get_checkpointer
from src.graph import build_graph
from src.state import initial_state


def _percentile(sorted_vals: list[float], pct: float) -> float:
    """Nearest-rank percentile. Fixes the off-by-one that made p95 == max (#211)."""
    if not sorted_vals:
        return 0.0
    rank = max(1, math.ceil(pct / 100.0 * len(sorted_vals)))
    return sorted_vals[min(rank, len(sorted_vals)) - 1]


# ── Benchmark parameters ──────────────────────────────────────────────────────

N_RUNS = 20            # Number of graph runs (each = one write + one read cycle)
WRITE_THRESHOLD_MS = 150  # Each checkpoint write < 150ms on target hardware
READ_THRESHOLD_MS = 75    # Each state read < 75ms on target hardware


# ── Benchmark core ────────────────────────────────────────────────────────────

def run_benchmark(use_memory: bool = False) -> dict[str, Any]:
    """
    Execute the checkpointer benchmark via the graph's public API.

    Each iteration:
      1. Invokes the graph up to the Gate 1 interrupt (triggers a checkpoint write)
      2. Reads the state snapshot back (exercises the checkpoint read path)

    Timing is wall-clock around each step.
    """
    checkpointer = get_checkpointer(use_memory=use_memory)
    backend = "MemorySaver" if use_memory else "PostgresSaver"
    graph = build_graph(checkpointer=checkpointer)

    write_times_ms: list[float] = []
    read_times_ms: list[float] = []

    for _ in range(N_RUNS):
        run_id = str(uuid.uuid4())
        state = initial_state(run_id=run_id)
        config = {"configurable": {"thread_id": run_id}}

        # Write: invoke graph until Gate 1 interrupt — checkpointer writes state
        t0 = time.perf_counter()
        graph.invoke(state, config=config)
        write_times_ms.append((time.perf_counter() - t0) * 1000)

        # Read: get_state reads the most recent checkpoint
        t0 = time.perf_counter()
        snapshot = graph.get_state(config)
        read_times_ms.append((time.perf_counter() - t0) * 1000)

        assert snapshot is not None, "Checkpoint read returned None"
        assert snapshot.values.get("run_id") == run_id, "run_id mismatch after checkpoint round-trip"

    write_sorted = sorted(write_times_ms)
    read_sorted = sorted(read_times_ms)

    return {
        "backend": backend,
        "n_runs": N_RUNS,
        "write_p50_ms": _percentile(write_sorted, 50),
        "write_p95_ms": _percentile(write_sorted, 95),
        "write_max_ms": max(write_times_ms),
        "read_p50_ms": _percentile(read_sorted, 50),
        "read_p95_ms": _percentile(read_sorted, 95),
        "read_max_ms": max(read_times_ms),
        "write_threshold_ms": WRITE_THRESHOLD_MS,
        "read_threshold_ms": READ_THRESHOLD_MS,
        "write_threshold_passed": all(t < WRITE_THRESHOLD_MS for t in write_times_ms),
        "read_threshold_passed": all(t < READ_THRESHOLD_MS for t in read_times_ms),
    }


# ── MLflow logging ────────────────────────────────────────────────────────────

def log_to_mlflow(results: dict[str, Any]) -> None:
    """Log benchmark results to MLflow (local tracking server, no SaaS)."""
    try:
        import mlflow
        with mlflow.start_run(run_name=f"checkpointer_benchmark_{results['backend']}"):
            mlflow.log_params({
                "backend": results["backend"],
                "n_runs": results["n_runs"],
                "write_threshold_ms": results["write_threshold_ms"],
                "read_threshold_ms": results["read_threshold_ms"],
            })
            mlflow.log_metrics({
                "write_p50_ms": results["write_p50_ms"],
                "write_p95_ms": results["write_p95_ms"],
                "write_max_ms": results["write_max_ms"],
                "read_p50_ms": results["read_p50_ms"],
                "read_p95_ms": results["read_p95_ms"],
                "read_max_ms": results["read_max_ms"],
            })
    except Exception as e:
        warnings.warn(f"MLflow logging failed (non-critical): {e}")


# ── pytest integration ────────────────────────────────────────────────────────

@pytest.mark.benchmark
class TestCheckpointerBenchmark:
    """Phase 0 checkpointer throughput benchmark (pytest entry point)."""

    def test_memory_saver_benchmark(self):
        """MemorySaver baseline — always runs, no Postgres required."""
        results = run_benchmark(use_memory=True)
        print(f"\nMemorySaver: write p50={results['write_p50_ms']:.1f}ms  "
              f"read p50={results['read_p50_ms']:.1f}ms")
        assert results["write_p50_ms"] < 500, (
            f"MemorySaver write p50 {results['write_p50_ms']:.0f}ms unexpectedly slow — "
            "check for regressions in graph compilation"
        )

    @pytest.mark.skipif(
        not __import__("os").environ.get("HCGRC_POSTGRES_URL")
        and not __import__("shutil").which("psql"),
        reason="PostgreSQL not available — set HCGRC_POSTGRES_URL to run",
    )
    def test_postgres_saver_benchmark(self):
        """PostgresSaver benchmark — requires Postgres on localhost."""
        results = run_benchmark(use_memory=False)
        log_to_mlflow(results)
        print(f"\nPostgresSaver: write p50={results['write_p50_ms']:.1f}ms "
              f"(threshold: {WRITE_THRESHOLD_MS}ms)  "
              f"read p50={results['read_p50_ms']:.1f}ms "
              f"(threshold: {READ_THRESHOLD_MS}ms)")
        assert results["write_p95_ms"] < WRITE_THRESHOLD_MS, (
            f"Write p95 {results['write_p95_ms']:.1f}ms exceeds {WRITE_THRESHOLD_MS}ms"
        )
        assert results["read_p95_ms"] < READ_THRESHOLD_MS, (
            f"Read p95 {results['read_p95_ms']:.1f}ms exceeds {READ_THRESHOLD_MS}ms"
        )


# ── Standalone runner ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Running MemorySaver benchmark ({N_RUNS} runs)...")
    mem = run_benchmark(use_memory=True)
    print(f"  Write: p50={mem['write_p50_ms']:.1f}ms  p95={mem['write_p95_ms']:.1f}ms  "
          f"max={mem['write_max_ms']:.1f}ms")
    print(f"  Read:  p50={mem['read_p50_ms']:.1f}ms  p95={mem['read_p95_ms']:.1f}ms  "
          f"max={mem['read_max_ms']:.1f}ms")

    try:
        print(f"\nRunning PostgresSaver benchmark ({N_RUNS} runs)...")
        pg = run_benchmark(use_memory=False)
        log_to_mlflow(pg)
        print(f"  Write: p50={pg['write_p50_ms']:.1f}ms  p95={pg['write_p95_ms']:.1f}ms  "
              f"(threshold: {WRITE_THRESHOLD_MS}ms) — "
              f"{'PASSED' if pg['write_threshold_passed'] else 'FAILED'}")
        print(f"  Read:  p50={pg['read_p50_ms']:.1f}ms  p95={pg['read_p95_ms']:.1f}ms  "
              f"(threshold: {READ_THRESHOLD_MS}ms) — "
              f"{'PASSED' if pg['read_threshold_passed'] else 'FAILED'}")
    except Exception as e:
        print(f"  PostgresSaver unavailable: {e}")
        print("  Set HCGRC_POSTGRES_URL or start Postgres to run.")
