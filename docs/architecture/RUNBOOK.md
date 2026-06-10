# Diagnostic Runbook

Common diagnostic procedures for the HC-GRC platform. All cross-store queries use `run_id` as the common key — propagated to MLflow, Phoenix, W3C PROV-DM, and PostgresSaver at run start (per ADR-0015, #79).

---

## 1. What did agent X do on run Y?

**Step 1 — Get the run_id**
```bash
# If you know the approximate time
mlflow runs search --experiment-name hc-grc --filter "tags.start_time > '2026-01-01'"

# If you know the gate or phase
psql -d hcgrc -c "SELECT run_id, phase, gate_status FROM checkpoints WHERE thread_id = '<run_id>' ORDER BY checkpoint_id DESC LIMIT 1;"
```

**Step 2 — MLflow: inputs, outputs, scores**
```bash
mlflow runs get --run-id <run_id>
mlflow artifacts list --run-id <run_id>
```

**Step 3 — Phoenix: LLM traces for that agent**
```
Phoenix UI → Traces → Filter: run_id = <run_id>, span.agent = <agent_name>
```

**Step 4 — PROV-DM: full activity chain**
```sparql
SELECT ?activity ?startedAtTime ?endedAtTime ?used ?generated
WHERE {
  ?activity prov:wasAssociatedWith <agent:X> .
  ?activity prov:startedAtTime ?startedAtTime .
  ?activity prov:used ?used .
  OPTIONAL { ?activity prov:generated ?generated }
  FILTER (str(?activity) = "<run_id>")
}
```

---

## 2. Why did Gate N reject?

**Step 1 — Gate record in PostgresSaver**
```sql
SELECT gate_decisions, gate_status, timestamp
FROM checkpoints
WHERE thread_id = '<run_id>'
  AND gate_decisions->>'gate-N' IS NOT NULL
ORDER BY checkpoint_id DESC LIMIT 1;
```

**Step 2 — Gate coordinator provenance**
```sparql
SELECT ?rationale ?dissent ?reviewer
WHERE {
  <gate:N:<run_id>> prov:wasAssociatedWith ?reviewer .
  <gate:N:<run_id>> hcgrc:rationale ?rationale .
  <gate:N:<run_id>> hcgrc:dissent ?dissent .
}
```

**Step 3 — Full run context at gate time (MLflow)**
```bash
mlflow runs get --run-id <run_id>
# Review metrics logged at the gate step
```

---

## 3. Full provenance chain for finding F

**Step 1 — Locate finding in PROV-DM**
```sparql
SELECT ?activity ?agent ?input ?output ?timestamp
WHERE {
  <finding:F> prov:wasDerivedFrom ?output .
  ?activity prov:generated ?output .
  ?activity prov:wasAssociatedWith ?agent .
  ?activity prov:used ?input .
  ?activity prov:startedAtTime ?timestamp .
}
ORDER BY ?timestamp
```

**Step 2 — Confirm hypothesis was pre-registered before test ran**
```bash
# Check Preregistration Ledger timestamp vs. confirmatory run timestamp
grep -A 5 "finding:F" docs/protocol/PREREGISTRATION_LEDGER.md
# Compare timestamp to MLflow run start time for confirmatory run
```

**Step 3 — Verify RFC 3161 timestamp**
```bash
openssl ts -verify -in <finding_F.tsr> -data <hypothesis_record.json> -CAfile tsa-ca.pem
```

---

## 4. Did Agent Evolution modify a protected agent?

```bash
# Check lab notebook for any evolution actions on protected agents
grep -r "p1-strm-nlp\|p2-control-topology\|p3-regulatory-convergence\|p4-risk-blindspot\|p5-ai-governance\|statistical-analyst\|hypothesis-formalizer" \
  lab-notebook/ | grep -i "prompt\|modified\|optimized"

# Check git log for unauthorized changes
git log --all --follow -- agents/03-analysis/p1-strm-nlp/AGENT.md
git log --all --follow -- agents/04-statistical/statistical-analyst/AGENT.md
git log --all --follow -- agents/01-research/hypothesis-formalizer/AGENT.md
```

Any modification to a protected agent that does not have a corresponding Escalation approval GitHub issue is a protocol violation. Log to INCIDENTS.md immediately.

---

## 5. Escalation loop not responding — platform appears stalled

**Check:** Is there an open Escalation GitHub issue awaiting a decision?
```bash
cd /path/to/hc-grc
gh issue list --label "escalation" --state open
```

If yes: the platform is parked per ADR-0012. It will not auto-proceed. Review the proposal in Claude and respond with approve/reject/defer.

If no open Escalation issues: check for platform errors.
```bash
# Check most recent checkpoint state
psql -d hcgrc -c "SELECT thread_id, phase, error_state, timestamp FROM checkpoints ORDER BY timestamp DESC LIMIT 5;"

# Check Phoenix for recent agent failures
# Phoenix UI → Traces → Filter: status = ERROR, last 24h
```

---

## Common run_id Propagation Reference

| Store | Where run_id appears | How to query |
|-------|---------------------|--------------|
| MLflow | `tags.run_id` on every experiment run | `mlflow runs search --filter "tags.run_id='<id>'"` |
| Phoenix | Trace attribute `run_id` | Filter in Phoenix UI or API |
| PROV-DM | Activity IRI contains run_id | SPARQL filter on activity IRI |
| PostgresSaver | `thread_id` column | SQL WHERE clause |
