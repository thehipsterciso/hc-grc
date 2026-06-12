"""
Repo Documentation Agent.

PURPOSE:
Produces and maintains audience-stratified documentation for the HC-GRC
repository. Three modes — executive, practitioner, technical — each written
for a distinct audience altitude drawn from the Hipster CISO persona taxonomy.

AUDIENCE TAXONOMY:
  executive    → P1 (B2B Executive Leader) + P2 (PE/Board/VC)
                 BCG/McKinsey altitude: business problem, strategic significance,
                 plain language, so-what explicit at every level
  practitioner → P3 (CDO/CAIO/CDAIO/CISO)
                 Methodological credibility, operational authenticity,
                 peer-level depth, tools-not-frameworks
  technical    → Developer/contributor
                 Implementation-first, dense, code-forward

BRANDING COMPLIANCE:
  All executive-mode content must pass Branding Compliance Agent review
  before commit. Independence positioning and commercial disclosure are
  non-negotiable checks.

PROTECTED STATUS:
  This agent is NOT a PROTECTED research agent per ADR-0015 §77.
  Documentation changes do not constitute research design changes.
  Agent Evolution may optimize documentation prompts autonomously.

See AGENT.md: agents/15-platform-devsecops/repo-documentation/AGENT.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from ..base import BaseResearchAgent, SAPViolation
from ...state import HCGRCState


DocumentationMode = Literal["executive", "practitioner", "technical"]

# Audience altitude notes injected into generation context by mode
_MODE_CONTEXT: dict[DocumentationMode, str] = {
    "executive": (
        "Target: P1 (B2B Executive Leader) and P2 (PE/Board/VC). "
        "Altitude: strategic. Opens with business problem, not technical solution. "
        "States the so-what explicitly at every section. "
        "No unexplained acronyms or jargon. "
        "Narrative arc: problem → current state gap → what we build → what changes. "
        "BCG/McKinsey presentation standard: clean hierarchy, bold claims supported "
        "immediately, no decorative content. Rewards 90-second skimming."
    ),
    "practitioner": (
        "Target: P3 (CDO/CAIO/CDAIO/CISO). "
        "Altitude: methodological + operational. "
        "Opens with credibility signals: pre-registration, gate structure, null results. "
        "Peer-level depth — no over-explaining. "
        "Operational authenticity: describes real complexity, does not sanitize. "
        "References tools by name. Specificity is respect."
    ),
    "technical": (
        "Target: Developer/contributor. "
        "Altitude: implementation. "
        "Architecture, interfaces, dependencies, test coverage, how to run, how to extend. "
        "Dense but navigable. Code blocks and precise naming."
    ),
}


@dataclass
class DocumentationRequest:
    """
    A request to generate or update a documentation artifact.

    All fields required. Mode determines altitude, voice, and format.
    Prior document content is read before any rewrite — no blind overwrites.
    """
    document_path: str              # relative path in repo, e.g. "OVERVIEW.md"
    mode: DocumentationMode         # executive | practitioner | technical
    trigger: str                    # what prompted this update, e.g. "Phase 0 complete"
    prior_content: str = ""         # current file content — populated before generation
    research_phase: str = "pre-execution"  # current platform phase
    compliance_required: bool = True  # executive mode always requires branding compliance


@dataclass
class DocumentationResult:
    """
    Output of a documentation generation run.
    """
    document_path: str
    mode: DocumentationMode
    content: str
    compliance_passed: bool | None = None  # None = not yet reviewed
    compliance_issues: list[str] = field(default_factory=list)
    run_id: str = ""
    notes: str = ""


class RepoDocumentationAgent(BaseResearchAgent):
    """
    Audience-stratified documentation agent for the HC-GRC repository.

    NOT a protected research agent — documentation does not affect research
    design and may be autonomously optimized by Agent Evolution.

    Dispatches by DocumentationMode, not by research phase. Can run in
    any phase (exploratory, confirmatory) for non-findings documentation.
    For executive summaries of findings: Gate 4 must be confirmed before
    findings are described as conclusions.
    """

    PROTECTED = False
    AGENT_ID = "repo-documentation"

    def __init__(
        self,
        repo_root: Path | str = Path("."),
        docs_output_dir: Path | str = Path("reports/executive-summary"),
    ) -> None:
        self.repo_root = Path(repo_root)
        self.docs_output_dir = Path(docs_output_dir)

    def run_exploratory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Generate or update documentation artifacts.

        Safe to run in exploratory phase for all documentation modes EXCEPT
        executive summaries of research findings (which require Gate 4).
        """
        raise NotImplementedError(
            "Documentation generation not yet implemented. "
            "Phase 1 implementation will: "
            "(1) read DocumentationRequest from state, "
            "(2) load mode context from _MODE_CONTEXT, "
            "(3) read current document content via mcp-github, "
            "(4) generate updated content respecting mode altitude and voice architecture, "
            "(5) for executive mode: pass to Branding Compliance Agent before commit, "
            "(6) commit via GitHub Management Agent, "
            "(7) log to lab notebook."
        )

    def run_confirmatory(self, state: HCGRCState) -> dict[str, Any]:
        """
        Generate executive summaries of confirmed research findings.

        Requires Gate 4 approval before findings described as conclusions.
        Executive summaries of unconfirmed findings are a misrepresentation.
        """
        raise NotImplementedError(
            "Confirmatory documentation (executive summaries of findings) "
            "not implemented until findings are available. "
            "Requires Gate 4 approval — confirmed results only."
        )

    def _get_mode_context(self, mode: DocumentationMode) -> str:
        """Return the audience altitude context string for the given mode."""
        return _MODE_CONTEXT[mode]

    def _requires_compliance_review(self, request: DocumentationRequest) -> bool:
        """
        Determine whether Branding Compliance Agent review is required.

        Executive mode always requires review.
        Practitioner and technical modes require review when content
        includes independence claims or commercial disclosures.
        """
        return request.mode == "executive" or request.compliance_required

    def _assert_findings_gated(self, state: HCGRCState, mode: DocumentationMode) -> None:
        """
        For executive mode documents describing research findings:
        assert Gate 4 is approved before framing findings as conclusions.

        Executive summaries of unconfirmed findings are a misrepresentation.
        This check applies only when the document contains finding claims —
        pre-execution and phase documentation are exempt.
        """
        if mode != "executive":
            return
        gate_status = state.get("gate_status", {})
        gate_4 = gate_status.get("gate_4")
        if gate_4 is None or gate_4.get("decision") != "approved":
            raise SAPViolation(
                "Executive summaries describing research findings require Gate 4 approval. "
                "Findings described as conclusions before confirmatory review is complete "
                "is a misrepresentation. Current Gate 4 status: "
                f"{gate_4.get('decision') if gate_4 else 'not_run'}."
            )
