# Research Design — DS/ML Project Framework

This document defines the research methodology for this project from first principles. It is the authoritative workflow reference. Every analysis conducted in this project follows these phases in order. Phases are not skipped; confirmatory analysis does not begin before exploratory analysis is complete.

---

## Phase 0 — Problem Definition

Before any data is touched, the following must be documented and locked.

**0.1 Research Questions**
State each question precisely. A well-formed research question names the variables, the relationship being tested, and the population it applies to. "Does X predict Y in population Z?"

**0.2 Unit of Analysis**
What is one observation? A row in the dataset. Everything else follows from this.

**0.3 Pre-specified Success Criteria**
Define what a meaningful result looks like before seeing any data. This includes:
- Minimum effect size worth reporting (e.g., Spearman ρ ≥ 0.3, not just p < 0.05)
- Classification accuracy threshold above which a model is considered informative vs. trivially explainable by class imbalance
- Coverage percentage below which a finding is considered a material gap

These thresholds are set here. They are not adjusted after results are seen.

**0.4 Scope Constraints**
What is explicitly out of scope for this project phase? Document it. Undocumented scope creep is the most common cause of research drift.

**0.5 Assumptions**
List every assumption the analysis depends on. Each assumption is either validated in Phase 1 EDA or flagged as a limitation.

---

## Phase 1 — Data

### 1.1 Acquisition

- Source documentation: name, URL, version/date, format, license
- Download scripts (reproducible, idempotent)
- SHA256 hash logged at download time — this is the immutable record of what was analyzed
- Files stored in `data/01-raw/` — never modified, treated as read-only

### 1.2 Schema Documentation

Before any analysis: document every field in every source file.
- Field name, data type, cardinality
- Semantics: what does this field actually mean in context?
- Known ambiguities, inconsistencies, or undocumented conventions in the source
- Entity-relationship diagram if multiple tables/files

This step is completed with the raw file in hand, not from documentation alone. Documentation lies. The file is the ground truth.

### 1.3 Exploratory Data Analysis (EDA)

EDA is not optional and is not abbreviated. It runs before any hypothesis test, any model, and any feature engineering decision. The purpose is to understand what the data actually contains — not what you expect it to contain.

**Univariate Analysis — every variable of interest**
- Continuous: distribution shape (histogram, KDE), min, max, mean, median, std, skewness, kurtosis, outliers (IQR method + visual inspection)
- Categorical: frequency table, class distribution, rare categories, unexpected values
- Text: length distribution (characters and tokens), vocabulary size, unique term count, presence of structured patterns

**Bivariate Analysis — all pairs of interest**
- Continuous × Continuous: scatterplot, Pearson, Spearman
- Categorical × Continuous: grouped distributions, boxplots
- Categorical × Categorical: contingency table, Cramér's V
- Target variable against all features: this is where predictive signal is first identified

**Class Balance Analysis**
For every classification task: what is the class distribution? A classifier trained on imbalanced data that beats majority-class baseline is the minimum bar, not the goal. Document imbalance ratio. Determine if resampling (SMOTE, undersampling) or class-weight adjustment is required.

**Missing Value Analysis**
- Missingness rate per field
- Missing Completely at Random (MCAR), Missing at Random (MAR), or Missing Not at Random (MNAR)?
- Imputation strategy or exclusion decision, documented with rationale

**Anomaly and Outlier Analysis**
- Isolation Forest or z-score flagging on continuous variables
- Manual inspection of top and bottom 1% of distributions
- Decision: exclude, cap, or retain with documentation

**Sample Size Inventory**
Count observations at every level of grouping relevant to the analysis (e.g., observations per class, per group, per time period). This feeds directly into the power analysis in Phase 2.

EDA outputs: a notebook (`notebooks/02_eda.ipynb`) and a written summary (`reports/eda_summary.md`) that documents every material finding.

### 1.4 Data Quality Assessment

- **Completeness**: what percentage of expected records are present?
- **Consistency**: do values in one field contradict values in another?
- **Accuracy**: spot-check a sample against the original source
- **Known biases**: are certain classes, groups, or time periods systematically over- or under-represented?
- **Resolution**: is the granularity of the data sufficient for the research questions?

Document every deficiency. A deficiency that is not documented becomes an uncontrolled confound.

### 1.5 Data Splits

**Define before any model sees the data.**

- What is the held-out test set? It is set aside now and not touched until final evaluation.
- What is the validation set strategy? k-fold cross-validation (k=5 or k=10) is standard.
- Is stratification required? Yes if class imbalance > 3:1.
- Is group-aware splitting required? Yes if the same entity appears in multiple rows and naive random split would leak information across train/test. Identify the grouping variable and use GroupKFold.
- What is the leakage analysis? Enumerate every way information from the test set could contaminate training. For each: is it present in the current split strategy? If yes, fix it.

Document the split rationale. The split is a scientific decision, not a technical default.

### 1.6 Feature Engineering

- List all candidate features derivable from raw data
- Distinguish: raw fields, engineered features (transformations, interactions), and external features
- Each feature needs: definition, motivation, expected relationship to target, and a validation check (does the computed value look correct on a sample?)
- Feature store: computed features written to `data/03-processed/`, versioned and reusable

---

## Phase 2 — Experimental Design

### 2.1 Baseline Models

Every experiment requires at least one trivial baseline and one simple baseline before complex models are evaluated.

**Trivial baseline**: the dumbest possible predictor. For regression: predict the mean. For classification: predict the majority class. For ranking: random order. No model is considered useful unless it beats the trivial baseline by the pre-specified success criterion.

**Simple baseline**: a single, interpretable model with no tuning. Logistic regression for classification. Linear regression for regression. TF-IDF cosine similarity for text similarity. This sets the floor for "simple and explainable" and is the benchmark that complex models are compared against.

Baseline results are locked before any complex model is run. If a complex model underperforms the simple baseline, that is a finding — not a reason to quietly drop the baseline.

### 2.2 Model Tiers

Models are evaluated in tiers, from simple to complex. Advancement from one tier to the next requires that the current tier's best model meets the minimum bar and that the research question justifies additional complexity.

**Tier 1 — Sparse / Bag-of-words**: TF-IDF, BM25, n-gram frequency. Fastest, most interpretable, highest explainability.

**Tier 2 — Dense word vectors**: Word2Vec, GloVe, fastText. Captures lexical semantics, no contextual understanding.

**Tier 3 — Dense sentence encoders**: sentence-BERT variants, Universal Sentence Encoder. Contextual sentence-level semantics.

**Tier 4 — Fine-tuned contextual models**: BERT, RoBERTa, DeBERTa fine-tuned on task-specific data. Maximum performance potential, minimum interpretability, maximum compute cost.

Tier 4 is not the default. It is justified only when Tier 3 does not meet the success criterion and the compute cost is acceptable.

### 2.3 Ablation Study Design

Ablations are designed before any model is run. For each component of the final model pipeline, define: what happens if this component is removed or replaced with a simpler version?

The purpose of ablations is to understand the contribution of each component to the final result. A result that depends on every component simultaneously and cannot be decomposed is not a scientific finding — it is a system output.

Example ablation axes:
- Embedding model (swap Tier 3 for Tier 2)
- Similarity measure (swap cosine for Jaccard)
- Preprocessing step (with/without stopword removal)
- Training data size (learning curves at 10%, 25%, 50%, 100%)

### 2.4 Power Analysis

Before running any hypothesis test: estimate the minimum sample size required to detect the pre-specified minimum effect size at α = 0.05, power = 0.80.

For correlation tests: use the formula for Spearman/Pearson power. For classification: use expected class sizes and test statistic distribution. For group comparison tests (Mann-Whitney, Kruskal-Wallis): use effect size estimates from literature or pilot data.

If available N is below the required N: the hypothesis is underpowered and results must be interpreted as exploratory, not confirmatory. Document this explicitly.

### 2.5 Evaluation Metrics

**Defined per task, before modeling begins.**

For regression:
- Primary: Spearman rank correlation (appropriate when scale is ordinal or the relationship may be monotonic but non-linear)
- Secondary: MAE, RMSE, R²
- Never use R² alone for ordinal targets

For classification (multi-class):
- Primary: macro-averaged F1 (appropriate when class imbalance is present and all classes matter equally)
- Secondary: per-class precision, recall, F1; Cohen's kappa; confusion matrix
- Never use accuracy alone when classes are imbalanced

For clustering:
- External (if ground truth exists): NMI, ARI
- Internal (no ground truth): Silhouette score, Davies-Bouldin index, Calinski-Harabasz index
- All three internal metrics together — no single clustering metric is reliable alone

For similarity tasks:
- Primary: Spearman correlation between model scores and human/expert scores
- Secondary: Bland-Altman limits of agreement (is the disagreement systematic or random?)

### 2.6 Hyperparameter Tuning

- Search strategy: grid search (small spaces), random search (medium), Bayesian optimization (large)
- Tuning is always done on the validation set, never the test set
- Final hyperparameters are locked before the test set is touched
- All tuning runs logged to the experiment tracker

---

## Phase 3 — Confirmatory Hypothesis Testing

### 3.1 Pre-registration

Every hypothesis is written down and committed to the repository before the analysis that tests it runs. The commit timestamp is the pre-registration record.

Pre-registration format (stored in `research/hypotheses/`):
```
Hypothesis ID: H[module].[number]
Date registered: YYYY-MM-DD
Research question: [one sentence]
Hypothesis (H1): [directional, specific, falsifiable]
Null hypothesis (H0): [what the world looks like if H1 is false]
Statistical test: [named test with justification]
Effect size measure: [named measure]
Minimum meaningful effect size: [pre-specified value]
Significance threshold: α = [value, typically 0.05]
Power target: [value, typically 0.80]
Required N: [from power analysis]
Multiple comparison correction: [method, if applicable]
Data source: [specific dataset and split]
Known confounds: [list with planned controls]
Analysis script: [path to script that runs this test]
```

### 3.2 Statistical Testing Standards

- Report effect size alongside p-value. A p-value alone is not a finding.
- Report confidence intervals (95% bootstrap CI unless parametric assumptions are verified).
- Apply multiple comparison correction whenever N tests > 1. Method: Benjamini-Hochberg FDR for large test families; Bonferroni for small families where FWER control is appropriate.
- Distinguish: confirmatory tests (pre-registered, strict α) from exploratory tests (hypothesis-generating, require replication).
- A null result is documented and reported. "We found no significant relationship between X and Y (Spearman ρ = 0.04, p = 0.31, 95% CI [−0.08, 0.16])" is a finding.

### 3.3 Assumption Validation

Every parametric test has assumptions. Validate them or use a non-parametric alternative.
- Normality: Shapiro-Wilk (small N) or D'Agostino-Pearson (large N). If violated: use Mann-Whitney, Kruskal-Wallis, Spearman.
- Homoscedasticity: Levene's test. If violated: use Welch's t-test or non-parametric equivalent.
- Independence: document and verify that observations are independent given the split strategy.

---

## Phase 4 — Model Evaluation and Interpretation

### 4.1 Held-out Test Set Evaluation

The test set is touched exactly once. Results on the test set are final. No re-tuning after seeing test results.

Report: all pre-specified metrics, comparison to baselines, confidence intervals.

### 4.2 Error Analysis

After evaluation: inspect what the model gets wrong.
- What types of examples are misclassified or have high residuals?
- Are errors systematic (clustered by a subgroup, input length, class)?
- What does a correct vs. incorrect prediction look like side-by-side?

Error analysis drives the next iteration of feature engineering and informs limitations.

### 4.3 Robustness Checks

- Performance on subgroups (by class, by domain, by data source)
- Sensitivity to preprocessing choices (does removing/changing a preprocessing step materially change results?)
- Stability across random seeds (report mean ± std over k seeds for stochastic models)

### 4.4 Interpretability

For each predictive model: what features drive predictions, and do they make sense?
- Linear models: coefficients
- Tree-based: feature importance (impurity-based and permutation)
- Neural/embedding models: SHAP values, probing classifiers, attention visualization where applicable
- A model whose predictions cannot be interpreted is a black box, not a finding

---

## Phase 5 — Reproducibility

### 5.1 Environment

- `requirements.txt` pinned to exact versions
- `environment.yml` for conda environments if applicable
- Python version pinned in `Makefile`
- No version ranges — `==` only

### 5.2 Seeds

- Every stochastic operation receives an explicit seed
- Seeds documented in experiment config files (`configs/`)
- The global seed is set at script entry point and logged to the experiment tracker

### 5.3 Data Versioning

- `data/01-raw/` is read-only after acquisition
- Every processed dataset carries a filename that encodes its source and transformation (e.g., `scf_2026_1_controls_normalized.parquet`)
- SHA256 of every `data/01-raw/` file logged in `data/01-raw/MANIFEST.md`

### 5.4 Experiment Tracking

All experiment runs log:
- Parameters (all hyperparameters, model configs, split configs)
- Metrics (all evaluation metrics, on train, validation, and test)
- Artifacts (model weights, predictions, figures)
- Tags (hypothesis ID, dataset version, model tier, researcher name)
- Duration and compute environment

A result that cannot be reproduced from the experiment log is not a result.

### 5.5 Code Standards

- All analytical code in `src/` is modular, importable, and tested
- Notebooks (`notebooks/`) are for exploration and presentation, not production logic
- No business logic in notebooks — notebooks call `src/` functions
- `make test` runs all tests before any result is committed
- `make reproduce` reruns the full pipeline from raw data to final outputs

---

## Phase 6 — Reporting

### 6.1 Research Report Structure

1. Abstract
2. Introduction and motivation
3. Related work
4. Data (sources, schema, EDA summary, quality assessment)
5. Methods (experimental design, model tiers, evaluation metrics)
6. Results (all pre-specified hypotheses, effect sizes, CIs, null results)
7. Discussion (interpretation, confounds, limitations)
8. Conclusion
9. Reproducibility statement (code, data, experiment tracker link)

### 6.2 Visualization Standards

- Every figure has a caption that can stand alone without the surrounding text
- Uncertainty is always shown: error bars (±1 std), CI ribbons, or box plots — never point estimates alone
- Color choices are colorblind-safe (ColorBrewer, viridis, or equivalent)
- No 3D plots for 2D data
- Axes start at zero unless there is a documented reason not to

### 6.3 What Gets Published

All of the following are publishable outputs:
- Positive results (H1 confirmed)
- Null results (H0 not rejected, with adequate power)
- Methodological contributions (the pipeline itself, if novel)
- Negative results (the approach failed and here is why)

The suppression of null and negative results is scientific misconduct. Document them.

---

## Directory Structure

```
project/
├── data/
│   ├── raw/                   # immutable source files + MANIFEST.md (SHA256, date)
│   ├── interim/               # intermediate transformations (not final)
│   ├── processed/             # final canonical datasets for modeling
│   └── external/              # third-party reference data
│
├── notebooks/
│   ├── 01_data_acquisition.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_baselines.ipynb
│   ├── 05_model_development.ipynb
│   ├── 06_evaluation.ipynb
│   └── 07_interpretation.ipynb
│
├── src/
│   ├── data/                  # acquisition, loading, cleaning, splitting
│   ├── features/              # feature engineering pipelines
│   ├── models/                # model definitions, training loops
│   ├── evaluation/            # metrics, scoring functions
│   └── visualization/         # plotting utilities
│
├── experiments/               # MLflow tracking (or equivalent)
│
├── reports/
│   ├── figures/               # saved plots
│   ├── outputs/               # tables, CSVs of results
│   └── eda_summary.md         # written EDA findings
│
├── research/
│   ├── hypotheses/            # pre-registered hypothesis files (one per H)
│   └── study-designs/         # experimental design documents per module
│
├── configs/                   # YAML experiment configs (seeds, split params, etc.)
├── tests/                     # unit + integration tests for src/
├── Makefile                   # reproduce, test, lint, clean targets
└── requirements.txt           # pinned exact versions
```

---

## Workflow Enforcement

The phases run in order. This is the gate logic:

```
Phase 0 (Problem Definition) → locked before data is touched
Phase 1.1–1.2 (Acquisition + Schema) → locked before EDA begins
Phase 1.3 (EDA) → complete before feature engineering or splits
Phase 1.4–1.5 (Quality + Splits) → complete before any model sees data
Phase 2 (Experimental Design) → baselines, metrics, power analysis done before modeling
Phase 3 (Hypothesis Pre-registration) → committed before confirmatory analysis runs
Phase 4 (Evaluation) → test set touched exactly once, at the end
```

Skipping a gate produces results that cannot be trusted. A fast result that cannot be trusted is not faster than a correct result.
