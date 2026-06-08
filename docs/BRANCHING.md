# hc-grc — Git Branch Strategy

**Effective:** 2026-06-08
**Enforced by:** Git hooks, pre-commit framework, stage_gate.py, CI workflows

This document specifies the branch topology, naming conventions, protection rules, and merge
policies for the hc-grc program. The strategy enforces independence between per-framework studies,
prevents premature cross-framework merges, and ensures that every artifact in `main` is certified.

---

## Branch topology

```
main                                       ← certified trunk only (protected)
  ├── stage/P0-setup                      ← program-wide orchestration setup
  ├── stage/P1-prereg                     ← pre-registration (T1 tripwire)
  ├── stage/S3-method-validation          ← method validation on ground truth (shared)
  │
  ├── scf/S4-corpus                       ← per-framework: corpus + crosswalk
  ├── scf/S5-embedding                    ← per-framework: embedding ensemble
  ├── scf/S6-instrument-validity          ← per-framework: construct validity
  ├── scf/S7-investigations               ← per-framework: statistical studies
  ├── scf/S8f-triangulation               ← per-framework: within-framework synthesis
  ├── scf/S9-replication                  ← per-framework: adversarial replication
  │
  ├── nist-800-53/S4-corpus               ← [same stages for each of 4 other frameworks]
  ├── nist-800-53/S5-embedding
  ├── ... [S6–S9 omitted for brevity]
  │
  ├── nist-800-171/S4-corpus
  ├── nist-csf-2.0/S4-corpus
  ├── cis-v8/S4-corpus
  │
  ├── synthesis/X1-alignment              ← cross-framework synthesis (Tier B)
  ├── synthesis/X2-triangulation          ← enabled only when ≥2 frameworks clear S9
  ├── synthesis/X3-insight-gap-map
  ├── synthesis/X4-stance-synthesis       ← (T4 tripwire)
  └── synthesis/X5-release                ← (T5 tripwire)
```

---

## Branching rules

### main branch

- **Only destination for PRs from stage branches.**
- **No direct pushes.** All changes through pull requests.
- **CI checks required:** registry-schema-local, ruff, black, detect-secrets, no-data-in-git.
- **Require branch protection:**
  - At least one approved review (→ context-manager).
  - All status checks pass.
  - No force-pushes.
  - Dismiss stale reviews.
- **Merge strategy:** squash-and-rebase (clean history). The PR title is the commit message; body
  becomes the extended commit body.
- **Artifact certification requirement:** before a stage branch may merge to main, all artifacts for
  that stage must be registered in `registry/` with passing certificates in `ledger/`. The
  `stage_gate.py` script enforces this (CI gate + pre-merge hook).

### Program-level shared stages: `stage/P0-setup`, `stage/P1-prereg`, `stage/S3-method-validation`

- **Created once, branched from main.**
- **One branch per stage.** No per-framework variants.
- **S3 is a read-only method library** once certified (locked after completion).
- **Merge to main only when:**
  - All required artifacts are registered and certified.
  - For P1 (T1 tripwire): `docs/tripwires/T1.signed` must exist with a non-empty signature.
  - For S3: no tripwire, but all method-validation artifacts must be certified.

### Per-framework stages: `<framework>/<stage-slug>` (e.g., `scf/S4-corpus`, `nist-800-53/S5-embedding`)

- **One branch per framework per stage.** Exactly five frameworks, eight stages each (S1f–S9).
- **Total:** 40 per-framework branches + 3 shared program stages + 5 synthesis stages = 48 active branches.
- **Run in parallel:** no commit dependencies between framework branches before Tier B.
- **Stage sequence per framework is strict:**
  - S1f → S3 (shared) → S4 → S5 → S6 → S7 → S8f → S9.
  - A framework's branch `scf/S5-embedding` may not open until `scf/S4-corpus` is merged to main.
- **Independence rule (pre-merge validation):**
  - A per-framework stage branch must not contain commits from another framework's stage branch
    before the branch merges to main.
  - The pre-push hook `no-cross-framework-commits` validates this locally.
  - CI workflow `independence-lint` validates it on PR.
  - Violation blocks merge until resolved (force-rebase, not squash, to preserve independence).
- **Merge to main only when:**
  - All required artifacts are registered and certified.
  - For S4 (T2 tripwire per framework): `docs/tripwires/T2-<framework>.signed` must exist.
  - For S5 (T3 tripwire, shared): `docs/tripwires/T3.signed` must exist (frozen once, shared across all frameworks).

### Synthesis stages: `synthesis/X1-alignment`, `synthesis/X2-triangulation`, etc.

- **X1 may not open until ≥2 per-framework studies are certified through S9.**
- **Tier B gate enforced by:**
  - `stage_gate.py --tier-b-check` verifies certified framework count.
  - CI gate on X1 PR blocks merge until condition is met.
- **X2–X3 may proceed as soon as X1 merges.** They do not wait for all five frameworks.
- **X4 (stance synthesis) requires T4 tripwire:** `docs/tripwires/T4.signed` must exist.
- **X5 (release) requires T5 tripwire:** `docs/tripwires/T5.signed` must exist.
- **Merge to main only when:**
  - All required artifacts registered and certified.
  - Any required tripwires are signed.
  - No cross-framework artifact dependencies (enforced by stage_gate.py).

---

## Naming conventions

All branch names must follow this pattern:

```
<scope>/<stage-slug>
or
stage/<stage-slug>
```

**Scope:** one of `scf`, `nist-800-53`, `nist-800-171`, `nist-csf-2.0`, `cis-v8`, `synthesis`.

**Stage slug:** lowercase, hyphen-separated. Examples:
- `S4-corpus`
- `S5-embedding`
- `X1-alignment`
- `X4-stance-synthesis`

**Invalid examples:**
- `scf-S4` (wrong order)
- `SCF/S4_CORPUS` (uppercase, underscores)
- `scf/s4-corpus` (lowercase stage number)
- `scf/S4/corpus` (too many slashes)

**Enforcement:** pre-push hook `check-branch-name` validates all new branch names. Force-push
bypasses hooks; pushing to a branch with an invalid name is allowed only if it already exists.

---

## Commit conventions

Commits to any branch must follow a format based on whether they touch the registry.

### Registry touches: `[<STAGE>:<FRAMEWORK>] <artifact-type>: <brief-description>`

**Example:**
```
[S4:scf] control-asset: ingest NIST SCF taxonomy and build control corpus

Registry entry: scf/S4/controls.json (487 controls, lineage v2.1)
Artifact ID: scf-S4-controls-v2.1
```

**Required:**
- Stage tag: `[P0]`, `[P1]`, `[S3]`, `[S4:scf]`, `[S5:nist-800-53]`, etc.
- Artifact type: a slug from the artifact schema (e.g., `control-asset`, `embedding-ensemble`).
- Brief one-liner summary of what changed.
- Extended body (after blank line): artifact ID, registry path, summary of what was registered.

**Enforced by:** `scripts/hooks/commit-msg` hook (fails if missing on commits touching
`registry/`, `ledger/`, or `docs/tripwires/`).

### Non-registry commits: conventional format

**Examples:**
```
fix: correct embedding normalization in S5 pipeline

chore: update Makefile targets

docs: clarify stage_gate.py usage in README

feat: add tripwire signature validation to stage_gate.py
```

**Prefix:** `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`.

**Enforced by:** `scripts/hooks/commit-msg` hook (optional but recommended for clarity).

---

## Merge policies

### Default strategy

- **Squash-and-rebase:** condenses a feature branch's commits into a single commit on main.
- **Rationale:** keeps main's history linear and readable; hides in-progress iterations.
- **Exception:** if a stage branch has logical commits that are themselves certified steps, use
  regular merge (fast-forward if possible). Discuss with `git-workflow-manager` before merging.

### Conflict resolution

- **No merge conflicts allowed in automated merge.** The merging agent must resolve conflicts
  locally, test, and push a new commit to the stage branch before attempting merge again.
- **If a stage branch diverges from main (e.g., due to a fix in another branch),** rebase the
  stage branch onto main, not merge. This preserves independence.
- **Conflicts in `registry/` or `ledger/`:** these should be extremely rare (append-only ledger).
  If they occur, open an issue; do not auto-resolve.

---

## Enforcement mechanisms

### Pre-commit hooks (run on all commits)

Located in `.pre-commit-config.yaml`. Run before any commit is created.

- `ruff`: linting.
- `black`: formatting, 100-column limit.
- `check-json`: validates JSON files (including `registry/*.json`, `ledger/*.json`).
- `detect-secrets`: blocks commits with credential patterns.
- `no-data-in-git`: fails if staged files match `data/`, `*.parquet`, `embeddings/`, `*.h5`, `*.pkl`.
- `no-hand-edit-agents`: fails if `.claude/agents/*.md` files are staged without being in
  `scripts/sync-agents.sh` output.
- `registry-schema-local`: validates staged `registry/*.json` files against schema.

### Pre-push hooks (run before push)

- `check-branch-name`: enforces naming convention.
- `no-cross-framework-commits`: per-framework stage branches must not contain commits from other
  frameworks (one level only; does not block after merge to main).

**Install:**
```bash
make hooks
```

### Commit message hook

`scripts/hooks/commit-msg` — enforces message format.

- **On files touching `registry/`, `ledger/`, `docs/tripwires/`:** require `[STAGE:FRAMEWORK]` tag
  and artifact ID reference.
- **On all other commits:** conventional format recommended (enforced as a gentle warning, not hard fail).

**Install:** included in `make hooks`.

### CI gates (GitHub Actions)

- **`registry-schema-local`**: pre-commit check, runs on every commit.
- **`independence-lint`**: validates that per-framework stage branches do not contain cross-framework
  commits. Runs on PR.
- **`stage-gate-check`**: runs `stage_gate.py --stage <STAGE> --framework <FRAMEWORK>` to verify
  all artifacts are certified before merge. Blocks merge if not.
- **`no-tripwire-fork`**: verifies that T1–T5 tripwire commits only add signatures, never remove them.

---

## Per-stage merge gates (stage_gate.py)

Before a stage branch may merge to main, `stage_gate.py` is invoked via CI with that stage and
framework (or `--all` for shared stages). The script:

1. Loads `docs/STAGE_GATES.yaml`.
2. Queries `registry/` for all artifacts matching the stage + framework.
3. For each required artifact type in the gate definition: checks it exists and is registered.
4. For each registered artifact: checks its `certificate_ref` resolves to a passing certificate
   (verdict=ACCEPT) in `ledger/`.
5. Checks all `depends_on` stages are also certified.
6. If tripwire required: checks `docs/tripwires/<tripwire-id>.signed` exists with a signature.
7. For X1: checks that ≥2 frameworks have all S9 artifacts certified.
8. Exits 0 if all pass; exits 1 with a detailed diff of what's missing.

**Usage:**
```bash
# Check a per-framework stage
python scripts/stage_gate.py --stage S4 --framework scf

# Check a shared stage
python scripts/stage_gate.py --stage P1 --all

# Dry-run: check all stages across all frameworks
python scripts/stage_gate.py --validate

# Check if Tier B can open (≥2 frameworks through S9)
python scripts/stage_gate.py --tier-b-check
```

---

## Tag strategy

**Semantic versioning for releases:**

```
v1.0.0-alpha  ← first certified per-framework characterization
v1.0.0        ← certified cross-framework synthesis (X4 stance)
v1.1.0        ← X5 release package
```

**Artifact versioning (git commits, not tags):**

Each artifact in `registry/` carries a `source_commit` field pointing to the commit that produced it.
This allows reproducibility without relying on mutable tags.

---

## Quick reference: branching model diagram

```
                    [main — certified only]
                            ▲
                            │ (PR + stage_gate.py gate)
                            │
        ┌───────────┬───────┴───────┬──────────────┐
        │           │               │              │
    [P0-setup]  [P1-prereg]   [S3-method-val]   [synthesis/*]
        │           │               │              │
        └─→ [scf/S4-corpus]                      [X1-alignment]
            ↓                                      ↓
        [scf/S5-embedding]                   [X2-triangulation]
            ↓                                      ↓
        [scf/S6-instrument]                   [X3-insight-gap]
            ↓                                      ↓
        [scf/S7-investigations]               [X4-stance]
            ↓                                      ↓
        [scf/S8f-triangulation]               [X5-release]
            ↓
        [scf/S9-replication]
            │
            └─→ [main]
                  ▲
        [nist-800-53/S4-...-S9] ──→ [main]
        [nist-800-171/S4-...-S9] ──→ [main]
        [nist-csf-2.0/S4-...-S9] ──→ [main]
        [cis-v8/S4-...-S9] ──────→ [main]
```

---

## Migration checklist

If converting an existing repo to this model:

- [ ] Protect main: require PR, status checks, no force-push.
- [ ] Install hooks: `make hooks`.
- [ ] Create `docs/STAGE_GATES.yaml`.
- [ ] Create `scripts/stage_gate.py`.
- [ ] Create `scripts/hooks/commit-msg`.
- [ ] Create `.pre-commit-config.yaml`.
- [ ] Set up registry schema in `registry/schema/`.
- [ ] Set up ledger schema in `ledger/schema/`.
- [ ] Test locally: `make test` + `make validate`.
- [ ] Verify CI: commit to a test branch, open a PR, watch checks pass/fail.
- [ ] Document in team wiki (link to this file).

---

## Upstream source management

The hc-grc program ingests control frameworks from four upstream sources via Git submodules:

1. **awesome-claude-code-subagents** — Agent library (affects `.claude/agents/` roster only)
2. **scf** — Secure Controls Framework, CC BY 4.0, quarterly releases
3. **oscal-content** — NIST OSCAL (SP 800-53, SP 800-171, CSF), public domain, semantic versioning
4. **cis-controls-oscal** — CIS Controls v8 in OSCAL, archived (no updates expected)

### Submodule update process

**Pre-update (T2-adjacent tripwire):**
1. Fetch new tags: `git -C upstream/<name> fetch --tags`.
2. Review the release on GitHub: confirm license and check for schema changes.
3. Open a GitHub issue: "Upstream update available: [source] [version]".
4. Wait for human approval before proceeding.

**Update execution (after approval):**
```bash
git -C upstream/<name> fetch --tags
git -C upstream/<name> checkout <new-tag>
git add upstream/<name>
git commit -m "chore: pin <name> to <new-tag>"
```

**CI gate:** The `upstream-update-check.yml` workflow runs quarterly (first Monday of each quarter,
09:00 UTC) to check for new versions and open issues if updates are available.

### Framework source isolation during studies

When a per-framework study branch (e.g., `scf/S4-corpus`) is created, it records the exact
commit hash of its source submodule at branch inception. S4–S9 stages always ingest from that
pinned commit, **not** from a later update to main.

Example: if main is updated to SCF 2026.2.0, but the scf/S4-corpus branch was created when
SCF was at 2026.1.1, the study uses 2026.1.1. This ensures reproducibility: the corpus and
all downstream artifacts are tied to a specific source version.

Update the framework source within a study only if:
- Explicitly called for in an artifact or investigation report.
- Approved via amendment to the pre-registration or stage goals.
- Documented with a git commit explaining the reason for mid-study ingest of a new version.

### Agent roster updates

The awesome-claude-code-subagents submodule is separate from framework sources. Updates to
the agent library trigger the `agent-sync-check` CI workflow, which validates that
`.claude/agents/` remains in sync with the roster specified in `scripts/sync-agents.sh`.

Do not manually edit `.claude/agents/` files; regenerate after updating the agent submodule:
```bash
bash scripts/sync-agents.sh
```

See `docs/UPSTREAM_SOURCES.md` for detailed licensing, update cadence, and file paths for each source.

---

## References

- `docs/PROGRAM_ROADMAP.md` — stage definitions and data flow.
- `docs/UPSTREAM_SOURCES.md` — submodule licensing, update process, source file paths.
- `docs/AGENT_SYSTEM.md` — which agents run where.
- `docs/STAGE_GATES.yaml` — machine-readable gate definitions.
- `scripts/stage_gate.py` — the enforcement script.
- `Makefile` — `make hooks`, `make validate`, `make sync-agents`.
