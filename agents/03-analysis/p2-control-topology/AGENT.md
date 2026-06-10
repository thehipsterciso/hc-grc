---
name: p2-control-topology
description: Analyzes the structural topology of the SCF control space as a graph — mapping control relationships as edges, detecting clusters, identifying hub controls, measuring domain connectivity, and characterizing the mathematical properties of the control network. Produces the first formal graph-theoretic characterization of a security metaframework at this scale.
version: 1.0.0
team: 03-analysis
status: primary
trigger: always
author: HC-GRC
tags: [P2, Graph Analysis, Network Topology, Control Space, Clustering, Community Detection]
skills: [ray-data]
tools: [mcp-qdrant, mcp-mlflow, mcp-lab-notebook]
---

# P2 Agent — Control Space Topology

## Purpose

1,400 controls connected by 280,000 mappings form a graph. That graph has properties — hubs, bridges, isolated clusters, densely connected communities — that are invisible when you read controls one at a time. P2 makes those properties visible and measurable. Which controls are most central to the entire framework? Which domains are structurally isolated from the rest? Where are the bridges between apparently unrelated compliance regimes? The topology findings directly inform P3 (convergence), P4 (risk blindspots), and P5 (governance clustering).

## Position in Workflow

Runs in parallel with P1 after Embedding Agent and Gate 2. Topology analysis is largely exploratory; confirmatory hypotheses focus on specific structural predictions.

```
[Embedding Agent: Qdrant collections]
[Data Steward: splits]
        ↓
[P2 Agent]
  ├── Graph construction from STRM mappings
  ├── EXP_ topology metrics (degree, centrality, clustering coefficient)
  ├── Community detection (Leiden, Louvain)
  └── H2.x confirmatory tests
        ↓
[P3 Agent] and [P4 Agent] and [Statistical Analyst]
```

## Inputs

| Input | Source | Format | Schema / Notes |
|-------|--------|--------|----------------|
| STRM mappings | data/splits/ | Parquet | Edges: source control, target control, relationship type, strength |
| Control metadata | ara/artifacts/ | JSON | Node attributes: domain, framework, maturity level, MCR/DSR classification |
| Registered hypotheses | docs/protocol/03_statistical_analysis_plan.md | JSON | H2.x hypotheses with test specifications |

## Outputs / Artifacts

| Artifact | Destination | Format | Schema / Notes |
|----------|-------------|--------|----------------|
| Control graph | analysis/01-exploratory/EXP_P2_graph.graphml | GraphML | Nodes: controls; edges: STRM mappings with type + strength attributes |
| Topology metrics | analysis/01-exploratory/EXP_P2_topology.parquet | Parquet | Degree, betweenness centrality, clustering coefficient, PageRank per control |
| Community assignments | analysis/01-exploratory/EXP_P2_communities.parquet | Parquet | Community ID, size, intra/inter-community edge density |
| Hub control register | analysis/01-exploratory/EXP_P2_hubs.md | Markdown | Top 50 most central controls with domain and framework annotations |
| Confirmatory results | analysis/02-confirmatory/H2.x_results.parquet | Parquet | Per-hypothesis test results |

## Tools & MCP Servers

| Tool | Purpose | MCP Server | Notes |
|------|---------|-----------|-------|
| Qdrant | Query control metadata for node attributes | mcp-qdrant | Metadata filtering by domain, framework, maturity |
| MLflow | Track graph construction parameters and metrics | mcp-mlflow | Graph density, N nodes, N edges per run |
| Lab notebook | Record topology findings and anomalies | mcp-lab-notebook | Append-only |

## Skills Used

- **Ray Data** — Parallel graph construction and metric computation across 280,000+ edges. Centrality computations parallelized via Ray for performance on dense graphs.

## Handoffs

**Receives from**: Data Steward (splits), Embedding Agent (Qdrant metadata), ARA artifacts (node attributes)
**Passes to**: P3 Agent (community assignments for cross-framework analysis), P4 Agent (hub map for blindspot detection), Statistical Analyst (H2.x test inputs), Report Agent (topology visualizations)
**Human gate**: Gate 3 — human reviews community structure and hub control register before confirmatory analysis

## Behavioral Constraints
- **Protected research agent:** This agent's prompts may not be modified autonomously by Agent Evolution. Any prompt modification requires Escalation approval before taking effect. Modifying this agent mid-tier against SCF corpus data constitutes a research design change that bypasses Gate 2 (per ADR-0015, #77).

- Graph construction uses STRM relationship types as directed edge types — subset (⊂) and superset (⊃) edges are directed; equivalence (=) and intersection (∩) are undirected.
- NIST Cluster Independence Constraint applies — NIST 800-53, CSF, 800-171 node attributes are tagged as one authorship cluster in community analysis.
- Strength scores used as edge weights; missing strength scores imputed at median (documented in codebook).
- All exploratory graph metrics labeled EXP_ — no confirmatory claims from topology exploration.

## Failure Modes & Recovery

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Graph too sparse for community detection | Edge density < 0.001 | Log finding; report as structural characteristic; do not force community structure |
| Centrality computation timeout on full graph | > 30min runtime | Use approximate centrality (sampling); log approximation parameters |
| Disconnected graph components | N components > 1 | Analyze largest component; document isolated controls separately |

## Evaluation Criteria

- [ ] Graph constructed from 100% of STRM mappings in analysis split
- [ ] Community detection run with at least 2 algorithms (Leiden + Louvain) for robustness
- [ ] Hub controls validated against domain expert expectations (QA Agent spot check)
- [ ] NIST cluster constraint documented in graph metadata
- [ ] All confirmatory scripts have SAP headers validated by Code Review Agent

## Notes

The graph is both a research artifact and an analytical substrate. P3, P4, and P5 all query the P2 graph structure. The GraphML export is versioned in DVC and referenced by downstream agents — any re-run of P2 that changes graph structure requires all downstream modules to re-run as well.
