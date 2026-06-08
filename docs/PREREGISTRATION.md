# hc-grc — Pre-Registration

**Status: DRAFT — NOT FROZEN.** This register becomes binding only when frozen and hashed at human
tripwire T1. Until then it is a scaffold. After freezing, it is immutable; thresholds may not be
changed after results are seen.

**Rule of admissibility.** Every question below is phrased to be answerable in any direction. No
question presupposes its answer; no decision rule rewards a particular outcome. A result that
confirms a framework's own claims about itself is as publishable as one that refutes them.

---

## Frameworks in the first wave

| ID | Framework | License | Native text | Role |
|----|-----------|---------|-------------|------|
| F1 | Secure Controls Framework | Creative Commons | yes | corpus + crosswalk |
| F2 | NIST SP 800-53 Rev 5 | public domain | yes (OSCAL) | corpus |
| F3 | NIST CSF 2.0 | public domain | yes | corpus |
| F4 | NIST SP 800-171 Rev 3 | public domain | yes (OSCAL) | corpus |
| F5 | CIS Controls v8 | open terms | yes | corpus |

The same question set (Q1–Q8) is run on every framework so results are comparable in Tier B.

---

## Per-framework questions (run on F1–F5)

For each: **aim** (neutral), **hypothesis** (falsifiable, directional only where a direction is
meaningful), **method** (must be S3-certified), **decision rule** (threshold set at freeze, never
after).

**Q1 — Corpus structure (descriptive).** What is the statistical distribution of the corpus (text,
control count, category balance, coverage)? *No hypothesis; descriptive baseline.*

**Q2 — Intrinsic dimensionality.** What is the intrinsic dimensionality of the control embedding
space? *Aim: estimate it with CIs. No target value is assumed.* Method: TwoNN + parallel analysis +
participation ratio consensus. Decision rule: report the estimate and its interval; no pass/fail.

**Q3 — Cluster tendency.** Does the embedding space exhibit non-random cluster structure?
H0: spatial distribution is random (Hopkins H ≤ [threshold @freeze]). Method: Hopkins + permutation.

**Q4 — Taxonomy coherence.** Are the framework's own control categories semantically coherent —
do controls within a category sit closer than controls across categories? H0: intra ≤ inter
(categories are not reflected in content). Method: permutation test + per-category profile + ANOVA.
*Both outcomes are findings: coherent taxonomy and imposed taxonomy are equally reportable.*

**Q5 — Emergent grouping.** What groupings emerge from content alone, and how do they relate to the
framework's imposed taxonomy? Method: HDBSCAN + k-means, full validity panel, ARI/NMI vs taxonomy.

**Q6 — Internal reference structure.** What is the topology of the framework's internal
cross-references / control relationships (where present)? Method: graph construction + community
detection + permutation on modularity.

**Q7 — Coverage & gaps.** Where is coverage thin, isolated, or sparse? Method: nearest-neighbor
distance distribution + KDE, threshold-free with FDR control. *No post-hoc cut in the inference path.*

**Q8 — Dimensional structure vs low-dimensional schemas.** How does the measured dimensional
structure relate to common low-dimensional governance schemas (e.g., the CIA triad)? *Open
measurement: the answer may be that such a schema captures the structure well, partially, or poorly.
No outcome is favored.* Method: rotated PCA + concept-vector correlation + variance accounting, with
CIs. Decision rule: report the fraction of structure aligned with each schema and its interval.

---

## Cross-framework questions (Tier B, run in synthesis)

**X-Q1 — Replication class.** For each per-framework result (Q2–Q8), does it replicate across F1–F5?
Classify each as intrinsic (holds across frameworks), framework-specific, or crosswalk-dependent.
Decision rule: "intrinsic" requires the result to hold in ≥ [k @freeze] of 5 frameworks within
overlapping CIs.

**X-Q2 — Convergent dimensional structure.** Do independently-authored frameworks converge on a
common dimensional structure of control space? *Open: convergence, partial convergence, or
divergence are all reportable outcomes.* Method: cross-framework comparison of Q2/Q8 results on the
aligned substrate, with alignment quality carried as a limitation.

---

## Decision-rule discipline

- Thresholds for Q3, Q4, X-Q1 are set at freeze (T1), before any data is embedded.
- No threshold, cutoff, or subgroup may be introduced after results are seen. The
  `falsification-probe` adversary stance rejects any artifact that does.
- Every estimate carries a 95% bootstrap CI. Structural claims carry a permutation test.
- "Robust" requires ensemble replication; "intrinsic" requires cross-framework replication.

---

## To freeze (T1 checklist)

- [ ] Thresholds set for Q3, Q4, X-Q1.
- [ ] Method for each question is S3-certified or scheduled for S3.
- [ ] `data-scientist-adversary` (falsification-probe + assumption-ledger) certifies the register
      contains no presupposing question and no outcome-rewarding rule.
- [ ] Human signature; register hashed and made immutable.
