"""
EmbeddingAgent — Dense vector infrastructure for SCF controls and STRM mappings.

Generates embeddings from the curated corpus, stores them in Qdrant (semantic
search, all agents), and builds the FAISS flat index (P1 all-pairs computation).
These are complementary — do not collapse into a single index.

Model selection is governed by LEDGER-0002 (model candidates pre-registered) and
configs/platform.yaml (model_candidates section). Primary model designation is a
Gate 2 event. All candidates in the LEDGER-0002 race must be evaluated in Phase 1
before designation.

If selected model F1 < 0.70 on STRM classification: triggers domain model
fine-tuning via Team 06 (human approval required).

Phase 1 stub: run() raises NotImplementedError.

Required tools: mcp-qdrant, mcp-dvc, mcp-lab-notebook
Required skills: sentence-transformers, qdrant
See: agents/02-data/embedding-agent/AGENT.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ...state import HCGRCState
from ..base import BasePipelineAgent

# ── Result types ──────────────────────────────────────────────────────────────


@dataclass
class EmbeddingManifest:
    """
    Provenance record for an embedding run. Written to state and to disk.
    Required at Gate 2 to confirm which model produced the embeddings.
    """

    model_name: str = ""           # HuggingFace model ID, e.g. "BAAI/bge-base-en-v1.5"
    model_hash: str = ""           # SHA-256 of model weights file
    corpus_dvc_hash: str = ""      # DVC hash of curated corpus used for embedding
    timestamp_utc: str = ""
    control_embedding_count: int = 0
    mapping_embedding_count: int = 0
    qdrant_collections: list[str] = field(
        default_factory=lambda: ["hcgrc_controls", "hcgrc_mappings"]
    )
    faiss_index_path: str = ""     # data/03-processed/faiss/ (DVC tracked)
    faiss_index_dvc_hash: str = ""
    strm_f1_score: float | None = None  # populated by P1 after evaluation; None pre-evaluation


@dataclass
class EmbeddingQualityReport:
    """Spot-check results for nearest-neighbor coherence. Surfaced in lab notebook."""

    sample_size: int = 50          # 50 samples per AGENT.md evaluation criteria
    coherent_count: int = 0
    incoherent_examples: list[str] = field(default_factory=list)
    mean_intracluster_similarity: float = 0.0
    oov_rate: float = 0.0          # out-of-vocabulary token rate
    p95_query_latency_ms: float = 0.0  # Qdrant semantic search


# F1 threshold below which domain fine-tuning is triggered (AGENT.md)
_STRM_F1_THRESHOLD = 0.70


# ── Agent ─────────────────────────────────────────────────────────────────────


class EmbeddingAgent(BasePipelineAgent):
    """
    Generates and manages the vector infrastructure for all HC-GRC semantic analysis.

    FAISS index: for P1's exhaustive all-pairs computation (~280K × 280K pairwise
    comparisons). Read-only after P1 analysis begins.

    Qdrant collections: for semantic search by P2, P3, P4, P5, and Literature Agent.
    Supports hybrid search (dense + sparse), metadata filtering by SCF domain/
    framework/maturity level, and scroll-based bulk retrieval.

    Behavioral constraints (per AGENT.md):
      - Never mix embeddings from different model versions in the same index
      - Embedding manifest updated before any analysis agent queries the index
      - FAISS index is read-only after P1 analysis begins
      - All stochastic components use seed from configs/seeds.yaml
      - Embedding drift: if mean cosine shift > 0.05 on new SCF version, flag
        for human review — never auto-re-embed
      - Never export Qdrant collections or FAISS indices off-machine (CC BY-ND 4.0)
    """

    AGENT_ID = "embedding-agent"
    PROTECTED = False

    # Drift threshold: if mean cosine similarity shift exceeds this after SCF update,
    # flag for human review rather than auto-re-embedding
    DRIFT_THRESHOLD = 0.05

    def run(self, state: HCGRCState) -> dict[str, Any]:
        """
        Generate embeddings, build Qdrant collections and FAISS index.

        Phase 1 implementation will:
          1. Load primary model candidate from configs/platform.yaml
             (model_candidates section — LEDGER-0002 candidate set)
             NOTE: primary model is NULL until Gate 2 designation. Phase 1 runs
             all 5 candidates (3 general + 2 diversity anchors) and records F1
             scores to inform Gate 2 model selection.
          2. Batch-encode curated control text (GPU if available, CPU fallback)
          3. Build Qdrant collection: hcgrc_controls (1,400+ controls)
          4. Build Qdrant collection: hcgrc_mappings (280K+ STRM pair embeddings)
          5. Build FAISS flat L2 index for P1 all-pairs (~280K × embedding_dim)
          6. Run quality spot-check: 50 nearest-neighbor samples, measure coherence
          7. Record EmbeddingManifest to state (embedding_manifest field)
          8. DVC push FAISS index to local remote
          9. Append embedding quality report to lab notebook

        If any model achieves F1 < 0.70 on STRM classification (evaluated by
        P1 agent after EDA), triggers domain fine-tuning via Team 06 + human
        approval before Gate 2 model designation.

        Returns partial HCGRCState update:
          embedding_manifest: EmbeddingManifest as dict
          phase_1_ready: True — data pipeline complete, P1-P5 may start
          prov_activities: embedding provenance record
        """
        raise NotImplementedError(
            "EmbeddingAgent.run() — Phase 1 implementation pending. "
            "Requires: curated corpus from DataCurationAgent, Qdrant Docker running, "
            "sentence-transformers + FAISS installed, configs/platform.yaml with "
            "LEDGER-0002 model candidates. See agents/02-data/embedding-agent/AGENT.md."
        )

    def check_f1_threshold(self, manifest: EmbeddingManifest) -> bool:
        """
        Returns True if strm_f1_score meets the minimum threshold.

        If False: triggers domain model fine-tuning request via Team 06.
        Called by P1 agent after EDA evaluation; result recorded to manifest.
        """
        if manifest.strm_f1_score is None:
            return True  # Not yet evaluated — allow to proceed
        return manifest.strm_f1_score >= _STRM_F1_THRESHOLD

    def check_embedding_drift(
        self, mean_cosine_shift: float
    ) -> bool:
        """
        Returns True if cosine similarity distribution shift is within threshold.

        If False: flag for human review. Never auto-re-embed on drift — requires
        protocol review to determine if drift affects pre-registered analysis.
        """
        return mean_cosine_shift <= self.DRIFT_THRESHOLD

    def _build_prov_record(
        self, manifest: EmbeddingManifest, run_id: str
    ) -> dict[str, Any]:
        """Build provenance record for the embedding run."""
        return {
            "activity": "embedding_generation",
            "agent_id": self.AGENT_ID,
            "run_id": run_id,
            "model_name": manifest.model_name,
            "model_hash": manifest.model_hash,
            "corpus_dvc_hash": manifest.corpus_dvc_hash,
            "timestamp_utc": manifest.timestamp_utc,
            "control_embedding_count": manifest.control_embedding_count,
            "mapping_embedding_count": manifest.mapping_embedding_count,
            "faiss_index_dvc_hash": manifest.faiss_index_dvc_hash,
        }
