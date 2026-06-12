# HC-GRC

> **Not a technical reader?** Start with [OVERVIEW.md](OVERVIEW.md) — a plain language guide to what this project is, why it matters, and how it works.

**Autonomous scientific research platform for empirical analysis of cybersecurity control frameworks — starting with the Secure Controls Framework (SCF).**

The SCF is a metaframework of 1,400+ security controls mapped to 33 domains via ~280,000 expert-derived Set Theory Relationship Mappings (STRM). These mappings — which define how controls across frameworks relate to one another (subset, intersection, equivalence, superset, disjoint) — have never been empirically validated. This platform does that. And it doesn't stop there.

## The Research Program

This platform is the foundation of a three-tier research program. What we're building toward:

**Tier 1 — Framework Science (this project, plus future framework projects)**

Empirical knowledge graphs of each major GRC framework. The SCF's STRM mappings are testable hypotheses — not ground truth. We test them. Null results are first-class outputs. Each framework gets its own independent study (`hc-grc-nist-800-53`, `hc-grc-cis-v8`, `hc-grc-nist-800-82`...) to preserve pre-registration integrity across the program.

**Tier 2 — Comparative Analysis (future: `hc-grc-comparative`)**

Cross-framework synthesis. Which controls are genuinely load-bearing across multiple independent frameworks? Where do GRC frameworks actually converge, and where do they only appear to? What is the blast radius of a control failure — if control X goes down, what propagates through the cross-framework topology? What are the underlying archetypes the industry has reproduced under dozens of different names?

**Tier 3 — Organizational Impact Modeling (deferred: `hc-grc-impact`)**

The commercially significant tier. Model Tier 2 findings against real organizations. Causal inference — not correlation — to quantify which control failures drive financial losses and by how much. SHAP explainability for the board conversation. Monte Carlo quantification with confidence intervals. This is what actuaries do for insurance. Nobody has done it for cybersecurity controls grounded in empirically proven framework relationships.

## What This Project Studies

Five analytical modules, run in parallel:

| Module | Question |
|--------|----------|
| **P1 — STRM NLP Calibration** | Do the semantic relationships between control texts match the expert-assigned STRM relationship types? |
| **P2 — Control Space Topology** | What is the latent community structure of the 1,400+ control space? |
| **P3 — Regulatory Convergence Atlas** | Where do frameworks genuinely converge vs. appear to converge through shared terminology? |
| **P4 — Risk Blindspot Engine** | Which of the 39 SCF risk categories have systematic coverage gaps? |
| **P5 — AI Governance Clustering** | How do AI governance controls cluster relative to established security domains? |

## Architecture

The platform is agent-driven. Fifty specialized agents — organized into seventeen teams — execute the full research lifecycle from data acquisition through peer-reviewed publication. Human approval gates are enforced structurally at five points in the pipeline.

The architecture is designed for the full program: ARA artifact schemas are framework-agnostic so Tier 2 can ingest all Tier 1 outputs without schema changes. Null results are structured identically to positive findings. Confidence scores are first-class.

See [`agents/`](agents/) for the full agent library and [`docs/architecture/AGENT_WORKFLOW.md`](docs/architecture/AGENT_WORKFLOW.md) for the technical design.

## Research Design

This is a pre-registered, exploratory-first study. Exploratory analysis characterizes the data and informs hypothesis formation. Confirmatory analysis tests pre-registered hypotheses against a held-out test split that is inaccessible until Gate 2. The firewall between phases is structural, not procedural.

See [`docs/protocol/`](docs/protocol/) for the full research protocol and [`docs/protocol/PREREGISTRATION_LEDGER.md`](docs/protocol/PREREGISTRATION_LEDGER.md) for the timestamped pre-registration record.

## Navigating This Repository

```
agents/          Agent library — 50 AGENT.md specification cards across 17 teams
ara/             Agent-Native Research Artifact — structured data artifacts and deliverables
analysis/        Phase-separated analysis outputs (01-exploratory/ and 02-confirmatory/)
configs/         Experiment and pipeline configuration
data/            Data pipeline (01-raw/ → 02-interim/ → 03-processed/ → external/)
docs/            All documentation
  charter/       Project governance and framework constitutions
  architecture/  Technical platform design and infrastructure specs
  decisions/     Architectural Decision Records (ADRs)
  literature/    Literature review, search strategy, synthesis
  protocol/      Research protocol, pre-registration, SAP
experiments/     Experiment runs and empirical tracking
manuscript/      Academic paper manuscript
notebooks/       EDA and analysis notebooks
reports/         Outputs and deliverables (figures, papers, whitepapers, etc.)
reproducibility/ Replication package
scripts/         CI/CD automation and hooks
src/             Platform implementation (built by agents)
tests/           Test suite (built by agents)
```

## Key Documents

| Document | Purpose |
|----------|---------|
| [`docs/charter/PROJECT_CHARTER.md`](docs/charter/PROJECT_CHARTER.md) | Full scope, schema, technology stack |
| [`docs/architecture/AGENT_WORKFLOW.md`](docs/architecture/AGENT_WORKFLOW.md) | LangGraph topology, state schema, gate implementations |
| [`docs/architecture/SWARM_IMPLEMENTATION_ROADMAP.md`](docs/architecture/SWARM_IMPLEMENTATION_ROADMAP.md) | Implementation sequence, phases 0–6 plus Tier 2/3 |
| [`docs/decisions/`](docs/decisions/) | All ADRs (ADR-0001 through ADR-0016) |
| [`docs/protocol/PREREGISTRATION_LEDGER.md`](docs/protocol/PREREGISTRATION_LEDGER.md) | Timestamped pre-registration record |
| [`KICKOFF_READINESS.md`](KICKOFF_READINESS.md) | Definition of Ready, critical path, backlog (issues #109–#127) |
| [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) | Canonical directory map — read at run start |

## Status

Platform is in pre-execution phase. Agent library complete (50 cards). Research protocol locked at framework level. Statistical Analysis Plan deferred until post-exploratory (Gate 2). Data acquisition has not begun.

## License

Research outputs and documentation: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)  
Platform code: [MIT](LICENSE)

SCF data is used under CC BY-ND 4.0 (Center for Internet Security). Derived datasets may not be published.
