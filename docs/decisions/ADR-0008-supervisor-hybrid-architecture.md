# ADR-0008: Supervisor + Hybrid Architecture for Multi-Agent Orchestration

**Status:** Accepted  
**Date:** 2026-06-10  
**Author:** Thomas Jones  
**Relates to:** ADR-0001 (LangGraph), AGENT_WORKFLOW.md

---

## Context

HC-GRC deploys 48 agents across 17 teams to execute an empirical research study of the Secure Controls Framework. The agents must enforce a strict exploratory/confirmatory firewall (Gate 2), validate results at 5 human approval checkpoints, process 1,400+ controls (which exceed a single LLM context window), and execute five logically independent analysis modules (P1–P5) without each module blocking the others.

Three multi-agent orchestration patterns were evaluated:

1. **Pure Swarm** — routing intelligence distributed across agents; agents hand off peer-to-peer without a central coordinator
2. **Flat Supervisor** — single coordinator routes to all worker agents; sequential dispatch
3. **Supervisor + Hybrid (Subgraphs)** — hierarchical supervisor coordinates team-level subgraphs; fan-out parallelism within subgraphs

---

## Decision

**Supervisor + Hybrid (Subgraphs)**

---

## Rationale

### Why Not Pure Swarm

A swarm pattern is the wrong match for HC-GRC's task structure on four dimensions:

**Ordered execution is mandatory.** The exploratory/confirmatory firewall at Gate 2 is not optional and cannot be enforced by peer-to-peer handoffs. In a swarm, each agent determines its own handoff target. An analysis agent could theoretically hand off to the confirmatory statistics agent before Gate 2 approval. The supervisor pattern holds global context and enforces ordering through explicit conditional edges — this is a structural guarantee, not a prompt engineering hope.

**Cascading failure risk.** Research from the MAST taxonomy (1,600+ annotated agent execution traces, κ=0.88) identified cascading failure as the dominant failure mode in swarm architectures. In a swarm, a corrupted context passes forward from agent to agent with no circuit breaker. In a supervisor architecture, the coordinator can detect failure and halt dispatch to downstream agents. For a research project with no git version control and 1,400+ controls processed per run, a cascade that corrupts mid-run state is not recoverable.

**O(n²) failure surface.** With 48 agents in a full mesh, there are 1,128 potential failure points. Testing coverage cannot scale to that surface. The hierarchical pattern reduces this to O(n) within each team.

**Context window:** 1,400 SCF controls and 280,000 STRM mappings cannot fit in a single context. Supervisor architecture enables multi-agent subgraphs that each hold focused context.

### Why Not Flat Supervisor

A flat supervisor with all 48 agents as workers would accumulate the full message history from all agent interactions in the supervisor's context window. Research shows routing accuracy degrades measurably after 8-12 sub-agent round trips as historical messages crowd out current task state.

Additionally, P1–P5 analysis modules are logically independent — there is no reason to run them sequentially through a flat supervisor when they can execute in parallel. A flat supervisor's synchronous routing loop forces serial execution even for independent work.

### Why Supervisor + Hybrid

The hybrid pattern separates concerns into planning and execution tiers. The top-level supervisor handles global state, gate enforcement, and team sequencing. Each team subgraph handles its own internal logic with isolated state. P1–P5 modules run as parallel branches within the analysis subgraph (T-03) using LangGraph's `Send` API.

This matches the task structure:
- Global ordering: enforced by the supervisor
- Local parallelism: fan-out within analysis and evaluation subgraphs
- Gate firewalls: interrupt() nodes as structured breaks in the supervisor's routing
- Context isolation: each subgraph holds focused context for its domain

A counterintuitive research finding supports this: applying supervisor coordination to a previously uncoordinated agent framework reduced average token consumption by 39.36% while maintaining accuracy, because supervisor validation prevented redundant work by downstream agents (source: coordination study, arxiv.org/html/2510.26585v1).

---

## Consequences

**Positive:**
- Gate 2 firewall is structurally enforced — not possible to bypass without explicit architectural change
- P1–P5 modules execute in parallel, bounding analysis phase latency to the slowest single module
- Team subgraphs are independently debuggable and testable
- Supervisor context window remains manageable because team outputs are surfaced as summaries, not full internal transcripts

**Negative:**
- Hybrid architectures have higher infrastructure complexity than flat supervisors
- Subgraph state isolation requires explicit state schema design — `Annotated[list[...], add]` reducers on every key that parallel branches write to
- Debugging requires `subgraphs=True` flag on `get_state()` calls; subgraph state is only accessible while interrupted

**Mitigation:**
- State schema is defined once in `HCGRCState` (see AGENT_WORKFLOW.md Section 4) and validated by CARDS_SPEC.md tooling
- Graph topology is compiled and inspectable via `graph.get_graph(xray=True).draw_mermaid()`

---

## Implementation Notes

- LangGraph 1.0 (GA October 22, 2025) is the implementation baseline. The `interrupt()` / `Command(resume=...)` HITL pattern is first-class in v1.0.
- LangGraph 1.1 (December 2025) retry middleware is used for transient LLM failures.
- Each team subgraph is a `StateGraph` compiled independently, then registered as a node in the parent graph. Teams can be developed, tested, and deployed independently.
- See AGENT_WORKFLOW.md for complete graph topology, state schema, and node implementations.

---

## References

- [Swarm vs Supervisor — Augment Code](https://www.augmentcode.com/guides/swarm-vs-supervisor)
- [LangGraph Multi-Agent Workflows — LangChain Blog](https://blog.langchain.dev/langgraph-multi-agent-workflows/)
- [Scaling LangGraph Agents — AI Practitioner](https://aipractitioner.substack.com/p/scaling-langgraph-agents-parallelization)
- [LangGraph 1.0 GA — LangChain Blog](https://blog.langchain.com/langchain-langgraph-1dot0/)
- [MAST Failure Taxonomy — arxiv.org/html/2503.13657v3](https://arxiv.org/html/2503.13657v3)
- [Coordination Token Reduction Study — arxiv.org/html/2510.26585v1](https://arxiv.org/html/2510.26585v1)
