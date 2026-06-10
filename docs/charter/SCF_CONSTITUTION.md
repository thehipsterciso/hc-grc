# SCF Constitution — What the Secure Controls Framework Is and How It Works

This document encodes a complete understanding of the Secure Controls Framework (SCF) — its design, structure, components, relationships, and significance. It is the authoritative reference for how the hc-grc program understands, studies, and reasons about the SCF.

---

## 1. What the SCF Is

The Secure Controls Framework is a **metaframework** — not a compliance framework, not a regulation, and not an audit standard. It is a unified control catalog that maps to 200+ laws, regulations, and frameworks simultaneously. Its official designation is the "Common Controls Framework™."

Its defining characteristics:

- **1,400+ controls** organized into **33 domains** covering cybersecurity, data privacy, and resilience
- **Free, Creative Commons licensed** — maintained by volunteer GRC practitioners (CISOs, architects, engineers, auditors, privacy experts)
- **Quarterly release cadence** with stable control IDs across versions (enabling version-to-version tracking)
- **Available in CSV and NIST OSCAL JSON** formats for GRC platform integration
- **Maps to 200+ laws, regulations, and frameworks** across 5 geographic regions via STRM

The SCF's purpose is to allow an organization to implement one control set and satisfy multiple compliance obligations simultaneously — rather than running parallel programs for NIST 800-53, ISO 27001, PCI DSS, HIPAA, GDPR, and others independently.

The SCF is **not**:
- A replacement for any specific compliance requirement
- A certification body (that is the CAP program — separate)
- An audit standard by itself
- A risk assessment methodology by itself (that is the SCR-RMM — separate)

---

## 2. What a Control Is

The SCF's definition is precise and strategic:

> **A control is the power to influence or direct behaviors and the course of events.**

This is not a technical safeguard. It is a governance instrument. Controls exist to make secure practices the default behavior of an organization — administratively, technically, and physically.

More precisely, per the SCR-RMM:
- **A risk exists due to the absence of or a deficiency with a control**
- **A threat affects the ability of a control to exist or operate properly**

These are not interchangeable. Risk is the exposure that exists when controls fail or are absent. Threat is the environmental condition that stresses controls. Controls sit between threat and risk — they are what converts a threat environment into a risk posture.

This means the completeness, accuracy, and structural soundness of a control architecture is the direct determinant of an organization's actual risk exposure — not just its compliance posture.

---

## 3. The 33 Domains

The SCF organizes controls into 33 domains using three-letter codes + sequential numbers (e.g., GOV-03). This naming convention is designed to be universal — the same control reference means the same thing across all organizations, vendors, assessors, and regulators that use the SCF.

### Governance & Management (7 domains)
| Code | Domain | Core Purpose |
|------|---------|-------------|
| GOV | Governance | Execute a documented, risk-based program supporting business objectives |
| RSK | Risk Management | Proactively identify, assess, and remediate risk aligned with organizational thresholds |
| CPL | Compliance | Oversee control execution to demonstrate due care and due diligence |
| PRM | Project & Resource Management | Operationalize security strategy through project integration |
| CHG | Change Management | Authorize and control modifications with stakeholder participation |
| HRS | Human Resources Security | Personnel practices for a security-conscious workforce |
| SAT | Security Awareness & Training | Ongoing user education about threats and secure practices |

### Technical Controls (10 domains)
| Code | Domain | Core Purpose |
|------|---------|-------------|
| SEA | Secure Engineering & Architecture | Deliver secure systems using industry-recognized engineering principles |
| TDA | Technology Development & Acquisition | Secure software development lifecycle reducing vulnerability impact |
| CFG | Configuration Management | Enforce secure configurations per vendor and industry standards |
| CRY | Cryptography | Protect data confidentiality and integrity at rest and in transit |
| IAC | Identity & Access Control | Enforce least privilege through identity and access management |
| END | Endpoint Security | Harden endpoint devices against threats |
| NET | Network Security | Defense-in-depth network architecture with least functionality |
| CLD | Cloud Security | Cloud governance with security equal to internal controls |
| EMB | Embedded Technology | Additional scrutiny for embedded systems based on malicious use potential |
| WEB | Web Security | Internet-facing technology security through configuration and monitoring |

### Security Operations (6 domains)
| Code | Domain | Core Purpose |
|------|---------|-------------|
| OPS | Security Operations | Execute cybersecurity operations delivering secure systems |
| MON | Continuous Monitoring | Situational awareness through centralized collection and analysis |
| MNT | Maintenance | Proactive asset maintenance per vendor recommendations |
| VPM | Vulnerability & Patch Management | Attack surface management to strengthen systems |
| IRO | Incident Response | Response capability with trained personnel and documented plans |
| IAO | Infrastructure & Operations | Impartial assessment validating controls before production |

### Data & Privacy (5 domains)
| Code | Domain | Core Purpose |
|------|---------|-------------|
| PRI | Privacy | Align data privacy practices with industry-recognized principles |
| DCH | Data Classification & Handling | Standardized data classification enabling proper handling |
| TPM | Third-Party Management | Supply chain risk management for trustworthy third parties |
| AAT | AI & Autonomous Technologies | Trustworthy AI minimizing unintended consequences |
| THR | Threat Management | Proactive threat identification and risk assessment |

### People & Physical (5 domains)
| Code | Domain | Core Purpose |
|------|---------|-------------|
| PES | Physical & Environmental Security | Layered physical security and environmental controls |
| MDM | Mobile Device Management | Restrict mobile connectivity limiting attack surface |
| AST | Asset Management | Technology asset lifecycle from purchase through disposition |
| BCD | Business Continuity & DR | Resilient capability sustaining critical functions through recovery |
| CAP | Cybersecurity Assessment | Govern current and future technology capacity and performance |

---

## 4. The Risk Architecture

The SCF's risk model has three hierarchical layers that must be understood as a system, not independently:

### Strategic Layer — Risk Appetite
- Defined by corporate/board leadership
- A high-level statement of what types and amounts of risk the organization is willing to accept in pursuit of value
- **Subjective** — directional guidance, not operational criteria
- Influences organizational strategy and cascades down to risk tolerance
- Example: "We are a moderate-risk organization. Any activity with greater than moderate risk requires executive case-by-case approval."

### Operational Layer — Risk Tolerance
- Defined by line-of-business management
- **Objective criteria** that translate risk appetite into graduated scales
- Typically five categories: Low / Moderate / High / Severe / Extreme
- Built from two measurable dimensions:
  - **Impact Effect (IE)**: Insignificant → Minor → Moderate → Major → Critical → Catastrophic
  - **Occurrence Likelihood (OL)**: Remote (<1%) → Highly Unlikely (1-10%) → Unlikely (10-25%) → Possible (25-70%) → Likely (70-99%) → Almost Certain (>99%)
- Influences LOB objectives, capability maturity targets, and resource prioritization

### Tactical Layer — Risk Thresholds
- Defined at department/team level
- Concrete decision points and operational control limits that trigger management action
- Unique to each organization based on: financial stability, compliance obligations, management preferences, insurance limits
- Governs: processes, technologies, staffing, and supply chain decisions

### The Four Risk Treatment Options
Every identified risk resolves to one of four decisions:
1. **Reduce** — implement or strengthen controls to bring risk within tolerance
2. **Avoid** — change the business activity to eliminate the risk
3. **Transfer** — shift risk to a third party (insurance, contract, outsourcing)
4. **Accept** — formal acknowledgment that the risk is within appetite (requires appropriate authority level)

### The Negligence Threshold
The SCF locates the negligence boundary between L1 and L2 maturity. At L1 (ad hoc practices), insufficient evidence of due care exists — a "reasonable person" standard would find negligence. At L2, documented evidence of due diligence begins. This has legal and regulatory significance: L0-L1 controls can constitute negligence if harm results.

---

## 5. The 39 Risk Categories

The SCF maps every control to a catalog of 39 risks organized by domain. These are the risks that materialize when a control fails or is absent. They are grouped as:

**Access Control**: R-AC-1 (accountability), R-AC-2 (privilege assignment), R-AC-3 (privilege escalation), R-AC-4 (unauthorized access)

**Asset Management**: R-AM-1 (lost/damaged/stolen assets), R-AM-2 (integrity loss), R-AM-3 (AI emergent properties)

**Business Continuity**: R-BC-1 (business interruption), R-BC-2 (data loss/corruption), R-BC-3 (productivity reduction), R-BC-4 (technical attack), R-BC-5 (non-technical attack)

**Exposure**: R-EX-1 (revenue loss), R-EX-2 (cancelled contract), R-EX-3 (diminished competitive advantage), R-EX-4 (reputation damage), R-EX-5 (fines and judgements), R-EX-6 (unmitigated vulnerabilities), R-EX-7 (system compromise)

**Governance**: R-GV-1 (inability to support business processes), R-GV-2 (incorrect controls scoping), R-GV-3 (lack of roles/responsibilities), R-GV-4 (inadequate internal practices), R-GV-5 (inadequate third-party practices), R-GV-6 (lack of internal oversight), R-GV-7 (lack of third-party oversight), R-GV-8 (illegal content/abusive action)

**Incident Response**: R-IR-1 (inability to investigate/prosecute), R-IR-2 (improper response), R-IR-3 (ineffective remediation), R-IR-4 (response expense)

**Situational Awareness**: R-SA-1 (inability to maintain awareness), R-SA-2 (lack of security-minded workforce)

**Supply Chain**: R-SC-1 (third-party cybersecurity exposure), R-SC-2 (third-party physical exposure), R-SC-3 (supply chain visibility), R-SC-4 (compliance/legal exposure), R-SC-5 (product/service misuse), R-SC-6 (third-party reliance)

The significance: this is an empirically derived taxonomy of what goes wrong when controls fail. It is not theoretical — it is derived from incident history and regulatory findings. Every SCF control maps to one or more of these 39 risks.

---

## 6. The Capability Maturity Model (SCR-CMM)

The SCF defines six maturity levels for control execution:

| Level | Name | Characteristics | Risk Implication |
|-------|------|-----------------|-----------------|
| L0 | Not Performed | Non-existent practices | Negligent |
| L1 | Performed Informally | Ad hoc, inconsistent | Generally negligent |
| L2 | Planned & Tracked | Requirements-driven, compliance-focused | Audit-ready for specific obligations |
| L3 | Well Defined | Enterprise-wide standardization, security-focused | Compliance is a natural byproduct |
| L4 | Quantitatively Controlled | Metrics-driven, governance oversight | Measurable, objectively managed |
| L5 | Continuously Improving | World-class, predictive, AI/ML-enabled | Continuous risk reduction |

**Key insight**: Risk associated with a control decreases with maturity, but noticeable risk reductions are harder to attain above L3. The practical "sweet spot" for most organizations is L2–L4. L0–L1 are considered negligent by reasonable person standards.

**Internal vs. external shift**: L0–L3 are internal maturity levels (IT/security/compliance teams drive them). L4–L5 are external — business stakeholders are genuinely involved in oversight and continuous improvement. This creates a fundamental shift in who owns the security program.

---

## 7. Set Theory Relationship Mapping (STRM)

The STRM is the SCF's methodology for documenting how SCF controls relate to external laws, regulations, and frameworks. It uses NIST IR 8477 methodology with five relationship types:

| Symbol | Relationship | Meaning |
|--------|-------------|---------|
| ⊂ | Subset Of | SCF control is contained within the external requirement |
| ∩ | Intersects | Partial overlap — SCF control partially satisfies the requirement |
| = | Equal To | SCF control fully satisfies the external requirement |
| ⊃ | Superset Of | SCF control exceeds the external requirement |
| ∅ | No Relation | No meaningful relationship |

Each mapping includes a **numeric strength score** indicating confidence in the relationship assessment. This is critical for the hc-grc program: STRM is the SCF's own structured claim about how it relates to other frameworks. These claims are exactly what the hc-grc program tests empirically — whether the structural relationships the SCF asserts are borne out in the actual control text.

---

## 8. The SCRMS — Operational Implementation

The SCRMS (Security, Compliance & Resilience Management System) is the SCF's operational playbook — how organizations actually implement the framework. It replaces siloed management systems (separate ISMSs, privacy programs, risk programs) with a unified approach.

**Five dimensions of coverage (PPTDF-AI)**:
- **People** — training, hiring, access governance
- **Processes** — policies, procedures, change management
- **Technology** — systems, networks, applications, configurations
- **Data** — classification, handling, encryption, governance
- **Facilities** — physical security, environmental controls
- **AI** — AI and autonomous technology governance (added in recent versions)

**Control categories**:
- **MCR (Minimum Compliance Requirements)** — non-negotiable externally mandated controls from laws and contracts
- **DSR (Discretionary Security Requirements)** — risk-based enhancements beyond compliance minimums

**Nine operational principles**:
1. Establish Context
2. Identify Applicable Controls
3. Define Maturity Expectations
4. Publish Governance Documentation
5. Assign Stakeholder Accountability
6. Prioritize Capabilities According to Risk
7. Maintain Situational Awareness
8. Manage Risk
9. Evolve Processes

The SCRMS uses a PDCA (Plan-Do-Check-Act) lifecycle across strategic, operational, and tactical dimensions.

---

## 9. Cybersecurity Materiality

The SCF defines materiality as: *"A deficiency, or a combination of deficiencies, in an organization's cybersecurity and/or data privacy controls (across its supply chain) where it is probable that reasonable threats will not be prevented or detected in a timely manner that directly, or indirectly, affects assurance that the organization can adhere to its stated risk tolerance."*

A control deficiency is material when it has one or more of the following financial impacts:
- ≥ 5% of pre-tax income
- ≥ 0.5% of total assets
- ≥ 1% of total equity (shareholder value)
- ≥ 0.5% of total revenue

Material controls receive prioritized assessment focus in the CAP. Compensating controls cannot substitute for material control failures. This aligns with SEC cybersecurity disclosure requirements for publicly traded companies.

Materiality connects the SCF to financial reporting, M&A due diligence, and regulatory disclosure — it is the bridge between security posture and financial consequence.

---

## 10. The SCF as a Crosswalk

The SCF serves a role no other single framework plays: it is the **alignment substrate** for cross-framework comparison. Because the SCF maps to 200+ laws and frameworks via STRM, and because it is organized into a stable, versioned, semantically consistent taxonomy, it is the natural reference point for understanding how frameworks relate to each other.

For the hc-grc program, this means the SCF is both:
1. **A subject of study** — its own structural properties, domain organization, and control-to-risk mappings are characterized as a corpus
2. **The alignment layer** — the SCF crosswalk is what makes cross-framework comparison in Tier 2 possible; it provides the common substrate onto which NIST 800-53, CIS Controls, and others are mapped for structural comparison

The SCF's STRM claims (subset/intersect/superset relationships) are precisely the structural assertions that empirical analysis can test — whether the claimed coverage relationships hold in the actual control text, and where they diverge from what STRM asserts.

---

## 11. What the SCF Does Not Solve

Understanding what the SCF is requires understanding what it leaves open:

- **The SCF asserts coverage; it does not measure it.** STRM mapping is expert judgment, not empirical measurement. Whether a "superset" relationship holds in practice — whether the SCF control actually covers the external requirement's semantic content — is a question the SCF's methodology cannot answer about itself.
- **Domain boundaries are editorial choices.** The 33-domain structure reflects how the SCF Council organized control space. Whether those boundaries correspond to natural clusters in actual control semantics is an empirical question, not a design decision.
- **Maturity targets are organizational, not universal.** The L2–L4 "sweet spot" guidance is practical but not derived from measurement of actual risk reduction across control types and domains.
- **The 39 risk categories are a taxonomy, not a coverage map.** Knowing which risks exist does not establish which are well-covered by existing frameworks and which are systematically underserved.

These are precisely the gaps that empirical characterization of control space — the hc-grc program's purpose — can address.
