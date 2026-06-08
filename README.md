# hc-grc — Empirical Characterization of Governance Control Frameworks

An autonomous, adversarially-verified research program that studies governance, risk, and
compliance (GRC) control frameworks as structured data corpora — one framework at a time, then
synthesized across frameworks — to describe how control space is actually organized, where its
boundaries and gaps lie, and what structure it has.

## Stance: findings first

**This program does not set out to prove anything.** It characterizes the structure of each
framework rigorously, surfaces the insights and the gaps, and only then — as a clearly separated,
late, adversary-gated step — theorizes a stance *from* what the data said. Any hypothesis we hold
going in is treated as inadmissible until re-derived under pre-registration. No conclusion is wired
into the questions, the methods, or the success criteria. If a framework's structure turns out to
be exactly what its authors claim, that is a finding and it ships.

## How it is organized

Two tiers.

**Per-framework studies** (`frameworks/<name>/`) — each framework runs the same rigorous pipeline
independently and produces its own structural characterization. First wave (all open-licensed):

| Study | Framework | License | Role |
|-------|-----------|---------|------|
| `frameworks/scf/` | Secure Controls Framework | Creative Commons | Corpus **and** cross-framework crosswalk |
| `frameworks/nist-800-53/` | NIST SP 800-53 Rev 5 | Public domain (OSCAL) | Native corpus |
| `frameworks/nist-csf-2.0/` | NIST CSF 2.0 | Public domain | Native corpus |
| `frameworks/nist-800-171/` | NIST SP 800-171 Rev 3 | Public domain (OSCAL) | Native corpus |
| `frameworks/cis-v8/` | CIS Controls v8 | Open terms | Native corpus |

**Cross-framework synthesis** (`synthesis/`) — aligns the per-framework findings (via the SCF
crosswalk) and tests which structural results replicate across independently-authored frameworks.
Replication across frameworks is the strongest evidence the program produces: it separates what is
intrinsic to control space from what is an artifact of any single framework's editorial choices.

## How the work is checked

Every artifact is produced by a discipline agent and certified by a **same-discipline adversary
agent** before it enters shared state — same discipline for competence, a rotating review stance
for a different mental model, and a different model family for weight-level independence. The
adversary agents live natively in `agents/adversarial-review/`, and the framework's producer agents
are pinned as a submodule at `upstream/awesome-claude-code-subagents/`. Claude Code auto-loads the
working set from `.claude/agents/`. The full agent system — its four tiers, orchestration topology,
and the produce→certify→register loop — is documented in `docs/AGENT_SYSTEM.md`.

## Documents

- `docs/AGENT_SYSTEM.md` — the agent system architecture: tiers, topology, and how a unit of work flows
- `docs/PROGRAM_ROADMAP.md` — the two-tier stage architecture and execution plan
- `docs/PREREGISTRATION.md` — the register of open questions, methods, and decision rules (to be frozen)
- `CLAUDE.md` — program governance and hard constraints
- `synthesis/SYNTHESIS_PLAN.md` — cross-framework triangulation, insight/gap, and stance synthesis

## Status

Ready to execute. The agent system is wired (`.claude/agents/` auto-loads 36 agents), the framework
is pinned as a submodule (`upstream/`), and the program docs are in place. Nothing is frozen yet:
the pre-registration must be frozen (human tripwire T1) before any data is touched. Open this folder
in Claude Code and instruct the orchestrator to begin.

## License

Program code and analysis: Apache-2.0. Each framework's source data is used under its own license,
recorded per study. SCF data under Creative Commons per ComplianceForge terms; NIST OSCAL content
is public domain.
