# Pre-registration Ledger

**Type:** Append-only. No entry is ever modified or deleted after commitment.
**Backing:** This file is committed to the `pre-registration` protected branch. The branch has no force-push and no history-rewriting permitted.
**Timestamps:** Every entry requiring a timestamp uses RFC 3161 via a trusted timestamp authority. The `.tsr` file is stored in `protocol/registration/` alongside this document.

This ledger is the single document a journal reviewer, audit committee, or Adversarial Protocol arbiter would request first. It must be complete, current, and honest — including gate rejections, protocol revisions, and anything that did not go according to plan.

---

## Entry Format

```
---
type: [pre-registration | gate-decision | protocol-revision | incident-ref | sap-amendment]
entry_id: LEDGER-NNNN
date: YYYY-MM-DD
author: [human name | orchestrator]
rfc3161_tsr: protocol/registration/LEDGER-NNNN.tsr
---

### Summary
[One paragraph. What happened. What was decided. Why.]

### Details
[Required fields per entry type — see below.]

### Dissent
[Null if none. Text if present. Required field — never omit.]
```

---

## Entry Types and Required Fields

### `pre-registration`
Records a locked protocol artifact being committed to the pre-registration branch.

Required fields:
- `artifact`: filename and path
- `git_commit_sha`: commit SHA on pre-registration branch
- `rfc3161_tsr`: path to timestamp file
- `content_hash`: SHA-256 of the artifact at time of registration
- `registered_by`: human reviewer name

### `gate-decision`
Records a human approval gate decision.

Required fields:
- `gate_id`: gate-1 through gate-5
- `outcome`: approved | rejected | deferred
- `reviewer`: human reviewer name
- `rationale`: minimum 20 words describing the specific basis for the decision
- `dissent`: null | text
- `run_manifest_ref`: run_id of the pipeline run triggering the gate
- `rfc3161_tsr`: path to timestamp file

### `protocol-revision`
Records any change to a locked protocol document after initial pre-registration.

Required fields:
- `revised_artifact`: filename and path
- `previous_version_hash`: SHA-256 of the artifact before revision
- `new_version_hash`: SHA-256 of the artifact after revision
- `revision_rationale`: minimum 50 words explaining why the revision was necessary
- `affects_pre_registered_analysis`: true | false
- `approved_by`: human reviewer name

Protocol revisions affecting pre-registered analysis require a new `pre-registration` entry for the revised artifact.

### `sap-amendment`
Records an addition to the SAP after initial lock. Pre-SAP-lock additions are standard; post-SAP-lock amendments are exceptional and must justify why the amendment is not a SAP violation.

Required fields:
- `amendment_type`: pre-lock-addition | post-lock-exception
- `hypothesis_ids_added`: list of new H[module].[n] IDs
- `justification`: if `post-lock-exception`, minimum 100 words justifying why this is not a SAP violation
- `approved_by`: human reviewer name
- `affects_exploratory_data`: true | false

### `incident-ref`
Cross-reference to an entry in INCIDENTS.md that affected the protocol.

Required fields:
- `incident_id`: INC-NNNN from INCIDENTS.md
- `protocol_impact`: how the incident affected the research protocol
- `resolution`: what was done

---

## Ledger Entries

*This section is append-only. New entries are added below the most recent entry. Entries are never deleted, moved, or modified after commitment.*

---

```
---
type: pre-registration
entry_id: LEDGER-0001
date: 2026-06-09
author: Thomas Jones
rfc3161_tsr: protocol/registration/LEDGER-0001.tsr
---

### Summary
Framework-level pre-registration. Locks platform-scope research questions, theoretical framework, and methods scaffolding prior to data acquisition and exploratory analysis. Specific hypotheses (H[module].[n]) and the full SAP are deferred until after exploratory characterization — this is an explicit design choice documented in the methods scaffolding.

### Details
- artifact: protocol/00_research_questions.md
- content_hash: [to be populated at commit time]
- artifact: protocol/01_theoretical_framework.md
- content_hash: [to be populated at commit time]
- artifact: protocol/04_methods_scaffolding.md
- content_hash: [to be populated at commit time]
- git_commit_sha: [to be populated at commit time]
- rfc3161_tsr: protocol/registration/LEDGER-0001.tsr
- registered_by: Thomas Jones

### Dissent
null
```

---

## RFC 3161 Timestamp Procedure

1. Lock the artifact (commit to pre-registration branch — no further modification)
2. Request timestamp: `openssl ts -query -data <artifact> -no_nonce -sha256 -cert > request.tsq`
3. Submit to TSA: `curl -H "Content-Type: application/timestamp-query" --data-binary @request.tsq https://freetsa.org/tsr > LEDGER-NNNN.tsr`
4. Verify: `openssl ts -verify -in LEDGER-NNNN.tsr -queryfile request.tsq -CAfile cacert.pem`
5. Store `.tsr` in `protocol/registration/` and commit alongside the ledger entry

The FreeTSA authority (https://freetsa.org) is the default TSA. The Orchestrator automates steps 2–5. Step 1 (locking the artifact via commit) is a human action.

---

## Integrity Check

To verify the ledger has not been modified since a given entry:

```bash
# Verify a specific TSR file
openssl ts -verify \
  -in protocol/registration/LEDGER-NNNN.tsr \
  -data protocol/00_research_questions.md \
  -CAfile protocol/registration/cacert.pem
```

The pre-registration branch's Git history is itself an integrity record. `git log --follow protocol/PREREGISTRATION_LEDGER.md` shows every commit that touched the ledger. Any commit that modifies a prior entry (not appends a new one) is a protocol violation.
