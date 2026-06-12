"""
Run-start grounding for the orchestrator (#125, #126).

Loads the canonical repo structure and institutional memory so routing never
depends on a degrading context window. See the run-start grounding +
pre-phase memory-load constraints in
agents/00-orchestration/orchestrator/AGENT.md and ADR-0015 (#72): the
Agent-Evolution loop is only real if failures are read back, not just written.

Two capabilities:
  #125  load_project_structure() + assert_canonical_path()  — know where things
        go; refuse to allocate a path under a non-canonical top-level directory
        (a new top-level dir requires an ADR, not an autonomous decision).
  #126  load_institutional_memory()  — load open INCIDENTS + recent
        failure_events + the adversarial-findings register before a phase, so
        the orchestrator routes around documented failure modes.

Stdlib only.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
STRUCTURE_FILE = REPO_ROOT / "PROJECT_STRUCTURE.md"
INCIDENTS_FILE = REPO_ROOT / "INCIDENTS.md"
ADVERSARIAL_FINDINGS_REF = "docs/decisions/ADVERSARIAL_FINDINGS.md"

# Canonical top-level locations agents may write under. Pinned here as the
# guard's source of truth (fallback if PROJECT_STRUCTURE.md is unparseable),
# kept in sync with that file's top-level table.
CANONICAL_TOP_LEVEL: set[str] = {
    "agents", "src", "ara", "data", "analysis", "reports", "docs",
    "configs", "scripts", "tests", "reproducibility", "notebooks",
    "experiments", "manuscript",
}


# ── #125 — structural grounding ──────────────────────────────────────────────

def load_project_structure(structure_file: Path = STRUCTURE_FILE) -> dict[str, Any]:
    """Parse the canonical directory map. Returns {"top_level": set, "raw": str}.

    Falls back to CANONICAL_TOP_LEVEL if the file is absent so the guard always
    has a defined allow-list.
    """
    top = set(CANONICAL_TOP_LEVEL)
    raw = ""
    if structure_file.exists():
        raw = structure_file.read_text()
        # Top-level table cells are markdown code spans like `agents/` or `data/`.
        for m in re.finditer(r"`([a-z0-9_]+)/", raw):
            top.add(m.group(1))
    return {"top_level": top, "raw": raw}


def assert_canonical_path(path: str, structure: dict[str, Any] | None = None) -> str:
    """Path guard (#125). Return ``path`` if it is acceptable; raise ValueError if
    it sits under a non-canonical top-level directory.

    Files at the repo root (no slash) are allowed (e.g. README.md). Anything with
    a directory component must use a canonical top-level dir.
    """
    structure = structure or load_project_structure()
    top = structure["top_level"]
    norm = path.strip().lstrip("./").strip("/")
    if not norm:
        raise ValueError("empty path")
    if "/" not in norm:
        return path  # repo-root file
    head = norm.split("/", 1)[0]
    if head not in top:
        raise ValueError(
            f"path '{path}' is under non-canonical top-level '{head}/'. "
            f"Reuse an existing location, or add an ADR to introduce a new "
            f"top-level directory. Canonical: {sorted(top)}"
        )
    return path


# ── #126 — institutional-memory read-back ────────────────────────────────────

def load_open_incidents(incidents_file: Path = INCIDENTS_FILE) -> list[dict[str, str]]:
    """Return INCIDENTS entries whose status is ``open`` or ``monitoring``.

    Only the content after the ``## Incident Log`` heading is scanned, so the
    format-template example earlier in the file is never parsed as a real entry.
    """
    out: list[dict[str, str]] = []
    if not incidents_file.exists():
        return out
    text = incidents_file.read_text()
    marker = "## Incident Log"
    if marker in text:
        text = text.split(marker, 1)[1]
    for inc_id, status in re.findall(
        r"incident_id:\s*(INC-\d+)\b.*?status:\s*(open|monitoring|resolved)\b",
        text, re.S,
    ):
        if status in ("open", "monitoring"):
            out.append({"incident_id": inc_id, "status": status})
    return out


def load_institutional_memory(
    state: dict[str, Any] | None = None,
    incidents_file: Path = INCIDENTS_FILE,
) -> dict[str, Any]:
    """Pre-phase memory load (#126): open incidents + recent failure_events from
    state + a pointer to the adversarial-findings register. The orchestrator
    routes around these documented failure modes.
    """
    state = state or {}
    failure_events = state.get("failure_events") or []
    return {
        "open_incidents": load_open_incidents(incidents_file),
        "recent_failure_events": failure_events[-10:],
        "adversarial_findings_ref": ADVERSARIAL_FINDINGS_REF,
    }


# ── Combined run-start grounding (used by t00_orchestrator_node) ──────────────

def ground_orchestrator(state: dict[str, Any] | None = None) -> dict[str, Any]:
    """Load structure + institutional memory at run start. Returns a compact
    grounding summary for the orchestrator's provenance record.
    """
    structure = load_project_structure()
    memory = load_institutional_memory(state)
    return {
        "canonical_top_level": sorted(structure["top_level"]),
        "open_incident_count": len(memory["open_incidents"]),
        "open_incidents": memory["open_incidents"],
        "recent_failure_event_count": len(memory["recent_failure_events"]),
        "adversarial_findings_ref": memory["adversarial_findings_ref"],
    }
