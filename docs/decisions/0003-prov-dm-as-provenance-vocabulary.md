# ADR-0003: W3C PROV-DM as Canonical Provenance Vocabulary

**Status:** Accepted
**Date:** 2026-06-09
**Deciders:** Thomas Jones

---

## Context

HC-GRC requires verifiable lineage from raw SCF data through every transformation to every published finding. The platform needs a provenance vocabulary that: (a) is a published standard with long-term stability, (b) has a delegation primitive matching LangGraph's supervisor pattern, (c) is serializable to RDF for external queryability, and (d) is supported by Python tooling.

## Decision

W3C PROV-DM (https://www.w3.org/TR/prov-dm/) is the canonical provenance vocabulary for HC-GRC. PROV-O (OWL2/RDF) is the serialization format. Python implementation via `rdflib`. The seven core relations are mapped to LangGraph constructs in PROVENANCE_MODEL.md. Custom entity, activity, and agent types are prefixed `hcgrc:` per the namespace.

## Alternatives Considered

**OpenLineage:** Excellent for pipeline lineage, integrates with Airflow/dbt/Spark. Does not have a native delegation primitive (`ActedOnBehalfOf`) — it models job-to-job lineage, not agent-to-agent delegation. HC-GRC will emit OpenLineage events as a supplementary format (see ADR-0006) but PROV-DM is the primary vocabulary.

**ML Metadata (MLMD):** Covers artifacts, executions, and contexts well. No agent or delegation primitive. Custom ContextTypes would be required for Gate, Hypothesis, and SAP concepts. More complex operational dependency (requires MLMD service). Eliminated in favor of PROV-DM + DVC.

**Ad-hoc JSON lineage:** Tempting for simplicity. Rejected because it produces platform-specific provenance that requires a custom parser for external audit. PROV-DM gives the platform a standard that auditors, journal reviewers, and automated tools can consume without HC-GRC-specific documentation.

## Consequences

**Positive:**
- `ActedOnBehalfOf` directly models LangGraph supervisor → sub-agent delegation
- SPARQL queries over the provenance store answer audit questions in standard syntax
- W3C recommendation — stable, long lifecycle, extensive external tooling
- `rdflib` is mature and well-maintained in the Python ecosystem

**Negative:**
- RDF/OWL adds conceptual overhead for contributors unfamiliar with the semantic web stack
- Fuseki or equivalent RDF store adds an optional but recommended operational dependency
- PROV-O serialization requires discipline to keep in sync with actual pipeline execution

**Mitigation:** The Orchestrator emits PROV-O triples automatically at each node completion. Contributors do not hand-author provenance records — they implement nodes that emit them.
