# ADR-0013: Research Design Reframe — STRM Demoted from Ground Truth to Secondary Comparison

**Status:** Accepted  
**Date:** 2026-06-10  
**Author:** Thomas Jones  
**Supersedes:** Portions of ADR-0010 describing STRM as the validation criterion for P1  
**Relates to:** ADR-0010 (three-tier program), ADR-0012 (autonomous iterative architecture), issues #57, #70, #63, #58, #66, #67

---

## Context

The original P1 design used STRM labels as ground truth: train classifiers on STRM labels, validate NLP similarity against STRM scores, interpret high correlation as evidence that STRM labels are valid.

Adversarial review identified two structural problems:

**Construct contamination (#57):** SCF control texts were written by the same experts who assigned the STRM labels. High NLP-STRM correlation cannot distinguish expert validity from expert consistency from circular self-reference (texts authored to encode the intended mapping). No mechanism existed to separate these three explanations.

**Ground truth circularity (#70):** Training classifiers to predict STRM labels and calling high accuracy "validation" measures internal consistency, not semantic validity. Experts could have assigned all labels consistently but incorrectly and the classifier would still achieve high accuracy.

---

## Decision

**Primary validation criterion:** NLP similarity models are evaluated against each other using mathematical criteria — not STRM agreement.

**STRM:** Demoted to secondary comparison. Divergence between model consensus and STRM labels is an explicit research finding, not a failure condition.

**Thomas's hypothesis (to be tested):** Expert-driven STRM assessments may deviate substantially from computational NLP similarity models. That deviation characterizes where human expert judgment and computational similarity diverge — which is itself a GRC-relevant finding.

---

## Operational Design

### Primary Analysis — Model-Driven Evaluation

Candidate embedding models are evaluated on mathematical criteria independent of STRM:

**Phase 1 (no SCF data):** Models evaluated on published STS benchmarks (STS-B, SICK-R) and SCF structural metadata anchor pairs (see below). T-01 searches for regulatory/legal domain benchmarks during Phase 0; if found, added to Phase 1. If not found, absence is documented and Phase 2 results weighted more heavily. Produces ranked shortlist of 3–5 models.

**Candidate model set diversity requirement:** The candidate set must include at minimum two diversity anchors beyond the general-purpose model cluster: (1) a model domain fine-tuned on legal/regulatory text; (2) a model from a different architecture class (sparse retrieval or substantially different training corpus). T-01 identifies specific models during Phase 0. Diversity anchor selection is logged to the Preregistration Ledger before Phase 1 runs. Phase 1 does not run without both anchors present.

**SCF structural metadata anchor pairs (no human labeling required):** Similarity anchors = control pairs with STRM relationship '= Equal To'. Dissimilarity anchors = control pairs across unrelated domains with STRM relationship '∅ No Relation'. Used in both Phase 1 and Phase 2 consistency validation.

**Phase 2 (pre-Gate 2 calibration sample):** Shortlisted models evaluated on a held-out calibration sample using:
- **Silhouette score** — internal cluster validity of the embedding space
- **Anchor consistency score** — proportion of STRM '= Equal To' anchor pairs ranked above '∅ No Relation' anchor pairs in pairwise similarity. Validates that cluster geometry is consistent with the SCF's own semantic relationship assertions. Limitation: anchor quality is bounded by STRM reliability (disclosed in SAP Section 12).
- **Cross-model agreement** — pairwise Spearman between models' similarity rankings across the full candidate set including diversity anchors. Agreement across architecturally diverse models is stronger evidence than agreement within a single training lineage.

Primary model is the model with highest cross-model agreement and cluster validity. This designation is logged to the Preregistration Ledger with a cryptographic timestamp before the Gate 2 confirmatory split executes.

### Secondary Analysis — STRM Comparison

After primary model selection:
- Model-derived similarity structure is compared against STRM labels
- Divergences are quantified and characterized
- STRM inter-rater reliability is estimated (Fleiss' kappa on a re-rated sample) and used to contextualize divergence findings: unreliable STRM would explain divergence; reliable STRM that still diverges from models is a stronger finding about SCF annotation quality

### What Both Outcomes Mean

| Result | Interpretation |
|--------|---------------|
| Models agree with STRM | Computational similarity finds the same semantic structure the experts intended to encode |
| Models agree with each other, diverge from STRM | STRM labeling scheme is inconsistent with computational semantic similarity — directly useful to GRC practitioners evaluating SCF reliability |
| Models disagree with each other | No consensus semantic structure; embedding choice matters; P1 primary finding is methodological |
| STRM has low inter-rater reliability | Divergence from models is partially explained by STRM noise; characterizes SCF annotation quality |

All four outcomes are informative. None is a failure condition.

---

## Contribution Framing

**Original (retired):** "First empirical validation of STRM mappings."

**Revised:** "First empirical characterization of SCF semantic structure using NLP similarity methods, with comparison to expert-assigned STRM labels — including quantification of where computational similarity and expert judgment diverge."

This is a more honest claim and a more interesting one. It answers a question GRC practitioners actually need answered: can they trust the SCF's expert-assigned mapping scores, and where do those scores diverge from what the text actually says?

---

## Consequences

**What this enables:**
- Construct contamination and ground truth circularity are eliminated by design
- Both high and low model-STRM agreement produce meaningful findings
- STRM reliability is characterized as a research output rather than required as a prerequisite
- Model selection is principled and STRM-independent

**What this requires:**
- Phase 1 and Phase 2 model evaluation protocol executes before Gate 2
- Primary model designation logged to Preregistration Ledger before confirmatory split
- All other models designated as secondary/sensitivity analyses at the same time
- STRM inter-rater reliability estimated as part of secondary analysis

**What this closes:**
- #57: Construct contamination — eliminated
- #70: Ground truth circularity — eliminated
- #63: STRM reliability as validity threat — resolved (now a finding)
- #58: Trivially weak null models — replaced with permutation baseline and cross-model agreement
- #66: Multiple comparisons / outcome-dependent model selection — resolved by Phase 1/2 protocol
- #67: Unit of analysis — resolved (SCF control, ~1,400 units, consistent with #60 GroupKFold)

---

## Alternatives Considered

**Keep STRM as ground truth, obtain independent annotation sample:** Would break the circularity but requires recruiting domain experts, significant coordination overhead, and delays the research. The reframe achieves stronger methodological defensibility without this dependency.

**Frame P1 as consistency study only, drop STRM comparison entirely:** Loses the most interesting finding — the divergence between computational and expert judgment. The comparison is the value.
