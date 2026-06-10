# ADR-0009: Local Observability Stack (No LangSmith)

**Status:** Accepted  
**Date:** 2026-06-10  
**Author:** Thomas Jones  
**Relates to:** ADR-0001 (LangGraph), ADR-0006 (Local-First), AGENT_WORKFLOW.md Section 8

---

## Context

HC-GRC requires observability for 48 agents executing multi-step LangGraph workflows. Observability needs include: distributed tracing across agent nodes, token usage per agent, latency per node, evaluation metrics, experiment parameter tracking, and artifact lineage.

The platform constraint is **local-first, data-sovereign** — no data, embeddings, traces, or results leave the machine. This eliminates SaaS-only observability tools.

**LangSmith is disqualified.** SaaS-only; no self-hosted option.

---

## Decision

**Local observability stack:**

| Layer               | Tool              | License      | Self-Hosted |
|---------------------|-------------------|--------------|-------------|
| Distributed tracing | Arize Phoenix     | Apache 2.0   | ✅ Yes       |
| Instrumentation     | OpenInference SDK | Apache 2.0   | ✅ Yes       |
| OTel transport      | OpenTelemetry     | Apache 2.0   | ✅ Yes       |
| Experiment tracking | MLflow (local)    | Apache 2.0   | ✅ Yes       |
| Provenance          | W3C PROV-DM       | W3C standard | ✅ Yes       |

---

## Rationale

### Why Arize Phoenix (not Langfuse, not custom)

**Langfuse** was the primary alternative. It is MIT-licensed, self-hostable, and OpenTelemetry-native. The deciding factor against Langfuse is evaluation capability: Phoenix brings Arize's ML observability heritage with deeper evaluation primitives than Langfuse — specifically per-trace LLM-as-judge evaluation, hallucination detection, and retrieval relevance scoring. For a scientific research platform where evaluation rigor is non-negotiable, Phoenix's evaluation depth tips the decision.

**Phoenix specifics relevant to HC-GRC:**
- LangGraph auto-instrumentation via `LangChainInstrumentor()` — zero configuration to capture all node traces
- Local-first: `px.launch_app()` starts a local server; no external connections
- OTLP endpoint at `/api/public/otel` accepts any OpenTelemetry-compatible trace
- Per-span token counts, latency, and LLM inputs/outputs captured automatically
- Embedded dataset and experiment management for prompt evaluation

### Why MLflow for Experiment Tracking

LangSmith's experiment tracking (prompt comparison, run comparison) is the primary feature that MLflow lacks. However, MLflow's artifact logging, parameter tracking, and run comparison are sufficient for HC-GRC's needs. MLflow runs fully locally (`mlflow server --host 127.0.0.1 --port 5000`) and integrates with the project's Python environment without cloud dependencies.

Phoenix handles the distributed tracing layer. MLflow handles the research experiment layer. These are complementary, not overlapping.

### OpenTelemetry as Integration Layer

Both Phoenix and MLflow support OpenTelemetry. This means if a better self-hosted backend emerges, traces can be rerouted without changes to the LangGraph instrumentation code. The OTEL SDK is the stable interface; the backend is swappable.

---

## Configuration

```python
# Observability bootstrap — called once at run start, before graph compilation

import phoenix as px
from openinference.instrumentation.langchain import LangChainInstrumentor
import mlflow

# ── Phoenix (local tracing) ──────────────────────────────────────
px_session = px.launch_app()  # Starts server at http://localhost:6006
LangChainInstrumentor().instrument()
# All LangGraph node invocations now emit OTLP traces automatically.
# No per-node instrumentation code required.

# ── MLflow (experiment tracking) ─────────────────────────────────
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("hc-grc-scf-analysis")

with mlflow.start_run(run_name=run_id):
    mlflow.log_params({
        "scf_version": scf_version,
        "hypothesis_count": len(hypotheses),
        "analysis_modules": "P1,P2,P3,P4,P5",
    })
    # Metrics are logged per-gate as the run progresses
```

---

## Consequences

**Positive:**
- Zero data egress — all traces, metrics, and artifacts stay on the local machine
- No SaaS dependency risk (pricing changes, API outages, acquisition events)
- OpenTelemetry as transport layer makes the backend swappable
- Phoenix evaluation primitives support scientific rigor requirements

**Negative:**
- No hosted UI — Phoenix and MLflow UIs require a running local server
- Team collaboration requires running Phoenix/MLflow on a shared local server or VPN
- Phoenix's LangGraph-specific views are less polished than LangSmith's (which was built specifically for LangGraph)

**Mitigation:**
- Single-machine execution model makes local-only acceptable for v0.1
- VPN-accessible shared server is straightforward if team grows

---

## Alternatives Considered and Rejected

| Tool            | Reason Rejected                                              |
|-----------------|--------------------------------------------------------------|
| LangSmith       | SaaS-only; no self-hosted option (ADR-0006)                  |
| Langfuse        | Self-hostable ✅; loses to Phoenix on evaluation depth        |
| W&B             | SaaS-only post-CoreWeave acquisition; rejected in ADR-0006   |
| OpenLLMetry     | Apache 2.0, vendor-neutral — **not rejected**; used as OTEL instrumentation layer where needed |
| Custom tracing  | Not justified; OpenTelemetry + Phoenix is well-maintained and production-tested |

---

## References

- [Arize Phoenix — What is Phoenix](https://arize.com/docs/phoenix)
- [Langfuse vs LangSmith — Langfuse](https://langfuse.com/faq/all/langsmith-alternative)
- [Top LangSmith Alternatives 2026 — SigNoz](https://signoz.io/comparisons/langsmith-alternatives/)
- [LLM Observability Platforms 2026 — Spheron](https://www.spheron.network/blog/llm-observability-gpu-cloud-langfuse-arize-phoenix-helicone/)
