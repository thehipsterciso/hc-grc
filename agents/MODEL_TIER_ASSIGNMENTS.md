# Model Tier Assignments

**Version:** 0.1.0
**Status:** Draft — authored 2026-06-12 (KICKOFF_READINESS.md, P1 backlog item 8)
**Authority:** ADR-0016 (LLM Execution Routing)

Routing is **by stakes**, per ADR-0016. This registry is the single source of truth for which execution tier each agent runs on, pending ratification of a per-card `model_tier:` frontmatter field (and a corresponding CARDS_SPEC.md schema bump).

## Tiers

| Tier | Backend | When |
|------|---------|------|
| **T1 — Deterministic ML** | Mac mini, 24/7. No LLM. | Computation: embeddings, graph algorithms, clustering, statistics, deterministic tooling |
| **T2 — Local LLM** | Mac mini, 24/7 (Ollama/llama.cpp) | Low-stakes / high-volume reasoning: bulk classification, triage, drafting, routine review |
| **T3 — Frontier (Max 20x via Agent SDK)** | Claude, bursty/queued | High-risk, high-complexity judgments where a wrong call corrupts the science or a public output |
| **Infra** | Mac mini | Model-ops / serving agents that operate the platform, not the research |

## Assignments

| Team | Agent | Tier | Protected | Rationale |
|------|-------|------|-----------|-----------|
| 00-orchestration | orchestrator | T2 | — | Routine routing is local; hard escalations may invoke T3 reasoning |
| 00-orchestration | agent-evolution | T2 | — | DSPy re-optimization; cannot autonomously modify protected agents |
| 01-research | ideation-agent | T2 | — | Low-stakes brainstorming |
| 01-research | literature-agent | T2 | — | Bulk triage/summarization local; final synthesis may escalate to T3 |
| 01-research | hypothesis-formalizer | **T3** | ✓ | Defines the pre-registered tests — errors propagate through all confirmatory analysis |
| 02-data | data-acquisition | T1 | — | Download, hash, ARA compile — deterministic |
| 02-data | data-curation | T1 | — | NeMo Curator dedup/normalize — deterministic |
| 02-data | data-steward | T1 | — | Great Expectations validation, stratified split — deterministic |
| 02-data | embedding-agent | T1 | — | Embedding computation — deterministic ML |
| 02-data | tokenization-agent | T1 | — | Tokenization — deterministic |
| 03-analysis | p1-strm-nlp | T2 | ✓ | High-volume per-pair STRM classification — local LLM at scale |
| 03-analysis | p2-control-topology | T1 | ✓ | Graph centrality + Leiden/Louvain — deterministic |
| 03-analysis | p3-regulatory-convergence | **T3** | ✓ | Genuine-vs-terminological convergence is a nuanced semantic judgment |
| 03-analysis | p4-risk-blindspot | T1 | ✓ | Coverage-density computation — deterministic |
| 03-analysis | p5-ai-governance | T1 | ✓ | HDBSCAN + UMAP clustering — deterministic |
| 04-statistical | statistical-analyst | T1 + **T3** | ✓ | Test computation deterministic (T1); result interpretation high-stakes (T3) |
| 05-inference | distributed-training | Infra | — | Deferred (Tier-1 single-node); model-ops |
| 05-inference | extended-serving | Infra | — | Conditional; serving infra |
| 05-inference | local-inference | Infra | — | Operates the T2 local-model serving stack |
| 06-training | fine-tuning-agent | Infra | — | Conditional; trains local embedding/models |
| 06-training | post-training-agent | Infra | — | Deferred (Tier-2 capability) |
| 07-optimization | emerging-techniques | Infra | — | Conditional; model-ops |
| 07-optimization | quantization-agent | Infra | — | Conditional; model-ops |
| 07-optimization | training-optimization | Infra | — | Conditional; model-ops |
| 08-interpretability | interpretability-agent | Infra | — | Deferred (Tier-2 mechanistic analysis) |
| 09-evaluation | evaluation-agent | T2 | — | Routine model/output evaluation local; high-stakes eval may escalate |
| 10-safety-compliance | code-review-agent | T2 | — | SAP-header and analysis-script review — bounded, local |
| 10-safety-compliance | guardrails-agent | T2 | — | Inline guardrail checks (small/local models) |
| 11-quality-provenance | provenance-agent | T1 | — | PROV-DM record generation — deterministic |
| 11-quality-provenance | qa-agent | **T3** | — | Adversarial rigor review; catches hallucinated/unsupported findings |
| 12-academic-dissemination | report-agent | **T3** | — | Interpretation of findings — a wrong reading propagates to every public output |
| 12-academic-dissemination | ml-paper-agent | **T3** | — | Public scientific claims |
| 12-academic-dissemination | whitepaper-agent | **T3** | — | Public practitioner claims |
| 12-academic-dissemination | conference-agent | T2 | — | Reformatting an already-approved paper for venues |
| 13-business-digital | brochure-agent | T2 | — | Marketing copy; public-facing final copy may escalate |
| 13-business-digital | business-presentation | T2 | — | Board/exec decks from approved findings |
| 13-business-digital | social-media-agent | T2 | — | Short-form promotion |
| 13-business-digital | substack-agent | T2 | — | The Hipster CISO drafts; high-stakes public voice may escalate |
| 14-visual-communications | branding-compliance | T2 | — | Brand-rule checks |
| 14-visual-communications | chart-agent | T1 | — | Chart rendering — deterministic |
| 14-visual-communications | visualization-agent | T1 | — | Visualization rendering — deterministic |
| 15-platform-devsecops | cicd-agent | Infra | — | CI/CD config — deterministic tooling |
| 15-platform-devsecops | dependency-management | T1 | — | Dependency scanning — deterministic |
| 15-platform-devsecops | devsecops-agent | T1 | — | Security-posture aggregation — deterministic |
| 15-platform-devsecops | github-management | Infra | — | GitHub API operations — deterministic |
| 15-platform-devsecops | repo-documentation | T2 | — | Doc drafting (executive/practitioner/technical) local |
| 15-platform-devsecops | sbom-agent | T1 | — | SBOM generation — deterministic |
| 15-platform-devsecops | vex-agent | T1 | — | VEX generation — deterministic |
| 16-legal-licensing | ip-attribution | T1 | — | Attribution checks — deterministic |
| 16-legal-licensing | license-compliance | T1 | — | License scanning — deterministic |

## Tally

- **T3 (frontier):** hypothesis-formalizer, p3-regulatory-convergence, statistical-analyst (interpretation), qa-agent, report-agent, ml-paper-agent, whitepaper-agent — 7 agents. Deliberately small to fit the fixed subscription envelope.
- **T2 (local LLM):** ~13 agents.
- **T1 (deterministic ML):** ~18 agents.
- **Infra:** ~9 agents (most deferred/conditional in Tier 1).

## Notes

- "Protected" (✓) is the ADR-0015 #77 Agent-Evolution constraint, independent of tier. Reconciled to canonical card names 2026-06-12 (was drifted in ADR-0015 §7 and GATES.md).
- Agents marked `T1 + T3` or "may escalate" run primarily on the cheaper tier and invoke frontier only for the named high-stakes sub-step. The `reasoning_client` abstraction (ADR-0016) makes the per-call choice.
