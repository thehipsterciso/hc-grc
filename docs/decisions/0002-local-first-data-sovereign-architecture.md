# ADR-0002: Local-First, Data-Sovereign Architecture

**Status:** Accepted
**Date:** 2026-06-09
**Deciders:** Thomas Jones

---

## Context

HC-GRC processes the SCF corpus — a CC BY-ND licensed metaframework — and produces findings that will be submitted for publication. The platform generates embeddings, traces, experiment logs, and intermediate analysis artifacts. Several SaaS-hosted tooling options are available for observability (LangSmith), vector storage (Pinecone), and experiment tracking (W&B). Each would require data to leave the local machine.

Two constraints make data sovereignty non-negotiable: (1) the CC BY-ND license on the SCF prohibits publishing derived datasets — if derived artifacts are stored in a third-party SaaS, the license exposure is ambiguous; (2) the platform is a scientific research tool whose integrity depends on controlling the full data chain.

## Decision

All infrastructure is self-hosted locally. No data, embeddings, traces, or results leave the machine. Specifically:

- **LangSmith** is disqualified — SaaS-only, no self-hosted option
- **Pinecone** is disqualified — SaaS-only
- **W&B (Weights & Biases)** is disqualified — SaaS-only post-CoreWeave acquisition
- **Neptune AI** is disqualified — acquired by OpenAI, March 2026, shut down
- **Qdrant** replaces Pinecone — self-hosted Docker deployment
- **MLflow** replaces W&B — self-hosted, local PostgreSQL backend
- **Phoenix (Arize)** replaces LangSmith — self-hosted, OpenInference/OpenTelemetry instrumentation
- **PostgreSQL** provides LangGraph checkpointing and MLflow artifact storage
- **DVC** provides data and model versioning with local remote

Self-signed TLS on local services is expected behavior, not a bug.

## Alternatives Considered

**Hybrid: local compute, SaaS observability:** Tempting for reduced operational overhead. Rejected because trace data contains SCF-derived content (control text, embedding context, analysis prompts). CC BY-ND ambiguity plus reproducibility integrity requirements both point to local-only.

**OSS self-hosted W&B:** W&B Community (self-hosted) existed pre-CoreWeave acquisition. No longer maintained as of 2026. Eliminated.

## Consequences

**Positive:**
- No ambiguity about CC BY-ND compliance — derived artifacts never leave the machine
- Full audit trail under local control — no SaaS outage can affect reproducibility
- Self-signed TLS is normal; no certificate management complexity for external CAs

**Negative:**
- Operational overhead: Docker Compose services must be maintained locally
- No cloud backup by default — local backup strategy is the operator's responsibility
- Some SaaS integrations (CI badge, hosted dataset registries) require explicit workarounds

**Infrastructure services required (NOT agents — they don't act autonomously):**
PostgreSQL, Qdrant, MLflow, Phoenix, Langfuse (optional), TensorBoard
