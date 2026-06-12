# AGENT.md Cards Specification

**Version:** 1.0.0
**Status:** Locked

This document is the authoritative specification for all AGENT.md cards in the HC-GRC agent library. The 50 cards in `agents/**/AGENT.md` are instances of this schema. A Pydantic validator runs against this spec on pre-commit and in CI. Any frontmatter field change on an existing card is a version bump. Any body section change that alters an agent's behavioral constraints or handoffs requires a version bump and a lab notebook entry.

The cards are the single source of truth for the following auto-generated documents. Do not author these manually — they drift:
- `HANDOFFS.md` — derived from all "Receives from" / "Passes to" sections
- `CONTRACTS.md` — derived from all Inputs and Outputs tables
- `INFRASTRUCTURE_REQUIREMENTS.md` — derived from all Tools & MCP Servers sections
- `CAPABILITY_MATRIX.md` — derived from all Skills Used sections
- `GATES.md` (inventory table) — derived from all "Human gate" entries in Handoffs sections
- `SKILLS_INVENTORY.md` — derived from all `skills:` frontmatter fields
- topology graph (Mermaid/Graphviz) — derived from Handoffs DAG

---

## Frontmatter Schema

```yaml
---
name: agent-name-here           # Required. kebab-case. Gerund or noun form.
description: "..."              # Required. Third person. What it does AND when to use it. Max 512 chars.
version: 1.0.0                  # Required. Semantic versioning. Bump on any functional change.
team: NN-team-name              # Required. Matches directory name exactly.
status: primary | conditional | deferred  # Required. primary = active every pipeline; conditional = activates on trigger; deferred = Tier-2, not yet active.
trigger: "always | <condition>" # Required. "always" for primary agents. Specific condition string for conditional.
author: HC-GRC                  # Required. Fixed value.
tags: [Tag One, Tag Two]        # Required. Title Case for words; UPPERCASE for acronyms (RLHF, NLP, STRM, SAP).
skills: [skill-name]            # Required. kebab-case skill names from AI Research Skills Library. Empty list [] if none.
tools: [mcp-server-name]        # Required. Tool and MCP server identifiers. Empty list [] if none.
agent_id: ""                    # Optional at authoring time. Auto-populated by card validator. See §Agent ID.
deprecated: false               # Optional. Default false. See §Deprecation.
superseded_by: ""               # Required if deprecated: true. Name of replacement agent.
---
```

### Field Rules

**`name`**: Must match the directory name containing the card. Validated at pre-commit. Hyphens only — no underscores, no spaces.

**`description`**: Third person ("Provides guidance for...", "Manages...", "Executes..."). Must state what the agent does and the condition under which it is invoked. First-person voice ("I can...") fails validation.

**`version`**: Semantic versioning — `MAJOR.MINOR.PATCH`. Increment rules:
- PATCH: prose clarification, no behavioral change
- MINOR: new handoff, new tool, new output artifact, new behavioral constraint
- MAJOR: change to inputs/outputs schema, change to trigger condition, change to team assignment

**`status`**: `primary` agents run on every pipeline. `conditional` agents require `trigger` to name the specific condition. `deferred` agents are specified for a later tier and not yet active. A `primary` agent whose `trigger` does not begin with `always` fails validation (an explanatory `always — …` annotation is allowed).

**Completeness policy**: required body sections, the three Handoffs fields, and the Evaluation-Criteria checklist are **hard errors for `primary` (active) agents** and **advisory warnings for `conditional`/`deferred`** agents, which are incomplete by design until their tier activates. Frontmatter rules apply to all cards equally.

**`skills`**: Names from the AI Research Skills Library (`agents/` directory) or from the ARA pattern for custom agents. Must be resolvable to an installed skill at runtime. Empty list `[]` is valid for ARA-pattern agents.

**`tools`**: MCP server identifiers as registered in the infrastructure config. Format: `mcp-<server-name>` (e.g., `mcp-qdrant`, `mcp-mlflow`, `mcp-github`). Empty list `[]` is valid.

---

## Required Body Sections

Every AGENT.md must contain these sections in this order. Sections may be abbreviated for simple agents but may not be omitted.

| Section | Required | Notes |
|---------|----------|-------|
| `## Purpose` | Yes | What the agent does and why it exists. No bullet points — prose only. |
| `## Position in Workflow` | Yes for primary | ASCII diagram showing where the agent sits in the pipeline. May omit for simple pass-through agents. |
| `## Inputs` | Yes | Table: Input / Source / Format / Required |
| `## Outputs / Artifacts` | Yes | Table: Artifact / Destination / Format / Notes |
| `## Tools & MCP Servers` | Yes if tools list non-empty | Table: Tool / Purpose |
| `## Skills Used` | Yes if skills list non-empty | Bullet list: skill name — how it is used in this agent specifically |
| `## Handoffs` | Yes | **Receives from**, **Passes to**, **Human gate** (required — "None" is valid) |
| `## Behavioral Constraints` | Yes | Bullet list. Every constraint is enforceable — no vague principles. |
| `## Failure Modes & Recovery` | Yes | Table: Failure / Recovery |
| `## Evaluation Criteria` | Yes | Checklist — `[ ]` format. These are the auto-generated Definition of Done. |
| `## Trigger Conditions` | Conditional only | Table or prose for conditional agents. Primary agents omit this section. |
| `## Notes` | Optional | Free text. Not parsed. |

### Handoffs Format

```markdown
## Handoffs
**Receives from**: [Agent Name], [Agent Name] — or "None" (pipeline start)
**Passes to**: [Agent Name], [Agent Name] — or "None" (pipeline end)
**Human gate**: Gate N — [brief description] — or "None"
```

`Human gate` is a required field. If the agent does not trigger a human gate, write `**Human gate**: None`. This field populates the GATES.md inventory table.

---

## Agent ID

`agent_id` is a content-addressed identifier derived from the card content at validation time:

```
agent_id = "hcgrc:" + sha256(name + ":" + version + ":" + team)[0:16]
```

The agent_id is stable across prose edits and changes only when `name`, `version`, or `team` change. It is written into the frontmatter by the card validator and must not be hand-authored. It appears in the run manifest `agent_revisions[]` array.

---

## Deprecation

When an agent is replaced:
1. Set `deprecated: true` and `superseded_by: <replacement-agent-name>` in the outgoing card
2. Write an ADR in `decisions/NNNN-deprecate-<agent-name>.md`
3. Keep the deprecated card in the repository — do not delete it
4. The deprecated card does not appear in auto-generated active-agent docs but does appear in the full card inventory

---

## Validation Rules (enforced at pre-commit and CI)

1. `name` matches directory name
2. `version` is valid semver
3. `status == "primary"` → `trigger == "always"`
4. `status == "conditional"` → `trigger != "always"` and trigger is non-empty
5. `description` does not start with "I" (first-person check)
6. `description` length ≤ 512 characters
7. All `skills[]` entries are resolvable skill names
8. All `tools[]` entries match `mcp-*` pattern
9. `## Handoffs` section contains `**Receives from**`, `**Passes to**`, `**Human gate**`
10. `## Evaluation Criteria` contains at least one `[ ]` checklist item
11. `deprecated: true` requires `superseded_by` to be non-empty
12. If `agent_id` is present, it matches the derivation formula

---

## Auto-generation Parser Contract

The parser (`tools/generate_docs.py`, implemented; stdlib-only) reads cards by walking `agents/**/AGENT.md`. It:
- Parses frontmatter and splits body sections by heading
- Validates against the rules above (hard errors for `primary`; advisory for `conditional`/`deferred`)
- Extracts the structured sections (Inputs, Outputs, Tools, Handoffs, Skills) by heading name
- Regenerates the derived docs into `agents/generated/` (never hand-authored): `HANDOFFS.md`, `CONTRACTS.md`, `INFRASTRUCTURE_REQUIREMENTS.md`, `CAPABILITY_MATRIX.md`, `SKILLS_INVENTORY.md`, `GATES_INVENTORY.md`, `topology.mmd`

Usage: `make generate-docs` (regenerate) / `python tools/generate_docs.py --check` (validate, exit 1 on hard errors). `--check` is wired into CI once active-card errors reach zero.

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-09 | Initial spec lock — 48 existing cards are v1.0.0 instances |
