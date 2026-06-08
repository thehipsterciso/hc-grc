# Ledger Schema

## What the ledger contains

`ledger/certificates/` — one JSON file per ACCEPT certificate (filename = certificate_id + .json).
`ledger/defects/`      — one JSON file per REJECT record (filename = defect_id + .json).

Both are append-only. Neither is modified after writing; revisions produce new records.

## Certificate linkage

An artifact's `certificate_ref` field is the stem of its certificate filename:

```
artifact.certificate_ref = "cert-S4-control-assets-scf-001"
  → resolves to: ledger/certificates/cert-S4-control-assets-scf-001.json
  → stage_gate.py requires that file to exist and cert.verdict == "ACCEPT"
```

## Self-attestation for adversary-less stages (P0)

P0 has no required adversary disciplines. Its artifacts still require a passing certificate.
The certificate uses the `adversary_block.self_attested: true` branch of the oneOf in
`certificate.schema.json`. The `model_independence_note` must state:
"orchestration artifact; no same-discipline adversary per P0 gate design".

All other stages use the normal adversary block (agent, model, stance, rounds).

## Defect records

error-coordinator writes a defect record to `ledger/defects/` on every REJECT. The artifact's
`revision_history` array references defect records by stem. When the artifact is eventually
accepted, the certificate's `defect_refs` array lists all prior defect record stems, providing
a complete audit trail from first submission through acceptance.
