# Transcript: mlops-engineer — CI/Reproducibility Remediation
**Date:** 2026-06-08
**Stage:** P0
**Agent:** mlops-engineer (Tier-1 producer)
**Task:** Fix CI workflows, Dockerfile, Makefile, branch protection
**Status:** COMPLETED — 13 files modified. PENDING ADVERSARY REVIEW (ml-engineer-adversary).

---

## Files Written

- `.github/workflows/certificate-completeness.yml` — Added `pull_request_target` on `main` triggering `validate-all-for-main` job; both jobs install `requirements-dev.txt`.
- `.github/workflows/provenance-integrity.yml` — P0 self-attestation exception: skip adversary checks when `adversary` is null AND `self_attested: true`; otherwise require non-empty model and family; comment explains P0 exception.
- `.github/workflows/registry-validate.yml` — Certificate ref resolves to `ledger/certificates/{cert_ref}.json`; hard-fails when directory missing or file absent; silent bypass removed.
- `.github/workflows/repro-smoke.yml` — Added stage/framework branch triggers.
- `.github/workflows/prereg-freeze-guard.yml` — Rewrote: added push trigger; recomputes sha256sum and compares to frozen value; fails with exact required error message.
- `.github/workflows/independence-lint.yml` — Parse errors recorded as violations and exit non-zero; Rule 2 uses dependency graph (dep resolves to a registered artifact at stage S5) not string matching.
- `.github/workflows/pin-docker-digest.yml` — New manual `workflow_dispatch` workflow that pulls, inspects digest, opens PR pinning Dockerfile.
- `.github/workflows/python-quality.yml` — Installs `requirements-dev.txt` only.
- `repro/Dockerfile` — Explicit pinning instructions; `--no-cache-dir` on pip install; uses `requirements-dev.txt` explicitly.
- `Makefile` — Smoke target captures stdout; sha256-compares to `expected_output.sha256`; exits non-zero with clear message on mismatch.
- `docs/CI.md` — Certificate-completeness added to main required checks; ledger path corrected; branch protection script referenced as enforcement mechanism.
- `docs/REPRODUCIBILITY.md` — Added Dockerfile digest pinning section describing pinning process and the pin-docker-digest workflow.
- `scripts/setup-branch-protection.sh` — New bash script using gh CLI; configures all 9 required status checks on main; stage-gate on framework branches; minimum checks on all branches; `--dry-run` flag prints without applying.

## Files Not Modified (Out of Scope)

- `scripts/stage_gate.py` — `--validate-all` flag required but script is out of scope for this run; must be updated separately.
- `registry/schema/artifact.schema.json` — Schema being fixed in parallel; workflow fix is consistent with that change.
- `requirements-dev.txt` — `pyyaml` already present; `jsonschema>=4.22.0` added by parallel data-engineer run.

## Definition of Done

1. `certificate-completeness` triggers on PRs to main via `pull_request_target`; runs `--validate-all`.
2. `provenance-integrity` skips adversary checks when `adversary` is null AND `self_attested: true`; otherwise requires non-empty model and family.
3. `registry-validate` resolves to `ledger/certificates/{cert_ref}.json`; fails loudly when directory missing or file absent.
4. Dockerfile has `--no-cache-dir`; uses `requirements-dev.txt`; `pin-docker-digest.yml` workflow exists; `REPRODUCIBILITY.md` describes the process.
5. `make smoke` computes sha256, compares to `repro/smoke/expected_output.sha256`, exits non-zero with clear message on mismatch.
6. `prereg-freeze-guard` has push trigger; recomputes and compares content hash when hash file exists; correct failure message.
7. `scripts/setup-branch-protection.sh` exists; executable; configures all 9 CI workflows as required checks on main; `--dry-run` flag; CI.md references it.
8. `independence-lint` fails on parse errors; Rule 2 checks actual S5-stage artifact presence in registry.
9. `repro-smoke` triggers on PRs to `stage/*`, `scf/*`, `nist-800-53/*`, `nist-csf-2.0/*`, `nist-800-171/*`, `cis-v8/*` in addition to main and nightly.
10. All CI Python jobs install `requirements-dev.txt`; `requirements.txt` fallback removed.
