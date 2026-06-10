# ADR-0011: Resilience and Fault Tolerance Architecture

**Status:** Accepted  
**Date:** 2026-06-10  
**Author:** Thomas Jones  
**Relates to:** ADR-0001 (LangGraph), ADR-0007 (PostgresSaver), AGENT_WORKFLOW.md

---

## Context

HC-GRC analysis runs can take hours. The question: what happens when the machine loses power, the laptop lid closes, the network drops, or the PostgreSQL process is killed mid-run? What survives? What is lost? What can be resumed?

This ADR defines the failure taxonomy for the platform, specifies what each failure mode destroys vs. preserves, and documents the architectural responses to each.

---

## Decision

**The platform is designed for resumable execution, not continuous execution.**

Every run is checkpointed at the granularity of a LangGraph node boundary via PostgresSaver. The definition of "resilient" is: any hardware or process failure between gate boundaries results in at most the loss of the current in-flight superstep, and the run can be resumed from the last checkpoint with no data integrity consequences.

Continuous operation (the workflow keeps running while the laptop is closed) requires a persistent compute host — a dedicated local server or remote VM. For single-machine nomad operation, the answer to "can I close my laptop?" is: **the state is safe; the computation pauses.**

---

## Failure Taxonomy

### F1 — Process Crash (Python killed, OOM, uncaught exception)

**What happens:** The Python process executing the LangGraph run dies mid-node.

**What survives:** Every node that completed before the crash. PostgresSaver writes a checkpoint at the completion of each node boundary. Incomplete nodes are not checkpointed — the partial state of the crashed node is lost.

**What is lost:** The work done by the node that was in-flight at the time of the crash.

**Recovery:** Restart the run with the same `thread_id`. LangGraph reads the latest checkpoint from PostgreSQL and resumes at the last completed node. The interrupted node re-executes from the top — this is why **node implementations must be idempotent**.

**Idempotency requirement:** Any node that has side effects (writes a file, calls an external API, appends to a database) must either (a) be idempotent by nature (pure computation), (b) check for prior completion before executing, or (c) use a transaction that rolls back on failure. The Gate 2 data split node is the critical example — it computes the split before `interrupt()` and the computation must be deterministic given the same state inputs so that re-execution after a crash produces the same split.

---

### F2 — Laptop Lid Closed / System Sleep

**What happens:** The OS suspends all processes. PostgreSQL may or may not be suspended cleanly depending on OS version and configuration. Python process is frozen.

**What survives:** All committed PostgreSQL checkpoints. In-flight computation in the current node is frozen and will resume when the lid opens.

**What is lost:** Nothing, typically. Modern macOS suspends processes cleanly. The Python process resumes exactly where it was.

**Edge case — network-dependent operations:** If a node is mid-HTTP-call to a local LLM server when the lid closes, the HTTP connection will time out. The node will receive a `ConnectionError` or `TimeoutError` on wake. LangGraph 1.1 retry middleware handles transient connection failures with exponential backoff. If retries are exhausted, the node fails and an error is logged to the `errors` state key. The run is checkpointed at the last successful node; a human must inspect `errors` and decide whether to resume or revert to the prior checkpoint.

**Recovery:** Open the lid. If the Python process is still alive (typical), execution continues automatically. If it died (rare), restart with the same `thread_id` — resumes from the last checkpoint.

---

### F3 — Power Loss (hard shutdown, battery dead)

**What happens:** All processes killed without SIGTERM. PostgreSQL journal may or may not be in a consistent state.

**What survives:** All data committed to PostgreSQL before the power event. PostgreSQL's WAL (write-ahead log) guarantees that committed transactions survive hard shutdowns. The last checkpoint written before power loss is intact.

**What is lost:** The in-flight superstep. Any Python state that was not yet checkpointed is lost.

**Recovery:** Restart PostgreSQL (`brew services start postgresql@16` or equivalent). Restart the LangGraph run with the same `thread_id`. LangGraph reads the last committed checkpoint and resumes. The analysis continues from the last successful node boundary.

**DVC data safety:** All files in `data/01-raw/` are DVC-tracked with SHA-256 manifests committed to Git. Power loss cannot corrupt DVC-tracked data — the data files survive in the filesystem, and DVC verifies integrity on next run. If a file write was in progress at power loss, the next DVC check will detect the integrity failure and flag the file as corrupted. The original can be re-acquired from the source.

---

### F4 — Network Connectivity Loss

**What happens:** The machine loses internet access mid-run.

**What survives:** All local computation. PostgreSQL checkpoints. Locally-cached embeddings. DVC-tracked data files.

**What is lost:** In-flight API calls (if using LLM API mode). Any in-progress web scraping or data download.

**Recovery design:** The platform is designed local-first (ADR-0006). All LLM inference uses local Ollama/vLLM by default. All data is pre-downloaded and DVC-tracked before the run begins. A network connectivity loss mid-run should therefore have no impact on execution.

**If API mode is selected:** LangGraph 1.1 retry middleware catches `httpx.ConnectError` and retries with exponential backoff. If the network is not restored within the retry window (default: 3 attempts, max 30s wait), the node fails. Error is logged to state. Run is checkpointed. Human resumes when connectivity is restored.

---

### F5 — Data Corruption (disk error, partial write)

**What happens:** A data file is written partially due to disk failure or abrupt termination during a write.

**What survives:** DVC-tracked files are verified against their SHA-256 manifest on every run. A corrupted file will be detected at ingestion time.

**What is lost:** The corrupted file.

**Recovery:** `dvc checkout` restores the last committed version of any DVC-tracked file from the DVC cache. If the local cache is also corrupted (hardware failure), the file must be re-acquired from the original source.

**Gate 2 immutability:** After Gate 2 approval, the test split manifest is written to state and locked (`data_manifest["locked"] == True`). Any attempt to re-run data processing after Gate 2 approval is blocked by the gate enforcement logic. The test split cannot be accidentally regenerated by a crash-and-resume cycle.

---

### F6 — PostgreSQL Failure

**What happens:** The PostgreSQL process crashes or the checkpoint tables become corrupted.

**What survives:** If PostgreSQL crashes cleanly (SIGTERM), WAL replay on restart recovers all committed transactions. If the data directory is corrupted (disk failure), all checkpoint data in that PostgreSQL instance is at risk.

**Mitigation — checkpoint export:** Before each gate interrupt, the platform exports the current checkpoint state to a JSON file in `data/02-interim/checkpoints/`. This is a safety net: if PostgreSQL is lost, the JSON export preserves the gate-approved state up to the last export. It does not capture in-flight computation, only gate-boundary snapshots.

```python
# Before each interrupt() call — idempotent, runs on the approved state
def export_checkpoint_snapshot(state: HCGRCState, gate: str) -> None:
    """Export gate-boundary checkpoint to filesystem as resilience backup."""
    snapshot_path = Path(f"data/02-interim/checkpoints/gate_{gate}_{state['run_id']}.json")
    snapshot_path.write_text(json.dumps({
        "run_id": state["run_id"],
        "gate": gate,
        "timestamp": datetime.utcnow().isoformat(),
        "gate_status": state["gate_status"],
        "hypotheses": state["hypotheses"],
        "data_manifest": state["data_manifest"],
    }, indent=2))
```

**Recovery from PostgreSQL loss:** Load the most recent JSON checkpoint snapshot. Use `graph.update_state()` to restore the checkpointed state into a new PostgreSQL thread. Resume from the last gate boundary.

---

## The Answer to "Can I Close My Laptop?"

| Scenario | State Safe? | Computation Continues? | Resume How? |
|----------|-------------|----------------------|-------------|
| Lid closed, process alive | ✅ Yes | ⏸ Paused | Opens automatically on wake |
| Lid closed, process dies | ✅ Yes | ❌ No | `python run.py --thread-id <id>` |
| Power loss | ✅ Yes (last checkpoint) | ❌ No | Restart PostgreSQL, then `python run.py --thread-id <id>` |
| Waiting at a gate interrupt | ✅ Yes (indefinitely) | ⏸ Paused | Resume whenever ready |
| Mid-superstep crash | ✅ Up to last node | ❌ No | `python run.py --thread-id <id>` |

**The short answer:** Close the lid. State is in PostgreSQL. The run pauses. When you come back, resume with the same thread ID. The worst case is re-running the last in-flight node. Gate decisions and pre-registered data splits are immutable.

---

## For Long-Running Analysis (Hours to Days)

If a run needs to execute continuously without the laptop being open — for example, P1 map-reduce over 1,400 controls — the appropriate solution is a persistent local compute host:

**Option A — Dedicated home server or mini PC.** PostgreSQL and the Python agent run on a machine that doesn't sleep. The laptop is only needed for gate approvals. SSH or VPN access for monitoring.

**Option B — Remote VM.** A cloud VM (or a VM running on a NAS or home server) hosts PostgreSQL and the Python agent. The laptop connects for gate approvals. Data-sovereignty is maintained as long as the VM is self-controlled and not a commercial provider with access to the data.

**Option C — Batch the run into gate-bounded segments.** Design the run to always pause at a gate before the multi-hour computation begins. Run the analysis while awake; come back to the next gate when it completes. The gate structure was designed for this pattern.

---

## Consequences

**Positive:**
- Arbitrary process failure results in at most one superstep of re-work
- Gate-approved decisions (data splits, pre-registration) survive any failure event
- DVC + SHA-256 + JSON checkpoint snapshots provide triple-layer data protection
- The architecture is nomad-compatible: run from any machine, close the laptop, resume later

**Negative:**
- True continuous execution requires a persistent host — laptop-only means paused, not running
- Idempotency requirement imposes a discipline on all node implementations

**Accepted tradeoff:** The research integrity guarantee (gate decisions are immutable and survive any failure) is more important than uninterrupted execution. A paused run that resumes correctly is vastly preferable to a running run that silently produces corrupted results.
