#!/usr/bin/env python3
"""
Documentation drift detector for HC-GRC pull requests.

Maps changed files to affected documentation layers. Posts a structured
drift report. Exits non-zero on critical drift (confirmed findings without
updated executive documentation).

Usage:
    python scripts/check_doc_drift.py                # full report
    python scripts/check_doc_drift.py --critical-only  # exit 1 if critical drift

Called by: .github/workflows/docs-sync.yml on every PR.
Governs:   agents/15-platform-devsecops/repo-documentation/AGENT.md
"""

from __future__ import annotations

import fnmatch
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ── Drift severity ────────────────────────────────────────────────────────────

WARN = "warn"      # update required before merge (advisory)
BLOCK = "block"    # blocks merge — misrepresentation or integrity risk


# ── File pattern → documentation impact map ──────────────────────────────────
# Each entry: (glob_pattern, severity, affected_docs, human_instruction)

DRIFT_MAP: list[tuple[str, str, list[str], str]] = [
    (
        "agents/**/*.md",
        WARN,
        ["README.md (Architecture section)"],
        "A new or modified agent card may require updating the architecture "
        "description in README.md. Verify the agent count and team structure "
        "are still accurate.",
    ),
    (
        "src/agents/**",
        WARN,
        ["README.md (Status section)"],
        "Agent implementation changes may require updating the Status section "
        "in README.md to reflect current build state.",
    ),
    (
        "configs/**",
        WARN,
        ["README.md (Navigating This Repository)"],
        "New or changed config files may need to be reflected in the "
        "repository navigation guide.",
    ),
    (
        "docs/decisions/**",
        WARN,
        ["README.md (Key Documents table)"],
        "New ADRs should be added to the Key Documents table in README.md.",
    ),
    (
        "docs/protocol/**",
        WARN,
        ["README.md (Research Design)", "OVERVIEW.md (research integrity section)"],
        "Protocol changes may require updating the research design description "
        "in README.md and the integrity section in OVERVIEW.md.",
    ),
    (
        "docs/protocol/PREREGISTRATION_LEDGER.md",
        BLOCK,
        ["README.md (Research Design)", "OVERVIEW.md"],
        "Pre-registration ledger changes are gate-level events. "
        "README.md Research Design and OVERVIEW.md must be reviewed "
        "and updated to reflect the current registration state.",
    ),
    (
        "analysis/02-confirmatory/**",
        BLOCK,
        ["OVERVIEW.md (findings)", "reports/executive-summary/"],
        "Confirmed analysis outputs exist. OVERVIEW.md must not describe "
        "the research as pre-findings. Executive summary in "
        "reports/executive-summary/ must be generated before merge.",
    ),
    (
        "manuscript/**",
        BLOCK,
        ["OVERVIEW.md", "README.md (Status)"],
        "Manuscript changes indicate a publication milestone. "
        "OVERVIEW.md and README.md status must be updated to reflect "
        "current publication state.",
    ),
    (
        "src/**/*.py",
        WARN,
        ["README.md (Status)"],
        "Implementation changes may require updating the Status section "
        "in README.md.",
    ),
    (
        "OVERVIEW.md",
        WARN,
        ["Branding compliance review"],
        "OVERVIEW.md is executive-mode (P1/P2) content. Any change to this "
        "file requires branding compliance review per the repo-documentation "
        "agent constraints before merge.",
    ),
]


# ── Core logic ────────────────────────────────────────────────────────────────

@dataclass
class DriftFinding:
    changed_file: str
    severity: str
    affected_docs: list[str]
    instruction: str


def load_changed_files(path: str) -> list[str]:
    try:
        return Path(path).read_text().strip().splitlines()
    except FileNotFoundError:
        return []


def detect_drift(changed_files: list[str]) -> list[DriftFinding]:
    findings: list[DriftFinding] = []
    seen: set[tuple[str, str]] = set()

    for changed in changed_files:
        for pattern, severity, affected_docs, instruction in DRIFT_MAP:
            if fnmatch.fnmatch(changed, pattern):
                key = (pattern, changed)
                if key not in seen:
                    findings.append(DriftFinding(
                        changed_file=changed,
                        severity=severity,
                        affected_docs=affected_docs,
                        instruction=instruction,
                    ))
                    seen.add(key)

    return findings


def format_report(
    changed_files: list[str],
    findings: list[DriftFinding],
) -> str:
    if not findings:
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

    lines.append("")

    if blocks:
        lines.append("### 🚫 Critical — Merge Blocked")
        lines.append("")
        for f in blocks:
            lines.append(f"**Changed:** `{f.changed_file}`")
            lines.append(f"**Affects:** {', '.join(f.affected_docs)}")
            lines.append(f"**Required action:** {f.instruction}")
            lines.append("")

    if warns:
        lines.append("### ⚠️ Required Updates")
        lines.append("")
        for f in warns:
            lines.append(f"**Changed:** `{f.changed_file}`")
            lines.append(f"**Affects:** {', '.join(f.affected_docs)}")
            lines.append(f"**Action:** {f.instruction}")
            lines.append("")

    lines.append("---")
    lines.append(
        "Complete documentation updates, check the PR template checklist, "
        "and re-push to re-run this check."
    )

    return "\n".join(lines)


def main(critical_only: bool = False) -> int:
    changed_files_path = os.environ.get(
        "CHANGED_FILES_PATH", "/tmp/changed_files.txt"
    )
    changed_files = load_changed_files(changed_files_path)

    if not changed_files:
        print("No changed files detected. Skipping drift check.")
        return 0

    findings = detect_drift(changed_files)
    blocks = [f for f in findings if f.severity == BLOCK]

    if critical_only:
        return 1 if blocks else 0

    report = format_report(changed_files, findings)
    print(report)

    return 1 if blocks else 0


if __name__ == "__main__":
    critical_only = "--critical-only" in sys.argv
    sys.exit(main(critical_only=critical_only))
