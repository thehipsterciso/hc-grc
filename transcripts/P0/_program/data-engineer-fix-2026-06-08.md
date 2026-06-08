# Transcript: data-engineer — Schema/Gate/Scripts Remediation
**Date:** 2026-06-08
**Stage:** P0
**Agent:** data-engineer/claude-sonnet-4-6@hc-macbook-pro.local (Tier-1 producer)
**Task:** Fix artifact schema, defect schema, stage_gate.py, capture-transcript scripts, hooks
**Status:** COMPLETED — 12 files modified. PENDING ADVERSARY REVIEW (data-engineer-adversary/claude-opus-4-8@hc-macbook-pro.local).

---

## Files Written

- `registry/schema/artifact.schema.json` — Rebuilt as draft-07. Added all missing fields: `content_hash`, `reproduction`, `transcript_ref`, `question_id`+`null_reason`, `evidence_class` expanded enum, `limitations`, `created_at`, `registry_version`. Adversary field is now a `oneOf` with full review form (agent, model, family, stance) for P1+ and self-attestation form (`self_attested: true`, `reason`) for P0 only. `additionalProperties: false` retained.
- `ledger/schema/defect.schema.json` — `defects` changed from array of strings to array of objects requiring `{category, description, severity}`. `severity` is enum `critical/high/medium/low`. `certificate_id` added (nullable). `resolution_ref` added (nullable). Defect-id convention updated to dot-separated per LEDGER.md.
- `docs/REGISTRY.md` — Full field table replaced with authoritative list matching schema exactly. P0 self-attestation exception section added with example JSON.
- `docs/LEDGER.md` — Defect fields table updated to match new schema. Canonical ledger path `ledger/certificates/{certificate_id}.json` documented explicitly.
- `scripts/stage_gate.py` — `import jsonschema` added. `_load_artifact_schema()` method added. `--validate-artifact` now runs `jsonschema.validate()` after fast pre-check. After verdict check, adversary discipline verified against `required_adversary_disciplines` (skipped for self-attested P0 certs).
- `tests/test_stage_gate.py` — Added 7 tests: `test_certificate_path_construction`, `test_validate_artifact_schema_valid`, `test_validate_artifact_schema_missing_content_hash`, `test_validate_artifact_schema_malformed_git_commit`, `test_adversary_discipline_check_fails`, `test_adversary_discipline_check_passes`, `test_adversary_discipline_check_skipped_for_p0`.
- `requirements-dev.txt` — `jsonschema>=4.22.0` added; `pyyaml` already present.
- `scripts/capture-transcript.sh` — Dead line (line 93) removed. Collision handling added (appends -2, -3, etc.). Stage regex tightened to exact STAGE_GATES.yaml set.
- `scripts/capture-transcript.py` — `validate_stage()` replaced regex with exact set membership. Collision handling added. `import re` removed.
- `scripts/hooks/commit-msg` — Made executable. Contents already correct.
- `.DS_Store` files deleted from `registry/` and `ledger/` directories.

## Files Not Modified (Out of Scope)

- `docs/STAGE_GATES.yaml` — Not in scope; no defects against it.
- `ledger/schema/certificate.schema.json` — Already correct; `adversary_block` oneOf includes `family` field.
- All 6 hook files (`check-agents-generated.sh`, `check-branch-name.sh`, `check-cross-framework-commits.sh`, `validate-registry-schema.py`, `sync-agents.sh`) — Already existed and were executable.

## Definition of Done

1. `artifact.schema.json` valid draft-07, includes all required fields; `adversary.family` present in full review branch; P0 self-attestation branch present.
2. `defect.schema.json` has severity enum, defects as object array with `{category, description, severity}`, `certificate_id` and `resolution_ref` fields present.
3. `stage_gate.py` applies `jsonschema.validate()` in `--validate-artifact`; adversary discipline check present; ledger path is `ledger/certificates/<cert_ref>.json`.
4. All 6 hook scripts exist and are executable.
5. `sync-agents.sh` supports `--dry-run`, exits nonzero on divergence.
6. No `.DS_Store` files in `registry/` or `ledger/`.
7. `test_stage_gate.py` has tests for schema validation, ledger path construction, adversary discipline check.
