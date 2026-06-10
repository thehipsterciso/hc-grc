# Methods Scaffolding

**Lock status:** LOCKED at framework pre-registration. This document locks the methodological rules that govern the full analysis — test families, split strategy, seed management, the exploratory/confirmatory firewall, and hyperparameter handling. It does not name specific hypotheses or pre-specify effect sizes; those are deferred to the SAP. What is locked here cannot be changed after pre-registration without a documented SAP amendment.

**Deferred:** Specific statistical tests per hypothesis, effect size thresholds, primary/secondary outcome designations. These require exploratory characterization to specify meaningfully.

---

## 1. Data Split Strategy

### Proportions
- **Train:** 70%
- **Validation:** 15%
- **Test (confirmatory holdout):** 15%

Proportions are fixed. Post-registration changes to proportions constitute a SAP violation.

### Stratification
Stratification variables are determined at data acquisition based on the actual distribution of the corpus. At minimum: SCF domain (33 classes) and STRM relationship type (5 classes). If domain × relationship type produces sparse cells, stratification falls back to domain only. The stratification decision is logged in the data steward's artifact before split execution.

### Seed Management
The random seed for all split operations is a single value set at first data acquisition and recorded in two places: the data steward's DVC artifact metadata and the pre-registration commit. **The seed is sacrosanct after pre-registration.** Changing it after the split is executed constitutes a SAP violation equivalent to running multiple splits and selecting the favorable one.

Seed selection method: generated from the RFC 3161 timestamp of the pre-registration commit (timestamp → SHA-256 → first 8 hex digits → integer). This makes the seed auditable and eliminates any possibility of seed selection bias.

### Test Set Access Control
The test split is physically inaccessible before Gate 2 (Orchestrator-enforced, LangGraph topology). The Data Steward agent writes the test split to an encrypted DVC artifact at split time. The decryption key is held by the Orchestrator and released only at Gate 2. All pre-Gate 2 evaluation runs — including model training, fine-tuning decisions, and exploratory analysis — use train + validation only.

Any analysis that touches the test split before Gate 2 invalidates the confirmatory analysis. This is not recoverable.

---

## 2. Exploratory / Confirmatory Firewall

### The Firewall Rule
A statistical finding is either exploratory or confirmatory. It cannot be both. An exploratory finding that is later "confirmed" by re-testing on the same data is not a confirmatory finding — it is a double-dipped exploratory finding reported with false confirmatory framing. The split architecture enforces this structurally: exploratory runs on train + validation, confirmatory runs on test.

### What Counts as Exploratory
- Any analysis run before SAP lock
- Any analysis that was not pre-specified at SAP lock, regardless of when it runs
- Any analysis motivated by looking at exploratory results
- Hyperparameter search and calibration
- Model selection and architecture decisions

### What Counts as Confirmatory
- Tests of pre-specified hypotheses (H[module].[n] format, locked in SAP)
- Run on the test split
- Run after Gate 2
- Exactly one test per hypothesis — no re-testing after seeing results

### Reporting Rules
Exploratory findings are reported with descriptive statistics, visualizations, and directional language. No p-values, no significance claims, no "the data shows" framing for exploratory results. Confirmatory findings include: the pre-specified hypothesis text, the test used, the test statistic, the p-value (uncorrected and corrected), the effect size with confidence interval, and whether the pre-specified threshold was met.

Null results in confirmatory analysis are reported with the same structure and in the same section of any output as positive results.

---

## 3. Test Families by Module

These are the families of statistical methods appropriate for each module's question type. Specific tests — which variant, which correction method, what effect size threshold — are deferred to the SAP after exploratory characterization establishes the actual data structure.

### P1 — STRM NLP Calibration
*Question type: classification accuracy, semantic similarity distribution*

Applicable test families:
- **Classification metrics:** Precision, recall, F1 (macro and weighted), Matthews Correlation Coefficient. Primary evaluation metric chosen at SAP lock after class balance is characterized.
- **Distributional comparison:** Comparing semantic similarity distributions across mapping type categories. Non-parametric tests preferred (Kruskal-Wallis, Dunn post-hoc with correction) given unknown distribution shape. Parametric alternatives if normality holds.
- **Correlation analysis:** Rank correlation (Spearman) between NLP-derived similarity scores and expert strength scores. Pearson if both distributions are normal.
- **NIST cluster independence constraint:** NIST 800-53, CSF, 800-171 mappings are treated as a single evidence cluster. Within-cluster mappings are excluded from cross-framework analyses. This constraint is enforced at the data layer, not at the analysis layer — it is not a choice made per analysis, it is a standing rule.

### P2 — Control Space Topology
*Question type: graph structure, community detection*

Applicable test families:
- **Graph topology metrics:** Degree distribution, betweenness centrality, eigenvector centrality, clustering coefficient. Computed on the directed STRM graph.
- **Community detection:** Leiden algorithm (primary). Louvain (secondary, for comparison). Resolution parameter search is exploratory; final parameter pre-specified at SAP lock.
- **Community-domain comparison:** Normalized Mutual Information (NMI) between empirical community assignment and SCF domain labels. Tests whether empirical structure replicates declared domain structure.
- **Statistical significance of topological claims:** Permutation tests comparing observed metrics against null model (degree-preserving random graph). Specific null model variant pre-specified at SAP lock.

### P3 — Regulatory Convergence Atlas
*Question type: cross-framework similarity, cluster comparison*

Applicable test families:
- **Pairwise convergence quantification:** Mean semantic similarity of STRM-linked control pairs per framework dyad. Effect size: Cohen's d for comparison across dyads.
- **Genuine vs. terminological convergence:** Controlling for within-author-community vocabulary similarity. Specific operationalization deferred to SAP — requires observing the actual within-author vs. cross-author similarity gap in exploratory analysis.
- **NIST cluster independence:** As in P1 — within-NIST-cluster convergence is not treated as independent evidence of cross-framework convergence.
- **Multiple comparisons correction:** Bonferroni or Benjamini-Hochberg. Method pre-specified at SAP lock after the number of framework dyads being tested is known from exploratory analysis.

### P4 — Risk Blindspot Engine
*Question type: coverage distribution, gap detection*

Applicable test families:
- **Coverage distribution analysis:** Distribution of control counts per risk category. Summary statistics: mean, median, Gini coefficient (coverage inequality), identified zero-coverage categories.
- **Gap characterization:** Risk categories below a coverage threshold (threshold pre-specified at SAP lock based on exploratory distribution). Not a null hypothesis test — gap detection is descriptive.
- **Domain-gap co-location:** Chi-square or Fisher's exact test for association between domain membership and below-threshold risk category coverage.

### P5 — AI Governance Clustering
*Question type: clustering, structural integration*

Applicable test families:
- **Clustering quality:** DBCV (Density-Based Clustering Validation) for HDBSCAN — appropriate for variable-density clusters. Silhouette score as secondary. Per-domain and cross-domain.
- **Hyperparameter handling:** `min_cluster_size` and `min_samples` are exploratory parameters — searched in train split, pre-specified at SAP lock, not re-tuned after.
- **Noise point handling:** HDBSCAN noise points (cluster assignment = -1) are findings, not failures. They are reported as structurally unintegrated controls. Their proportion is a metric, not a nuisance.
- **Cross-domain integration test:** Network density comparison between AI governance cross-domain STRM connections vs. baseline (comparable domain, matched for recency). Specific comparable domain pre-specified at SAP lock.

---

## 4. Hyperparameter Handling Rules

### The Core Rule
Hyperparameters that affect the structure of the analysis — not just performance — must be pre-specified in the SAP before confirmatory analysis. Hyperparameters discovered during exploratory analysis are reported as exploratory findings, then locked in the SAP. They are not "tuned" on the test set.

### Exploratory Phase (train + validation)
- Hyperparameter search runs entirely on train + validation
- Search method (grid, random, Bayesian) documented in lab notebook at time of execution
- Final selected values logged to MLflow with justification
- Validation performance at selected values recorded — this is the expected performance estimate

### Pre-SAP Lock
- All hyperparameters used in confirmatory analysis are written into the SAP as fixed values
- Changing them after SAP lock constitutes a SAP violation

### Model Selection
- Model architecture and embedding model selection are exploratory decisions
- The models used in confirmatory analysis are named in the SAP and pinned to DVC artifact versions
- Using a different model version than the one named in the SAP (even a superior one discovered after lock) constitutes a SAP violation

### HDBSCAN Specifics (P5)
`min_cluster_size` and `min_samples` are pre-specified in the SAP per SCF domain (33 sets of parameters, one per domain) and one set for the cross-domain synthesis. These are searched in the exploratory phase and locked. Noise point handling policy (report as unintegrated, not re-labeled) is locked here.

---

## 5. Multiple Comparisons and Family-Wise Error Control

### Rule
Any analysis that runs multiple tests — across framework dyads in P3, across community structures in P2, across risk categories in P4 — must pre-specify its correction method in the SAP. The correction method is not chosen after seeing the uncorrected p-values.

### Preferred Methods
- **Benjamini-Hochberg (FDR control):** Preferred when tests are expected to have non-zero true effects (discovery-oriented testing)
- **Bonferroni:** Preferred when family-wise error rate control is more important than power (small number of high-stakes tests)
- **None:** Acceptable only for pre-specified primary outcomes when the family size is one

### Reporting
Uncorrected p-values are always reported alongside corrected values. The correction method and the family of tests it applies to are specified in the SAP.

---

## 6. Effect Size and Practical Significance

### Rule
Every confirmatory test reports an effect size with confidence interval regardless of whether the null hypothesis is rejected. A statistically significant finding with a negligible effect size is not a substantively meaningful finding. The SAP pre-specifies the minimum effect size considered practically significant for each test.

### Effect Size Families by Test Type
| Test type | Effect size measure |
|-----------|---------------------|
| Difference in means | Cohen's d |
| Rank correlation | Spearman ρ |
| Classification improvement | ΔF1 (absolute change) |
| Community structure | ΔNMI |
| Clustering quality | ΔDBCV |
| Association (categorical) | Cramér's V |

Confidence interval method (bootstrap, exact, asymptotic) pre-specified per test in the SAP.

---

## 7. Handling Missing and Incomplete Data

### Missing Control Descriptions
Controls with missing or incomplete text descriptions are excluded from NLP-based analyses (P1, P3, P5). The exclusion is logged with count and proportion. If excluded proportion exceeds 5% in any domain, the impact on that domain's results is specifically noted in findings.

### Missing STRM Strength Scores
STRM mappings with missing strength scores are included in structural analyses (P2) but excluded from correlation analyses that require the strength score (P1). Missing proportion logged.

### These rules are locked here. The proportion thresholds (5%) and the inclusion/exclusion decisions are not re-made at analysis time.

---

## 8. Reproducibility Requirements

Every confirmatory analysis run must be reproducible from the DVC artifact chain alone. Reproducibility means: given the locked DVC artifact for the test split, the locked model versions, the locked hyperparameters from the SAP, and the locked code version (pinned commit SHA), the analysis produces the same results.

Randomness that affects results is controlled via the seed management procedure in Section 1. Any random operation not covered by the primary seed (e.g., HDBSCAN internal randomness) uses `random_state = primary_seed + module_number` where module_number is 1–5 for P1–P5.

---

## 9. What Is Not Locked Here

The following are explicitly deferred to the SAP:
- Specific hypothesis statements (H[module].[n])
- Pre-specified effect size thresholds per test
- Primary vs. secondary outcome designation per module
- Specific test variant choices within the families named above
- Specific comparable domain for P5 cross-domain integration test
- Resolution parameter for Leiden algorithm (P2)
- Correction method for P3 framework dyad comparisons
- Model architecture and embedding model selections

These deferred items require observing the exploratory distribution of the data before they can be specified meaningfully.
