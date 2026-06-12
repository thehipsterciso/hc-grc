# HC-GRC — Kickoff Readiness

**Maintained by:** Orchestrator (T-00)
**Status:** Pre-execution — assembling Definition of Ready
**Last updated:** 2026-06-12

> Purpose: a single administrative view of what must be true before the agent swarm
> executes on real SCF data, the critical path to get there, and the prioritized
> backlog that closes the gap. Owner is required only for high-stakes decisions
> (marked **[OWNER]**); all other work proceeds autonomously.

---

## 1. Where we actually are (verified 2026-06-12)

| Layer | State |
|-------|-------|
| Architecture & governance | Complete — 15 ADRs accepted (ADR-0016 proposed) |
| Agent specifications | **49** AGENT.md cards (README still says 48 — stale) |
| LangGraph skeleton | Phase 0 real and tested; Gate 1 interrupt/resume works |
| Infrastructure | MLflow + Phoenix + Qdrant + Postgres provisioned, idle |
| **Agent implementations** | **12 of 49 have code; all 12 are `NotImplementedError` stubs** |
| **LLM integration** | **None in code** — no client wired anywhere |
| **Real SCF data** | **Not acquired** — `data/01-raw/` empty |

**Honest summary:** a sound governance design and a tested-but-hollow topology.
The executable research system is roughly 10–15% built. The five analytical
modules (P1–P5) that are the scientific point are all stubs.

## 2. Locked decisions

| # | Decision | Ref |
|---|----------|-----|
| D1 | LLM routing by stakes: deterministic ML + low-stakes reasoning local on the Mac mini (24/7); high-stakes reasoning on Claude Max 20x via Agent SDK; **no metered API**; $200/mo fixed envelope; bursty/queued is fine | ADR-0016 (proposed) |
| D2 | Operating model: autonomous; owner only for high-stakes calls; **80% rigor / 20% speed** | — |

## 3. Definition of Ready — gate to real execution

Nothing in §5 P2+ runs until every box is checked.

### Track A — Phase-0 sign-off (ADR-0015 #71)
- [ ] Gate-1 synthetic dry-run produces a valid gate record
- [ ] PostgresSaver checkpointing confirmed on the Mac mini
- [ ] `compute_data_split()` idempotency test passes (bit-identical)
- [ ] Hardware benchmark → lock `batch_size` (placeholder = 50)
- [ ] Governance dry-run green end-to-end

### Track B — Specs & decisions
- [ ] **[OWNER]** Sign off ADR-0016 (LLM routing + sovereignty carve-out)
- [x] Create **Report Agent** card — `agents/12-academic-dissemination/report-agent/AGENT.md` (2026-06-12)
- [x] Define **ARA artifact schema** — `ara/ARA_SPEC.md` (2026-06-12; `src/ara/models.py` generation is a follow-up build task)
- [x] Add **tier assignment** — `agents/MODEL_TIER_ASSIGNMENTS.md` registry (2026-06-12; per-card `model_tier:` frontmatter + CARDS_SPEC bump is a follow-up)
- [ ] **[OWNER]** Resolve **DIVERGENCE-01** metric (P1 design depends on it)
- [x] Fix protected-agent **name drift** — corrected in GATES.md + ADR-0015 erratum (2026-06-12)
- [ ] **Reconcile gate-number drift** (NEW, integrity-relevant): the P1–P5 analysis
      cards call the exploratory/EDA review "Gate 3" and the results review "Gate 4",
      but the locked GATES.md + `src/graph.py` define Gate 2 = exploratory→confirmatory
      firewall and Gate 3 = analysis/results review. The cards are off-by-one against
      the firewall authority. Must reconcile before any card drives gate routing.

### Track C — Build prerequisites
- [ ] `reasoning_client` abstraction over the Agent SDK (setup-token, headless)
- [ ] Local model serving (Ollama/llama.cpp) + Tier-2 open model selected/benchmarked
- [ ] Rate-window backpressure: frontier work queues/resumes, never spills to API
- [ ] Data-pipeline agents implemented (4) → SCF acquisition + DVC + embeddings
- [ ] **P1 module implemented** (the vertical slice — §4)

## 4. Critical path — prove the machine with one module, then fan out

```
ADR-0016 sign-off + Report/ARA/tier specs ─┐
Phase-0 sign-off (Track A)                  ─┼─► reasoning_client + local serving
                                             │            │
                                             │            ▼
                                             └─► Data pipeline (acquire → DVC → embed)
                                                          │
                                                          ▼
                                              P1 end-to-end ─► Gate 1 ─► first real output
                                                          │
                                                          ▼
                                       THEN fan out P2–P5 + downstream agents
```

**Definition of "kicked off":** one real analytical module (P1) runs on real SCF
data through Gate 1. That single slice exercises infra + data + local LLM +
subscription reasoning + gates as one working system. Everything after is breadth.

## 5. Prioritized backlog

**P0 — blockers**
1. **[OWNER]** Sign ADR-0016
2. Complete Phase-0 sign-off (Track A, 5 items)
3. Build `reasoning_client` + rate-window backpressure
4. Stand up local serving + select Tier-2 model
5. Implement 4 data-pipeline agents + acquire SCF (SHA-256 + DVC)

**P1 — specs that unblock build (cheap, parallel with P0)**
6. ~~Create Report Agent card~~ ✅ 2026-06-12
7. ~~Define ARA artifact schema~~ ✅ 2026-06-12 (`ara/ARA_SPEC.md`; model codegen pending)
8. ~~Add tier assignment to all cards~~ ✅ 2026-06-12 (`agents/MODEL_TIER_ASSIGNMENTS.md`; per-card field pending)
9. **[OWNER]** Resolve DIVERGENCE-01
10. ~~Reconcile protected-agent name drift~~ ✅ 2026-06-12 (GATES.md + ADR-0015 erratum)
10a. **Reconcile gate-number drift** (NEW): analysis cards off-by-one vs locked GATES.md/graph.py firewall

**P2 — first analysis slice**
11. Implement P1 (STRM NLP) end-to-end → run Gate 1

**P3 — fan-out (only after the slice works)**
12. Implement P2/P4/P5 (local ML) + P3 (frontier reasoning)
13. hypothesis-formalizer + statistical-analyst → Gate 2 firewall live
14. Schema hygiene: 30 cards missing Tools sections; MCP registry; card validator

**P4 — deferred, NOT needed to kick off**
Dissemination (team 12), business/digital (13), most of inference/training/
optimization (05–08). Post-findings work; do not let it pull focus.

## 6. The binding constraint, stated once

Frontier reasoning runs inside a fixed $200/month subscription envelope with rate
windows. This is an ordinary budget the framework plans against — the design
response is: keep frontier volume small (local-heavy routing) and let frontier
work queue and resume against rate windows. Not a risk, a constraint. Handled.
