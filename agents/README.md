# Agents

> The full agent system architecture — the four tiers, the orchestration topology, the per-stage
> execution pattern, and model assignments — is in [`../docs/AGENT_SYSTEM.md`](../docs/AGENT_SYSTEM.md).
> This file is the quick producer→adversary pairing reference.

This program is executed by agents from the `awesome-claude-code-subagents` framework (pinned at
`upstream/awesome-claude-code-subagents/`). The **adversary** agents that certify every artifact are
ours and live natively in `adversarial-review/` here. At runtime, Claude Code auto-loads the working
set from `.claude/agents/` (producers copied from the submodule + the 8 adversaries; see
`scripts/sync-agents.sh`). Each producing discipline is paired to its adversary on a different model
family.

## Producer → adversary pairings

| Producer (default model: sonnet) | Adversary (default model: opus) | Certifies |
|---|---|---|
| `data-engineer` | `data-engineer-adversary` | ingestion, per-control assets, crosswalk, lineage (S4, X1) |
| `nlp-engineer` | `nlp-engineer-adversary` | enriched text, tokenization, probes (S5) |
| `ml-engineer` | `ml-engineer-adversary` | embeddings, CKA, classifiers, reproducibility (S5, S6, S7, S9) |
| `llm-architect` | `llm-architect-adversary` | embedding-selection criterion (S5, T3) |
| `data-scientist` | `data-scientist-adversary` | stats, dimensionality, clustering, gaps (P1, S3, S6, S7, X2) |
| `knowledge-synthesizer` | `knowledge-synthesizer-adversary` | within- and cross-framework triangulation, stance (S8f, X2–X4) |
| `technical-writer` | `technical-writer-adversary` | leadership translation (X5) |
| `documentation-engineer` | `documentation-engineer-adversary` | reproducibility package (X5) |

## Three layers (summary)

1. **Same discipline** — competence to catch discipline-specific defects.
2. **Different mental model** — a rotating review stance (independent reconstruction, falsification
   probe, competing hypotheses, assumption ledger, premortem), different from the producer's.
3. **Tier-level diversity** — adversary runs on `opus` (higher tier) while producer runs on
   `sonnet`, providing weight-level diversity within the Anthropic family.

**Cross-discipline backstop** (per stage): `competitive-analyst` + `product-manager` audit each
stage's accepted set for defects the whole discipline shares.

See `adversarial-review/README.md` for the full protocol and `adversarial-review/_TEMPLATE.md` for
adding an adversary discipline.
