# ADR-0005: AGENT.md as the Agent Card Format

**Status:** Accepted
**Date:** 2026-06-09
**Deciders:** Thomas Jones

---

## Context

The platform has 48 agents across 17 teams. Each agent needs a machine-parseable, human-readable document that declares its purpose, inputs, outputs, tools, skills, behavioral constraints, failure modes, and handoffs. This document is both the agent's contract with the platform and the source of truth for auto-generated infrastructure documentation.

The question was: what format, what filename?

## Decision

Each agent has exactly one `AGENT.md` file in its directory. Format follows the AI Research Skills Library `SKILL.md` convention adapted for agents — YAML frontmatter with required fields, standardized body sections. Filename is `AGENT.md` (not `SKILL.md`) to make the semantic distinction clear at a glance: skills describe capabilities, agents describe autonomous actors.

The cards are the single source of truth. HANDOFFS.md, CONTRACTS.md, INFRASTRUCTURE_REQUIREMENTS.md, CAPABILITY_MATRIX.md, GATES.md (inventory), SKILLS_INVENTORY.md, and the topology graph all auto-generate from parsing the cards. These derivative docs are never hand-authored.

The formal specification is CARDS_SPEC.md in the `agents/` directory. A Pydantic validator enforces the schema on pre-commit and in CI.

## Alternatives Considered

**SKILL.md (same filename as the skill library):** Consistent with the AI Research Skills Library convention. Rejected because the semantic distinction between "a skill describing a library capability" and "an agent that acts autonomously in a pipeline" is lost when both use the same filename. A developer browsing the repo should immediately know which is which.

**JSON or YAML card (no prose):** Machine-readable but not human-readable without a renderer. Agents are architectural objects that humans review at gates and in design sessions. Markdown with structured frontmatter gives both.

**No formal format (prose documents):** Common in early-stage systems. Rejected because auto-generation from prose is unreliable. The structured sections (Inputs table, Outputs table, Handoffs) are the auto-generation targets.

**A2A AgentCard JSON at `/.well-known/agent-card.json`:** The A2A standard (Linux Foundation, 2025) is designed for inter-organization agent discovery. HC-GRC is a local, supervised, single-organization platform. A2A adds network exposure overhead without benefit in this context. AGENT.md captures the spirit of A2A's capability declaration for the local case.

## Consequences

**Positive:**
- 48 cards are machine-parseable via `python-frontmatter` + Pydantic
- Auto-generated docs eliminate drift between the card spec and derivative documentation
- Human-readable for gate reviews and architectural design sessions
- Schema validation on pre-commit prevents structural drift

**Negative:**
- 48 cards to maintain — version bumps are required on any functional change
- Prose sections (Purpose, Behavioral Constraints) are not machine-validated for correctness, only for presence
- Auto-generation requires `tools/generate_docs.py` to be implemented and kept current
