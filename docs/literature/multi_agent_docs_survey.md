# Multi-Agent System Documentation Survey

**Purpose**: Inform documentation strategy for hc-grc by surveying what mature multi-agent LangChain/LangGraph systems, AI-for-science platforms, and adjacent standards bodies actually document. Identify gaps in the tentative hc-grc documentation roadmap and recommend additions, auto-generation opportunities, pitfalls, and tooling.

**Method**: Five-angle parallel literature and primary-source survey (LangGraph/multi-agent conventions; ML reproducibility and provenance standards; agent governance and capability advertising; adversarial collaboration and DAG documentation; autonomous-science platforms 2024–2026). All quoted material is verbatim from a primary source identified by URL. Where a primary source could not be fetched in this session, the gap is named explicitly and no claim is asserted in its place.

**Date**: 2026-06-09

---

## 1. Reference patterns — what mature platforms actually maintain

This section catalogs concrete documentation artifacts that primary sources demonstrably ship or require. For each artifact: what it is, why it exists, what gap it closes, who authors it, who consumes it, and the citation.

### 1.1 `AGENTS.md` / `CLAUDE.md` at repo root (LangGraph convention)

**What it is.** A 57-line file at the root of `langchain-ai/langgraph` that doubles as a contributor guide and an agent-runtime instruction file. The file enumerates the monorepo's library structure, prescribes the `make format` / `make lint` / `make test` commands required before any pull request, and includes a hand-drawn ASCII dependency map of the agent-adjacent libraries (`checkpoint`, `checkpoint-postgres`, `langgraph`, `prebuilt`).

**Why it exists.** It is the single canonical orientation document for both human contributors and AI coding agents working in the monorepo. It collapses what would otherwise be split across `CONTRIBUTING.md`, an architecture doc, and a separate agent prompt.

**What gap it closes.** Stale architecture docs that disagree with the actual repo layout. The file is short enough to be re-read on every contribution and lives next to the code it describes.

**Who authors / consumes.** Maintainers author it. Human contributors and AI coding agents (Claude Code, Cursor, etc.) consume it. The fact that `AGENTS.md` and `CLAUDE.md` are byte-identical in the LangGraph repo confirms the design intent: same instructions, two well-known filenames.

**Citation**: https://github.com/langchain-ai/langgraph/blob/main/AGENTS.md (verified — fetched in full).

### 1.2 `StateSnapshot` schema and `checkpoint_ns` semantics (LangGraph persistence)

**What it is.** A typed object the LangGraph checkpointer writes at every super-step. Documented fields: `values`, `next`, `config`, `metadata` (with `source ∈ {"input","loop","update"}` and a `step` counter), `created_at`, `parent_config`, `tasks`. The `checkpoint_ns` (checkpoint namespace) is a structured string: empty for the parent graph, `"node_name:uuid"` for subgraphs, joined with `|` for nested subgraphs.

**Why it exists.** Without a documented snapshot schema, replay, audit, and partial-resumption guarantees are unverifiable. With one, a regulator or arbiter can answer "what did the graph know at step N" against a fixed contract.

**Citation**: https://docs.langchain.com/oss/python/langgraph/persistence (verified — fetched in full). LangGraph also documents three explicit `durability` modes — `"exit"`, `"async"`, `"sync"` — and recommends `"sync"` for high-durability cases: it "ensures that LangGraph writes every checkpoint before continuing execution, providing high durability at the cost of some performance overhead."

### 1.3 The four HITL decision types and the "Rules of Interrupts" (LangGraph)

**What it is.** A fixed enumeration of human responses — `approve | edit | reject | respond` — with strict ordering: "Decisions must be provided in the same order as the actions appear in the interrupt request" (https://docs.langchain.com/oss/python/langchain/human-in-the-loop). The "Rules of interrupts" page lists four engineering constraints that must hold for replay correctness: do not wrap `interrupt` calls in try/except; do not reorder `interrupt` calls within a node; do not return complex values; side effects called before `interrupt` must be idempotent (https://docs.langchain.com/oss/python/langgraph/interrupts).

**Why it exists.** Resumption from a checkpoint is index-based. Reordering, swallowing, or non-idempotent side effects silently break replay integrity — the failure is observable only on the second run, often much later.

**Why hc-grc cares.** The five hc-grc gates inherit these semantics whether you document them or not. Failing to record them in a `GATES.md`-equivalent means each gate's correctness depends on whichever engineer last touched the node.

### 1.4 ADR folder convention — Microsoft Agent Framework

**What it is.** `docs/decisions/` containing numbered ADRs (e.g., `0021-agent-skills-design.md`), separated from `docs/design/` (which holds active design documents), separated again from `schemas/` (machine-readable contracts) and `declarative-agents/` (YAML agent definitions).

**Why it exists.** A clean split between "what we decided and when" (immutable ledger), "how it is currently built" (mutable design), and "what the machine reads" (schemas). The Microsoft Agent Framework README explicitly directs contributors to all four locations: "Contributing Guide … Python Development Guide … Design Documents … Architectural Decision Records" (https://github.com/microsoft/agent-framework, verified). It also ships a `TRANSPARENCY_FAQ.md` for responsible-AI disclosures — a pattern AutoGen uses as well ("TRANSPARENCY_FAQS.md").

**Who authors / consumes.** Maintainers author ADRs at decision time. Reviewers and historians consume them when asking "why did we choose this." For hc-grc's `EVOLUTION.md`, ADRs are the canonical primitive.

### 1.5 A2A AgentCard schema (Linux Foundation / Google)

**What it is.** A JSON manifest published at `/.well-known/agent-card.json` defining: `protocolVersion`, `name`, `description`, `url`, `version`, `skills` (array of `AgentSkill` with `id`, `name`, `description`, `tags`, `inputModes`, `outputModes`, `examples`), `capabilities` (`streaming`, `pushNotifications`, `stateTransitionHistory`, `extendedAgentCard`), `provider` (`name`, `domain`), `securitySchemes` / `security` (OpenAPI 3.2-style), `preferredTransport`, `AgentInterface[]` (per-transport bindings), and `AgentCardSignature` (cryptographic signature over the card).

**Why it exists.** Inter-agent discovery and authority resolution without a centralized registry. An agent's identity is bound to its declared capabilities at the JSON document level; the signature makes substitution and silent capability creep detectable.

**Citation**: A2A specification (https://a2a-protocol.org/latest/specification/), Google's announcement post (https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/), and IBM's overview (https://www.ibm.com/think/topics/agent2agent-protocol). A2A was donated to the Linux Foundation in June 2025 with 50+ partner companies. Independently corroborated by the worked AgentCard examples in arXiv 2509.18415 (Malkapuram et al., *Context Lineage Assurance for Non-Human Identities*).

### 1.6 Model Context Protocol — runtime capability negotiation (not a manifest)

**What it is.** A JSON-RPC 2.0 protocol between hosts, clients, and servers. Server capabilities are *negotiated at runtime* via `initialize` / `tools/list` / `resources/list` / `prompts/list` rather than declared in a static document. The MCP specification states explicitly that servers offer "Resources, Prompts, Tools" and that the protocol itself "cannot enforce these security principles at the protocol level" — authority resolution is host-mediated user consent.

**Why this matters for hc-grc**. Each AGENT.md card already declares which MCP servers it uses (`mcp-qdrant`, `mcp-mlflow`, etc.). The cards are doing for hc-grc what `/.well-known/agent-card.json` does in A2A — but for the local, supervised case. The runtime-negotiation model means the cards should be treated as *current intent*, not as a security boundary.

**Citation**: https://modelcontextprotocol.io/specification (MCP spec).

### 1.7 Cryptographic identity block (arXiv 2509.18415)

**What it is.** An extension to the A2A AgentCard that adds:

```
"identity": {
  "agent_id": "aid://sha256(public_key || provider.domain || timestamp)",
  "public_key": "ed25519:...",
  "identity_proof": "ed25519:Sign_priv(agent_id || skills)",
  "lineage_support": { "merkle_proof_generation": true, "dpop_binding": true }
}
```

**Why it exists.** It binds the agent's identity to a content-addressed hash of its public key and its declared skills. Any change to the capability set invalidates the signature. Combined with Merkle inclusion proofs and DPoP (RFC 9449), it lets a downstream auditor verify "this artifact was produced by an agent whose declared capabilities at the time included X."

**Citation**: Malkapuram et al., arXiv 2509.18415 (verified — fetched in full, including Listing 1 and the FedRAMP worked example in Appendix A).

### 1.8 Mitchell et al. Model Cards — nine-section template

**What it is.** A standardized reporting template with nine sections: Model Details, Intended Use (including explicit *non-applications*), Factors, Metrics, Evaluation Data, Training Data, Quantitative Analyses, Ethical Considerations, Caveats and Recommendations.

**Why it exists.** To force model authors to disclose intended use and contra-indications at the same level of rigor as performance metrics.

**Citation**: Mitchell et al. 2018, arXiv 1810.03993. (Note — PDF fetch timed out in this session; the nine-section list is corroborated via the HuggingFace model card template at https://huggingface.co/docs/hub/model-cards which adopts the same structure.)

### 1.9 NeurIPS 2026 reproducibility requirements

**What it is.** A handbook-level checklist now requiring explicit disclosure of agent/LLM use in methodology, plus a self-contained executable code submission and Schema.org or DCAT dataset metadata.

**Direct quotes** from the NeurIPS 2026 Main Track Handbook (https://neurips.cc/Conferences/2026/MainTrackHandbook, verified):

- "The use of agents and/or LLMs in implementing the method should be described in the experimental setup section (or equivalent) if it is an important, original, or non-standard component of the approach e.g. if the paper is about using an LLM as a search heuristic."
- "Your code submission should include training and evaluation code, specification of dependencies, etc. See https://github.com/paperswithcode/releasing-research-code for more detailed guidelines."
- "Your code submission ideally should be self-contained and executable."
- "The dataset should adhere to Schema.org or DCAT metadata standards" with "a persistent identifier such as Digital Object Identifier or Compact Identifier."

NeurIPS 2026 also instated MLRC (ML Reproducibility Challenge) as an official track that names "Reproducibility of AI agents and AI systems" as a scope (https://neurips.cc/Conferences/2026/CallForReproducibility, verified). This is the first major venue making agentic-system reproducibility a publishable contribution category.

**Why hc-grc cares.** If any paper from this platform targets NeurIPS, an `AGENT_WORKFLOW.md` is no longer a documentation nicety — it is a venue requirement.

### 1.10 TOP Guidelines — seven research practices × three levels

**What it is.** The Transparency and Openness Promotion guidelines (Center for Open Science) define seven research practices: Study Registration, Study Protocol, Analysis Plan, Materials Transparency, Analysis Code Transparency, Data Transparency, Reporting Transparency. Each has three escalating levels: Disclosed → Shared and Cited → Certified. The 2025 update adds two Verification Practices (Results Transparency and Computational Reproducibility) and four Verification Studies — Replication, Registered Report, Multiverse, and Many Analyst.

**Direct quotes** from https://www.cos.io/initiatives/top-guidelines (verified):

- Registered Report: "a registered study in which a study protocol and analysis plan are peer reviewed, and the study is pre-accepted by a publication outlet, before the research is undertaken."
- Multiverse: "A study in which a single research team examines the research question of interest across different, reasonable choices for processing and analyzing the same data."
- Many Analyst: "A study in which independent analysis teams conduct plausible alternative analyses of a research question on the same dataset."

**Why hc-grc cares.** Multiverse and Many Analyst are the closest standardized analogues of the hc-grc adversarial protocol. They give the platform a citation handle when explaining why parallel-analysis paths are part of the design rather than a bug.

### 1.11 W3C PROV-DM — the only fetched standard with multi-agent vocabulary

**What it is.** A W3C recommendation defining three core types — `Entity`, `Activity`, `Agent` — and seven core relations: `WasGeneratedBy`, `Used`, `WasInformedBy` (Communication), `WasDerivedFrom`, `WasAttributedTo`, `WasAssociatedWith`, `ActedOnBehalfOf` (Delegation). PROV-DM is serializable to PROV-O (OWL2/RDF), PROV-N (human-readable), and PROV-XML.

**Why it matters here.** PROV-DM is the only fetched standard with a native vocabulary for delegated, multi-agent semantics. The `Agent` type explicitly subsumes "a software agent is running software." The `ActedOnBehalfOf` relation is defined as "the assignment of authority and responsibility to an agent (by itself or by another agent) to carry out a specific activity as a delegate or representative, while the agent it acts on behalf of retains some responsibility for the outcome of the delegated work." That sentence describes the LangGraph supervisor pattern in formal prose.

**Citation**: https://www.w3.org/TR/prov-dm/ (verified — fetched in full).

### 1.12 ML Metadata (MLMD) data model

**What it is.** A library for tracking artifacts, executions, and contexts in ML pipelines. Core types: `ArtifactType` / `Artifact`, `ExecutionType` / `Execution`, `Event` (with types including `DECLARED_INPUT` and `DECLARED_OUTPUT`), `ContextType` / `Context`, plus `Attribution` (artifact-to-context) and `Association` (execution-to-context). Backends: SQLite, MySQL, PostgreSQL.

**Direct quote** (https://www.tensorflow.org/tfx/guide/mlmd, verified): "Every run of a production ML pipeline generates metadata containing information about the various pipeline components, their executions (e.g. training runs), and resulting artifacts (e.g. trained models)."

**What MLMD does *not* model.** Agents, delegation, human approval gates. Its `ContextType` is enumerated as "projects, pipeline runs, experiments, owners." For hc-grc, a custom `ContextType` like `Gate`, `AgentRole`, `Hypothesis`, `SAP` would be required.

### 1.13 OpenLineage — Job / Run / Dataset object model + facets

**What it is.** An LF AI & Data Foundation graduated standard. Three entities (`Job`, `Run`, `Dataset`) and three event types: `RunEvent`, `JobEvent` (design-time, not associated with a run), `DatasetEvent` (design-time, not associated with a run).

**Facet inventory** (verbatim from https://openlineage.io/docs/spec/facets/, verified):

- Job facets: Job Documentation, Job Type, Ownership, Source Code, Source Code Location, SQL, Tags.
- Run facets: Environment Variables, Error Message, External Query, Extraction Error, Job Dependencies, Nominal Time, Parent Run, Execution Parameters, Processing Engine, Tags, Test Run.
- Dataset facets: Catalog, Column Level Lineage, Data Quality Assertions, Data Quality Metrics, Datasource, Dataset Documentation, Lifecycle State Change, Ownership, Subset Definition, Schema, Storage, Symlinks, Hierarchy, Tags, Dataset Type, Version, plus Input- and Output-only facets.

Custom facet rule (verbatim): "Custom facets must use a distinct prefix named after the project defining them to avoid collision with standard facets... The naming of custom facets should follow the pattern `{prefix}{name}{entity}Facet` PascalCased."

**Why hc-grc cares.** OpenLineage gives a portable schema for lineage emission that integrates with Airflow, Spark, dbt, Flink, and Dagster out of the box (https://github.com/OpenLineage/OpenLineage, verified). If hc-grc emits OpenLineage events from LangGraph nodes, the existing OL tooling stack becomes available for lineage visualization without writing it from scratch.

### 1.14 DAG production-doc conventions — Airflow / Dagster / Prefect

**What production-grade workflow projects maintain** (sourced from the canonical upstream files of each project):

- **Airflow** (`airflow-core/docs/best-practices.rst`, verified): an idempotency contract — "You should treat tasks in Airflow equivalent to transactions in a database... never produce incomplete results... Airflow can retry a task if it fails. Thus, the tasks should produce the same outcome on every re-run." A determinism rule: "The Python datetime `now()` function ... should never be used inside a task." An inter-task data-passing rule: small messages via XCom, large data via remote storage.
- **Dagster** (`docs/guides/build/assets/index.md`, verified): assets, not tasks, as the primitive. "An asset is an object in persistent storage, such as a table, file, or persisted machine learning model. An asset definition is a description, in code, of an asset that should exist and how to produce and update that asset." Materializations (counted) vs observations (uncounted) as first-class events.
- **Prefect** (`docs/v3/concepts/flows.mdx`, verified): named state machine — `Scheduled → Pending → Running → Completed` with `Failed`, `Cancelled`, `Crashed`, plus the operational concept of "zombie flow runs." Parameter schemas auto-generated via Pydantic. A hard operational limit: "Flow run parameters cannot exceed 512 KB in size by default."

The common thread: every production orchestrator documents (a) a declarative graph, (b) per-node idempotency or determinism contract, (c) parameter schemas, (d) a state-machine log per run, (e) a connections/secrets registry, and (f) a lineage event stream.

### 1.15 Adversarial collaboration — required artifacts and protocol steps

**What it is.** A research protocol, originally formalized by Daniel Kahneman, in which two parties who hold opposing positions commit in writing to jointly designed empirical tests whose results both sides pre-agree to take seriously.

**Required artifacts** (verbatim, https://www.edge.org/adversarial-collaboration-daniel-kahneman, verified; and Isch et al. 2025, *Theory and Society*, https://link.springer.com/article/10.1007/s11186-025-09634-2, verified):

- A pre-project agreement that serves "almost as a contract" to hold collaborators accountable.
- Clearly articulated methods and agreed-upon protocols.
- A pre-registered methodology.
- A trusted, neutral third-party arbiter who maintains the record. "The protocol insisted on the mediator's responsibility for record keeping." (Kahneman)
- An explicit acceptance that the initial study will be inconclusive: "The key statement in the protocol requires participants to accept in advance that the initial study will be inconclusive. Allow each site to propose an additional experiment." (Kahneman)
- Neutral execution venue where possible — Templeton-funded ACs "are conducted with extremely careful protocols, including a requirement that the adversaries sign on to take seriously results that challenge their theory" and "the research is collected by neutral laboratories. It's not collected by the adversaries themselves."
- Conflict-resolution mechanics from the 2025 survey of 29 AC participants: pausing meetings to diffuse tensions, splitting collaborators into separate email threads, arbiters blinding themselves to conditions before analysis.

Kahneman also recommends "the combination of adversarial collaboration with pre-registration" as "particularly useful." That recommendation is directly relevant to a pre-registered, SAP-locked platform like hc-grc.

### 1.16 Autonomous-science-platform documentation patterns and documented failure modes

Across the Sakana AI Scientist (v1 and v2), ChemCrow, Coscientist, and Agent Laboratory repositories, six documentation patterns recur, and one set of failure modes is reported in detail:

**Recurring documentation patterns** (synthesized from the verified repo READMEs):

- Template/seed JSON as the agent contract — AI Scientist v1 ships per-template `prompt.json` + `seed_ideas.json`; v2 ships ideas as JSON with `Interestingness`, `Feasibility`, `Novelty` scores and a boolean `novel` label; Agent Laboratory ships per-task YAML in `experiment_configs/`.
- A single launcher script as the public API (`launch_scientist.py`, `launch_scientist_bfts.py`, `ai_lab_repo.py`).
- Worked-example artifacts shipped in-repo (AI Scientist v1 ships ten example PDFs).
- Tools-as-classes-with-descriptions (ChemCrow's 18 chemistry tools — the LangChain pattern, where the tool description doubles as the LLM-facing prompt).
- Timestamped run directory with HTML graph visualization (AI Scientist v2's `experiments/<timestamp>_<idea>/logs/0-run/unified_tree_viz.html`).
- HITL exposed as a CLI flag (`copilot-mode: "true"` in Agent Laboratory), not as a graph node.

**Failure modes documented in Beel, Kan & Baumgart 2025** (arXiv 2502.14297, *Evaluating Sakana's AI Scientist*, verified via the ar5iv mirror at https://ar5iv.labs.arxiv.org/html/2502.14297):

- "Four of seven manuscripts (57%) contained incorrect or hallucinated numerical results, with discrepancies in hyperparameters and performance metrics."
- "five out of twelve proposed experiments (42%) failed due to coding errors, and those that did run often produced logically flawed or misleading results."
- "Structural errors were frequent, including missing figures, repeated sections, and placeholder text such as 'Conclusions Here'."
- "poorly substantiated, with a median of just five citations per paper—most of which were outdated (only five out of 34 citations were from 2020 or later)."
- "several generated research ideas were incorrectly classified as novel, including well-established concepts such as micro-batching for stochastic gradient descent (SGD)."
- "Modifications made by its LLM-based coding assistant (Aider) are often undocumented, leading to reproducibility issues and making it hard to trace experimental changes."

The same paper proposes two schema-level artifacts the field is converging on:

- **RPML — Research Process Markup Language**: "RPML—based on a schema such as JSON or XML—should record experiment setups, code versions, container images, dataset versions, hyperparameters, and citation contexts automatically, ensuring full traceability and reproducibility."
- **RAML — Research Attribution Markup Language**: "a JSON-based schema embedded within research papers, either as inline annotations or in a separate metadata file" with levels `Generated | Edited | Suggested`.

These are not yet standards; they are well-cited proposals. They are nonetheless the most directly applicable forward-looking schema the survey turned up, because they were designed specifically for agentic research output.

### 1.17 Phoenix / OpenInference / OpenTelemetry — observability for agents

**What it is.** Arize Phoenix is "an open-source, self-hosted observability platform for monitoring, debugging, and improving LLM applications and AI Agents at scale. It is built on top of OpenTelemetry and is powered by OpenInference instrumentation" (https://arize.com/phoenix/, verified via search snippets). OpenInference is "a set of conventions that standardizes tracing in AI applications" and provides "end-to-end traces with clear parent–child span relationships, unified visibility across agent, LLM, and tool spans, and a consistent trace schema across runtimes and LLMs."

**Why hc-grc cares.** Phoenix is in the existing hc-grc stack. OpenInference plus OpenTelemetry give the platform a portable trace schema that survives a swap of the agent framework. Phoenix's documented vendor support includes LangGraph, CrewAI, OpenAI Agents SDK, and DSPy, which means downstream evaluator code is portable.

---

## 2. Gap analysis vs. the hc-grc tentative documentation list

The hc-grc roadmap of new docs is: `AGENT_WORKFLOW.md`, `HANDOFFS.md`, `CONTRACTS.md`, `INFRASTRUCTURE_REQUIREMENTS.md`, `CAPABILITY_MATRIX.md`, `GATES.md`, `STAGES.md`, `ADVERSARIAL_PROTOCOL.md`, `EVOLUTION.md`, `OBSERVABILITY.md`.

### What is missing against community convention

The roadmap is strong on workflow, contract, and gate documentation. It is comparatively thin in five areas where mature platforms ship explicit artifacts:

**Run manifest schema.** No document in the roadmap defines the per-run JSON that records the topology used, the agent revisions, the model versions and seeds, the container digest, the data split hash, the Qdrant collection hash, the MLflow run id, the Phoenix trace id, and the lab-notebook commit. Beel et al. 2025 (arXiv 2502.14297) name this directly as the field's largest documentation gap and propose it under the name RPML. Without it, the hc-grc lab notebook records human intent but not execution truth.

**Provenance schema (formal).** `CONTRACTS.md` covers artifact schemas. It does not, as named, commit hc-grc to a formal provenance vocabulary. W3C PROV-DM gives the platform a 7-relation core that maps directly to LangGraph topology — `Activity` (node), `Entity` (artifact), `Agent` (LLM agent or human reviewer), `WasInformedBy` (handoff), `ActedOnBehalfOf` (delegation), `WasDerivedFrom` (revision). Naming PROV-DM as the canonical provenance vocabulary closes the gap between "we record handoffs" and "an external auditor can verify lineage."

**Pre-registration ledger.** `STAGES.md` will cover the lifecycle. It does not name a document that holds the timestamped pre-registration record — locked SAP commit hash, OSF or RFC 3161 timestamp, hypothesis-set version, gate decisions. This is the single document a journal reviewer or an FDA-style audit would request first.

**Reproducibility contract.** The roadmap has `INFRASTRUCTURE_REQUIREMENTS.md` but no document that maps hc-grc against the NeurIPS 2026 reproducibility checklist, the TOP guidelines' seven practices, and the MLRC scope criteria. For a publication-target platform this is a foreseeable gap.

**Cards-as-discoverable-manifests.** The roadmap treats AGENT.md as authored documentation. The A2A AgentCard convention and Mitchell-style model cards demonstrate that agent identity becomes auditable only when the card is machine-discoverable and content-addressed. A `CARDS_SPEC.md` (or equivalent) would commit hc-grc to a card schema version, an `agent_id` derivation rule, and a deprecation field.

### What is redundant

`CAPABILITY_MATRIX.md` and `INFRASTRUCTURE_REQUIREMENTS.md` together overlap meaningfully with `CONTRACTS.md`. All three derive from the same frontmatter (tools, MCP servers, skills) on the AGENT cards. If all three are authored independently, they will drift. The cleanest separation is: `INFRASTRUCTURE_REQUIREMENTS.md` is a deployment-time contract (what must be installed), `CAPABILITY_MATRIX.md` is a runtime contract (what each agent can do), and `CONTRACTS.md` is an interaction contract (input/output schemas at boundaries). All three should be auto-generated from the cards (see §4); the only authored prose is the rationale prefacing each.

### What is misnamed against community convention

`AGENT_WORKFLOW.md` is fine as an internal name, but the community convention for "the document that describes how the graph runs" is closer to `ARCHITECTURE.md` (in most LangGraph-adjacent repos) or `TOPOLOGY.md`. Microsoft Agent Framework names its equivalent `docs/design/`. If publication or external review is in scope, naming the file `ARCHITECTURE.md` increases discoverability.

`ADVERSARIAL_PROTOCOL.md` is well-chosen and corresponds directly to the Adversarial Collaboration Project's framing (https://web.sas.upenn.edu/adcollabproject/). The alternative `MANY_ANALYST_PROTOCOL.md` would be more discoverable to ML reviewers familiar with TOP terminology; the current name reads more cleanly to a domain expert. Either works; keep `ADVERSARIAL_PROTOCOL.md` and reference the TOP Many Analyst / Multiverse equivalents inside it.

`EVOLUTION.md` is unique to hc-grc. The community-standard primitive for the same content is "Architectural Decision Record" (ADR). I would split: `EVOLUTION.md` becomes a narrative ledger (a quarterly summary), and `decisions/NNNN-*.md` files (Microsoft Agent Framework pattern) hold the individual decisions with full context.

`OBSERVABILITY.md` is conventional and well-chosen.

`GATES.md` is precise and correct.

---

## 3. Recommended additions

These are concrete proposals, each with the requested fields (what / why / gap closed / authors / consumers) plus a sequencing rationale.

### 3.1 `RUN_MANIFEST.md` + per-run `manifest.json` schema

**What.** A document that defines the JSON schema for the manifest written at the end of every research run. Fields at minimum: `run_id`, `topology_hash`, `agent_revisions[]`, `model_versions{}`, `seeds{}`, `container_digest`, `data_split_hash`, `qdrant_collection_hash`, `mlflow_run_id`, `phoenix_trace_id`, `lab_notebook_commit`, `gate_decisions[]`, `pre_registration_ref`.

**Why.** This is the single artifact that lets an external auditor replay or attribute any finding. It is the platform's RPML-equivalent (Beel et al. 2025, arXiv 2502.14297, verified).

**Gap closed.** Anti-cherry-picking is currently enforced by the lab notebook. Lab notebook records intent; manifest records execution truth. The gap between the two is where the Sakana AI Scientist evaluation paper found 42% of experiments failed silently and 57% of manuscripts contained hallucinated numbers.

**Authors.** The Orchestrator emits the manifest automatically. The schema document is authored by Provenance Agent + Quality Agent.

**Consumers.** Reviewers, replicators, the Adversarial Protocol arbiter, the Evolution agent.

**Sequencing.** First. Almost every other recommended doc references this schema.

### 3.2 `PROVENANCE_MODEL.md`

**What.** Names W3C PROV-DM (https://www.w3.org/TR/prov-dm/, verified) as the canonical provenance vocabulary and maps the seven relations to LangGraph constructs. Defines the PROV-O serialization the platform emits.

**Why.** Without naming a formal vocabulary, "provenance" devolves into ad-hoc notebook prose. PROV-DM is the only fetched standard with a delegation primitive (`ActedOnBehalfOf`) that matches the supervisor-with-sub-agents topology.

**Gap closed.** Currently `CONTRACTS.md` defines artifact schemas. `PROVENANCE_MODEL.md` defines the relationships between artifacts and the agents that produced them — which `CONTRACTS.md` is not the natural place for.

**Authors.** Provenance Agent + a domain expert who has read the spec.

**Consumers.** External reviewers (journal or audit), the Adversarial Protocol arbiter, downstream tooling that consumes lineage events.

**Sequencing.** Second. Anchors §3.1 by giving the manifest fields formal semantics.

### 3.3 `PREREGISTRATION_LEDGER.md` + `protocol/registration/` directory

**What.** A timestamped append-only record of: locked SAP commit hash, RFC 3161 timestamp, OSF preregistration URL (if used), hypothesis-set version, every gate decision (with reviewer, rationale, and timestamp), and every protocol revision with its rationale.

**Why.** TOP Level 3 ("Certified") requires "A party independent from the researchers verified" the registration and the analysis plan (https://www.cos.io/initiatives/top-guidelines, verified). NeurIPS 2026 handbook requires methodology disclosure for agent-based methods. A registered-report-style submission requires a verifiable pre-registration record.

**Gap closed.** The current SCF/PROJECT_CHARTER pair documents intent. The lab notebook records narrative. Neither is the timestamped, signed record an auditor or registered-reports journal would require.

**Authors.** Orchestrator (machine-writable timestamps) + human reviewer at each gate.

**Consumers.** Journal reviewers, audit committees, the platform's own Adversarial Protocol arbiter.

**Sequencing.** Third. Should be in place before Gate 2 closes for the first time.

### 3.4 `REPRODUCIBILITY_COMPLIANCE.md`

**What.** A document that maps hc-grc against three primary checklists: the NeurIPS 2026 reproducibility checklist (https://neurips.cc/Conferences/2026/CallForReproducibility, verified), the TOP guidelines' seven practices × three levels (https://www.cos.io/initiatives/top-guidelines, verified), and Paper-with-Code's "Releasing Research Code" guidelines (https://github.com/paperswithcode/releasing-research-code, referenced by NeurIPS handbook).

**Why.** Compliance documents are the cheapest insurance against late-stage submission rework. They also force the question early: which items are we Level 1 ("Disclosed") on and which are we Level 3 ("Certified") on. The answer changes design decisions.

**Gap closed.** "We are reproducible" becomes "we are TOP Level 2 on Analysis Code Transparency, Level 1 on Materials Transparency, and we have an open question about Computational Reproducibility verification." The auditable version.

**Authors.** Reproducibility Agent + Quality Agent.

**Consumers.** Submission committees, the platform's external reviewers, the principal investigator.

**Sequencing.** Fourth.

### 3.5 `CARDS_SPEC.md`

**What.** A specification document for the AGENT.md card format. Defines the frontmatter schema, the required body sections, the `agent_id` derivation rule (suggest content-addressed hash following arXiv 2509.18415), the `deprecation` field semantics, and the rule that any frontmatter change is a version bump.

**Why.** The cards are already the canonical agent contract. They are not yet machine-verifiable. A spec turns "48 hand-written cards" into "48 instances of a schema" — and that distinction is what permits §4's auto-generation strategy.

**Gap closed.** Currently the AGENT_TEMPLATE.md is the de facto spec. A spec document upgrades the template into a versioned schema with validation rules.

**Authors.** Orchestrator team + a domain reviewer familiar with A2A AgentCard, Mitchell model cards, and arXiv 2509.18415.

**Consumers.** Every agent author, the Code Review Agent, every downstream auto-generated doc.

**Sequencing.** Fifth, but can run in parallel with §3.1.

### 3.6 `OPENLINEAGE_INTEGRATION.md`

**What.** A document specifying which OpenLineage facets hc-grc emits, which custom facets it defines (following the `hcgrc{Name}{Entity}Facet` naming rule from https://openlineage.io/docs/spec/facets/, verified), and which lineage backend (Marquez, custom) the platform writes to.

**Why.** OpenLineage already integrates with Airflow, dbt, Spark, Dagster, and Flink. Emitting OL events from LangGraph nodes gives hc-grc access to the existing visualization, alerting, and quality-assertion ecosystem without writing it from scratch.

**Gap closed.** `OBSERVABILITY.md` currently covers Phoenix and MLflow. It does not commit hc-grc to a portable lineage event format usable by tooling outside the hc-grc stack.

**Authors.** Platform DevSecOps team + Provenance Agent.

**Consumers.** Downstream lineage visualization, audit tooling, data-quality checks at gate transitions.

**Sequencing.** Sixth. Optional but recommended; emit OL events even if you do not stand up a Marquez instance immediately.

### 3.7 ADR collection — `decisions/NNNN-*.md`

**What.** A numbered, append-only collection of architectural decision records. Each ADR follows the Michael Nygard format: Title, Status (proposed / accepted / superseded / deprecated), Context, Decision, Consequences. Microsoft Agent Framework demonstrates this convention at scale (https://github.com/microsoft/agent-framework, verified).

**Why.** ADRs are the canonical primitive for "why did we do it this way." `EVOLUTION.md` works as a quarterly narrative summary; the ADR collection is the underlying ledger.

**Gap closed.** Currently the lab notebook captures decisions chronologically interleaved with experimental findings. ADRs separate "we changed the analysis plan because of an observation in run X" from the observation itself.

**Authors.** Whichever agent or human proposes the change.

**Consumers.** Future-Thomas, future maintainers, the Adversarial Protocol arbiter when asked "why did the platform's design shift between Gate 3 and Gate 4."

**Sequencing.** Seventh. Pre-populate the existing constitution-level decisions (PROJECT_CHARTER, RESEARCH_DESIGN, RISK_CONSTITUTION, SCF_CONSTITUTION) as ADRs so the ledger does not start empty.

### 3.8 `INCIDENTS.md` (or `FAILURES.md`)

**What.** An append-only record of every documented failure: agent timeout, schema violation, gate-rejection that caused a protocol revision, hallucinated citation caught at review, etc. Format follows post-mortem conventions (Google SRE workbook is a reasonable reference): timestamp, summary, detection, response, root cause, contributing factors, action items, status.

**Why.** Every failure mode listed in §1.16 from the Sakana evaluation paper (arXiv 2502.14297) describes a failure that was discovered only because someone read the outputs carefully and remembered it. A single document, append-only, makes the institutional memory portable.

**Gap closed.** The AGENT cards' "Failure Modes & Recovery" tables describe failure types ex ante. They do not record actual incidents.

**Authors.** Whichever agent or human encountered the failure.

**Consumers.** Quality Agent, Adversarial Protocol arbiter, the platform's later self-evaluation against MLRC reproducibility criteria.

**Sequencing.** Eighth. Empty at platform start; populates organically.

### 3.9 Sequencing rationale

The order above is not arbitrary. RUN_MANIFEST.md is first because every other doc references its fields. PROVENANCE_MODEL.md is second because it gives the manifest fields formal semantics. PREREGISTRATION_LEDGER.md is third because it must exist before any confirmatory run. REPRODUCIBILITY_COMPLIANCE.md is fourth because it is cheap once the first three are written and surfaces design tradeoffs early. CARDS_SPEC.md is fifth and is the precondition for the auto-generation work in §4. OPENLINEAGE_INTEGRATION.md and the ADR collection can be done in parallel from sixth and seventh. INCIDENTS.md is empty at start and grows organically.

---

## 4. Auto-generation opportunities

The hc-grc plan already names four docs as programmatically derived from the AGENT cards: HANDOFFS, CONTRACTS, INFRASTRUCTURE_REQUIREMENTS, CAPABILITY_MATRIX. The following are additional derivations available with the same parser plus minimal runtime instrumentation.

**`GATES.md` — partial auto-generation.** Every Handoff section in every AGENT.md card names a "Human gate" or "None." Parsing the cards yields the gate inventory (which gates exist, which agents pass through them) and the gate-to-team mapping. The prose explaining each gate's criteria stays hand-authored; the inventory table is generated.

**Agent-team topology graph.** Parsing the Handoffs sections across all 48 cards yields a directed graph: edges from "Receives from" to "Passes to." This is the input to a Graphviz / Mermaid render of the full topology, suitable for inclusion in `AGENT_WORKFLOW.md` (or `ARCHITECTURE.md`) and for use as a topology hash field in the run manifest.

**Skill catalog.** Aggregating the `skills:` frontmatter field across cards gives the platform's full declared skill inventory, the agents that claim each skill, and version drift (if cards declare different versions of the same skill). This becomes either part of `CAPABILITY_MATRIX.md` or a separate `SKILLS_INVENTORY.md`.

**Tool / MCP-server inventory with concentration analysis.** Aggregating the `tools:` frontmatter field gives the platform's full MCP-server dependency surface. Concentration analysis (which servers are single points of failure across multiple agents) is a single SQL query against the parsed cards. This complements `INFRASTRUCTURE_REQUIREMENTS.md` with a risk view.

**Failure-mode catalog.** Aggregating "Failure Modes & Recovery" tables across all 48 cards yields a corpus of every named failure with detection logic and recovery procedure. This is the input to `INCIDENTS.md` taxonomy and to a regression test suite (each row is a `pytest.mark.failure_mode` case).

**Evaluation-criteria checklist.** Aggregating "Evaluation Criteria" sections gives the platform's full Definition of Done across agents. This is the input to the Quality Agent's per-run checklist and can be cross-referenced against the run manifest at completion.

**Behavioral-constraint registry.** Aggregating "Behavioral Constraints" sections gives every hard prohibition across the platform. This is the input to a constraint-violation linter for the Code Review Agent.

**Run-manifest from runtime.** The manifest itself (§3.1) is generated by the Orchestrator from LangGraph state. The schema is documented; the instances are emitted.

**OpenLineage events from runtime.** Each LangGraph node emission becomes an OpenLineage `RunEvent` with facets populated from the node's inputs, outputs, and metadata. The facet schemas come from the OpenLineage spec; the values come from the running graph.

**Topology hash for the manifest.** Hashing the parsed Handoffs DAG yields a stable identifier for "the workflow version this run executed." Combined with agent-revision pins, it gives the manifest a strong identity field.

**What stays hand-authored.** Anything narrative — PROJECT_CHARTER, RESEARCH_DESIGN, RISK_CONSTITUTION, SCF_CONSTITUTION, PROVENANCE_MODEL, REPRODUCIBILITY_COMPLIANCE, ADRs, the prose preface of every auto-generated doc, the rationale section of every gate, the incident write-ups. The auto-generation does not eliminate authorial work; it eliminates copy-and-paste drift.

---

## 5. Pitfalls — what other platforms got wrong

These are documented failure patterns from primary sources. Most have already been mentioned in §1; this section consolidates them into the patterns hc-grc should design against.

**Documentation drift.** When the same fact is authored in two places, the two places will disagree within months. LangGraph's AGENTS.md / CLAUDE.md pair is byte-identical for exactly this reason. The hc-grc roadmap currently has three docs (`CAPABILITY_MATRIX`, `INFRASTRUCTURE_REQUIREMENTS`, `CONTRACTS`) that derive from the same frontmatter. If they are authored independently, they will drift. The mitigation is to author the cards as the single source of truth and to generate the three docs deterministically.

**The 12-line README.** Coscientist's repository (https://github.com/gomesgroup/coscientist, verified) ships a 12-line README and directory names matched to paper figure numbers. The repo is supporting-information for the Nature paper, not a runnable platform. The pitfall is to let a README of that shape stand in for architecture documentation when the platform is meant to be reused. For a 48-agent platform, `README.md` must be navigation, not architecture.

**Implicit agent identity.** AI Scientist v1 and v2 (https://github.com/SakanaAI/AI-Scientist and https://github.com/SakanaAI/AI-Scientist-v2, verified) encode agent identity in Python module names (`mlesolver.py`, `papersolver.py`). The result is that prompt diffs become undocumented and untrackable. hc-grc's AGENT.md card per agent is the right pattern; the pitfall would be to let the prompts drift inside the agent code without revving the card frontmatter.

**Undocumented intermediate edits.** Beel et al. 2025 (arXiv 2502.14297, verified): "Modifications made by its LLM-based coding assistant (Aider) are often undocumented, leading to reproducibility issues and making it hard to trace experimental changes." Any sub-agent that modifies code or analysis between gates must emit a diff into the run manifest. Hidden modifications are the most expensive class of bug in autonomous research systems precisely because they are observable only at the end.

**Auto-novelty checks without baselines.** Beel et al. also documented that AI Scientist v1 classified "micro-batching for SGD" as novel. The pitfall pattern: an LLM-based novelty check without a documented baseline corpus and a rejection log. For controls characterization, novelty claims need a documented baseline and a paper trail.

**Gates as rubber stamps.** The Adversarial Collaboration Project's 2025 retrospective (Isch et al., https://link.springer.com/article/10.1007/s11186-025-09634-2, verified) observed that "to date, we are not aware of any AC where one side openly admitted thorough defeat." Gates and adversarial reviews tend to converge on consensus when the same parties review repeatedly. The hc-grc mitigation should rotate reviewers, require a written dissent or assent at each gate, and surface gate decisions verbatim in the pre-registration ledger so that pattern-matching ("did this reviewer ever say no") is one query.

**Observability as read-only.** Phoenix, MLflow, and lineage graphs are read-only by default — they tell you what happened but do not gate anything. The pitfall is to invest in observability without wiring at least one assertion (data quality, schema, gate precondition) that can halt the workflow when a tracked metric goes out of range. OpenLineage's `dataQualityAssertions` facet is the spec hook for this (https://openlineage.io/docs/spec/facets/, verified).

**Templated example outputs in lieu of test suites.** AI Scientist v1 ships ten example PDFs but no eval suite. Showcase artifacts do not substitute for evaluation manifests. hc-grc's "Evaluation Criteria" sections per agent are the right primitive; the pitfall would be to ship example outputs as a stand-in for a continuously running evaluation harness.

**Reading-day rot.** Even well-maintained docs drift if no one is required to read them. The Microsoft Agent Framework ADR convention is partly a forcing function: numbered ADRs accumulate, and any contributor making a change must either reference an existing ADR or write a new one. The hc-grc equivalent is to make the run manifest (§3.1) reference the ADR ids that govern its execution. If an ADR is never referenced, it is a candidate for retirement or merge into another doc.

**Over-documentation.** The opposite failure. A 200-page architecture document that no one reads is worse than a 20-page document that everyone does. The Microsoft Agent Framework keeps decisions short and numbered. LangGraph keeps `AGENTS.md` to 57 lines. The hc-grc roadmap, as named, is in danger of producing ten substantial documents; the recommendation is to keep each under 2000 words where the auto-generation table is the bulk of the content.

**Verifying that gates record dissent, not just consent.** Tied to the gates-as-rubber-stamps point. The pre-registration ledger should record gate dissent in the same format as gate assent: both are first-class outcomes. If the ledger only has assents, the gate is decorative.

---

## 6. Tool / format recommendations

This section names which tools should generate or maintain which docs. Verified capabilities are anchored to the relevant primary source. Capabilities I could not verify in this session are marked explicitly.

**Card schema validation — `pydantic` + `python-frontmatter`.** The AGENT.md cards already use YAML frontmatter. A Pydantic model per the `CARDS_SPEC.md` schema, applied at PR time via pre-commit, prevents schema drift and is the precondition for every auto-generated doc. Verified Pydantic capability — frontmatter parsing is a one-line library call; schema validation is the Pydantic primary use case.

**Auto-generated docs — write the cards, generate the rest.** A single Python script that walks `agents/**/AGENT.md`, parses the frontmatter and known sections, and emits `HANDOFFS.md`, `CONTRACTS.md`, `INFRASTRUCTURE_REQUIREMENTS.md`, `CAPABILITY_MATRIX.md`, `GATES.md` (inventory portion), `SKILLS_INVENTORY.md`, plus the topology Graphviz/Mermaid file. Run on pre-commit and in CI. No third-party tool required; the data shape is already in your hands.

**Static docs hosting — MkDocs with `mkdocs-material` or Sphinx.** Both are widely used. MkDocs-material is the lower-friction choice for a primarily Markdown corpus and ships search out of the box (https://squidfunk.github.io/mkdocs-material/, search snippet — not directly verified in this session). Sphinx with `myst-parser` is the right choice if you want stronger cross-reference and citation tooling, which a research platform with peer-reviewed citation requirements may want. My recommendation: MkDocs first, migrate to Sphinx if and when the citation-graph requirements grow.

**Provenance emission — emit W3C PROV-O (RDF) from the Orchestrator.** PROV-DM (https://www.w3.org/TR/prov-dm/, verified) names PROV-O as the W3C-recommended RDF serialization. Python tooling: `rdflib` is mature. The Orchestrator already emits routing decisions to MLflow; emitting the same events as PROV-O triples to a side store gives external auditors a portable lineage graph. Verified — `rdflib` and W3C PROV-O are stable, primary-source-defined.

**Lineage events — OpenLineage SDK with custom facets prefixed `hcgrc`.** The OpenLineage spec (https://openlineage.io/docs/spec/facets/, verified) explicitly permits and prescribes the naming pattern `{prefix}{name}{Entity}Facet`. The OpenLineage Python SDK is documented at https://github.com/OpenLineage/OpenLineage (verified — repo is a graduated LF AI & Data project). Recommended initial custom facets: `hcgrcHitlGateRunFacet`, `hcgrcExploratoryPhaseJobFacet`, `hcgrcSapLockDatasetFacet`, `hcgrcAgentRevisionRunFacet`.

**Runtime observability — Phoenix (already in stack) + OpenInference.** Phoenix is "built on top of OpenTelemetry and is powered by OpenInference instrumentation" (https://arize.com/phoenix/, verified via WebSearch snippets). The OpenInference standard is at https://github.com/Arize-ai/openinference (referenced from Phoenix). Recommendation: standardize on OpenInference span semantics from the start. They are vendor-neutral and survive a swap to LangSmith or another tracer.

**Experiment tracking — MLflow (already in stack).** The MLflow primary docs at https://mlflow.org/docs/latest/tracking.html could not be fetched in this session; I therefore do not assert specific MLflow lineage features here without verification. The orchestrator AGENT.md card already documents MLflow as the routing-decision logger; that scope is appropriate. Confirm specific MLflow lineage/registry capabilities against the live docs before extending scope.

**Data and model versioning — DVC.** Primary docs (https://dvc.org/) could not be fetched in this session. I will not assert DVC capabilities without verification. The `dvc.yaml` / `.dvc` lineage pattern is well-documented in the public DVC docs; confirm against the live docs before committing.

**Pre-registration backing — OSF Registries + RFC 3161 timestamp.** OSF's preregistration page returned an empty SPA shell on fetch; the OSF help page at https://help.osf.io/article/158-create-a-preregistration is the recommended re-fetch target before relying on specific OSF templates. RFC 3161 timestamping is a stable standard for the signed commit hash on the pre-registration branch — implementation via FreeTSA or a paid timestamp authority. Confirm RFC 3161 capability against the chosen TSA.

**Dataset metadata — Croissant for any public dataset release.** Croissant's primary docs (https://github.com/mlcommons/croissant and the arXiv paper at https://arxiv.org/abs/2403.19546) timed out in this session; I will not assert specific Croissant fields without verification. The platform's NeurIPS-compliance posture (Schema.org or DCAT, per the verified NeurIPS 2026 handbook) is satisfied by Croissant since it builds on Schema.org per WebSearch summaries. Confirm against the live Croissant docs before committing to specific RecordSet / Field semantics.

**ADR tooling — `adr-tools` or plain Markdown.** Either is fine. `adr-tools` (https://github.com/npryce/adr-tools, not directly verified in this session) automates numbering and supersede links. Plain Markdown with a numbered convention works as well. Microsoft Agent Framework appears to use plain Markdown (verified — `docs/decisions/0021-*.md` files in https://github.com/microsoft/agent-framework).

**CI integration.** Pre-commit hooks: card schema validation, auto-generated doc regeneration, ADR format check. CI on PR: full doc regeneration with diff check, broken-link check, citation-format check against a defined style (suggest IEEE numeric or Vancouver since the platform is publishing in venues that accept either).

---

## Sources index

This index lists every primary source consulted. Each source is marked Verified (fetched in full or in substantive part), Partial (fetched but truncated or hit token/time limits), or Unfetched (could not be retrieved in this session). Where a source is Unfetched, no claim in this document depends on its specific content; any reference to that source is for the reader's onward investigation.

### LangChain / LangGraph

- https://docs.langchain.com/oss/python/langchain/human-in-the-loop — Verified
- https://docs.langchain.com/oss/python/langgraph/persistence — Verified
- https://docs.langchain.com/oss/python/langgraph/interrupts — Verified
- https://github.com/langchain-ai/langgraph (README and AGENTS.md) — Verified
- https://github.com/langchain-ai/langgraph/blob/main/AGENTS.md — Verified
- https://github.com/langchain-ai/langgraph-supervisor-py — Verified
- https://docs.smith.langchain.com — Unfetched (timeout)

### Multi-agent frameworks

- https://github.com/microsoft/agent-framework — Verified
- https://github.com/microsoft/autogen — Verified
- https://github.com/FoundationAgents/MetaGPT — Verified
- https://github.com/openai/swarm — Verified
- https://github.com/crewAIInc/crewAI — Partial (README fetched; deep extraction limited)

### Reproducibility and provenance

- https://neurips.cc/Conferences/2026/MainTrackHandbook — Verified
- https://neurips.cc/Conferences/2026/CallForReproducibility — Verified
- https://www.cos.io/initiatives/top-guidelines — Verified
- https://reproml.org/ — Verified
- https://www.w3.org/TR/prov-dm/ — Verified
- https://www.tensorflow.org/tfx/guide/mlmd — Verified
- https://mlflow.org/docs/latest/tracking.html — Unfetched (timeout)
- https://dvc.org/doc/use-cases/versioning-data-and-models — Unfetched (timeout)
- https://github.com/mlcommons/croissant — Unfetched (timeout)
- https://arxiv.org/abs/2403.19546 (Croissant paper) — Unfetched (timeout)
- https://arxiv.org/abs/2507.01075 (Provenance Tracking in Large-Scale ML Systems) — Unfetched (timeout)
- https://help.osf.io/article/158-create-a-preregistration — Unfetched (OSF SPA shell)

### Agent governance

- https://modelcontextprotocol.io/specification — Verified
- https://a2a-protocol.org/latest/specification/ — Partial (size truncated; field names cross-confirmed)
- https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/ — Verified
- https://www.ibm.com/think/topics/agent2agent-protocol — Verified via WebSearch summary
- https://arxiv.org/abs/2509.18415 (Context Lineage Assurance) — Verified (fetched full PDF including Listing 1)
- https://arxiv.org/abs/2505.02279 (Survey of Agent Interoperability Protocols) — Partial (snippets only)
- https://arxiv.org/abs/1810.03993 (Mitchell et al., Model Cards) — Partial (snippets only; PDF timeout)
- https://huggingface.co/docs/hub/model-cards — Partial (snippets only)

### Adversarial collaboration

- https://web.sas.upenn.edu/adcollabproject/publications/ — Verified
- https://www.edge.org/adversarial-collaboration-daniel-kahneman — Verified
- https://link.springer.com/article/10.1007/s11186-025-09634-2 (Isch et al. 2025) — Verified
- https://journals.sagepub.com/doi/abs/10.1111/1467-9280.00350 (Mellers/Hertwig/Kahneman 2001) — Unfetched (paywall)
- https://training.cochrane.org/handbook — Unfetched (timeout)
- https://www.equator-network.org/ — Unfetched (timeout)
- https://www.nist.gov/itl/ai-risk-management-framework — Unfetched (proxy block)

### DAG and lineage

- https://openlineage.io/docs/ — Verified
- https://openlineage.io/docs/spec/object-model — Verified
- https://openlineage.io/docs/spec/facets/ (index pages) — Verified
- https://github.com/OpenLineage/OpenLineage — Verified
- https://raw.githubusercontent.com/apache/airflow/main/airflow-core/docs/best-practices.rst — Verified
- https://raw.githubusercontent.com/dagster-io/dagster/master/docs/docs/guides/build/assets/index.md — Verified
- https://raw.githubusercontent.com/PrefectHQ/prefect/main/docs/v3/concepts/flows.mdx — Verified

### Autonomous-science platforms

- https://github.com/SakanaAI/AI-Scientist — Verified
- https://github.com/SakanaAI/AI-Scientist-v2 — Verified
- https://ar5iv.labs.arxiv.org/html/2502.14297 (Beel/Kan/Baumgart evaluation) — Verified
- https://github.com/ur-whitelab/chemcrow-public — Verified
- https://github.com/gomesgroup/coscientist — Verified
- https://github.com/SamuelSchmidgall/AgentLaboratory — Verified
- https://deepmind.google/blog/co-scientist-a-multi-agent-ai-partner-to-accelerate-research/ — Partial (search snippets)
- https://arxiv.org/abs/2408.06292 (AI Scientist v1 paper) — Unfetched (timeout)
- https://arxiv.org/abs/2504.08066 (AI Scientist v2 paper) — Unfetched (timeout)
- https://arxiv.org/abs/2304.05376 (ChemCrow paper) — Unfetched (timeout)
- https://www.nature.com/articles/s41586-023-06792-0 (Coscientist Nature paper) — Unfetched (paywall)

### Observability

- https://arize.com/phoenix/ — Verified via WebSearch summaries
- https://github.com/Arize-ai/phoenix — Referenced; not directly fetched in this session
- https://github.com/Arize-ai/openinference — Referenced; not directly fetched in this session

---

## Closing note on the platform's hard citation constraint

The platform's stated constraint is that every algorithm selection and methodology cites a peer-reviewed source or authoritative standard. The recommendations in this document are anchored against that constraint with verified citations wherever possible. Three categories of citation strength are present:

1. **Strong**: W3C recommendations (PROV-DM), NeurIPS handbook text, peer-reviewed papers (Mellers/Hertwig/Kahneman 2001 via Kahneman's own retelling; Isch et al. 2025; Beel et al. 2025), and Linux Foundation / graduated open-source specifications (OpenLineage). These can be cited directly in protocol documents.

2. **Authoritative-but-evolving**: A2A specification (Linux Foundation, but still v0.x and v1.x evolution active), MCP specification (Anthropic-stewarded but still evolving), the OpenInference convention, the TOP Guidelines (CoS-maintained, regularly updated). These are citable but require version pinning.

3. **Proposals, not standards**: RPML and RAML (Beel et al. 2025), the `agent.json` family, the cryptographic identity extension in arXiv 2509.18415. These are well-cited proposals worth adopting in spirit but should not be cited as if they were standards.

The platform's adversarial-protocol stance applies to its own documentation as well. This survey reports what it could verify and names what it could not. A senior practitioner should be able to commit to a sequencing and tooling plan from this document. Where any specific tool capability is load-bearing for a decision (MLflow lineage, DVC pipeline stages, Croissant RecordSet semantics, LangSmith dataset spec), the recommendation is to re-fetch the source and verify before commitment — the unfetched-sources index above names them.
