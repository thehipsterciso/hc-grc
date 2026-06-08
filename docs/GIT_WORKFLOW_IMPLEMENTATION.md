# hc-grc — Git Workflow Implementation Guide

**Status:** Ready for adoption  
**Last updated:** 2026-06-08

This guide walks through the complete Git workflow for hc-grc: branch strategy, stage gates,
hooks, and team processes. All components are in place; follow the checklist below to activate.

---

## Files created

### Documentation
- **`docs/BRANCHING.md`** — Full branch strategy, naming conventions, merge policies.
- **`docs/STAGE_GATES.yaml`** — Machine-readable gate definitions for all 18 stages.
- **`docs/GIT_WORKFLOW_IMPLEMENTATION.md`** — This file.

### Enforcement
- **`scripts/stage_gate.py`** — Python script to validate stage certification before merge.
- **`.pre-commit-config.yaml`** — Pre-commit framework config (ruff, black, detect-secrets, custom hooks).
- **`scripts/hooks/commit-msg`** — Enforces commit message format (registry tags, artifact IDs).
- **`scripts/hooks/check-branch-name.sh`** — Validates branch name format on push.
- **`scripts/hooks/check-cross-framework-commits.sh`** — Prevents cross-framework commits in stage branches.
- **`scripts/hooks/check-agents-generated.sh`** — Prevents hand-edits to generated agent files.
- **`scripts/hooks/validate-registry-schema.py`** — Validates JSON schema for registry/ledger.

### Build & Test
- **`Makefile`** — Common commands: `make install`, `make hooks`, `make validate`, etc.
- **`requirements-dev.txt`** — Dev dependencies (ruff, black, pre-commit, pyyaml, pydantic, pytest).
- **`tests/test_stage_gate.py`** — Unit tests for stage_gate.py (testable without live registry).

---

## Activation checklist

### 1. Environment setup

```bash
cd /Users/thomasjones/hc-grc

# Install dependencies
make install

# Verify hooks are installed
git hooks list
# Should show: commit-msg, pre-commit, pre-push
```

### 2. Protect main branch (GitHub UI)

On GitHub, go to **Settings → Branches → main → Branch protection rules**:

- [ ] Require pull requests before merging
- [ ] Require status checks to pass before merge (include: `registry-schema-local`)
- [ ] Require branches to be up to date before merging
- [ ] Require code reviews (≥1 approval)
- [ ] Dismiss stale pull reviews
- [ ] Require status checks to pass before merge: include all CI workflows

(Or use the `gh` CLI if you prefer:)
```bash
gh api repos/thehipsterciso/hc-grc/branches/main/protection --input - << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["registry-schema-local"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  }
}
EOF
```

### 3. Create tripwire directory structure

```bash
mkdir -p docs/tripwires
git add docs/tripwires/.gitkeep
git commit -m "chore: create tripwires directory"
git push
```

### 4. Create registry and ledger schemas

Registry and ledger files are expected in:
- `registry/schema/` — JSONSchema for artifacts
- `ledger/schema/` — JSONSchema for certificates

(These are loaded by `validate-registry-schema.py` and can remain empty initially; the
in-line validation in the Python script covers the essential fields.)

### 5. Test locally

```bash
# Test stage_gate.py
python scripts/stage_gate.py --validate
# Should show: "VALIDATION ERRORS" (expected; no artifacts yet)

# Test hooks
echo "import sys" > test_script.py
pre-commit run ruff --files test_script.py
# Should pass or show lint messages

# Test commit message hook
git commit --allow-empty -m "test: no commit-msg hook on allow-empty"
# Should succeed

# Cleanup
rm test_script.py
```

### 6. Create CI workflow (GitHub Actions)

Add `.github/workflows/git-gates.yml`:

```yaml
name: Git Gates

on:
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  registry-schema:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install pyyaml pydantic
      - run: python scripts/hooks/validate-registry-schema.py

  independence-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history
      - run: bash scripts/hooks/check-cross-framework-commits.sh || true
        # Non-blocking on first runs

  stage-gate-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install pyyaml pydantic
      - name: Extract stage and framework from branch
        id: branch-info
        run: |
          BRANCH=${{ github.head_ref }}
          if [[ "$BRANCH" =~ ^stage/(.+)$ ]]; then
            echo "stage=${BASH_REMATCH[1]}" >> $GITHUB_OUTPUT
            echo "all=true" >> $GITHUB_OUTPUT
          elif [[ "$BRANCH" =~ ^([a-z-]+)/(.+)$ ]]; then
            echo "framework=${BASH_REMATCH[1]}" >> $GITHUB_OUTPUT
            echo "stage=${BASH_REMATCH[2]}" >> $GITHUB_OUTPUT
          fi
      - name: Validate stage gate
        run: |
          if [ -n "${{ steps.branch-info.outputs.stage }}" ]; then
            ARGS="--stage ${{ steps.branch-info.outputs.stage }}"
            if [ "${{ steps.branch-info.outputs.all }}" = "true" ]; then
              ARGS="$ARGS --all"
            elif [ -n "${{ steps.branch-info.outputs.framework }}" ]; then
              ARGS="$ARGS --framework ${{ steps.branch-info.outputs.framework }}"
            fi
            python scripts/stage_gate.py $ARGS || true
            # Non-blocking until artifacts are registered
          fi
```

### 7. Document for team

Link to these files in your team wiki or README:

```markdown
## Git Workflow

- **Branch strategy:** [docs/BRANCHING.md](docs/BRANCHING.md)
- **Stage gates:** [docs/STAGE_GATES.yaml](docs/STAGE_GATES.yaml)
- **Setup:** `make install && make hooks`
- **Validate:** `make validate`
- **Common tasks:**
  - `make lint` / `make format` — Code quality
  - `make sync-agents` — Regenerate agent files
  - `make freeze-prereg` — Lock pre-registration (T1 action)
```

---

## Day-to-day usage

### For framework study leads (S4–S9 per framework)

**Starting a new stage branch:**

```bash
# From main, create and check out a new stage branch
git checkout -b scf/S4-corpus

# Make changes, commit with proper message
git commit -m "[S4:scf] control-asset: ingest NIST SCF controls

Registry entry: registry/scf/S4/controls.json
Artifact ID: scf-S4-controls-v2.1
"

# Hooks validate commit message automatically

# Push to remote (hooks validate branch name)
git push --set-upstream origin scf/S4-corpus

# Open a PR (link to issue, describe artifacts)
gh pr create --title "S4: Build SCF corpus" \
  --body "Ingests NIST SCF 2.0 controls and builds the crosswalk table..."
```

**Before merging to main:**

```bash
# Agent runs the artifact certification process
# (handled by multi-agent-coordinator in the actual program)

# Once artifacts are registered and certified:
python scripts/stage_gate.py --stage S4 --framework scf

# If gate passes:
# 1. Request review (merged by context-manager or coordinator)
# 2. PR is squash-merged to main
# 3. Delete branch
```

### For synthesis leads (X1–X5, Tier B)

**Same process, but X1 is blocked until ≥2 frameworks clear S9:**

```bash
# Check if Tier B can open
python scripts/stage_gate.py --tier-b-check

# If it returns the green light, create X1 branch
git checkout -b synthesis/X1-alignment
```

### For the coordinator (multi-agent-coordinator agent)

```bash
# Before spawning a stage, validate its dependencies
python scripts/stage_gate.py --validate

# Monitor progress across all stages
python scripts/stage_gate.py --validate -v

# Check if Tier B can advance
python scripts/stage_gate.py --tier-b-check

# On merge to main, update the ledger and mark the stage complete
# (this is automated in the production system)
```

### Tripwire actions (human)

**T1: Freeze pre-registration**

```bash
make freeze-prereg
# Prompts for confirmation, then:
# - Hashes docs/PREREGISTRATION.md
# - Commits the hash
# Next: Sign the tripwire
mkdir -p docs/tripwires
echo "Thomas Jones" > docs/tripwires/T1.signed
git add docs/tripwires/T1.signed
git commit -m "[P1] Freeze pre-registration (T1 tripwire signed)"
git push
```

**T2, T3, T4, T5: Same pattern**

```bash
mkdir -p docs/tripwires
echo "Thomas Jones" > docs/tripwires/T2-scf.signed  # Per framework
# or
echo "Thomas Jones" > docs/tripwires/T4.signed      # Shared
git add docs/tripwires/T*.signed
git commit -m "[<STAGE>] <action> (T<N> tripwire signed)"
git push
```

---

## Conflict resolution

### Scenario 1: Main diverges while you're working on a stage

```bash
git fetch origin
git rebase origin/main
# Resolve conflicts in your editor
git add .
git rebase --continue
git push --force-with-lease
```

### Scenario 2: Another framework's stage branch is merged while you're developing

If your per-framework stage branch is affected:

```bash
# Ensure you remain independent
git rebase origin/main

# If that introduces cross-framework commits:
# (hooks will catch this on push)
# Solution: re-apply your changes on top of clean main
git rebase --interactive origin/main
# Reorder commits to remove cross-framework ones
# Or start fresh from main
```

### Scenario 3: Registry/ledger conflict

Should never happen (append-only design). If it does, open an issue; don't merge.

---

## Troubleshooting

### "Invalid branch name" on push

```bash
# Check current branch
git branch -v

# Rename if needed
git branch -m <old-name> <new-name>

# Valid patterns:
# stage/<slug>
# <framework>/<slug>
# Example: git branch -m scf/S4_corpus scf/S4-corpus
```

### "Cross-framework commit detected"

This happens if your per-framework branch contains commits from another framework's branch.

```bash
# Solution: rebase onto main
git rebase origin/main

# Verify no cross-framework commits remain
git log origin/main..HEAD --oneline
# Should show only your commits

# Force-push (safe with lease)
git push --force-with-lease
```

### "Certificate not found"

The artifact is registered but its certificate doesn't exist in the ledger.

```bash
# Check what's registered
ls -la registry/**/*.json | head -10

# Check what certificates exist
ls -la ledger/certificates/ | head -10

# If a certificate is missing, the artifact needs to be re-certified
# before the stage can merge.
```

### "Tripwire T1 required but not signed"

```bash
# Check if the tripwire file exists and is signed
ls -la docs/tripwires/T1.signed

# If not, create it
mkdir -p docs/tripwires
echo "Thomas Jones" > docs/tripwires/T1.signed
git add docs/tripwires/T1.signed
git commit -m "[P1] Sign T1 tripwire (freeze pre-registration)"
git push
```

### "Pre-commit hook failed"

```bash
# See which hook failed
pre-commit run --all-files

# Fix issues:
# - Code style: make format
# - JSON schema: edit the file to match schema
# - Secrets detected: remove and commit without the secret
# - Data files: don't commit (add to .gitignore)

# Re-stage and commit
git add .
git commit -m "fix: address pre-commit issues"
```

---

## Monitoring and reporting

### Check overall program status

```bash
make validate
```

Outputs a summary:
- All stages certified: ✓
- Missing artifacts per stage: listed
- Tripwire status: signed or pending
- Tier B readiness: framework count

### Check a specific stage

```bash
python scripts/stage_gate.py --stage S4 --framework scf -v
```

Outputs:
- Required artifacts: listed with ✓ or ✗
- Certificate verdicts: ACCEPT or REJECT
- Dependencies: validated recursively

### Check Tier B eligibility

```bash
python scripts/stage_gate.py --tier-b-check -v
```

Outputs:
- Framework count through S9
- Minimum required (2)
- Green light if ready, or how many more needed

---

## References

- **`docs/BRANCHING.md`** — Complete branch strategy and naming rules
- **`docs/STAGE_GATES.yaml`** — Stage definitions and artifact requirements
- **`docs/PROGRAM_ROADMAP.md`** — Program flow and dependencies
- **`docs/AGENT_SYSTEM.md`** — Agent roles and responsibilities
- **`scripts/stage_gate.py`** — Gate validation logic (code reference)
- **`Makefile`** — All available commands

---

## Integration with the agent system

The Git workflow enforces the stage gates that the multi-agent-coordinator depends on:

1. **Agent runs a stage** → produces artifacts with Definition of Done
2. **Artifacts are certified** (same-discipline adversary reviews)
3. **Artifacts registered** in `registry/` with certificate reference
4. **Stage gate validates** via `stage_gate.py`:
   - All required artifacts exist
   - All certificates are ACCEPT
   - Dependencies are satisfied
   - Tripwires (if any) are signed
5. **PR is merged** to main (only certified artifacts reach trunk)
6. **Registry becomes the source of truth** for what's been completed

No agent can access work from a stage that hasn't passed its gate. This enforces the
"certified-only registry" principle from the program roadmap.

---

## Future enhancements

- Auto-tag releases with semantic versioning on X5 merge
- Automated changelog generation from registry entries
- Slack notifications on stage completion
- Metrics dashboard (framework progress, artifact count, certificate trends)
- Automated bisect support (find the commit that introduced a defect)
