# Hardening Log

**Type:** Append-only register of the end-to-end hardening effort.
**Scope:** The LangChain (reasoning seam), LangGraph (graph/state/checkpointer/gates),
and Phoenix/OpenTelemetry (the self-hosted LangSmith replacement, ADR-0002/0009)
implementations, audited against vendor + industry best practice.

**Method:** Each pass runs a multi-agent audit (one auditor per layer × dimension,
reading the real code) whose findings are each adversarially verified to remove
false positives. Confirmed findings are fixed with tests, then the next pass
re-audits. **Termination condition:** a full audit pass produces zero confirmed
findings.

Passes are never edited after they are written. New passes are appended.

---

## Pass Index

| Pass | Date (UTC) | Confirmed | Fixed | Status |
|------|------------|-----------|-------|--------|
| 1 | 2026-06-13 | 39 (7H/19M/13L) | 39 | ✅ complete |
| 2 | 2026-06-13 | 33 (1C/4H/16M/12L) | 33 | ✅ complete |
| 3 | 2026-06-13 | _pending workflow_ | — | re-audit running |

---

## Pass 1 — 2026-06-13

**Audit:** multi-agent (run `wf_80c12d66-108`), 14 dimensions across langgraph / langchain / phoenix / cross-cutting. 81 agents, ~1.8M tokens.
**Result:** 39 confirmed findings (7 high · 19 medium · 13 low) after 28 rejected as false-positive/nit by adversarial verification.
**Tracking:** GitHub issues #144–#182 (labels `hardening` + `pass-1` + severity + area).

| # | Issue | Sev | Layer | File | Finding | Status |
|---|-------|-----|-------|------|---------|--------|
| 1 | #144 | high | `cross` | pyproject.toml | Invalid PEP 517 build-backend — package cannot be built or pip-installed | ✅ fixed |
| 2 | #145 | high | `langchain` | reasoning_client.py | No per-call timeout on any reasoning call — a hung backend blocks a synchronous LangGraph  | open |
| 3 | #146 | high | `langchain` | reasoning_client.py | Tier-3 path can silently spill to the metered Anthropic API when ANTHROPIC_API_KEY is pres | open |
| 4 | #147 | high | `langgraph` | checkpointer.py | Persistent single Connection has no health-check or reconnect — dies permanently on Postgr | ✅ fixed |
| 5 | #148 | high | `langgraph` | phase1.py | Non-NotImplementedError exceptions in P1-P5 agents crash the entire graph run with no isol | open |
| 6 | #149 | high | `phoenix` | graph.py | instrument_langchain() is never called by any run path — all LLM/agent execution is untrac | open |
| 7 | #150 | high | `phoenix` | reasoning_client.py | Tier 3 (highest-stakes Claude Max) LLM calls emit no spans — invisible in Phoenix | open |
| 8 | #151 | medium | `cross` | reasoning_client.py | reasoning_client.py has zero unit tests — the most failure-prone seam is entirely uncovere | open |
| 9 | #152 | medium | `cross` | gates.py | Gate 2 through Gate 5 nodes are completely untested (gates.py ~42% covered) | open |
| 10 | #153 | medium | `cross` | test_orchestrator_grounding.py | Live-grounding test is non-deterministic and double-invokes the backend; effectively never | open |
| 11 | #154 | medium | `cross` | gates.py | Gate 2 hard-prerequisite failure path (returns without interrupt) is untested | open |
| 12 | #155 | medium | `cross` | orchestrator.py | 'deferred' decision path is untested in gate nodes and routing functions | open |
| 13 | #156 | medium | `cross` | requirements.txt | Unbounded langgraph / langchain-core ranges resolve to 1.x — major-version drift, non-repr | ✅ fixed |
| 14 | #157 | medium | `langchain` | reasoning_client.py | No retry/backoff on transient failures — a single flaky call fails the whole tier-routed s | open |
| 15 | #158 | medium | `langchain` | reasoning_client.py | Tier-3 call has no timeout — an unresponsive `claude` CLI hangs the LangGraph node indefin | open |
| 16 | #159 | medium | `langchain` | reasoning_client.py | _extract_json greedy regex span produces invalid JSON when the reply contains multiple JSO | open |
| 17 | #160 | medium | `langchain` | base.py | Protected-agent phase dispatch never matches the phase values the graph actually sets — Ph | ✅ fixed |
| 18 | #161 | medium | `langgraph` | test_postgres_checkpointer.py | Audit-target test test_postgres_checkpointer.py does not exist — checkpointer durability i | open |
| 19 | #162 | medium | `langgraph` | graph.py | No resume path exists: runners call invoke() once and return; nothing consumes the interru | open |
| 20 | #163 | medium | `langgraph` | gates.py | interrupt() return value is used without validating it is a dict, so a non-dict operator r | open |
| 21 | #164 | medium | `langgraph` | gates.py | Gate 2 prerequisite failure returns no gate_status, so the router silently parks the run a | open |
| 22 | #165 | medium | `langgraph` | graph.py | Orchestrator-style external LLM calls (and future agent calls) have no timeout or RetryPol | open |
| 23 | #166 | medium | `phoenix` | phoenix_setup.py | register() uses default SimpleSpanProcessor — synchronous per-span export instead of Batch | open |
| 24 | #167 | medium | `phoenix` | phoenix_setup.py | run_id is never set as a Phoenix span attribute — documented propagation path is dead code | open |
| 25 | #168 | medium | `phoenix` | reasoning_client.py | reasoning_client.complete() cannot carry run_id into traces — no config/metadata seam | open |
| 26 | #169 | medium | `phoenix` | phoenix_setup.py | Phoenix register() uses default batch=False -> blocking SimpleSpanProcessor; no span buffe | open |
| 27 | #170 | low | `cross` | test_gate1.py | Graph-level data-split determinism (fixed seed=42) is asserted only as non-null, not pinne | open |
| 28 | #171 | low | `cross` | config.py | platform.yaml is loaded with no schema validation — silent misconfiguration | open |
| 29 | #172 | low | `langchain` | reasoning_client.py | complete_json greedy JSON extraction grabs trailing prose and fails on otherwise-valid rep | open |
| 30 | #173 | low | `langchain` | reasoning_client.py | is_available() liveness probe has no timeout and runs a full model round-trip — a wedged b | open |
| 31 | #174 | low | `langchain` | reasoning_client.py | is_available() spends a real Tier-3 frontier turn against the subscription envelope on eve | open |
| 32 | #175 | low | `langchain` | reasoning_client.py | complete_json relies on prompt-instruction + regex extraction instead of Ollama's native f | open |
| 33 | #176 | low | `langgraph` | checkpointer.py | setup() migrations run without an advisory lock — concurrent initializers race on checkpoi | ✅ fixed |
| 34 | #177 | low | `langgraph` | gates.py | Resuming a run after a gate already decided will overwrite the prior decision and re-fire  | open |
| 35 | #178 | low | `langgraph` | gates.py | Gate 2 hard-prerequisite failure returns without writing gate_status, causing silent route | open |
| 36 | #179 | low | `langgraph` | graph.py | Gate-2-rejected loop back to exploratory_phase has no recursion/termination guard | open |
| 37 | #180 | low | `langgraph` | gates.py | Malformed operator_response from interrupt() silently defaults gates to 'rejected' / swall | open |
| 38 | #181 | low | `phoenix` | phoenix_setup.py | instrument_langchain() is documented as idempotent but has no guard — repeat calls double- | open |
| 39 | #182 | low | `phoenix` | phoenix_setup.py | Docstring asserts traces are 'buffered' on server outage, but the configured processor pro | open |

### Fix batches (all 39 closed)
- **Batch 1 — surgical highs + deps** (`1761f7f`): #144 pyproject build-backend, #147 checkpointer self-healing pool, #176 migration advisory lock, #160 base.py phase_2 dispatch / SAP firewall, #156 dependency pins.
- **Batch 2 — reasoning_client reliability** (`3c119cc`): #145/#158 timeouts, #146 metered-API scrub, #157 retry/backoff, #159/#172/#175 robust JSON, #173/#174 cheap liveness, #151 unit tests.
- **Batch 3 — Phoenix/OTel wiring** (`30e70ae`): #149 instrument on run, #150/#168 T3 + run_id spans, #166/#169/#182 BatchSpanProcessor, #167 run_id context, #181 idempotency. Verified spans land in Phoenix.
- **Batch 4 — LangGraph fault isolation & interrupt safety** (`2f06f5b`): #148 agent fault isolation, #163/#180 response validation, #177 idempotency guard, #164/#178 gate_2 prereq gate_status, #165 RetryPolicy, #179 recursion limit, #162 resume_run, #154 test.
- **Batch 5 — tests & config** (`cc99013`): #152/#155 gate decision coverage, #153 deterministic grounding test, #161 checkpointer tests, #170 split determinism, #171 config validation.

**Pass 1 result: 39/39 fixed, 89 tests passing.** Pass 2 re-audits the hardened code for regressions and any newly-introduced issues.

---

## Pass 2 — 2026-06-13

**Re-audit** of the hardened code (run `wf_df446928-130`, 75 agents). 33 confirmed
findings (1 critical, 4 high, 16 medium, 12 low) after 28 rejected. Tracked as
issues #184–#216; **6 were regressions introduced by pass-1 batches** (label
`regression`). The value of iterating: pass 2 caught a **critical** regression —
the pass-1 `_already_decided` idempotency guard (#177) had silently killed the
Gate-2 reject→re-review governance loop.

### Fix batches (all 33 closed)
- **Batch 6 — regressions + deps** (`2027513`): #184/#187 reject-loop re-fire,
  #186/#188/#201 RetryPolicy `retry_on` excludes governance/logic errors,
  #193 dep upper bounds, #192 qdrant-client declared, #191 CI deps pinned.
- **Batch 7 — reasoning_client v3** (`77695be`): #185 T3 rate-window backpressure,
  #194/#209 error classification, #195/#196/#197/#198 Ollama timeout/num_ctx/seed/
  num_predict, #203/#204 span usage + real model, #208 retry clamp, #210 model-pull
  liveness, #189/#190/#205 tests.
- **Batch 8 — langgraph/obs/config** (`f59f29e`): #200 runner default checkpointer,
  #206 retry_policy= + deprecation-as-error, #213 drop dead gate nodes, #202
  IMPLEMENTED marker, #207 vector_store validation, #215 span flush, #216 loopback
  guard, #199/#211/#212/#214 bench + docs.

**Pass 2 result: 33/33 fixed, 97 tests passing.** Pass 3 re-audits again.

---

## Pass 3 — 2026-06-13

_Re-audit after pass-2 fixes. Findings recorded when the workflow completes._
