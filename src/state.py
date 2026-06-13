"""
HCGRCState — canonical LangGraph state for the HC-GRC research platform.

All nodes read from and write to this TypedDict. Fields are append-only
where possible to preserve audit history within a run.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any, Literal

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

# ── Phase labels ────────────────────────────────────────────────────────────

Phase = Literal["phase_0", "phase_1", "phase_2"]

# Gate identifiers 1–5
GateID = Literal["gate_1", "gate_2", "gate_3", "gate_4", "gate_5"]

GateDecision = Literal["pending", "approved", "rejected", "deferred"]


# ── Core state ───────────────────────────────────────────────────────────────


class GateStatus(TypedDict):
    """Written exclusively by GateCoordinatorNode to avoid concurrent writes."""

    gate_id: GateID
    decision: GateDecision
    rationale: str
    reviewer: str  # "operator" | "claude" | "synthetic"
    timestamp_utc: str  # ISO-8601
    run_id: str


class HCGRCState(TypedDict):
    """
    Canonical platform state. run_id propagates to all four stores:
      - MLflow  (tags.run_id)
      - Phoenix (trace attribute run_id)
      - PROV-DM (activity IRI contains run_id)
      - PostgresSaver (thread_id column)

    See RUNBOOK.md for cross-store query procedures.
    """

    # ── Identity ─────────────────────────────────────────────────────────────
    run_id: str  # UUID4, set at graph entry, propagated everywhere
    thread_id: str  # LangGraph thread ID (== run_id for single-run threads)
    phase: Phase

    # ── Gate tracking ────────────────────────────────────────────────────────
    # Merge reducer: {**a, **b} ensures concurrent gate writes are safe by
    # construction. gate_coordinator_node is the canonical writer, but the
    # reducer protects against any future path that returns a partial update.
    # Fixes: ADR-0015 §75 serial guarantee (F1) + silent overwrite risk (F4).
    gate_status: Annotated[dict[GateID, GateStatus], lambda a, b: {**a, **b}]

    # ── Failure events (written by gate nodes on rejection) ───────────────────
    # Agent Evolution monitors this store for routing re-optimization signals.
    failure_events: Annotated[list[dict[str, Any]], lambda a, b: a + b]

    # ── Research artifacts (append-only) ──────────────────────────────────────
    hypotheses: Annotated[list[dict[str, Any]], lambda a, b: a + b]
    findings: Annotated[list[dict[str, Any]], lambda a, b: a + b]

    # ── Data split record ─────────────────────────────────────────────────────
    # Un-reduced (last-write-wins) scalars. Written by exactly one node per phase —
    # data_split_node in Phase 0, DataStewardAgent in Phase 1 — never concurrently,
    # so last-write-wins is safe by sequencing, not by a reducer (#212). Immutable
    # after Gate 1. If these ever become concurrently written, add a reducer.
    data_split_manifest_hash: str | None  # SHA-256 of the raw manifest file
    data_split_seed: int | None  # derived from manifest hash (int.from_bytes)
    data_split_verified: bool  # True after idempotency assertion passes

    # ── Phase 1 execution tracking ────────────────────────────────────────────
    # phase_1_ready: True after data pipeline writes validated splits to disk.
    # exploratory_complete: True after all P1-P5 nodes complete (or graceful stub).
    phase_1_ready: bool
    exploratory_complete: bool

    # ── Data pipeline provenance ──────────────────────────────────────────────
    # Written by EmbeddingAgent after embedding run completes. Required at Gate 2
    # to confirm which model produced the embeddings used in exploratory analysis.
    # Keys: model_name, model_hash, corpus_dvc_hash, timestamp_utc
    embedding_manifest: dict[str, Any] | None

    # ── Exploratory analysis artifacts (append, deduped) ──────────────────────
    # eda_artifacts: file paths to all EXP_* outputs from P1-P5 nodes.
    # Each node appends its artifact paths. Gate 3 verifies all 5 agents present.
    # Deduped on merge so a Gate-2 reject → re-run-exploratory loop cannot
    # accumulate the same artifact path repeatedly (#235).
    # eda_agent_statuses: per-agent completion records.
    # Keys: agent_id, status ("completed"|"stub_pending"|"failed"), note, timestamp_utc
    eda_artifacts: Annotated[list[str], lambda a, b: a + [x for x in b if x not in a]]
    eda_agent_statuses: Annotated[list[dict[str, Any]], lambda a, b: a + b]

    # ── Formalized hypothesis set (append-only) ───────────────────────────────
    # Written by HypothesisFormalizerAgent before Gate 2.
    # Each entry is a FormalHypothesis dict (see src/agents/hypothesis_formalizer).
    hypothesis_set: Annotated[list[dict[str, Any]], lambda a, b: a + b]

    # ── Orchestrator run-start grounding ──────────────────────────────────────
    # Produced by t00_orchestrator_node via the reasoning_client (Tier 2). The
    # orchestrator reasons about the run *inside the graph* rather than the work
    # being done by hand outside the framework (ADR-0016 — the agency contract).
    # None when the reasoning backend was unavailable (graceful degradation).
    run_grounding: str | None

    # ── Escalation ────────────────────────────────────────────────────────────
    escalation_issue_number: int | None  # GitHub issue number if parked
    escalation_reason: str | None

    # ── LLM messages (for agent traces) ──────────────────────────────────────
    messages: Annotated[list, add_messages]

    # ── Provenance ────────────────────────────────────────────────────────────
    prov_activities: Annotated[list[dict[str, Any]], lambda a, b: a + b]


def initial_state(run_id: str | None = None) -> HCGRCState:
    """Return a clean initial state for a new run."""
    rid = run_id or str(uuid.uuid4())
    return HCGRCState(
        run_id=rid,
        thread_id=rid,
        phase="phase_0",
        gate_status={},
        failure_events=[],
        hypotheses=[],
        findings=[],
        data_split_manifest_hash=None,
        data_split_seed=None,
        data_split_verified=False,
        phase_1_ready=False,
        exploratory_complete=False,
        embedding_manifest=None,
        eda_artifacts=[],
        eda_agent_statuses=[],
        hypothesis_set=[],
        run_grounding=None,
        escalation_issue_number=None,
        escalation_reason=None,
        messages=[],
        prov_activities=[],
    )
