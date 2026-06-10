# ADR-0012: Autonomous Iterative Research Architecture

**Status:** Accepted  
**Date:** 2026-06-10  
**Author:** Thomas Jones  
**Supersedes:** N/A  
**Relates to:** ADR-0010 (three-tier program), ADR-0011 (resilience), AGENT_WORKFLOW.md

---

## Context

The platform was initially designed as a linear research pipeline: one pass through phases 0–5, five pre-specified analysis modules (P1–P5), terminating at a manuscript. This assumed a human researcher making deliberate analytical choices at each phase.

The actual design intent is different. Thomas builds and governs the infrastructure. The platform conducts the research — autonomously theorizing, iterating, self-correcting, and evolving its direction. Thomas approves hard pivots; the platform handles everything else without waiting for human input.

This ADR captures that design intent and the architecture it requires.

---

## Decision

The HC-GRC platform is an **autonomous research organism**, not a research pipeline.

Key architectural commitments:

1. **Cyclic topology over linear pipeline** — exploratory findings feed back into hypothesis generation; new research threads spawn and execute without requiring a full restart
2. **Two-tier autonomy** — tangential directions proceed autonomously; substantially different directions route to human approval before execution
3. **Platform-determined publication cadence** — the platform researches optimal publication cadence, proposes a roadmap, and Thomas approves the proposal (not each publication decision)
4. **Evolving module set** — P1–P5 are initial hypotheses, not fixed scope; the platform generates, pursues, and retires modules as evidence warrants

---

## The Research Charter

The platform maintains a **Research Charter** — a structured, machine-readable statement of the current approved research direction. It captures:

```
{
  "primary_objective": "Understand the SCF data space empirically — inputs, outputs, mappings, deviations, financial risk implications",
  "approved_domains": [...],      // subject areas currently in scope
  "methodology_class": [...],     // analytical approaches currently approved
  "data_sources": [...],          // licensed data sources currently available
  "approved_tier": 1,             // current program tier
  "compass_version": "1.0.0"      // version-controlled; changes require Thomas approval
}
```

The Charter is the reference point for drift detection. It is version-controlled and each approved version is timestamped. Thomas approves Charter changes, not individual analysis decisions.

---

## Two-Tier Autonomy Model

### Tier A — Autonomous Proceed

The platform proceeds without human approval when a proposed new direction is **tangential** to the current Charter:

- New sub-hypotheses that refine a question already in scope
- Method variations within an approved methodology class
- New analytical angles on existing approved data sources
- Exploratory threads that emerge from findings within an approved domain
- Failure recovery and self-repair that stays within current scope

**Operational definition:** A direction is tangential if it does not require a Charter amendment — no new domains, no new methodology classes, no new data sources, no tier change.

All Tier A actions are logged with full provenance. Thomas can review the log at any time; the platform does not wait for review before proceeding.

### Tier B — Human Approval Required

The platform parks the proposed direction and notifies Thomas when it would require a **Charter amendment**:

- New subject domains not in the current Charter
- Substantially different methodology classes (e.g., shifting from NLP similarity to causal inference)
- New data sources requiring licensing or privacy review
- Tier escalation (Tier 1 → Tier 2, Tier 2 → Tier 3)
- Any action with irreversible consequences outside current scope

**Notification format:** The platform generates a structured proposal containing: proposed Charter amendment, rationale from findings, estimated scope and compute impact, recommended approval/rejection, and the finding that triggered it. Thomas responds with approve/reject/defer.

**Non-negotiable:** Tier B never auto-escalates. The platform waits indefinitely for a Tier B decision. It continues all Tier A work in parallel. Thomas does not slow down innovation — he gates scope expansion, not execution within approved scope.

---

## Feedback Loop Architecture

The current linear topology (phases 0→5, terminate) is replaced with a cyclic structure:

```
┌─────────────────────────────────────────────────────┐
│                  RESEARCH ORGANISM                  │
│                                                     │
│   Data Ingestion → Exploratory Analysis             │
│         ↑                    ↓                      │
│   Hypothesis             Findings                   │
│   Generation  ←─────────────┘                      │
│         ↓                                           │
│   Drift Detection                                   │
│    ↙          ↘                                     │
│ Tier A        Tier B                                │
│ (proceed)     (park + notify Thomas)                │
│    ↓                                                │
│ Confirmatory Analysis                               │
│         ↓                                           │
│   Publication Trigger Evaluation                    │
│    ↙          ↘                                     │
│ Publish       Continue                              │
│               (loop back to Exploratory)            │
└─────────────────────────────────────────────────────┘
```

The graph does not terminate after one pass. Each completed analysis cycle evaluates whether publication criteria are met. If not, findings feed back into the next exploratory cycle.

---

## Publication Trigger

Publication cadence is platform-determined, not pre-specified. The platform:

1. Researches optimal publication cadence for empirical GRC/NLP work (venues, timing, preprint vs. peer review norms)
2. Proposes a publication roadmap as a Charter amendment (Tier B — Thomas approves)
3. Once approved, evaluates publication readiness after each completed confirmatory cycle
4. Triggers manuscript preparation when readiness criteria are met

**Readiness criteria (platform-evaluated):**
- Minimum evidentiary threshold met for at least one primary finding
- Null results documented with equal rigor to positive findings
- Reproducibility package complete
- Finding is novel relative to published literature (platform monitors continuously)

---

## Implications for Pre-Registration

The traditional pre-registration model (register hypotheses before data is seen, never deviate) does not fit a continuously iterating autonomous system. This does not mean abandoning epistemic rigor — it means applying a different governance model appropriate to the execution model.

Adopted approach: **Registered Reports with continuous amendment logging**

- Each hypothesis the platform pursues is logged to the Preregistration Ledger with a timestamp before confirmatory testing begins — regardless of whether it was pre-specified or platform-generated
- The audit trail in W3C PROV-DM provides complete lineage from observation → hypothesis → test → result
- The platform cannot retroactively alter a logged hypothesis or its test result
- Exploratory findings are always distinguished from confirmatory findings in all outputs

This provides stronger transparency guarantees than traditional pre-registration because every step is logged in real time, not just the initial hypothesis set.

---

## Consequences

**What this enables:**
- Platform can discover and pursue research directions Thomas would not have pre-specified
- Findings compound — each cycle informs the next
- Publication happens when evidence is ready, not on an arbitrary schedule
- Thomas's involvement is scoped to Charter governance, not research execution

**What this requires (architectural work):**
- Feedback edges in the LangGraph topology (cycles, not just DAG)
- Research Charter as a versioned, machine-readable artifact
- Drift detection node that evaluates proposed directions against the Charter
- Tier B notification and response workflow (Gate variant, not a research gate)
- Publication readiness evaluator node
- Continuous literature monitoring to track novelty

**What this closes (issues resolved by this ADR):**
- #95: Scope vs. solo capacity — resolved (platform executes, Thomas governs)
- #69: Five modules with no primary question — resolved (modules are platform-discovered, not pre-specified)
- Partially addresses #61, #85: pre-registration and hypothesis selection bias — addressed by Registered Reports model above

**What this does not close:**
- #91: Tier escalation needs explicit go/no-go criteria (Tier B decision, but criteria still need defining)
- #94: Tier 1 completion definition still needed (what triggers the platform to consider Tier 1 done?)
- #89: Single-operator governance — Thomas is still the sole Charter approver

---

## Alternatives Considered

**Keep linear pipeline, scope to one person manually** — Rejected. Underutilizes the platform capability and caps the research at what Thomas can personally execute. The whole point of the platform is to exceed that ceiling.

**Fully autonomous with no human approval** — Rejected. Scope expansion without human oversight creates uncontrolled resource consumption, potential data licensing violations, and research directions that don't serve the strategic objective. The two-tier model preserves autonomy within approved scope while protecting against unconstrained drift.

**Pre-specify all modules upfront, no evolution** — Rejected. This is the original design flaw. Pre-specifying questions before seeing the data is the performative certainty problem. The platform should discover what questions are worth asking.
