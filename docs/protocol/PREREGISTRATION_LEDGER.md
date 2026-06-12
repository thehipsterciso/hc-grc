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
status: pre-lock | draft — content_hash and git_commit_sha are populated at formal commit to pre-registration branch; hashes below are placeholders until that event
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

```
---
type: pre-registration
entry_id: LEDGER-0002
date: 2026-06-11
author: Thomas Jones
rfc3161_tsr: protocol/registration/LEDGER-0002.tsr
status: pre-lock | draft — content_hash and git_commit_sha are populated at formal commit to pre-registration branch; hashes below are placeholders until that event
---

### Summary
Phase 0 model candidate set registration. Locks the embedding model candidate list
required by SAP §10 before Phase 1 runs. Registers two diversity anchors as required
by ADR-0013 and SAP §10. Candidate-level performance evaluation happens in Phase 1
(Phase 1 benchmark evaluation + Phase 2 calibration sample). Selection of the primary
model is a Gate 2 event — this entry only locks who is in the race.

### Details
- artifact: configs/platform.yaml (model_candidates section)
- content_hash: [to be populated at commit time]
- git_commit_sha: [to be populated at commit time]
- registered_by: Thomas Jones

**General-purpose cluster (3 models):**

| Model | HuggingFace ID | Rationale |
|-------|---------------|-----------|
| all-MiniLM-L6-v2 | sentence-transformers/all-MiniLM-L6-v2 | Baseline; widely cited; fast; establishes performance floor |
| BGE-base-en-v1.5 | BAAI/bge-base-en-v1.5 | Strong general-purpose; instruction-aware; well-maintained |
| E5-base-v2 | intfloat/e5-base-v2 | E5 family; instruction-tuned for retrieval and semantic similarity |

**Diversity anchor 1 — legal/regulatory domain fine-tuning:**

| Model | HuggingFace ID | Rationale |
|-------|---------------|-----------|
| Legal-BERT | nlpaueb/legal-bert-base-uncased | Trained on EU legislation, contracts, and court decisions. GRC controls are regulatory artifacts; this model's training distribution is closer to SCF control language than general corpora. Widely cited in legal NLP literature. |

**Diversity anchor 2 — architectural diversity (sparse retrieval):**

| Model | HuggingFace ID | Rationale |
|-------|---------------|-----------|
| SPLADE-v2 Ensemble Distil | naver/splade-cocondenser-ensemble-distil | Sparse learned representation; different architecture class from all dense models above. Captures lexical overlap differently from cosine similarity over dense embeddings. If sparse and dense models agree on STRM divergence, the finding is more robust than dense-only agreement. Runs locally — no SaaS dependency. |

**What this entry does NOT lock:**
- Phase 1 benchmark scores (to be populated during Phase 1)
- Phase 2 calibration sample scores (to be populated before Gate 2)
- Primary model designation (Gate 2 event — not decided here)
- DIVERGENCE-01 operationalization (Gate 2 prerequisite — decided after EDA)

**Phase 1 may not run without both diversity anchors present in the candidate set.**
Any change to this candidate list requires a LEDGER protocol-revision entry before
Phase 1 begins.

### Dissent
null
```

---

```
---
type: pre-registration
entry_id: LEDGER-0003
date: 2026-06-11
author: Thomas Jones
rfc3161_tsr: protocol/registration/LEDGER-0003.tsr
status: pre-lock | draft — content_hash and git_commit_sha are populated at formal commit to pre-registration branch; hashes below are placeholders until that event
---

### Summary
Fleiss kappa path selection per SAP §12. SAP §12 specifies two paths for estimating
STRM inter-rater reliability: (1) recruit GRC domain expert raters before Gate 1 as a
prerequisite; (2) acknowledge that STRM reliability is unestimated and close the
interpretation pathway that requires reliability evidence. This entry selects and locks
Path 2 before Phase 1 begins.

### Details
- artifact: docs/protocol/03_statistical_analysis_plan.md (Section 12, STRM
  Inter-Rater Reliability subsection)
- content_hash: [to be populated at commit time]
- git_commit_sha: [to be populated at commit time]
- registered_by: Thomas Jones

**Decision: Path 2 — Acknowledge unestimated STRM reliability**

Rationale for Path 2 over Path 1:

Rater recruitment for Path 1 requires GRC domain experts willing to independently
re-rate a sample of STRM mapping pairs across the five relationship categories
(⊂ Subset, ⊃ Superset, ∩ Intersection, = Equal To, ∅ No Relation). Recruiting
qualified raters requires either (a) formal institutional collaboration not yet
established, or (b) compensated expert review with associated cost and timeline
implications that are out of scope for Phase 0. Neither is available pre-publication.

Path 2 is not a methodological concession — it is the correct pre-publication path.
The SCF corpus itself provides STRM-asserted relationship pairs usable as weak
supervision anchors (LEDGER-0002 model candidates evaluated against = Equal To and
∅ No Relation pairs). Rater recruitment is designated a post-publication community
contribution milestone per SAP §12.

**Consequences of Path 2 (locked here, disclosed in all publications):**
- STRM reliability is unestimated in this study
- Interpretation pathway: "model-STRM divergence explained by annotator inconsistency
  vs. systematic annotation error" is UNAVAILABLE
- Available interpretation: "divergence between computational similarity and STRM labels
  exists and is quantified; attribution to annotation error vs. semantic disagreement
  requires future reliability estimation"
- This limitation appears in SAP §12 and in the methods section of all publications

**DIVERGENCE-01 note:** Operationalization of model-STRM divergence (DIVERGENCE-01
open decision, SAP §10) is a Gate 2 prerequisite, not a Gate 1 prerequisite. It
requires knowing the STRM label distribution from exploratory analysis. Selection is
deferred to post-EDA, pre-Gate 2. It is NOT logged in this entry.

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
