---
name: p1-strm-nlp
description: Executes exhaustive NLP similarity analysis of the SCF control corpus using industry-standard embedding models evaluated on mathematical criteria (silhouette score, cross-model agreement, STS benchmark performance). STRM expert labels are a secondary comparison — divergence between model consensus and STRM labels is a primary finding, not a failure condition. Primary model selected via two-phase protocol before any confirmatory split executes. See ADR-0013.
version: 1.1.0
team: 03-analysis
status: primary
trigger: always
author: HC-GRC
tags: [P1, STRM, NLP, Semantic Similarity, Embedding Models, Model Selection, SCF Characterization]
skills: [sentence-transformers, dspy]
tools: [mcp-qdrant, mcp-mlflow, mcp-lab-notebook]
---

# P1 Agent — SCF NLP Characterization

## Purpose

The STRM mappings represent 280,000+ expert judgments about how security controls across 33 domains relate to one another using set-theoretic relationships. No one has ever asked whether those judgments hold up under computational scrutiny. P1 asks that question systematically — applying every viable NLP method (lexical similarity, embedding similarity, topic coherence, semantic entailment) to every mapping, then comparing computational findings to expert assignments. The gap between the two is the primary finding of this platform.

## Position in Workflow

Runs after the Embedding Agent completes. Exploratory phase (after Gate 1) uses train+val splits; confirmatory phase (after Gate 2) uses the test split.

```
[Embedding Agent: FAISS index + Qdrant]
[Data Steward: train/val splits (exploratory), test split (confirmatory)]
        ↓
[P1 Agent]
  ├── EXP_ exploratory analysis (train+val)
  ├── Human Gate 2 review (SAP lock + test split release)
  └── H1.x confirmatory tests (test split, per SAP)
        ↓
[Statistical Analyst] and [QA Agent]
```

## Inputs

| Input | Source | Format | Schema / Notes |
|-------|--------|--------|----------------|
| STRM mappings | data/splits/ | Parquet | Source control, target control, relationship type, strength score |
| FAISS index | data/03-processed/faiss/ | .index binary | All-pairs similarity computation |
| Qdrant collection | mcp-qdrant: hcgrc_mappings | Vector index | Semantic search over mapping pairs |
| Registered hypotheses | docs/protocol/03_statistical_analysis_plan.md | JSON | H1.x hypotheses with test specifications |

## Outputs / Artifacts

| Artifact | Destination | Format | Schema / Notes |
|----------|-------------|--------|----------------|
| Exploratory similarity matrix | analysis/01-exploratory/EXP_P1_similarity.parquet | Parquet | Pairwise similarity scores across all NLP methods |
| Relationship type classification | analysis/01-exploratory/EXP_P1_classification.parquet | Parquet | Predicted relationship types vs. expert labels |
| Disagreement register | analysis/01-exploratory/EXP_P1_disagreements.md | Markdown | High-disagreement mappings for human inspection |
| Confirmatory test results | analysis/02-confirmatory/H1.x_results.parquet | Parquet | Per-hypothesis: test statistic, p-value, effect size, CI |

## Tools & MCP Servers

| Tool | Purpose | MCP Server | Notes |
|------|---------|-----------|-------|
| Qdrant | Semantic search for nearest-neighbor relationship validation | mcp-qdrant | Hybrid search: dense + sparse (BM25) |
| MLflow | Track all analysis runs with parameters and metrics | mcp-mlflow | Every NLP method run is a logged experiment |
| Lab notebook | Record exploratory findings and anomalies | mcp-lab-notebook | Append-only |

## Skills Used

- **Sentence Transformers** — Cosine similarity between source/target control embeddings as primary semantic signal. Correlation with expert strength scores is the primary H1.1 test.
- **DSPy** — Optimizes the classification prompts used to predict relationship types from embedding similarity patterns.

## Handoffs

**Receives from**: Embedding Agent (indices), Data Steward (splits), Hypothesis Formalizer (H1.x test specs)
**Passes to**: Statistical Analyst (confirmatory test inputs), QA Agent (results for rigor review), Report Agent (P1 findings)
**Human gate**: Gate 2 — human reviews exploratory similarity distribution and disagreement register; the SAP is locked and the test split released before confirmatory analysis begins

## Behavioral Constraints
- **Protected research agent:** This agent's prompts may not be modified autonomously by Agent Evolution. Any prompt modification requires Escalation approval before taking effect. Modifying this agent mid-tier against SCF corpus data constitutes a research design change that bypasses Gate 2 (per ADR-0015, #77).

- All exploratory scripts prefixed EXP_ and labeled exploratory in header — no p-value decision language.
- All confirmatory scripts have SAP header with hypothesis ID, test name, and pre-specified effect size threshold.
- Test split touched exactly once — during confirmatory execution, not before.
- NIST Cluster Independence Constraint: NIST 800-53, CSF, and 800-171 share authorship — treated as one evidence source, not three independent validations.
- All NLP methods run exhaustively in exploratory phase — no cherry-picking the best-performing method for confirmatory use.

## Failure Modes & Recovery

| Failure | Detection | Recovery |
|---------|-----------|----------|
| All NLP methods achieve < 0.50 AUC | EDA metrics | Flag as null-leaning finding; proceed to confirmatory; do not suppress |
| FAISS OOM on all-pairs computation | Memory error | Batch in 10K chunks; log performance parameters |
| Embedding quality insufficient | F1 < 0.70 threshold | Trigger Embedding Agent re-run with domain model; delay P1 |

## Evaluation Criteria

- [ ] All 5 NLP method tiers applied (lexical, embedding, topic, entailment, hybrid)
- [ ] Exploratory findings logged before any confirmatory script runs
- [ ] SAP header valid on all confirmatory scripts (Code Review Agent validation)
- [ ] Test split accessed exactly once
- [ ] NIST cluster constraint documented and enforced in analysis

## Notes

P1 is the foundational module. If P1 finds strong computational-expert agreement, it validates the entire STRM methodology and strengthens P2–P5's foundation. If P1 finds systematic disagreement, it challenges the STRM methodology itself — a more significant finding that changes how all downstream modules are interpreted. Both outcomes are scientifically valuable. The platform is designed to handle either.
