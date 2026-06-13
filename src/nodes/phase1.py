"""
Phase 1 LangGraph node wrappers.

Topology (Phase 1 exploratory subgraph):

  phase_1_entry
      ↓
  data_pipeline          ← DataAcquisitionAgent → DataCurationAgent
      ↓                    → DataStewardAgent → EmbeddingAgent (sequential)
  exploratory_phase      ← P1 → P2 → P3 → P4 → P5 (sequential now;
      ↓                    TODO: parallelize via Send() when implementations live)
  hypothesis_formalize   ← HypothesisFormalizerAgent
      ↓
  gate_2                 ← (in gates.py)
      ↓
  [approved: confirmatory_entry | rejected: exploratory_phase loop]

Parallelization note:
  P1-P5 are currently called sequentially within exploratory_phase_node.
  When implementations are live, replace with Send()-based fan-out:
    def dispatch_exploratory(state) -> list[Send]:
        return [Send("p1_node", state), Send("p2_node", state), ...]
  Each worker appends to eda_artifacts and eda_agent_statuses via append reducers.
  After all workers complete, route to hypothesis_formalize.
  See LangGraph map-reduce pattern for the fan-in wiring.

NotImplementedError handling:
  Each P1-P5 call is wrapped in try/except NotImplementedError. Agents that
  have not been implemented yet record a "stub_pending" status to eda_agent_statuses.
  This allows the graph to execute in tests and governance dry-runs without
  requiring all research implementations to be live.
"""

from __future__ import annotations

import datetime
from typing import Any

from ..agents import (
    DataAcquisitionAgent,
    DataCurationAgent,
    DataStewardAgent,
    EmbeddingAgent,
    HypothesisFormalizerAgent,
    P1StrmNlpAgent,
    P2ControlTopologyAgent,
    P3RegulatoryConvergenceAgent,
    P4RiskBlindspotAgent,
    P5AiGovernanceAgent,
)
from ..state import HCGRCState

# ── Agent singletons ──────────────────────────────────────────────────────────
# Created once at module load; nodes call instance methods.

_data_acquisition = DataAcquisitionAgent()
_data_curation = DataCurationAgent()
_data_steward = DataStewardAgent()
_embedding_agent = EmbeddingAgent()

_p1 = P1StrmNlpAgent()
_p2 = P2ControlTopologyAgent()
_p3 = P3RegulatoryConvergenceAgent()
_p4 = P4RiskBlindspotAgent()
_p5 = P5AiGovernanceAgent()
_hypothesis_formalizer = HypothesisFormalizerAgent()


# ── Helpers ───────────────────────────────────────────────────────────────────


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _stub_status(agent_id: str, run_id: str) -> dict[str, Any]:
    """Status record written when an agent has not been implemented yet."""
    return {
        "agent_id": agent_id,
        "status": "stub_pending",
        "note": (
            f"{agent_id} implementation pending — NotImplementedError caught. "
            "Will run when Phase 1 is live on Mac mini."
        ),
        "timestamp_utc": _utc_now(),
        "run_id": run_id,
    }


def _failed_status(agent_id: str, run_id: str, exc: BaseException) -> dict[str, Any]:
    """Status record written when an agent raises a real runtime error (not a stub).

    Produces the 'failed' status the state schema documents, so one agent's bug is
    recorded and isolated instead of crashing the whole subgraph (#148)."""
    return {
        "agent_id": agent_id,
        "status": "failed",
        "error": repr(exc),
        "note": f"{agent_id} raised {type(exc).__name__} during execution",
        "timestamp_utc": _utc_now(),
        "run_id": run_id,
    }


def _failure_event(agent_id: str, run_id: str, exc: BaseException) -> dict[str, Any]:
    """Failure event for Agent-Evolution / operator monitoring (append reducer)."""
    return {
        "event_type": "agent_runtime_error",
        "agent_id": agent_id,
        "error": repr(exc),
        "run_id": run_id,
        "timestamp_utc": _utc_now(),
    }


def _prov(activity: str, run_id: str, **kwargs: Any) -> dict[str, Any]:
    """Minimal PROV-DM compatible activity record."""
    return {
        "activity": activity,
        "run_id": run_id,
        "timestamp_utc": _utc_now(),
        **kwargs,
    }


# ── Data pipeline node ────────────────────────────────────────────────────────


def data_pipeline_node(state: HCGRCState) -> dict[str, Any]:
    """
    Orchestrates the sequential data pipeline:
      DataAcquisitionAgent → DataCurationAgent → DataStewardAgent → EmbeddingAgent

    Each stage is blocked on its predecessor completing successfully. If any stage
    raises NotImplementedError (Phase 1 stub), the pipeline records a stub_pending
    status and returns with phase_1_ready=False.

    When all four stages complete: sets phase_1_ready=True in state.
    """
    run_id = state["run_id"]
    pipeline_statuses: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    prov: list[dict[str, Any]] = []

    stages = [
        (_data_acquisition, "data-acquisition"),
        (_data_curation, "data-curation"),
        (_data_steward, "data-steward"),
        (_embedding_agent, "embedding-agent"),
    ]

    accumulated_update: dict[str, Any] = {}

    for agent, agent_id in stages:
        try:
            stage_update = agent.run(state)
            pipeline_statuses.append({
                "agent_id": agent_id,
                "status": "completed",
                "timestamp_utc": _utc_now(),
                "run_id": run_id,
            })
            # Merge stage update into accumulated (agent writes prov_activities etc.)
            for k, v in stage_update.items():
                if k == "prov_activities" and isinstance(v, list):
                    prov.extend(v)
                else:
                    accumulated_update[k] = v
        except NotImplementedError as exc:
            # Only an unimplemented agent legitimately raises NotImplementedError.
            # Once IMPLEMENTED, a NotImplementedError is a real bug, not a stub (#202).
            if getattr(agent, "IMPLEMENTED", False):
                pipeline_statuses.append(_failed_status(agent_id, run_id, exc))
                failures.append(_failure_event(agent_id, run_id, exc))
                prov.append(_prov(
                    f"data_pipeline_{agent_id.replace('-', '_')}_failed", run_id, error=repr(exc),
                ))
                break
            pipeline_statuses.append(_stub_status(agent_id, run_id))
            # Cannot continue pipeline if a stage is not implemented
            # Phase 1 is not ready until all four stages complete
            prov.append(_prov(
                f"data_pipeline_{agent_id.replace('-', '_')}_stub",
                run_id,
                note="NotImplementedError — Phase 1 implementation pending",
            ))
            break
        except Exception as exc:
            # A real runtime error in one stage is recorded as 'failed' and halts
            # the pipeline (later stages depend on earlier ones) without crashing
            # the graph or discarding prior stages' output (#148). A governance
            # violation must propagate — it is not a recoverable pipeline fault.
            from ..agents.base import SAPViolationError
            pipeline_statuses.append(_failed_status(agent_id, run_id, exc))
            failures.append(_failure_event(agent_id, run_id, exc))
            prov.append(_prov(
                f"data_pipeline_{agent_id.replace('-', '_')}_failed", run_id, error=repr(exc),
            ))
            if isinstance(exc, SAPViolationError):
                raise
            break

    # phase_1_ready only if all four stages completed (no stubs/failures in statuses)
    all_complete = all(s["status"] == "completed" for s in pipeline_statuses)

    return {
        **accumulated_update,
        "phase_1_ready": all_complete,
        "eda_agent_statuses": pipeline_statuses,
        "failure_events": failures,
        "prov_activities": prov + [_prov("data_pipeline_node", run_id,
                                         all_complete=all_complete)],
    }


# ── Exploratory phase node ────────────────────────────────────────────────────


def exploratory_phase_node(state: HCGRCState) -> dict[str, Any]:
    """
    Calls P1-P5 exploratory analysis sequentially. Catches NotImplementedError
    per agent and records stub_pending status.

    PARALLELIZATION NOTE: When P1-P5 implementations are live, replace this node
    with a Send()-based fan-out. See module docstring for the pattern.

    P1-P5 are PROTECTED agents — they are called via __call__() which dispatches
    to run_exploratory() based on state["phase"]. Each returns a partial state
    update dict with eda_artifacts appended.

    Gate 2 is NOT required here — this is exploratory phase. Each agent internally
    enforces the EXP_ artifact naming convention and no p-value decision language.
    """
    run_id = state["run_id"]
    agent_statuses: list[dict[str, Any]] = []
    all_eda_artifacts: list[str] = []
    failures: list[dict[str, Any]] = []
    prov: list[dict[str, Any]] = []

    research_agents = [
        (_p1, "p1-strm-nlp"),
        (_p2, "p2-control-topology"),
        (_p3, "p3-regulatory-convergence"),
        (_p4, "p4-risk-blindspot"),
        (_p5, "p5-ai-governance"),
    ]

    for agent, agent_id in research_agents:
        try:
            # __call__ dispatches to run_exploratory() based on state["phase"]
            agent_update = agent(state)
            artifacts = agent_update.get("eda_artifacts", [])
            all_eda_artifacts.extend(artifacts)
            agent_statuses.append({
                "agent_id": agent_id,
                "status": "completed",
                "artifact_count": len(artifacts),
                "timestamp_utc": _utc_now(),
                "run_id": run_id,
            })
            prov.append(_prov(f"exploratory_{agent_id.replace('-', '_')}", run_id,
                               artifact_count=len(artifacts)))
        except NotImplementedError as exc:
            if getattr(agent, "IMPLEMENTED", False):
                # Real bug from an implemented agent — record as failed, not stub (#202).
                agent_statuses.append(_failed_status(agent_id, run_id, exc))
                failures.append(_failure_event(agent_id, run_id, exc))
                prov.append(_prov(
                    f"exploratory_{agent_id.replace('-', '_')}_failed", run_id, error=repr(exc),
                ))
                continue
            agent_statuses.append(_stub_status(agent_id, run_id))
            prov.append(_prov(
                f"exploratory_{agent_id.replace('-', '_')}_stub",
                run_id,
                note="NotImplementedError — Phase 1 implementation pending",
            ))
        except Exception as exc:
            # P1-P5 are independent — one agent's runtime error is recorded as
            # 'failed' and the loop continues so the other agents' artifacts are
            # preserved, instead of crashing the whole exploratory subgraph (#148).
            # A governance violation must propagate, not be swallowed.
            from ..agents.base import SAPViolationError
            if isinstance(exc, SAPViolationError):
                raise
            agent_statuses.append(_failed_status(agent_id, run_id, exc))
            failures.append(_failure_event(agent_id, run_id, exc))
            prov.append(_prov(
                f"exploratory_{agent_id.replace('-', '_')}_failed", run_id, error=repr(exc),
            ))

    all_stubs = all(s["status"] == "stub_pending" for s in agent_statuses)
    any_complete = any(s["status"] == "completed" for s in agent_statuses)
    exploratory_complete = any_complete and not all_stubs

    # exploratory_complete = True only if at least one agent returned real results.
    # In Phase 1 dry-run (all stubs), stays False — Gate 2 checklist will surface this.
    return {
        "phase": "phase_1",
        "eda_artifacts": all_eda_artifacts,
        "eda_agent_statuses": agent_statuses,
        "failure_events": failures,
        "exploratory_complete": exploratory_complete,
        "prov_activities": prov + [_prov("exploratory_phase_node", run_id,
                                          exploratory_complete=exploratory_complete)],
    }


# ── Hypothesis formalization node ─────────────────────────────────────────────


def hypothesis_formalize_node(state: HCGRCState) -> dict[str, Any]:
    """
    Calls HypothesisFormalizerAgent to produce the pre-registered hypothesis set.

    Runs after exploratory analysis completes. Output populates state["hypothesis_set"]
    with FormalHypothesis dicts. This is the set that gets locked at Gate 2.

    HypothesisFormalizerAgent is PROTECTED. Its run_exploratory() builds hypotheses
    from EDA outputs and HARKing validation stub. Output is the Gate 2 input.
    """
    run_id = state["run_id"]
    agent_id = "hypothesis-formalizer"

    try:
        agent_update = _hypothesis_formalizer(state)
        hypothesis_count = len(agent_update.get("hypothesis_set", []))
        return {
            **agent_update,
            "prov_activities": [_prov("hypothesis_formalization", run_id,
                                       hypothesis_count=hypothesis_count)],
        }
    except NotImplementedError as exc:
        # Only an unimplemented agent legitimately raises NotImplementedError;
        # once IMPLEMENTED it is a real bug, not a stub (#237).
        if getattr(_hypothesis_formalizer, "IMPLEMENTED", False):
            return {
                "eda_agent_statuses": [_failed_status(agent_id, run_id, exc)],
                "failure_events": [_failure_event(agent_id, run_id, exc)],
                "prov_activities": [_prov("hypothesis_formalization_failed", run_id,
                                          error=repr(exc))],
            }
        return {
            "eda_agent_statuses": [_stub_status(agent_id, run_id)],
            "prov_activities": [_prov("hypothesis_formalization_stub", run_id,
                                       note="NotImplementedError — Phase 1 pending")],
        }
    except Exception as exc:
        # Isolate a real runtime error: record it instead of crashing the graph,
        # and emit a failure_event for the monitor (#35). SAP violations propagate.
        from ..agents.base import SAPViolationError
        if isinstance(exc, SAPViolationError):
            raise
        return {
            "eda_agent_statuses": [_failed_status(agent_id, run_id, exc)],
            "failure_events": [_failure_event(agent_id, run_id, exc)],
            "prov_activities": [_prov("hypothesis_formalization_failed", run_id,
                                      error=repr(exc))],
        }


# ── Confirmatory entry stub ───────────────────────────────────────────────────


def confirmatory_entry_node(state: HCGRCState) -> dict[str, Any]:
    """
    Entry point for Phase 2 confirmatory analysis subgraph.

    Gate 2 approval is required before this node runs (enforced by
    route_after_gate_2 in orchestrator.py). The confirmatory subgraph
    (statistical-analyst + P1-P5 confirmatory runs) is Phase 2 mechanism work.
    """
    return {
        "phase": "phase_2",
        "prov_activities": [
            _prov(
                "confirmatory_entry",
                state["run_id"],
                note="Phase 2 confirmatory subgraph — not yet implemented",
            )
        ],
    }
