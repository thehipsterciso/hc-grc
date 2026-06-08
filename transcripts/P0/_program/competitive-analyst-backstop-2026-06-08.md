# Transcript: competitive-analyst — Backstop Audit
**Date:** 2026-06-08
**Stage:** P0
**Agent:** competitive-analyst (Tier-3 cross-discipline backstop)
**Stance:** cross-discipline enforceability audit
**Scope:** ORCHESTRATOR_PROTOCOL.md v1.0, COORDINATOR_CRON_PROTOCOL.md v1.0, AGENT_SYSTEM.md, data-engineer.md (hardened agent sample)
**Status:** COMPLETED — 10 findings, 2 critical. Pending ledger registration.

---

## Findings

### Finding 1 — Mandatory footer not mechanically verifiable; run-id unresolved (CRITICAL)
Footer template contains free-text fields with no schema. CI cannot parse reliably. `--run-id <run-id>` is an unresolved placeholder the agent cannot fill — coordinator must inject it pre-dispatch. No script validates footer completeness or catches the placeholder.

**Fix:** Emit footer as fenced YAML/JSON with mandatory typed keys. Coordinator injects run-id at dispatch time. Add pre-commit/CI hook that parses every response file and fails on absent keys or unresolved placeholders.

### Finding 2 — "Same run" adversary constraint unenforceable given async execution (CRITICAL)
If session times out, context exhausts, or interrupt fires after producer completes but before adversary dispatch, Rule 1's guarantee fails. Prevention is partially impossible. Step 2 recovery is the real enforcement mechanism, not the "same run" rule.

**Fix:** Demote "same run" to a best-effort guideline. Make Step 2 the primary guarantee. Write a sentinel file at the moment of producer dispatch (not completion) so Step 2 can detect partial state even if coordinator dies before producer returns.

### Finding 3 — Step 2 blocks indefinitely on rejection loops (HIGH)
Protocol requires all adversaries to complete before advancing to Step 3. In a P0-recovery scenario with 5 uncertified artifacts, Step 2 is unbounded. Rejection loops have no exit condition specified.

**Fix:** Adversaries dispatched in Step 2 follow the standard 3-round/arbiter limit. Step 2 exits when all violations have a *dispatched* adversary (not necessarily a completed certificate). Completions handled in subsequent cron runs.

### Finding 4 — Producer output detection depends on potentially-empty ledger (HIGH)
Step 2 relies on ledger queries. P0's ledger was empty — a Step 2 check after P0 would have declared "no violations" despite 5 uncertified artifacts. Protocol has no defense against an empty ledger.

**Fix:** Step 2 must use a filesystem-based check as primary: for each known artifact output path (derivable from stage graph), check file-exists AND certificate-exists. A file with no certificate is a violation regardless of ledger state. Ledger query is secondary cross-check.

### Finding 5 — Conditional approval detection requires unspecified NLP parsing (HIGH)
Rule 1.5 declares hedged verdicts ("accept with reservations") as rejections. But no structured verdict format exists. Coordinator must parse free text. An adversary can write an ambiguous opening clause and a compliant coordinator may misclassify it.

**Fix:** Define a structured verdict field in adversary certificates with enumerated value `PASS` or `REJECT` only. Coordinator reads only that field for routing. Certificates missing the field are treated as REJECT.

### Finding 6 — Failure mode F5 (false status reporting) not addressed in protocol (MEDIUM)
Neither protocol document contains rules about agent status reporting, timeouts, or what to do when a dispatched agent produces no output within expected time.

**Fix:** Add a maximum-wait rule. If a dispatched agent does not complete within the window, log `status: unresolved` in ledger, do not claim agent is running, raise in next cron run's Step 2 as a missing-output condition.

### Finding 7 — Scope violation pre-flight bypassed if defect record was never written (MEDIUM)
Pre-flight checks for scope violations in the ledger. But orchestrator can observe a violation, judge it correct, and continue without recording a defect (exactly what happened in P0 Failure 3). No defect record = pre-flight passes.

**Fix:** Pre-flight scope check must include git-based comparison of every governance document against its last pre-dispatch-logged state. Independent of whether a defect record exists. Define an explicit exception pathway for substantively-correct unauthorized modifications requiring human review + ledger entry.

### Finding 8 — Arbiter agent undefined; deadlock resolution has no concrete dispatch target (MEDIUM)
ORCHESTRATOR_PROTOCOL Rule 1.4 and AGENT_SYSTEM.md reference an arbiter agent but no agent file exists in `agents/` or `.claude/agents/`. A coordinator reaching round 3 deadlock has nothing to dispatch.

**Fix:** Define an `arbiter` agent file with system prompt, model assignment, and decision protocol before first production run. Model assignment: a different Anthropic tier / fresh context.

### Finding 9 — Per-framework vs program-level tripwire scope ambiguous in Step 7 (LOW)
Step 7 final paragraph says "do not attempt workaround work... while a program-level tripwire is blocking" but does not explicitly state that T2 (per-framework) only blocks that framework while others may advance.

**Fix:** State explicitly: T2 blocks work only for the framework whose T2 is unsigned. T1, T3, T4, T5 block all frameworks.

### Finding 10 — T1 linkage to findings registration is implicit, not enforced at protocol level (LOW)
Protocol does not explicitly require T1 to be signed before S3/S7 results are registered. The tripwire check in Rule 7 is present but the conditional is vague.

**Fix:** Pre-flight checklist should enumerate which stages require which tripwires: T1 required before S3 and any stage that registers findings (S5–S9, X1–X4).

---

## Failure Mode Coverage Table

| P0 Failure | Protocol response | Gap? |
|---|---|---|
| F1 — Producers accepted without adversary | Rule 1.3, Step 2, Rule 7 pre-flight | Gap: detection depends on ledger (Finding 4) |
| F2 — Transcripts not captured | Rule 2, Step 3 | Adequate (given non-empty ledger) |
| F3 — Out-of-scope file modification | Rule 3, Step 5 | Gap: pre-flight depends on defect records that may not exist (Finding 7) |
| F4 — Coordinator ran agent-domain commands | Rule 4 | Adequate |
| F5 — False status reporting | Not addressed | No rule added (Finding 6) |
| F6 — No git commits | Rule 5, Step 4 | Adequate |

New failure modes not in failure record: run-id resolution gap (F1), unbounded Step 2 blocking (F3), absent arbiter definition (F8).

---

## Severity Summary

| # | Finding | Severity |
|---|---|---|
| 1 | Footer not mechanically verifiable; run-id unresolved | Critical |
| 2 | "Same run" adversary constraint unenforceable | Critical |
| 3 | Step 2 blocks indefinitely on rejection loops | High |
| 4 | Producer output detection depends on empty-ledger-vulnerable query | High |
| 5 | Conditional approval requires unspecified NLP parsing | High |
| 6 | False status reporting not addressed | Medium |
| 7 | Scope violation pre-flight bypassed if no defect record | Medium |
| 8 | Arbiter agent undefined | Medium |
| 9 | Per-framework vs program-level tripwire scope ambiguous | Low |
| 10 | T1 linkage to findings registration implicit | Low |

**Classification:** Tier-3 finding. Does not constitute a certificate. Each finding requires a protocol revision by the producing discipline, followed by same-discipline adversary review before the revised protocol is binding.
