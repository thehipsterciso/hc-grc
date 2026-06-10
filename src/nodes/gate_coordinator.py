"""
GateCoordinatorNode — serialized writer of gate_status in HCGRCState.

Per ADR-0015 (#75): all writes to gate_status go through this node.
No other node writes gate_status directly. This is the only point where
gate decisions are recorded, preventing concurrent write races when multiple
agents are running in the same LangGraph thread.

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

    updated_gate_status = dict(state.get("gate_status", {}))
    updated_gate_status[gate_id] = record

    return {"gate_status": updated_gate_status}
