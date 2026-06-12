#!/usr/bin/env python3
"""
Documentation drift detector for HC-GRC pull requests.

Maps changed files to affected documentation layers. Posts a structured
drift report. Exits non-zero on critical drift.

Usage:
    python scripts/check_doc_drift.py                # full report (factual audit + diff advisory)
    python scripts/check_doc_drift.py --factual      # factual audit only — no git needed (pre-commit)
    python scripts/check_doc_drift.py --critical-only  # exit 1 if critical drift (incl. factual)

Two layers:
  - Factual audit (always runs): counts agents/**/AGENT.md and the ADR range, and
    BLOCKS if README/OVERVIEW/CARDS_SPEC state a different number. This is the
    enforcing layer — it catches the agent-count / ADR-index drift the advisory
    map below only hinted at.
  - Diff advisory (needs changed files): maps changed paths to docs that may need
    review. Mostly WARN.

Called by: .github/workflows/docs-sync.yml on every PR; .pre-commit-config.yaml on every commit.
Governs:   agents/15-platform-devsecops/repo-documentation/AGENT.md

Pattern matching: uses pathlib.PurePath.match() which supports ** recursive globs.
fnmatch.fnmatch() was intentionally NOT used — it does not support ** semantics.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePath


# ── Drift severity ────────────────────────────────────────────────────────────

WARN = "warn"    # update required before merge (advisory)
BLOCK = "block"  # blocks merge — misrepresentation or integrity risk


# ── File pattern → documentation impact map ──────────────────────────────────
# Each entry: (glob_pattern, severity, affected_docs, human_instruction, anchor_hint)
# Pattern uses pathlib.PurePath.match() semantics: ** matches any number of dirs.

DRIFT_MAP: list[tuple[str, str, list[str], str, str]] = [
    (
        "agents/**/*.md",
        WARN,
        ["README.md § Architecture", "OVERVIEW.md § What This Builds"],
        "A new or modified agent card may require updating the Architecture section "
        "in README.md (agent count, team structure) and the 'What This Builds' section "
        "in OVERVIEW.md if a new analytical module was added.",
        "README.md: search '## Architecture' or '## Agent Teams'. "
        "OVERVIEW.md: search '## What This Builds' or the five-module table.",
    ),
    (
        "src/agents/**",
        WARN,
        ["README.md § Status"],
        "Agent implementation changes may require updating the Status section in README.md "
        "to reflect current build state (scaffolded / implemented / tested).",
        "README.md: search '## Status' or '## Current State'.",
    ),
    (
        "src/**/*.py",
        WARN,
        ["README.md § Status"],
        "Implementation changes may require updating the Status section in README.md.",
        "README.md: search '## Status' or '## Current State'.",
    ),
    (
        "configs/**",
        WARN,
        ["README.md § Navigating This Repository"],
        "New or changed config files may need to be reflected in the repository navigation guide.",
        "README.md: search '## Navigating' or '## Repository Structure'.",
    ),
    (
        "docs/decisions/**",
        WARN,
        ["README.md § Key Documents"],
        "New ADRs should be added to the Key Documents table in README.md with title, "
        "date, and one-sentence decision summary.",
        "README.md: search '## Key Documents' or the ADR table.",
    ),
    (
        "docs/protocol/**",
        WARN,
        ["README.md § Research Design", "OVERVIEW.md § research integrity"],
        "Protocol changes may require updating the Research Design description in README.md "
        "and the research integrity section in OVERVIEW.md.",
        "README.md: search '## Research Design' or '## Protocol'. "
        "OVERVIEW.md: search '## What Makes This Different' or the pre-registration paragraph.",
    ),
    (
        "docs/architecture/**",
        WARN,
        ["README.md § Architecture"],
        "Architecture document changes may require updating the Architecture section "
        "in README.md to reflect current agent team structure and system design.",
        "README.md: search '## Architecture' or '## System Design'.",
    ),
    (
        "reports/executive-summary/**",
        WARN,
        ["OVERVIEW.md § Where Things Stand"],
        "Executive summary outputs require updating the 'Where Things Stand' section "
        "in OVERVIEW.md to reflect current findings state for P1/P2 audiences.",
        "OVERVIEW.md: search '## Where Things Stand'.",
    ),
    (
        "docs/protocol/PREREGISTRATION_LEDGER.md",
        BLOCK,
        ["README.md § Research Design", "OVERVIEW.md § What Makes This Different"],
        "Pre-registration ledger changes are gate-level events. README.md Research Design "
        "and OVERVIEW.md 'What Makes This Different' (pre-registration paragraph) must be "
        "reviewed and updated to reflect current registration state.",
        "README.md: search '## Research Design'. "
        "OVERVIEW.md: search '## What Makes This Different' — specifically the pre-registration claim.",
    ),
    (
        "docs/protocol/GATES.md",
        BLOCK,
        ["OVERVIEW.md § Where Things Stand", "README.md § Status"],
        "GATES.md changes indicate a phase or gate transition. OVERVIEW.md 'Where Things Stand' "
        "and README.md Status must be updated to reflect current platform state for all audiences.",
        "OVERVIEW.md: search '## Where Things Stand'. README.md: search '## Status'.",
    ),
    (
        "analysis/02-confirmatory/**",
        BLOCK,
        ["OVERVIEW.md § Where Things Stand", "reports/executive-summary/"],
        "Confirmed analysis outputs exist. OVERVIEW.md must not describe the research as "
        "pre-findings. An executive summary in reports/executive-summary/ must exist and be "
        "current before this merges. Gate 4 approval required.",
        "OVERVIEW.md: search '## Where Things Stand'. "
        "Check reports/executive-summary/ directory exists and contains a current summary.",
    ),
    (
        "manuscript/**",
        BLOCK,
        ["OVERVIEW.md § Where Things Stand", "README.md § Status"],
        "Manuscript changes indicate a publication milestone. OVERVIEW.md and README.md "
        "Status must be updated to reflect current publication state.",
        "OVERVIEW.md: search '## Where Things Stand'. README.md: search '## Status'.",
    ),
    (
        "OVERVIEW.md",
        BLOCK,
        ["Branding compliance review required"],
        "OVERVIEW.md is executive-mode (P1/P2) content. Changes require human branding "
        "review before merge: verify voice architecture compliance (premium executive rigor, "
        "warm authority, no unexplained jargon). Check the PR template Branding Compliance "
        "section and confirm the lab notebook entry. "
        "GATE GUARD: if analysis/02-confirmatory/ is empty, OVERVIEW.md must not contain "
        "findings language (effect sizes, p-values, 'results show', 'we find', 'confirmed').",
        "Review OVERVIEW.md diff for: new findings language, jargon without plain-language "
        "bridge, marketing boilerplate, missing 'so what' at each section.",
    ),
    (
        "RESEARCH_BRIEF.md",
        BLOCK,
        ["Branding compliance review required", "Gate 4 status check required"],
        "RESEARCH_BRIEF.md is investor-thesis executive content (P1/P2). Changes require "
        "human branding review AND Gate 4 confirmation before merge. This document must not "
        "contain research findings before Gate 4 (confirmatory results review) is approved.",
        "Verify Gate 4 status in docs/protocol/GATES.md before allowing findings language. "
        "Review diff for: premature findings claims, unsubstantiated independence assertions, "
        "jargon without definition.",
    ),
]

# ── Required sections — executive-mode documents ──────────────────────────────
# Used by structural integrity check. Keys are file paths (relative to repo root).
# Values are section header patterns that must be present in the file.
REQUIRED_SECTIONS: dict[str, list[str]] = {
    "OVERVIEW.md": [
        "## Where Things Stand",
        "## What Makes This Different",
        "## What This Builds",
    ],
}

# ── Directories that must be covered in DRIFT_MAP ─────────────────────────────
# Self-coverage check: alert if a project directory has no DRIFT_MAP entry.
EXPECTED_COVERED_PREFIXES: list[str] = [
    "agents/",
    "src/agents/",
    "src/",
    "configs/",
    "docs/decisions/",
    "docs/protocol/",
    "docs/architecture/",
    "reports/executive-summary/",
    "analysis/02-confirmatory/",
    "manuscript/",
]


# ── Core logic ────────────────────────────────────────────────────────────────

@dataclass
class DriftFinding:
    changed_file: str
    severity: str
    affected_docs: list[str]
    instruction: str
    anchor_hint: str


def load_changed_files(path: str) -> list[str]:
    try:
        lines = Path(path).read_text().strip().splitlines()
        return [ln.strip() for ln in lines if ln.strip()]
    except FileNotFoundError:
        return []


def path_matches(file_path: str, pattern: str) -> bool:
    """
    Match a file path against a glob pattern using pathlib.PurePath.match().
    Supports ** recursive glob semantics.

    pathlib.PurePath.match() matches from the RIGHT — patterns without a leading
    component match suffixes. To match from the root we anchor by passing the
    full path. Patterns starting with a named component (e.g. 'agents/**/*.md')
    are matched against the full path string via PurePath.
    """
    p = PurePath(file_path)
    return p.match(pattern)


def detect_drift(changed_files: list[str]) -> list[DriftFinding]:
    findings: list[DriftFinding] = []
    seen: set[tuple[str, str]] = set()

    for changed in changed_files:
        for pattern, severity, affected_docs, instruction, anchor in DRIFT_MAP:
            if path_matches(changed, pattern):
                key = (pattern, changed)
                if key not in seen:
                    findings.append(DriftFinding(
                        changed_file=changed,
                        severity=severity,
                        affected_docs=affected_docs,
                        instruction=instruction,
                        anchor_hint=anchor,
                    ))
                    seen.add(key)

    return findings


def check_composite_gate(changed_files: list[str]) -> list[DriftFinding]:
    """
    Composite relational checks that require cross-file awareness.
    Cannot be expressed as independent per-file patterns.
    """
    findings: list[DriftFinding] = []

    confirmatory_changed = any(
        path_matches(f, "analysis/02-confirmatory/**") for f in changed_files
    )
    overview_changed = any(f == "OVERVIEW.md" for f in changed_files)

    if confirmatory_changed and not overview_changed:
        findings.append(DriftFinding(
            changed_file="[COMPOSITE CHECK]",
            severity=BLOCK,
            affected_docs=["OVERVIEW.md § Where Things Stand"],
            instruction=(
                "Confirmatory analysis outputs changed but OVERVIEW.md was NOT updated. "
                "OVERVIEW.md must not describe the research as pre-findings once confirmed "
                "results exist. Update 'Where Things Stand' and generate an executive summary "
                "in reports/executive-summary/ before merge. Gate 4 approval required."
            ),
            anchor_hint="OVERVIEW.md: search '## Where Things Stand'.",
        ))

    return findings


def check_self_coverage() -> list[str]:
    """
    Verify that known project directories have DRIFT_MAP coverage.
    Returns a list of warning strings if any prefix is uncovered.
    """
    all_patterns = " ".join(pattern for pattern, *_ in DRIFT_MAP)
    uncovered = []
    for prefix in EXPECTED_COVERED_PREFIXES:
        # Check if any pattern would plausibly match files in this prefix
        covered = any(
            pattern.startswith(prefix.rstrip("/")) or prefix.rstrip("/") in pattern
            for pattern, *_ in DRIFT_MAP
        )
        if not covered:
            uncovered.append(prefix)
    return uncovered


def format_finding_block(f: DriftFinding) -> list[str]:
    lines = []
    if f.changed_file == "[COMPOSITE CHECK]":
        lines.append("**Composite check — cross-file condition:**")
    else:
        lines.append(f"**Changed:** `{f.changed_file}`")
    lines.append(f"**Affects:** {', '.join(f.affected_docs)}")
    lines.append(f"**Required action:** {f.instruction}")
    lines.append(f"**Where to look:** {f.anchor_hint}")
    lines.append("")
    return lines


def format_report(
    changed_files: list[str],
    findings: list[DriftFinding],
    uncovered: list[str],
) -> str:
    if not findings and not uncovered:
        return (
            "✅ **No documentation drift detected.**\n\n"
            f"Checked {len(changed_files)} changed file(s) against the "
            "documentation impact map. No documentation updates required."
        )

    blocks = [f for f in findings if f.severity == BLOCK]
    warns = [f for f in findings if f.severity == WARN]

    lines: list[str] = []

    if blocks:
        lines.append(
            f"🚫 **{len(blocks)} critical drift item(s) — merge blocked until resolved.**"
        )
    if warns:
        lines.append(
            f"⚠️ **{len(warns)} documentation update(s) required before merge.**"
        )
    if uncovered:
        lines.append(
            f"🗺️ **{len(uncovered)} project directory/directories not covered by drift map — consider updating `scripts/check_doc_drift.py`.**"
        )

    lines.append("")

    if blocks:
        lines.append("### 🚫 Critical — Merge Blocked")
        lines.append("")
        for f in blocks:
            lines.extend(format_finding_block(f))

    if warns:
        lines.append("### ⚠️ Required Updates")
        lines.append("")
        for f in warns:
            lines.extend(format_finding_block(f))

    if uncovered:
        lines.append("### 🗺️ Drift Map Coverage Gaps")
        lines.append("")
        lines.append(
            "The following project directories have no entry in `scripts/check_doc_drift.py`. "
            "Add entries before files in these directories can be merged with confidence:"
        )
        for prefix in uncovered:
            lines.append(f"- `{prefix}`")
        lines.append("")

    lines.append("---")
    lines.append(
        "Run `make check-docs` locally to verify fixes before pushing. "
        "Complete the PR template checklist and re-push to re-run this check."
    )

    return "\n".join(lines)


# ── Factual audit — verify stated counts against ground truth ─────────────────
# Unlike the diff-based drift map (advisory), these checks read the repository and
# the documents and BLOCK on any mismatch. They run on EVERY invocation — with or
# without changed files — so a local pre-commit hook catches the kind of drift
# (agent count, ADR index) that the advisory map only hinted at.

REPO_ROOT = Path(__file__).resolve().parent.parent


def _agent_card_count() -> int:
    return len(list((REPO_ROOT / "agents").glob("**/AGENT.md")))


def _max_adr_number() -> int:
    nums = [
        int(m.group(1))
        for p in (REPO_ROOT / "docs" / "decisions").glob("*.md")
        if (m := re.search(r"(\d{4})", p.name))
    ]
    return max(nums) if nums else 0


# (path, regex with ONE numeric capture group, truth key, label)
FACTUAL_PATTERNS: list[tuple[str, str, str, str]] = [
    ("README.md", r"(\d+) AGENT\.md specification cards", "agent_count", "agent card count (nav block)"),
    ("README.md", r"Agent library complete \((\d+) cards\)", "agent_count", "agent card count (Status)"),
    ("OVERVIEW.md", r"The (\d+)-agent research system", "agent_count", "agent count (OVERVIEW)"),
    ("agents/CARDS_SPEC.md", r"The (\d+) cards in `agents", "agent_count", "agent card count (CARDS_SPEC)"),
    ("README.md", r"ADR-0001 through ADR-0*(\d+)", "adr_max", "ADR index range (Key Documents)"),
]

# Spelled-out literals that are definitively stale once the count moves past them.
# Update when the canonical agent count changes.
STALE_SPELLED: list[tuple[str, str]] = [
    ("README.md", "Forty-eight"), ("README.md", "Forty-nine"),
    ("OVERVIEW.md", "Forty-eight"), ("OVERVIEW.md", "Forty-nine"),
]


def factual_audit() -> list[DriftFinding]:
    """Verify document-stated facts against repository ground truth. BLOCK on mismatch."""
    findings: list[DriftFinding] = []
    truth = {"agent_count": _agent_card_count(), "adr_max": _max_adr_number()}

    for rel_path, pattern, truth_key, label in FACTUAL_PATTERNS:
        f = REPO_ROOT / rel_path
        if not f.exists():
            continue
        expected = truth[truth_key]
        m = re.search(pattern, f.read_text())
        if m is None:
            findings.append(DriftFinding(
                changed_file=rel_path, severity=BLOCK,
                affected_docs=[f"{rel_path} — {label}"],
                instruction=(
                    f"Expected a statement asserting {label} = {expected}, but none matched "
                    f"/{pattern}/. Canonical value is {expected}."
                ),
                anchor_hint=f"Add/restore the {label} statement in {rel_path}.",
            ))
            continue
        if int(m.group(1)) != expected:
            findings.append(DriftFinding(
                changed_file=rel_path, severity=BLOCK,
                affected_docs=[f"{rel_path} — {label}"],
                instruction=f"{label} states {m.group(1)} but ground truth is {expected}. Update {rel_path}.",
                anchor_hint=f"{rel_path}: search for '{m.group(0)}'.",
            ))

    for rel_path, literal in STALE_SPELLED:
        f = REPO_ROOT / rel_path
        if f.exists() and literal in f.read_text():
            findings.append(DriftFinding(
                changed_file=rel_path, severity=BLOCK,
                affected_docs=[f"{rel_path} — stale spelled count"],
                instruction=f"'{literal}' is a stale spelled-out count. Current agent count is {truth['agent_count']}.",
                anchor_hint=f"{rel_path}: search for '{literal}'.",
            ))

    return findings


def main(critical_only: bool = False, factual_only: bool = False) -> int:
    factual = factual_audit()

    if factual_only:
        if factual:
            print(format_report([], factual, []))
        else:
            print("✅ Factual audit passed (agent count, ADR index).")
        return 1 if any(f.severity == BLOCK for f in factual) else 0

    changed_files_path = os.environ.get("CHANGED_FILES_PATH", "/tmp/changed_files.txt")
    changed_files = load_changed_files(changed_files_path)

    # Factual blocks always count, even when no files changed (local/pre-commit use).
    findings = list(factual)
    if changed_files:
        findings += detect_drift(changed_files)
        findings += check_composite_gate(changed_files)

    blocks = [f for f in findings if f.severity == BLOCK]

    if critical_only:
        return 1 if blocks else 0

    uncovered = check_self_coverage()
    print(format_report(changed_files, findings, uncovered))

    return 1 if blocks else 0


if __name__ == "__main__":
    critical_only = "--critical-only" in sys.argv
    factual_only = "--factual" in sys.argv
    sys.exit(main(critical_only=critical_only, factual_only=factual_only))
