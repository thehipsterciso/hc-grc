# Upstream Source Management

This document specifies the four upstream framework sources that hc-grc ingests, their licensing,
versioning, update cadence, and the exact file paths that S4 corpus ingestion consumes.

---

## Upstream submodules overview

| Source | Role | License | Update Cadence | Status |
|--------|------|---------|-----------------|--------|
| `upstream/awesome-claude-code-subagents` | Claude Code agent framework | Apache 2.0 | Ad-hoc | Active |
| `upstream/scf` | Secure Controls Framework | CC BY 4.0 | Quarterly | Active |
| `upstream/oscal-content` | NIST OSCAL frameworks | Public Domain | Semantic (1-2x/year) | Active |
| `upstream/cis-controls-oscal` | CIS Controls v8 in OSCAL | Per CIS EULA | None (archived) | Frozen |

---

## 1. awesome-claude-code-subagents

**Role:** Claude Code agent library. Provides the producers and adversary agents used by the hc-grc
program orchestrator.

**URL:** https://github.com/VoltAgent/awesome-claude-code-subagents.git

**License:** Apache 2.0

**Current Pin:** (git track as needed; no formal tag)

**Data Format & Path:**
- Category structure under `upstream/awesome-claude-code-subagents/categories/`
- Individual agent markdown files (e.g., `context-manager.md`, `git-workflow-manager.md`)
- Consumed by `scripts/sync-agents.sh` to populate `.claude/agents/`

**Update Cadence:** Ad-hoc. Update when new agent capabilities are required by program stages.
Does NOT follow a formal release cycle.

**Update Process:**
```bash
cd ~/hc-grc
git -C upstream/awesome-claude-code-subagents fetch origin
git -C upstream/awesome-claude-code-subagents checkout <branch-or-commit>
git add upstream/awesome-claude-code-subagents
git commit -m "chore: update agent framework reference"
bash scripts/sync-agents.sh  # regenerate .claude/agents/ manifest
```

**Notes:**
- This submodule affects the **agent roster only**, not the frameworks ingested by S4.
- Changes trigger the `agent-sync-check` CI workflow, which validates that `.claude/agents/`
  remains in sync with the roster specified in `scripts/sync-agents.sh`.

---

## 2. Secure Controls Framework (SCF)

**Role:** Primary GRC control framework study. Provides control taxonomy, definitions, and
lineage mappings.

**URL:** https://github.com/securecontrolsframework/securecontrolsframework.git

**License:** CC BY 4.0 (Creative Commons Attribution 4.0 International)

**Current Pin:** `2026.1.1` (semantic tag: `year.quarter[.patch]`)

**Data Format & Path:**
- **File:** `upstream/scf/secure-controls-framework-scf-2026-1.xlsx`
- **Format:** Excel workbook (single sheet or multi-sheet structure TBD by S4 ingester)
- **Consumed by:** S4-corpus stage for control asset ingestion, control-to-control lineage mapping

**Update Cadence:** Quarterly, aligned to calendar quarters.
- Q1 release: expected ~March; tag `2026.1.x`
- Q2 release: expected ~June; tag `2026.2.x`
- Q3 release: expected ~September; tag `2026.3.x`
- Q4 release: expected ~December; tag `2026.4.x`

**Update Process:**
1. **Pre-update review (T2-adjacent tripwire):**
   - Fetch new tags: `git -C upstream/scf fetch --tags`
   - Inspect release notes and license clause in the new tag.
   - Confirm license remains CC BY 4.0 and no breaking schema changes.
   - Open a GitHub issue in hc-grc: "Upstream update: SCF [new-version] available for review."
   - Link to the tag on GitHub.
   - Wait for human approval (T2 decision gate).

2. **Update after approval:**
   ```bash
   git -C upstream/scf fetch --tags
   git -C upstream/scf checkout <new-tag>  # e.g., 2026.2.0
   git add upstream/scf
   git commit -m "chore: pin SCF to <new-tag>"
   git push
   ```

3. **PR merge:**
   - Open a PR with title: `chore: update SCF to <new-tag>`
   - Description: link to release notes, changelog of what changed.
   - Merge only after CI passes and human confirms no schema-breaking changes.

**Notes:**
- SCF XLSX structure may evolve; coordinate with S4-corpus stage on schema changes.
- If a breaking schema change is detected, it must be flagged as a data hazard before the
  study proceeds.
- Mid-study submodule updates do NOT retroactively affect in-progress S4–S9 studies; each
  framework branch pins its ingestion at the commit recorded when the branch was created.

---

## 3. NIST OSCAL Content

**Role:** NIST security control frameworks in OSCAL format. Provides SP 800-53 Rev. 5,
SP 800-171 Rev. 2, and Cybersecurity Framework 2.0 definitions.

**URL:** https://github.com/usnistgov/oscal-content.git

**License:** Public Domain (no attribution required)

**Current Pin:** `v1.5.0` (semantic versioning)

**Data Format & Paths:**
- **Base Path:** `upstream/oscal-content/nist.gov/`
- **SP 800-53 Rev. 5 (primary):** `upstream/oscal-content/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json`
  (also available as YAML and XML in the same revision directory)
- **SP 800-171 Rev. 3 (latest):** `upstream/oscal-content/nist.gov/SP800-171/rev3/json/NIST_SP800-171_rev3_catalog.json`
  (also available as YAML and XML)
- **CSF 2.0:** `upstream/oscal-content/nist.gov/CSF/v2.0/json/NIST_CSF_v2.0_catalog.json`
  (also available as YAML and XML)
- **Consumed by:** Three per-framework study tracks (nist-800-53, nist-800-171, nist-csf-2.0)
  for S4-corpus ingestion.

**Update Cadence:** Semantic versioning, typically 1–2 major releases per year.
- NIST publishes updates when control families are revised or new frameworks are added.
- Minor/patch releases address schema refinements.

**Update Process:**
1. **Pre-update review (T2-adjacent):**
   - Fetch new tags: `git -C upstream/oscal-content fetch --tags`
   - Review NIST's release notes on GitHub (Releases page).
   - Confirm licenses remain Public Domain.
   - Open a GitHub issue: "Upstream update: NIST OSCAL [new-version] available for review."
   - List the affected frameworks (e.g., "SP 800-53 rev 5.2, CSF 2.0 additions").

2. **Update after approval:**
   ```bash
   git -C upstream/oscal-content fetch --tags
   git -C upstream/oscal-content checkout <new-tag>  # e.g., v1.6.0
   git add upstream/oscal-content
   git commit -m "chore: pin NIST OSCAL to <new-tag>"
   ```

3. **PR merge:** Same as SCF.

**Notes:**
- OSCAL schema is stable; updates are typically additive (new controls, refinements).
- If OSCAL's JSON/YAML structure changes, coordinate with each framework's S4 stage.
- Three independent study tracks (nist-800-53, nist-800-171, nist-csf-2.0) may progress
  at different speeds; each pins its ingestion independently.

---

## 4. CIS Controls v8 in OSCAL Format

**Role:** CIS Controls v8 in OSCAL representation. Provides the CIS v8 control taxonomy
as an alternative to the vendor-supplied mapping.

**URL:** https://github.com/CISecurity/CISControls_OSCAL.git

**License:** CIS EULA (per CIS Security's terms; not open-source)

**Current Pin:** `HEAD` (commit hash: `7cff2ec`, message: "Update README.md")

**Data Format & Path:**
- **File:** `upstream/cis-controls-oscal/src/catalogs/xml/cis-controls-v8_OSCAL-1.0.xml`
- **Format:** XML (OSCAL-compliant)
- **Consumed by:** cis-v8/S4-corpus stage for control asset ingestion

**Update Cadence:** NONE (archived repository)

- CIS Security has **archived this repository** as of 2024. No further updates are expected.
- This is a **permanent pin**. Do not update unless CIS reopens the repo or provides a
  formal replacement.
- The control definitions in v8 are stable; CIS does not plan v9 in the foreseeable future.

**Update Process:**
- Do not update. If CIS releases an official v9 OSCAL or a replacement, that would be a
  NEW submodule, not an update to this one.
- If you have evidence of a CIS-official update, open an issue for manual review before
  considering any change.

**Notes:**
- The CIS EULA prohibits certain uses of the controls (e.g., commercial resale). Ensure
  any artifacts derived from this submodule comply with CIS licensing terms.
- This is the only closed-source framework in the set. T2 tripwire must confirm license
  compliance before ingesting.

---

## Submodule update workflow summary

### For SCF and NIST OSCAL (active):

1. **Monitor:** Check GitHub releases page (e.g., via `git fetch --tags`) quarterly for SCF,
   semi-annually for NIST OSCAL.
2. **Pre-update gate (T2-adjacent):**
   - Open an issue: "Upstream update available: [framework] [version]"
   - Include tag message, release notes link, and a note of any schema changes.
   - Human reviews and approves (or rejects due to breaking changes).
3. **Execute update:** `git -C upstream/<name> fetch --tags && git -C upstream/<name> checkout <tag>`
4. **Commit & PR:** Commit the submodule pointer update with a clear message.
5. **CI gate:** Run `upstream-update-check.yml` (GitHub Actions workflow, see below) to confirm
   the update is registered.

### For CIS (archived):

- **Do not update.** The repo is archived; no further changes are expected.

### Mid-study isolation:

- When a per-framework study branch (e.g., `scf/S4-corpus`) is created, it records the current
  commit of its source submodule in `docs/<framework>/S4-SOURCE-PIN.json` or similar artifact.
- If the submodule is updated on main **after** the study branch is created, the study uses
  its recorded pin, **not** the new main version.
- This ensures reproducibility: a study's S4–S9 stages always ingest the same source version,
  even if upstream moves forward mid-study.

---

## GitHub Actions: upstream-update-check.yml

A scheduled CI workflow checks for new upstream versions quarterly and opens issues if updates
are available.

**Schedule:** First Monday of each quarter at 09:00 UTC.
- Cron: `0 9 1 1,4,7,10 *` (day 1 of Jan, Apr, Jul, Oct; fine-grained alternatives use
  `schedule` with a conditional date check)

**Behavior:**

1. **Fetch latest tags** from SCF and NIST OSCAL upstream.
2. **Compare** current pin (from `.gitmodules`) to latest tag.
3. **If newer version exists:**
   - Open a GitHub issue: `Upstream update available: [framework] [new-version]`
   - Include:
     - Current pin and new version.
     - Link to the release on GitHub (tag page).
     - Commit log since current pin (first 5 commits).
     - Note that human review is required before merging update.
   - Example title: `Upstream update: SCF 2026.2.0 available`
4. **If no update:** No action (silent pass).
5. **CIS:** Skipped (archived repo).

**Notes:**
- This workflow does **not** automatically update. It flags availability only.
- T2 decision gate is manual: a human reviews the issue, checks release notes, confirms
  license/schema compatibility, and only then does an engineer execute the update.
- The workflow can be manually triggered via GitHub UI if you need to check for updates outside
  the quarterly schedule.

---

## Provenance and T2 gate

Before any submodule pointer update is merged to main:

1. **Check licensing:** Confirm the new version's license matches the current (or is compatible).
2. **Check schema:** Run a pre-check (if one exists) to ensure data structure compatibility.
3. **Open an issue:** For manual review and approval (T2 decision).
4. **Update:** After approval, execute the update and merge the PR.
5. **Document:** The PR commit message includes the new tag/version and a link to release notes.

This prevents inadvertent schema breaks or license violations from being merged into a study.

---

## References

- `.gitmodules` — submodule definitions and URLs.
- `.github/workflows/upstream-update-check.yml` — quarterly update checker.
- `docs/BRANCHING.md` — how submodule updates integrate with the branching strategy.
- `scripts/sync-agents.sh` — how the agent submodule populates `.claude/agents/`.
