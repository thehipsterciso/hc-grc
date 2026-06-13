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


_VALID_DECISIONS = {"approved", "rejected", "deferred"}
# Only 'approved' is terminal — it stops the gate re-firing on re-entry (don't
# re-unlock). 'rejected' routes back for re-review and 'deferred' parks the run for
# the operator to re-trigger later; BOTH must re-fire the interrupt when the gate
# is re-entered, so neither is terminal (pass-3 #5).
_TERMINAL_DECISIONS = {"approved"}


def _parse_operator_response(resp: Any, gate_id: str) -> tuple[str, str]:
    """
    Validate the operator's interrupt() response and return (decision, rationale).

    A malformed response must NOT be silently coerced to 'rejected' (that would
    let a non-dict or a typo'd decision masquerade as a real governance decision,
    #163/#180). Fail loud so the operator re-submits a well-formed response on the
    next resume.
    """
    if not isinstance(resp, dict):
        raise ValueError(
            f"{gate_id}: operator response must be a dict like "
            f"{{'decision': 'approved'|'rejected'|'deferred', 'rationale': '...'}}, "
            f"got {type(resp).__name__}."
        )
    decision = resp.get("decision")
    if decision not in _VALID_DECISIONS:
        raise ValueError(
            f"{gate_id}: operator response 'decision' must be one of "
            f"{sorted(_VALID_DECISIONS)}, got {decision!r}."
        )
    rationale = resp.get("rationale") or "No rationale provided."
    return decision, rationale


def _already_decided(state: HCGRCState, gate_id: str) -> bool:
    """
    True if this gate already holds a TERMINAL decision (approved only).

    Guards against a re-invocation re-firing the interrupt and re-running
    downstream effects on top of a terminal decision (#177). A 'rejected' record
    is deliberately NOT terminal: the Gate-2 reject → revise → re-review loop
    (route_after_gate_2 → exploratory → … → gate_2) must re-fire the interrupt so
    the operator is re-prompted, otherwise the gate short-circuits to {} and the
    graph spins until GraphRecursionError (pass-2 #184/#187). The loop-back path
    is responsible for producing the revised state that warrants re-review.
    """
    record = state.get("gate_status", {}).get(gate_id)
    return bool(record) and record.get("decision") in _TERMINAL_DECISIONS


def _finalize_gate(state: HCGRCState, gate_id: str, decision: str,
                   rationale: str, reviewer: str = "operator") -> dict[str, Any]:
    """Build the gate node's state update: failure event (if not approved) + the
    authoritative gate_status record (written only by gate_coordinator_node)."""
    update: dict[str, Any] = {}
    if decision == "rejected":
        # 'deferred' is a park, not a failure — only a rejection is a failure_event
        # (a deferred decision recorded as a rejection mislabels the audit trail).
        update["failure_events"] = [_rejection_event(gate_id, rationale, state["run_id"])]
    from .gate_coordinator import gate_coordinator_node
    update.update(gate_coordinator_node(state, gate_id, decision, rationale, reviewer=reviewer))
    return update


def _run_gate(state: HCGRCState, gate_id: str, proposal: dict[str, Any]) -> dict[str, Any]:
    """
    Drive one gate: idempotency guard, then interrupt() the operator and finalize.

    Validation runs INSIDE a re-prompt loop (pass-3 #3): interrupt() consumes and
    persists the resume value before validation, so raising on a malformed value
    would strand it in the checkpoint and replay it forever. Instead, a malformed
    or mis-correlated response re-fires a fresh interrupt (next resume index)
    carrying the error, so the operator can re-submit and actually recover.

    Gate-id correlation (pass-3 #4): if the operator response names a gate, it must
    match this gate — a stale/misrouted decision cannot be applied to the wrong gate.
    """
    if _already_decided(state, gate_id):
        return {}
    current = proposal
    while True:
        resp = interrupt(current)
        if isinstance(resp, dict) and resp.get("gate_id") not in (None, gate_id):
            current = {**proposal, "error": (
                f"response gate_id {resp.get('gate_id')!r} does not match {gate_id}")}
            continue
        try:
            decision, rationale = _parse_operator_response(resp, gate_id)
        except ValueError as exc:
            current = {**proposal, "error": str(exc)}
            continue
        return _finalize_gate(state, gate_id, decision, rationale)


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
        # ── Preregistration Ledger entries (logged before Phase 1 data ingestion) ──
        "LEDGER-0002: Diversity anchor model candidates logged (T-01 — 3 general + 2 anchors)",
        "LEDGER-0003: Fleiss kappa path selection logged (path 1: recruit raters | path 2: acknowledge unestimated)",
        # ── NOTE: DIVERGENCE-01 is a Gate 2 prerequisite, NOT Gate 1 ──────────────
        # DIVERGENCE-01 (operationalization of model-STRM divergence) requires the
        # STRM label distribution from EDA — which has not run yet at Gate 1.
        # Decision framework is defined in SAP §10. Specific operationalization is
        # selected post-EDA, logged to Preregistration Ledger before Gate 2.
        # Confirmed: SAP §10 DIVERGENCE-01 decision framework understood and acknowledged",
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
    return _run_gate(state, "gate_1", proposal)


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
    # Verify hard prerequisites before surfacing this irreversible gate. Gate 2
    # unlocks the test split, so the machine-checkable preconditions for a sound
    # exploratory→confirmatory transition are ALL enforced here, not just the data
    # split (pass-3 #1): exploratory analysis must be complete and a non-empty
    # pre-registered hypothesis set must exist before the operator can even be asked.
    hard_failures = []
    if not state.get("data_split_verified"):
        hard_failures.append("data_split_verified is False — run compute_data_split() first")
    if not state.get("exploratory_complete"):
        hard_failures.append(
            "exploratory_complete is False — P1-P5 exploratory analysis has not finished")
    if not state.get("hypothesis_set"):
        hard_failures.append(
            "hypothesis_set is empty — no pre-registered hypotheses to lock at Gate 2")

    if hard_failures:
        # Write an authoritative gate_status record so the router and operator see
        # the failure (#164/#178). Decision is DEFERRED, not rejected: a system
        # prerequisite failure must PARK the run (route_after_gate_2 deferred→END),
        # not feed it into the operator reject→revise→re-review loop, which would
        # spin forever because re-running exploratory cannot satisfy an unmet
        # prerequisite (pass-3 #20). The operator re-triggers once prereqs are met.
        rationale = "Hard prerequisite failure: " + "; ".join(hard_failures)
        update = {
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
        from .gate_coordinator import gate_coordinator_node
        update.update(
            gate_coordinator_node(state, "gate_2", "deferred", rationale, reviewer="system")
        )
        return update

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

    return _run_gate(state, "gate_2", proposal)


# ── Gate 3 ────────────────────────────────────────────────────────────────────


def gate_3_node(state: HCGRCState) -> dict[str, Any]:
    """
    Gate 3 — EDA findings review before confirmatory phase begins.

    Fires after HypothesisFormalizerAgent completes. The operator reviews
    P1-P5 exploratory outputs and the formalized hypothesis set before any
    confirmatory test runs. Approving this gate:
      - Unlocks the test split (in addition to Gate 2 — DataStewardAgent
        requires BOTH gate_2 AND gate_3 approved before test split access)
      - Confirms that DIVERGENCE-01 operationalization is final
      - Confirms the hypothesis set is complete for pre-registration

    Hard prerequisite: exploratory_complete must be True (or all agents
    in stub_pending status is acceptable for a governance dry-run).
    """
    checklist = [
        # ── P1-P5 artifact presence ────────────────────────────────────────────
        "P1 (STRM NLP): EXP_P1_similarity.parquet and EXP_P1_disagreements.md present and reviewed",
        "P1: Model F1 scores on STRM classification recorded for all 5 LEDGER-0002 candidates",
        "P2 (Control Topology): EXP_P2_graph.graphml, topology.parquet, communities.parquet reviewed",
        "P2: NIST cluster constraint verified — NIST 800-53, CSF, 800-171 treated as ONE "
        "evidence source (not 3 independent NIST findings)",
        "P3 (Regulatory Convergence): EXP_P3_convergence.parquet and atlas.json reviewed — "
        "ConvergenceType distribution examined",
        "P4 (Risk Blindspot): EXP_P4_blindspots.json reviewed — false coverage cases "
        "excluded (controls without STRM mappings excluded from blindspot claims)",
        "P5 (AI Governance): EXP_P5_taxonomy_comparison.md reviewed — UMAP parameters "
        "confirmed consistent with SAP pre-registration",
        # ── Model designation ──────────────────────────────────────────────────
        "Primary embedding model designated from LEDGER-0002 candidates based on Phase 1 F1 scores",
        "Primary model designation and all secondary/sensitivity models logged to "
        "Preregistration Ledger before this gate approves",
        "If best model F1 < 0.70: domain fine-tuning triggered via Team 06 and approved "
        "before proceeding — do not approve Gate 3 with an F1 below threshold",
        # ── SAP lock prerequisites ─────────────────────────────────────────────
        "DIVERGENCE-01 operationalization finalized and logged to Preregistration Ledger — "
        "this decision requires STRM label distribution from EDA (now available)",
        "Hypothesis set reviewed — all H[module].[n] IDs assigned with null hypothesis, "
        "named test, effect size threshold, and decision rule",
        "Effect size thresholds are grounded in domain literature — not selected to "
        "match the EDA distribution (that would be HARKing)",
        "HARKing check: no hypothesis was added to the set after P1-P5 outputs were reviewed "
        "unless it was pre-specified in methods scaffolding",
        # ── Test split integrity ───────────────────────────────────────────────
        "No analysis agent has received test split paths — all EDA artifacts reference "
        "train/val splits only. Test split data_steward access log shows zero test reads",
        "Data split seed hash unchanged since Gate 2",
        # ── License compliance ─────────────────────────────────────────────────
        "No SCF-derived embeddings, derived datasets, or analysis results have left the machine",
    ]

    proposal = _build_gate_proposal(
        gate_id="gate_3",
        title="Gate 3 — EDA Findings Review",
        summary=(
            "Exploratory analysis is complete. P1-P5 have produced their EXP_ artifact sets. "
            "Hypotheses are formalized. Approving this gate unlocks the test split and "
            "confirms the hypothesis set for pre-registration. "
            "This is the last human checkpoint before any confirmatory tests run."
        ),
        checklist=checklist,
        run_id=state["run_id"],
    )

    return _run_gate(state, "gate_3", proposal)


# ── Gate 4 ────────────────────────────────────────────────────────────────────


def gate_4_node(state: HCGRCState) -> dict[str, Any]:
    """
    Gate 4 — Confirmatory results review before reporting begins.

    Fires after all confirmatory analyses complete (P1-P5 confirmatory runs +
    StatisticalAnalystAgent). The operator reviews statistical results before
    any output enters the reporting or dissemination pipeline.

    Approving this gate:
      - Authorizes Repo Documentation Agent to write executive-mode finding summaries
      - Triggers the Branding Compliance Agent review for any executive content
      - Unlocks the Reporter Agent to begin manuscript preparation

    This gate prevents premature disclosure of unreviewed statistical results.
    """
    checklist = [
        # ── Confirmatory analysis completeness ────────────────────────────────
        "All pre-registered H[module].[n] hypotheses have decision records: "
        "'reject null' or 'fail to reject null' — no hypothesis left undecided",
        "StatisticalAnalystAgent has produced ConfirmatoryResult records for all hypotheses — "
        "p_value, effect_size, ci_lower, ci_upper, n_obs, corrected_p_value present",
        # ── Statistical rigor ─────────────────────────────────────────────────
        "Multiple comparison correction applied per SAP Section 6 — corrected_p_value "
        "values present and correction method matches SAP specification",
        "Effect sizes with confidence intervals reported for all significant findings",
        "Pre-specified sensitivity analyses complete and results recorded",
        "No post-hoc test additions — all tests match the pre-registered SAP exactly. "
        "Any deviation is a SAP amendment requiring separate LEDGER entry",
        # ── Null result integrity ──────────────────────────────────────────────
        "Null results documented with same level of detail as significant results — "
        "failing to reject null is a finding, not a non-finding",
        "Selective reporting check: number of decision records == number of "
        "pre-registered hypotheses (no cherry-picking)",
        # ── Methodological constraints ─────────────────────────────────────────
        "NIST cluster constraint respected in all findings — NIST 800-53, CSF, "
        "800-171 share one authorship source (not counted as independent validation)",
        "STRM reliability limitation disclosed in all finding summaries — "
        "per LEDGER-0003 (Path 2): interpretation pathway 'annotator inconsistency' "
        "is UNAVAILABLE; only 'quantified divergence exists' interpretation is available",
        "DIVERGENCE-01 operationalization matches the version logged to Preregistration Ledger",
        # ── Data and license compliance ────────────────────────────────────────
        "No SCF-derived data in any external-facing artifact (CC BY-ND 4.0)",
        "All statistical outputs reference data/splits/test/ DVC hash — "
        "confirms correct test set was used (seed_hash unchanged from Gate 2)",
        # ── Documentation triggers ─────────────────────────────────────────────
        "Orchestrator has triggered Repo Documentation Agent for finding documentation "
        "and executive summary preparation",
        "Branding Compliance Agent review queued for any executive-mode content",
    ]

    proposal = _build_gate_proposal(
        gate_id="gate_4",
        title="Gate 4 — Confirmatory Results Review",
        summary=(
            "Confirmatory analysis is complete. All pre-registered hypotheses have decisions. "
            "Statistical results are ready for operator review before entering the reporting pipeline. "
            "Approving this gate authorizes executive-mode documentation and manuscript preparation."
        ),
        checklist=checklist,
        run_id=state["run_id"],
    )

    return _run_gate(state, "gate_4", proposal)


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
    return _run_gate(state, "gate_5", proposal)
