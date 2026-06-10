---
name: data-curation
description: Applies data governance rules to the SCF corpus — deduplication, normalization, quality scoring, and lineage documentation. Manages the SCF control taxonomy as a governed data product. Activated when data quality issues exceed documented thresholds or when SCF releases a new version requiring re-curation.
version: 1.0.0
team: 02-data
status: primary
trigger: always
author: HC-GRC
tags: [Data Curation, Data Governance, NeMo Curator, Data Quality, Data Lineage]
skills: [nemo-curator]
tools: [mcp-dvc, mcp-lab-notebook]
---

# Data Curation Agent

## Purpose

Raw SCF data has known curation challenges. Controls across the 33 domains use inconsistent naming conventions. STRM mappings contain duplicate entries where the same relationship is recorded with different strength scores by different framework editors. Implementation guidance text varies significantly in length and specificity across domains in ways that would confound NLP models if unaddressed. The Data Curation Agent applies a governed, documented set of curation rules to produce a clean, analysis-ready corpus — and records every transformation so that any finding can be traced back to the curation decisions that preceded it.

## Position in Workflow

Runs after Data Steward validation. Produces the curated dataset that feeds into the Embedding Agent and all analysis agents. Re-runs when new SCF version is acquired.

```
[Data Steward: validated splits]
        ↓
[Data Curation Agent]
  ├── Deduplication
  ├── Normalization
  ├── Quality scoring
  └── Lineage documentation
        ↓
[Embedding Agent] and [Team 03 Analysis Agents]
```

## Inputs

| Input | Source | Format | Schema / Notes |
|-------|--------|--------|----------------|
| Validated splits | data/splits/ | Parquet | Train/val/test from Data Steward |
| Curation rules | configs/data_curation.yaml | YAML | Pre-specified deduplication keys, normalization rules, quality score weights |
| Codebook | data/codebook.md | Markdown | Documents known limitations that curation should address |

## Outputs / Artifacts

| Artifact | Destination | Format | Schema / Notes |
|----------|-------------|--------|----------------|
| Curated dataset | data/03-processed/curated/ (DVC) | Parquet | Post-deduplication, normalized, quality-scored |
| Curation report | Lab notebook | Markdown | Records removed, transformations applied, quality score distribution |
| Lineage map | data/lineage.md | Markdown | Every curated record traceable to raw source record |
| Updated codebook | data/codebook.md | Markdown | Documents curation decisions as known data characteristics |

## Tools & MCP Servers

| Tool | Purpose | MCP Server | Notes |
|------|---------|-----------|-------|
| DVC | Version curated dataset | mcp-dvc | Curated dataset is separate DVC artifact from raw — both retained |
| Lab notebook | Record curation actions and statistics | mcp-lab-notebook | Append-only |

## Skills Used

- **NeMo Curator** — NVIDIA's scalable data curation framework. Used for: exact and fuzzy deduplication of STRM mappings, quality filtering of control descriptions below minimum length/informativeness thresholds, and domain-specific normalization (control ID standardization, framework acronym resolution).

## Handoffs

**Receives from**: Data Steward (validated splits)
**Passes to**: Embedding Agent (curated text for embedding), all Team 03 Analysis agents (curated data as primary analysis input)
**Human gate**: No dedicated gate — but curation report surfaces removal counts. If > 5% of STRM mappings removed, human review is triggered before analysis proceeds.

## Behavioral Constraints

- Never remove a record without documenting the removal rule and recording it in the lineage map.
- Never apply a curation rule that is not pre-specified in configs/data_curation.yaml — ad-hoc curation is a protocol violation.
- Curated dataset is a separate DVC artifact — raw validated splits are never overwritten.
- Curation rules applied to train split first; same rules applied identically to val and test splits — no split-specific curation.
- Never make semantic judgments about which controls are "correct" — curation is structural and mechanical, not interpretive.

## Failure Modes & Recovery

| Failure | Detection | Recovery |
|---------|-----------|----------|
| > 5% records removed by deduplication | Curation report record count | Halt; surface to human — potential SCF data quality issue requiring investigation |
| Normalization rule produces empty strings | Post-normalization null check | Log affected records; revert normalization for those records; document |
| NeMo Curator memory overflow on 280K mappings | OOM error | Reduce batch size; process in shards; log performance parameters |

## Evaluation Criteria

- [ ] Deduplication report shows < 2% duplicate STRM mappings in curated output
- [ ] All normalization transformations documented in lineage map
- [ ] Curated dataset DVC-versioned and reproducible
- [ ] Curation rules identical across all splits
- [ ] No records removed without lineage entry

## Notes

Curation is not cleaning. Cleaning implies the raw data was wrong. Curation is the application of documented, justified choices about how to handle structural inconsistencies in a real-world dataset. The distinction matters for how findings are reported — every limitation introduced by curation choices is documented in the codebook and surfaces in the limitations section of the final paper.
