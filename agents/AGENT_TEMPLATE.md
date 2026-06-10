---
name: agent-name-here
description: Third-person description of what this agent does and when it activates. Include role, primary artifact, and trigger condition.
version: 1.0.0
team: 00-orchestration
status: primary
trigger: always
author: HC-GRC
tags: [Tag One, Tag Two]
skills: [skill-name-1, skill-name-2]
tools: [tool-name-1, tool-name-2]
---

# Agent Name

## Purpose

What problem this agent solves in the research workflow. Not a restatement of the name — the actual reason this role exists and what breaks without it.

## Position in Workflow

Where this agent sits in the sequence. What must have happened before it activates. What it unblocks.

```
[Predecessor Agent] → [This Agent] → [Successor Agent]
                             ↓
                     [Primary Artifact]
```

## Inputs

| Input | Source Agent | Format | Schema / Notes |
|-------|-------------|--------|----------------|
| | | | |

## Outputs / Artifacts

| Artifact | Destination | Format | Schema / Notes |
|----------|-------------|--------|----------------|
| | | | |

## Tools & MCP Servers

| Tool | Purpose | MCP Server | Notes |
|------|---------|-----------|-------|
| | | | |

## Skills Used

Links to skill library entries this agent draws on.

- **[Skill Name]** — how it is used in this agent's context

## Handoffs

**Receives from**: [Agent names]
**Passes to**: [Agent names]
**Human gate**: [None / Gate N — description of what the human decides]

## Behavioral Constraints

What this agent must never do. Hard boundaries that cannot be overridden by orchestrator instructions.

- Never ...
- Never ...

## Failure Modes & Recovery

| Failure | Detection | Recovery |
|---------|-----------|----------|
| | | |

## Evaluation Criteria

How the QA Agent and Orchestrator determine this agent succeeded.

- [ ] Criterion 1
- [ ] Criterion 2

## Trigger Conditions

*(For conditional agents only — delete section for primary agents)*

| Trigger | Threshold | Activated By |
|---------|-----------|-------------|
| | | |

## Notes

Anything not captured above that is essential for implementation.
