# Registry Schema

## What a registry entry is

A registry entry is a JSON object satisfying `artifact.schema.json` that records a single
certified artifact. context-manager writes exactly one entry per artifact, and only after the
artifact carries a passing certificate. The entry records full provenance: who produced it, what
model, which adversary certified it, which stance was applied, the git commit at registration,
the source version consumed, and the full revision history of any prior rejection rounds.

## Required fields (gate-enforced by stage_gate.py)

`artifact_id`, `artifact_type`, `stage_id`, `certificate_ref`

`stage_gate.py --validate-artifact` enforces these four fields only. The remaining provenance
fields (producer, adversary, git_commit, source_version, depends_on, revision_history) are
enforced by this schema, not by the gate script. See "Provenance gap" below.

## The certificate_ref linkage

`certificate_ref` is the filename stem of the certificate under `ledger/certificates/`:

```
artifact.certificate_ref = "cert-P0-orchestration-harness-001"
  → resolves to: ledger/certificates/cert-P0-orchestration-harness-001.json
  → stage_gate.py loads that file and checks cert.verdict == "ACCEPT"
```

## Adversary-less self-attestation for P0

Stage P0 has `required_adversary_disciplines: []` in STAGE_GATES.yaml — orchestration artifacts
have no same-discipline adversary by gate design. The gate still requires every registered
artifact to carry a passing certificate. For P0 artifacts, the certificate uses the
`self_attested: true` form (see `ledger/schema/certificate.schema.json`, `adversary_block`
oneOf branch 2). In the artifact entry, `adversary` may be null.

## Provenance gap (coordinator must be aware)

`git_commit` is required by CLAUDE.md hard constraint #8 and enforced by this schema, but
stage_gate.py `--validate-artifact` does NOT check it. Artifact registration without a valid
git commit will pass the gate script but fail schema validation. The first valid git_commit
is available only after the repo's initial commit; do not register artifacts before that commit.
