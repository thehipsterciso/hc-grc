"""
bench_checkpointer.py — PostgresSaver throughput benchmark.

Phase 0 deliverable #4: measure write/read throughput on target hardware.
Results are logged to MLflow for cross-run comparison.

Run with:
    python -m pytest tests/benchmarks/bench_checkpointer.py -v -s
    -- or --
    python tests/benchmarks/bench_checkpointer.py

Prerequisites:
    - PostgreSQL running on localhost:5432/hcgrc
    - HCGRC_POSTGRES_URL env var (optional, defaults to localhost)

If Postgres is not available, the benchmark falls back to MemorySaver
and logs a warning. MemorySaver results are not representative of
production performance.
"""

from __future__ import annotations

import time
import uuid
import warnings
from typing import Any

import pytest

from src.checkpointer import get_checkpointer
from src.graph import build_graph
from src.state import initial_state


# ── Benchmark parameters ──────────────────────────────────────────────────────

N_WRITES = 50      # Number of checkpoint writes to benchmark
N_READS = 50       # Number of checkpoint reads to benchmark
WRITE_THRESHOLD_MS = 100  # Each write should complete < 100ms on target hardware
READ_THRESHOLD_MS = 50    # Each read should complete < 50ms on target hardware


# ── Benchmark helpers ─────────────────────────────────────────────────────────

def _synthetic_checkpoint_state(run_id: str) -> dict[str, Any]:
    """Build a synthetic state payload similar to a real platform state."""
    return {
        "run_id": run_id,
        "thread_id": run_id,
        "phase": "phase_0",
        "gate_status": {},
        "failure_events": [],
        "hypotheses": [{"id": f"H1.{i}", "text": f"Synthetic hypothesis {i}"} for i in range(10)],
        "findings": [],
        "data_split_manifest_hash": None,
        "data_split_seed": 42,
        "data_split_verified": True,
        "escalation_issue_number": None,
        "escalation_reason": None,
        "messages": [],
        "prov_activities": [
            {"activity": "synthetic", "run_id": run_id, "seq": i}
            for i in range(20)
        ],
    }


def run_benchmark(use_memory: bool = False) -> dict[str, Any]:
    """
    Execute the checkpointer benchmark and return timing results.

    Args:
        use_memory: If True, use MemorySaver (no Postgres needed).
    """
    checkpointer = get_checkpointer(use_memory=use_memory)
    backend = "MemorySaver" if use_memory else "PostgresSaver"

    write_times_ms = []
    read_times_ms = []

    for i in range(N_WRITES):
        run_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": run_id}}
        state = _synthetic_checkpoint_state(run_id)

        # Write benchmark
        t0 = time.perf_counter()
        checkpointer.put(
            config,
            checkpoint={
                "v": 1,
                "id": run_id,
                "ts": str(time.time()),
                "channel_values": state,
                "channel_versions": {},
                "versions_seen": {},
                "pending_sends": [],
            },
            metadata={"source": "benchmark", "step": i},
            new_versions={},
        )
        write_times_ms.append((time.perf_counter() - t0) * 1000)

    # Read benchmark (re-read the same checkpoints)
    for i in range(min(N_READS, N_WRITES)):
        run_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": run_id}}

        t0 = time.perf_counter()
        _ = checkpointer.get(config)
        read_times_ms.append((time.perf_counter() - t0) * 1000)

    results = {
        "backend": backend,
        "n_writes": N_WRITES,
        "n_reads": N_READS,
        "write_p50_ms": sorted(write_times_ms)[len(write_times_ms) // 2],
        "write_p95_ms": sorted(write_times_ms)[int(len(write_times_ms) * 0.95)],
        "write_max_ms": max(write_times_ms),
        "read_p50_ms": sorted(read_times_ms)[len(read_times_ms) // 2],
        "read_p95_ms": sorted(read_times_ms)[int(len(read_times_ms) * 0.95)],
        "read_max_ms": max(read_times_ms),
        "write_threshold_ms": WRITE_THRESHOLD_MS,
        "read_threshold_ms": READ_THRESHOLD_MS,
        "write_threshold_passed": all(t < WRITE_THRESHOLD_MS for t in write_times_ms),
        "read_threshold_passed": all(t < READ_THRESHOLD_MS for t in read_times_ms),
    }

    return results


# ── MLflow logging ────────────────────────────────────────────────────────────

def log_to_mlflow(results: dict[str, Any]) -> None:
    """Log benchmark results to MLflow (local tracking, no SaaS)."""
    try:
        import mlflow
        with mlflow.start_run(run_name=f"checkpointer_benchmark_{results['backend']}"):
            mlflow.log_params({
                "backend": results["backend"],
                "n_writes": results["n_writes"],
                "n_reads": results["n_reads"],
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
        """MemorySaver benchmark — always runs, no Postgres required."""
        results = run_benchmark(use_memory=True)
        print(f"\nMemorySaver benchmark: write p50={results['write_p50_ms']:.2f}ms, "
              f"read p50={results['read_p50_ms']:.2f}ms")
        # MemorySaver should be very fast
        assert results["write_p50_ms"] < 10, "MemorySaver write p50 should be < 10ms"
        assert results["read_p50_ms"] < 10, "MemorySaver read p50 should be < 10ms"

    @pytest.mark.skipif(
        not __import__("os").environ.get("HCGRC_POSTGRES_URL")
        and not __import__("shutil").which("psql"),
        reason="PostgreSQL not available — set HCGRC_POSTGRES_URL to run",
    )
    def test_postgres_saver_benchmark(self):
        """PostgresSaver benchmark — requires Postgres on localhost."""
        results = run_benchmark(use_memory=False)
        log_to_mlflow(results)
        print(f"\nPostgresSaver benchmark: write p50={results['write_p50_ms']:.2f}ms "
              f"(threshold: {WRITE_THRESHOLD_MS}ms), "
              f"read p50={results['read_p50_ms']:.2f}ms "
              f"(threshold: {READ_THRESHOLD_MS}ms)")
        assert results["write_p95_ms"] < WRITE_THRESHOLD_MS, (
            f"Write p95 {results['write_p95_ms']:.1f}ms exceeds threshold {WRITE_THRESHOLD_MS}ms"
        )
        assert results["read_p95_ms"] < READ_THRESHOLD_MS, (
            f"Read p95 {results['read_p95_ms']:.1f}ms exceeds threshold {READ_THRESHOLD_MS}ms"
        )


# ── Standalone runner ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Running MemorySaver benchmark...")
    mem_results = run_benchmark(use_memory=True)
    print(f"  Write: p50={mem_results['write_p50_ms']:.2f}ms, "
          f"p95={mem_results['write_p95_ms']:.2f}ms, max={mem_results['write_max_ms']:.2f}ms")
    print(f"  Read:  p50={mem_results['read_p50_ms']:.2f}ms, "
          f"p95={mem_results['read_p95_ms']:.2f}ms, max={mem_results['read_max_ms']:.2f}ms")

    try:
        print("\nRunning PostgresSaver benchmark...")
        pg_results = run_benchmark(use_memory=False)
        log_to_mlflow(pg_results)
        print(f"  Write: p50={pg_results['write_p50_ms']:.2f}ms, "
              f"p95={pg_results['write_p95_ms']:.2f}ms (threshold: {WRITE_THRESHOLD_MS}ms)")
        print(f"  Read:  p50={pg_results['read_p50_ms']:.2f}ms, "
              f"p95={pg_results['read_p95_ms']:.2f}ms (threshold: {READ_THRESHOLD_MS}ms)")
        passed = pg_results["write_threshold_passed"] and pg_results["read_threshold_passed"]
        print(f"  Threshold check: {'PASSED' if passed else 'FAILED'}")
    except Exception as e:
        print(f"  PostgresSaver unavailable: {e}")
        print("  Set HCGRC_POSTGRES_URL or start Postgres to run this benchmark.")
