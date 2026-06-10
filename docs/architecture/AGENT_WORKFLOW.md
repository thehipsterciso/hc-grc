# Agent Workflow Architecture

**HC-GRC | LangGraph Topology Document**  
**Status:** Authoritative  
**Relates to:** ADR-0001 (LangGraph), ADR-0008 (Supervisor+Hybrid), ADR-0009 (Local Observability), ADR-0010 (Three-Tier Program), ADR-0011 (Resilience)  
**Required for:** NeurIPS 2026 reproducibility disclosure

> **Program Context:** This document describes the agent workflow for Tier 1 of a three-tier research program (see ADR-0010). The workflow architecture and ARA artifact schemas defined here are shared across all future Tier 1 framework projects. They are designed as the data interface that Tier 2 (`hc-grc-comparative`) will consume. Any change to the ARA artifact schema or state key structure requires evaluating impact on Tier 2 ingestion.

---

## 1. Overview

HC-GRC is a 48-agent, 17-team autonomous research platform built on LangGraph 1.0 (GA: October 22, 2025). The platform executes a multi-phase empirical study of the Secure Controls Framework (SCF) across five analysis modules (P1–P5), enforcing an exploratory/confirmatory firewall at Gate 2 that is structural rather than procedural.

This document describes the full LangGraph graph topology: agent nodes, edges, team subgraphs, interrupt() gate positions, state schema, fan-out/fan-in execution patterns, human-in-the-loop sequences, and the PostgresSaver persistence layer.

**Agents do the work. This document describes what they will build.**

---

## 2. Architecture Pattern: Supervisor + Hybrid

### 2.1 Decision

HC-GRC uses a **supervisor-with-subgraph hybrid** pattern, not a pure swarm. See ADR-0008 for full rationale.

At the macro level: a top-level `OrchestratorSupervisor` (Team 00) routes to 16 subordinate team subgraphs. Each team subgraph is a self-contained `StateGraph` compiled as a node in the parent graph. Analysis teams (03–04) use **fan-out/fan-in parallel execution** within their subgraphs. Gate teams (16) use **interrupt()** to enforce human approval before the workflow advances.

### 2.2 Pattern Comparison (Why Not Pure Swarm)

| Dimension                  | HC-GRC Requirement                          | Swarm | Supervisor+Hybrid |
|----------------------------|---------------------------------------------|-------|-------------------|
| Task interdependency       | High — Gate 2 firewall enforces ordering    | ❌    | ✅                |
| Intermediate validation    | Required at 5 gates                         | ❌    | ✅                |
| Exploratory/confirmatory   | Gate must be structurally enforced          | ❌    | ✅                |
| P1–P5 parallel execution   | P1–P5 modules are logically independent post-Gate 2 | partial | ✅ |
| Context window             | 1,400+ controls exceed single LLM context  | ❌    | ✅                |
| Error isolation            | Team failure must not cascade to other teams | ❌    | ✅                |
| Audit trail / provenance   | Every decision must be traceable            | ❌    | ✅                |

---

## 3. Team Topology

### 3.1 Team Registry

| Team | ID   | Name                         | Pattern           | Gate  |
|------|------|------------------------------|-------------------|-------|
| 00   | T-00 | Orchestration                | Top supervisor    | —     |
| 01   | T-01 | Research & Literature        | Sequential        | Gate 1|
| 02   | T-02 | Data Acquisition & Curation  | Sequential        | —     |
| 03   | T-03 | Analysis (P1–P5)             | Fan-out parallel  | —     |
| 04   | T-04 | Statistical Analysis         | Sequential        | Gate 3|
| 05   | T-05 | Hypothesis Management        | Sequential        | Gate 2|
| 06   | T-06 | Training & Fine-tuning       | Sequential        | —     |
| 07   | T-07 | Optimization                 | Sequential        | —     |
| 08   | T-08 | Infrastructure               | Sequential        | —     |
| 09   | T-09 | Evaluation                   | Fan-out parallel  | Gate 4|
| 10   | T-10 | Safety & Compliance          | Sequential        | —     |
| 11   | T-11 | Reporting & Communication    | Sequential        | —     |
| 12   | T-12 | Quality Assurance            | Sequential        | —     |
| 13   | T-13 | Provenance & Versioning      | Sequential        | —     |
| 14   | T-14 | Documentation                | Sequential        | —     |
| 15   | T-15 | Code Review                  | Sequential        | —     |
| 16   | T-16 | Gate Enforcement             | interrupt() nodes | All 5 |

### 3.2 Macro Graph (Top-Level)

```
START
  └─► T-00 OrchestratorSupervisor
        ├─► T-01 ResearchSubgraph ──────────────────── Gate 1 ──►
        │         └─► T-02 DataSubgraph ──────────────────────────►
        │                   └─► T-05 HypothesisSubgraph ──── Gate 2 (FIREWALL) ──►
        │                             └─► T-03 AnalysisSubgraph [fan-out P1-P5] ──►
        │                                       └─► T-04 StatisticsSubgraph ── Gate 3 ──►
        │                                                 └─► T-09 EvaluationSubgraph ── Gate 4 ──►
        │                                                           └─► T-11 ReportingSubgraph ── Gate 5 ──►
        │                                                                     └─► END
        └─► T-08/T-07/T-06/T-10/T-12/T-13/T-14/T-15 (support subgraphs, invoked on-demand)
```

T-16 (Gate Enforcement) is not a sequential node in the flow — it is a cross-cutting concern. Its `interrupt()` nodes are embedded within the subgraphs where each gate fires.

---

## 4. State Schema

### 4.1 Top-Level State (`HCGRCState`)

All state flows through a single typed dictionary. Subgraphs share keys by convention; isolated state for internal subgraph use uses private keys prefixed with `_team_XX_`.

```python
from typing import Annotated, TypedDict, Optional
from operator import add
from datetime import datetime

class HCGRCState(TypedDict):
    # ── Execution control ──────────────────────────────────────────
    run_id: str                               # UUID, set at START, immutable
    phase: str                                # current phase label
    gate_status: dict[str, str]               # gate_id → "pending"|"approved"|"rejected"

    # ── Research artifacts (append-only via reducer) ───────────────
    hypotheses: Annotated[list[dict], add]    # pre-registered hypotheses
    literature_refs: Annotated[list[dict], add]
    data_manifest: dict                       # DVC manifest pointer

    # ── Analysis results (fan-out collectors) ──────────────────────
    p1_results: Annotated[list[dict], add]    # P1: STRM NLP
    p2_results: Annotated[list[dict], add]    # P2: Control Topology
    p3_results: Annotated[list[dict], add]    # P3: Regulatory Convergence
    p4_results: Annotated[list[dict], add]    # P4: Risk Blindspot
    p5_results: Annotated[list[dict], add]    # P5: AI Governance
    statistical_results: dict                  # post-Gate 3 confirmatory outputs

    # ── Provenance ─────────────────────────────────────────────────
    prov_trace: Annotated[list[dict], add]    # W3C PROV-DM events (append only)
    ara_artifacts: Annotated[list[str], add]  # paths to ARA artifact files

    # ── Human gate payloads ────────────────────────────────────────
    gate_payloads: dict[str, dict]            # gate_id → payload shown to human
    gate_decisions: dict[str, str]            # gate_id → human decision

    # ── Error / null results ───────────────────────────────────────
    null_results: Annotated[list[dict], add]
    errors: Annotated[list[dict], add]
```

**Key design choices:**

- `Annotated[list[..], add]` on every collector that parallel branches write to. Without this reducer, the last parallel branch's write silently overwrites all others.
- `gate_status` and `gate_decisions` are plain dicts (written sequentially by T-16 after each interrupt).
- `prov_trace` is append-only. No agent ever modifies an existing provenance record.

---

## 5. Human-in-the-Loop Gates

### 5.1 Gate Architecture

HC-GRC enforces five human approval gates using LangGraph's `interrupt()` / `Command(resume=...)` pattern. A persistent `PostgresSaver` checkpointer is mandatory — without it, frozen state cannot survive process restarts.

**Gate positions:**

| Gate | Phase                        | Trigger Condition                               | Blast Radius if Skipped        |
|------|------------------------------|--------------------------------------------------|-------------------------------|
| 1    | Post-literature review       | Literature synthesis complete; SAP draft ready   | Wrong research questions locked in |
| 2    | Pre-confirmatory analysis    | **FIREWALL** — test split physically locked here | Exploratory contamination of confirmatory set |
| 3    | Post-statistical analysis    | All hypothesis tests complete                    | False inference advances to manuscript |
| 4    | Post-evaluation              | Final benchmark results available                | Flawed results cited in paper |
| 5    | Pre-publication              | Manuscript and ARA artifacts ready               | Non-reproducible research published |

### 5.2 Gate 2 as Structural Firewall

Gate 2 is not a soft checkpoint. It is the architectural boundary between the exploratory and confirmatory phases. The data split node in T-05 physically separates the test set **before** calling `interrupt()`. The confirmatory analysis agents (T-04 statistical tests) are not dispatched until `Command(resume="approve")` is received.

```python
from langgraph.types import interrupt, Command

def gate_2_node(state: HCGRCState) -> dict:
    """
    CRITICAL: Do not move test split to after the interrupt.
    The split must happen BEFORE the pause so that the human
    cannot inadvertently influence what goes into the test set.
    The split is pure computation (idempotent), safe before interrupt().
    """
    # Pure computation — safe before interrupt(), will re-run on resume but idempotent
    split_manifest = compute_data_split(state["data_manifest"])

    # Graph pauses here. Human reviews: hypotheses, SAP, proposed test split.
    decision = interrupt({
        "gate": "gate_2",
        "message": "Review pre-registration packet. Approve to lock test split and proceed to confirmatory analysis.",
        "hypotheses": state["hypotheses"],
        "data_split_manifest": split_manifest,
        "sap_document": "docs/protocol/03_statistical_analysis_plan.md",
        "warning": "Approving this gate is IRREVERSIBLE. The test split will be physically locked.",
    })

    if decision != "approve":
        return {
            "gate_status": {**state["gate_status"], "gate_2": "rejected"},
            "gate_decisions": {**state["gate_decisions"], "gate_2": decision},
        }

    return {
        "gate_status": {**state["gate_status"], "gate_2": "approved"},
        "gate_decisions": {**state["gate_decisions"], "gate_2": decision},
        "data_manifest": {**state["data_manifest"], "test_split": split_manifest, "locked": True},
    }
```

### 5.3 Production HITL Requirements

All five gates run against a persistent PostgresSaver. `MemorySaver` is prohibited outside unit tests.

**Failure modes HC-GRC must mitigate:**

1. **Abandoned gate (never resumed):** Background job scans for threads where `gate_status` is `"pending"` and `updated_at` is older than 72 hours. Sends reminder notification. After 7 days, marks thread `"expired"` and logs to null results.

2. **Stale state on late resume:** After Gate 2 approval, the confirmatory analysis node re-validates that the data manifest hash matches what was displayed in the gate payload before proceeding.

3. **Node re-entry side effects:** All code before `interrupt()` in any gate node is pure computation. Side effects (DVC lock, filesystem writes) occur after the interrupt returns.

4. **Multiple sequential interrupts:** Gate nodes contain exactly one `interrupt()` call each. The UI layer must handle the queue gracefully — later gates are not rendered until earlier ones are approved.

---

## 6. Fan-Out / Fan-In: Analysis Subgraph (T-03)

### 6.1 Pattern

P1 through P5 are logically independent modules. They share the same input data (the locked SCF dataset) but do not require each other's outputs to proceed. This is the canonical use case for LangGraph fan-out.

T-03 dispatches all five analysis modules in a single superstep. Wall-clock time for the analysis phase is bounded by the slowest module, not the sum of all five.

### 6.2 Static Fan-Out (Fixed Modules)

```python
from langgraph.types import Send

def dispatch_analysis(state: HCGRCState) -> list[Send]:
    """Fan-out: dispatch all 5 analysis modules in parallel."""
    modules = [
        ("p1_strm_nlp",      {"module": "P1", **state}),
        ("p2_topology",      {"module": "P2", **state}),
        ("p3_convergence",   {"module": "P3", **state}),
        ("p4_blindspot",     {"module": "P4", **state}),
        ("p5_ai_governance", {"module": "P5", **state}),
    ]
    return [Send(node, module_state) for node, module_state in modules]
```

Each analysis node writes to its dedicated results key (`p1_results`, `p2_results`, etc.) with `Annotated[list[dict], add]` reducers. The fan-in aggregation node fires after all five complete.

### 6.3 Per-Module Fan-Out (Map-Reduce over Controls)

Within P1, the 1,400+ SCF controls are processed in parallel using the `Send` API. The number of control batches is not known at build time — it depends on the SCF data loaded at runtime.

```python
def dispatch_p1_controls(state: dict) -> list[Send]:
    """Map over control batches. Each batch → independent subgraph run."""
    batches = chunk_controls(state["controls"], batch_size=50)
    return [
        Send("analyze_control_batch", {"batch": batch, "p1_results": [], "module": "P1"})
        for batch in batches
    ]
```

This map-reduce pattern is used in P1 (NLP similarity), P2 (graph topology), and P4 (risk blindspot). P3 and P5 operate at the framework level rather than the control level and use static fan-out over regulatory frameworks.

### 6.4 State Isolation vs Shared State

Team subgraphs use **isolated state** for internal processing (private to the team's subgraph) and **shared state** for outputs (surfaced to the parent graph via shared state keys).

The boundary contract is explicit: a team subgraph's final node writes to the parent-visible keys (`p1_results`, `ara_artifacts`, `prov_trace`) and does not expose its internal intermediate state to the orchestrator.

---

## 7. PostgresSaver Checkpointing

### 7.1 Configuration

```python
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection

def build_checkpointer() -> PostgresSaver:
    conn = Connection.connect(
        "postgresql://hcgrc_agent:***@localhost:5432/hcgrc_checkpoints",
        autocommit=True,
        row_factory=dict_row,
    )
    checkpointer = PostgresSaver(conn)
    checkpointer.setup()  # Creates required tables on first run only
    return checkpointer
```

**Required on first run:** `checkpointer.setup()` creates the `checkpoints`, `checkpoint_blobs`, and `checkpoint_writes` tables. Idempotent on subsequent runs.

### 7.2 Thread ID Strategy

Each research run gets a unique thread ID. Gate sequences within a run share the same thread ID so the checkpointer can restore frozen state across gate pauses.

```python
import uuid

run_id = str(uuid.uuid4())
config = {
    "configurable": {
        "thread_id": run_id,
        "run_metadata": {
            "project": "hc-grc",
            "version": "0.1.0",
            "initiated_by": "thomas@hcgrc",
        }
    }
}
```

Sub-agent threads (for per-control map-reduce tasks) use `f"{run_id}::p1::{batch_idx}"` — scoped to the parent run, unique per batch.

### 7.3 Time Travel and Debugging

PostgresSaver supports state inspection at any past checkpoint:

```python
# Get current state
snapshot = graph.get_state(config)

# List all checkpoints for a run
history = list(graph.get_state_history(config))

# Replay from a specific checkpoint (debugging, re-analysis)
past_config = history[3].config
graph.invoke(None, past_config)
```

Gate 2 approval is an irreversible operational decision. Time travel to replay from before Gate 2 for debugging purposes is permitted in development but logged to INCIDENTS.md in any production replay.

---

## 8. Local Observability Stack

LangSmith is disqualified (SaaS-only). The local stack:

| Layer               | Tool              | Purpose                                    |
|---------------------|-------------------|--------------------------------------------|
| Tracing             | Arize Phoenix     | OTLP traces for all LangGraph nodes; local-first |
| Metrics             | OpenTelemetry SDK | Spans, latency, token counts               |
| Experiment tracking | MLflow (local)    | Run parameters, metrics, artifact lineage  |
| Provenance          | W3C PROV-DM       | Canonical vocabulary; Turtle serialization |

**Phoenix configuration (local):**

```python
import phoenix as px
from openinference.instrumentation.langchain import LangChainInstrumentor

# Start local Phoenix server (runs in-process or as a sidecar)
session = px.launch_app()

# Instrument LangChain/LangGraph — captures all node traces automatically
LangChainInstrumentor().instrument()

# All LangGraph invocations now emit OTLP traces to the local Phoenix server
# Phoenix UI available at http://localhost:6006
```

No data leaves the machine. Phoenix stores traces locally. MLflow experiment tracking also runs locally (`mlflow server --host 127.0.0.1`).

See ADR-0009 for the full observability stack decision.

---

## 9. Error Handling and Fault Tolerance

### 9.1 Superstep Atomicity

If any node in a parallel superstep raises an unhandled exception, the entire superstep fails atomically. Results from successfully completed branches in that superstep are preserved in the checkpoint but not committed to the parent state until all branches succeed.

Implication: each analysis node (P1–P5) must catch its own exceptions and return a sentinel value (a null result entry) rather than propagating exceptions. This prevents one failing analysis module from canceling the other four.

```python
def p1_strm_nlp(state: dict) -> dict:
    try:
        results = run_p1_analysis(state)
        return {"p1_results": results, "prov_trace": [build_prov_event("P1_COMPLETE")]}
    except Exception as e:
        return {
            "p1_results": [],
            "null_results": [{"module": "P1", "reason": str(e), "timestamp": now()}],
            "errors": [{"module": "P1", "exception": str(e)}],
        }
```

### 9.2 Retry Strategy (v1.1 Middleware)

LangGraph 1.1 (December 2025) introduced model retry middleware with configurable exponential backoff. This is the preferred retry mechanism for transient LLM API failures.

```python
from langgraph.middleware import RetryMiddleware

graph = builder.compile(
    checkpointer=checkpointer,
    middleware=[RetryMiddleware(max_retries=3, backoff_factor=2.0)],
)
```

### 9.3 Abandoned Gate Recovery

A background process (T-16 GateWatchdog) polls the checkpointer for threads in `pending` gate state older than 72 hours. It does not auto-approve or auto-reject — it sends a reminder. After 7 days without a response, it logs to `null_results/abandoned_runs/` and marks the thread `expired`.

---

## 10. Graph Compilation

```python
from langgraph.graph import StateGraph, START, END

def build_hcgrc_graph(checkpointer: PostgresSaver) -> CompiledGraph:
    builder = StateGraph(HCGRCState)

    # Register all team subgraphs as nodes
    builder.add_node("t01_research",    build_research_subgraph())
    builder.add_node("t02_data",        build_data_subgraph())
    builder.add_node("t05_hypothesis",  build_hypothesis_subgraph())
    builder.add_node("t03_analysis",    build_analysis_subgraph())   # fan-out P1-P5
    builder.add_node("t04_statistics",  build_statistics_subgraph())
    builder.add_node("t09_evaluation",  build_evaluation_subgraph())
    builder.add_node("t11_reporting",   build_reporting_subgraph())

    # Gate nodes (interrupt() wrappers, part of T-16)
    builder.add_node("gate_1", gate_1_node)
    builder.add_node("gate_2", gate_2_node)
    builder.add_node("gate_3", gate_3_node)
    builder.add_node("gate_4", gate_4_node)
    builder.add_node("gate_5", gate_5_node)

    # Primary pipeline edges
    builder.add_edge(START,              "t01_research")
    builder.add_edge("t01_research",     "gate_1")
    builder.add_edge("gate_1",           "t02_data")
    builder.add_edge("t02_data",         "t05_hypothesis")
    builder.add_edge("t05_hypothesis",   "gate_2")      # FIREWALL
    builder.add_edge("gate_2",           "t03_analysis")
    builder.add_edge("t03_analysis",     "t04_statistics")
    builder.add_edge("t04_statistics",   "gate_3")
    builder.add_edge("gate_3",           "t09_evaluation")
    builder.add_edge("t09_evaluation",   "gate_4")
    builder.add_edge("gate_4",           "t11_reporting")
    builder.add_edge("t11_reporting",    "gate_5")
    builder.add_edge("gate_5",           END)

    return builder.compile(checkpointer=checkpointer)
```

Support subgraphs (T-06 through T-15) are invoked by individual nodes within the primary pipeline where needed, not wired as top-level pipeline nodes. This keeps the primary execution path legible and the graph compilation deterministic.

---

## 11. Graph Visualization

Once the graph is compiled, generate a Mermaid diagram for the docs:

```python
# Generates a Mermaid diagram of the compiled graph
print(graph.get_graph().draw_mermaid())

# For subgraph introspection
print(graph.get_graph(xray=True).draw_mermaid())
```

The full compiled Mermaid diagram is to be committed to `docs/architecture/graph_topology.mermaid` by the T-14 documentation agent after initial build.

---

## 12. Sources

| Source | Relevance |
|--------|-----------|
| [LangGraph 1.0 GA Announcement](https://blog.langchain.com/langchain-langgraph-1dot0/) | v1.0 release, feature set |
| [LangGraph Hierarchical Agent Teams](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/hierarchical_agent_teams/) | Team subgraph patterns |
| [HITL with interrupt() — AbstractAlgorithms](https://www.abstractalgorithms.dev/langgraph-human-in-the-loop) | Full interrupt/Command/update_state lifecycle |
| [Scaling LangGraph — AI Practitioner](https://aipractitioner.substack.com/p/scaling-langgraph-agents-parallelization) | Parallelization, subgraphs, map-reduce, Send API |
| [Swarm vs Supervisor — Augment Code](https://www.augmentcode.com/guides/swarm-vs-supervisor) | Architecture pattern decision framework |
| [Fan-Out/Fan-In Patterns — markaicode](https://markaicode.com/langgraph-parallel-fan-out-fan-in/) | Reducer design, Send API, superstep mechanics |
| [langgraph-checkpoint-postgres · PyPI](https://pypi.org/project/langgraph-checkpoint-postgres/) | PostgresSaver setup |
| [Arize Phoenix Docs](https://arize.com/docs/phoenix) | Local OTLP observability |
| [LangSmith Alternatives — SigNoz](https://signoz.io/comparisons/langsmith-alternatives/) | Observability stack comparison |
