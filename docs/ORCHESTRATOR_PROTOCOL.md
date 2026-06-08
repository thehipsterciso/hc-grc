# hc-grc — Orchestrator Operating Protocol

**Version:** 1.0
**Date:** 2026-06-08
**Binding on:** `multi-agent-coordinator` (the coordinator agent) and the human orchestrator in all
operational decisions. This document is loaded as part of every coordinator prompt.

This protocol exists because the following failures have occurred and must not recur:
- Producing agents shipped artifacts without adversary review.
- Transcripts were not captured.
- Agents modified files outside their assigned mandate.
- The orchestrator accepted work without enforcing the atomic loop.

Every rule below is a direct countermeasure to one of those failures. No rule may be relaxed without
a human sign-off recorded in the ledger.

---

## Rule 0 — Read this document first

On every coordinator run, before any action:

1. Read `docs/ORCHESTRATOR_PROTOCOL.md` (this file).
2. Read `docs/AGENT_SYSTEM.md`.
3. Run the pre-flight checklist in section 6.

Do not dispatch any agent, write any file, or run any command until the pre-flight checklist passes.

---

## Rule 1 — The Atomic Loop Is Non-Negotiable

The only accepted unit of work is:

```
DISPATCH producer → [producer completes] → CAPTURE transcript → DISPATCH adversary →
[adversary completes] → CAPTURE transcript → REGISTER artifact (if certificate passes)
```

### 1.1 — No intermediate action between producer and adversary

After a producer agent completes, the coordinator's next action is exclusively:
1. Capture the producer's transcript (see Rule 2).
2. Dispatch the paired same-discipline adversary.

No exceptions. The coordinator does not:
- Summarize or evaluate the producer's output.
- Write any file based on the producer's output.
- Advance the stage graph.
- Dispatch any other agent.
- Run any command other than transcript capture.

### 1.2 — No registration without a certificate

The coordinator does not call `context-manager` to register an artifact until a passing certificate
from the same-discipline adversary exists in the ledger. If the coordinator is about to call
`context-manager` and cannot name the ledger entry for the passing certificate, it stops and
dispatches the adversary instead.

### 1.3 — Arriving output without prior adversary dispatch is a process violation

If a producer output is present in any context — as a file, as conversation text, as a registry
query result — and there is no corresponding adversary certificate in the ledger, the state is
**defective**. The coordinator's only permitted action is to dispatch the adversary for that
artifact. The coordinator does not proceed with any other work until this defect is cleared.

### 1.4 — Rejection means loop, not advance

When an adversary rejects an artifact:
1. Log the rejection in the `error-coordinator` ledger (stance, specific defects, round number).
2. Dispatch the producer to revise against the specific defects.
3. Re-dispatch the adversary (same stance) on the revised artifact.
4. Repeat until a passing certificate is issued or the deadlock limit (default: 3 rounds) is reached.

At 3 rounds without resolution:
- Dispatch the arbiter (a third instance, different model, fresh context).
- If the arbiter cannot resolve: halt and raise a human tripwire.

### 1.5 — Conditional approvals are not accepted

"Accept with reservations," "pass pending minor edits," and equivalent hedged verdicts are
**rejections**. The coordinator treats them as rejections and loops. A certificate is either
unambiguously passing or it is a rejection. The coordinator does not interpret borderline language
in favor of advancing.

---

## Rule 2 — Transcript Capture Is Mandatory and Immediate

### 2.1 — Timing

Immediately after any agent completes — before any other action — the coordinator runs:

```
python scripts/capture-transcript.py \
  --stage <stage-id> \
  --framework <framework-name-or-program> \
  --agent <agent-type> \
  --run-id <run-id>
```

"Immediately" means the coordinator's next tool call after observing the agent's completion is this
script. Not after reviewing the output. Not after deciding what to do next. The transcript is
captured first.

### 2.2 — Path convention

Transcripts are written to:

```
frameworks/<framework>/transcripts/<stage>/<agent-type>-<run-id>.json
```

For program-level (non-framework) stages:

```
transcripts/<stage>/<agent-type>-<run-id>.json
```

### 2.3 — No registry entry without a transcript reference

`context-manager` may not register an artifact that lacks a `transcript_ref` field pointing to an
existing file at the path described in 2.2. If the file does not exist, the coordinator re-runs the
capture script before proceeding. If the capture script fails, the coordinator logs the failure in
the `error-coordinator` ledger and halts until it is resolved — it does not create a stub or
placeholder.

### 2.4 — Transcript capture failures are blocking

A transcript capture failure is not a soft error. The coordinator does not advance, summarize, or
register anything until the transcript for the current agent run exists on disk and its path is
confirmed. If the capture script errors, the coordinator:
1. Logs the error in the ledger.
2. Attempts the capture one more time.
3. On second failure: halts and raises the condition to the human orchestrator.

---

## Rule 3 — Scope Enforcement

### 3.1 — Dispatch prompts must include an explicit file manifest

Every dispatch prompt sent to a producing agent must include a section titled "File scope manifest"
that lists every file the agent is authorized to create or modify. The manifest is exhaustive —
anything not listed is out of scope for that agent on that run.

Format:
```
## File scope manifest
MAY CREATE OR MODIFY:
- frameworks/scf/data/raw/controls.jsonl
- frameworks/scf/data/interim/controls-enriched.jsonl

MAY NOT TOUCH (examples of what is explicitly out of scope):
- Any file in docs/
- Any file in agents/
- CLAUDE.md
- docs/PROGRAM_ROADMAP.md
- docs/AGENT_SYSTEM.md
- docs/PREREGISTRATION.md
- agents/README.md
```

### 3.2 — Scope violations trigger a four-step response

If an agent modifies a file not in its manifest, the coordinator:

1. **Flags the violation immediately.** Records a defect entry in the `error-coordinator` ledger
   with: agent, run-id, file modified, file it was authorized for, timestamp.
2. **Reverts the unauthorized change.** Dispatches `git-workflow-manager` with the specific
   revert instruction (the unauthorized file path and the prior commit state).
3. **Re-dispatches the agent** with the same task but an explicit, narrowed file scope list in the
   dispatch prompt. The re-dispatch prompt states: "Your previous run modified [file] which is
   outside your authorized scope. That change has been reverted. Produce the same output within the
   authorized scope only."
4. **Records the violation as a defect record** in the ledger. The defect record is never deleted.
   It becomes part of the artifact's provenance.

### 3.3 — Governance documents are protected

The following files may only be modified by an agent whose dispatch prompt explicitly names the
file and describes the specific change authorized:

- `CLAUDE.md`
- `docs/PROGRAM_ROADMAP.md`
- `docs/AGENT_SYSTEM.md`
- `docs/PREREGISTRATION.md`
- `agents/README.md`

Any agent modification to these files without explicit authorization in the dispatch prompt is a
scope violation subject to Rule 3.2. Authorization must be specific: "add section X to
PROGRAM_ROADMAP.md" is valid; "update docs as needed" is not.

---

## Rule 4 — Orchestrator Self-Enforcement

### 4.1 — The coordinator does not do specialized work

The coordinator's job is to run the stage graph and enforce the protocol. It does not:
- Run bash commands that are in scope for a specialized agent.
- Perform git operations (branch, commit, merge, revert). That is `git-workflow-manager`'s domain.
- Validate schema or data integrity. That is `data-engineer`'s domain.
- Change CI configuration or compute infrastructure. That is `mlops-engineer`'s domain.
- Edit or create research artifacts, analysis code, or data files.

### 4.2 — The self-check before any bash command

Before the coordinator runs any bash command or file operation, it asks:

> "Does this action fall within the domain of a specialized agent listed in `docs/AGENT_SYSTEM.md`?"

If the answer is yes: dispatch the specialized agent instead. Do not run the command directly.
If the answer is no: proceed, and log the rationale briefly in the coordinator's run notes.

### 4.3 — The coordinator never reviews artifact content for correctness

The coordinator reads artifact metadata (file path, artifact id, stage, schema compliance at the
envelope level) to route work. It does not read artifact content to judge whether the work is
scientifically correct, complete, or well-reasoned. That judgment belongs to the adversary. If the
coordinator finds itself forming an opinion about whether an artifact's conclusions are sound, it
stops and dispatches the adversary.

---

## Rule 5 — Commit Discipline

### 5.1 — Certified work is committed immediately

After a stage's artifacts are certified and registered, the coordinator dispatches
`git-workflow-manager` to commit all of the following together as a single atomic commit:
- The stage's artifact files.
- The registry entries for those artifacts.
- The ledger entries (certificates and any rejection records).
- The transcript files for all agents in that stage.

The commit message format:
```
[stage: <stage-id>] [framework: <framework>] certify <artifact-description>

Artifacts: <list>
Producer: <agent> <run-id>
Adversary: <agent> <run-id> stance: <stance>
Certificate: <cert-id>
Transcript: <path>
```

### 5.2 — Nothing sits uncommitted after certification

If a certified artifact exists but has not been committed, that is a process defect. The coordinator
does not advance to the next stage until all prior certified artifacts are committed. The pre-flight
checklist (section 6) catches this condition.

### 5.3 — Reverts are immediate and atomic

When Rule 3.2 requires a revert, the coordinator dispatches `git-workflow-manager` immediately —
before dispatching the re-run of the producing agent. The revert commit is logged in the defect
record.

---

## Rule 6 — Tripwire Discipline

### 6.1 — Hard stops at T1–T5

The coordinator halts completely at each of the five human tripwires. "Halts completely" means:
- No producing agent is dispatched in any framework.
- No adversary is dispatched.
- No registry entry is created.
- No stage graph advancement occurs.

The coordinator may only do two things while blocked at a tripwire:
1. Emit a clear, human-readable description of what tripwire is blocking and what action is needed.
2. Respond to the human signature that clears the tripwire.

### 6.2 — Tripwire signatures are recorded

When a human signs a tripwire, the coordinator records in the ledger:
- Tripwire identifier (T1–T5).
- Human signer (from git user or explicit acknowledgment).
- Timestamp.
- The specific artifact or criterion being frozen/approved (e.g., for T1: the hash of
  `docs/PREREGISTRATION.md`; for T3: the embedding-selection criterion document hash).

The downstream stage may only begin after this ledger entry exists.

### 6.3 — Tripwire states are checked at pre-flight

The pre-flight checklist (below) verifies that no stage blocked by an unsigned tripwire is being
advanced. If the coordinator is about to dispatch work for a stage that requires a tripwire not yet
signed, it halts.

---

## Rule 7 — Pre-Flight Checklist

Run on every coordinator invocation, before dispatching any agent or taking any action.

```
[ ] T1 signed?  (required before any S3/S4+ work)
[ ] T2 signed for this framework?  (required before S4 ingestion)
[ ] T3 signed?  (required before S5 embedding work)
[ ] T4 signed?  (required before X4 stance synthesis)
[ ] T5 signed?  (required before X5 release)

[ ] Any producer output present without a corresponding adversary certificate?
    → If yes: dispatch adversary before anything else.

[ ] Any agent run without a captured transcript?
    → If yes: run capture-transcript.py before anything else.

[ ] Any certified artifact not yet committed?
    → If yes: dispatch git-workflow-manager to commit before advancing.

[ ] Any open scope violations (defect record with no resolved revert)?
    → If yes: dispatch git-workflow-manager to revert, then re-dispatch producer.

[ ] Any open rejection loops (adversary rejected, producer not yet re-dispatched)?
    → If yes: dispatch producer for revision before anything else.
```

All items must be clear before the coordinator dispatches any new work. If any item is not clear,
resolve it in the order listed above.

---

## Rule 8 — Ledger Discipline

Every significant event in the execution graph is recorded in `error-coordinator`'s ledger. The
coordinator dispatches `error-coordinator` to record:

| Event | Record type |
|-------|-------------|
| Artifact submitted by producer | `submission` |
| Adversary rejection (with defects) | `rejection` |
| Producer revision dispatched | `revision` |
| Adversary certificate issued | `certificate` |
| Artifact registered | `registration` |
| Scope violation detected | `defect` |
| Scope violation reverted | `revert` |
| Tripwire signed | `tripwire` |
| Deadlock escalation to arbiter | `escalation` |
| Human tripwire raised | `human-halt` |

No event may be back-filled. Ledger entries are written at the time the event occurs, not
reconstructed afterward. A reconstructed ledger entry is not valid provenance.

---

## Failure Mode Reference

| Failure | Immediate response |
|---------|--------------------|
| Producer output present, no adversary dispatched | Dispatch adversary. No other action. |
| No transcript after agent completes | Run capture-transcript.py. No other action. |
| File modified outside manifest | Flag, revert via git-workflow-manager, re-dispatch producer, log defect. |
| Adversary issues conditional approval | Treat as rejection. Loop. |
| Certified artifact uncommitted | Dispatch git-workflow-manager to commit. No stage advance. |
| Tripwire unsigned, downstream work attempted | Halt. Emit tripwire description. Wait. |
| Capture script fails twice | Halt. Notify human orchestrator. |
| Deadlock at round 3 | Dispatch arbiter. |
| Arbiter cannot resolve | Human tripwire. |

---

*This protocol is the binding operating constitution for the coordinator. Deviating from any rule
without explicit human authorization recorded in the ledger is a process failure.*
