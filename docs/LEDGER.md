# hc-grc — Ledger

**Version:** 1.0
**Date:** 2026-06-08

The ledger is the program's append-only provenance record. It holds every certificate issued by a
Tier-2 adversary and every defect record raised during rejection rounds. Nothing is deleted from
the ledger. The ledger is what `error-coordinator` maintains and what makes the program's acceptance
history auditable.

---

## Structure

```
ledger/
  schema/
    certificate.schema.json     JSON Schema for certificate records
    defect.schema.json          JSON Schema for defect records
  certificates/                 one file per passing certificate (<certificate_id>.json)
  defects/                      one file per rejection round (<defect_id>.json)
```

**Canonical ledger certificate path:** `ledger/certificates/{certificate_id}.json`

This is the path that `context-manager`, `stage_gate.py`, and all consumers must use when
resolving a `certificate_ref` from a registry entry. The stem of the filename is the
`certificate_id`; the full path is always `ledger/certificates/<certificate_ref>.json`. Any code
that constructs a different path (e.g. `ledger/<cert>.json` without the `certificates/`
subdirectory) is incorrect and will cause stage gate failures.

Rejection-round certificates (verdict `REJECT`) are stored as defect records under `ledger/defects/`,
not as certificate files. A file in `ledger/certificates/` with `verdict: REJECT` will cause the
stage gate to fail — that directory holds only ACCEPT records.

---

## The certificate flow

Every artifact travels this path before it can be registered:

```
producer (Tier 1, sonnet)
    |
    | artifact + Definition of Done
    v
same-discipline adversary (Tier 2, opus, rotating stance)
    |
    |-- precondition check
    |-- discipline-specific reject checklist
    |-- stance protocol
    |-- two-axis gate (completeness + quality)
    |
    +-- ACCEPT --> certificate written to ledger/certificates/
    |              context-manager registers the artifact
    |
    +-- REJECT --> defect record written to ledger/defects/
                   producer revises
                   re-audit (same adversary, same stance)
                   repeat until ACCEPT or deadlock
                           |
                        deadlock after N rounds (default 3)
                           |
                        ARBITER (3rd instance, fresh context, different model)
                           |
                        still unresolved --> human tripwire
```

The adversary's stance rotates across the five options (`independent-reconstruction`,
`falsification-probe`, `competing-hypotheses`, `assumption-ledger`, `premortem`) so that no
artifact is hit from the same angle twice across its revision rounds. The stance applied in each
round is recorded on both the defect record and the final certificate.

---

## Certificate fields

Defined in `ledger/schema/certificate.schema.json`. Key fields:

| Field | Purpose |
|---|---|
| `certificate_id` | Primary key. The stem of the file under `ledger/certificates/`. Must equal `certificate_ref` in the corresponding registry entry. |
| `artifact_id` | The artifact this certificate covers. |
| `verdict` | `ACCEPT` or `REJECT`. Only ACCEPT certificates are stored under `ledger/certificates/`. |
| `producer` | `{agent, model}` — the Tier-1 identity. |
| `adversary` | `{agent, model, family}` — the Tier-2 identity. `family` is always `anthropic`; it is explicit so the single-family limitation appears in every record. |
| `stance` | Rotating review stance the adversary applied. |
| `rounds` | Number of audit rounds before this verdict. 1 means first-round accept. |
| `completeness_verdict` | Whether the artifact covers all required elements of its Definition of Done. |
| `quality_verdict` | Whether the artifact meets the methodological quality bar for the stage. |
| `residual_limitations` | Limitations that survive acceptance. For finding artifacts that feed synthesis, must include: "Model independence: tier-level diversity only (Anthropic sonnet/opus); cross-framework replication (S9) is the structural robustness check." |
| `arbiter` | `{used, agent, model}` — arbiter escalation record. Null fields when not invoked. |
| `human_tripwire` | `{required, tripwire_id, signed_by, signed_at}` — human-signature record for gated stages (T1-T5). |
| `revision_diffs` | Ordered list of `defect_id`s raised and resolved during this certification cycle. Empty for first-round accepts. |
| `timestamp` | When the certificate was issued. |
| `git_commit` | 40-char SHA-1 at certification time. Must match the artifact's `git_commit`. |

---

## Defect records

A defect record is written by `error-coordinator` every time a Tier-2 adversary issues a REJECT.
It is the authoritative log of what was wrong and what the producer must fix.

Defined in `ledger/schema/defect.schema.json`. Key fields:

| Field | Purpose |
|---|---|
| `defect_id` | Primary key. Convention: `defect.<artifact_id>.r<round>` (dot-separated). Stem of the file under `ledger/defects/`. |
| `artifact_id` | The artifact that was rejected. |
| `certificate_id` | The `certificate_id` of the rejection-round certificate this defect record corresponds to. Null if no separate certificate record was issued for the rejection. |
| `round` | The review round number (1-indexed). If this equals the stage's `max_rounds` (default 3), the arbiter must be invoked. |
| `adversary` | `{agent, model, stance}` — the Tier-2 identity and stance at time of rejection. |
| `defects` | Array of `{category, description, severity}` objects. Each defect must be specific enough for the producer to know exactly what to revise. `category` is a string label (e.g. `missing-field`, `schema-violation`, `methodology`). `description` is the actionable text (min 10 chars). `severity` is one of `critical`, `high`, `medium`, `low`. |
| `resolution_ref` | Path or reference to the revised artifact, populated once the producer submits a revision. Null until resolution is submitted. |
| `timestamp` | When the rejection was issued. |

Defect records are never deleted or modified after creation. If a subsequent revision fails, a new
defect record is written for that round. The chain of defect records for a given `artifact_id`
is the complete revision history.

---

## What error-coordinator maintains

`error-coordinator` is the sole writer to both `ledger/certificates/` and `ledger/defects/`. Its
responsibilities:

1. **Receive adversary verdicts.** When a Tier-2 adversary issues a verdict, the coordinator
   receives it with the full review payload.

2. **On REJECT:** Write a defect record to `ledger/defects/<defect_id>.json`. Notify the producer
   via the coordinator with the `defect_id` and the specific defect list. Track the round count.

3. **On ACCEPT:** Write the certificate to `ledger/certificates/<certificate_id>.json`. Notify
   `context-manager` that the artifact is cleared for registration, passing the `certificate_id`.

4. **On deadlock:** When round count hits `max_rounds` without ACCEPT, escalate to the arbiter.
   Record the arbiter's identity and model on the certificate. If the arbiter cannot resolve, flag
   for human tripwire.

5. **On human tripwire:** Write a partial certificate with `human_tripwire.required: true` and
   `signed_by: null`. Hold the artifact. When the human signs, update `signed_by` and `signed_at`,
   then release the artifact for registration.

6. **Audit log queries.** Any agent may query `error-coordinator` for the certification history of
   an artifact or stage. The ledger is the answer.

---

## Append-only enforcement

The ledger is the provenance record. Files in `ledger/certificates/` and `ledger/defects/` are
written once and never modified. This is enforced by:

- `error-coordinator` only creates files in these directories, never overwrites.
- The git history of `ledger/` is the audit log. Any modification to an existing ledger file
  appears as a diff and is treated as a provenance violation.
- The `certificate_id` and `defect_id` naming conventions embed the artifact and round, making
  accidental collision detectable.

If a certificate needs correction (e.g. a wrong timestamp), a new certificate is issued with a
suffix indicating the correction (e.g. `cert.<artifact_id>.v2`) and the original is retained.
The registry entry is updated to reference the corrected certificate; the original remains in
the ledger.

---

## Relationship to the registry

The ledger and registry are two views of the same provenance record:

- The **ledger** is the full history — every round, every defect, every revision, every verdict.
  It is append-only and never trimmed.
- The **registry** is the accepted-artifacts index — only what passed, with a pointer back to the
  certificate. It is the surface downstream agents query.

The link between them is `certificate_ref` in the registry entry and `artifact_id` in the
certificate. Together they form a closed loop: a registry entry can always be traced to its
certificate, and a certificate can always be traced to the artifact it covers.

No artifact appears in the registry without a corresponding ACCEPT certificate in the ledger.
No ACCEPT certificate in the ledger is unlinked — every one maps to exactly one registry entry.
