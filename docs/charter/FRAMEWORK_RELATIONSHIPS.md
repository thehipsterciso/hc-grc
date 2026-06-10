# Framework Relationships Constitution — How GRC Frameworks Relate to Each Other and to the SCF

This document encodes the structural relationships between frameworks in the hc-grc program and the SCF's methodology for mapping them. It is the reference for how cross-framework analysis is conducted and what claims it can and cannot support. The program is open-ended — the current study set is the first wave, not a ceiling.

---

## 1. The Current Study Set

The program begins with five frameworks. Expansion to additional frameworks is expected. Each new framework added must be evaluated against the independence constraints in section 2, the licensing requirements in section 8, and the crosswalk availability in section 9 before inclusion.

| Framework | Code | Publisher | License | Role in hc-grc |
|-----------|------|-----------|---------|----------------|
| Secure Controls Framework | SCF | SCF Council / ComplianceForge | Creative Commons | Corpus + crosswalk substrate |
| NIST SP 800-53 Rev 5 | NIST-800-53 | NIST | Public domain (OSCAL) | Native corpus |
| NIST CSF 2.0 | NIST-CSF | NIST | Public domain | Native corpus |
| NIST SP 800-171 Rev 3 | NIST-800-171 | NIST | Public domain (OSCAL) | Native corpus |
| CIS Controls v8 | CIS-v8 | Center for Internet Security | Open terms | Native corpus |

---

## 2. The NIST Cluster — The Critical Independence Constraint

Three frameworks in the current study set share a common author: NIST. This is not a minor observation. It is a structural constraint on what cross-framework findings can claim. Any future NIST-derived framework added to the program (e.g., NIST 800-171A, NIST AI RMF) extends this cluster and does not add an independent evidence source.

**NIST SP 800-53** is the comprehensive security and privacy controls catalog for federal information systems. It is the most expansive NIST framework — the source document from which many others derive.

**NIST CSF 2.0** is the Cybersecurity Framework — a risk-based framework organized around five functions (Identify, Protect, Detect, Respond, Recover) with a sixth added in version 2.0 (Govern). It is designed for broad adoption across sectors, abstracting NIST 800-53 into higher-level outcomes.

**NIST SP 800-171** governs protection of Controlled Unclassified Information (CUI) in non-federal systems. It is a subset of 800-53, scoped for defense contractors and federal supply chain.

These three frameworks share:
- The same authoring organization (NIST)
- Overlapping control populations (800-171 is explicitly derived from 800-53)
- Common terminology, taxonomic conventions, and risk framing
- The same OSCAL format and schema

**The constraint**: Agreement among NIST 800-53, NIST CSF, and NIST 800-171 on any structural finding does not constitute independent replication. It constitutes agreement within a single editorial lineage. The "NIST cluster" (L2 constraint in hc-grc terminology) means:

- A finding that holds in all three NIST frameworks but not in any non-NIST framework is a **NIST-cluster property**, not an intrinsic property of control space
- A finding that holds across the NIST cluster AND at least one non-NIST framework (SCF, CIS, or any future addition) is a candidate for "intrinsic" classification — subject to further adversarial review
- A finding that holds across all frameworks under study, spanning multiple independent authoring organizations, is the program's strongest evidence class

---

## 3. The SCF as Crosswalk Substrate

The SCF is unique among frameworks in the hc-grc program: it was explicitly designed to map to all others via STRM. This gives it a dual role:

**As a research subject**: The SCF's own structural properties — domain organization, control density, risk coverage, network topology — are characterized as a corpus alongside the other four frameworks.

**As the alignment layer**: Because the SCF maps to NIST 800-53, NIST CSF, NIST 800-171, and CIS Controls (among 200+ others), it provides the common substrate for cross-framework comparison in Tier B. The crosswalk built from SCF's STRM mappings is what allows the program to ask: does finding X in 800-53 correspond to finding Y in CIS Controls, and what does the SCF's control space look like when both are projected onto it?

**The circularity constraint (L1)**: SCF crosswalk evidence cannot establish "structural similarity" between the SCF and any other framework. That would be circular — the SCF defined the crosswalk, so agreement between SCF and any framework's STRM mapping is not independent evidence. It is a tautology. Any cross-framework claim that traces primarily to SCF-to-SCF crosswalk agreement is invalid.

---

## 4. The STRM Relationship Types — What They Mean for Analysis

The SCF's Set Theory Relationship Mapping uses five relationship types from NIST IR 8477:

**⊂ Subset Of**: The SCF control is contained within the external requirement. The external requirement demands more than or equal to what the SCF control specifies. An organization implementing the SCF control satisfies part of the requirement but may not satisfy all of it.

**∩ Intersects**: Partial overlap. The SCF control and the external requirement share some semantic content but neither contains the other. Implementing the SCF control addresses some but not all of the requirement, and vice versa.

**= Equal To**: The SCF control fully satisfies the external requirement and the requirement fully satisfies the SCF control. They are semantically equivalent.

**⊃ Superset Of**: The SCF control exceeds the external requirement. Implementing the SCF control satisfies the requirement and provides additional coverage.

**∅ No Relation**: No meaningful overlap between the SCF control and the external requirement.

**What these mean empirically**: STRM mappings are expert judgments, not measurements. They represent the SCF Council's assessment of semantic overlap. The hc-grc program tests whether these claimed relationships hold in the actual control text — whether controls the STRM marks as "= Equal To" are actually semantically equivalent when the text is embedded and analyzed, or whether "⊃ Superset Of" claims overstate the SCF's coverage relative to the mapped framework.

---

## 5. Framework Scope Differences — What Each Is For

Understanding what each framework was designed to cover is prerequisite to interpreting structural differences.

**SCF**: Comprehensive metaframework. Designed to cover every control domain relevant to cybersecurity, privacy, and resilience for organizations of any size or sector. No specific regulatory mandate — designed for voluntary adoption as a compliance consolidation tool.

**NIST 800-53**: Comprehensive security and privacy controls for federal information systems and organizations. Required for federal agencies (FISMA). The most granular and extensive NIST framework — 20 control families, 1,000+ controls including enhancements. Includes privacy controls integrated with security controls since Rev 5.

**NIST CSF 2.0**: Outcome-based risk framework for broad adoption. Organized by function (Govern, Identify, Protect, Detect, Respond, Recover) rather than control domain. Maps to 800-53 but at a higher level of abstraction. Not prescriptive — organizations choose their implementation approach.

**NIST 800-171**: Subset of 800-53, scoped for CUI protection in non-federal systems. 110 basic security requirements across 14 families. Required for defense contractors (DFARS clause 252.204-7012) and increasingly for broader federal supply chain participation (CMMC).

**CIS Controls v8**: 18 controls organized into three implementation groups (IG1/IG2/IG3) scaled by organizational size and risk profile. Prescriptive and prioritized — designed for practical implementation, not comprehensive coverage. Based on observed attack patterns (not regulatory requirements).

**Structural implications**:
- 800-53 and SCF are comprehensive; CSF and CIS Controls are selective
- 800-171 is a derivative subset — it does not introduce novel control concepts, only scopes and combines elements from 800-53
- CIS Controls are attack-surface-driven; the others are more domain-completeness-driven
- These design differences should produce measurable structural differences in clustering, network topology, and coverage distribution — and those differences are findings, not artifacts

---

## 6. What Cross-Framework Replication Means

The hc-grc program's strongest evidence is a structural finding that replicates across the frameworks under study. This requires understanding what "replication" means across frameworks with different scope, design intent, and authorship. As the program expands, additional frameworks increase the available replication surface — but only those from independent authoring organizations add independent evidence.

**Intrinsic property**: A structural finding that holds across all frameworks under study — including across the NIST cluster AND at least one non-NIST framework — is a candidate for "intrinsic" classification. It suggests the finding is a property of control space itself, not an artifact of any particular framework's design philosophy. Intrinsic findings are the most strategically significant — they describe the underlying landscape that every framework is trying to map. The more independent authoring organizations represented in the replication set, the stronger the intrinsic claim.

**Framework-specific property**: A finding that appears in some frameworks but not others. This is evidence about those frameworks' editorial choices — what they chose to emphasize, scope out, or organize differently. Framework-specific findings are significant for framework selection decisions: if your risk profile is concentrated in an area one framework handles differently than others, that is material information.

**Crosswalk-dependent property**: A finding that appears only when frameworks are aligned via the SCF crosswalk. This finding is conditional on the quality of the crosswalk alignment — a noisy or incorrect crosswalk mapping could produce spurious agreements or hide genuine differences. Crosswalk-dependent findings must always be reported with their alignment quality caveat.

**The L2 independence constraint, restated**: A finding that holds only within the NIST cluster (800-53, CSF, 800-171) is not independent replication. Three findings that share authorship, terminology, and derivation history are one evidence source, not three.

---

## 7. The SCF's Relationship to Compliance Frameworks

The SCF maps to the following categories of external frameworks (partial list from 200+):

**US Federal**: FISMA, FedRAMP, CMMC, DFARS, SOX (IT), GLBA, HIPAA, FDA 21 CFR Part 11, NERC CIP, TSA security directives

**International**: GDPR, NIS2, DORA, ISO 27001/27002, ISO 31000, ISO 31010

**Industry**: PCI DSS, HITRUST CSF, SOC 2 Trust Services Criteria, COBIT, CSA CCM, OWASP

**State/Regional**: CCPA, NY DFS Cybersecurity Regulation, Texas DIR

For each mapping, STRM specifies the relationship type (⊂, ∩, =, ⊃, ∅) and a strength score. The density and type distribution of these mappings across SCF domains is empirically measurable — and reveals which SCF domains are structurally central (mapped to by many external frameworks) versus peripheral (few external framework mappings).

This is a direct measure of **regulatory coverage concentration** — which control domains regulators and industry bodies have converged on versus which they have largely ignored.

---

## 8. Framework Licensing and Its Significance

All frameworks in the hc-grc program's first wave are open-licensed. This is deliberate — it means:

- Source text is freely available for ingestion without license negotiation (T2 trivial)
- The corpus can be published as part of a reproducibility package
- Findings are based on the full authoritative text, not summaries or abstracts

**SCF**: Creative Commons. The SCF Council explicitly permits analysis and derivative works under CC terms.

**NIST frameworks**: Public domain (US government works). OSCAL format is published on GitHub with no restrictions.

**CIS Controls v8**: Available under CIS open terms for non-commercial analysis.

A future expansion to paywalled frameworks (ISO 27001, PCI DSS full text) requires T2 sign-off due to licensing implications — this is the human gate the program preserves for that decision.

---

## 9. The Crosswalk's Role in Tier B Analysis

Tier B of the hc-grc program (cross-framework synthesis) depends on the SCF crosswalk as its alignment substrate. The mechanics:

1. Each framework's controls are mapped to SCF controls via STRM relationships
2. Controls that map to the same SCF control are placed in "alignment" for comparison
3. Structural findings from each framework's Tier A study are compared at the SCF-aligned level
4. Findings that hold across aligned controls from multiple frameworks are candidates for cross-framework claims

**What this analysis can and cannot claim**:
- It CAN identify which structural properties survive framework alignment — i.e., are visible from multiple frameworks' perspectives on the same underlying control space
- It CANNOT claim that frameworks with high SCF alignment scores are "better" or "more comprehensive" — that is a normative judgment, not a structural finding
- It CAN identify which risk categories (from the 39) are well-covered by multiple frameworks and which are addressed by only one or none
- It CANNOT resolve disagreements between frameworks' STRM mappings by fiat — where STRM claims equivalence but textual analysis finds divergence, both are reported

The crosswalk is a measurement instrument, not a ground truth. Its quality is itself a finding, and every cross-framework claim must carry its alignment quality as a caveat.
