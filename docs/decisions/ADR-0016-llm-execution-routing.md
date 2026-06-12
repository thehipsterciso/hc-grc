# ADR-0016: LLM Execution Routing — Local-First Compute, Subscription Frontier Reasoning

**Status:** Proposed
**Date:** 2026-06-12
**Author:** Thomas Jones
**Supersedes:** N/A
**Amends:** ADR-0002 (local-first, data-sovereign architecture)
**Relates to:** ADR-0010 (three-tier program), ADR-0012 (autonomous architecture), ADR-0015 (#80 gate delivery)

---

## Context

The platform's agents require LLM inference of two very different characters: (1) high-volume, latency-tolerant parsing and classification across 1,400+ controls and ~280,000 STRM mappings, and (2) a small number of high-stakes reasoning judgments where a wrong answer corrupts the science or a public output (hypothesis formalization, genuine-vs-terminological convergence, adversarial QA, statistical interpretation, manuscript reasoning).

A single backend cannot serve both well. Routing all work to a frontier model is unaffordable and unnecessary; routing all work to a local model under-serves the judgments that carry research-integrity risk.

Two hard constraints frame the decision:

1. **No metered API spend.** Execution runs entirely within a fixed **Claude Max 20x subscription ($200/month)**. The pay-per-token Anthropic API is out of scope by owner decision. This is an ordinary, fixed budget constraint — the kind every program operates under — and the orchestration framework (ADR-0001, LangGraph) is expected to plan within it.
2. **Dedicated headless compute.** A dedicated Mac mini runs 24/7. Latency is acceptable; bursty, queued execution against subscription rate windows is acceptable.

ADR-0002 established local-first, data-sovereign infrastructure, motivated by the SCF's CC BY-ND license and reproducibility integrity. That ADR addressed **storage** of derived artifacts in SaaS. It did not contemplate **transient inference** over SCF-derived text by a hosted frontier model. This ADR resolves that gap explicitly.

## Decision

LLM work is routed across three tiers **by stakes**, not by whether a task is "reasoning."

### Tier 1 — Deterministic ML (Mac mini, 24/7, no LLM)
Embeddings and the non-generative analytical modules: P2 control topology, P4 risk-coverage density, P5 clustering (HDBSCAN/UMAP). These are computation, not inference.

### Tier 2 — Local LLM (Mac mini, 24/7)
Low-impact, high-volume reasoning served by a locally hosted open model (Ollama / llama.cpp): P1 per-pair STRM classification at scale, literature first-pass triage, ideation, routine documentation generation. Fully on-device; no ADR-0002 tension.

### Tier 3 — Frontier reasoning (Claude Max 20x via the Claude Agent SDK)
Reserved for high-risk, high-complexity judgments only:

| Agent | Why frontier |
|-------|--------------|
| hypothesis-formalizer | Defines the pre-registered tests; errors propagate into the entire confirmatory phase |
| p3-regulatory-convergence | Genuine-vs-terminological distinction is a nuanced semantic judgment |
| qa-agent | Adversarial critique that catches hallucinated or unsupported findings |
| statistical-analyst (interpretation) | Translating results into claims under SAP constraints |
| ml-paper-agent / whitepaper-agent (final reasoning) | Public-facing scientific claims |

Authentication is via `claude setup-token` (a long-lived token in `CLAUDE_CODE_OAUTH_TOKEN`) on the headless node, drawing the subscription's included usage. **No Anthropic API key is provisioned.**

### Budget as a design constraint
The $200/month subscription envelope and its rate windows are treated as a fixed input the system designs against — not as a risk to be re-surfaced. Frontier volume is kept small by routing all low-stakes work to Tiers 1–2. When a subscription rate window is reached, frontier work **queues and resumes**; it never spills to a metered API. This backpressure is ordinary engineering within the LangGraph orchestration layer, consistent with the resilience model in ADR-0011.

### Implementation seam
Tier-3 nodes call frontier inference through a thin `reasoning_client` abstraction (Agent SDK implementation). The abstraction isolates the auth/transport choice from agent logic so the platform is not coupled to a single mechanism.

## Sovereignty position (amendment to ADR-0002)

ADR-0002 disqualified SaaS for **storing** derived artifacts (traces, embeddings, datasets). This ADR permits **transient, non-retained inference** over SCF-derived text by the frontier model, under these conditions:

- No derived **dataset** is transmitted or stored off-device in bulk; only the specific control/mapping text needed for a single reasoning call is sent, transiently, per call.
- All persistent artifacts (embeddings, traces, experiment logs, results) remain on-device per ADR-0002, unchanged.
- SCF attribution obligations (CC BY-ND) are preserved; no derived dataset is published.
- This is consistent in spirit with ADR-0015 §10, where Gate 2 payloads travel as summaries while the dataset stays on the compute node — here, the boundary is drawn at *storage*, with inference explicitly permitted.

## Alternatives Considered

**All-frontier routing:** Rejected — unaffordable within the fixed envelope and unnecessary for deterministic and high-volume work.

**All-local routing:** Rejected — under-serves the high-stakes judgments (hypothesis design, convergence semantics, adversarial QA) where local model quality is a research-integrity risk.

**Metered Anthropic API for Tier 3:** Out of scope by owner decision. The fixed-subscription model is a deliberate budget choice, not a limitation to engineer around.

## Consequences

**Positive:**
- Costs are bounded and predictable by construction (fixed subscription).
- The Mac mini's 24/7 capacity absorbs the heavy, deterministic majority of the workload.
- Frontier capability is applied precisely where correctness risk is highest.
- The `reasoning_client` seam prevents lock-in to any single auth/transport mechanism.

**Negative / accepted trade-offs:**
- Frontier work is bursty and subject to subscription rate windows; wall-clock latency on Tier-3-heavy phases is higher. Accepted (80/20 rigor-over-speed posture).
- ADR-0002's "no SCF-derived content leaves the machine" stance is narrowed: transient inference is now permitted while storage remains local-only. This is the substantive change requiring owner sign-off.

**Documents requiring update on acceptance:**
- ADR-0002: add cross-reference noting the inference carve-out.
- Agent cards: add a `model:`/tier assignment field (Tier 1/2/3) across all cards — currently unspecified.
- SWARM_IMPLEMENTATION_ROADMAP.md: add `reasoning_client` + local serving as Phase 0/1 build items.
- PROJECT_CHARTER.md tech stack: record local serving (Ollama/llama.cpp) and Agent-SDK frontier path.

## Open items (non-blocking)

- Selection of the local open model(s) for Tier 2 — benchmarked on the mini before P1 implementation.
- Per-agent confirmation of Tier 2 vs Tier 3 placement as cards gain `model:` assignments.
