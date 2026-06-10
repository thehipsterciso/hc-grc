# Study Design Template

One file per analytical module. Completed before any analysis in that module begins.

---

**Module ID**: [e.g., P1]  
**Module Name**: [descriptive name]  
**Date locked**: YYYY-MM-DD  
**Status**: [ ] Design phase  [ ] Analysis running  [ ] Complete  

---

## 1. Problem Statement

[What question does this module answer? One paragraph. Be specific about variables and population.]

## 2. Unit of Analysis

[What is one observation in this module? Every downstream decision depends on this being correct.]

## 3. Pre-specified Success Criteria

[What result would be meaningful? Defined here, not after results are seen.]

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| [metric]  | [value]   | [why]     |

## 4. Data Requirements

| Dataset | Location | Fields required | N (estimated) |
|---------|----------|-----------------|---------------|
|         |          |                 |               |

**EDA prerequisites**: [List any EDA findings that must be confirmed before this module proceeds. e.g., "class distribution of relationship_type must be documented"]

## 5. Baselines

| Baseline | Description | Implementation | Expected performance |
|----------|-------------|----------------|----------------------|
| Trivial  | [majority class / mean predictor / random] | | |
| Simple   | [e.g., TF-IDF cosine + logistic regression] | | |

Baselines are run and results locked before complex models are evaluated.

## 6. Model Tiers and Selection Criteria

| Tier | Model class | Justification for advancement |
|------|-------------|-------------------------------|
| T1   |             | Advance if: [criterion]       |
| T2   |             | Advance if: [criterion]       |
| T3   |             | Advance if: [criterion]       |
| T4   |             | Advance if: [criterion]       |

**Model selection criterion**: [How is the final model selected? Best validation metric? Pareto of performance vs. interpretability?]

## 7. Train / Validation / Test Split

**Split strategy**: [random / stratified / group-aware / temporal]  
**Grouping variable** (if group-aware): [field name and rationale]  
**Split ratios**: [e.g., 70/15/15]  
**Stratified by**: [target class / domain / other]  
**Leakage analysis**: [enumerate each leakage risk and whether it is controlled]  
**Cross-validation**: [k-fold, k=, stratified?]  

## 8. Features

| Feature | Source field | Type | Engineering | Expected signal direction |
|---------|-------------|------|-------------|--------------------------|
|         |             |      |             |                          |

## 9. Evaluation Metrics

| Task | Primary metric | Secondary metrics | Reason for choice |
|------|---------------|-------------------|-------------------|
|      |               |                   |                   |

**Baseline comparison**: All metrics reported relative to trivial and simple baselines.

## 10. Ablation Plan

| Ablation | Component modified | Hypothesis being tested by ablation |
|----------|--------------------|-------------------------------------|
| A1       |                    |                                     |
| A2       |                    |                                     |

## 11. Power Analysis Summary

| Hypothesis ID | Effect size target | Required N | Available N | Powered? |
|--------------|-------------------|------------|-------------|----------|
|              |                   |            |             |          |

## 12. Hypotheses in this Module

[List all hypothesis IDs registered for this module. Link to `research/hypotheses/` files.]

## 13. Known Confounds and Controls

| Confound | Mechanism | Control |
|----------|-----------|---------|
|          |           |         |

## 14. Limitations

[What can this module NOT conclude, even if results are strong? Document before analysis.]

## 15. Outputs

| Output | Format | Location | Consumer |
|--------|--------|----------|----------|
|        |        |          |          |
