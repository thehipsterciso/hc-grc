# hc-grc — Program Governance

## What this program is

Empirical, peer-review-grade characterization of GRC control frameworks as structured corpora.
Each framework is studied independently with the same rigorous pipeline; findings are then
synthesized across frameworks. The program is executed by autonomous agents, with every artifact
certified by a same-discipline adversary before it is accepted.

## The first principle: findings first, stance last

This program proves nothing on entry. It exists to *characterize*, and to find insight and gaps —
not to substantiate a position. Theorizing a stance is a single, late, explicitly-separated stage
(`synthesis/`, stage X4) that runs only after the findings exist, and it is itself adversary-gated
to resist overclaiming. Prior beliefs — including any conclusion reached in earlier exploratory
work — are inadmissible until re-derived here under pre-registration.

This is not a slogan. It is enforced:
- No research question may be phrased to presuppose its answer.
- No success criterion may reward a particular outcome.
- The `falsification-probe` and `competing-hypotheses` adversary stances reject any artifact that
  reaches for a desired result.

## Hard constraints

1. **Autonomous execution.** The coordinator runs the stage graph; agents do the work. No human
   approves mid-run except at the named tripwires below.
2. **Same-discipline adversary on every artifact.** Producer and adversary are the same discipline,
   different mental model (rotating stance), different tier within the Anthropic family (sonnet →
   opus). Nothing enters the registry without a passing certificate. See `agents/` and
   `docs/PROGRAM_ROADMAP.md`.
3. **Pre-registration before data.** Every question carries a falsifiable hypothesis (or a neutral
   descriptive aim), an analysis plan, and a decision rule with thresholds set *before* results.
   No post-hoc thresholds in any inference path.
4. **Methods validated on ground truth before use.** No method touches a real framework until it is
   shown to recover known structure in synthetic data at the relevant n and geometry.
5. **Instrument validated before findings.** An embedding is certified to measure governance
   semantics (construct validity, cross-model stability) before any study consumes it.
6. **Bootstrap CIs on everything; multiple indices; permutation tests for structural claims.**
   No bare point estimates. No single-metric conclusions.
7. **Robust vs provisional, earned not asserted.** "Robust" requires replication across the
   embedding ensemble and, for cross-framework claims, replication across independently-authored
   frameworks.
8. **Full provenance.** Every artifact registered with producer, adversary, stance, certificate,
   revision history, source version, and git commit.
9. **No predetermined thesis, no external thesis vehicle.** The program references no downstream
   conclusion or product. Its output is a characterization and, separately and last, a stance
   derived from it.

## Human tripwires (the only points that wait on a person)

- **T1 — Freeze the pre-registration** (program-wide questions, methods, decision rules).
- **T2 — Confirm each framework's licensing** before ingesting its text (trivial for the open
  first wave; a real fork for any paywalled expansion).
- **T3 — Freeze the embedding-selection criterion** (shared across frameworks; must be orthogonal
  to every question it feeds).
- **T4 — Sign off the stance synthesis** before it is written — the guard on the one derivative,
  interpretive step.
- **T5 — Publication.**

Everything between these runs hands-off.

## What not to do

- Do not wire any conclusion into a question, method, or success criterion.
- Do not let an agent accept its own work; spawn the same-discipline adversary.
- Do not accept conditional approvals; revise and re-audit until clean.
- Do not call correlated evidence (studies sharing an embedding or a framework) "independent."
- Do not proceed past a tripwire without the human signature.
- Do not import a prior stance as an assumption. It is a finding to be re-earned or discarded.

## Structure

```
docs/PROGRAM_ROADMAP.md     two-tier stage architecture
docs/PREREGISTRATION.md     frozen register (T1)
frameworks/<name>/          per-framework study (pipeline instance)
frameworks/_TEMPLATE/       study scaffold for adding a framework
synthesis/                  cross-framework triangulation, insight/gap, stance
agents/                     adversary-agent references (framework category 11)
```
