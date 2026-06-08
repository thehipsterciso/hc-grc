# hc-grc — Agent System Architecture

The program is executed entirely by agents; no human runs a stage. This document is the *structure*
of that system: who exists, how they are organized into tiers, how a single unit of work flows from
production to certified registration, what model each runs on, and where each agent physically
lives. It is the missing map between `docs/PROGRAM_ROADMAP.md` (what happens) and `agents/README.md`
(the producer→adversary pairings).

---

## The system at a glance

```
                         ┌───────────────────────────────────────────────┐
                         │  ORCHESTRATION & INFRASTRUCTURE  (Tier 0)      │
                         │  multi-agent-coordinator  ── runs the graph    │
                         │  agent-organizer · mlops-engineer ·            │
                         │  git-workflow-manager                          │
                         └───────────────┬───────────────────────────────┘
                                         │ spawns per-stage teams, enforces gates
            ┌────────────────────────────┼────────────────────────────┐
            ▼                            ▼                             ▼
 ┌──────────────────┐        ┌───────────────────────┐      ┌────────────────────┐
 │  SHARED STATE     │        │  PRODUCING DISCIPLINES │      │  SAME-DISCIPLINE    │
 │  (Tier 0)         │        │  (Tier 1)              │      │  ADVERSARIES (Tier 2)│
 │  context-manager  │◄──────►│  data-engineer         │◄────►│  data-engineer-adv   │
 │  — certified-only │ register│  nlp-engineer          │ gate │  nlp-engineer-adv    │
 │    registry       │  only   │  ml-engineer           │ each │  ml-engineer-adv     │
 │  error-coordinator│ certified│ llm-architect          │artifact│ llm-architect-adv  │
 │  — defect/cert    │        │  data-scientist        │      │  data-scientist-adv  │
 │    ledger         │        │  knowledge-synthesizer │      │  knowledge-synth-adv │
 │                   │        │  technical-writer      │      │  technical-writer-adv│
 │                   │        │  documentation-engineer│      │  documentation-eng-adv│
 └───────────────────┘        └───────────┬───────────┘      └────────────────────┘
                                          │ at each stage boundary
                                          ▼
                            ┌───────────────────────────────┐
                            │ CROSS-DISCIPLINE BACKSTOP (Tier 3)│
                            │ competitive-analyst + product-manager │
                            │ audit the stage's accepted set    │
                            └───────────────────────────────┘
```

Four tiers. Tier 0 coordinates and holds state. Tier 1 produces. Tier 2 certifies each artifact,
same discipline as its producer. Tier 3 audits each *stage* across disciplines, as a backstop for
the one blind spot Tier 2 cannot see.

---

## Tier 0 — Orchestration & infrastructure

Stood up once at stage P0; persists for the whole program.

| Agent | Role | Model |
|-------|------|-------|
| `multi-agent-coordinator` | Runs the stage graph end to end. Spawns each stage's producers and their adversaries; advances only on passing certificates; never judges work on its merits. | opus |
| `agent-organizer` | Designs the roster and the producer→adversary→model pairings. Run once up front; re-run only if scope changes. | opus |
| `context-manager` | Owns the registry. Registers an artifact **only** with an attached passing certificate; records producer, adversary, stance, certificate, source version, git commit. | sonnet |
| `error-coordinator` | The defect/certificate ledger — every rejection, stance used, revision diff, and certificate. This ledger *is* the provenance record. | sonnet |
| `mlops-engineer` | Reproducible, seed-pinned, containerized compute, so an adversary can actually re-run a producer's work to check it. | sonnet |
| `git-workflow-manager` | Branch per stage; merge gated on a complete certificate set, not human review. | sonnet |

---

## Tier 1 — Producing disciplines

The agents that do the science and the writing. Each is shadowed by its Tier-2 adversary. Defaults
to `sonnet` (a producer's adversary runs `opus`, giving Layer-3 weight independence).

| Producer | Produces | Paired adversary |
|----------|----------|------------------|
| `data-engineer` | ingestion, per-control assets, the SCF crosswalk, lineage | `data-engineer-adversary` |
| `nlp-engineer` | enriched text, tokenization, probe sets | `nlp-engineer-adversary` |
| `ml-engineer` | embeddings, CKA, classifiers, reproducibility | `ml-engineer-adversary` |
| `llm-architect` | embedding-selection criterion | `llm-architect-adversary` |
| `data-scientist` | statistics, dimensionality, clustering, gaps | `data-scientist-adversary` |
| `knowledge-synthesizer` | within- and cross-framework triangulation, stance | `knowledge-synthesizer-adversary` |
| `technical-writer` | leadership translation | `technical-writer-adversary` |
| `documentation-engineer` | reproducibility package, run instructions | `documentation-engineer-adversary` |

**Support disciplines** (contribute to a stage but are not the lead; certified through the lead's
adversary): `research-analyst`, `first-principles-thinking`, `scientific-literature-researcher`,
`data-researcher`, `data-analyst`, `legal-advisor`, `license-engineer`, `compliance-auditor`,
`content-marketer`, `business-analyst`, `content-quality-editor`, `ai-writing-auditor`.

---

## Tier 2 — Same-discipline adversaries

The eight agents in `agents/adversarial-review/` (loaded at runtime from `.claude/agents/`). Each
holds the producer's discipline (Layer 1 competence), draws a rotating review stance different from
the producer's (Layer 2 epistemic independence), and runs `opus` against the producer's `sonnet`
(Layer 3 weight independence). They are read-only on the artifact and hold reject authority. Full
protocol and reject checklists live in each agent body; the pairing summary is in `agents/README.md`.

## Tier 3 — Cross-discipline backstop

`competitive-analyst` (novelty/defensibility vs the literature) and `product-manager` (overclaim,
decision-meaning) audit each stage's *accepted set*. They cannot edit — only raise a blocking issue
that re-opens an artifact's loop. This is the structural answer to the one defect a same-discipline
adversary cannot catch: one the whole discipline shares.

---

## The atomic operation — how one artifact gets accepted

Everything the system does reduces to this loop. It is the acceptance protocol the Tier-2 adversaries
run (see the agent bodies in `agents/adversarial-review/` for the full version).

```
 producer (model A) ──► artifact + Definition of Done
        │
        ▼
 same-discipline adversary (model B, stance ≠ producer's)
        │  precondition check → discipline checklist → stance protocol → two-axis gate
        ├─ REJECT (specific defects) ─► producer revises ─► re-audit (same stance)
        └─ ACCEPT (signed certificate) ─► context-manager registers the artifact
        │
   deadlock after N rounds (default 3) ─► ARBITER (3rd instance, model C, fresh context)
                                          ─► still unresolved ─► human tripwire
```

A certificate carries: artifact id, producer+model, adversary+model, stance used, rounds,
completeness/quality verdicts, residual limitations. No certificate → no registration → no
downstream agent can consume the work.

## How a stage executes

1. `multi-agent-coordinator` confirms the stage's dependencies are certified, then spawns its
   producer team.
2. Producers emit artifacts, each with a Definition of Done.
3. The coordinator spawns the paired Tier-2 adversary for each artifact — different model, stance
   rotated so the same artifact is never hit from the same angle twice — and runs the atomic loop.
4. `context-manager` registers only certified artifacts; `error-coordinator` logs everything.
5. The Tier-3 backstop audits the stage's accepted set; any blocking issue re-opens an artifact.
6. The stage advances. A human is involved only at the five tripwires (T1–T5 in `CLAUDE.md`).

---

## Model assignment (Layer 3 in practice)

| Seat | Default model | Why |
|------|---------------|-----|
| Producers (Tier 1) | `sonnet` | throughput |
| Adversaries (Tier 2) | `opus` | higher tier within Anthropic family; different weights; strongest critic |
| Arbiter (deadlock) | a different Anthropic tier / fresh context | breaks ties without inheriting either side's priors |
| Coordinator / organizer | `opus` | planning and gate discipline |

Set per spawn via the Agent tool's model override. If an adversary is ever forced onto the same
model as its producer, it must declare that on the certificate as a known limitation.

---

## Model independence: honest accounting

**All agents run on Anthropic models.** The tier-level independence (sonnet → opus) provides
weight-level diversity, not family-level independence. This is a known program limitation.

- **(a) Single-family architecture.** Producer agents run `sonnet`; adversary agents run `opus`.
  Both are Anthropic models. A shared blind spot in the Anthropic model family (an error or bias
  common to both tiers' training) would pass through Tier 2's adversarial check.

- **(b) What tier diversity does provide.** Different weights, different scaling properties, and
  different generalization profiles between tiers. An error specific to one tier can be caught by
  the other. But errors in the underlying architecture, training data, or values shared across the
  family are not caught by tier-level review alone.

- **(c) Where strongest independence is earned.** **S9 adversarial replication** is where the
  program's most robust independence is built. S9 runs a second, independently-spawned analysis
  team blind to the first team's results. This team selects independently from the S3-certified
  method menu, makes independent choices about analysis direction and hypothesis focus, and works
  on the same corpus and pre-registration. Replication of a finding by a team with different
  analysts, different method choices, and different reasoning paths is not vulnerable to a shared
  model family blind spot — it is evidence of genuine structural signal.

- **(d) Limitation recorded in every certificate.** Every Tier-2 certificate for a finding that
  will feed cross-framework synthesis carries a note: "Model independence: tier-level diversity
  only (Anthropic sonnet ↔ opus); cross-framework replication (S9) is the structural robustness
  check."

This is not a flaw in the system — it is a design choice. Tier-level diversity catches adversarial
oversights; S9 replication and cross-framework evidence catch systemic ones. The limitation is
explicit in every artifact's provenance.

---

## Where the agents physically live

- **Pinned framework source:** `upstream/awesome-claude-code-subagents/` — a git submodule of the
  `voltagent-subagents` marketplace (categories 01–10), the version-controlled source of every
  producer, orchestration, and backstop agent.
- **Native adversaries (8):** `agents/adversarial-review/` — authored for this program; the
  human-readable home, with their own README and `_TEMPLATE.md` for adding disciplines.
- **Runtime set (generated):** `.claude/agents/` — what Claude Code auto-loads: ~28 producer agents
  copied from the submodule plus the 8 adversaries, regenerated by `scripts/sync-agents.sh`.
- **Binding:** `agents/README.md` holds the producer→adversary pairings; this document holds the
  structure. As an alternative to the copied producers, install the `voltagent-subagents`
  marketplace (see `.claude/agents/README.md`).

---

## Which agents run where (program map)

| Stage | Lead producers | Adversaries | Tier-0 / backstop |
|-------|----------------|-------------|-------------------|
| P0 setup | — | — | all Tier 0 |
| P1 pre-registration | research-analyst, first-principles-thinking, data-scientist | data-scientist-adv | coordinator; T1 |
| S3 method validation | data-scientist, ml-engineer | data-scientist-adv | coordinator |
| S4 corpus + crosswalk | data-engineer (+legal/license) | data-engineer-adv | T2 backstop; T2 tripwire |
| S5 embedding | nlp-engineer, ml-engineer, llm-architect | nlp/ml/llm-architect-adv | T3 tripwire |
| S6 instrument validity | data-scientist, ml-engineer | data-scientist-adv, ml-engineer-adv | — |
| S7 investigations | data-scientist (+support) | data-scientist-adv | backstop per stage |
| S8f within-framework triangulation | knowledge-synthesizer, data-scientist | knowledge-synthesizer-adv | — |
| S9 replication | 2nd data-scientist/ml-engineer team (diff model) | their adversaries | coordinator |
| X1–X3 synthesis | data-engineer, data-scientist, knowledge-synthesizer | data-engineer-adv, knowledge-synthesizer-adv | backstop |
| X4 stance | knowledge-synthesizer, first-principles-thinking | knowledge-synthesizer-adv (premortem) | competitive-analyst + product-manager; T4 |
| X5 release | documentation-engineer, technical-writer, product-manager | documentation-eng-adv, technical-writer-adv | T5 |

---

## Roster counts

6 orchestration/infrastructure · 8 core producers (+ ~12 support) · 8 same-discipline adversaries ·
2 cross-discipline backstop. The producing, orchestration, and backstop agents are stock framework
agents; the eight adversaries are the ones authored for this program.
