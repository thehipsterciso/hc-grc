# hc-grc — Pre-Registration

**Program:** hc-grc — Empirical characterization of GRC control frameworks as structured corpora
**Date drafted:** 2026-06-08
**Version:** 2.0-draft
**sha256:** [FROZEN AT T1 — not yet assigned]

**Status: DRAFT — NOT FROZEN.**
This document becomes binding only when hashed and signed at human tripwire T1. Until T1, it is
a pre-freeze draft subject to adversary review. After T1, it is immutable: no question, method
description, threshold, exclusion criterion, or decision rule may be changed after results are seen.

**Rule of admissibility.** Every question is phrased to be answerable in any direction. No question
presupposes its answer. No success criterion rewards a particular outcome. A result that challenges
a framework's stated structure is as publishable as one that confirms it. A null result is a finding.

---

## 1. Purpose and scope

This document pre-registers all research questions, neutral and falsifiable hypotheses, analysis
plans (what is measured and how results are classified — not which algorithms implement the
measurements), decision rules, and their deferred thresholds for the hc-grc program.

It covers:
- Per-framework questions (Q1–Q7): answered once per framework in stage S7.
- Cross-framework questions (X-Q1–X-Q3): answered in Tier B stage X2 after all five frameworks
  clear S9.

What this document does NOT do:
- Name any algorithm, implementation, or software library. Method selection occurs in S3.
- Set any numeric threshold. Thresholds are set after S3 validates methods on synthetic ground
  truth at the relevant n and geometry, and are recorded in this document before any real framework
  data is analyzed.
- Presuppose any result. The program characterizes; it does not confirm.

---

## 2. Hard constraints (immutable after T1)

1. No question may be rephrased after T1.
2. No threshold may be introduced or changed after results are seen.
3. No exclusion criterion may be added after data ingestion begins.
4. No algorithm may be substituted for a certified one without re-running S3 for that method.
5. No finding may be labeled "robust" without replication across the full embedding ensemble.
6. No finding may be labeled "intrinsic" without cross-framework replication meeting the
   criterion registered in X-Q1 (set at T1 freeze).
7. Cross-discipline backstop (`competitive-analyst`, `product-manager`) audits every stage's
   accepted set before it advances.

---

## 3. Framework roster

| ID | Framework | License | Native text | Role in program |
|----|-----------|---------|-------------|-----------------|
| F1 | Secure Controls Framework (SCF) | Creative Commons | yes | corpus + crosswalk substrate |
| F2 | NIST SP 800-53 Rev 5 | public domain | yes (OSCAL) | corpus |
| F3 | NIST CSF 2.0 | public domain | yes | corpus |
| F4 | NIST SP 800-171 Rev 3 | public domain | yes (OSCAL) | corpus |
| F5 | CIS Controls v8 | open terms | yes | corpus |

---

## 4. Structural limitations registered upfront

These limitations are known before data is analyzed. They constrain how findings are interpreted
and must be reported in every artifact that relies on the affected structures.

### L1 — SCF dual role (circularity risk)

F1 (SCF) serves two distinct roles:
1. It is a Tier A study corpus: its control text is analyzed as an independent framework subject.
2. It is the crosswalk substrate for Tier B X1 alignment: its control mappings are used to relate
   the other four frameworks for cross-framework comparison.

**Risk:** If the SCF corpus has structural artifacts (e.g., systematic coverage biases, unusual
dimensional structure, or idiosyncratic clustering), those artifacts may propagate through the X1
crosswalk into every cross-framework comparison. A cross-framework result could then reflect SCF's
structural peculiarities rather than a genuine property of control space.

**Mitigations (both required):**
1. Crosswalk quality is independently measured in X1 and carried as a quantified limitation on
   every downstream X2 claim.
2. A sensitivity analysis in X2 tests each cross-framework claim with SCF excluded from the X1
   alignment substrate, using an alternative alignment approach (registered at X1 design time).
   Any X2 result that does not survive this exclusion is classified as "crosswalk-dependent" and
   may not be labeled "intrinsic."

### L2 — NIST authorship cluster (independence constraint)

F2 (NIST SP 800-53 r5), F3 (NIST CSF 2.0), and F4 (NIST SP 800-171 r3) share NIST authorship,
editorial conventions, and framework lineage. They are not three independently-authored corpora.

**Consequence for evidence classification:**
- Agreement among F2, F3, and F4 alone does not constitute independent replication. They form a
  correlated cluster; treat them as a single data point for independence purposes.
- For a cross-framework result to qualify as "intrinsic" under X-Q1, it must replicate across at
  least one non-NIST framework (F1 SCF or F5 CIS Controls v8) in addition to any NIST cluster
  agreement.
- The replication count for X-Q1's threshold (set at T1 freeze) is parameterized by
  independent-authorship groups, not raw framework count. The maximum independent groups in this
  wave are: NIST cluster (1 group), SCF (1 group), CIS Controls v8 (1 group) = 3 independent
  authorship groups across 5 frameworks.

---

## 5. Assumptions ledger

Each assumption the analysis rests on is registered here with its falsifying condition and the
consequence if false.

| # | Assumption | What would falsify it | Consequence if false |
|---|------------|-----------------------|----------------------|
| A1 | Embedding vectors carry governance-semantic signal beyond surface-text similarity | S6 construct-validity probes show the embedding cannot distinguish governance-relevant from governance-irrelevant text at above-chance rates | Invalidates all embedding-based findings; S6 acts as gate |
| A2 | Cross-model embedding agreement (measured by CKA in S6) is sufficient to treat the ensemble as convergent | CKA between any two ensemble models falls below the S6-registered convergence threshold | Degrades confidence; findings labeled provisional until a third model is added or the failing pair is replaced |
| A3 | S3-certified methods applied to real framework corpora behave within the performance envelope observed on synthetic data | A method produces degenerate or non-convergent output on a real corpus (see stopping rule, section 8) | Method failure recorded; finding for that question reported as "method failure" with observed failure mode |
| A4 | The SCF crosswalk covers the other frameworks at sufficient density for X1 alignment | Crosswalk coverage analysis in X1 finds fewer than [DEFERRED — set after S4 crosswalk build] of controls in any framework mapped | Degrades X2 for that framework; cross-framework claim for that framework is labeled "crosswalk-dependent" |
| A5 | Control text as ingested (post-exclusion, section 7) is representative of each framework's intended semantic content | A systematic comparison of included vs excluded controls reveals the exclusion criteria are correlated with semantic content | Report the correlation as a limitation; do not apply post-hoc inclusion changes |
| A6 | The bootstrap CI procedure (section 9) is valid for the sample sizes encountered | Effective sample size for any framework falls below the minimum established in S3 power analysis | Report CI as unreliable for that framework; label finding provisional |

---

## 6. Evidence class definitions

These definitions are fixed here. They apply to every finding produced in S7, S8f, S9, and X2.

**Robust:** A finding replicates across all three models in the embedding ensemble (S7 ensemble
convergence) AND survives the S9 blind replication within overlapping confidence intervals.

**Provisional:** A finding replicates across all three models in the embedding ensemble but has
not yet completed S9 blind replication.

**Framework-specific:** A finding holds in some frameworks but not others in X2, where the
pattern is not explained by the NIST authorship cluster or SCF circularity.

**Crosswalk-dependent:** A cross-framework finding that does not survive the SCF-exclusion
sensitivity analysis in X2 (see L1 mitigation 2). May not be labeled "intrinsic."

**Intrinsic:** A finding classified as Robust that replicates across at least two independent
authorship groups (see L2), at least one of which is non-NIST, meeting the X-Q1 threshold (set
at T1 freeze).

**Method failure:** A method produced degenerate or non-convergent output on the target corpus.
No result is imputed. The failure mode is documented.

---

## 7. Pre-analysis exclusion criteria

The following exclusion criteria are registered now. No exclusion criterion may be added or
modified after data ingestion begins in S4.

Controls are excluded from embedding-based analysis if they meet ANY of the following:

1. **Null or empty text:** The control's primary text field (title + description combined) is null,
   empty, or contains only whitespace after stripping.
2. **Duplicate control ID:** Where the same control ID appears more than once in the ingested
   corpus, only the first occurrence (by source file ordering) is retained; duplicates are logged.
3. **Below minimum token length:** Controls whose combined title + description text falls below
   [DEFERRED — set after S3 token-length sensitivity analysis] tokens are excluded. This threshold
   applies uniformly across all frameworks.
4. **Placeholder/stub text:** Controls whose text matches a known stub pattern (e.g., "[TBD]",
   "[Placeholder]", "Reserved") are excluded and logged.

Exclusions are logged with reason code. The count and proportion of excluded controls per
framework are reported as corpus characteristics in Q1.

---

## 8. Stopping rule

If a method certified in S3 fails to converge or produces degenerate output on a real framework
corpus (a failure mode not observed or recoverable in S3), the procedure is:

1. The failure is recorded in the finding slot for that question as "method failure" with the
   observed failure mode (non-convergence, empty output, singular matrix, etc.).
2. No result is imputed, interpolated, or substituted.
3. No alternative uncertified method may be used to fill the gap.
4. The `error-coordinator` opens a defect issue. A second S3 cycle on a replacement method may
   be initiated — but any replacement method must complete S3 certification before it touches any
   real framework corpus.
5. The affected question is reported as "pending method replacement" until either a certified
   replacement succeeds or the question is retired from the register by explicit human sign-off.

---

## 9. Bootstrap CI parameters

These parameters are registered now and apply uniformly to all quantitative findings.

- **Iterations:** 10,000
- **Confidence level:** 95%
- **Method:** Bias-corrected and accelerated (BCa)
- **Scope:** All point estimates in S7 and X2 carry a BCa bootstrap CI computed with these
  parameters. No bare point estimate appears in any registered finding.

---

## 10. Embedding ensemble design

- **Ensemble size:** 3 models. This is a registered design decision.
- **Model selection:** The specific models are selected at S5 under the criterion frozen at T3.
  That criterion must be orthogonal to every research question in this document — i.e., it may
  not prefer models that produce high or low values on any measure this program intends to study.
- **Ensemble convergence:** Agreement across all three models is required to label a finding
  "robust" (see section 6).
- **CKA threshold for convergence:** [DEFERRED — set after S6 baseline on first framework].
  Registered here before any cross-model CKA is computed on real data.

---

## 11. Per-framework questions (S7 — answered once per framework, F1 through F5)

Each question follows this structure:
- **Aim:** neutral statement of what is being measured.
- **Hypothesis / null hypothesis:** what is being tested; the null is the default.
- **Falsifiability:** what result would show the null holds or the hypothesis is false.
- **Analysis plan:** what is measured and how results are classified (no algorithm names).
- **Success criterion:** the study succeeds if the method is applied correctly and findings are
  reported regardless of direction.
- **Thresholds:** all deferred to post-S3 (see section 12).

---

### Q1 — Corpus structure (descriptive baseline)

**Aim:** Characterize the statistical distribution of the ingested corpus: total control count,
distribution of text length per control, category membership counts, and metadata completeness.

**Hypothesis:** None. Q1 is a descriptive baseline. No inference is drawn.

**Falsifiability:** N/A (descriptive).

**Analysis plan:** For each framework, compute and report: total control count after exclusions
(section 7), text length distribution (median, IQR, min, max, with a summary plot), count and
proportion of controls per taxonomy category, and count and proportion of excluded controls with
reason codes. No embedding is used.

**Success criterion:** The study succeeds if the corpus statistics are computed and reported
completely, including exclusion counts.

**Thresholds:** None applicable.

---

### Q2 — Intrinsic dimensionality

**Aim:** Estimate the intrinsic dimensionality of the framework's control embedding space — the
number of dimensions that captures the meaningful variance in the control corpus.

**Hypothesis:** Neutral — no target dimensionality is assumed. Both high and low dimensionality
are informative findings.

**Null hypothesis:** Not applicable as a binary test. The aim is estimation with a CI, not a
pass/fail test.

**Falsifiability:** The estimate is falsified if an independent team using different S3-certified
dimensionality estimation methods produces an estimate outside the CI reported here (assessed in
S9).

**Analysis plan:** Apply a minimum of two independent S3-certified dimensionality estimation
methods to the embedding ensemble. Report the estimate and BCa bootstrap CI from each method and
each ensemble model. Where estimates agree across methods and models, report the consensus range.
Where they disagree, report both and characterize the disagreement.

**Success criterion:** The study succeeds if at least two certified methods produce estimates with
CIs, regardless of the magnitude of the estimated dimensionality.

**Thresholds:** Method selection and any convergence criterion are [DEFERRED — set after S3].

---

### Q3 — Cluster tendency

**Aim:** Test whether the control embedding space exhibits non-random spatial structure —
specifically, whether it is more clustered than would be expected by chance given the same
marginal distributions.

**Hypothesis:** The embedding space exhibits non-random cluster tendency.

**Null hypothesis (H0):** The spatial distribution of control embeddings is consistent with
random sampling from the marginal distributions (no excess clustering).

**Falsifiability:** H0 is not falsified if the cluster tendency statistic, computed on the
observed embedding, falls within the null distribution generated by permutation. H is falsified
if the statistic is outside that distribution at the registered significance level.

**Analysis plan:** Apply an S3-certified cluster tendency test to the embedding ensemble. Generate
a permutation null distribution. Report the observed statistic, the null distribution summary,
and whether the observed value falls outside the null at the registered significance level. Run
across all three ensemble models; report agreement and disagreement.

**Success criterion:** The study succeeds if the test is run and the result (reject H0 or fail
to reject H0) is reported for all three ensemble models, regardless of direction.

**Thresholds:**
- Significance level for H0 rejection: [DEFERRED — set after S3]
- Cluster tendency statistic threshold: [DEFERRED — set after S3]

---

### Q4 — Taxonomy coherence

**Aim:** Test whether the framework's own control taxonomy is reflected in the semantic content
of its controls — i.e., whether controls in the same category are semantically more similar to
each other than to controls in other categories.

**Hypothesis:** The framework's taxonomy is reflected in control semantics (intra-category
semantic similarity exceeds inter-category semantic similarity).

**Null hypothesis (H0):** Intra-category semantic similarity is not greater than inter-category
similarity. The taxonomy is not recoverable from control content alone.

**Falsifiability:** The hypothesis is falsified if intra-category similarity does not exceed
inter-category similarity at the registered threshold after permutation testing, or if the
permutation test fails to reject H0. Both outcomes — coherent taxonomy and semantically
unrecoverable taxonomy — are equally valid findings.

**Note on Q4 and SCF:** For F1 (SCF), this question is answered on SCF's own taxonomy (Tier A,
per-framework). SCF's role as crosswalk substrate (L1) is a Tier B concern and does not affect
Q4's per-framework interpretation. The Tier B sensitivity analysis (L1 mitigation 2) addresses
the crosswalk propagation risk separately.

**Analysis plan:** Compute pairwise semantic similarity between all controls in the embedding
space. Compute the mean intra-category and inter-category similarity for each category. Apply a
permutation test (permuting category labels) to generate a null distribution for the
intra-minus-inter difference. Report the observed difference, the permutation null distribution,
and a per-category profile showing which categories (if any) exhibit higher-than-chance coherence.
Run across all three ensemble models.

**Success criterion:** The study succeeds if the test is run and results are reported for all
categories and all ensemble models, regardless of whether the taxonomy is found to be coherent
or not.

**Thresholds:**
- Significance level for H0 rejection: [DEFERRED — set after S3]
- Minimum effect size for "coherent" label: [DEFERRED — set after S3]

---

### Q5 — Emergent grouping

**Aim:** Identify what groupings emerge from control content alone (without reference to the
framework's taxonomy), and characterize how those content-derived groupings relate to the
framework's imposed taxonomy.

**Hypothesis:** Neutral — the content-derived groupings may align closely with the taxonomy,
partially align, or not align. All outcomes are informative.

**Null hypothesis (H0):** The correspondence between content-derived groupings and the imposed
taxonomy is no greater than chance.

**Falsifiability:** H0 is not falsified if agreement metrics between content-derived groupings
and taxonomy labels fall within the chance distribution established by permutation. H0 is
falsified if agreement metrics exceed chance at the registered significance level.

**Analysis plan:** Apply one or more S3-certified grouping methods to the embedding space. Select
the number of groups using S3-certified validity indices (multiple indices, not a single one).
Compute agreement between content-derived groupings and the framework's taxonomy using at least
two complementary agreement metrics. Report the grouping structure, the validity index values,
the agreement metrics with BCa CIs, and the permutation null distribution for agreement. Run
across all three ensemble models.

**Success criterion:** The study succeeds if groupings are identified using S3-certified methods,
agreement with taxonomy is quantified, and results are reported regardless of the level of
agreement found.

**Thresholds:**
- Number of groups: [DEFERRED — set after S3 validity index analysis on synthetic data at
  relevant n and geometry]
- Validity index acceptance range: [DEFERRED — set after S3]
- Significance level for H0 rejection: [DEFERRED — set after S3]

---

### Q6 — Internal reference structure

**Aim:** Where a framework contains explicit internal cross-references or stated control
relationships, characterize the topology of that reference network: density, connectivity,
community structure, and the presence of isolated or hub controls.

**Hypothesis:** Neutral — the reference network may be dense or sparse, modular or diffuse, with
or without isolated controls.

**Null hypothesis (H0):** Any observed community structure in the reference network is no greater
than expected by chance given the network's degree sequence.

**Falsifiability:** H0 is not falsified if the modularity of the observed network falls within
the null distribution generated by permutation of the degree sequence. H0 is falsified if
observed modularity exceeds the null at the registered significance level.

**Scope note:** Not all frameworks in this wave have explicit internal cross-references. Where a
framework does not provide them, Q6 is reported as "not applicable — no explicit reference
structure present" and this is not a failure.

**Analysis plan:** Extract the internal cross-reference graph where present. Compute degree
distribution, density, and connected-component structure. Apply an S3-certified community
detection method. Apply a permutation test on the degree sequence to generate a null distribution
for modularity. Report the network topology summary, community assignments, modularity with BCa
CI, and the permutation result. Identify isolated controls (degree zero) and high-degree hub
controls by the registered threshold.

**Success criterion:** The study succeeds if the reference structure is characterized (or
correctly identified as absent), community detection is applied where applicable, and results
are reported regardless of whether modular structure is found.

**Thresholds:**
- Significance level for modularity H0 rejection: [DEFERRED — set after S3]
- Hub degree threshold: [DEFERRED — set after S3]

---

### Q7 — Coverage concentration and gaps

**Aim:** Characterize where the framework's control space is dense and where it is sparse —
identifying regions of concentrated coverage and regions that may constitute gaps relative to
the overall semantic space occupied.

**Hypothesis:** Neutral — the framework may show uniform coverage or may show systematic
concentrations and gaps. Both patterns are informative.

**Null hypothesis (H0):** Coverage density across the control space is spatially uniform (no
control region is significantly more or less dense than expected under a uniform spatial
distribution).

**Falsifiability:** H0 is not falsified if local density estimates across the space do not
deviate from the uniform expectation after multiple-comparisons correction. H0 is falsified if
one or more regions show significantly elevated or depressed density after correction.

**Analysis plan:** Estimate local density across the embedding space using an S3-certified
density estimation method. Compare observed density to a null expectation. Apply false discovery
rate (FDR) correction for multiple comparisons across spatial regions; no uncorrected threshold
appears in the inference path. Identify and report dense regions (coverage concentrations) and
sparse regions (potential gaps) that survive FDR correction. Run across all three ensemble models;
report which density features are consistent across models and which are model-specific.

**Note on CIA triad:** If the analysis plan for dimensional structure (a cross-cutting
measurement) reveals that coverage gaps align with specific conceptual axes (such as the CIA
triad or other low-dimensional governance schemas), this is reported as an observation. The null
for any CIA-triad-related coverage test is: CIA triad representation is uniform across control
categories (no category shows disproportionate CIA coverage relative to its size). This is tested
as a secondary analysis within Q7, not a separate question.

**Success criterion:** The study succeeds if density is estimated and the FDR-corrected result
is reported regardless of whether significant gaps or concentrations are found.

**Thresholds:**
- FDR correction method and alpha: [DEFERRED — set after S3]
- Minimum region size for gap reporting: [DEFERRED — set after S3]

---

## 12. Cross-framework questions (X2 — answered after all five frameworks clear S9)

These questions are answered in Tier B stage X2. They require all five per-framework studies
(S7, S8f, S9) to be certified before being answered. They may be answered incrementally as
frameworks clear S9, but final classification requires all five.

For all cross-framework questions: the NIST independence constraint (L2) and SCF circularity
limitation (L1) apply as registered in section 4. "Intrinsic" classification requires replication
across at least two independent authorship groups, at least one non-NIST.

---

### X-Q1 — Replication classification

**Aim:** For each per-framework result (Q2–Q7), determine whether it replicates across the five
frameworks, and classify each result by evidence class.

**Hypothesis:** Neutral — any classification outcome is a finding.

**Null hypothesis (H0):** Per-framework results do not replicate beyond chance across frameworks
(no systematic cross-framework structure exists).

**Falsifiability:** H0 is not falsified if the proportion of results replicating across
frameworks does not exceed the chance proportion estimated by permuting framework labels. H0 is
falsified if replication exceeds chance at the registered significance level.

**Analysis plan:** For each Q2–Q7 result, assess replication across the aligned frameworks using
overlapping CI agreement. Classify each as: intrinsic, framework-specific, or
crosswalk-dependent (using the definitions in section 6 and the independence constraint in L2).
Apply the SCF-exclusion sensitivity analysis from L1 to all cross-framework claims before
labeling any result "intrinsic." Report the full replication matrix.

**Success criterion:** The study succeeds if every per-framework result is assigned a
classification with its evidence class definition and limitations, regardless of how many results
achieve "intrinsic" classification.

**Thresholds:**
- Minimum frameworks agreeing for "intrinsic" label: [DEFERRED — set after S3, parameterized
  by independent authorship groups per L2]
- Significance level for H0 rejection: [DEFERRED — set after S3]

---

### X-Q2 — Convergent dimensional structure

**Aim:** Test whether independently-authored frameworks converge on a common dimensional
structure of control space, or whether dimensional structure is framework-specific.

**Hypothesis:** Neutral — convergence, partial convergence, and divergence are all reportable
outcomes.

**Null hypothesis (H0):** The dimensional structure estimates from each framework are consistent
with independent draws from a common population (no more similar to each other than expected by
chance).

**Falsifiability:** H0 is not falsified if pairwise similarity of Q2 results across frameworks
does not exceed the chance distribution from permutation. H0 is falsified if cross-framework
similarity exceeds chance.

**Analysis plan:** Compare Q2 (intrinsic dimensionality) and Q7 (coverage structure) results
across frameworks on the aligned substrate from X1. Carry alignment quality as a quantified
limitation on every comparison. Report the degree of convergence with BCa CIs. Apply the
NIST-cluster independence constraint from L2 — agreement among F2, F3, F4 alone is not
reported as independent convergence.

**Success criterion:** The study succeeds if convergence is measured and classified, and the NIST
cluster constraint and SCF circularity limitation are both reported, regardless of whether
frameworks converge.

**Thresholds:**
- Convergence similarity metric: [DEFERRED — set after S3]
- Significance level: [DEFERRED — set after S3]

---

### X-Q3 — Cross-framework coverage agreement and divergence

**Aim:** Characterize where frameworks agree in their coverage concentrations and gaps
(Q7 results), and where they diverge — identifying structural gaps that are consistent across
independently-authored frameworks versus gaps that are specific to individual frameworks or to
the NIST authorship cluster.

**Hypothesis:** Neutral — both consensus gaps and framework-idiosyncratic gaps are informative
findings.

**Null hypothesis (H0):** Coverage gap locations across frameworks are no more consistent than
expected by chance given each framework's corpus size and semantic distribution.

**Falsifiability:** H0 is not falsified if the spatial overlap of gap regions across frameworks
does not exceed the chance overlap from permutation. H0 is falsified if consensus gap regions
are more spatially consistent than chance.

**Analysis plan:** Align the Q7 density and gap maps across frameworks using the X1 alignment.
Compute spatial agreement of gap regions across frameworks. Identify regions where gaps are
consistent across at least two independent authorship groups (per L2) and regions where gaps
are framework-specific. Report the NIST cluster treatment explicitly. Apply the SCF sensitivity
analysis from L1.

**Success criterion:** The study succeeds if coverage agreement is measured and the results are
classified by evidence class (consensus, framework-specific, crosswalk-dependent), regardless
of how many consensus gaps are identified.

**Thresholds:**
- Spatial overlap metric and significance level: [DEFERRED — set after S3]
- Minimum independent authorship groups for "consensus" label: [DEFERRED — set after S3,
  consistent with X-Q1 threshold]

---

## 13. Deferred items register

All items marked [DEFERRED] above are collected here for completeness. Each deferred threshold
must be set and recorded in this document before any real framework data is analyzed at the
relevant stage.

| Item | Question(s) | Set when | Dependency |
|------|-------------|----------|------------|
| Cluster tendency statistic threshold | Q3 | After S3 method validation | S3 certified method selected |
| Significance level (all hypothesis tests) | Q3, Q4, Q5, Q6, Q7, X-Q1, X-Q2, X-Q3 | After S3 | S3 complete |
| Minimum token length for exclusion | Section 7, item 3 | After S3 token-length sensitivity analysis | S3 complete |
| Minimum effect size for "coherent" label (Q4) | Q4 | After S3 | S3 complete |
| Validity index acceptance range and group count (Q5) | Q5 | After S3 on synthetic data at relevant n and geometry | S3 complete |
| Hub degree threshold (Q6) | Q6 | After S3 | S3 complete |
| FDR correction method and alpha (Q7) | Q7 | After S3 | S3 complete |
| Minimum region size for gap reporting (Q7) | Q7 | After S3 | S3 complete |
| CIA triad test null threshold (Q7 secondary) | Q7 | After S3 | S3 complete |
| Minimum frameworks for "intrinsic" label | X-Q1 | After S3, parameterized by L2 | S3 complete |
| Convergence similarity metric and threshold (X-Q2) | X-Q2 | After S3 | S3 complete |
| Spatial overlap metric and threshold (X-Q3) | X-Q3 | After S3 | S3 complete |
| Crosswalk coverage minimum (A4) | X1, X-Q1, X-Q2, X-Q3 | After S4 crosswalk build | S4 SCF complete |
| CKA ensemble convergence threshold | Section 10 | After S6 baseline on first framework | S6 first framework complete |
| Embedding model selection | Section 10 | T3 (human tripwire) | T3 |

---

## 14. T1 freeze checklist

This document is submitted for adversary review by `data-scientist-adversary` (falsification-probe
+ assumption-ledger stance). It becomes frozen only with a passing certificate and human signature.

- [ ] All 16 adversary-identified defects (D1–D16) addressed in this version.
- [ ] No algorithm names anywhere in this document.
- [ ] All thresholds marked [DEFERRED — set after S3] or equivalent.
- [ ] Q4 hypothesis is neutral (no directional presupposition).
- [ ] SCF dual-role circularity documented as structural limitation L1 with mitigation plan.
- [ ] NIST authorship cluster documented as structural limitation L2 with independence constraint.
- [ ] Assumptions ledger present (section 5, 6 entries).
- [ ] Evidence class definitions present (section 6).
- [ ] Pre-analysis exclusion criteria present (section 7, 4 criteria).
- [ ] Stopping rule present (section 8).
- [ ] Bootstrap CI parameters present and uniform (section 9).
- [ ] Embedding ensemble size registered as design decision (section 10).
- [ ] Per-framework questions clearly separated from cross-framework questions.
- [ ] sha256 placeholder present for T1 freeze.
- [ ] Document is a DRAFT — not frozen.
- [ ] `data-scientist-adversary` (falsification-probe + assumption-ledger) certifies this register
      contains no presupposing question and no outcome-rewarding rule.
- [ ] Human signature (Thomas Jones) — T1 tripwire.
- [ ] sha256 hash assigned and recorded above.
