#!/usr/bin/env bash
# Seed the HC-GRC kickoff backlog as GitHub issues, using the repo's EXISTING
# label taxonomy (no new labels). ONE-SHOT: running twice creates duplicates.
# Requires gh authenticated against github.com/thehipsterciso/hc-grc.
#
# Source of truth for the backlog: KICKOFF_READINESS.md.
# NOT created here (already tracked): DIVERGENCE-01 == existing issue #101 (closed).
set -euo pipefail

issue () { gh issue create --title "$1" --label "$2" --body "$3"; }

echo "Creating issues..."

# ── P0 — Phase-0 sign-off (Track A) ─────────────────────────────────────────
issue "Phase-0: Gate-1 synthetic dry-run produces a valid gate record" "p0,gate,architecture" \
"Per ADR-0015 #71 / GATES.md Phase-0 prerequisites. Run the synthetic Gate-1 interrupt and confirm a valid gate record is written. No SCF data may be acquired until all Phase-0 items pass. Closes the execution side of #93."
issue "Phase-0: PostgresSaver checkpointing confirmed on the Mac mini" "p0,architecture,infra" \
"Confirm LangGraph PostgresSaver checkpoint/replay on the target compute node."
issue "Phase-0: compute_data_split() idempotency test passes (bit-identical)" "p0,gate,architecture" \
"ADR-0015 #75. Two runs with identical state produce bit-identical output; seed derived from SHA-256 of the data manifest hash. Execution of the fix logged in (closed) #75."
issue "Phase-0: hardware benchmark complete, lock batch_size" "p0,architecture,infra" \
"ADR-0015 #76. Characterize PostgresSaver write throughput; replace placeholder batch_size=50 and lock in SWARM_IMPLEMENTATION_ROADMAP.md. Execution of (closed) #76."
issue "Phase-0: governance dry-run green end-to-end" "p0,gate,governance" \
"All five gate components passing in a synthetic governance dry-run. Execution side of (closed) #93."

# ── P0 — Build prerequisites ────────────────────────────────────────────────
issue "Build reasoning_client (Agent SDK) + rate-window backpressure" "p0,architecture,infra" \
"Per ADR-0016. Thin reasoning_client over the Claude Agent SDK (setup-token, headless). Queue/resume against subscription rate windows; never spill to a metered API."
issue "Stand up local model serving + select/benchmark Tier-2 model" "p0,infra,ds-ml" \
"Ollama/llama.cpp on the Mac mini for Tier-2 (local LLM) work. Select and benchmark the open model for P1 bulk classification. See agents/MODEL_TIER_ASSIGNMENTS.md."
issue "Implement 4 data-pipeline agents + acquire SCF (SHA-256 + DVC)" "p0,agent,ds-ml,blocking" \
"Implement data-acquisition, data-curation, data-steward, embedding-agent (currently NotImplementedError stubs). Acquire real SCF, verify SHA-256, DVC-track. Emits ARA artifacts per ara/ARA_SPEC.md."

# ── Owner decision ──────────────────────────────────────────────────────────
issue "[OWNER] Sign off ADR-0016 (LLM execution routing)" "p0,governance,blocking" \
"docs/decisions/ADR-0016-llm-execution-routing.md is Proposed. Substantive change: narrows ADR-0002 to permit transient frontier inference over SCF-derived text (storage stays local). Owner sign-off required. (DIVERGENCE-01 decision tracked separately at #101.)"

# ── Integrity / spec ────────────────────────────────────────────────────────
issue "Reconcile gate-number drift: analysis cards vs GATES.md/graph.py" "high,gate,agent" \
"P1–P5 cards call the EDA review 'Gate 3' and results review 'Gate 4', but locked GATES.md + src/graph.py define Gate 2 = exploratory->confirmatory firewall, Gate 3 = analysis review. Cards are off-by-one against the firewall authority. Reconcile before any card drives gate routing."
issue "Schema hygiene: add Tools & MCP Servers section to 30 cards" "schema,agent,docs" \
"30 cards declare tools in frontmatter but omit the required '## Tools & MCP Servers' section (CARDS_SPEC.md). Will fail validation once the validator exists."
issue "Create MCP server registry" "registry,infra,agent" \
"Cards reference mcp-* servers (mcp-sap-validator, mcp-lab-notebook, mcp-qdrant, mcp-mlflow, mcp-dvc, mcp-github, mcp-phoenix) with no registry of endpoints/operations. Create one."
issue "Implement card validator (tools/generate_docs.py) per CARDS_SPEC" "ci,schema,scripts" \
"CARDS_SPEC.md assumes a Pydantic validator + doc generator that does not exist. Build it to surface the schema gaps above and auto-generate HANDOFFS/CONTRACTS/etc."

# ── Vertical slice + fan-out ────────────────────────────────────────────────
issue "Implement P1 (STRM NLP) end-to-end -> run Gate 1 (the kickoff slice)" "agent,ds-ml,gate" \
"The vertical slice that proves the machine: P1 on real SCF data through Gate 1. Exercises infra + data + local LLM + gates as one system. Win condition for 'kicked off'."
issue "Implement P2/P4/P5 (local ML) + P3 (frontier reasoning)" "agent,ds-ml" \
"Fan out the remaining analysis modules after the P1 slice works. P2/P4/P5 deterministic (Tier 1); P3 frontier (Tier 3)."
issue "hypothesis-formalizer + statistical-analyst -> Gate 2 firewall live" "agent,gate,architecture" \
"Implement the two protected agents and wire the structural exploratory->confirmatory firewall at Gate 2."

# ── Agent-Evolution / context-persistence loop ──────────────────────────────
issue "Wire orchestrator run-start grounding (PROJECT_STRUCTURE load + path guard)" "agent,process,architecture" \
"Spec done (orchestrator card v1.1.0 + PROJECT_STRUCTURE.md). Build: load the structure map at run start; block artifact writes outside canonical locations; new top-level dir => ADR."
issue "Close the Agent-Evolution read-back loop (pre-phase memory load)" "agent,process,architecture" \
"The platform writes failures (INCIDENTS.md, failure_events, lab_notebook) but does not read them back. Build the pre-phase load of open incidents + adversarial findings + recent failure_events into orchestrator context (ADR-0015 #72). Without this the evolution design is a no-op."
issue "Make adversarial findings a living register" "process,registry,adversary-finding" \
"Extend INCIDENTS.md or add docs/decisions/ADVERSARIAL_FINDINGS.md, content-addressed, consumed by the read-back loop. ADR-0015 captured #71-#80 in prose; make it a growing ledger."

echo "Done. Review: gh issue list --state open"
