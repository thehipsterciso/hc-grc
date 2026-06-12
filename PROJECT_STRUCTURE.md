# Project Structure — Canonical Map

**Version:** 0.1.0
**Status:** Authoritative — the single source of truth for *where things go*.
**Generated:** 2026-06-12 from the live tree. Regenerate when directories change.

> **Why this file exists.** As a run progresses, the orchestrator and agents lose
> contextual memory of the repo layout. Without a deterministic map, an agent that
> wants to (e.g.) drop an experiment will *invent* a new location instead of using
> the one already prepared — fragmenting the structure. This file is read at run
> start (see the Orchestrator card's run-start grounding constraint) so that
> location knowledge never depends on a model's degrading context.
>
> **Rule:** Reuse the locations below. **Do not create a new top-level directory
> without an ADR.** If a needed location is missing, extend an existing one or
> propose the addition — never silently create a parallel structure.
> The `exists?` column is load-bearing: several paths referenced in `README.md`'s
> navigation block are **not yet created** — do not assume a directory exists
> because a doc mentions it.

## Top-level layout

| Path | Exists? | Purpose | Who writes |
|------|:------:|---------|-----------|
| `agents/` | ✅ | 49 AGENT.md spec cards across 17 teams + `CARDS_SPEC.md`, `AGENT_TEMPLATE.md`, `MODEL_TIER_ASSIGNMENTS.md` | Orchestrator (spec) |
| `src/` | ✅ | Platform implementation — `graph.py`, `state.py`, `checkpointer.py`, `nodes/`, `agents/`, `infrastructure/` | Build |
| `src/agents/` | ✅ | One package per implemented agent (currently 12 stubs) | Build |
| `src/nodes/` | ✅ | LangGraph node functions (orchestrator, gates, data_split, phase1) | Build |
| `src/infrastructure/` | ✅ | MLflow / Phoenix / Qdrant / config wiring | Build |
| `ara/` | ✅ | `ARA_SPEC.md` (data contract) + `artifacts/` (compiled SCF model, findings records) | Data Acquisition, Report Agent |
| `data/` | ✅ | Pipeline: `01-raw/` → `02-interim/` → `03-processed/`; plus `embeddings/`, `external/` | Data team |
| `analysis/` | ✅ | `01-exploratory/` (EXP_* artifacts) and `02-confirmatory/` (H[x].[y]_* results) | P1–P5, Statistical Analyst |
| `reports/` | ✅ | Deliverables; `null-results/` exists; `findings/` created by Report Agent | Report + dissemination |
| `docs/` | ✅ | `architecture/`, `charter/`, `decisions/` (ADRs), `literature/`, `protocol/`, `research/` | All |
| `configs/` | ✅ | Experiment + pipeline config (`platform.yaml`, `data_sources.yaml`, `analysis.yaml`) | Build |
| `scripts/` | ✅ | Automation; `infra/` for provisioning | Build / DevSecOps |
| `tests/` | ✅ | `test_phase0/`, `test_infrastructure/`, `benchmarks/` | Build |
| `reproducibility/` | ✅ | Replication package | Provenance / QA |
| `mlruns/`, `mlflow.db`, `phoenix_storage/`, `qdrant_storage/` | ✅ | Local observability stores — runtime data, not source. DVC/git-ignored as configured | Infra (runtime) |
| `.github/workflows/` | ✅ | CI | CICD Agent |
| `notebooks/` | ❌ not yet | EDA notebooks (README references it) — **create only when first needed** | P1–P5 |
| `experiments/` | ❌ not yet | Experiment runs / empirical tracking (README references it) — **create only when first needed** | Build |
| `manuscript/` | ❌ not yet | Academic paper source (README references it) — created at dissemination | ML Paper Agent |

## Conventions agents must follow

- **Exploratory outputs** → `analysis/01-exploratory/`, prefixed `EXP_`. **Confirmatory** → `analysis/02-confirmatory/`, named `H{module}.{n}_*`. The prefix is a firewall signal (ADR-0007), validated.
- **Raw data is never modified in place**; new acquisitions are new DVC versions under `data/01-raw/`.
- **ARA artifacts** (the inter-agent data contract) live under `ara/artifacts/`, schema per `ara/ARA_SPEC.md`.
- **Null results** are first-class → `reports/null-results/`, same rigor as positive.
- **Findings synthesis** → `reports/findings/` (Report Agent), the single interpreted source.
- **New top-level directory ⇒ ADR.** Anything else extends the paths above.

## Institutional-memory locations (read these; see Orchestrator grounding)

| Path | Purpose |
|------|---------|
| `INCIDENTS.md` | Append-only failure log. Load `status: open / monitoring` entries before a phase starts. |
| `lab_notebook.md` | Chronological decision/dead-end record — the anti-cherry-picking trail. |
| `docs/decisions/` | ADRs + errata. ADR-0015 is the adversarial-findings resolutions (#71–#80). |
| `docs/protocol/PREREGISTRATION_LEDGER.md` | Timestamped pre-registration record. |
| `failure_events` (in `HCGRCState`) | Runtime gate-rejection signals Agent Evolution monitors for re-optimization. |
| `KICKOFF_READINESS.md` | Live backlog / Definition of Ready. |
