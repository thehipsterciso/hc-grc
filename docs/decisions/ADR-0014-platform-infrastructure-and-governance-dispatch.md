# ADR-0014: Platform Infrastructure Architecture and Governance Dispatch

**Status:** Accepted  
**Date:** 2026-06-10  
**Author:** Thomas Jones  
**Supersedes:** N/A  
**Relates to:** ADR-0002 (local-first data sovereignty), ADR-0012 (autonomous iterative architecture), ADR-0013 (research design)

---

## Context

ADR-0012 established the autonomous research organism model: the platform executes continuously, the operator governs Charter-level decisions asynchronously. That model requires two infrastructure commitments that were previously unspecified:

1. A compute substrate capable of continuous, unattended, multi-day operation independent of the operator's development workstation
2. A governance dispatch channel that delivers Escalation proposals to the operator and returns decisions to the platform — regardless of where the operator is physically located at the time

This ADR captures both commitments and the architectural rationale behind them.

---

## Decision

### 1. Dedicated Compute Node

The platform runs on a dedicated Apple Silicon compute node, physically and logically separate from the development workstation.

**Rationale:**
- The autonomous research organism model requires continuous operation. A platform that runs only when the development workstation is active is not autonomous — it is interactive with extra steps.
- Resource contention between development activity and research execution introduces non-determinism into run timing, memory availability, and thermal performance. Separation eliminates this class of problem.
- Apple Silicon's unified memory architecture and Neural Engine provide high-throughput ML inference at low power draw, making always-on operation economically viable.
- With dedicated hardware, the platform can run exhaustive analyses — full model comparison grids, multi-day iterative hypothesis cycles, deep Monte Carlo sensitivity runs — that would be impractical on a development machine constrained by competing workloads.

**Operational implication:** The compute node is the platform's production environment. It runs the full agent swarm, holds all persistent state (PostgreSQL checkpoint store, vector stores, embedding caches), and is the authoritative source of all research outputs. The development workstation is for code development and testing only.

---

### 2. Redundant Multi-WAN Connectivity

The compute node maintains internet connectivity via a multi-WAN bonding and failover device with two independent ISP uplinks.

**Rationale:**
- The Escalation governance loop requires reliable bidirectional connectivity: the platform must be able to send proposals outbound, and operator decisions must be able to reach the platform inbound.
- Single-ISP dependency introduces a single point of failure in the governance loop. A Escalation proposal that cannot be delivered — or a decision that cannot be received — stalls the platform indefinitely under ADR-0012's "never auto-escalate" rule.
- Multi-WAN bonding provides both redundancy (automatic failover if one uplink goes down) and throughput (bonded bandwidth for data-intensive operations such as literature corpus downloads or model weight fetches).
- The connectivity infrastructure is treated as a platform dependency, not an operator convenience. Its availability is a prerequisite for unattended autonomous operation.

**Data sovereignty:** Connectivity is outbound for notifications, governance dispatch, and literature access. SCF corpus data, derived embeddings, intermediate analysis artifacts, and research outputs remain on the compute node at all times, consistent with ADR-0002.

---

### 3. Claude as Governance Dispatch Interface

Escalation proposals are delivered to the operator via Claude. The operator reviews and responds through the same interface. No custom governance UI is built.

**Rationale:**

**Operator fluency.** The operator's primary working interface is already Claude across all devices. A governance notification that arrives in the same interface as the operator's existing workflow has near-zero adoption friction. A custom UI requires context-switching and familiarity investment that a solo research operation cannot justify.

**Cross-device availability.** Claude is accessible on desktop, tablet, and mobile. Escalation proposals reach the operator on whatever device is in use at the time of notification — no device-specific setup required.

**Structured natural language as the interface.** Escalation proposals are structured JSON with a natural language summary. Claude renders the proposal as a readable briefing, the operator responds in natural language, and Claude translates the response into a structured decision record. This is precisely the task Claude is designed for — there is no reason to build a separate UI to do it.

**Existing infrastructure.** GitHub issues are already the project's decision record. The platform files a GitHub issue for each Escalation proposal. The operator's existing GitHub notification infrastructure delivers the alert. Claude (with GitHub MCP access) reads the proposal, facilitates the decision conversation, and writes the structured decision back as a comment. The Preregistration Ledger and W3C PROV-DM audit trail record the decision with cryptographic timestamp. Every component of this loop already exists.

---

## Operational Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPUTE NODE (always-on)                  │
│                                                             │
│  Platform executes research autonomously                    │
│         ↓                                                   │
│  Escalation condition detected (Charter amendment required)     │
│         ↓                                                   │
│  Platform generates structured proposal:                    │
│    - Proposed Charter amendment                             │
│    - Rationale from findings                                │
│    - Scope and compute impact                               │
│    - Recommended approve/reject                             │
│         ↓                                                   │
│  Files GitHub issue → operator notified on any device       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    OPERATOR (any device, any location)      │
│                                                             │
│  Receives notification → opens proposal in Claude           │
│  Reviews natural language briefing                          │
│  Responds: approve / reject / defer (with conditions)       │
│  Claude writes structured decision → GitHub comment         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    COMPUTE NODE                             │
│                                                             │
│  Platform polls for decision                                │
│  Decision received → Charter amended or proposal parked     │
│  Decision logged to PROV-DM audit trail with timestamp      │
│  Autonomous execution resumes / new Charter version activated│
└─────────────────────────────────────────────────────────────┘
```

---

## Development Workflow

```
Development workstation  →  git push  →  Compute node pulls and runs
(code, tests, ADRs)                      (platform execution, state, outputs)
```

The compute node runs a persistent git pull loop or webhook trigger. Code changes deployed from the development workstation are live on the compute node without manual intervention.

---

## Consequences

**What this enables:**
- True autonomous operation — the platform works continuously without operator presence
- Multi-day exhaustive analysis runs that would be impractical on a development workstation
- Governance decisions can be made from any location on any device without dedicated tooling
- The research program scales with the operator's availability to govern, not their availability to babysit a running process

**What this requires (not yet built):**
- Compute node provisioning: OS, dependencies, Docker Compose stack, PostgreSQL, vector stores
- Git deployment trigger on compute node (webhook or pull loop)
- Platform Escalation proposal generator: structured JSON + natural language summary → GitHub issue
- GitHub notification routing confirmed to reach operator's devices
- Claude GitHub MCP access configured and tested

**What this does not change:**
- ADR-0002: data sovereignty. SCF data, embeddings, and research outputs stay on the compute node.
- ADR-0012: two-tier autonomy. Autonomous proceeds without operator approval. Escalation parks and notifies. Neither changes based on infrastructure.
- The Preregistration Ledger, PROV-DM audit trail, and cryptographic timestamps are unaffected — they run on the compute node regardless of governance dispatch channel.

---

## Alternatives Considered

**Custom governance dashboard (web UI on compute node):** Rejected. Requires building and maintaining a frontend that provides no capability Claude does not already provide. Introduces a login/auth surface, a deployment target, and ongoing maintenance burden for a solo research operation.

**Email-only notification:** Rejected. Email delivers the alert but does not facilitate the decision conversation. The operator would need to context-switch to another tool to review the structured proposal and formulate a response. Claude provides the full loop in one interface.

**Operator's development workstation as the platform node:** Rejected. Eliminates continuous autonomous operation, creates resource contention, and ties research progress to operator availability. Fundamentally incompatible with ADR-0012.
