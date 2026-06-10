# ADR-0001: LangGraph as Primary Orchestration Framework

**Status:** Accepted
**Date:** 2026-06-09
**Deciders:** Thomas Jones

---

## Context

HC-GRC requires a multi-agent orchestration framework that can enforce five mandatory human approval gates — structurally, not as advisory checks. The gates must be impossible to bypass at the code level, not just convention. The platform also requires durable checkpointing so pipeline runs can be interrupted, inspected, and resumed without data loss. Evaluation criteria: human-in-the-loop enforcement, checkpointing, Python ecosystem, local deployment, active maintenance.

## Decision

Use LangGraph 1.0 as the primary orchestration framework. Human approval gates are implemented as `interrupt()` / `Command(resume=...)` calls in the Orchestrator node. Durable checkpointing uses `PostgresSaver` backed by the local PostgreSQL service. The five gate topology is defined at graph construction time — it is structural, not conditional.

## Alternatives Considered

**CrewAI:** Role-based, sequential execution model. Human-in-the-loop is a flag, not a graph node — it cannot enforce gate topology at the structural level. Eliminated.

**AutoGPT / MetaGPT:** Autonomous-first architectures. Both treat human review as optional. Eliminated on fundamental mismatch with the scientific rigor requirements of the platform.

**Custom LangChain chains:** No built-in graph topology or checkpointing. Would require reimplementing what LangGraph provides. Eliminated.

**Prefect / Airflow:** Workflow orchestrators not designed for LLM agent patterns. No native support for LLM-to-LLM delegation or structured human review at the gate level. Eliminated.

## Consequences

**Positive:**
- Five gates are structurally enforced — the graph cannot route past a gate without a `Command(resume=...)` response
- PostgresSaver checkpointing enables replay and audit
- LangGraph's `checkpoint_ns` semantics allow subgraph-level provenance
- Active development with Anthropic partnership; `interrupt()` API is stable in 1.0

**Negative:**
- LangGraph 1.x API may evolve; gate implementations need monitoring for deprecations
- PostgresSaver adds a PostgreSQL service dependency; mitigated by local Docker deployment
- `interrupt()` engineering rules (GATES.md §Engineering Requirements) must be followed precisely or replay integrity breaks silently

**Constraints introduced:**
- All gate nodes must follow the four interrupt() engineering rules documented in GATES.md
- `durability: "sync"` is required for PostgresSaver on gate nodes
