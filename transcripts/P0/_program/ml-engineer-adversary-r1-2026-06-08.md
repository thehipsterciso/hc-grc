# Transcript: ml-engineer-adversary — Round 1 Audit
**Date:** 2026-06-08
**Stage:** P0
**Agent:** ml-engineer-adversary (Tier-2 same-discipline adversary)
**Model:** claude-opus-4-8
**Stance:** falsification-probe
**Artifact set:** P0 CI/reproducibility remediation
**Verdict:** REJECT
**Round:** 1

---

## Defects Found

### Defect 1 — P0 self-attestation shape mismatch between schema and provenance-integrity.yml (CRITICAL)
Schema's self-attestation oneOf form places `self_attested+reason` INSIDE the adversary object: `adversary: {self_attested: true, reason: "..."}`. `additionalProperties: false` forbids a top-level `self_attested` key. Adversary oneOf also forbids `adversary: null`.

But `provenance-integrity.yml` (lines 112-124) gates its P0 exception on `adversary is None` AND top-level `artifact.get("self_attested")`.

Result: a schema-valid P0 artifact fails provenance-integrity with "adversary.model is missing" and "adversary.family is missing". A provenance-passing artifact (`adversary: null` + top-level `self_attested`) fails schema validation. The two required checks are mutually exclusive — NO P0 self-attested artifact can pass both.

**Fix:** Make provenance-integrity read `self_attested` from inside the adversary object: check `adversary.get("self_attested") is True` as the exception condition (drop the `adversary is None` branch). The schema is authoritative; the workflow must conform to it.

---

## Certificate

```
CERTIFICATE
artifact_set: P0 CI/reproducibility remediation
producer: mlops-engineer
adversary: ml-engineer-adversary
model: claude-opus-4-8
stance: falsification-probe
verdict: REJECT
rounds: 1
findings:
  - [CRITICAL] provenance-integrity.yml vs artifact.schema.json P0 self-attestation shape mismatch.
    Schema puts self_attested inside adversary object; workflow checks adversary is None + top-level
    self_attested. No P0 self-attested artifact can pass both required checks simultaneously.
    Fix: conform workflow to schema shape.
limitations:
  - Same Anthropic family (claude-opus-4-8); Layer-3 weight independence is partial
  - stage_gate.py --validate-all not audited (out of scope per producer); certificate-completeness main gate unverified end-to-end
residual_risk:
  - Workflows with live GitHub events (pull_request_target permissions, ruleset API responses) not testable without an actual GitHub run
  - Further schema changes to adversary block require re-audit of this workflow
```
