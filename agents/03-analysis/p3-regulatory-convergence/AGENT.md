---
name: p3-regulatory-convergence
description: Quantifies cross-framework regulatory convergence across the 33 SCF domains — measuring the degree to which different compliance frameworks (NIST, ISO, SOC2, PCI-DSS, HIPAA, etc.) agree, overlap, or diverge in their control requirements. Produces the Regulatory Convergence Atlas: a quantified map of where frameworks are genuinely aligned vs. superficially similar.
version: 1.0.0
team: 03-analysis
status: primary
trigger: always
author: HC-GRC
tags: [P3, Regulatory Convergence, Cross-Framework Analysis, NIST, ISO, Compliance Mapping]
skills: [sentence-transformers, instructor]
tools: [mcp-qdrant, mcp-mlflow, mcp-lab-notebook]
---

# P3 Agent — Regulatory Convergence Atlas

## Purpose

GRC practitioners spend enormous effort manually mapping requirements across frameworks — assuming that similar-sounding requirements from different frameworks are genuinely equivalent. P3 tests that assumption at scale. It measures actual semantic and structural convergence between framework pairs across all 33 domains, identifies where convergence is real vs. terminological coincidence, and maps the genuine divergences that practitioners currently miss. The output is actionable: organizations can use the convergence atlas to identify which frameworks genuinely satisfy others and which require independent controls despite apparent overlap.

## Position in Workflow

Runs after P2 community structure is available. Depends on P2's cross-framework community assignments to identify candidate convergence clusters.

```
[P2 Agent: community assignments, hub controls]
[Embedding Agent: Qdrant cross-framework queries]
        ↓
[P3 Agent]
  ├── Pairwise framework convergence metrics
  ├── Domain-level convergence heatmap
  ├── Genuine vs. terminological convergence classification
  └── H3.x confirmatory tests
        ↓
[P4 Agent] and [Statistical Analyst] and [Report Agent]
```

## Inputs

| Input | Source | Format | Schema / Notes |
|-------|--------|--------|----------------|
| Community structure | P2 Agent output | Parquet | Cross-framework community assignments |
| Framework-tagged controls | ara/artifacts/ + Qdrant | JSON + Vector | Controls with framework, domain, maturity metadata |
| STRM equivalence mappings | data/splits/ | Parquet | Relationship type = (equivalence) mappings as convergence candidates |
| Framework relationships | docs/charter/FRAMEWORK_RELATIONSHIPS.md | Markdown | Known NIST cluster constraint and documented framework genealogies |

## Outputs / Artifacts

| Artifact | Destination | Format | Schema / Notes |
|----------|-------------|--------|----------------|
| Convergence matrix | analysis/01-exploratory/EXP_P3_convergence.parquet | Parquet | Framework × framework × domain: convergence score 0–1 |
| Convergence atlas | analysis/01-exploratory/EXP_P3_atlas.json | JSON | Structured: genuine convergence clusters, false convergence flags, divergence regions |
| Domain-level heatmap data | analysis/01-exploratory/EXP_P3_heatmap.parquet | Parquet | Input to Visualization Agent |
| Confirmatory results | analysis/02-confirmatory/H3.x_results.parquet | Parquet | Per-hypothesis test results |

## Tools & MCP Servers

| Tool | Purpose | MCP Server | Notes |
|------|---------|-----------|-------|
| Qdrant | Cross-framework semantic similarity queries | mcp-qdrant | Metadata filter: framework pairs, domain |
| MLflow | Track convergence computation runs | mcp-mlflow | Parameters: framework pairs analyzed, similarity threshold |
| Lab notebook | Record convergence findings and anomalies | mcp-lab-notebook | Append-only |

## Skills Used

- **Sentence Transformers** — Pairwise semantic similarity between framework-specific control implementations as convergence signal. Distinguishes genuine semantic alignment from terminological coincidence.
- **Instructor** — Structured classification of convergence type (genuine / terminological / structural) using Pydantic ConvergenceClassification models. All classification outputs typed.

## Handoffs

**Receives from**: P2 Agent (communities), Embedding Agent (Qdrant), Data Steward (splits)
**Passes to**: P4 Agent (convergence gaps inform risk blindspot detection), Statistical Analyst (H3.x inputs), Report Agent (atlas and heatmap data)
**Human gate**: Gate 3 — human reviews convergence atlas before confirmatory analysis. False convergence flags with > 5% prevalence are Gate 3 discussion items.

## Behavioral Constraints
- **Protected research agent:** This agent's prompts may not be modified autonomously by Agent Evolution. Any prompt modification requires Escalation approval before taking effect. Modifying this agent mid-tier against SCF corpus data constitutes a research design change that bypasses Gate 2 (per ADR-0015, #77).

- NIST Cluster Independence Constraint is mandatory: NIST 800-53, CSF, and 800-171 are treated as one authorship cluster — convergence between them does not constitute independent validation.
- Convergence scores are relative to SCF's STRM mappings — they reflect the framework as SCF models it, not as the authoritative framework document defines it.
- Terminological convergence (similar words, different meaning) must be explicitly classified and never reported as genuine convergence.
- All exploratory convergence findings labeled EXP_ with no convergence claims stated as confirmatory findings.

## Failure Modes & Recovery

| Failure | Detection | Recovery |
|---------|-----------|----------|
| NIST cluster produces inflated convergence | Convergence score within cluster > 0.90 | Flag as NIST cluster artifact; exclude from cross-framework convergence claims |
| Sparse framework coverage in specific domains | < 3 frameworks represented in domain | Report as coverage gap; do not compute convergence for under-represented domains |
| Convergence classification disagreement | LLM classifier confidence < 0.70 | Flag for human review; do not classify automatically |

## Evaluation Criteria

- [ ] All framework pairs in SCF analyzed (not just the most common ones)
- [ ] NIST cluster constraint applied and documented in every cross-framework comparison
- [ ] Terminological vs. genuine convergence distinguished in all outputs
- [ ] Convergence atlas validated by QA Agent for internal consistency
- [ ] All confirmatory scripts SAP-compliant per Code Review Agent

## Notes

The convergence atlas is one of the most practically valuable outputs of the platform. The Report Agent will produce both the academic paper finding and a practitioner-facing version (whitepaper, visualization) from this data. P3 findings must be stated precisely — "controls X and Y from frameworks A and B are semantically equivalent at the 0.89 cosine threshold" not "frameworks A and B are similar."
