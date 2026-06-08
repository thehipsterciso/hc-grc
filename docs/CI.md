# CI — Workflow Reference

Nine GitHub Actions workflows gate the hc-grc program. This document is the operational reference:
what each workflow gates, what triggers it, what a failure means, how to fix it, and which branch
protection rules require it.

---

## Workflow index

| Workflow | File | Triggers | Branch-protection required |
|---|---|---|---|
| registry-validate | `registry-validate.yml` | push, PR (all branches) | all branches |
| certificate-completeness | `certificate-completeness.yml` | PR to stage/framework/synthesis branches; PR to main | stage/scf/nist-*/cis-*/synthesis branches **and main** |
| provenance-integrity | `provenance-integrity.yml` | push, PR (all branches) | all branches |
| independence-lint | `independence-lint.yml` | PR (all branches) | all branches |
| prereg-freeze-guard | `prereg-freeze-guard.yml` | PR touching PREREGISTRATION.md | all branches |
| repro-smoke | `repro-smoke.yml` | PR to main, nightly 2am UTC | main |
| python-quality | `python-quality.yml` | push, PR (all branches) | all branches |
| lint-docs | `lint-docs.yml` | PR (all branches) | all branches |
| agent-sync-check | `agent-sync-check.yml` | PR touching agents/ or submodule | all branches |

---

## registry-validate

**What it gates:** Every changed registry JSON file is syntactically valid and schema-complete.
Catches missing required fields, orphaned certificate references, and dangling transcript references
before they enter the branch.

**Triggers:** Every push and every PR on any branch.

**Failure means:**
- `malformed JSON` — the file cannot be parsed. Open it and fix the syntax error at the indicated
  line/column.
- `schema error` — a required field is missing or has the wrong type. Compare against
  `registry/schema/artifact.schema.json` and add/correct the field.
- `certificate_ref present but no corresponding ledger entry` — the artifact claims a certificate
  that does not exist at `ledger/certificates/{certificate_ref}.json`. Either the file was not
  committed, the `certificate_ref` value is wrong, or `ledger/certificates/` does not exist yet.
  Create the directory, commit the certificate file, or correct the ref. Note: a missing
  `ledger/certificates/` directory is a hard failure, not a skip.
- `transcript_ref file does not exist` — the path in `transcript_ref` is not in the repo. Either
  commit the transcript file or remove the field if the transcript is not yet produced.

**How to fix:** Run the validation locally:
```
python scripts/validate_registry.py  # if the script exists, or:
python -c "
import json, jsonschema, pathlib
schema = json.load(open('registry/schema/artifact.schema.json'))
for f in pathlib.Path('registry').rglob('*.json'):
    if 'schema' not in str(f) and 'ledger' not in str(f):
        jsonschema.validate(json.load(open(f)), schema)
        print(f'OK: {f}')
"
```

---

## certificate-completeness

**What it gates:** Before a stage branch merges, every artifact required for that stage has a
passing adversary certificate. This is the merge gate enforcing the hard constraint: nothing enters
the registry without a passing certificate.

**Triggers:** Two distinct trigger blocks:

1. PR targeting `stage/*`, `scf/*`, `nist-800-53/*`, `nist-csf-2.0/*`, `nist-800-171/*`,
   `cis-v8/*`, `synthesis/*` — runs `stage_gate.py --stage <derived-stage>` for the specific stage.
2. PR targeting `main` — runs `stage_gate.py --validate-all` to re-validate all registered
   artifacts across all stages before the final merge. This ensures main is never left in a state
   where certificates are incomplete or stale.

**Stage is derived from the branch name** (trigger 1 only). Branch `scf/s4-corpus-construction` →
stage `s4`. Branch `synthesis/x3-insight-map` → stage `x3`. Branch `stage/s7-nist-csf` → stage `s7`.

**Failure means:** `scripts/stage_gate.py` exited non-zero for the derived stage. One or more
artifacts required for that stage are either unregistered or registered without a passing
certificate.

**How to fix:**
1. Run `python scripts/stage_gate.py --stage <stage>` locally to see which artifacts are missing
   or uncertified.
2. Ensure the producer/adversary loop is complete and `context-manager` has registered the artifact
   with an attached certificate.
3. Verify the ledger entry exists in `registry/ledger/`.

**Note:** This check is intentionally strict. A conditional approval (adversary passes with
reservations pending future fixes) is not sufficient — the artifact must be fully certified.

---

## provenance-integrity

**What it gates:** Every registered artifact has complete provenance: named models, declared
adversary family, a git commit hash, and valid `depends_on` references. Also enforces that Tier-A
stages do not carry cross-framework dependencies.

**Triggers:** Every push and every PR on any branch.

**Failure means:**
- `producer.model is missing` — fill in the model identifier (e.g. `claude-sonnet-4-6`).
- `adversary.model is missing` — fill in the adversary model (default: `opus`).
- `adversary.family is missing` — declare the model family even if same as producer (honest
  declaration required by the program's hard constraints).
- `git_commit field is missing` — add the commit SHA at which the artifact was produced. Use
  `git rev-parse HEAD`.
- `depends_on references unregistered artifact_id` — the referenced artifact must be registered
  before this one can reference it. Register the dependency first, or correct the artifact_id.
- `cross-framework dependency in Tier-A stage` — a Tier-A stage artifact (S1f–S9) has
  `depends_on` referencing an artifact from a different framework. This violates per-framework
  independence. Either remove the cross-framework dependency or move this artifact to a Tier-B
  stage (X1–X5).

**How to fix:** Inspect the error message — it names the specific field and file. Edit the registry
JSON to supply the missing or incorrect value.

---

## independence-lint

**What it gates:** Three independence rules that protect the integrity of cross-framework evidence
classification:

1. **S7/S8f independence** — artifacts in the investigations (S7) and within-framework
   triangulation (S8f) stages must not depend on artifacts from a different framework. Mixing
   frameworks at these stages would corrupt the independence assumption that makes Tier B meaningful.
2. **Embedding correlation disclosure** — any two artifacts both classified `intrinsic` or `robust`
   that share an embedding `depends_on` must each declare that correlation in `limitations`.
   Failing to declare it allows correlated evidence to be called independent.
3. **Valid rotating stance** — the `stance` field, when present, must be one of:
   `independent-reconstruction`, `falsification-probe`, `competing-hypotheses`,
   `assumption-ledger`, `premortem`.

**Triggers:** Every PR on any branch.

**Failure means:**
- `INDEPENDENCE_VIOLATION` — remove the cross-framework `depends_on` entry from the S7/S8f
  artifact. If the dependency is genuinely needed, restructure it as a Tier-B artifact.
- `CORRELATION_UNDECLARED` — add a `limitations` entry to the artifact (and its sibling) declaring
  that the finding shares an embedding with correlated studies. E.g.:
  `"Finding shares embedding artifact X with studies Y and Z; these are not independent replications."`
- `INVALID_STANCE` — correct the `stance` field to one of the five valid values.

---

## prereg-freeze-guard

**What it gates:** Modifications to `docs/PREREGISTRATION.md` after tripwire T1 has been signed.
Post-hoc changes to the pre-registration would violate the no-post-hoc-thresholds constraint and
corrupt the entire program's epistemic integrity.

**Triggers:** Any PR that touches `docs/PREREGISTRATION.md`.

**How the freeze works:** When a human signs T1, they run:
```
sha256sum docs/PREREGISTRATION.md > docs/PREREGISTRATION.md.sha256
git add docs/PREREGISTRATION.md.sha256
git commit -m "freeze: T1 pre-registration signed"
```
Once that file exists, this workflow blocks all further changes.

**Failure means:** `docs/PREREGISTRATION.md.sha256` exists and the PR does not carry the label
`tripwire-override`. The pre-registration is frozen.

**How to fix (legitimate amendment):**
1. Get explicit human sign-off that the amendment is warranted.
2. Add the label `tripwire-override` to the PR (must be done by a human with write access).
3. Re-run the check.
4. After merging, update `docs/PREREGISTRATION.md.sha256` to the new hash and commit with a note
   explaining why the amendment was permitted.

Do not automate around this gate. Its entire purpose is to require a human decision.

---

## repro-smoke

**What it gates:** The P0 exit criterion — the autonomy harness can (a) run a trivial task
reproducibly and (b) self-reject a seeded-bad artifact. This is the baseline the whole program
depends on.

**Triggers:** Every PR to `main`; nightly at 2am UTC.

**Two sub-tests:**

1. **Trivial task** — `repro/smoke/run_trivial.sh` runs inside the container and produces stdout.
   That stdout is sha256-summed and compared against `repro/smoke/expected_output.sha256`. Byte
   mismatch means the container is not producing identical output across runs (non-determinism or
   environment drift).

2. **Bad artifact rejection** — `repro/smoke/run_bad_artifact.sh` submits a deliberately malformed
   artifact to `scripts/stage_gate.py`. The test asserts non-zero exit. If stage_gate.py exits 0,
   the gate is broken and the program has no self-rejection capability.

**Failure means:**

- Trivial task mismatch: the container environment has drifted. Rebuild from the pinned Dockerfile
  (`FROM python:3.11-slim@sha256:<digest>`). If the base image digest has changed, update and
  re-pin it, then recompute `expected_output.sha256` by running the container locally:
  ```
  docker build -t hc-grc-repro repro/
  docker run --rm hc-grc-repro bash repro/smoke/run_trivial.sh | sha256sum
  # Update repro/smoke/expected_output.sha256 with the new hash
  ```
- Bad artifact accepted: `scripts/stage_gate.py` has a logic regression. Fix the validation logic
  so it rejects artifacts missing required fields (`certificate_ref`, `adversary.model`,
  `git_commit`).

**Nightly failure** on the schedule trigger (not PR-triggered) means the container or stage gate
has regressed since the last merge. Investigate before the next working day.

---

## python-quality

**What it gates:** Code quality and test correctness. Ruff lint, black formatting (100-char line
length), and pytest with no network access.

**Triggers:** Every push and every PR on any branch.

**Failure means:**
- `ruff` error — fix the lint issue. Common: unused imports, undefined names, complexity.
  `ruff check --fix .` handles auto-fixable issues.
- `black --check` failure — run `black --line-length 100 .` to reformat, then commit the result.
- `pytest` failure — a test is broken. Run `pytest tests/ -x --tb=long` locally. External calls
  must be mocked — if a test is reaching the network, add the appropriate mock.

**Note on network isolation:** The workflow sets `no_proxy=*` to block network. If a test fails
only in CI with a connection error, it is making a real network call that needs to be mocked.

---

## lint-docs

**What it gates:** Two things:

1. **Required files exist and are non-stub.** The following files must be present and contain more
   than a single title line: `docs/BRANCHING.md`, `docs/REGISTRY.md`, `docs/LEDGER.md`,
   `docs/REPRODUCIBILITY.md`, `docs/CI.md`, `docs/STAGE_GATES.yaml`, `Makefile`.
2. **Internal markdown links in changed `.md` files are not broken.** External HTTP links are not
   checked (no network in CI).

**Triggers:** Every PR on any branch.

**Failure means:**
- `MISSING` — create the file. See `frameworks/_TEMPLATE/` for scaffold patterns.
- `EMPTY` — the file exists but has no content. Add substantive content.
- `STUB (title-only)` — the file has only a title line. Fill it in.
- `broken internal link` — a relative link in a changed `.md` file points to a path that does not
  exist. Correct the path or create the linked file.

---

## agent-sync-check

**What it gates:** `.claude/agents/` stays in sync with the program roster as defined in
`scripts/sync-agents.sh`. Prevents stale, missing, or extraneous agents from being silently
loaded by Claude Code.

**Triggers:** Any PR touching `agents/`, `.gitmodules`, or `upstream/`.

**Failure means:** `scripts/sync-agents.sh --dry-run` detected that the current `.claude/agents/`
does not match what sync would produce. Either agents were added/removed from the roster in
`sync-agents.sh` without regenerating, or files in `.claude/agents/` were manually edited.

**How to fix:**
```
bash scripts/sync-agents.sh
git add .claude/agents/
git commit -m "chore: regenerate .claude/agents/ from sync-agents.sh"
```

If agents are missing from the submodule (`MISSING from submodule: <name>`), update the submodule:
```
git submodule update --remote upstream/awesome-claude-code-subagents
# Verify the agent file now exists, then re-run sync
bash scripts/sync-agents.sh
```

---

## Branch protection configuration

Configure the following required status checks in GitHub repository settings under
Settings → Branches → Branch protection rules:

**For `main`:**
- `registry-validate / validate`
- `provenance-integrity / provenance`
- `independence-lint / independence`
- `python-quality / quality`
- `lint-docs / required-docs`
- `lint-docs / markdown-links`
- `repro-smoke / smoke`
- `certificate-completeness / validate-all-for-main`

**For `stage/*`, `scf/*`, `nist-800-53/*`, `nist-csf-2.0/*`, `nist-800-171/*`, `cis-v8/*`,
`synthesis/*`:**
- All checks required for `main`, plus:
- `certificate-completeness / stage-gate`

**For all branches (including feature branches):**
- `registry-validate / validate`
- `provenance-integrity / provenance`
- `python-quality / quality`

Set "Require branches to be up to date before merging" on `main` and all stage branches.

**Enforcement:** Branch protection rules are applied programmatically by `scripts/setup-branch-protection.sh`,
which uses the `gh` CLI to configure all required status checks, PR review requirements, and direct-push
blocks. Run it once after the repository is created:

```bash
bash scripts/setup-branch-protection.sh --dry-run  # review what will be configured
bash scripts/setup-branch-protection.sh            # apply
```

The script requires admin access to the repository. The documentation above and the script are the
single source of truth — if they diverge, the script takes precedence (it is what GitHub actually
enforces).

---

## Common patterns and quick fixes

**A PR fails multiple checks at once after adding a new registry entry:**
Start with `registry-validate` — if the JSON is malformed, all other checks will also error on it.
Fix schema errors first.

**A PR fails `provenance-integrity` with `depends_on references unregistered artifact_id`:**
The dependency must be registered in a prior commit or in the same PR. Check that the dependency
JSON file exists in `registry/` and has the correct `artifact_id` value matching exactly what you
referenced.

**`certificate-completeness` fails on a stage branch but all artifacts look registered:**
The branch name may not be yielding the expected stage identifier. Check what `scripts/stage_gate.py
--stage <derived-stage>` returns. The stage is extracted as the first path segment after the branch
prefix, lowercased (e.g. `scf/s4-corpus` → `s4`).

**`repro-smoke` fails nightly but not on PRs:**
The base image may have received a security patch that changed behavior. Pin the Dockerfile
`FROM` line to a digest and rebuild.

**`prereg-freeze-guard` blocks a legitimate correction:**
See the "How to fix" section for that workflow above. The label `tripwire-override` is the only
legitimate path. Document the reason for the amendment in the commit message.
