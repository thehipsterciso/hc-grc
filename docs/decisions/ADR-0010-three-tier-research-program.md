# ADR-0010: Three-Tier Research Program Architecture

**Status:** Accepted  
**Date:** 2026-06-10  
**Author:** Thomas Jones  
**Relates to:** ADR-0001 (LangGraph), ADR-0008 (Supervisor+Hybrid), PROJECT_CHARTER.md

---

## Context

The initial HC-GRC platform was scoped as an empirical analysis of the Secure Controls Framework (SCF). Through architectural reasoning, the full research program has been clarified as substantially larger: the SCF analysis is the foundation of a multi-framework, multi-tier research program whose ultimate goal is an empirically-grounded organizational risk and financial impact model.

This ADR captures the strategic architecture of the full program so that every design decision in the current platform — agent roles, state schemas, ARA artifact formats, graph data models — is made with the full program in mind.

---

## Decision

**The HC-GRC research program is organized into three tiers. The current project (hc-grc) is Tier 1, SCF. All design decisions in Tier 1 must be made with Tier 2 and Tier 3 as explicit downstream consumers.**

---

## The Three-Tier Architecture

### Tier 1 — Framework Science (current project, plus future framework projects)

**Purpose:** Build mathematically rigorous knowledge graphs of each framework. Validate SCF's STRM mappings empirically. Produce the first empirical evidence about whether the GRC industry's dominant metaframework accurately describes the relationships it claims.

**The core insight:** The SCF is simultaneously a research subject AND the measurement instrument. Its ~280,000 STRM mappings are a structured set of claims — "SCF control X has relationship type R to framework Y control Z." These claims are the hypothesis set for each framework study. The research does not trust the mappings; it tests them.

**Projects in this tier:**
- `hc-grc` (current) — SCF analysis, all 5 modules (P1–P5)
- `hc-grc-nist-800-53` — Tests SCF→NIST 800-53 STRM mapping validity
- `hc-grc-nist-800-82` — Tests SCF→NIST 800-82 (ICS/OT) mapping validity
- `hc-grc-cis-v8` — Tests SCF→CIS Controls v8 mapping validity
- Additional frameworks as licensed data becomes available

**What Tier 1 produces:**
- Per-framework knowledge graphs (nodes = controls, edges = typed relationships)
- Empirical validation scores for STRM mapping subsets
- Null results for mappings that fail empirical testing
- ARA artifacts: structured JSON/Parquet knowledge graphs for Tier 2 consumption

**Key constraint:** Each framework project is independently pre-registered and reproducible. Pre-registration integrity requires that no framework project's confirmatory data is visible while another framework project's hypotheses are being formed. Separate projects enforce this boundary structurally.

**Shared methodology:** The analysis methodology (P1–P5 modules, LangGraph architecture, gate structure, checkpointing) is identical across all Tier 1 projects. The only variables are: which STRM mapping subset is loaded, which target framework's control structure is tested against, and which data licensing constraints apply.

---

### Tier 2 — Comparative Analysis (future: `hc-grc-comparative`)

**Purpose:** Ingest all Tier 1 knowledge graphs. Answer questions no single framework project can answer: where does the GRC landscape genuinely converge, where does it diverge, and which controls are load-bearing across frameworks vs. cosmetic?

**The research program this tier enables:**

*Gap analysis.* Which risks are addressed by NIST 800-53 but not CIS v8? Which controls appear in every framework SCF maps to — and are therefore candidates for a universal control baseline? The gaps are the story.

*Alignment and misalignment scoring.* Where frameworks claim to align (through shared SCF STRM mappings), do their control texts actually describe the same requirements? Tier 1 provides the empirical answer per framework pair; Tier 2 synthesizes the pattern across all pairs.

*Control importance ranking.* Graph centrality analysis across all framework graphs combined. Controls that appear as high-centrality nodes in multiple independent framework graphs are empirically load-bearing. This is the first data-driven answer to "what matters most."

*Blast radius modeling.* If control X fails — is deimplemented, misconfigured, or absent — what propagates through the cross-framework control graph? Information cascade modeling on the combined graph quantifies exposure. This is the empirical basis for prioritization that the industry currently approximates with gut instinct.

*Framework archetype discovery.* Dimensionality reduction across all framework control graphs to find the underlying archetypes. The hypothesis: the GRC industry has produced dozens of frameworks that are actually expressing 5-8 underlying control archetypes, obscured by terminology differences and jurisdictional positioning.

**DS/ML stack for Tier 2:**
- Graph analytics: centrality, community detection, subgraph isomorphism across framework graphs
- Information cascade / graph diffusion models for blast radius
- Dimensionality reduction (UMAP, PCA on graph embedding space) for archetype discovery
- Cross-graph alignment: node alignment algorithms to identify functionally equivalent controls across frameworks

---

### Tier 3 — Organizational Impact Modeling (future: `hc-grc-impact`)

**Purpose:** The most commercially significant tier. Take Tier 2's empirical findings about control importance, gaps, alignment, and blast radius, and model their impact on real organizations. Quantify: what does it actually cost an organization when specific controls fail, and by how much?

**Why this matters:** Every current approach to GRC risk quantification — FAIR, vendor risk scoring, compliance gap assessments — is ultimately grounded in expert judgment. The estimates are credible because experts made them, not because they were tested. Tier 3 grounds the same questions in empirically proven framework relationships from Tier 1 and 2.

**The research program this tier enables:**

*[Amended by #64 resolution — 2026-06-10]*

The original Tier 3 design specified causal inference via do-calculus and causal forests. That specification was made before Tier 1 or Tier 2 data was examined. Adversarial review (issue #64) found that causal forests assume identification is already achieved — they do not create it — and that the required data (breach records, financial loss at organizational scale, control posture data) may not exist in usable form for causal inference. FAIR models use expert elicitation precisely because this data is unavailable.

**Tier 3 methodology is TBD by Tier 2 findings.** The platform will evaluate what analytical leverage Tier 2 data provides and propose a Tier 3 methodology at that point. Candidate approaches include genuine causal inference (if an identification strategy is achievable), predictive modeling (if causal identification is not achievable with available data), or actuarial loss modeling grounded in empirically validated framework relationships from Tier 1 and 2.

The commercial objective — quantifying what it costs organizations when specific controls fail — remains unchanged. The method for achieving it is held open pending evidence.

Any Tier 3 methodology proposal is a Charter amendment under ADR-0012 and requires Thomas approval before execution.

**Tier 3 is deferred.** It requires Tier 2 outputs as inputs and involves personally identifiable organizational data that introduces privacy and consent constraints outside the current project's scope. Architecture decisions that would affect Tier 3's feasibility should be flagged, but no Tier 3 implementation work begins until Tier 2 is operational.

---

## The Full Program Architecture

```
Tier 1 Projects (Framework Science)
┌──────────────┐  ┌───────────────────┐  ┌──────────────────┐  ┌──────────────┐
│  hc-grc      │  │ hc-grc-nist-800-53│  │ hc-grc-nist-800- │  │ hc-grc-cis-  │
│  (SCF)       │  │                   │  │ 82 (ICS/OT)      │  │ v8           │
│  [CURRENT]   │  │   [FUTURE]        │  │   [FUTURE]       │  │  [FUTURE]    │
└──────┬───────┘  └────────┬──────────┘  └────────┬─────────┘  └──────┬───────┘
       │                   │                      │                   │
       └───────────────────┴──────────────────────┴───────────────────┘
                                       │
                              ARA artifacts: knowledge graphs,
                              validated mapping scores, null results
                                       │
                                       ▼
                    ┌──────────────────────────────────┐
                    │  hc-grc-comparative               │
                    │  (Tier 2: Comparative Analysis)   │
                    │  Gaps · Alignment · Blast Radius  │
                    │  Control Importance · Archetypes  │
                    │              [FUTURE]             │
                    └──────────────────┬───────────────┘
                                       │
                              Cross-framework findings:
                              importance rankings, gap maps,
                              blast radius models
                                       │
                                       ▼
                    ┌──────────────────────────────────┐
                    │  hc-grc-impact                   │
                    │  (Tier 3: Organizational Impact) │
                    │  Causal risk model · SHAP        │
                    │  Financial loss attribution      │
                    │  Monte Carlo quantification      │
                    │          [DEFERRED]              │
                    └──────────────────────────────────┘
```

---

## Design Implications for the Current Project

Every Tier 1 design decision must be made as if Tier 2 will consume its outputs. Specifically:

**ARA artifact schema must be framework-agnostic.** The knowledge graph structure in `ara/artifacts/` must work for NIST 800-53 the same way it works for SCF. No SCF-specific assumptions may be baked into the ARA schema. The `STRMMapping` Pydantic model is the universal edge type — it works for any source→target framework pair.

**Graph data models must compose.** Tier 2 will ingest multiple framework graphs and run cross-graph algorithms. The `Control` and `Framework` Pydantic models must support multi-framework instantiation without schema modification.

**Null results are first-class outputs.** A STRM mapping that fails empirical testing is not a failure of the project — it is a finding. Null results from P1 (mappings that don't hold up) are Tier 2 inputs: they define the misalignment map. Every null result must be structured identically to a positive finding so Tier 2 can consume them.

**Blast radius groundwork starts in P2.** The control topology graph built in P2 (Control Space Topology) is the precursor to Tier 2's cross-framework blast radius model. P2's graph algorithms and visualization outputs should be designed with eventual multi-graph composition in mind.

---

## Consequences

**Positive:**
- Every design decision in the current project is now made against the full program requirements
- The ARA artifact interface is defined once and serves all three tiers
- Framework-specific projects share a common methodology, reducing duplication
- The organizational impact goal gives clear commercial direction even though Tier 3 is deferred

**Negative:**
- Adds design constraints to the current project (ARA schema must be framework-agnostic, graph models must compose)
- The full program spans multiple years and projects — long-term commitment required

**Accepted tradeoff:** The additional design constraints on the current project are small. The ARA schema and graph models are more carefully designed as a result. The long-term payoff — a multi-tier research program producing the first empirically grounded organizational GRC risk model — justifies the constraint.
