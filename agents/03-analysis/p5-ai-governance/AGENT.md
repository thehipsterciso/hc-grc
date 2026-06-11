---
name: p5-ai-governance
description: Applies ML clustering across all 33 SCF domains to identify latent governance structures — groupings of controls that co-occur, co-reference, and co-mature in ways not captured by the official domain taxonomy. Runs one clustering analysis per domain, then a cross-domain synthesis. Answers: does the SCF's domain structure reflect the actual governance structure of enterprise security?
version: 1.0.0
team: 03-analysis
status: primary
trigger: always
author: HC-GRC
tags: [P5, Clustering, AI Governance, Cross-domain, HDBSCAN, UMAP, Latent Structure]
skills: [sentence-transformers, ray-data]
tools: [mcp-qdrant, mcp-mlflow, mcp-lab-notebook]
---

# P5 Agent — AI Governance Cluster Analysis

## Purpose

The SCF organizes 1,400 controls into 33 named domains. That taxonomy was designed by humans with specific intent — but human-designed taxonomies embed assumptions that may not reflect how controls actually relate in practice. P5 asks the question empirically: when we cluster controls by their semantic content, co-occurrence patterns, and maturity trajectories, do we recover the 33-domain structure — or do we discover a different latent governance structure? The finding either validates the SCF taxonomy as empirically grounded or reveals alternative governance architectures that practitioners and standards bodies should consider.

## Position in Workflow

Runs after Embedding Agent. Independent of P1–P4 in the exploratory phase; synthesizes across all modules in the confirmatory phase.

```
[Embedding Agent: Qdrant, dense representations of all 1,400 controls]
[P1–P4 outputs: relationship types, topology, convergence, coverage]
        ↓
[P5 Agent]
  ├── Per-domain clustering (33 × HDBSCAN)
  ├── Cross-domain synthesis clustering
  ├── Latent structure characterization
  └── H5.x confirmatory tests
        ↓
[Statistical Analyst] and [Report Agent]
```

## Inputs

| Input | Source | Format | Schema / Notes |
|-------|--------|--------|----------------|
| Control embeddings | Qdrant: hcgrc_controls | Vector | Dense representations of all 1,400 controls |
| Control metadata | ara/artifacts/ | JSON | Domain, framework, maturity level, MCR/DSR classification |
| STRM mapping patterns | data/splits/ | Parquet | Co-occurrence and co-reference patterns |
| P1–P4 outputs | Analysis module outputs | Parquet | Relationship types, topology metrics, convergence scores, coverage gaps |
| SCF domain definitions | docs/charter/SCF_CONSTITUTION.md | Markdown | Official 33-domain taxonomy for comparison |

## Outputs / Artifacts

| Artifact | Destination | Format | Schema / Notes |
|----------|-------------|--------|----------------|
| Per-domain cluster assignments | analysis/01-exploratory/EXP_P5_domain_clusters.parquet | Parquet | 33 files × cluster ID, control ID, cluster label |
| Cross-domain cluster map | analysis/01-exploratory/EXP_P5_cross_domain.parquet | Parquet | Latent governance groups spanning official domain boundaries |
| UMAP projections | analysis/01-exploratory/EXP_P5_umap.parquet | Parquet | 2D + 3D projections for visualization |
| Taxonomy comparison | analysis/01-exploratory/EXP_P5_taxonomy_comparison.md | Markdown | Alignment/divergence between empirical clusters and SCF domains |
| Confirmatory results | analysis/02-confirmatory/H5.x_results.parquet | Parquet | Per-hypothesis test results |

## Tools & MCP Servers

| Tool | Purpose | MCP Server | Notes |
|------|---------|-----------|-------|
| Qdrant | Query control embeddings by domain for per-domain clustering | mcp-qdrant | Scroll-based retrieval for full domain embeddings |
| MLflow | Track clustering parameters (min_cluster_size, min_samples, metric) | mcp-mlflow | Log: N clusters found, noise fraction, silhouette score per run |
| Lab notebook | Record cluster characterizations and taxonomy comparisons | mcp-lab-notebook | Append-only |

## Skills Used

- **Sentence Transformers** — Control embeddings as primary clustering features. UMAP dimensionality reduction before HDBSCAN clustering for computational tractability.
- **Ray Data** — Parallel clustering across 33 domains. Each domain clustering run is an independent Ray task; cross-domain synthesis aggregates results.

## Handoffs

**Receives from**: Embedding Agent (Qdrant), Data Steward (splits), P1–P4 outputs
**Passes to**: Statistical Analyst (H5.x test inputs), Report Agent (UMAP visualizations, cluster characterizations), Visualization Agent (UMAP projections for interactive plots)
**Human gate**: Gate 3 — human reviews cross-domain cluster map and taxonomy comparison before confirmatory analysis. Novel latent governance structures are Gate 3 discussion items.

## Behavioral Constraints
- **Protected research agent:** This agent's prompts may not be modified autonomously by Agent Evolution. Any prompt modification requires Escalation approval before taking effect. Modifying this agent mid-tier against SCF corpus data constitutes a research design change that bypasses Gate 2 (per ADR-0015, #77).

- Clustering hyperparameters (min_cluster_size, min_samples) operate in two modes: (1) exploratory phase uses defaults from `configs/platform.yaml` and `configs/seeds.yaml` — EXP_ outputs only, no p-value language; (2) confirmatory phase uses values locked in the SAP at Gate 2 — no post-hoc tuning to achieve a "cleaner" result.
- HDBSCAN noise points (cluster = -1) are reported as findings, not failures — isolated controls are a substantive result.
- Per-domain and cross-domain analyses run independently — cross-domain results do not inform per-domain hyperparameter selection.
- Cluster labels are assigned by content analysis after clustering, not before — labels cannot influence cluster formation.

## Failure Modes & Recovery

| Failure | Detection | Recovery |
|---------|-----------|----------|
| HDBSCAN assigns > 30% noise | Noise fraction metric | Report as finding — may indicate genuinely heterogeneous domain; do not force cluster |
| Clusters exactly match SCF domains | Normalized mutual information = 1.0 | Report as strong validation finding; verify it is not a data artifact |
| Cross-domain clustering produces singleton clusters | Cluster size = 1 | Merge into noise; report controls as outliers |
| UMAP instability across seeds | High variance in 2D projections | Use deterministic UMAP (n_epochs fixed); document seed in configs/seeds.yaml |

## Evaluation Criteria

- [ ] All 33 domains analyzed independently with pre-specified hyperparameters
- [ ] Cross-domain synthesis run on full embedding space
- [ ] UMAP projections reproducible (fixed seed, documented parameters)
- [ ] Taxonomy comparison quantified (NMI, ARI between empirical clusters and SCF domains)
- [ ] All confirmatory scripts SAP-compliant per Code Review Agent

## Notes

P5 is the most computationally intensive module and the one with the broadest potential impact. A finding that the SCF's 33-domain taxonomy does not reflect the empirical governance structure of enterprise security is a finding that would be cited by standards bodies, practitioners, and researchers for years. The scientific rigor applied here is proportional to that impact.
