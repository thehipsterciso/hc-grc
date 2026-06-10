# ADR-0004: Five-Gate Human Approval Topology

**Status:** Accepted
**Date:** 2026-06-09
**Deciders:** Thomas Jones

---

## Context

The platform runs autonomous LLM agents on a pre-registered scientific protocol. The central scientific integrity risk is that exploratory analysis bleeds into confirmatory claims — a finding derived from the data used to test it. Autonomous systems amplify this risk because they can execute many analysis paths quickly and without the natural cognitive friction that slows human researchers.

The question was: how many gates, at what transitions, enforced how?

## Decision

Five human approval gates, implemented structurally in the LangGraph topology (not as advisory checks), at the following transitions:

1. **Gate 1** — Protocol lock → Exploratory analysis begins
2. **Gate 2** — Exploratory complete → Confirmatory analysis begins (SAP lock, test split release)
3. **Gate 3** — Confirmatory complete → Dissemination preparation begins
4. **Gate 4** — QA review → External dissemination authorized
5. **Gate 5** — Internal review → External publication/release

Gate 2 is the most critical: it is the point of no return for the exploratory/confirmatory firewall. After Gate 2, the test split is decrypted and confirmatory analysis runs on data that exploratory analysis never touched. This gate cannot be reversed.

## Alternatives Considered

**Three gates (start, analysis-complete, release):** Simpler. Does not enforce the exploratory/confirmatory firewall at the code level — a human must manually check whether SAP was locked before confirmatory analysis ran. Eliminated because the firewall must be structural.

**Seven gates (additional gates within exploratory for module sign-off):** More granular. Creates operational overhead that may cause gate fatigue — reviewers stop reading carefully when every small step requires approval. Eliminated.

**No gates (fully autonomous):** Inconsistent with the platform's scientific integrity requirements. A SAP violation (running confirmatory analysis before locking the SAP) in a fully autonomous system could invalidate the entire study. Eliminated.

## Consequences

**Positive:**
- The exploratory/confirmatory firewall is enforced at the infrastructure level — it cannot be bypassed without modifying the LangGraph graph definition
- Gate decisions are timestamped, signed, and logged in the pre-registration ledger — audit trail is complete
- Dissent is a required field at every gate — the gate cannot be rubber-stamped

**Negative:**
- Five gates require five human review sessions — operational overhead compared to a fully autonomous pipeline
- Gate 2 is irreversible — releasing the test split cannot be undone; a poor SAP locked at Gate 2 means a poor confirmatory study

**Design constraint:** Gate nodes must follow the four interrupt() engineering rules in GATES.md. Violation silently breaks replay integrity.
