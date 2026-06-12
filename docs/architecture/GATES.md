# Human Approval Gates

**Status:** Locked — gate topology is fixed at pre-registration.

---

## Phase 0 Prerequisites — Structural Firewall Preconditions

All structural integrity claims in the project documentation are conditional on Phase 0 implementation completing before any data acquisition. The following must be verified before SCF data enters the system (per ADR-0015, #71):

- [x] LangGraph skeleton running with all five gate nodes present
- [x] Gate 1 fires with synthetic payload and produces a valid gate record *(#109 — `tests/test_phase0/test_gate1.py`)*
- [x] PostgresSaver checkpointing confirmed on Mac Mini compute node *(#110 — `tests/test_infrastructure/test_postgres_checkpointer.py`, live `hcgrc` DB)*
- [x] `compute_data_split()` idempotency test passes: two runs with identical state produce bit-identical output (seed derived from SHA-256 of data manifest hash — see #75) *(#111 — `tests/test_phase0/test_data_split.py`)*
- [x] Hardware benchmark complete: PostgresSaver write throughput characterized (write p95 12.7 ms / read p95 1.2 ms), `batch_size=50` locked (see #76) *(#112)*
- [x] Governance dry-run complete: all five components passing (see #93) *(#113 — `tests/test_phase0/test_governance_dry_run.py`)*

**Phase-0 sign-off COMPLETE (2026-06-12, verified on hc-macmini). SCF data acquisition (#116) is now unblocked.**

---

## Protected Agent Set — Agent Evolution Constraint

The following agents' prompts may not be modified by Agent Evolution autonomously. Any modification requires Escalation approval before taking effect (per ADR-0015, #77):

| Agent | Role |
|-------|------|
| p1-strm-nlp | NLP similarity measurement |
| p2-control-topology | Control-space topology / community detection |
| p3-regulatory-convergence | Cross-framework convergence measurement |
| p4-risk-blindspot | Risk-coverage gap analysis |
| p5-ai-governance | AI-governance clustering |
| statistical-analyst | Evidence weighting and testing |
| hypothesis-formalizer | Hypothesis structure for testing |

Agent Evolution retains full autonomous scope over all non-protected agents.

> **Names reconciled 2026-06-12.** The P2–P5 entries previously named non-existent
> agents (`p2-domain-clustering`, `p3-coverage-diffusion`, `p4-gap-analysis`,
> `p5-risk-quantification`). They are corrected here to the canonical card names in
> `agents/03-analysis/`. This is an integrity-critical list — a wrong name means
> Agent Evolution's protection guard targets a non-existent agent and the real
> analysis agent is left unprotected. ADR-0015 §7 carries a matching erratum.

---

## Gate Coordinator Node

All `gate_status` and `gate_decisions` writes are routed exclusively through a single serialized gate coordinator node. No agent writes directly to these keys. Enforced by LangGraph edge definitions (per ADR-0015, #74).

HC-GRC enforces five human approval gates implemented as LangGraph `interrupt()` calls in the Orchestrator node. Gates are not advisory — they are structural. The pipeline cannot advance past a gate without an explicit human decision recorded in the run manifest and the pre-registration ledger.

---

## Engineering Requirements (LangGraph interrupt() Rules)

These are correctness requirements, not guidelines. Violating them silently breaks checkpoint replay. Every engineer and agent working on gate implementation must read this section.

**Rule 1: Do not wrap `interrupt()` calls in try/except.**
Swallowed exceptions during interrupt prevent LangGraph from recording the interrupt in the checkpoint. On replay, the graph skips the gate entirely. This failure is silent on the first run and observable only on re-run.

**Rule 2: Do not reorder `interrupt()` calls within a node.**
Resumption from a checkpoint is index-based. If a node contains two interrupt calls and their order is swapped between the original run and a replay, the second human response is delivered to the first gate. The failure is logically silent — the graph resumes, but with the wrong gate decision applied.

**Rule 3: Do not return complex objects from `interrupt()`.**
Return only serializable primitives. Complex objects may fail to checkpoint correctly, producing a gate that appears to have been approved but whose decision cannot be verified on replay.

**Rule 4: Side effects before `interrupt()` must be idempotent.**
LangGraph may re-execute a node on replay. Any side effect that ran before the interrupt (writing to the lab notebook, emitting a provenance record) runs again. If those operations are not idempotent, replays produce duplicate records or inconsistent state.

**Implementation note:** LangGraph documentation recommends `durability: "sync"` for high-durability cases (gate-critical pipeline). This ensures checkpoints are written before execution continues. Set this in the PostgresSaver configuration for all gate nodes.

**Human response format:** Gate decisions must be provided as `approve | edit | reject | respond`. Decisions are delivered via `Command(resume=...)` and must be in the same order as the `interrupt()` calls appear in the gate node.

---

## Gate Inventory

| Gate | ID | Phase Transition | Trigger Condition | Decision Types |
|------|-----|-----------------|-------------------|----------------|
| Gate 1 | `gate-1` | Pre-analysis → Exploratory | Protocol documents reviewed and locked | approve / reject |
| Gate 2 | `gate-2` | Exploratory → Confirmatory | SAP finalized, hypotheses registered, test split released | approve / reject |
| Gate 3 | `gate-3` | Confirmatory → Review | All pre-specified confirmatory tests complete | approve / reject / edit |
| Gate 4 | `gate-4` | Review → Dissemination | QA Agent scores all findings ≥ 3.5/5 | approve / reject |
| Gate 5 | `gate-5` | Dissemination → Archive | External publication or release | approve / reject |

---

## Gate Definitions

### Gate 1 — Protocol Lock
**Unlocks:** Exploratory analysis on train + validation splits.
**Requires before approval:**
- `00_research_questions.md` — platform-level ERQs complete
- `01_theoretical_framework.md` — theoretical claims and construct definitions locked
- `04_methods_scaffolding.md` — test families, split strategy, firewall rules locked
- Pre-registration commit on protected branch with RFC 3161 timestamp
- Data acquisition complete — SCF downloaded, SHA-256 verified, DVC versioned

**Data access change:** None — test split remains locked.
**Cannot approve if:** Any protocol document is in draft state. Pre-registration commit missing.

### Gate 2 — Confirmatory Lock
**Unlocks:** Confirmatory analysis on the held-out test split. Releases test split decryption key.
**Requires before approval:**
- Exploratory analysis complete — all five ERQs characterized
- `03_statistical_analysis_plan.md` — specific hypotheses (H[module].[n]), named tests, effect size thresholds, correction methods all locked
- SAP pre-registration commit on protected branch with RFC 3161 timestamp
- Theoretical framework amendment committed (TC1–TC4 → specific hypotheses)
- Human reviewer has read and approved the SAP

**Data access change:** Test split becomes accessible. This transition is irreversible.
**Cannot approve if:** SAP is incomplete. Any hypothesis lacks a named test or effect size. Exploratory analysis ran on the test split (manifest `test_split_accessed == true` for any prior exploratory run).

### Gate 3 — Analysis Review
**Unlocks:** Dissemination preparation (writing agents).
**Requires before approval:**
- All pre-specified confirmatory tests complete on test split
- Statistical Analyst outputs reviewed
- QA Agent has scored all findings
- Null results documented with equal rigor as positive results
- Run manifest complete for all confirmatory runs

**Cannot approve if:** Any pre-specified hypothesis test is missing. QA Agent has not scored all findings.

### Gate 4 — Dissemination Authorization
**Unlocks:** ML Paper Agent, Whitepaper Agent, Business Presentation Agent, and all dissemination agents.
**Requires before approval:**
- All findings have QA score ≥ 3.5/5
- All findings trace to pre-registered hypotheses
- Limitations section covers all QA-flagged concerns
- Branding Compliance Agent pre-review for any practitioner-facing outputs

**Cannot approve if:** Any finding with QA score < 3.5/5 without documented escalation reason. Any finding without SAP trace.

### Gate 5 — Archive and Release
**Unlocks:** External publication or public release of findings.
**Requires before approval:**
- License Compliance Agent review complete
- IP Attribution Agent sign-off — all attributions present including SCF CC BY-ND
- Branding Compliance Agent final review
- Human reviewer has read final outputs

---

## Dissent Logging Requirement

Gate decisions are recorded in two places: the run manifest `gate_decisions[]` array and the pre-registration ledger. Both record `outcome`, `reviewer`, `timestamp`, `rationale`, and `dissent`.

`dissent` is a required field in both records. `null` means no dissent — it is not the same as an absent field. A gate record with no `dissent` field fails manifest validation.

**Rationale for this rule:** Adversarial collaboration research (Isch et al. 2025) documents that approval gates converge on consensus when the same reviewer never records dissent. A dissent field that is always `null` is a signal, not a validation failure — but it is a signal that should trigger review of whether the gate is functioning as a real check.

Gate rejections must include a rationale of at least 20 words. A rejection with a short rationale ("insufficient quality") fails manifest validation. The rationale must name the specific deficiency.

---

## Agents Passing Through Each Gate

*Auto-generated from AGENT.md Handoffs sections. Regenerate with `make generate-docs`.*

| Gate | Agents That Trigger It |
|------|----------------------|
| Gate 1 | Orchestrator (protocol lock check) |
| Gate 2 | Orchestrator (SAP lock + exploratory complete check) |
| Gate 3 | Orchestrator (confirmatory analysis complete check) |
| Gate 4 | QA Agent → Orchestrator |
| Gate 5 | Branding Compliance Agent → Orchestrator |

*Note: This table is currently hand-authored. Once `tools/generate_docs.py` is implemented per CARDS_SPEC.md, this section is auto-generated.*
