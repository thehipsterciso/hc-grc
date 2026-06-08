# hc-grc — Coordinator Cron Protocol

**Version:** 1.0
**Date:** 2026-06-08
**Loaded by:** `multi-agent-coordinator` on every scheduled run, before any action.

This document is part of the coordinator's prompt on every invocation. Every run follows this exact
sequence. Skipping any step is a process violation.

---

## The invariant

Every coordinator run, regardless of what triggered it, follows the same eight-step sequence in
order. Steps 1–5 are diagnostic and corrective. Steps 6–8 are forward work. Forward work does not
begin until all diagnostic steps are clean.

---

## Step 1 — Load the operating constitution

Before doing anything else:

1. Read `docs/ORCHESTRATOR_PROTOCOL.md`.
2. Read `docs/AGENT_SYSTEM.md`.

Do not proceed until both files are in context. If either file is missing or unreadable, halt and
notify the human orchestrator — the program cannot run without its operating rules.

---

## Step 2 — Check for uncertified producer output (process violations)

Use filesystem-based detection as the PRIMARY mechanism:

1. For each known artifact output path (derivable from stage graph + scope manifests), check:
   - Does the artifact file exist?
   - Does a corresponding certificate exist at `ledger/certificates/<cert-id>.json`?
2. A file with no certificate is a **process violation** regardless of ledger state.

Ledger query is SECONDARY cross-check:
- For each producing agent run recorded in the ledger since the last certified registration, verify
  a same-discipline adversary certificate exists in the ledger for that run's output.

For each process violation found:
1. Log the violation in `error-coordinator`'s ledger as a `process-violation` record with the
   producer agent, run-id, artifact path, and timestamp of the gap.
2. Dispatch the same-discipline adversary for that artifact immediately.

After all violations have a dispatched adversary (not necessarily a completed certificate):
- If any adversary run newly completes during this step, capture its transcript before continuing.
- Do not proceed to Step 3 while any adversary dispatch from this step is still outstanding.
- The 3-round/arbiter loop limit applies to these remediation adversaries.

---

## Step 3 — Check for uncaptured transcripts

For every agent run in the ledger (producers and adversaries), verify that a transcript file
exists at its expected path under `frameworks/<framework>/transcripts/` or `transcripts/`.

For each run with no transcript file:
1. Run `scripts/capture-transcript.py` with the correct `--stage`, `--framework`, `--agent`,
   and `--run-id` arguments.
2. If the capture script fails twice, log a `transcript-capture-failure` defect in the ledger
   and flag it for human resolution. Do not attempt to proceed past this run's work in the stage
   graph until the transcript exists or the human explicitly releases the block.
3. If the transcript cannot be recovered (the agent run is gone from context), log a
   `transcript-irrecoverable` defect. The artifact associated with that run is quarantined: it
   cannot be registered or consumed downstream until the defect is resolved.

---

## Step 4 — Check for uncommitted certified work

Query the git status of the working tree. Any certified artifact, registry entry, ledger entry, or
transcript file that is not yet committed is a process gap.

For each such gap:
1. Dispatch `git-workflow-manager` with the list of uncommitted certified files and the commit
   message template from `docs/ORCHESTRATOR_PROTOCOL.md` Rule 5.1.
2. Wait for the commit to complete and its transcript to be captured before proceeding.

Do not advance to Step 5 while any uncommitted certified work exists.

---

## Step 5 — Check for open scope violations

Query the `error-coordinator` ledger for any `defect` records of type `scope-violation` that do
not have a corresponding `revert` record.

For each unresolved scope violation:
1. Dispatch `git-workflow-manager` to revert the unauthorized file change.
2. After the revert is confirmed and committed, re-dispatch the producing agent with a corrected
   dispatch prompt that includes an explicit, narrowed file scope manifest.
3. Do not advance to Step 6 until all scope violations are resolved and the affected artifacts
   have re-entered the atomic loop.

---

## Step 6 — Run the pre-flight checklist

Before dispatching any new work, run the full pre-flight checklist from
`docs/ORCHESTRATOR_PROTOCOL.md` Rule 7.

All items must be clear. If any item surfaces a new condition not already handled in Steps 2–5,
handle it by the same rules before proceeding.

---

## Step 7 — Determine what stage is ready to advance

With the diagnostic steps clean:

1. Read the stage graph from `docs/PROGRAM_ROADMAP.md`.
2. For each stage in the graph, check:
   - Are all upstream stage dependencies certified and registered?
   - Is the required tripwire for this stage signed?
     * T1 blocks S3 and any stage registering findings (S5–S9, X1–X4).
     * T2 blocks only the specific framework whose T2 is unsigned; other frameworks can proceed.
     * T3 blocks S5 (embedding work across all frameworks).
     * T4 blocks X4 (stance synthesis across all frameworks).
     * T5 blocks X5 (release across all frameworks).
   - Are there any open rejection loops for this stage's in-progress artifacts?
3. Identify the set of stages that are ready to begin or continue.
4. Prioritize:
   - First: close any open rejection loops (re-dispatch a producer with revision instructions).
   - Second: advance the critical path (P0 → P1 → S3 → SCF S4 → S5 → ...).
   - Third: advance parallel per-framework stages.

If a program-level tripwire (T1, T3, T4, T5) is unsigned and is blocking all ready stages, emit
a clear description of which tripwire, what it protects, and what the human must do to clear it.
Then halt. Do not attempt workaround work in a different stage while a program-level tripwire is
blocking. If only a per-framework tripwire T2 is unsigned, proceed with other frameworks.

---

## Step 8 — Dispatch producer and adversary as an atomic pair

For each stage unit of work ready to begin, the coordinator dispatches the producer and adversary
together in the same coordinator run. The sequence is:

```
1. Generate the run-id for this dispatch (format: <stage>-<agent-role>-<ISO8601-date>-<seq>).
   Write the sentinel file at ledger/in-progress/<run-id>.json with status: "producer_dispatched".

2. Construct the dispatch prompt for the producing agent.
   - Include the agent's full identity (role/model@hc-macbook-pro.local).
   - Include the file scope manifest (Rule 3.1 of ORCHESTRATOR_PROTOCOL.md).
   - Include the Definition of Done requirements the adversary will check.
   - Inject the run-id into the prompt so the agent includes it in the footer.
   - Include the stage, framework, and run-id.

3. Dispatch the producing agent.

4. Wait for the producer to complete.

5. Immediately run: python scripts/capture-transcript.py --stage <stage> --framework <framework>
   --agent <agent-identity> --run-id <run-id> (producer's transcript).

6. Update sentinel file: status: "adversary_dispatched".

7. Construct the dispatch prompt for the same-discipline adversary.
   - Include the adversary's full identity (role/model@hc-macbook-pro.local).
   - Include the artifact path, the producer's run-id, the rotating review stance for this round.
   - Include the adversary's reject checklist for this discipline.

8. Dispatch the adversary.

9. Wait for the adversary to complete.

10. Immediately run: python scripts/capture-transcript.py --stage <stage> --framework <framework>
    --agent <agent-identity> --run-id <run-id> (adversary's transcript).

11. If certificate passes: dispatch context-manager to register, dispatch error-coordinator to
    record the certificate, delete sentinel file, then proceed to Step 4 (commit the artifacts).

12. If certificate is a rejection: dispatch error-coordinator to record the rejection, then
    return to Step 8 step 2 with the producer re-dispatch (revision pass).
```

A coordinator run that dispatches a producer and does not complete through at least the adversary
dispatch before yielding is a partial run. If the coordinator must yield mid-loop (e.g., because
of token limits), it must record the in-progress state in the ledger with enough detail that the
next run can resume at the correct point without repeating completed steps.

### Never leave a producer without an adversary in the same run

The rule is: **no coordinator run ends with a producer dispatch and no adversary dispatch.** If the
coordinator cannot complete both in a single run, it must not dispatch the producer. It dispatches
nothing and records in the ledger that the unit of work is pending a full atomic run.

---

## Summary of step ordering

| Step | Action | Blocks if not clean |
|------|--------|---------------------|
| 1 | Load operating constitution | Yes — halt if files missing |
| 2 | Clear uncertified producer output | Yes — dispatch adversaries first |
| 3 | Capture missing transcripts | Yes — capture or flag before advancing |
| 4 | Commit uncommitted certified work | Yes — commit before advancing |
| 5 | Resolve open scope violations | Yes — revert and re-run before advancing |
| 6 | Pre-flight checklist | Yes — all items must be clear |
| 7 | Determine ready stages | — |
| 8 | Dispatch producer + adversary as a pair | Yes — never one without the other |

*This document is the coordinator's operating sequence. It is not advisory. Every deviation is a
process failure and must be logged as a defect in the `error-coordinator` ledger.*
