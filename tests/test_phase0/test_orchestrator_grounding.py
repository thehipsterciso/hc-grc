"""
Tests for T-00 run-start grounding through the reasoning_client (ADR-0016).

The agency contract: the orchestrator reasons about the run *inside the graph*
via the reasoning_client, and the graph never depends on a live model to advance.

Two paths are covered:
  1. Graceful degradation — when the reasoning backend is unavailable, the node
     records run_grounding=None, marks the provenance record grounded=False, and
     the run still proceeds to Gate 1. (Default suite path; HCGRC_DISABLE_REASONING.)
  2. Live grounding — when the Tier 2 backend is actually up, the node produces
     real text and marks grounded=True. (Skipped if no backend is reachable.)
"""

from __future__ import annotations

import pytest

from src.nodes.orchestrator import _ORCHESTRATOR_TIER, t00_orchestrator_node
from src.reasoning_client import is_available
from src.state import initial_state


def _t00_prov(update: dict) -> dict:
    records = [p for p in update["prov_activities"] if p["activity"] == "t00_orchestration"]
    assert len(records) == 1
    return records[0]


def test_grounding_degrades_gracefully_when_backend_disabled(monkeypatch):
    """With reasoning disabled, the node must not raise and must advance the run."""
    monkeypatch.setenv("HCGRC_DISABLE_REASONING", "1")
    state = initial_state(run_id="grounding-degrade-001")

    update = t00_orchestrator_node(state)

    assert update["run_grounding"] is None
    prov = _t00_prov(update)
    assert prov["grounded"] is False
    assert prov["tier"] == _ORCHESTRATOR_TIER.value
    assert "unavailable" in prov["note"]


def test_grounding_records_phase(monkeypatch):
    """The provenance record carries the run's phase regardless of backend state."""
    monkeypatch.setenv("HCGRC_DISABLE_REASONING", "1")
    state = initial_state(run_id="grounding-phase-001")

    prov = _t00_prov(t00_orchestrator_node(state))

    assert prov["phase"] == "phase_0"
    assert prov["run_id"] == "grounding-phase-001"


def test_grounding_live_when_backend_available(monkeypatch):
    """When a real Tier 2 backend is reachable, the node produces grounding text."""
    monkeypatch.delenv("HCGRC_DISABLE_REASONING", raising=False)
    if not is_available(_ORCHESTRATOR_TIER):
        pytest.skip("Tier 2 reasoning backend not reachable in this environment")

    state = initial_state(run_id="grounding-live-001")
    update = t00_orchestrator_node(state)

    assert isinstance(update["run_grounding"], str)
    assert update["run_grounding"].strip()
    prov = _t00_prov(update)
    assert prov["grounded"] is True
