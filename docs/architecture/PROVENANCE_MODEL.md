# Provenance Model

**Standard:** W3C PROV-DM (https://www.w3.org/TR/prov-dm/)
**Serialization:** PROV-O (OWL2/RDF) emitted by the Orchestrator via `rdflib`
**Status:** Locked — vocabulary selection is an architectural decision (see ADR-0003)

This document names W3C PROV-DM as the canonical provenance vocabulary for HC-GRC and maps its seven core relations to the platform's LangGraph topology. Without a named formal vocabulary, "provenance" becomes ad-hoc notebook prose — present everywhere, queryable nowhere. With PROV-DM, an external auditor can verify lineage from raw SCF data through every transformation to every finding, using standard tooling.

---

## Why PROV-DM

PROV-DM is the only W3C-recommended standard with a native delegation primitive (`ActedOnBehalfOf`) that models the LangGraph supervisor pattern directly. Its three core types — `Entity`, `Activity`, `Agent` — map cleanly to HC-GRC's artifact / pipeline-node / LLM-agent topology. Its `WasInformedBy` relation models agent-to-agent handoffs. No other fetched provenance standard has this combination.

---

## Core Type Mapping

| PROV-DM Type | HC-GRC Instantiation | Examples |
|-------------|---------------------|---------|
| `Entity` | Any artifact produced or consumed by the pipeline | SCF XLSX, DVC artifact, model checkpoint, analysis result, finding, run manifest |
| `Activity` | Any LangGraph node execution (one step in one run) | `data-acquisition:run-001`, `p1-strm-nlp:run-001:exploratory` |
| `Agent` | Any LLM agent, human reviewer, or external system acting in the pipeline | `orchestrator-agent`, `thomas-jones` (human), `github-api` |

---

## Seven-Relation Mapping

| PROV-DM Relation | Formal Meaning | HC-GRC Application |
|-----------------|---------------|-------------------|
| `WasGeneratedBy` | Entity was produced by an Activity | SCF curated dataset WasGeneratedBy data-curation run |
| `Used` | Activity consumed an Entity | p1-strm-nlp Used the curated dataset |
| `WasInformedBy` | Activity was triggered or informed by another Activity (Communication) | p2-control-topology WasInformedBy data-curation (handoff) |
| `WasDerivedFrom` | Entity was derived from another Entity | embedding artifact WasDerivedFrom curated dataset |
| `WasAttributedTo` | Entity is attributed to an Agent | finding H1.1 WasAttributedTo statistical-analyst-agent |
| `WasAssociatedWith` | Activity was associated with an Agent (responsibility) | p1-strm-nlp WasAssociatedWith p1-agent |
| `ActedOnBehalfOf` | Agent acted on behalf of another Agent (delegation) | p1-agent ActedOnBehalfOf orchestrator-agent |

The `ActedOnBehalfOf` relation is the formal description of the LangGraph supervisor pattern: each analysis agent is delegated by the Orchestrator, which retains responsibility for the outcome.

---

## HC-GRC Entity Types

These are `prov:type` annotations on Entity instances, allowing queries like "show me all SAP artifacts" or "show me all model checkpoints."

| Type URI | Description |
|----------|-------------|
| `hcgrc:RawData` | Unmodified source data (SCF XLSX, literature) |
| `hcgrc:ProcessedData` | Transformed or curated dataset |
| `hcgrc:DataSplit` | Train/val/test split artifact |
| `hcgrc:ModelCheckpoint` | Fine-tuned or aligned model weights |
| `hcgrc:EmbeddingCollection` | Qdrant collection or FAISS index |
| `hcgrc:AnalysisResult` | Output of a P1–P5 analysis run |
| `hcgrc:Finding` | A specific result with SAP traceability |
| `hcgrc:SAP` | Statistical Analysis Plan (locked version) |
| `hcgrc:RunManifest` | Per-run execution record |
| `hcgrc:GateDecision` | Human approval gate decision record |
| `hcgrc:ProtocolDocument` | Any document in `protocol/` |
| `hcgrc:PublicationArtifact` | Paper, whitepaper, or dissemination output |

---

## HC-GRC Activity Types

| Type URI | Description |
|----------|-------------|
| `hcgrc:DataAcquisition` | Downloading and verifying source data |
| `hcgrc:DataCuration` | Transforming raw data to processed form |
| `hcgrc:EmbeddingGeneration` | Producing vector embeddings |
| `hcgrc:AnalysisRun` | Executing a P1–P5 module |
| `hcgrc:ModelTraining` | Fine-tuning or post-training a model |
| `hcgrc:StatisticalTest` | Running a pre-registered confirmatory test |
| `hcgrc:GateReview` | Human review at an approval gate |
| `hcgrc:QualityAssessment` | QA Agent scoring a finding |

---

## HC-GRC Agent Types

| Type URI | Description |
|----------|-------------|
| `hcgrc:LLMAgent` | An autonomous LLM-driven agent (any AGENT.md card) |
| `hcgrc:HumanReviewer` | A human acting at a gate or in review |
| `hcgrc:OrchestratorAgent` | The Orchestrator specifically (delegation root) |
| `hcgrc:ExternalSystem` | An external API or service (GitHub, timestamp authority) |

---

## PROV-O Serialization

The Orchestrator emits PROV-O triples (Turtle syntax) at the close of each pipeline step. Example for a data curation run:

```turtle
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix hcgrc: <https://hc-grc.local/prov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Entity: raw SCF data
hcgrc:entity/scf-raw-20260609
    a prov:Entity, hcgrc:RawData ;
    prov:value "sha256:abc123..." ;
    hcgrc:dvcRef "data/01-raw/scf/scf_2026.xlsx" .

# Activity: curation run
hcgrc:activity/data-curation-run-001
    a prov:Activity, hcgrc:DataCuration ;
    prov:startedAtTime "2026-06-09T10:00:00Z"^^xsd:dateTime ;
    prov:endedAtTime   "2026-06-09T10:45:00Z"^^xsd:dateTime ;
    prov:used hcgrc:entity/scf-raw-20260609 .

# Entity: curated dataset
hcgrc:entity/scf-curated-run-001
    a prov:Entity, hcgrc:ProcessedData ;
    prov:wasGeneratedBy hcgrc:activity/data-curation-run-001 ;
    prov:wasDerivedFrom hcgrc:entity/scf-raw-20260609 ;
    hcgrc:dvcRef "data/03-processed/scf_curated/v1" .

# Agent: data-curation agent
hcgrc:agent/data-curation
    a prov:Agent, hcgrc:LLMAgent ;
    prov:actedOnBehalfOf hcgrc:agent/orchestrator .

# Association
hcgrc:activity/data-curation-run-001
    prov:wasAssociatedWith hcgrc:agent/data-curation .
```

---

## Storage and Querying

PROV-O triples are written to a local RDF store (default: Apache Jena Fuseki or `rdflib` in-memory export to `.ttl` files in `runs/<run_id>/provenance/`). Files are DVC-versioned alongside the run manifest.

SPARQL query for "show me all activities that used the locked test split":

```sparql
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX hcgrc: <https://hc-grc.local/prov#>

SELECT ?activity ?agent ?time WHERE {
  ?activity prov:used hcgrc:entity/scf-test-split-v1 ;
            prov:wasAssociatedWith ?agent ;
            prov:startedAtTime ?time .
}
ORDER BY ?time
```

This query answers the audit question: "Did any activity access the test split before Gate 2?" in O(n) time against the provenance store.
