# Transcript: ml-engineer-adversary — Round 2 Re-audit
**Date:** 2026-06-08
**Stage:** P0
**Agent:** ml-engineer-adversary/claude-opus-4-8@hc-macbook-pro.local (Tier-2 same-discipline adversary)
**Stance:** falsification-probe
**Artifact set:** P0 CI/reproducibility remediation round 2
**Verdict:** PASS
**Round:** 2

---

## Prior defect verified resolved

### Defect 1 — P0 self-attestation shape mismatch (CRITICAL → RESOLVED)
`provenance-integrity.yml` line 116 now reads `self_attested` from inside the adversary dict: `isinstance(adversary, dict) and adversary.get("self_attested") is True`. The `adversary is None` gating branch is removed.

All three scenarios verified:
1. P0 self-attested: `adversary: {"self_attested": true, "reason": "bootstrap"}` → PASS ✓
2. P1+ full review: `adversary: {"agent": "...", "model": "claude-opus-4-8", "family": "anthropic", "stance": "..."}` → PASS ✓
3. P1+ missing fields: `adversary: {"agent": "..."}` (no model, no family) → FAIL ✓

All falsification attempts defeated:
- Non-P0 self-attestation → blocked by schema allOf[1]; schema validated by registry-validate.yml on identical triggers
- `self_attested: false` + no model → fails model/family check ✓
- `self_attested: "true"` (string) → `is True` identity-strict; string fails → else branch demands model/family; schema requires `const: true` ✓
- `adversary: null` → `isinstance(null, dict)` false → else → fails model/family ✓
- P0 with full adversary form (no self_attested) → requires model/family; legitimate P0 artifacts that received review still pass ✓

## Non-blocking observation (not a defect)
The workflow's self-attestation exception (line 116) carries no independent `stage_id == "P0"` guard of its own. Relies on `registry-validate.yml`'s schema check. No live exploit path since both gates run on identical triggers, but protection is split across two workflows. Defense-in-depth would add a one-line stage guard. Non-blocking; outside original review set.

---

## Certificate

```
CERTIFICATE
artifact_set: P0 CI/reproducibility remediation round 2
producer: mlops-engineer
adversary: ml-engineer-adversary
model: claude-opus-4-8
stance: falsification-probe
verdict: PASS
rounds: 2
findings: prior critical defect resolved
limitations:
  - Producer and adversary share Anthropic family (Layer-3 weight independence not fully satisfiable in-program)
  - Verification by static trace of CI logic, not by executing GitHub Actions runners against fixture artifacts
residual_risk:
  - Workflow's self-attestation exception has no independent stage_id guard; depends on registry-validate.yml which silently skips when schema file is absent (line 56). No current exploitable path but not defense-in-depth.
```
