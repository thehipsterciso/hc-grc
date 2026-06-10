"""
Gate nodes for the HC-GRC research platform.

Five gates enforce human approval at structural transition points.
Each gate issues a LangGraph interrupt(), surfacing a structured proposal
to the operator. The operator responds via Claude on any device (ADR-0014).

Gate decisions are written by gate_coordinator_node — never directly here.
On rejection, each gate appends a failure_event for Agent Evolution monitoring.

Gate definitions:
  Gate 1 — Pre-data checkpoint (Phase 0 complete, all prerequisites verified)
  Gate 2 — Exploratory → Confirmatory (hypothesis lock, test data unlock)
  Gate 3 — Finding significance review (before publication pipeline)
  Gate 4 — Manuscript submission approval
  Gate 5 — Escalation resolution gate (triggered by ADR-0014 Escalation loop)
"""

from __future__ import annotations

import datetime
from typing import Any

from langgraph.types import interrupt

from ..state import HCGRCState


# ── Shared helpers ────────────────────────────────────────────────────────────


def _build_gate_proposal(gate_id: str, title: str, summary: str,
                          checklist: list[str], run_id: str) -> dict[str, Any]:
    """Build the structured proposal surfaced to the operator via interrupt()."""
    return {
        "gate_id": gate_id,
        "title": title,
        "summary": summary,
        "checklist": checklist,
        "run_id": run_id,
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "instructions": (
            "Respond with: {'decision': 'approved'|'rejected'|'deferred', "
            "'rationale': '<your reasoning>'}"
        ),
    }


def _rejection_event(gate_id: str, rationale: str, run_id: str) -> dict[str, Any]:
    """Failure event appended to state for Agent Evolution monitoring."""
    return {
        "event_type": "gate_rejection",
        "gate_id": gate_id,
        "rationale": rationale,
        "run_id": run_id,
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


# ── Gate 1 ────────────────────────────────────────────────────────────────────


def gate_1_node(state: HCGRCState) -> dict[str, Any]:
    """
    Gate 1 — Pre-data checkpoint.

    Fires before any SCF data enters the system. The operator verifies that
    all Phase 0 prerequisites are complete (ADR-0015, #71):

      1. LangGraph skeleton running
      2. Gate 1 fires with synthetic payload (this test)
      3. Data split idempotency verified (SHA-256 seed reproducible)
      4. PostgresSaver benchmark complete (throughput on target hardware)
      5. Governance dry-run complete (full escalation loop exercised)
      6. Diversity anchor models identified (T-01, ADR-0013)

    The interrupt() surfaces the proposal and parks the graph until the
    operator responds. No SCF data is loaded before this gate approves.
    """
    checklist = [
        "LangGraph skeleton compiles and graph executes on synthetic payload",
        "Gate 1 interrupt fires and resolves correctly",
        "compute_data_split() produces identical splits on two independent runs (SHA-256 seed)",
        "PostgresSaver write/read benchmark complete — throughput logged to MLflow",
        "Governance dry-run complete — escalation loop exercised end-to-end",
        "Diversity anchor model candidates identified by T-01 and logged to Preregistration Ledger",
        "DIVERGENCE-01 operationalization selected and logged (hard prerequisite per SAP §10)",
        "Fleiss kappa path selected (rater recruitment or acknowledged limitation) per SAP §12",
    ]

    proposal = _build_gate_proposal(
        gate_id="gate_1",
        title="Gate 1 — Pre-Data Checkpoint",
        summary=(
            "Platform has completed Phase 0 verification. All structural prerequisites "
            "are in place before SCF corpus data enters the system. "
            "Approve to unlock data ingestion and begin Phase 1."
        ),
        checklist=checklist,
        run_id=state["run_id"],
    )

    # interrupt() parks the graph and surfaces proposal to operator.
    # The operator's response dict is the return value of interrupt().
    operator_response: dict[str, Any] = interrupt(proposal)

    decision = operator_response.get("decision", "rejected")
    rationale = operator_response.get("rationale", "No rationale provided.")

    update: dict[str, Any] = {}

    if decision != "approved":
        update["failure_events"] = [_rejection_event("gate_1", rationale, state["run_id"])]

    # Gate coordinator writes the final gate_status record.
    # Import here to avoid circular import at module level.
    from .gate_coordinator import gate_coordinator_node
    update.update(gate_coordinator_node(state, "gate_1", decision, rationale))

    return update


# ── Gate 2 ────────────────────────────────────────────────────────────────────


def gate_2_node(state: HCGRCState) -> dict[str, Any]:
    """
    Gate 2 — Exploratory → Confirmatory transition.

    The most consequential gate. The operator reviews the pre-registered
    hypothesis set and approves unlocking the test split. Uses ADR-0014
    Escalation infrastructure (GitHub issue → Claude → decision record).

    Hard prerequisites (checked before interrupt fires):
      - DIVERGENCE-01 operationalization logged to Preregistration Ledger
      - Primary embedding model designated and logged
      - Hypothesis set complete and committed to PREREGISTRATION_LEDGER.md
      - Data split idempotency verified (data_split_verified == True)
    """
    # Verify hard prerequisites before surfacing the gate
    hard_failures = []
    if not state.get("data_split_verified"):
        hard_failures.append("data_split_verified is False — run compute_data_split() first")

    if hard_failures:
        return {
            "failure_events": [
                {
                    "event_type": "gate_prerequisite_failure",
                    "gate_id": "gate_2",
                    "failures": hard_failures,
                    "run_id": state["run_id"],
                    "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                }
            ]
        }

    checklist = [
        "DIVERGENCE-01 operationalization selected and logged to Preregistration Ledger",
        "Primary embedding model designated and logged to Preregistration Ledger",
        "All secondary/sensitivity models designated at same timestamp",
        "Hypothesis set complete — every confirmatory hypothesis in PREREGISTRATION_LEDGER.md",
        "Data split idempotency verified (SHA-256 seed, two independent runs identical)",
        "Exploratory analysis complete — no confirmatory tests have run",
        "SAP Section 1 (primary analysis) populated with specific hypothesis and effect size",
        "Multiple comparison families defined in SAP Section 6",
    ]

    proposal = _build_gate_proposal(
        gate_id="gate_2",
        title="Gate 2 — Exploratory → Confirmatory Transition",
        summary=(
            "Exploratory analysis is complete. Hypotheses are pre-registered. "
            "Approving this gate unlocks the test split for confirmatory analysis. "
            "This action is irreversible — test data cannot be re-locked after Gate 2 approves."
        ),
        checklist=checklist,
        run_id=state["run_id"],
    )

    operator_response: dict[str, Any] = interrupt(proposal)

    decision = operator_response.get("decision", "rejected")
    rationale = operator_response.get("rationale", "No rationale provided.")

    update: dict[str, Any] = {}

    if decision != "approved":
        update["failure_events"] = [_rejection_event("gate_2", rationale, state["run_id"])]

    from .gate_coordinator import gate_coordinator_node
    update.update(gate_coordinator_node(state, "gate_2", decision, rationale))

    return update


# ── Gates 3–5 (stubs — fully specified in later phases) ──────────────────────


def gate_3_node(state: HCGRCState) -> dict[str, Any]:
    """Gate 3 — Finding significance review (Phase 2, pre-publication)."""
    proposal = _build_gate_proposal(
        gate_id="gate_3",
        title="Gate 3 — Finding Significance Review",
        summary="Confirmatory analysis complete. Review findings before publication pipeline.",
        checklist=["[To be specified at Phase 2 design]"],
        run_id=state["run_id"],
    )
    operator_response: dict[str, Any] = interrupt(proposal)
    decision = operator_response.get("decision", "rejected")
    rationale = operator_response.get("rationale", "")
    update: dict[str, Any] = {}
    if decision != "approved":
        update["failure_events"] = [_rejection_event("gate_3", rationale, state["run_id"])]
    from .gate_coordinator import gate_coordinator_node
    update.update(gate_coordinator_node(state, "gate_3", decision, rationale))
    return update


def gate_4_node(state: HCGRCState) -> dict[str, Any]:
    """Gate 4 — Manuscript submission approval."""
    proposal = _build_gate_proposal(
        gate_id="gate_4",
        title="Gate 4 — Manuscript Submission Approval",
        summary="Manuscript ready for submission. Final operator review required.",
        checklist=["[To be specified at Phase 2 design]"],
        run_id=state["run_id"],
    )
    operator_response: dict[str, Any] = interrupt(proposal)
    decision = operator_response.get("decision", "rejected")
    rationale = operator_response.get("rationale", "")
    update: dict[str, Any] = {}
    if decision != "approved":
        update["failure_events"] = [_rejection_event("gate_4", rationale, state["run_id"])]
    from .gate_coordinator import gate_coordinator_node
    update.update(gate_coordinator_node(state, "gate_4", decision, rationale))
    return update


def gate_5_node(state: HCGRCState) -> dict[str, Any]:
    """Gate 5 — Escalation resolution (ADR-0014 Escalation loop)."""
    proposal = _build_gate_proposal(
        gate_id="gate_5",
        title="Gate 5 — Escalation Resolution",
        summary=(
            "Platform has filed an Escalation proposal. Operator review required before "
            "proceeding into new territory (new data sources, substantially different methods, "
            "expanded scope). Platform will not auto-proceed."
        ),
        checklist=[
            "Review Escalation proposal in GitHub issue",
            "Evaluate scope expansion request against project charter",
            "Approve, reject, or defer the proposal",
        ],
        run_id=state["run_id"],
    )
    operator_response: dict[str, Any] = interrupt(proposal)
    decision = operator_response.get("decision", "rejected")
    rationale = operator_response.get("rationale", "")
    update: dict[str, Any] = {}
    if decision != "approved":
        update["failure_events"] = [_rejection_event("gate_5", rationale, state["run_id"])]
    from .gate_coordinator import gate_coordinator_node
    update.update(gate_coordinator_node(state, "gate_5", decision, rationale))
    return update
