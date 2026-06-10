# Statistical Analysis Plan (SAP)

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

**Unit of analysis**: [What constitutes one observation]

**Split strategy**: [Random / stratified / group-aware — with justification]

**Leakage analysis**: [Every way test set information could contaminate training, and whether it is controlled]

| Split | Purpose | Size | Stratified by | Touched when |
|-------|---------|------|--------------|--------------|
| Training | Model fitting | % | | |
| Validation | Tuning and model selection | % | | |
| Test | Final evaluation | % | Set aside now, touched once at end |

**Cross-validation**: [k-fold strategy, k=, stratified by]

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

Models are selected by [criterion — e.g., macro-F1 on validation set]. Ties broken by [e.g., interpretability, compute cost].

The selection criterion is fixed here. It is not changed after models are evaluated.

---

## 11. Reporting Standards

- Effect size and confidence interval reported for every primary and secondary result
- Confidence intervals: 95%, bootstrap (10,000 resamples) unless parametric assumptions are verified
- Null results reported with effect size estimate and CI — "no significant difference" without a CI is not a finding
- All figures include uncertainty visualization (error bars, CI ribbons, or equivalent)
- Subgroup analyses pre-specified in Section 2; post-hoc subgroup analyses labeled exploratory
