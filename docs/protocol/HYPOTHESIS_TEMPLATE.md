# Hypothesis Pre-Registration Template

Copy this file. Rename to `H[module].[number]_[short_name].md`. Commit before running the analysis.

---

**Hypothesis ID**: H[module].[number]  
**Date registered**: YYYY-MM-DD  
**Status**: [ ] Pre-registered  [ ] Analysis running  [ ] Completed  [ ] Null result  

---

## Research Question

[One sentence. Names the variables, the direction, and the population.]

## Hypothesis (H1)

[Directional, specific, falsifiable. "We expect X to be positively associated with Y in population Z."]

## Null Hypothesis (H0)

[What the world looks like if H1 is false. "There is no association between X and Y."]

## Statistical Test

**Test**: [e.g., Spearman rank correlation, Mann-Whitney U, Chi-square]  
**Justification**: [Why this test is appropriate given the data type and distribution assumptions]  
**Assumption checks required**: [e.g., normality via Shapiro-Wilk, homoscedasticity via Levene's]  

## Effect Size

**Measure**: [e.g., Spearman ρ, Cohen's d, Cramér's V]  
**Minimum meaningful effect size**: [Pre-specified. e.g., ρ ≥ 0.30]  
**Rationale**: [Why this threshold is meaningful in context]

## Significance and Power

**Significance threshold (α)**: 0.05  
**Power target**: 0.80  
**Required N (from power analysis)**: [computed value]  
**Available N**: [actual sample size for this test]  
**Powered?**: [ ] Yes  [ ] No — results are exploratory only  

## Multiple Comparisons

**Part of a family of tests?**: [ ] Yes  [ ] No  
**Correction method**: [Benjamini-Hochberg / Bonferroni / None — with justification]  
**Corrected α**: [adjusted threshold]  

## Known Confounds

| Confound | Direction of bias | Control strategy |
|----------|-------------------|-----------------|
| [name]   | [inflates/deflates result] | [how handled] |

## Data

**Dataset**: [path to `data/03-processed/` file]  
**Dataset version**: [SHA256 or filename with version]  
**Split used**: [train / validation / test / full — with justification]  
**Unit of analysis**: [what is one row]  

## Analysis Script

**Path**: `src/[module]/[script_name].py`  
**Notebook**: `notebooks/[number]_[name].ipynb`  

## Results (filled after analysis)

**Test statistic**: [value]  
**p-value**: [value]  
**Effect size**: [value]  
**95% CI**: [lower, upper] (bootstrap, n=10,000 resamples)  
**Corrected p-value**: [value if applicable]  
**Decision**: [ ] Reject H0  [ ] Fail to reject H0  
**Interpretation**: [one sentence — what does this mean for the research question]  
**Anomalies / unexpected findings**: [anything that wasn't anticipated]  
