# T-01: Regulatory/Legal NLP Benchmark Search

**Date:** 2026-06-11  
**Author:** Thomas Jones (T-01 task)  
**Status:** Complete — findings incorporated into `configs/platform.yaml`  
**Scope:** Identify domain-specific NLP benchmarks for Phase 1 embedding model evaluation (SAP §10, LEDGER-0002)

---

## Summary Finding

**No GRC-specific benchmark exists.** No publicly available benchmark dataset provides pairwise semantic similarity labels over cybersecurity control language, compliance framework text, or security control descriptions of the kind found in SCF. This absence is itself a methodological contribution of this study — the HC-GRC platform will produce the first empirical ground truth about SCF control semantic structure.

Two domain-proxy benchmarks are available that are suitable for Phase 1 coarse model filtering, with meaningful domain gaps that must be disclosed. They are added to `configs/platform.yaml` as secondary validators, not domain-matched ground truth.

---

## Candidates Evaluated

### 1. General-Purpose STS (already in platform.yaml)

**STS-B** (Semantic Textual Similarity Benchmark) and **SICK-R** — widely used baselines, available via `sbert.net`. Used in Phase 1 to establish a performance floor. Documented in SAP §12 with domain shift caveat: strong general STS performance does not predict domain performance on regulatory text.

These remain the primary coarse filters as specified in `platform.yaml`.

---

### 2. LexGLUE / EURLEX ✓ Accepted (domain-proxy, weak signal)

**Source:** Chalkidis et al. 2021, `coastalcph/lex_glue` on HuggingFace  
**License:** CC-BY 4.0  
**Download:** `pip install datasets; load_dataset("coastalcph/lex_glue", "eur_lex")`  
**Size:** ~65K EU legislative documents, multi-label classification over 100 EuroVoc concept categories

**Task adaptation for embedding evaluation:**  
Documents sharing one or more EuroVoc labels are semantically related by legislative topic. Same-label pairs should have higher cosine similarity than random pairs. Evaluation: construct same-label vs. random-label pairs, measure AUC. This is a retrieval-style probe on the embedding space, not a direct similarity label.

**Domain relevance:**  
EU legislative text shares regulatory register with SCF controls — prescriptive language, cross-reference structure, obligation framing. Domain gap is significant: full EU laws (thousands of words) vs. SCF control descriptions (1–5 sentences). The embedding signal from document-level EURLEX classification will be weaker than sentence-level similarity, but the legal register provides better signal than general-corpus benchmarks.

**Verdict:** Accepted as Phase 1 secondary benchmark — legal domain proxy, classification adaptation, weak but directionally meaningful signal.

---

### 3. ObliQA / RIRAG ✓ Accepted (domain-proxy, better signal)

**Source:** RegNLP 2025 workshop, Gokhan et al. 2024; `github.com/RegNLP/ObliQADataset`  
**License:** CC-BY 4.0 (verify at download time)  
**Paper:** arxiv.org/abs/2409.05677  
**Size:** 27,869 questions derived from ~640K words of ADGM (Abu Dhabi Global Markets) financial regulation documents across 40 regulatory texts

**Task adaptation for embedding evaluation:**  
ObliQA provides query-passage relevance pairs — each question is mapped to one or more regulatory passages that answer it. This maps directly to embedding retrieval evaluation: encode questions and passages, compute MRR@10 and NDCG@10 to measure whether the top-retrieved passage is the relevant one. No task adaptation required beyond formatting.

**Domain relevance:**  
Financial regulation language (ADGM) is closer in structure and register to cybersecurity control language than general corpora. Both are regulatory obligation texts: prescriptive, short-to-medium length, cross-referenced, jurisdiction-specific. The domain gap to SCF is real (financial ≠ cybersecurity), but the linguistic register gap is smaller than any other available option.

**Verdict:** Accepted as Phase 1 secondary benchmark — regulatory language proxy, retrieval task format (cleanest mapping to our use case), medium domain gap.

---

### 4. LegalBench — Rejected for embedding evaluation

**Source:** Neel et al. 2023, NeurIPS, `nguha/legalbench` on HuggingFace  
**Tasks:** 162 tasks across statutes, judicial opinions, contracts (binary classification, entailment, extraction, generation)

**Rejection rationale:** LegalBench is designed to evaluate LLM legal reasoning, not embedding model similarity performance. Tasks require generation and multi-step reasoning. No pairwise similarity labels exist. Adapting it to embedding evaluation would require constructing proxies across 162 heterogeneous tasks with inconsistent label semantics. Overhead too high for the signal value.

---

### 5. LexGLUE CONTRACT-NLI — Rejected (domain gap too large)

**Source:** Koreeda & Manning 2021, within LexGLUE  
**Task:** Contract clause natural language inference (entailment between contract hypothesis and premise)

**Rejection rationale:** Entailment pairs (entailment/contradiction/neutral) can be adapted as similarity labels, but M&A contract language is linguistically distant from cybersecurity control descriptions. Legal inference structure differs from control semantic relationship structure. Domain gap exceeds that of ObliQA. Rejected in favor of ObliQA.

---

### 6. Cybersecurity-specific benchmarks (SECURE, CyberBench, CyberMetric) — Rejected

**Rejection rationale:** These benchmark LLM knowledge of cybersecurity concepts, not semantic similarity between control descriptions. No pairwise similarity structure. Evaluation tasks are QA and knowledge extraction, not retrieval or pair scoring. Not applicable.

---

### 7. Public framework crosswalks (CIS→NIST CSF OLIR, CIS Controls mapping) — Rejected for Phase 1

**Source:** CIS published NIST OLIR-compliant mappings of CIS Controls to NIST CSF  
**Assessment:** These provide structural mappings (which CIS control maps to which CSF subcategory) but not similarity scores. The mapping relationship is architectural (one-to-many category assignment), not a similarity label. Constructing silver-standard pairs from crosswalks would require significant interpretation of the mapping semantics — introducing researcher degrees of freedom before preregistration is locked. Deferred to post-Gate-2 if needed.

---

## Decision

| Benchmark | Status | Phase 1 Use | Domain | Task Format |
|-----------|--------|-------------|--------|-------------|
| STS-B | ✅ Already present | General coarse filter | General | Pairwise similarity scores |
| SICK-R | ✅ Already present | General coarse filter | General | Pairwise similarity scores |
| LexGLUE EURLEX | ✅ Added | Legal domain proxy | EU legislation | Multi-label → retrieval probe |
| ObliQA | ✅ Added | Regulatory domain proxy | Financial regulation | Retrieval MRR@10 / NDCG@10 |
| LegalBench | ❌ Rejected | — | Legal reasoning | LLM generation |
| CONTRACT-NLI | ❌ Rejected | — | M&A contracts | Entailment |
| Cybersecurity QA benchmarks | ❌ Rejected | — | CySec knowledge | QA |

---

## Disclosure Requirements

The following must appear in SAP §12 and in the methods section of all publications:

1. No GRC-specific semantic similarity benchmark exists at the time of this study. This is a limitation of the evaluation design and a contribution opportunity for the field.
2. EURLEX and ObliQA are domain-proxy benchmarks with meaningful gaps to SCF control language. Evaluation results on these benchmarks are directional, not predictive of SCF-domain performance.
3. Primary model selection at Gate 2 is based on performance on the calibration sample drawn from SCF-adjacent control language (SAP §10), not on these proxy benchmarks. The proxy benchmarks serve as Phase 1 coarse filters only.

---

## Files Updated

- `configs/platform.yaml` — `regulatory_benchmarks` section populated
- This document — `docs/research/T01-regulatory-benchmarks.md`
