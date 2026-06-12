"""
DataAcquisitionAgent — SCF corpus acquisition and ARA Compiler ingestion.

Acquires from the authoritative SCF GitHub repository, verifies SHA-256 integrity,
and runs the ARA Compiler to produce structured research artifacts in ara/artifacts/.
Single point of contact between the platform and the SCF source.

Phase 1 stub: run() raises NotImplementedError until real SCF data pipeline is
live on the Mac mini with DVC and ARA Compiler configured.

Required tools: mcp-dvc, mcp-lab-notebook
Required skills: ara-compiler, ray-data
See: agents/02-data/data-acquisition/AGENT.md
"""

from __future__ import annotations

import datetime
from typing import Any

from ..base import BasePipelineAgent
from ...state import HCGRCState


# ── Result type ───────────────────────────────────────────────────────────────


class AcquisitionResult:
    """Record of a completed data acquisition run."""

    __slots__ = (
        "source_url",
        "github_commit_hash",
        "sha256_hash",
        "acquisition_timestamp_utc",
        "control_count",
        "strm_mapping_count",
        "ara_artifact_paths",
        "dvc_remote_confirmed",
    )

    def __init__(
        self,
        source_url: str,
        github_commit_hash: str,
        sha256_hash: str,
        acquisition_timestamp_utc: str,
        control_count: int,
        strm_mapping_count: int,
        ara_artifact_paths: list[str],
        dvc_remote_confirmed: bool,
    ) -> None:
        self.source_url = source_url
        self.github_commit_hash = github_commit_hash
        self.sha256_hash = sha256_hash
        self.acquisition_timestamp_utc = acquisition_timestamp_utc
        self.control_count = control_count
        self.strm_mapping_count = strm_mapping_count
        self.ara_artifact_paths = ara_artifact_paths
        self.dvc_remote_confirmed = dvc_remote_confirmed


# Sanity bounds per AGENT.md Failure Modes — halt if below
_MIN_CONTROL_COUNT = 1_200
_MIN_STRM_MAPPING_COUNT = 250_000


# ── Agent ─────────────────────────────────────────────────────────────────────


class DataAcquisitionAgent(BasePipelineAgent):
    """
    Acquires SCF corpus from GitHub, verifies SHA-256, ingests via ARA Compiler.

    Behavioral constraints (per AGENT.md):
      - Never modify raw XLSX after acquisition — write-protected from landing
      - Never acquire from non-authoritative source
      - Halt immediately if SHA-256 verification fails — do not pass downstream
      - All data stays local — DVC remote is local filesystem only
      - Never overwrite a prior acquisition without creating a new DVC version
      - License guard: SCF (CC BY-ND 4.0) pre-approved; all other framework
        full-text requires operator license sign-off in lab notebook before ingest
    """

    AGENT_ID = "data-acquisition"
    PROTECTED = False

    def run(self, state: HCGRCState) -> dict[str, Any]:
        """
        Acquire SCF corpus, verify integrity, run ARA Compiler ingestion.

        Phase 1 implementation will:
          1. Read configs/data_sources.yaml for GitHub URL, branch, expected sheets
          2. Clone/pull from SCF GitHub at configured commit (mcp-dvc)
          3. Verify SHA-256 against MANIFEST.md — halt via RuntimeError if mismatch
          4. Record github_commit_hash and acquisition_timestamp to MANIFEST.md
          5. Run ARA Compiler — convert XLSX to JSON+Parquet in ara/artifacts/
          6. Validate record counts: controls >= 1,200; STRM mappings >= 250,000
          7. DVC push to local remote (never SaaS)
          8. Append acquisition event to lab notebook (append-only, mcp-lab-notebook)

        Returns partial HCGRCState update:
          prov_activities: acquisition provenance record
          phase_1_ready: remains False until DataStewardAgent writes splits
        """
        raise NotImplementedError(
            "DataAcquisitionAgent.run() — Phase 1 implementation pending. "
            "Requires: SCF GitHub access, mcp-dvc configured, ARA Compiler schema "
            "matching current SCF version. See agents/02-data/data-acquisition/AGENT.md."
        )

    def _verify_sha256(self, file_path: str, expected_hash: str) -> None:
        """
        Verify SHA-256 of acquired file against expected hash in MANIFEST.md.

        Raises RuntimeError if mismatch — behavioral constraint:
        never proceed if SHA-256 verification fails.
        """
        raise NotImplementedError

    def _validate_record_counts(self, result: AcquisitionResult) -> None:
        """
        Validate record counts meet minimum thresholds.

        Controls >= _MIN_CONTROL_COUNT, STRM mappings >= _MIN_STRM_MAPPING_COUNT.
        Raises ValueError if below — triggers halt and human escalation.
        """
        errors: list[str] = []
        if result.control_count < _MIN_CONTROL_COUNT:
            errors.append(
                f"controls={result.control_count} < minimum {_MIN_CONTROL_COUNT}"
            )
        if result.strm_mapping_count < _MIN_STRM_MAPPING_COUNT:
            errors.append(
                f"strm_mappings={result.strm_mapping_count} < minimum {_MIN_STRM_MAPPING_COUNT}"
            )
        if errors:
            raise ValueError(
                "Acquisition record count anomaly — possible incomplete acquisition. "
                "Halt required; human review before any downstream agent runs. "
                f"Failures: {'; '.join(errors)}"
            )

    def _build_prov_record(
        self, result: AcquisitionResult, run_id: str
    ) -> dict[str, Any]:
        """Build a PROV-DM compatible provenance record for the acquisition event."""
        return {
            "activity": "scf_acquisition",
            "agent_id": self.AGENT_ID,
            "run_id": run_id,
            "source_url": result.source_url,
            "github_commit_hash": result.github_commit_hash,
            "sha256_hash": result.sha256_hash,
            "timestamp_utc": result.acquisition_timestamp_utc,
            "control_count": result.control_count,
            "strm_mapping_count": result.strm_mapping_count,
            "dvc_remote_confirmed": result.dvc_remote_confirmed,
        }
