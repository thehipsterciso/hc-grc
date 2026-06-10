# Risk Constitution — How Risk Works in the SCF Model and What the hc-grc Program Measures

This document encodes the SCF's complete risk model and explains what it means for the hc-grc program's purpose. Any agent, researcher, or stakeholder working within this program must understand this model before interpreting findings.

---

## 1. The Foundational Equation

> **Risk exists due to the absence of or a deficiency with a control.**
> **A threat affects the ability of a control to exist or operate properly.**

These two statements from the SCF-RMM are not definitions for a glossary. They are the load-bearing structure of the entire framework. Every question in the hc-grc program ultimately traces back to this relationship:

```
Threat environment → stresses → Controls → whose absence or failure → produces → Risk
```

The implication: if you do not know the structural properties of your control architecture — what it covers, what it misses, how dense its coverage is across different risk domains — you cannot accurately assess your actual risk exposure. You can only assess risk within the boundaries your framework acknowledges.

---

## 2. The Three-Layer Risk Hierarchy

The SCF models risk governance as three interlocking layers. Each layer sets constraints for the one below it. The layers do not operate independently — a failure at any layer cascades.

### Layer 1: Strategic — Risk Appetite
**Who owns it**: Board / CEO / executive leadership  
**What it is**: A high-level, subjective statement of the types and amounts of risk the organization is willing to accept in pursuit of value  
**What it does**: Defines the upper bound of acceptable risk; influences organizational strategy; establishes the frame within which risk tolerance is set

Risk appetite is not operational. It cannot be measured directly. It is a governance instrument — a statement of intent that must be operationalized by the layer below.

**The failure mode**: Risk appetite statements that are divorced from operational reality. Executive leadership issues a "moderate risk" appetite statement while BAU practices routinely violate it due to technical debt, dysfunctional management, underfunding, or improperly scoped contracts. The appetite exists on paper; the actual posture is uncontrolled.

### Layer 2: Operational — Risk Tolerance
**Who owns it**: Line of Business (LOB) management  
**What it is**: Objective criteria that translate risk appetite into a graduated scale — typically Low / Moderate / High / Severe / Extreme  
**What it does**: Provides measurable thresholds that LOB decisions must stay within; influences capability maturity targets and resource prioritization

Risk tolerance is built from two measurable dimensions:

**Impact Effect (IE)**:
- Insignificant — negligible effect on business operations
- Minor — limited, recoverable impact
- Moderate — noticeable impact requiring management attention
- Major — significant disruption to operations or finances
- Critical — severe harm to the organization's viability or reputation
- Catastrophic — existential threat

**Occurrence Likelihood (OL)**:
- Remote — < 1% probability
- Highly Unlikely — 1% to 10%
- Unlikely — 10% to 25%
- Possible — 25% to 70%
- Likely — 70% to 99%
- Almost Certain — > 99%

Occurrence likelihood is estimated via: (1) relevant historical data, (2) probability forecasts, or (3) expert opinion.

### Layer 3: Tactical — Risk Thresholds
**Who owns it**: Department / team management  
**What it is**: Concrete, organization-specific criteria that trigger management action and response escalation  
**What it does**: Governs day-to-day operational decisions about processes, technologies, staffing, and supply chain

Risk thresholds are entirely unique to each organization. They are affected by: financial stability, management preferences, compliance obligations, and insurance coverage limits.

**The operational consequence**: When a risk is assessed against thresholds and found to exceed them, exactly four treatment options exist — reduce, avoid, transfer, or accept. Accepting a risk that exceeds the risk appetite is, by the SCF model, a potential violation of fiduciary duty and possibly negligence.

---

## 3. Materiality — Where Risk Becomes Financial and Legal

The SCF defines a cybersecurity control deficiency as **material** when:

*"It is probable that reasonable threats will not be prevented or detected in a timely manner that directly, or indirectly, affects assurance that the organization can adhere to its stated risk tolerance."*

Quantified as meeting one or more of:
- ≥ 5% of pre-tax income
- ≥ 0.5% of total assets
- ≥ 1% of total equity
- ≥ 0.5% of total revenue

Materiality bridges security posture and financial consequence. It is the threshold at which:
- SEC cybersecurity disclosure requirements (for public companies) are triggered
- Board oversight of security decisions is not optional but obligatory
- Control deficiencies move from operational risk to financial risk
- M&A valuations are directly affected

**For the hc-grc program**: A finding that a control domain is systematically sparse, structurally isolated, or uncovered by the frameworks organizations rely on is a materiality-relevant finding. It is not a technical observation — it has direct financial and legal implications for every organization whose risk program relies on that domain's coverage.

---

## 4. The 39 Risk Categories — The Taxonomy of What Goes Wrong

The SCF's risk catalog maps control failures to 39 defined risks. These are not theoretical — they are grounded in incident history, regulatory enforcement patterns, and litigation outcomes. They represent the empirically observed consequences of control absence or deficiency.

### Access Control Risks (R-AC)
- R-AC-1: Inability to maintain individual accountability (asset ownership, non-repudiation)
- R-AC-2: Improper assignment of privileged functions (RBAC failures, PAM gaps)
- R-AC-3: Privilege escalation (inability to restrict privileged access)
- R-AC-4: Unauthorized access (access granted beyond authorization)

### Asset Management Risks (R-AM)
- R-AM-1: Lost, damaged, or stolen assets
- R-AM-2: Loss of integrity through unauthorized changes
- R-AM-3: Emergent properties and unintended consequences from AI/autonomous technologies

### Business Continuity Risks (R-BC)
- R-BC-1: Business interruption (latency or outage affecting operations)
- R-BC-2: Data loss or corruption (CIA compromise)
- R-BC-3: Reduction in productivity
- R-BC-4: System compromise from technical attack (malware, phishing, hacking)
- R-BC-5: System compromise from non-technical attack (social engineering, sabotage)

### Exposure Risks (R-EX)
- R-EX-1: Loss of revenue
- R-EX-2: Cancelled contract for cause
- R-EX-3: Diminished competitive advantage
- R-EX-4: Diminished reputation / brand value
- R-EX-5: Fines and judgements from regulatory/contractual non-compliance
- R-EX-6: Unmitigated technical vulnerabilities
- R-EX-7: System, application, or service compromise

### Governance Risks (R-GV)
- R-GV-1: Inability to support business processes
- R-GV-2: Incorrect controls scoping (missing or wrong controls due to scoping errors)
- R-GV-3: Lack of roles and responsibilities
- R-GV-4: Inadequate internal practices
- R-GV-5: Inadequate third-party practices (C-SCRM failures)
- R-GV-6: Lack of oversight of internal controls
- R-GV-7: Lack of oversight of third-party controls
- R-GV-8: Illegal content or abusive action

### Incident Response Risks (R-IR)
- R-IR-1: Inability to investigate or prosecute incidents (chain of custody, evidence)
- R-IR-2: Improper response to incidents
- R-IR-3: Ineffective remediation actions
- R-IR-4: Financial expense of managing a loss event

### Situational Awareness Risks (R-SA)
- R-SA-1: Inability to maintain situational awareness (detection failures)
- R-SA-2: Lack of a security-minded workforce

### Supply Chain Risks (R-SC)
- R-SC-1: Third-party cybersecurity exposure
- R-SC-2: Third-party physical security exposure
- R-SC-3: Third-party supply chain relationships, visibility, and controls
- R-SC-4: Third-party compliance/legal exposure
- R-SC-5: Misuse of product or service
- R-SC-6: Business dependency on a third party

**What this taxonomy means for hc-grc**: Every finding about control coverage gaps maps directly to one or more of these 39 risks. A gap in coverage is not an abstract structural observation — it is a specific risk exposure that the organization cannot see, assess, or treat, because the framework it relies on does not acknowledge it.

---

## 5. The Negligence Standard

The SCF is explicit about where the legal line is:

- **L0 and L1** maturity are generally negligent. If a control is reasonably expected to exist and is absent or only ad hoc, a "reasonable person" standard would find negligence. This is not an internal assessment — it is the standard courts and regulators apply.
- **L2** is the minimum threshold for demonstrating due care and due diligence — the evidentiary bar for arguing that reasonable steps were taken.

Due care: the standard a reasonable person would exercise under similar circumstances.  
Due diligence: the care a reasonable person exercises to avoid harm to others.

Both are required to defend against negligence claims. Documentation of risk management decisions is not optional — if it is not documented, it does not exist in a legal context.

**The CISO/CRO protection implication**: When business leadership denies funding to reach a stated maturity target, the CISO who documented the target, the business case, and the denial is insulated. The documentation proves due diligence was performed and the risk acceptance was made at the appropriate authority level. Without documentation, risk defaults to the security function regardless of who actually made the decision.

---

## 6. The Control-Risk-Threat Ecosystem

Controls, risks, and threats are not equivalent. The SCF is precise:

| Concept | Definition | Relationship to Controls |
|---------|-----------|------------------------|
| Control | The power to influence or direct behaviors and events | Controls are the mechanism |
| Risk | A situation where something valued is exposed to danger, harm, or loss | Risk exists when controls are absent or deficient |
| Threat | A person or thing likely to cause damage or danger | Threats stress controls' ability to operate |
| Vulnerability | A weakness that can be exploited by a threat | Vulnerabilities exist within or between controls |

The relationships:
- A **threat** exploits a **vulnerability** to realize a **risk** where a **control** is absent or deficient
- Controls do not eliminate threats — they reduce the likelihood and impact of threats materializing as risk
- A well-functioning control under active threat is doing its job; a control deficiency under the same threat is a risk event in progress

---

## 7. Risk Ownership — Who Decides

The SCF is explicit that cybersecurity and IT departments do not "own" technology-related risks. Risk ownership resides with Line of Business management. Security functions:

- **Identify** risks through assessment
- **Assess** severity against established criteria
- **Report** findings to the appropriate risk owner with treatment options
- **Advise** on remediation approaches

But the **decision to reduce, avoid, transfer, or accept** belongs to the LOB manager who owns the affected business process. This is not a weakness in the model — it is a governance principle. Security teams that make unilateral risk decisions on behalf of business functions are operating outside their authority and creating accountability gaps.

**What goes wrong**: "Rogue risk management" occurs when risk teams create assessments disconnected from the organization's actual control framework — asking NIST 800-171 questions at an ISO shop, or inventing risks not supported by any policy or standard. This produces unusable findings, erodes trust, and generates risk register entries that cannot be treated because they are not grounded in the organization's actual control architecture.

---

## 8. Enterprise Risk Management — The Integration Requirement

Disjointed risk management practices produce a fundamental problem: "Moderate Risk" means different things to different departments. A cybersecurity "High Risk" may be a finance "Low Risk" and a legal "Critical Risk" for the same event.

Enterprise Risk Management (ERM) solves this by applying a consistent risk taxonomy organization-wide. The SCF's risk appetite → tolerance → threshold hierarchy is designed to make this consistency achievable — but only if the control architecture it is built on is actually comprehensive.

**The hidden dependency**: ERM assumes the control framework it maps to actually covers the risk domains that matter. If the frameworks the organization uses have structural gaps — domains where controls are sparse, isolated, or absent — ERM will systematically miss risks in those domains, not because of poor ERM practice, but because the underlying control architecture does not acknowledge them.

This is what hc-grc measures.

---

## 9. Third-Party and Supply Chain Risk

Supply chain risk is not a separate risk category in the SCF — it is embedded structurally across R-SC-1 through R-SC-6 and throughout the TPM domain. The SCF's view:

- ESPs (External Service Providers) are extensions of the organization's attack surface
- Traditional yes/no questionnaires provide insufficient insight into actual ESP security posture
- Maturity-based assessment (L0–L5 per control) provides the nuance needed to genuinely evaluate supply chain risk
- The SCF-B (business-level control set) was specifically designed for M&A due diligence

**M&A implications**: A single-framework due diligence engagement (e.g., using only NIST CSF) will provide a partial picture. The SCF-B was built to provide a more complete picture by drawing on: Trust Services Criteria (SOC 2), CIS CSC, COBIT, COSO, CSA CCM, ISO 27002, ISO 31000, NIST 800-160, NIST CSF, OWASP, GDPR, and others.

Areas that directly affect M&A valuations include: non-compliance with statutory obligations, data protection practices, IT asset lifecycle, historical incidents, open risk register items, situational awareness capability, software licensing, BC/DR, IT architecture, and staffing competency.

---

## 10. What This Means for the hc-grc Program

Every research question in hc-grc is ultimately a risk question. Specifically:

**Q: What is the structural coverage of each framework?**  
*Risk translation*: What risks does a program built on this framework actually see, and what risks are invisible to it by design?

**Q: Where do frameworks overlap?**  
*Risk translation*: Where are organizations doing redundant work to address the same underlying risk — work that could be consolidated without increasing exposure?

**Q: Where do frameworks diverge?**  
*Risk translation*: Which risks are framework-specific editorial choices, and which are fundamental properties of control space that should be covered regardless of framework selection?

**Q: Where are the collective gaps?**  
*Risk translation*: Which of the 39 risk categories are systematically underserved across the frameworks under study — representing the exposure that the entire GRC industry, as currently organized, cannot see?

**Q: What structural properties does each framework have?**  
*Risk translation*: Are domain boundaries meaningful risk clusters, or editorial artifacts? Are some domains structurally dense (many controls, strong cross-domain connections) while others are sparse — and what does that mean for the risk posture of organizations that treat all domains as equivalent?

The answers to these questions do not tell any organization what to do. They tell every organization what the foundation of their risk program actually looks like — and where its limits are. That is what a mature risk program requires to operate with honest awareness of its own boundaries.
