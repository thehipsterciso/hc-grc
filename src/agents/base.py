"""
HC-GRC agent base types and contracts.

All Phase 1 research agents inherit from BaseResearchAgent or implement the
same __call__ signature. The contract is:

    agent(state: HCGRCState, **kwargs) -> dict[str, Any]

The return dict is a LangGraph partial state update — merged into HCGRCState
by the graph runtime. Agents must never mutate state in place.

PROTECTED agents (P1–P5, statistical-analyst, hypothesis-formalizer) have
PROTECTED = True. Agent Evolution may not modify their prompts autonomously.
Any modification requires Escalation approval (ADR-0015 §77).

Phase guard:
  - Exploratory phase: access train_ids + val_ids only
  - Confirmatory phase: access test_ids — only after Gate 2 approval
  - Agents check state["gate_status"]["gate_2"].decision == "approved" before
    touching test split. Violation is a SAP violation.

EXP_ prefix convention:
  - All exploratory artifacts use EXP_ filename prefix
  - No p-value decision language in EXP_ outputs
  - Confirmatory scripts carry a SAP header with hypothesis ID and decision rule
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Literal

from ..state import HCGRCState

# ── Shared input types ────────────────────────────────────────────────────────

class STRMMapping:
    """
    A single STRM mapping between two SCF controls.

    In Phase 0 (synthetic): populated with placeholder values.
    In Phase 1+: populated from data/splits/*.parquet.
    """
    __slots__ = (
        "source_control_id", "target_control_id",
        "relationship_type", "strength_score",
        "source_domain", "target_domain",
        "source_framework", "target_framework",
    )

    def __init__(
        self,
        source_control_id: str,
        target_control_id: str,
        relationship_type: Literal["subset", "superset", "intersection", "equal", "no_relation"],
        strength_score: float | None = None,
        source_domain: str | None = None,
        target_domain: str | None = None,
        source_framework: str | None = None,
        target_framework: str | None = None,
    ) -> None:
        self.source_control_id = source_control_id
        self.target_control_id = target_control_id
        self.relationship_type = relationship_type
        self.strength_score = strength_score
        self.source_domain = source_domain
        self.target_domain = target_domain
        self.source_framework = source_framework
        self.target_framework = target_framework


class ControlMetadata:
    """Metadata for a single SCF control node."""
    __slots__ = (
        "control_id", "domain", "framework",
        "maturity_level", "mcr_dsr",
    )

    def __init__(
        self,
        control_id: str,
        domain: str,
        framework: str,
        maturity_level: str | None = None,
        mcr_dsr: Literal["MCR", "DSR", None] = None,
    ) -> None:
        self.control_id = control_id
        self.domain = domain
        self.framework = framework
        self.maturity_level = maturity_level
        self.mcr_dsr = mcr_dsr


# ── Phase guard ───────────────────────────────────────────────────────────────

class SAPViolationError(Exception):
    """Raised when an agent attempts to access test data before Gate 2."""
    pass


def assert_gate2_approved(state: HCGRCState) -> None:
    """
    Raise SAPViolationError if Gate 2 has not been approved.

    Must be called before any agent accesses test_ids or test split data.
    This is the primary enforcement mechanism for the pre-registration firewall.
    """
    gate_status = state.get("gate_status", {})
    gate_2 = gate_status.get("gate_2")
    if gate_2 is None or gate_2.get("decision") != "approved":
        raise SAPViolationError(
            "Attempted to access test split before Gate 2 approval. "
            "This is a SAP violation. Gate 2 status: "
            f"{gate_2.get('decision') if gate_2 else 'not_run'}. "
            "Do not access test_ids or confirmatory split until gate_2.decision == 'approved'."
        )


# ── Base agent ────────────────────────────────────────────────────────────────

class BaseResearchAgent(ABC):
    """
    Abstract base for all HC-GRC Phase 1 research agents.

    Subclasses implement run_exploratory() and run_confirmatory() separately.
    The __call__ method dispatches based on state["phase"].

    Protected agents set PROTECTED = True — checked by Agent Evolution before
    any prompt modification.
    """

    PROTECTED: bool = False  # override in P1–P5, statistical-analyst, hypothesis-formalizer
    AGENT_ID: str = ""       # kebab-case, matches AGENT.md name field

    def __call__(self, state: HCGRCState) -> dict[str, Any]:
        """
        LangGraph-compatible call: returns a partial state update dict.

        Dispatches to run_exploratory() or run_confirmatory() based on phase.

        The canonical phase values written by the graph are phase_0 / phase_1 /
        phase_2 (see state.Phase). Exploratory analysis runs in phase_0/phase_1;
        confirmatory analysis runs in phase_2, where the Gate 2 SAP firewall
        (assert_gate2_approved) must hold before any test-split access. The legacy
        string aliases "exploratory"/"confirmatory" are accepted defensively.
        (Hardening pass 1, #17: phase_2 previously hit the else-branch and raised,
        so run_confirmatory and the SAP firewall were unreachable.)
        """
        phase = state.get("phase", "phase_0")
        if phase in ("phase_0", "phase_1", "exploratory"):
            return self.run_exploratory(state)
        elif phase in ("phase_2", "confirmatory"):
            assert_gate2_approved(state)
            return self.run_confirmatory(state)
        else:
            raise ValueError(f"Unknown phase: {phase!r}")

    @abstractmethod
    def run_exploratory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Execute exploratory analysis on train + val splits.

        All output artifact filenames must be prefixed EXP_.
        No p-value decision language in any exploratory output.
        Must not touch test_ids.
        """
        ...

    @abstractmethod
    def run_confirmatory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Execute confirmatory analysis on test split for one hypothesis.

        Gate 2 approval is verified by __call__ before this is invoked.
        Every confirmatory script must carry a SAP header:
          # SAP header: hypothesis_id=H[x].[n], test=[named test],
          #             effect_size_threshold=[value], decision_rule=[criterion]
        """
        ...


# ── Base pipeline agent ───────────────────────────────────────────────────────

class BasePipelineAgent(ABC):
    """
    Abstract base for data pipeline agents (acquisition, curation, steward, embedding).

    Pipeline agents prepare and version the research corpus. They do not perform
    exploratory or confirmatory analysis — they have no run_exploratory() /
    run_confirmatory() distinction. They run once at project initialization and
    re-run when the SCF corpus is updated.

    Pipeline agents are never PROTECTED — they contain no analysis logic that
    could affect research conclusions. Agent Evolution may modify them without
    Escalation approval.

    The run() return dict is a partial HCGRCState update, merged by the graph runtime.
    Agents must never mutate state in place.
    """

    AGENT_ID: str = ""     # kebab-case, matches AGENT.md name field
    PROTECTED: bool = False  # never True for pipeline agents

    @abstractmethod
    def run(self, state: HCGRCState) -> dict[str, Any]:
        """
        Execute the pipeline stage and return a partial HCGRCState update.

        Raises NotImplementedError until the real SCF data pipeline is live
        on the Mac mini with DVC and Qdrant configured.
        """
        ...
