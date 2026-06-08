# hc-grc — Program Roadmap

**Version:** 1.0 (draft)
**Date:** 2026-06-08
**Premise:** Characterize GRC control frameworks as structured corpora, rigorously and
autonomously, one framework at a time, then synthesize across frameworks. Findings first; any
stance is a late, separate, derived output — never an input.

This roadmap is method-first and conclusion-free. It describes how the program measures structure
and checks itself. It names no expected result, because naming one would corrupt the measurement.

---

## Two tiers

**Tier A — per-framework studies.** Each framework runs the same pipeline (S0–S9) independently and
produces its own structural characterization. The studies do not see each other's results; that
independence is what makes the later cross-framework comparison meaningful.

**Tier B — cross-framework synthesis.** Once the per-framework studies are certified, Tier B aligns
them (using the SCF as crosswalk), tests which structural results replicate *across independently-
authored frameworks*, maps insight and gaps, and only then — last, and gated — derives a stance.

```
            ┌──────────────────────── Tier A (×5, in parallel) ─────────────────────────┐
 P0 setup ─►│ scf · nist-800-53 · nist-csf-2.0 · nist-800-171 · cis-v8                   │
 P1 prereg ►│   each runs:  S1f → (S3 shared) → S4 → S5 → S6 → S7 → S8f → S9             │
            └───────────────────────────────────┬──────────────────────────────────────┘
                                                 ▼
            ┌──────────────────────── Tier B (cross-framework) ────────────────────────┐
            │ X1 alignment (via SCF crosswalk) → X2 cross-framework triangulation →      │
            │ X3 insight & gap map → X4 stance synthesis (late, gated) → X5 release       │
            └───────────────────────────────────────────────────────────────────────────┘
```

Replication of a structural result across the five independently-authored frameworks is the
strongest evidence this program can produce. It is the mechanism that separates a property of
*control space* from an artifact of any one framework's editorial choices.

---

## The layered adversary model (how every artifact is checked)

Each producing agent is shadowed by a same-discipline adversary agent before its artifact is
registered. Three layers of independence, cheapest first:

1. **Competence — same discipline.** `data-scientist-adversary` audits `data-scientist`, etc., with
   a discipline-specific reject checklist. Catches what only a peer would see.
2. **Epistemic independence — different mental model.** The adversary draws a *rotating review
   stance* (independent reconstruction · falsification probe · competing hypotheses · assumption
   ledger · premortem) that differs from the producer's. It never re-reasons the producer's path.
3. **Tier-level independence — different tier within the Anthropic family.** The adversary runs on
   `opus` (a higher tier) while the producer runs on `sonnet`, providing weight-level diversity
   within the Anthropic model family.

A per-stage **cross-discipline** backstop (`competitive-analyst` + `product-manager`) audits each
stage's accepted set for the one thing same-discipline review cannot catch: a defect the whole
discipline shares. Adversaries live in `agents/adversarial-review/` (loaded at runtime from `.claude/agents/`); the full agent system is in `docs/AGENT_SYSTEM.md`.

`context-manager` registers an artifact only with a passing certificate; `error-coordinator` keeps
the defect/certificate ledger that *is* the provenance record.

---

## Tier A — the per-framework pipeline

Run once per framework, the five in parallel. P0 and P1 are shared program-level stages; S3's
method validation is shared (a method certified on ground truth is trusted for all frameworks).

### P0 — Program setup & autonomy harness  *(shared, once)*
Stand up the coordinator, the certified-only registry, the issue/certificate ledger, reproducible
compute, and the adversary pairings. Exit: the harness can run a trivial task and self-reject a
seeded-bad artifact.
Agents: `agent-organizer`, `multi-agent-coordinator`, `context-manager`, `error-coordinator`,
`mlops-engineer`, `git-workflow-manager`.

### P1 — Pre-registration  *(shared, once — human tripwire T1)*
Convert the program's aims into a register of questions, each with a falsifiable hypothesis or a
neutral descriptive aim, an analysis plan, and a decision rule with thresholds **set now**. Covers
both the per-framework questions and the cross-framework questions. Frozen and hashed.
Lead: `research-analyst`, `first-principles-thinking`, `data-scientist`. Adversary:
`data-scientist-adversary` (falsification-probe + assumption-ledger). Output: `PREREGISTRATION.md`.

### S1f — Framework question instantiation
Bind the registered questions to this framework's specifics (its taxonomy, control granularity,
metadata). No new questions invented post-hoc; only instantiation of the frozen register.

### S3 — Method validation on ground truth  *(shared)*
Prove each method recovers known structure in synthetic corpora at the relevant n and geometry
before it touches any real framework. Methods that fail are dropped. Adversary:
`data-scientist-adversary` (independent-reconstruction on a different generator).

### S4 — Corpus construction & provenance  *(per framework — human tripwire T2)*
Ingest the framework's controls into per-control assets with full lineage. Confirm the license
(trivial for the open first wave). The SCF study additionally builds the **crosswalk** table that
Tier B aligns on. Lead: `data-engineer` + `legal-advisor`/`license-engineer`. Adversary:
`data-engineer-adversary` (row-count reconciliation, lineage, silent nulls).

### S5 — Measurement instrument: embedding ensemble  *(per framework — human tripwire T3)*
Build the three-model ensemble over this framework's enriched control text. The selection criterion
is frozen once at program level, orthogonal to every question it feeds. Lead: `nlp-engineer`,
`ml-engineer`, `llm-architect`. Adversaries: `nlp-engineer-adversary`, `ml-engineer-adversary`,
`llm-architect-adversary`.

### S6 — Instrument construct validity
Certify that the embedding measures governance semantics, not surface text (cross-model CKA,
construct-validity probes). Dimensionality and cluster tendency are reported here as *properties of
the instrument*, not as findings. Adversary: `data-scientist-adversary` + `ml-engineer-adversary`.

### S7 — Investigations  *(one study per registered question)*
Each study: pull its question from the frozen register → use only S3-certified methods → run across
the ensemble with bootstrap CIs and multiple indices → pass the adversary gate → register the
finding labeled robust (replicates across the ensemble) or provisional. Lead: `data-scientist`,
certified by `data-scientist-adversary`. The question set is whatever the register holds; it is the
same set for every framework so results are comparable in Tier B.

### S8f — Within-framework triangulation
Build this framework's evidence-dependency graph: which findings share the embedding, which are
independent. Assign robust/provisional by demonstrated convergence. Adversary:
`knowledge-synthesizer-adversary`.

### S9 — Adversarial replication
A second, independently-spawned team, blind to the original results, re-runs the framework's
critical studies from the registered corpus + pre-registration using independently-selected methods
from the certified menu. Reproduction within CI is the bar. Output: a replication certificate per
critical finding.

---

## Tier B — cross-framework synthesis

Begins only when at least two per-framework studies are certified through S9. This is where the
program's distinctive evidence is made — and where the discipline against premature conclusions
matters most.

### X1 — Alignment
Map each framework's controls onto a common substrate so structural results can be compared. The
SCF crosswalk (from `frameworks/scf/`, S4) is the alignment layer: it relates controls across the
five frameworks. Alignment quality is itself measured and carried as a limitation — a noisy
crosswalk weakens every cross-framework claim and must not be hidden.
Lead: `data-engineer` + `data-scientist`. Adversary: `data-engineer-adversary` (crosswalk coverage,
many-to-many fan-out), `data-scientist-adversary`.

### X2 — Cross-framework triangulation
For each structural result found per-framework (taxonomy coherence, intrinsic dimensionality,
cluster structure, network/redundancy, coverage gaps), test whether it **replicates across the
five independently-authored frameworks**. Classify each result:
- **Intrinsic** — holds across frameworks (strong evidence it is a property of control space).
- **Framework-specific** — holds in some, not others (a property of those frameworks' design).
- **Crosswalk-dependent** — sensitive to alignment quality (report with that caveat).

This is the program's strongest output. A result that survives five independent framework designs is
far harder to dismiss than the same result in any one corpus.
Lead: `data-scientist` + `knowledge-synthesizer`. Adversary: `knowledge-synthesizer-adversary`
(rejects any "intrinsic" label not earned by demonstrated cross-framework replication; rejects
correlated evidence called independent).

### X3 — Insight & gap map
From the triangulated results, assemble: where frameworks agree, where they diverge, where coverage
is thin or isolated, where their taxonomies fracture. This is a *description of what was found*, not
an argument. Each item carries its evidence class from X2 and its limitations.
Lead: `knowledge-synthesizer` + `data-scientist`. Adversary: `knowledge-synthesizer-adversary`.

### X4 — Stance synthesis  *(late, derivative, gated — human tripwire T4)*
Only here does the program theorize. Taking the X3 map as the sole input, articulate a defensible
stance about control space — what the structure implies, what it challenges, what remains open. The
adversary's explicit job at this stage is to **resist overreach**: every claim must trace to an X2
result of stated evidence class, and any leap beyond the evidence is rejected. A human signs off
before this stage is written, acknowledging it is interpretive.
Lead: `knowledge-synthesizer`, with `first-principles-thinking`. Adversaries:
`knowledge-synthesizer-adversary` (premortem + competing-hypotheses stances) and the cross-discipline
backstop (`competitive-analyst` for novelty/defensibility, `product-manager` for overclaim).

### X5 — Release  *(human tripwire T5)*
Two congruent tracks: a peer-review-ready scientific record (every claim cited to an artifact) and,
separately, a translation for non-technical leadership (every claim traced to a scientific section,
no overclaim, no fear-selling). Reproducibility package: clone → run → results. One human read
before release. Lead: `documentation-engineer`, `technical-writer`, `product-manager`. Adversaries:
`documentation-engineer-adversary`, `technical-writer-adversary`.

---

## Human tripwires

Everything else runs hands-off. Five points wait on a person, each because it is irreversible or
interpretive:

| Tripwire | Where | Why a human |
|---|---|---|
| **T1** Freeze pre-registration | P1 | The contract the whole program is held to. |
| **T2** Confirm framework licensing | S4 (×5) | Trivial for the open wave; a real legal/cost fork for paywalled expansion. |
| **T3** Freeze embedding-selection criterion | S5 | Every embedding-based finding inherits it; must stay orthogonal to the questions. |
| **T4** Sign off stance synthesis | X4 | The one interpretive step; the place confirmation bias would enter. |
| **T5** Publication | X5 | The science goes out under your name. |

---

## Sequencing & parallelism

- **P0, P1, S3 are shared and run once.** A method certified on ground truth is trusted for all five frameworks.
- **The five per-framework pipelines (S1f–S9) run in parallel.** They are independent by design.
- **`frameworks/scf/` is on the critical path for Tier B** because it produces the crosswalk X1 needs. Prioritize its S4.
- **Tier B starts incrementally:** X1–X2 can begin as soon as the second framework clears S9 (SCF + one native framework), then re-runs as each additional framework lands — so cross-framework power grows rather than waiting for all five.

## Critical path

To a *complete, replicated characterization* (not to any particular result):

**P0 → P1(T1) → S3 → [frameworks/scf S4(T2) + one native framework S4] → S5(T3) → S6 → S7 → S8f → S9 → X1 → X2 → X3 → X4(T4) → X5(T5).**

The first synthesis is meaningful at two frameworks; it strengthens monotonically as the remaining
three land. There is no "headline" milestone — the milestone is a characterization that reproduced
across frameworks and survived blind replication, whatever it turned out to say.

*Two tiers: characterize each framework, then test what survives across all of them. Findings first,
stance last and gated, no conclusion wired in. Everything else is sequencing.*
