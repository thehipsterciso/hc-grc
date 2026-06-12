# Adversarial Findings — Living Register

**Status:** Living document. Append new findings; never delete.
**Canonical store:** GitHub issues labeled [`adversary-finding`](https://github.com/thehipsterciso/hc-grc/issues?q=label%3Aadversary-finding).
**Closes #127. Consumed by the Agent-Evolution read-back loop (#126).**

---

## Why this exists

The platform's value rests on its own honesty about where it is weak. Adversarial review
surfaces those weaknesses; this register makes them a *consumed* input rather than a
write-only archive. The Sakana AI Scientist failure mode (no institutional memory for
defects — see `INCIDENTS.md`) is mitigated only if findings are read back into decisions.
This register is the read side's index.

The **GitHub `adversary-finding` label is the source of truth** — each finding is an issue
with a severity label (`critical` / `high` / `medium` / `low`), area labels, and a resolution
trail. This file indexes them, defines the format, and specifies how agents consume them.

## Finding format (one issue per finding)

```
Title:   <one-line defect statement>
Labels:  adversary-finding, <critical|high|medium|low>, <area...>
Body:    Finding — what is wrong and why it matters.
         Evidence — how it was surfaced.
         Resolution — ADR / decision / code change that addresses it, or "accepted risk".
Close:   when resolved via an ADR, ledger entry, or code change (reference it).
```

## Consumption protocol (read-back loop, #126)

Before a phase starts, the orchestrator loads:
1. **Open** `adversary-finding` issues — unresolved weaknesses to route around.
2. Findings whose `area` labels intersect the upcoming phase (e.g. `methodology`, `gate`, `architecture`, `ds-ml`).
3. The ADR(s) that resolved related findings, to avoid re-introducing a closed defect.

A finding re-encountered after closure is a regression → reopen the issue and file an `INCIDENTS.md` entry.

## Register (as of 2026-06-12)

**Architecture integrity — #71–#80** — resolved by **ADR-0015** (ten decisions: structural-firewall
Phase-0 conditionality, orchestrator failure model, provenance ordering, gate-write protection,
data-split idempotency, checkpoint scale, Agent-Evolution protected set, inter-agent trust,
observability correlation, Gate-2 delivery).

**Methodology — #81–#88** — circular P1 validity, cosine-similarity adequacy, P4 taxonomy
independence, blast-radius capability, hypothesis-selection bias, SAP-deferral exposure,
contribution-claim verification, Tier-3 causal feasibility. Addressed across the protocol,
SAP, and ADR-0013 (STRM-as-secondary); several are accepted, disclosed limitations.

**Program governance — #89–#95** — single-operator independence, scope/resource estimation,
tier killswitch, untested governance (→ Phase-0 sign-off #109–#113), completion definition,
agent-roster scope, scale realism.

**Open architecture items** — #96 (runtime assertion guards, Phase 2), #103 (gate_coordinator
serialized node, Phase 1).

## Open items

- [ ] Wire the consumption protocol into the orchestrator node (#126).
- [ ] On each new adversarial review pass, file findings as `adversary-finding` issues and append a one-line pointer here if they introduce a new theme.
