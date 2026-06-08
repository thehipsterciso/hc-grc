# Adversarial Review

Same-discipline adversary agents that certify another agent's artifact before it is accepted
into shared state. Built for autonomous, multi-agent research and engineering programs where no
human reviews every artifact, but every artifact must still earn its place.

## The problem these solve

A reviewer of a **different** discipline is independent but incompetent for the task — a product
manager cannot tell you a variance assumption was violated. A reviewer of the **same** discipline
is competent but shares the producer's blind spot — two statisticians trained the same way frame
the same flawed null the same way. Neither alone is enough.

## The three stacked layers

Each agent here is the **same discipline** as the producer it reviews, and recovers independence
two other ways:

1. **Layer 1 — Competence (same discipline).** A discipline-specific completeness + quality
   checklist that only a peer would know to run.
2. **Layer 2 — Epistemic independence (different mental model).** The adversary applies a
   *rotating review stance* (independent reconstruction, falsification probe, competing
   hypotheses, assumption ledger, premortem) chosen to differ from the producer's — so the
   artifact is never attacked from the same angle twice.
3. **Layer 3 — Weight-level independence (different model family).** The adversary runs on a
   different underlying model than the producer (set via the `model` field), because two
   instances of the same base model share priors that no prompt removes.

A coarser **cross-discipline** audit (e.g. `competitive-analyst` + `product-manager`) is run
separately, per stage, as a backstop against a defect the whole discipline shares.

## Agents

| Adversary | Certifies artifacts from | Catches |
|-----------|--------------------------|---------|
| [data-scientist-adversary](data-scientist-adversary.md) | data-scientist | bare estimates, missing nulls/CIs, post-hoc thresholds, unmet assumptions |
| [data-engineer-adversary](data-engineer-adversary.md) | data-engineer | row-count drift, lineage gaps, silent nulls, non-reproducible builds |
| [nlp-engineer-adversary](nlp-engineer-adversary.md) | nlp-engineer | truncation, tokenizer mismatch, undocumented text construction, leaky probes |
| [ml-engineer-adversary](ml-engineer-adversary.md) | ml-engineer | non-reproducible embeddings, batch artifacts, CV leakage, missing baselines |
| [llm-architect-adversary](llm-architect-adversary.md) | llm-architect | non-pre-registered or non-orthogonal selection criteria, single-model claims |
| [knowledge-synthesizer-adversary](knowledge-synthesizer-adversary.md) | knowledge-synthesizer | uncited claims, unearned "robust" labels, overstated independence |
| [technical-writer-adversary](technical-writer-adversary.md) | technical-writer | claims that don't trace to evidence, untranslated jargon, overclaim/fear-selling |
| [documentation-engineer-adversary](documentation-engineer-adversary.md) | documentation-engineer | non-reproducible packages, stale docs, unpinned environments |

## Usage

1. The producing agent finishes an artifact and writes a **Definition of Done**.
2. Spawn the matching adversary **on a different model family** than the producer.
3. The adversary picks a stance different from the producer's, runs Layer 1 + the two-axis gate,
   and returns a REJECT (with specific defects) or an ACCEPT certificate.
4. Only a passing certificate lets the artifact be registered.

To add an adversary for another discipline, copy `_TEMPLATE.md`, fill the Layer-1 checklist with
that discipline's failure modes, and set a `model` that differs from the producer's default.

## Quick Selection Guide

| If you need to certify... | Use this adversary |
|---------------------------|--------------------|
| A statistical test, clustering, dimensionality, or classifier result | **data-scientist-adversary** |
| An ingestion pipeline, parquet build, or provenance lineage | **data-engineer-adversary** |
| Enriched-text construction, tokenization, or a probe set | **nlp-engineer-adversary** |
| An embedding, CKA, classifier, or reproducibility claim | **ml-engineer-adversary** |
| A model/embedding selection criterion (pre-registration, orthogonality) | **llm-architect-adversary** |
| A cross-study synthesis or robust/provisional labelling | **knowledge-synthesizer-adversary** |
| An executive/business translation of a finding | **technical-writer-adversary** |
| A reproducibility package, README, or run instructions | **documentation-engineer-adversary** |
| An artifact from a discipline not listed | Copy **_TEMPLATE.md**, fill the Layer-1 checklist |

## Common Review Patterns

**Per-artifact gate (the default):** the producing agent finishes an artifact and writes a
Definition of Done → spawn the matching adversary above on a different model family → it picks a
stance different from the producer's, runs Layer 1 + the two-axis gate, and returns a certificate
or a defect list. Only a passing certificate lets the artifact be registered.

**Deadlock:** if producer and adversary cannot converge after N rounds, spawn a third instance of
the same adversary (a third model, fresh context) as an arbiter.

**Stage backstop (cross-discipline):** at each stage boundary, pair these same-discipline
adversaries with a cross-discipline audit (e.g. **competitive-analyst** + **product-manager**) to
catch defects the whole discipline shares — the one thing a same-discipline critic cannot.

**Irreversible decisions:** adversaries escalate frozen pre-registrations, licensing calls,
selection-criterion freezes, and publication to a human tripwire. Agents do not settle irreversible
calls by majority.
