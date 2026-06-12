"""
test_grounding.py — run-start grounding (#125, #126).

Covers:
  - load_project_structure() returns the canonical top-level allow-list
  - assert_canonical_path() accepts canonical paths + root files, rejects others
  - load_open_incidents() ignores the format template; returns open/monitoring only
  - load_institutional_memory() surfaces failure_events + register pointer
  - ground_orchestrator() integrates both
  - t00_orchestrator_node attaches grounding to provenance
"""
from __future__ import annotations

import pytest

from src.grounding import (
    assert_canonical_path,
    ground_orchestrator,
    load_institutional_memory,
    load_open_incidents,
    load_project_structure,
)
from src.nodes.orchestrator import t00_orchestrator_node
from src.state import initial_state


# ── #125 structural grounding ─────────────────────────────────────────────────

class TestStructure:
    def test_top_level_contains_known_dirs(self):
        top = load_project_structure()["top_level"]
        for d in ("agents", "src", "ara", "data", "docs", "reports"):
            assert d in top

    @pytest.mark.parametrize("path", [
        "agents/03-analysis/p1-strm-nlp/AGENT.md",
        "src/grounding.py",
        "reports/findings/FINDINGS_REPORT.md",
        "analysis/01-exploratory/EXP_P1_similarity.parquet",
        "README.md",            # repo-root file allowed
        "KICKOFF_READINESS.md",
    ])
    def test_canonical_paths_accepted(self, path):
        assert assert_canonical_path(path) == path

    @pytest.mark.parametrize("path", [
        "scratch/experiment.json",
        "tmp/foo.parquet",
        "my_new_dir/output.md",
    ])
    def test_non_canonical_paths_rejected(self, path):
        with pytest.raises(ValueError, match="non-canonical top-level"):
            assert_canonical_path(path)


# ── #126 institutional memory ─────────────────────────────────────────────────

class TestInstitutionalMemory:
    def test_open_incidents_ignores_template(self):
        # INCIDENTS.md ships with a format template but no real entries pre-launch.
        incidents = load_open_incidents()
        assert incidents == []

    def test_open_incidents_parses_real_entries(self, tmp_path):
        f = tmp_path / "INCIDENTS.md"
        f.write_text(
            "## Incident Log\n\n"
            "incident_id: INC-0001\nstatus: open\n\n"
            "incident_id: INC-0002\nstatus: resolved\n\n"
            "incident_id: INC-0003\nstatus: monitoring\n"
        )
        got = load_open_incidents(f)
        ids = {e["incident_id"] for e in got}
        assert ids == {"INC-0001", "INC-0003"}  # resolved excluded

    def test_memory_surfaces_recent_failure_events(self):
        state = {"failure_events": [{"gate": "gate_2", "reason": "x"}] * 12}
        mem = load_institutional_memory(state)
        assert len(mem["recent_failure_events"]) == 10  # last 10
        assert mem["adversarial_findings_ref"].endswith("ADVERSARIAL_FINDINGS.md")


# ── Integration ───────────────────────────────────────────────────────────────

class TestOrchestratorGrounding:
    def test_ground_orchestrator_shape(self):
        g = ground_orchestrator(initial_state())
        assert "canonical_top_level" in g
        assert g["open_incident_count"] == 0
        assert "agents" in g["canonical_top_level"]

    def test_node_records_grounding_in_provenance(self):
        result = t00_orchestrator_node(initial_state())
        prov = result["prov_activities"][0]
        assert "grounding" in prov
        assert "canonical_top_level" in prov["grounding"]
