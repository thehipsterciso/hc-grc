# Theoretical Framework

**Lock status:** LOCKED at framework pre-registration. The core gap, contribution claim, and epistemic stance are data-independent and fixed before any SCF data is examined. Construct definitions and the conceptual model are locked here. Specific theoretical propositions that generate confirmatory hypotheses are deferred pending exploratory characterization — they will be added as an amendment to this document before SAP lock.

---

## The Gap This Platform Attacks

Security metaframeworks organize enterprise control libraries and assert relationships between controls across different regulatory and standards frameworks. The SCF/STRM corpus is the most systematically constructed such metaframework publicly available — 1,400+ controls, 33 domains, approximately 280,000 expert-derived relationship mappings with typed relationships (⊂ ∩ = ⊃ ∅) and strength scores (1–10).

These mappings represent expert consensus. Expert consensus is not the same as empirical validity. The distinction matters because:

**Organizations use STRM mappings to make resource allocation decisions.** A CISO who believes two frameworks converge on a control — based on a STRM mapping that asserts `=` with strength 9 — may invest in satisfying that control once and assume dual-framework compliance. If that mapping is semantically weak, the compliance posture is illusory. The decision was made on untested data.

**Researchers use SCF/STRM as ground truth for compliance automation systems.** A system trained to predict framework coverage based on STRM mappings inherits whatever error structure exists in those mappings. If that structure has never been characterized, the system's failure modes are unknown.

**The field has no empirical baseline for what "framework convergence" means quantitatively.** Practitioners claim frameworks converge or diverge, but without a common empirical measure, these claims are impressionistic. P3 of this platform attempts to establish that baseline.

The gap is not that experts are wrong. The gap is that the difference between "experts asserted this" and "this was empirically characterized" has never been measured. This platform measures it.

---

## Contribution Claim

**Primary contribution:** First large-scale empirical characterization of the SCF/STRM corpus — semantic validity of STRM mappings, topological structure of the control space, quantitative convergence across frameworks, risk coverage distribution, and AI governance clustering.

**Secondary contribution:** A reproducible, pre-registered methodology for analyzing security metaframework corpora that can be applied to future versions of SCF and to other metaframeworks.

**What this platform does NOT claim:**
- That the SCF is correct or incorrect as a normative framework
- That findings from this corpus generalize to all security control frameworks
- That the analytical methods are the only valid approach to these questions

The contribution is empirical characterization with explicit scope. It does not extend beyond what the data and methods can support.

---

## Epistemic Stance

This platform adopts a pre-registered, exploratory-first methodology. This is an explicit epistemic choice with consequences for how findings should be interpreted.

**Exploratory analysis is not preliminary.** Characterizing a corpus that has never been empirically examined is substantive scientific work. Exploratory findings are reported as descriptive results — distributions, structures, patterns — not as tested hypotheses. They generate hypotheses for confirmatory testing; they do not confirm them.

**Confirmatory analysis is constrained.** Only hypotheses pre-specified in the locked SAP are tested on the confirmatory (test) split. A finding that emerges from exploratory analysis and looks interesting is not a confirmatory result — it is a new hypothesis for a future study. This constraint prevents the most common form of bias in empirical security research: reporting exploratory patterns as if they were pre-specified tests.

**Null results are findings.** A hypothesis that fails to reach significance with the pre-specified effect size is a finding. It is reported with the same rigor as a positive result. The platform is designed to produce honest characterization, not to confirm prior beliefs about the SCF.

**Performative certainty is explicitly rejected.** Any claim made here is qualified by what the data and methods can actually support. The platform produces characterization of one corpus at one point in time. Generalizations beyond that boundary are marked explicitly as speculation.

---

## Core Theoretical Claims

These are data-independent propositions that motivate the research questions. They are not hypotheses — they are the prior beliefs that generate hypotheses. Specific hypotheses derived from these claims will be added as a pre-SAP amendment after exploratory characterization.

**TC1: Expert-derived semantic mappings contain systematic error structure**
Expert judgment in knowledge engineering tasks is consistent within domains and inconsistent across them, and degrades with cognitive load (mapping count, ambiguity of boundary controls). If this is true for STRM mappings, semantic similarity should predict mapping strength within relationship types but show domain-level variance. The specific pattern of that variance is unknown — that is what exploratory analysis characterizes.
- Supporting literature: Knowledge engineering literature on expert consistency; judgment and decision-making research on expertise degradation under volume
- Logical connection to hypotheses: Generates P1 hypotheses about the relationship between NLP-derived similarity scores and expert-assigned strength, moderated by domain

**TC2: Regulatory framework convergence is partially terminological, not purely semantic**
Frameworks authored within the same community share vocabulary. Shared vocabulary produces surface-level similarity in NLP embeddings that may not correspond to substantive control equivalence. The NIST cluster (800-53, CSF, 800-171) shares authorship; the convergence patterns within it are expected to differ qualitatively from cross-author convergence.
- Supporting literature: NLP research on domain-specific vocabulary; regulatory convergence literature (limited); prior work on shared vs. independent authorship effects on similarity measures
- Logical connection to hypotheses: Generates P3 hypotheses about NIST cluster convergence vs. cross-author convergence, requiring the NIST cluster independence constraint to be enforced in analysis

**TC3: Control space topology is not uniformly distributed**
In any large knowledge graph, a small number of nodes occupy disproportionately connected positions. In the SCF control space, some controls likely function as structural hubs — referenced across many frameworks and domains — while most controls are peripheral. This structural asymmetry has practical implications for compliance prioritization that have not been characterized.
- Supporting literature: Graph theory (scale-free network properties in knowledge graphs); prior work on control framework structure (limited)
- Logical connection to hypotheses: Generates P2 hypotheses about centrality distribution and community structure

**TC4: AI governance controls have not yet achieved structural integration with adjacent domains**
AI governance as a discipline is younger than most SCF domains. Controls addressing AI-specific risks (model integrity, training data, inference security) were added to existing frameworks designed around different threat models. If AI governance is structurally unintegrated, it should cluster as an isolated community in P5 rather than as a coherent cross-cutting concern, and should show weaker inter-domain STRM mapping density than comparable mature domains.
- Supporting literature: AI governance framework maturity literature; standards development lifecycle research
- Logical connection to hypotheses: Generates P5 hypotheses about AI governance cluster structure and cross-domain integration

---

## Conceptual Model

```
Expert Knowledge Engineering Process
        ↓
SCF Controls (1,400+)  ←→  STRM Mappings (280,000+)
   [nodes]                  [typed, weighted edges]
        ↓                            ↓
  P2: Topology              P1: Semantic Validity
  P4: Risk Coverage         P3: Convergence
  P5: AI Governance         (NIST cluster independence)
        ↓                            ↓
              Empirical Characterization
                           ↓
                Exploratory Findings (ERQ1–ERQ5)
                           ↓
                 [SAP lock — hypotheses specified]
                           ↓
                Confirmatory Tests (CRQ — deferred)
```

TC2 (terminological convergence) applies a moderating constraint to P3 and P1. The NIST cluster independence constraint is a methodological operationalization of TC2 — treating NIST 800-53, CSF, and 800-171 as one evidence source rather than three.

---

## Construct Definitions

These definitions govern how variables are operationalized in the analysis. Changes to these definitions after pre-registration constitute a SAP violation.

| Construct | Definition | Operationalization |
|-----------|-----------|-------------------|
| STRM semantic validity | The degree to which an expert-asserted mapping relationship is supported by NLP-derived semantic similarity | Cosine similarity of sentence-transformer embeddings of control descriptions, compared against mapping type and strength score |
| Framework convergence | The degree to which controls from two frameworks address the same risk vector | Semantic similarity of control descriptions, moderated by STRM mapping type; genuine convergence distinguished from terminological convergence by within-framework author group analysis |
| Control centrality | The structural importance of a control in the SCF graph | Degree, betweenness, and eigenvector centrality computed on directed STRM graph |
| Community structure | Empirically-derived groupings of controls that have denser internal than external STRM connections | Leiden algorithm output on STRM graph; compared against SCF domain boundaries |
| Risk coverage | The density of controls mapped to each of the 39 SCF risk categories | Count and semantic diversity of controls per risk category |
| AI governance integration | The degree to which AI governance controls have structural connections to adjacent domains | Cross-domain STRM density for AI governance controls vs. comparable domain baseline |
| NIST cluster | The set of frameworks with shared authorship: NIST SP 800-53, NIST CSF, NIST SP 800-171 | Treated as single evidence source for convergence analysis; within-cluster mappings excluded from cross-framework convergence claims |

---

## Boundary Conditions

This theoretical framework applies specifically to:
- The SCF corpus as of the acquired version (version pinned at data acquisition)
- Controls and STRM mappings for which full text descriptions are available
- The 33 SCF domains as defined in the acquired version

It does NOT apply to:
- Security control frameworks not represented in the SCF/STRM corpus
- Future versions of SCF without re-running the analysis
- Controls with missing or incomplete descriptions (handling defined in methods scaffolding)
- Inferences about the quality of individual framework authors' expertise

---

## Alternative Theories

These are documented before analysis to prevent motivated reasoning when results arrive.

| Alternative theory | How it would produce similar results | How it is distinguishable |
|-------------------|--------------------------------------|---------------------------|
| STRM mappings are semantically valid but NLP embeddings are inadequate | High NLP similarity scores but poor discrimination between mapping types | Distinguishable by checking whether a fine-tuned domain-specific model improves discrimination; if embeddings are the limitation, fine-tuning should resolve it |
| AI governance structural isolation reflects data recency, not domain immaturity | Recent SCF additions have fewer STRM mappings regardless of domain maturity | Distinguishable by comparing AI governance mapping density against other recent SCF domain additions of similar age |
| Apparent NIST cluster convergence reflects deliberate framework harmonization | Same result as TC2 but mechanism is intentional coordination, not shared vocabulary | May be indistinguishable empirically; acknowledged as limitation in findings |

---

## Pre-SAP Amendment Section

**[DEFERRED — to be populated before SAP lock]**

After exploratory characterization, specific theoretical propositions linking TC1–TC4 to confirmatory hypotheses will be added here as an amendment. The amendment will be committed to the pre-registration branch with RFC 3161 timestamp. The core framework above is not modified by the amendment — only the hypothesis-generating propositions section is extended.
