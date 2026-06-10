# Incidents

**Type:** Append-only. No entry is ever modified or deleted after commitment.
**Purpose:** Institutional memory for every documented failure — agent timeouts, schema violations, guardrail triggers, gate rejections that caused protocol revisions, hallucinated citations caught at review, data integrity violations, unexpected analysis failures. If it broke, it goes here.

The Sakana AI Scientist platform (Beel et al. 2025, arXiv 2502.14297) failed reproducibility review in part because there was no institutional memory for failures. 57% of manuscripts contained hallucinated results; 42% of experiments failed silently. Both categories were discovered only because someone read the outputs carefully. This document is the HC-GRC mitigation: every failure that anyone encounters — agent or human — gets written down, once, in the same place.

---

## Entry Format

```
---
incident_id: INC-NNNN
date: YYYY-MM-DD
severity: critical | high | medium | low
status: open | resolved | monitoring
detected_by: [agent name | human name]
affected_agents: [list]
run_manifest_ref: [run_id or null]
---

### Summary
[One paragraph. What broke. When. What the observable symptom was.]

### Detection
[How was this found? Automated check, human review, guardrail trigger, etc.]

### Response
[What was done immediately after detection.]

### Root Cause
[What actually caused this. Not the symptom — the cause.]

### Contributing Factors
[What conditions made this failure possible or harder to catch.]

### Action Items
| Item | Owner | Status | Due |
|------|-------|--------|-----|
| | | | |

### Ledger Reference
[LEDGER entry ID if this incident affected the protocol. null otherwise.]
```

---

## Severity Definitions

| Severity | Definition |
|----------|-----------|
| Critical | Data integrity violation, SAP violation, test split accessed before Gate 2, secrets exposed, hallucinated finding passed QA review |
| High | Agent producing incorrect outputs that passed guardrails, gate decision without rationale, pre-registration timestamp failure |
| Medium | Agent timeout requiring manual restart, schema validation failure, unexpected null result requiring investigation |
| Low | Documentation drift, minor formatting failure, recoverable pipeline stall |

---

## Incident Log

*Append new entries below. Do not modify existing entries.*

*(No incidents recorded — platform pre-launch)*
