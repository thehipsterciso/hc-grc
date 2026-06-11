"""
gate_coordinator_node — single write path for gate_status in HCGRCState.

Per ADR-0015 (#74, corrected 2026-06-11): all writes to gate_status go through
this function. No other node writes gate_status directly.

Phase 0 safety mechanism: gate_status has a merge reducer
  Annotated[dict[GateID, GateStatus], lambda a, b: {**a, **b}]
This function returns only the new {gate_id: record} entry; LangGraph merges it
into the existing dict. Safe because each gate writes a unique gate_id key.

Note: this is a helper function, not a standalone LangGraph node in Phase 0.
Phase 1 will promote it to a true serialized node to handle parallel topology.
See GitHub issue #103.

The coordinator does not evaluate gate criteria — that is each gate node's
responsibility. The coordinator only persists the decision handed to it.
"""

from __future__ import annotations

import datetime
from typing import Any

from ..state import GateDecision, GateID, GateStatus, HCGRCState


def gate_coordinator_node(state: HCGRCState, gate_id: GateID, decision: GateDecision,
                           rationale: str, reviewer: str = "operator") -> dict[str, Any]:
    """
    Write a gate decision to gate_status.

    Called by each gate node after the interrupt() resolves.
    Returns a partial state update that LangGraph merges.
    """
    record = GateStatus(
        gate_id=gate_id,
        decision=decision,
        rationale=rationale,
        reviewer=reviewer,
        timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        run_id=state["run_id"],
    )

    # gate_status has a merge reducer ({**a, **b}) — return only the new entry.
    # LangGraph merges it into the existing dict rather than replacing the whole field.
    return {"gate_status": {gate_id: record}}
