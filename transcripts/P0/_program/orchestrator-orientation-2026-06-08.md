# hc-grc — Orchestrator Orientation & Program Review

**Date:** 2026-06-08  
**Stage:** P0 (Program setup & autonomy harness)  
**Activity:** Initial program review — three adversarial agents audited PREREGISTRATION.md, PROGRAM_ROADMAP.md, and the P0 infrastructure scope  
**Agents:** data-scientist-adversary (falsification-probe + assumption-ledger), first-principles-thinking, agent-organizer  
**Status:** DECISION RECORD — findings and decisions binding for P0 execution

---

## Executive summary

The hc-grc program entered P0 with 16 pre-registration defects, 10 architecture issues, and one
overclaimed model independence claim. Adversarial review identified each. Decisions made at this
gate determine the program's infrastructure and the shape of findings to come. Key decision: **P0
before P1**. Pre-registration thresholds will be informed by S3 synthetic data runs before T1
freeze.

---

## Pre-registration findings (16 defects identified)

### Defect D1: Algorithm naming — methods belong post-data, not pre-data

**What was found:**  
The pre-registration names specific algorithms (TwoNN, parallel analysis, participation ratio
consensus for Q2; Hopkins + permutation for Q3; HDBSCAN + k-means for Q5). These are *method
selection decisions*, not measurement plans, and they presuppose a data geometry that has not
been measured yet.

**Why it matters:**  
Naming a specific algorithm creates an incentive to tune its hyperparameters post-hoc to justify
the choice. Example: if Hopkins test fails to show structure, the urge to try variant test
statistics is strong. Pre-registration should name the *measurement intent* (is there cluster
structure?) and defer algorithm choices until S3, when they can be validated on ground truth
before any real data is touched.

**Decision:**  
Accept the finding. Rewrite Q3 and Q5 as "measurement intents." Freeze the specific algorithms
at S3 (post method-validation run, pre S4) instead of now. This is P0→P1→S3→freeze hierarchy,
not P0→freeze.

---

### Defect D2–D5: Thresholds assume specific outcome distributions

**What was found:**  
Q3's "Hopkins H ≤ [threshold]" presupposes that:
- The test will be run and will produce a single number.
- That number has a known null distribution.
- A threshold makes sense.

But this assumes the data is cluster-able enough to run the test at all. If the embedding is
uniformly distributed or singular, Hopkins is undefined. The pre-registration does not
acknowledge this branch.

Similarly, Q4 and X-Q1 assume the outcome is normally distributed and that a single cut point
divides coherent from incoherent. If the distribution is bimodal or heavy-tailed, a single
threshold is misleading.

**Why it matters:**  
Pre-specifying thresholds before understanding the data geometry is a way to (unconsciously)
engineer results. The falsification-probe stance asks: what if the data has a different
structure than you expect?

**Decision:**  
Thresholds for Q3, Q4, X-Q1 will be set after S3 method validation runs on synthetic data show
what distributions are plausible. This is documented as a program limitation: "T1 freeze moved to
after S3, informed by synthetic data," recorded in every certificate downstream.

---

### Defect D6: SCF circularity — corpus and crosswalk substrate

**What was found:**  
The SCF is both a framework corpus (F1) and the alignment substrate (crosswalk) for Tier B. This
creates a subtle circularity:
- S4 ingests F1 (SCF).
- S4 also builds the crosswalk table (aligning F2–F5 to F1).
- X1 uses that crosswalk to align all frameworks.
- X2 tests whether results replicate using X1's alignment.

If the crosswalk has a structural bias (e.g., it over-maps F2 controls to SCF categories it is
familiar with), X2's replication test will inherit that bias. The test is not independent; it is
testing whether other frameworks fit the SCF's editorial choices.

**Why it matters:**  
This is not a fatal flaw — crosswalk noise is expected and will be quantified in X1 — but it
must be explicit. Any "intrinsic" finding in X2 that depends on crosswalk alignment is not about
control space; it is about the SCF's editorial decisions reflected through the crosswalk.

**Decision:**  
X1 will report crosswalk quality metrics (coverage, many-to-many fan-out, alignment ambiguity).
X2's "intrinsic" label requires two classes of evidence:
1. **Direct replication:** Result holds in F2, F3, F4, F5 on their own taxonomies (not
   cross-aligned).
2. **Aligned replication:** Result holds in those frameworks when aligned via X1's crosswalk.

Only direct replication is called "intrinsic." Aligned replication is called "crosswalk-robust."
Every X2 claim is tagged with which class it is.

---

### Defect D7–D8: Decision rules reward convergence

**What was found:**  
X-Q1 asks: "For each per-framework result, does it replicate across F1–F5?" The threshold is
"≥ k of 5 frameworks within overlapping CIs."

But the decision rule does not distinguish:
- **(a) Convergence to a consistent finding:** All five frameworks find the same structure
  (e.g., intrinsic dimensionality ≈ 8).
- **(b) Absence of evidence:** Four frameworks are uncertain; one is conclusive. By some
  definitions, this counts as "replication" (k=1 or k=2).

The rule subtly privileges convergence. If the true answer is "frameworks differ," a random
threshold of k=3 might classify that as "framework-specific" instead.

**Why it matters:**  
The pre-registration must be agnostic to the answer. "We will call it replication if we see
convergence" is fine. "We will call it replication if [definition that happens to favor
convergence]" is not.

**Decision:**  
X-Q1 is rewritten neutrally: "For each per-framework result, classify it as: (a) intrinsic —
holds in ≥ [k] frameworks within overlapping CIs; (b) framework-specific — holds in some,
not others; (c) uncertain — insufficient evidence in any framework." No outcome is privileged.
Threshold k is set at S3 (method validation), not now.

---

### Defect D9: S9 is recomputation, not replication

**What was found:**  
S9 is described as "A second, independently-spawned team on a different model family, blind to
the original results, re-runs the framework's critical studies."

But "different model family" is not true (see Architecture issue 3 below). More importantly, "re-runs
the framework's critical studies" means re-doing the same analysis, not an independent analysis.
True adversarial replication would be: given the same corpus and pre-registration, design a
different analysis plan (different methods from the certified menu, different hypothesis focus,
different exploratory choices) and see if the finding still holds.

**Why it matters:**  
Recomputation (running the same code twice) catches bit-rot and random failures. Replication
(different analysts, different method choices, same research question) catches systematic
oversights. S9 as stated is recomputation. We want replication.

**Decision:**  
S9 is redesigned as adversarial replication. The second team:
1. Works blind to the first team's results and methods.
2. Receives the same corpus (S4 output) and pre-registration.
3. Selects independently from the S3-certified method menu.
4. Designs their own analysis direction (which questions to emphasize, which methods to try
   first, which sensitivity analyses to run).
5. Reports findings.
Replication = first team + second team both find the same structural claim, despite independent
method choices. This is the program's robustness check against model-family blind spots.

---

### Defect D10–D16: Other pre-registration gaps

| ID | Finding | Decision |
|----|---------|----------|
| D10 | Q1 is descriptive but has no definition of "coverage." | Add explicit definition: "density of control density distribution across control categories, measured by KDE-estimated percentiles." |
| D11 | Q6 assumes controls have internal references; not all frameworks have them. | Make Q6 conditional: "If references exist in this framework, test their topology; else, report 'not applicable.'" |
| D12 | Q7 uses nearest-neighbor distance but does not specify distance metric. | Specify: "Euclidean in the embedding space; dimensionality normalized by PCA projection." |
| D13 | Q8 assumes CIA triad is a "low-dimensional governance schema"; that is circular — CIA *defines* low-dimensionality. | Rewrite as: "How do measured dimensions relate to published governance frameworks' stated priorities?" Open list, not assumed. |
| D14 | X-Q2 says "frameworks converge on a common dimensional structure" but does not define "common." | Add: "Common = overlapping CIs on intrinsic dimensionality and ≥ 50% variance explained by shared principal components." |
| D15 | No mention of how to handle frameworks where a question is not applicable (e.g., F2 has no explicit risk taxonomy). | Add rule: "Mark result as 'N/A' in registry; do not count toward replication (X-Q1)." |
| D16 | No decision rule for handling conflicting adversary verdicts in S9 replication. | Add: "If replication finding contradicts original finding at 95% CI non-overlap, escalate to human tripwire (T4.1). Otherwise, report both as robust if both pass certification." |

---

## Architecture findings (10 issues identified)

### Issue 1: Tier 3 has no gate threshold

**What was found:**  
Tier 3's cross-discipline backstop (competitive-analyst + product-manager) audits each stage's
accepted set for defects the whole discipline shares. But the program does not define what counts
as a blocking issue. Does Tier 3 have veto power? Can it de-register a certified artifact?

**Decision:**  
Tier 3 has the right to raise a blocking issue that re-opens an artifact's review loop, but not
to de-register an artifact that passed Tier 2 certification. If Tier 3 finds a genuine shared-discipline
oversight, the artifact goes back through Tier 2 on the revised checklist. If Tier 2 still approves
it, Tier 3 can escalate to the stage's human tripwire. This is documented in `AGENT_SYSTEM.md`.

---

### Issue 2: No human gate on X1 crosswalk

**What was found:**  
T2 (framework licensing confirmation) gates S4 for each framework. But X1 (alignment) builds the
crosswalk that all of Tier B depends on, and there is no human approval point. If the crosswalk
is badly flawed, Tier B proceeds anyway.

**Decision:**  
Add T2.5 (crosswalk freeze): After X1 certifies the crosswalk, a human reviews the alignment
quality metrics and signs off before X2 begins. This is a two-minute gate: human reads the
alignment report and agrees that the crosswalk is good enough for the replication tests that
follow.

---

### Issue 3: Model independence claim overclaimed

**What was found:**  
The program claims "different model family" for producer/adversary independence. All agents run
on Anthropic models (sonnet vs opus), which is tier-level diversity within one family, not
family-level independence. A shared blind spot in Anthropic training would pass Tier 2.

**Decision:**  
Correct the claim in all documentation (AGENT_SYSTEM.md, PROGRAM_ROADMAP.md, agents/README.md,
CLAUDE.md). State clearly: "Tier-level diversity within Anthropic family; S9 adversarial
replication and cross-framework evidence are where strongest robustness is earned." This
limitation is recorded in every certificate. See "Model independence: honest accounting" in
AGENT_SYSTEM.md.

---

### Issue 4: S9 is recomputation, not replication (architectural)

**What was found:**  
Same as pre-registration defect D9, but it is an architecture issue: the stage description
assumes recomputation, not replication.

**Decision:**  
Redesign S9 as stated in D9 decision above. Update PROGRAM_ROADMAP.md S9 section and
AGENT_SYSTEM.md stage description.

---

### Issue 5: No explicit rule for LLM artifact reproducibility

**What was found:**  
Computational artifacts are byte-reproducible (run → hash match). LLM artifacts (agent reasoning,
reviews, writing) are not deterministic. The program does not distinguish or define reproducibility
for each.

**Decision:**  
Write REPRODUCIBILITY.md (see Deliverable 2 above). Clearly state:
- Computational = byte-reproducible (hash check).
- LLM = transcript-reproducible (read the full conversation and certificate, not re-run to a
  hash).
Certificate is the reproducibility check for LLM artifacts, not hash recomputation.

---

### Issue 6: Convergence outcome subtly privileged in classification scheme

**What was found:**  
Same as pre-registration defect D7, but architectural: the stage classification (X2: intrinsic /
framework-specific / crosswalk-dependent) subtly assumes convergence is normal and divergence is
a special case.

**Decision:**  
Rewrite X2's classification scheme as neutral (see D7 decision). Update PROGRAM_ROADMAP.md X2
section.

---

### Issue 7: Support disciplines lack clear certification path

**What was found:**  
Support disciplines (research-analyst, first-principles-thinking, etc.) contribute to a stage but
are not the lead. How does their work get certified? Does the lead's adversary audit them?

**Decision:**  
Support discipline work is certified through the lead's adversary. Example: In P1 (pre-registration),
`data-scientist-adversary` certifies the entire register, including contributions from
`research-analyst` and `first-principles-thinking`. This is documented in AGENT_SYSTEM.md under
"Support disciplines."

---

### Issue 8: No escalation path for deadlock cycles

**What was found:**  
If a producer and adversary deadlock (default 3 rounds), an arbiter (3rd model / fresh context)
is invoked. But if the arbiter also disagrees, what happens? Infinite loop?

**Decision:**  
After arbiter round, if still unresolved: escalate to human tripwire. Tripwire decision is final
and recorded as a limitation in the certificate. This is documented in AGENT_SYSTEM.md atomic
operation section.

---

### Issue 9: Tier-2 adversary stance rotation not fully specified

**What was found:**  
AGENT_SYSTEM.md says adversaries use "rotating review stance" but does not define the rotation
algorithm. If two artifacts are submitted by the same producer, do they get the same stance or
different ones?

**Decision:**  
Stance rotation is per-artifact, not per-producer. Each artifact gets the stance that has been
used least recently for that discipline. This is managed by `error-coordinator` at registration.
Documented in AGENT_SYSTEM.md "Tier 2" section.

---

### Issue 10: Certificate ledger link to reproducibility unclear

**What was found:**  
The program records "full provenance" in certificates, but it is not clear how the certificate
links to the reproducibility block or transcript.

**Decision:**  
Every certificate includes fields:
- `artifact_id`: Unique identifier (framework + stage + producer + timestamp).
- `transcript_ref`: Path to the transcript (for LLM artifacts).
- `reproduction_block`: Inline reproduction details (seed, container, command, hash).
- `correlated_artifacts`: List of other findings that share inputs.

Registry schema updated in `docs/REGISTRY_SCHEMA.md` (created at P0). Documented in
REPRODUCIBILITY.md.

---

## Program-level decisions

### Decision 1: P0 before P1

**Rationale:**  
Pre-registration must be informed by understanding what can and cannot be measured from the data.
Running S3 (method validation on synthetic data) before freezing thresholds is the right sequence.

**Action:**  
1. P0: Set up harness, test autonomy, document findings.
2. P1 (draft): Write the pre-registration scaffold (question intents, method categories, decision
   criteria).
3. S3: Run method validation on synthetic data; see what distributions and geometries are
   plausible.
4. P1 (freeze): Revise thresholds based on S3 findings; freeze for T1 signature.

**Timeline:** P0 complete by 2026-06-14. P1 → S3 → P1 (freeze) → T1 by 2026-07-15.

---

### Decision 2: Model family limitation is documented, not hidden

**Rationale:**  
The program runs on Anthropic models only. This is not a hidden flaw; it is a design choice
(rapid iteration, integrated tooling, cost). It must be explicit in every artifact that claims
cross-model robustness.

**Action:**  
1. Correct all documentation (done at Deliverable 1).
2. Every Tier-2 certificate includes: "Model independence: tier-level diversity only (Anthropic
   sonnet ↔ opus); cross-framework replication (S9) is the structural robustness check."
3. Any claim of robustness in S7 must have S9 replication or cross-framework replication in
   Tier B to stand. Single-framework findings are robust *within that framework and embedding
   ensemble*, not across model families.

---

### Decision 3: Pre-registration thresholds informed by S3, not guessed at P0

**Rationale:**  
See D2–D5 above. Thresholds for Q3, Q4, X-Q1 will be set after S3 method validation shows what
data geometries are plausible.

**Action:**  
1. P1 (draft) does not freeze thresholds; it names the intents.
2. S3 runs method validation on synthetic data of varying geometries (clustered, random, low-rank,
   high-rank).
3. P1 (freeze) incorporates thresholds chosen to distinguish the geometries S3 found. These are
   now evidence-informed, not pre-guessed.
4. T1 freeze happens after S3, not before.
5. Every downstream certificate notes: "Thresholds set post S3 (informed by synthetic data);
   T1 freeze deferred."

---

### Decision 4: S9 is replication, not recomputation

**Rationale:**  
See D9 and Architecture issue 4. S9 earns the program's strongest robustness by having a second
team independently design methods while blind to the first team's choices.

**Action:**  
1. Redesign S9 stage description in PROGRAM_ROADMAP.md and AGENT_SYSTEM.md.
2. S9 lead is a second `data-scientist` and `ml-engineer` team.
3. They receive:
   - The S4 corpus (same as original team).
   - The P1 pre-registration (same questions).
   - The S3-certified method menu (same tools available).
4. They do NOT receive:
   - The original S7 findings.
   - The original team's method choices.
   - The original team's exploratory analyses.
5. Output: S9 findings. Replication is declared if original and S9 findings agree within CIs;
   disagreement is also a finding (not a failure).

---

### Decision 5: X1 has a human gate (T2.5: crosswalk freeze)

**Rationale:**  
The crosswalk is the alignment substrate for all of Tier B. If it is flawed, every cross-framework
claim is weakened. A human should confirm it is adequate before Tier B scales up.

**Action:**  
1. Add T2.5 (human tripwire) between X1 and X2.
2. Gate criteria: human reviews X1's alignment quality report and signs off.
3. Time estimate: 2 hours (one human read).
4. Escalation: if crosswalk is deemed inadequate, return to X1 for revision; do not proceed to
   X2 until adequate.

---

## Transcript capture & registry

### Decision 6: Capture transcripts from day one

**Rationale:**  
The program's provenance record is the full transcript (agent reasoning) + certificate (adversary
verdict). Both must be captured and archived from P0.

**Action:**  
1. Create `scripts/capture-transcript.sh` and `scripts/capture-transcript.py` (see Deliverable 3).
2. Every agent run saves its conversation transcript to `transcripts/<stage>/<framework>/<agent>-<timestamp>.md`.
3. At registration, the `context-manager` links the transcript via `transcript_ref` in the
   registry entry.
4. This transcript is part of the permanent record (in git, in the registry, in the release
   package).

---

## Open questions at end of P0

None. All major pre-registration and architecture issues identified in P0 have decisions
recorded above. The program is cleared to proceed to P1 (pre-registration draft) with these
findings and decisions bound.

---

## Signatures & approval

| Role | Status | Notes |
|------|--------|-------|
| Orchestrator (Thomas Jones) | — | Approved; P0 infrastructure stands up based on these findings. |
| data-scientist-adversary | PASS | Falsification-probe stance found no presupposing questions or outcome-rewarding rules post-correction. Assumption ledger: program structure (two tiers, same-discipline adversary, cross-framework replication) is sound; model family limitation is now explicitly documented. |
| first-principles-thinking | PASS | Reviewed program's logical coherence; confirmed that the staged sequence (P0 → P1 → S3 → P1-freeze) addresses the pre-registration defects. |
| agent-organizer | PASS | Roster and pairings confirmed; agent infrastructure (Tier 0–3) can support the stage graph. |

---

## Artifacts produced by P0

1. **AGENT_SYSTEM.md** — corrected model independence claim, added honest accounting section.
2. **PROGRAM_ROADMAP.md** — updated S9 and Q2/Q3 descriptions.
3. **REPRODUCIBILITY.md** — guide to reproducing any artifact (computational vs. LLM).
4. **scripts/capture-transcript.sh** — bash script for transcript capture.
5. **scripts/capture-transcript.py** — Python equivalent.
6. **transcripts/P0/_program/orchestrator-orientation-2026-06-08.md** — this document.
7. **docs/REGISTRY_SCHEMA.md** — registry entry format and fields.
8. **docs/PREREGISTRATION.md (draft revision)** — pre-registration scaffold post-corrections.

All artifacts pass adversarial review. P0 is complete. Ready for P1.
