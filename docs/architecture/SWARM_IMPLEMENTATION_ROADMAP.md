# HC-GRC Agent Swarm — Implementation Roadmap

**Status:** Active  
**Date:** 2026-06-10  
**Owner:** Thomas Jones  
**Relates to:** AGENT_WORKFLOW.md, ADR-0008, ADR-0009, CARDS_SPEC.md

---

## Guiding Principle

Agents do the work. This document is the specification they build from. The roadmap sequences implementation to maximize early feedback and de-risk the Gate 2 firewall before the full swarm is operational.

Build the skeleton before the body: get the graph compiling, gate nodes firing, and the checkpointer persisting before any analysis logic is implemented. The architecture is only real when Gate 2 actually blocks confirmatory execution.

---

## Phase 0: Infrastructure Foundation

**Objective:** Working LangGraph skeleton with PostgresSaver and Phoenix running locally. No analysis logic yet — the graph should compile, run, hit Gate 1, and pause.

**Deliverables:**

1. `src/infrastructure/tracking/` — MLflow local server setup script
2. `src/infrastructure/observability/` — Phoenix launch + LangChainInstrumentor bootstrap
3. `src/infrastructure/local-inference/` — Local LLM configuration (Ollama / vLLM)
4. PostgreSQL schema for checkpoints (run `checkpointer.setup()` once)
5. `HCGRCState` TypedDict with all reducers in `src/agents/orchestrator/`
6. Top-level `StateGraph` skeleton (all nodes registered, all edges wired, `pass` implementations)
7. Gate 1 node with `interrupt()` firing and `Command(resume=...)` resuming

**Success criteria:**
- `graph.invoke(initial_state, config)` compiles and runs
- Graph pauses at Gate 1 with correct payload in `result["__interrupt__"]`
- `graph.invoke(Command(resume="approve"), config)` resumes and reaches Gate 2
- PostgreSQL `checkpoints` table shows entries for the run thread

**Estimated complexity:** Medium — no LLM calls needed; stub nodes return hardcoded state.

---

## Phase 1: Data Pipeline (T-01, T-02)

**Objective:** Real data flowing into the graph. SCF XLSX acquired, DVC-tracked, loaded into state.

**Deliverables:**

1. T-01 Research subgraph — literature agent produces `literature_refs` in state
2. T-02 Data subgraph — data-acquisition agent downloads SCF XLSX to `data/01-raw/`, runs DVC tracking
3. `data/codebook.md` updated with actual field mappings
4. Gate 1 node receives real literature synthesis payload, not stub
5. `data_manifest` in state points to real DVC-tracked artifact

**Success criteria:**
- End-to-end run from START through Gate 1 approval to Gate 2 pause with real data
- `data/01-raw/SCF/` contains locked SCF XLSX
- `data_manifest["sha256"]` matches the file on disk

---

## Phase 2: Hypothesis & SAP (T-05, Gate 2)

**Objective:** Gate 2 firewall operational. Pre-registration complete before any analysis runs.

**Deliverables:**

1. T-05 Hypothesis subgraph — formalizes hypotheses into `hypotheses` state key
2. SAP document (`docs/protocol/03_statistical_analysis_plan.md`) filled out by T-05 agent
3. `PREREGISTRATION_LEDGER.md` updated with Gate 2 approval event
4. Gate 2 node: data split computed, test set physically locked, interrupt fires
5. Stale-state guard in Gate 2 node (re-validates split hash on resume)

**Success criteria:**
- Gate 2 `interrupt()` payload contains hypotheses, SAP link, and split manifest
- After `Command(resume="approve")`, `data_manifest["locked"] == True`
- Confirmatory agents are not reachable without Gate 2 approval (conditional edge test)
- Gate 2 rejection routes back to T-05 for hypothesis revision (not implemented yet — add conditional routing)

**This is the most critical phase.** Gate 2 must be correct before any analysis is built on top of it. A broken Gate 2 means exploratory data contaminates confirmatory tests.

---

## Phase 3: Analysis Fan-Out (T-03, P1–P5)

**Objective:** Five analysis modules running in parallel. Real outputs flowing into state.

**Deliverables (in parallel — these are independent):**

| Module | Subgraph | Agents | Output Key |
|--------|----------|--------|------------|
| P1 | p1-strm-nlp | strm-nlp-agent, embedding-agent | `p1_results` |
| P2 | p2-topology | control-topology-agent | `p2_results` |
| P3 | p3-convergence | convergence-agent | `p3_results` |
| P4 | p4-blindspot | blindspot-agent | `p4_results` |
| P5 | p5-ai-governance | ai-governance-agent | `p5_results` |

**Fan-out implementation:**
- `dispatch_analysis()` function returns `list[Send]` for all five modules
- Each module writes to its reducer-annotated state key
- Per-module fan-out (map-reduce over control batches) implemented for P1, P2, P4
- Fan-in aggregation node in T-03 fires after all five complete

**Success criteria:**
- All five modules fire in the same superstep (verify via Phoenix trace showing concurrent node execution)
- A P3 failure produces a null result entry, does not cancel P1/P2/P4/P5
- `p1_results` through `p5_results` all populated in state before T-04 receives control

---

## Phase 4: Statistical Analysis and Gates 3–4 (T-04, T-09)

**Objective:** Confirmatory statistical tests run against pre-registered hypotheses. Results gated by human review.

**Deliverables:**

1. T-04 Statistical subgraph — hypothesis tests against locked test split
2. Gate 3 node — human reviews statistical results before evaluation
3. T-09 Evaluation subgraph — benchmark metrics, effect sizes, null result logging
4. Gate 4 node — human approves evaluation before manuscript proceeds
5. Null results logged to `reports/null-results/` regardless of Gate 3/4 outcome

**Success criteria:**
- Statistical tests reference only `data/03-processed/test/` (never train split)
- Each hypothesis test result has a corresponding ARA artifact entry
- Gate 3 payload includes test statistics, p-values, effect sizes, and CIs for all hypotheses
- Null results are not suppressed — any rejected hypothesis produces a null result record

---

## Phase 5: Reporting and Gate 5 (T-11, T-14)

**Objective:** Manuscript and ARA artifacts complete. Gate 5 gates final publication.

**Deliverables:**

1. T-11 Reporting subgraph — generates `manuscript/` draft and ARA deliverables
2. T-14 Documentation subgraph — updates AGENT_WORKFLOW.md with compiled graph topology diagram
3. Gate 5 node — human approves final manuscript before external publication
4. `reproducibility/` populated with full reproduction package

**Success criteria:**
- `manuscript/` contains complete draft (LaTeX + compiled PDF via ml-paper-writing skill)
- ARA deliverables in `ara/` are complete and externally consumable
- `reproducibility/` contains all code, configs, and instructions to reproduce the study
- Gate 5 approval logged to `PREREGISTRATION_LEDGER.md` with timestamp

---

## Phase 6: Support Infrastructure (T-06 through T-16)

**Objective:** Hardening, monitoring, QA, provenance, and code review infrastructure.

**Deliverables:**

1. T-12 QA subgraph — property-based tests (`tests/property-based/`) for state integrity
2. T-13 Provenance subgraph — W3C PROV-DM trace completeness validation
3. T-16 GateWatchdog — abandoned gate expiry job (72-hour TTL)
4. T-15 Code Review subgraph — reviews all generated scripts before first execution
5. `tools/generate_docs.py` spec (task #30) — parser for auto-generating HANDOFFS.md, CONTRACTS.md, etc.

---

## Implementation Sequence (Dependency Graph)

```
Phase 0 ──► Phase 1 ──► Phase 2 (Gate 2) ──► Phase 3 (fan-out P1-P5)
                                                    │
                                                    └──► Phase 4 (stats + Gate 3-4)
                                                                │
                                                                └──► Phase 5 (manuscript + Gate 5)

Phase 6 runs in parallel with Phases 1-5 (support infrastructure is built as needed)
```

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Gate 2 firewall bypass | Low | Critical | Conditional edge test in Phase 2; no path from T-05 to T-04 without Gate 2 approval |
| State key collision in parallel fan-out | Medium | High | All collector keys use `Annotated[list[...], add]`; validated in Phase 3 unit tests |
| Checkpoint bloat (large SCF state) | Medium | Medium | Trim message history before interrupt; store ARA artifacts as file paths, not inline |
| Phoenix traces filling local disk | Low | Low | Log rotation on Phoenix storage; keep last 30 days |
| LLM token budget exceeded per run | Medium | Medium | MLflow tracks per-run token consumption; alert if run exceeds 5M tokens |
| Abandoned Gate 2 (researcher unavailable) | Medium | Low | GateWatchdog (Phase 6) sends reminders; 7-day auto-expiry |

---

## Known Pending Decisions

These questions were not resolved by the research in this session. They require a separate decision loop before Phase 3 implementation:

1. **Local LLM vs API:** Which model backs the analysis agents? Local Ollama (data-sovereign, slower) vs API (faster, data leaves machine)? The data-sovereign constraint from ADR-0006 suggests local — but 1,400 controls × 5 analysis modules is a significant compute load.

2. **Per-control batch size for P1 map-reduce:** What is the optimal `batch_size` for `chunk_controls()`? Too small → too many parallel branches → rate limits. Too large → long per-branch execution → latency equivalent to sequential.

3. **Gate UI:** How does the human receive and respond to gate interrupts? CLI, web UI, or Slack bot? The current architecture is agnostic — any of the three work. A decision should be made before Phase 2.

4. **Confirmatory test suite lock:** Which statistical tests are pre-registered for which hypotheses? This must be specified in the SAP before Gate 2 — the SAP being blank is intentional (ADR deferred until Gate 2), but the agent building the SAP needs a template. See task #29 (SAP deferral header).

---

---

## Tier 2: Comparative Analysis — Deferred (Future: `hc-grc-comparative`)

**Prerequisite:** Two or more Tier 1 framework projects completed with ARA artifacts exported.

**Objective:** Cross-framework knowledge graph synthesis. Ingest all Tier 1 outputs and answer questions that no single framework study can: where do GRC frameworks genuinely converge, where do they conflict, and which controls are empirically load-bearing across all of them?

**Architecture:** Mirrors this project's architecture exactly — same LangGraph topology, same gate structure, same ARA artifact format. Inputs are the exported knowledge graphs from each Tier 1 project (JSON/Parquet format, consumed via DVC remote). Workers differ: comparator agents replace framework-specific analysis agents.

**Phases:**

- **Phase T2-0:** Infrastructure — DVC remote configured to receive Tier 1 ARA artifacts; cross-graph schema validator implemented; PostgresSaver database provisioned for comparative runs
- **Phase T2-1:** Graph ingestion — ingest and validate all Tier 1 knowledge graphs; node alignment across framework vocabularies (functionally equivalent control identification)
- **Phase T2-2:** Gap analysis — compute coverage maps; which risk areas are addressed by some frameworks and absent from others
- **Phase T2-3:** Alignment / misalignment scoring — test SCF's mapping claims cross-framework; where claimed equivalence holds empirically and where it fails
- **Phase T2-4:** Centrality and importance ranking — graph centrality across the combined multi-framework graph; empirically load-bearing controls identified
- **Phase T2-5:** Blast radius modeling — information cascade / graph diffusion; simulate control failure propagation across the cross-framework topology
- **Phase T2-6:** Archetype discovery — dimensionality reduction across graph embedding space; cluster the GRC landscape into underlying control archetypes
- **Phase T2-7:** Reporting — manuscript, ARA deliverables, visualization package

**Key open questions at Tier 2 start:**
- Node alignment algorithm selection: exact string match, embedding similarity, or hybrid? (STRM mappings provide a starting alignment but will have gaps)
- Blast radius model: independent cascade model vs. Linear Threshold model vs. custom? Choice depends on what empirical data Tier 1 produces about control dependency types
- Archetype target: how many archetypes is the right k? Pre-register a range; data decides

---

## Tier 3: Organizational Impact Modeling — Deferred (Future: `hc-grc-impact`)

**Prerequisite:** Tier 2 complete. Tier 3 also requires external data (breach databases, financial loss records, organizational control posture data) with associated privacy, consent, and licensing requirements that are outside the current scope.

**Objective:** The commercially significant tier. Model the findings from Tiers 1–2 against real organizations to quantify: which control failures drive financial losses, and by how much?

**Status: DO NOT IMPLEMENT.** Tier 3 requires data licensing, privacy review, and consent framework design before any code is written. This tier is documented here to ensure Tier 1 and Tier 2 design decisions are made with Tier 3 as a downstream consumer.

**Phases (structural only — no implementation timeline):**

- **Phase T3-0:** Data acquisition and ethics — identify and license appropriate breach and loss datasets; design organizational parameterization consent model
- **Phase T3-1:** Feature engineering — control posture → feature vectors; gap severity scores from Tier 2 as features; organizational parameters as covariates
- **Phase T3-2:** Causal inference — causal forests and do-calculus to establish which control gaps causally drive financial outcomes (not just correlated)
- **Phase T3-3:** Predictive modeling — LightGBM/XGBoost with SHAP explainability; survival analysis for time-to-breach; Monte Carlo for loss quantification with confidence intervals
- **Phase T3-4:** Organizational parameterization — industry, size, geography, existing framework portfolio as model inputs; organization-specific output generation
- **Phase T3-5:** Validation and calibration — backtesting against historical breach/loss data; actuarial review
- **Phase T3-6:** Reporting and product pathway — findings document, SHAP visualization layer, API design for the organizational assessment product

**Design requirements Tier 1 and 2 must satisfy for Tier 3:**
- ARA artifact schema must include confidence scores on all findings (Tier 3 uses these as model features)
- Null results must be structured identically to positive findings (Tier 3 uses the full result distribution, not just confirmed findings)
- Blast radius scores from Tier 2 must be in a format compatible with ML feature extraction (numeric, normalized, with provenance)

---

## Sources

- [LangGraph 1.0 GA](https://blog.langchain.com/langchain-langgraph-1dot0/)
- [HITL Workflows — AbstractAlgorithms](https://www.abstractalgorithms.dev/langgraph-human-in-the-loop)
- [Scaling LangGraph — AI Practitioner](https://aipractitioner.substack.com/p/scaling-langgraph-agents-parallelization)
- [Swarm vs Supervisor — Augment Code](https://www.augmentcode.com/guides/swarm-vs-supervisor)
- [Fan-Out/Fan-In — markaicode](https://markaicode.com/langgraph-parallel-fan-out-fan-in/)
- [LangGraph Supervisor GitHub](https://github.com/langchain-ai/langgraph-supervisor-py)
- [PostgresSaver — PyPI](https://pypi.org/project/langgraph-checkpoint-postgres/)
- [Arize Phoenix Self-Hosted](https://arize.com/docs/phoenix)
