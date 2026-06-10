# ADR-0015: Architecture Integrity Decisions

**Status:** Accepted  
**Date:** 2026-06-10  
**Author:** Thomas Jones  
**Supersedes:** N/A  
**Relates to:** ADR-0011 (resilience), ADR-0012 (autonomous architecture), ADR-0014 (infrastructure)

---

## Context

Adversarial review surfaced ten architecture integrity issues (#71–#80) spanning: structural firewall implementation, orchestrator failure model, state schema safety, data split integrity, checkpoint scale, agent evolution scope, inter-agent trust, observability correlation, and gate delivery mechanism. This ADR captures the resolution of all ten.

---

## Decisions

### 1. Structural Firewall Claims Are Conditional on Phase 0 (#71)

All claims that "the firewall between phases is structural, not procedural" — in ADR-0004, ADR-0007, README, and the Charter — are conditional on Phase 0 implementation completing before any data acquisition.

**Phase 0 success criteria (hard prerequisites, added to GATES.md):**
- LangGraph skeleton running with all gate nodes present
- Gate 1 firing with synthetic payload confirmed
- PostgresSaver checkpointing confirmed on target hardware
- Gate 2 data split logic implemented and idempotency test passing
- No SCF data acquired until all criteria are met

The structural firewall claim becomes true when Phase 0 completes. Not before.

---

### 2. Orchestrator Failure Model — Option B + Evolve Layer (#72)

**Option B — Defensive gate nodes:** Each gate validates its own preconditions and rejects invalid state regardless of how T-00 routed. Gate nodes are the enforcement surface.

**Evolve layer:** Gate rejection events are logged with full context (proposed action, rejection reason, state snapshot, run_id, timestamp) to a `failure_events` store. Agent Evolution monitors `failure_events` for patterns:

- **Routing errors** (T-00 operational): Agent Evolution applies DSPy re-optimization to T-00's routing prompt autonomously. Logged to PROV-DM with before/after versions.
- **Architectural failures** (gate topology wrong, systematic design flaw): Escalation filed to operator.

This makes the platform self-correcting for operational routing failures without requiring a permanent watchdog node. Option A (real-time watchdog) becomes redundant once T-00's routing stabilizes through the evolve loop.

**Protected agent set:** Agent Evolution may not autonomously modify P1–P5, statistical-analyst, or hypothesis-formalizer prompts. See Decision 6.

---

### 3. Provenance Entry Ordering (#73)

Every entry appended to `prov_trace`, `errors`, and `null_results` carries:
- `timestamp`: ISO 8601 UTC, generated at write time by the writing agent
- `source_id`: agent name + run_id + superstep number

Downstream consumers sort by `timestamp` before processing. List position is never used as a proxy for execution order. Enforced by ARA Rigor Reviewer at validation time.

---

### 4. Gate Status Write Protection (#74)

All `gate_status` and `gate_decisions` writes are routed through a single serialized gate coordinator node. No agent writes directly to these keys. The coordinator is the sole authorized writer, enforced by LangGraph edge definitions (per Decision 7 — topology enforcement).

Sequential by construction. No custom reducer or runtime type checking required.

---

### 5. Data Split Idempotency — Deterministic Seed (#75)

`compute_data_split()` derives its random seed exclusively from SHA-256 of the data manifest hash. No system entropy is used (no time-based seed, `os.urandom()`, or unseeded numpy random).

**Required test (Phase 0 success criterion):** Run `compute_data_split()` twice with identical state. Assert bit-identical output. This test must pass before Gate 2 is considered operational.

---

### 6. Checkpoint Scale — Phase 0 Benchmark (#76)

Hardware benchmarking is a Phase 0 deliverable, not a Phase 3 decision. Before Phase 3 implementation begins:

1. Estimate checkpoint size per `HCGRCState` at analysis time
2. Benchmark PostgresSaver write throughput on Mac Mini compute node
3. Derive maximum feasible parallel branch count
4. Select `batch_size` accordingly — lock to SWARM_IMPLEMENTATION_ROADMAP.md

`batch_size=50` is a placeholder until the benchmark runs. The result may require architectural adjustment.

---

### 7. Agent Evolution Scope — Protected Agent Set (#77)

**Protected agents** (prompt modifications require Escalation approval before taking effect):

| Agent | Reason |
|-------|--------|
| p1-strm-nlp | Defines NLP similarity measurement approach |
| p2-domain-clustering | Defines clustering methodology |
| p3-coverage-diffusion | Defines semantic coverage measurement |
| p4-gap-analysis | Defines gap analysis methodology |
| p5-risk-quantification | Defines risk quantification approach |
| statistical-analyst | Defines how evidence is weighted and tested |
| hypothesis-formalizer | Defines how hypotheses are structured for testing |

Modifying these agents' prompts mid-tier against SCF corpus data is analytically equivalent to changing the research design post-hoc — a form of data snooping that bypasses Gate 2.

**Legitimate evolution paths for protected agents:**

1. **Before Gate 1:** DSPy optimization against synthetic data or public benchmarks only. No SCF data in system yet.
2. **Mid-tier via Escalation:** Platform files structured proposal with specific change and rationale. Operator reviews via Claude. Decision logged before change takes effect.
3. **Between tiers:** Post-tier retrospective informs deliberate redesign. Changes committed and version-bumped before next tier starts. This is science working correctly — Tier 1 findings inform Tier 2 instrument design.

**Agent Evolution scope:** Fully autonomous for all non-protected agents (T-00 routing, ingestion, reporting, QA, infrastructure).

---

### 8. Inter-Agent Trust — Topology Enforcement (#78)

**Phase 1 — Option A (structural):** LangGraph edge definitions control which agents connect to which state keys. An agent not wired to write a particular key cannot reach it — enforced at graph compile time, zero runtime overhead.

**Phase 2 — Option B (runtime assertions):** Deferred. Tracked in sub-issue #96. Activate when: a state corruption event occurs that topology enforcement did not catch, or Tier 2 scale requires finer-grained write control.

---

### 9. Observability Correlation — Common run_id (#79)

A single `run_id` is generated at the start of each research run and propagated to all four observability stores:

| Store | Integration |
|-------|------------|
| MLflow | `run_id` as experiment tag |
| Phoenix | `run_id` as trace attribute |
| W3C PROV-DM | `run_id` as activity identifier |
| PostgresSaver | `run_id` as thread_id / checkpoint key |

Cross-store correlation is a single-key lookup. A `RUNBOOK.md` documents the explicit cross-store query sequence for common diagnostic scenarios. No custom query infrastructure built.

---

### 10. Gate 2 Delivery — Escalation Loop (#80)

Gate 2 interrupt uses the Escalation loop established in ADR-0014. No separate UI required.

The Gate 2 payload (split parameters, summary statistics) travels via GitHub issue — not raw SCF data. Data stays on the compute node. The operator reviews summary artifacts, not the dataset. Local-first constraint (ADR-0002) maintained.

---

## Consequences

**What this enables:**
- Phase 0 can proceed with a complete, unambiguous success criteria checklist
- Orchestrator failures are self-correcting without permanent watchdog overhead
- Gate integrity is structurally enforced, not convention-dependent
- Research instrument (P1–P5) integrity is protected against silent prompt drift
- Cross-store diagnostics are operationally feasible for a single-operator program
- Gate 2 approval requires no new infrastructure

**What this closes:**
- #71 through #80: all ten adversarial architecture findings resolved

**What this creates:**
- #96: runtime assertion guards (Phase 2, sub-issue of #78)
- Phase 0 success criteria expanded with: idempotency test, hardware benchmark, Gate 1 structural test

**Documents requiring update:**
- GATES.md: Phase 0 prerequisites, protected agent set, gate coordinator node
- SWARM_IMPLEMENTATION_ROADMAP.md: batch_size benchmark as Phase 0 deliverable
- Agent Evolution AGENT.md: protected agent set constraint
- P1–P5 and statistical-analyst, hypothesis-formalizer AGENT.md cards: behavioral constraint on prompt modification
- RUNBOOK.md: create with common run_id cross-store query procedures
