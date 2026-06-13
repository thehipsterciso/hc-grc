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

from src.nodes.orchestrator import _ORCHESTRATOR_TIER, t00_orchestrator_node
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


def test_grounding_records_text_when_backend_returns(monkeypatch):
    """When the reasoning backend returns text, the node captures it as grounding.

    Deterministic and CI-runnable: the reasoning_client is stubbed (no live model,
    no double-invocation), so this exercises the node's capture/record logic on the
    success path every run, not just when Ollama happens to be up (#153)."""
    monkeypatch.delenv("HCGRC_DISABLE_REASONING", raising=False)
    captured = {}

    def fake_complete(tier, prompt, **kwargs):
        captured["tier"] = tier
        captured["kwargs"] = kwargs
        return "GROUNDING: objective, next step, Gate 1, preconditions."

    monkeypatch.setattr("src.nodes.orchestrator.complete", fake_complete)

    update = t00_orchestrator_node(initial_state(run_id="grounding-live-001"))

    assert update["run_grounding"] == "GROUNDING: objective, next step, Gate 1, preconditions."
    assert _t00_prov(update)["grounded"] is True
    # run context is threaded through for trace correlation.
    assert captured["tier"] == _ORCHESTRATOR_TIER
    assert captured["kwargs"].get("run_id") == "grounding-live-001"
    assert captured["kwargs"].get("agent_id") == "orchestrator"
