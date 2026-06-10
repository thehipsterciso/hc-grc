# Research Questions

**Lock status:** Platform-level questions LOCKED at framework pre-registration.
**Deferred:** Module-specific confirmatory hypotheses (H[module].[n] format) and effect size parameters. These are deferred until after exploratory characterization of the SCF/STRM corpus.

The distinction between exploratory and confirmatory is enforced structurally, not just procedurally. Exploratory analysis runs on train + validation splits and generates hypotheses. Confirmatory analysis runs on the held-out test split against pre-registered hypotheses only. These two phases share no data. Hypotheses derived from the data that will test them are not hypotheses — they are post-hoc fits.

---

## Platform Context

The Secure Controls Framework (SCF) contains 1,400+ security controls across 33 domains, linked by approximately 280,000 expert-derived Set Theory Relationship Mappings (STRM). Each STRM mapping asserts a logical relationship between controls across frameworks (⊂ ∩ = ⊃ ∅) and assigns a strength score (1–10). These mappings were created by domain experts through judgment-based processes.

**The central empirical gap:** STRM mappings have never been subjected to systematic empirical analysis. Their semantic validity, structural properties, and coverage characteristics are asserted, not measured. This platform is the first large-scale empirical investigation of that gap.

---

## Exploratory Research Questions

Exploratory RQs guide characterization of the corpus before hypotheses are formed. Results from exploratory analysis are descriptive — they generate hypotheses, they do not test them. No p-values are reported for exploratory findings. Effect estimates from exploratory analysis are directional only and must not be used to calibrate confirmatory tests.

**ERQ1 — STRM Semantic Structure (P1)**
What is the distribution of NLP-derived semantic similarity across the five STRM relationship types, and how does that distribution relate to expert-assigned strength scores? Are the five relationship categories semantically distinguishable at the embedding level, or do they overlap in ways that suggest the expert taxonomy encodes something other than semantic similarity?

**ERQ2 — Control Space Topology (P2)**
What is the empirical topological structure of the SCF control space when modeled as a directed graph over STRM mappings? Which controls occupy structurally dominant positions, and do the 33 SCF domain boundaries correspond to or cut across empirical community structure?

**ERQ3 — Cross-Framework Convergence (P3)**
When frameworks are compared via STRM mappings, what proportion of apparent convergence reflects genuine semantic alignment versus terminological similarity — controls that use similar language but address different risk vectors? Does the NIST cluster (NIST 800-53, CSF, 800-171) exhibit convergence patterns distinguishable from inter-author framework pairs?

**ERQ4 — Risk Coverage Distribution (P4)**
How are the 39 SCF risk categories covered across the control space? Are there systematic gaps — categories with sparse control coverage — or is coverage uniform? Do gaps co-locate with specific domains or framework families?

**ERQ5 — AI Governance Clustering (P5)**
How do AI governance controls cluster within and across the 33 SCF domains? Is AI governance represented as a coherent cross-cutting concern, as a domain-siloed set of controls, or as something in between? What structural relationship exists between AI governance controls and adjacent domains (privacy, data governance, security)?

---

## Confirmatory Research Questions

**[DEFERRED — to be populated after exploratory characterization]**

Confirmatory RQs are pre-specified. Each maps to one or more hypotheses in the Statistical Analysis Plan, and each hypothesis names a specific statistical test, the data it will run on, and a pre-specified effect size threshold. No confirmatory RQ is added after exploratory analysis begins.

Framework-level confirmatory questions will address whether the patterns observed in exploratory analysis are statistically distinguishable from what would be expected under appropriate null models. Specific CRQ statements will be written once exploratory characterization has established what is actually in the data.

---

## Scope Boundary

The following are explicitly out of scope for this platform:

- Normative evaluation of SCF quality — this platform characterizes structure, it does not assess whether the SCF is a good framework
- Prescriptive guidance on which controls organizations should adopt — findings are descriptive, not advisory
- Comparison of SCF against non-SCF frameworks not represented in the STRM corpus
- Generalization of findings beyond the SCF/STRM corpus to security controls in general without explicit qualification

---

## Change Log

| Date | Change | Reason | Affects pre-registered analysis? |
|------|--------|--------|----------------------------------|
| 2026-06-09 | Initial platform-level ERQ lock | Framework pre-registration | N/A — initial registration |
