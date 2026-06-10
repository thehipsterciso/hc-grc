# Statistical Analysis Plan (SAP)

> **DEFERRAL NOTICE — 2026-06-10**
> This document is a template. The SAP is finalized at Gate 2, after exploratory characterization of the SCF corpus. Fields marked `[To be populated]` are structurally deferred — populating them before exploratory analysis runs would constitute pre-specification of effect sizes without empirical foundation.
>
> **Locked now (framework pre-registration):** Analytical workflow, hypothesis format, correction methods, split strategy (GroupKFold on SCF control IDs per issue #60), unit of analysis (SCF control, ~1,400 effective observations per issue #67), and model selection criteria (Phase 1/2 protocol per ADR-0013).
>
> **Deferred to Gate 2:** Specific hypotheses, effect size thresholds, primary outcome measures, multiple comparison families.

**Version**: [version]  
**Date locked**: [date — this document is immutable after this date]  
**Pre-registration record**: `protocol/registration/`  

This document specifies every analysis this project will conduct. It is written and committed before any confirmatory analysis runs. Analyses not specified here that are conducted after data examination are exploratory and must be labeled as such in all reporting.

The SAP is a single document. It is not a collection of hypothesis files. Every analysis — primary, secondary, sensitivity, and exploratory — is listed here in one place so the full scope of the analytical program is visible and auditable.

---

## 1. Primary Analysis

The primary analysis is the one the project is fundamentally designed to answer. There is only one. If a project has multiple primary analyses, it has multiple projects.

**Primary question**: [To be populated — maps to CRQ1]

**Primary outcome measure**: [The single metric by which the primary analysis succeeds or fails]

**Statistical test**: [Named test]

**Decision rule**: The primary analysis is considered to support H1 if [specific criterion — effect size, p-value, CI — stated here].

---

## 2. Secondary Analyses

Secondary analyses address additional questions that are pre-specified but not the primary focus. They are fully pre-registered but interpreted with the understanding that they were designed to explore, not definitively test.

| Analysis ID | Question | Test | Outcome measure | Decision rule |
|-------------|---------|------|-----------------|---------------|
| SA-01 | | | | |
| SA-02 | | | | |

---

## 3. Sensitivity Analyses

Sensitivity analyses test whether primary findings hold under alternative analytical choices. They are pre-specified here so they cannot be selectively reported.

| Analysis ID | What varies | Baseline choice | Alternative choice | Expected direction of change |
|-------------|------------|-----------------|-------------------|------------------------------|
| SEN-01 | | | | |

---

## 4. Exploratory Analyses

Exploratory analyses are hypothesis-generating. They are conducted on the data and their findings are stated as hypotheses for future confirmatory work. They are NOT used to revise the conclusions of the confirmatory analyses above.

[List exploratory analyses planned before data examination. Additional exploratory analyses discovered during analysis are logged in `lab_notebook.md` with timestamps.]

---

## 5. Hypothesis Register

Every confirmatory hypothesis is listed here with its full specification. The pre-registration file in `protocol/registration/` records the timestamp.

### Hypothesis Format

```
ID:           H[module].[number]
Registered:   YYYY-MM-DD (commit hash: [hash])
Question:     [one sentence — specific, directional, falsifiable]
H1:           [what we expect to find]
H0:           [what the world looks like if H1 is false]
Test:         [named statistical test]
Assumptions:  [what must hold for this test to be valid, and how verified]
Effect size:  [measure and minimum meaningful magnitude]
α:            [significance threshold — typically 0.05]
Power:        [target — typically 0.80]
Required N:   [from power analysis]
Available N:  [actual]
Powered:      [yes / no — if no, analysis is exploratory]
Correction:   [multiple comparison method if part of a family]
Confounds:    [named confounds and how controlled]
Data:         [specific dataset and split]
Script:       [path to analysis script]
```

---

## 6. Multiple Comparisons

This project conducts [N] confirmatory hypothesis tests. Multiple comparison correction is applied as follows:

**Family definition**: [Which tests form a family — tests addressing the same research question are one family]

**Correction method**: [Benjamini-Hochberg FDR for large families; Bonferroni for small families where FWER control is required]

**Corrected thresholds**: [List adjusted α per family]

Tests are grouped into families here before analysis begins. Grouping is not adjusted after results are seen.

| Family | Hypotheses included | Correction method | Adjusted α |
|--------|--------------------|--------------------|------------|
| F1 | | | |

---

## 7. Data Splits

**Unit of analysis**: SCF control (~1,400 unique controls). Not mapping rows (280,000). All statistical tests assume independence at the control level. Mixed-effects modeling is required if mapping-level analysis is conducted.

**Split strategy**: GroupKFold on SCF control IDs. No SCF control text appears in both train and test partitions. The DataSplitAgent asserts `len(set(train_control_ids) ∩ test_control_ids) == 0` before writing partition assignments to provenance. This assertion is logged and is a required Gate 2 artifact.

**Leakage analysis**: Entity-level leakage (same control text in train and test via different mapping rows) is controlled by the GroupKFold strategy above. Temporal leakage: N/A — SCF corpus is a static snapshot. Feature leakage: [To be populated at Gate 2 — specific features identified after EDA].

| Split | Purpose | Size | Grouped by | Touched when |
|-------|---------|------|-----------|--------------|
| Training | Model fitting | ~70% | SCF control ID | Phase 1 only |
| Validation | Tuning and model selection | ~15% | SCF control ID | Phase 1 only |
| Test | Final confirmatory evaluation | ~15% | SCF control ID | Once, at Gate 2 confirmatory run |

**Cross-validation**: GroupKFold, k=5, groups=scf_control_id, on training split only.

---

## 8. Missing Data Protocol

**Expected missingness**: [anticipated rate per variable]

**Mechanism assumption**: [MCAR / MAR / MNAR — and how assessed]

**Handling strategy**: [complete case analysis / imputation method — specified before seeing missing data pattern]

---

## 9. Baseline Models

The following baselines are defined and run before any complex model is evaluated. Results are locked.

| Baseline | Description | Metric | Result (filled after baseline run) |
|----------|-------------|--------|-----------------------------------|
| Trivial | [e.g., majority class / mean] | | |
| Simple | [e.g., TF-IDF cosine / logistic regression] | | |

No model is reported as performing "well" unless it beats the simple baseline on the primary metric by the pre-specified margin.

---

## 10. Model Selection Criteria

Primary embedding model selection follows the two-phase protocol from ADR-0013. The selection criterion is fixed here and is not changed after any SCF data is examined.

**Phase 1 — Benchmark evaluation (no SCF data):**
Candidate models evaluated on published STS benchmarks (STS-B, SICK-R, and any available regulatory text benchmarks identified by T-01). Selection criterion: Spearman correlation on benchmark test set. Produces ranked shortlist of 3–5 models.

**Phase 2 — Calibration sample evaluation (pre-Gate 2 held-out sample):**
Shortlisted models evaluated on a held-out calibration sample using:
- Silhouette score on the SCF control embedding space
- Cross-model agreement: pairwise Spearman between models' pairwise similarity rankings

**Primary model**: Model with highest cross-model agreement + silhouette composite score. Designation logged to Preregistration Ledger with cryptographic timestamp before Gate 2 split executes.

**All other models**: Designated as secondary/sensitivity analyses at the same timestamp. Model selection is not revisited after Gate 2.

---

## 11. Reporting Standards

- Effect size and confidence interval reported for every primary and secondary result
- Confidence intervals: 95%, bootstrap (10,000 resamples) unless parametric assumptions are verified
- Null results reported with effect size estimate and CI — "no significant difference" without a CI is not a finding
- All figures include uncertainty visualization (error bars, CI ribbons, or equivalent)
- Subgroup analyses pre-specified in Section 2; post-hoc subgroup analyses labeled exploratory

---

## 12. Limitations and Design Tradeoffs

This section is required. It acknowledges known limitations of the design before any results are seen. It is written here so it cannot be omitted or softened after results are known.

### Exploratory-Guided Hypothesis Selection

The SAP is finalized at Gate 2, after exploratory analysis. This is intentional — specifying effect sizes before seeing the data produces authorial guesses presented as pre-specified thresholds (see issue #59 resolution). But this design has a cost: hypotheses entering Gate 2 are selected based on what looked tractable or promising in the exploratory phase. This is not traditional pre-registration. It is a two-stage adaptive design with a registration checkpoint between stages.

**Nature of the bias:** Effect sizes for data-adaptive hypotheses are subject to inflation relative to theory-derived hypotheses. Hypotheses that looked uninteresting in exploratory analysis are less likely to be registered, even if they would have been pre-specified before data was seen.

**Mitigation 1 — Multiple testing correction:** Benjamini-Hochberg FDR correction applied across all confirmatory hypotheses regardless of whether they are theory-derived or data-adaptive. Correction is applied to the full registered hypothesis set, not a subset selected after results.

**Mitigation 2 — Mandatory null result reporting:** Every hypothesis that enters the confirmatory phase is reported in all outputs regardless of outcome. Selective reporting of significant findings is not permitted. The full hypothesis set and all test results appear in the Preregistration Ledger and in any published appendix.

**Mitigation 3 — Epistemic status labeling:** All findings are labeled with their epistemic origin — `theory-derived` (pre-specified from literature/theory before any SCF data was seen), `data-adaptive` (registered before confirmatory test but generated from exploratory findings), or `exploratory` (not pre-registered). Labels appear in all outputs including publications. Readers assess inference strength for each finding independently.

This limitation is disclosed in the methods section of all publications. The adaptive design is not a flaw to hide — it is the appropriate design for an autonomous iterative research system operating on data it has not yet seen. The mitigations above provide the transparency that makes adaptive findings interpretable.
