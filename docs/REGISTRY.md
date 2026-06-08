# hc-grc — Registry

**Version:** 1.0
**Date:** 2026-06-08

The registry is the program's canonical index of accepted artifacts. Every piece of work that
downstream agents may consume must appear here with a passing certificate. Nothing enters the
registry without one.

---

## The model in one sentence

One JSON file per artifact, stored under `registry/<framework>/` or `registry/_program/`, written
only by `context-manager`, only after `error-coordinator` confirms a passing certificate exists in
`ledger/certificates/`.

---

## Directory layout

```
registry/
  schema/
    artifact.schema.json        JSON Schema for every registry entry
  _program/                     program-level artifacts (P0, P1, S3)
  scf/                          SCF per-framework artifacts (S1f, S4-S9)
  nist-800-53/
  nist-csf-2.0/
  nist-800-171/
  cis-v8/
```

Each file is named `<artifact_id>.json`. The `artifact_id` is the primary key; no two files in the
registry may share one.

---

## What qualifies as a registered artifact

An artifact is a discrete, versioned output — a corpus file, an embedding, a statistical result, a
finding, a triangulation report — that:

1. Has a Definition of Done agreed before the producing agent started work.
2. Was produced by a named Tier-1 agent on a named model.
3. Was reviewed by a same-discipline Tier-2 adversary on a different model and stance.
4. Received a certificate with `verdict: ACCEPT`.
5. Has a stable content hash (sha256 of its canonical serialization).

Infrastructure outputs from Tier-0 agents (the orchestration harness, branch configurations) are
also registered at P0 with self-attestation certificates per the gate design for that stage.

---

## Schema fields

All fields are defined in `registry/schema/artifact.schema.json`. The complete authoritative field set is:

| Field | Type | Required | Purpose |
|---|---|---|---|
| `artifact_id` | string | yes | Primary key. Pattern `<stage>-<artifact_type>[-<framework>]-<slug>`. Globally unique. |
| `artifact_type` | enum string | yes | Artifact type drawn from the `artifact_types` list in `docs/STAGE_GATES.yaml`. |
| `stage_id` | enum string | yes | Pipeline stage (P0, P1, S1f, S3, S4–S9, X1–X5). |
| `certificate_ref` | string | yes | Stem of the certificate file under `ledger/certificates/`. Full path: `ledger/certificates/<certificate_ref>.json`. Enforced by `stage_gate.py`. |
| `framework` | string or null | yes | Which framework this artifact belongs to (`scf`, `nist-800-53`, etc.). Null for program-level and synthesis stages (P0, P1, S3, X1–X5). Non-null required for per-framework stages (S1f, S4–S9). |
| `question_id` | string or null | yes | For investigation artifacts (S7, X2): the registered question ID this answers. Null for non-investigation artifacts; when null, `null_reason` is required. |
| `null_reason` | string | conditional | Required when `question_id` is null. Explains why no question is associated. |
| `producer` | `{agent, model}` | yes | Tier-1 agent identity and model string. |
| `adversary` | object | yes | Either `{agent, model, family, stance}` for stages P1+ (family is always `anthropic`; explicit to surface the single-family limitation), or `{self_attested: true, reason: string}` for P0 only. See P0 self-attestation exception below. |
| `stance` | enum string or null | yes | Rotating review stance the adversary applied. One of: `independent-reconstruction`, `falsification-probe`, `competing-hypotheses`, `assumption-ledger`, `premortem`. Null only for P0 self-attested artifacts. |
| `content_hash` | string (sha256, 64 hex chars) | yes | SHA-256 hex of the artifact's canonical serialization (UTF-8 JSON, sorted keys, no trailing whitespace). Detects drift between registry record and stored artifact. |
| `reproduction` | `{seed, container_digest, command, input_hashes[]}` | yes | Everything needed to re-run the producing computation from scratch. `seed` and `container_digest` may be null for deterministic/non-containerized artifacts. |
| `source_version` | string | yes | Version or content hash of the primary source consumed (e.g. framework release tag, PDF sha256). Enables downstream reproducibility checks. |
| `git_commit` | string (40-char hex) | yes | Full SHA-1 git commit hash at time of registration. Ties the entry to an immutable program state. |
| `evidence_class` | enum string or null | yes | `robust`, `provisional`, `intrinsic`, `framework-specific`, `crosswalk-dependent`, `descriptive`, or `not-applicable`. Null only if classification is deferred; must be set before synthesis consumes the artifact. |
| `depends_on` | string[] | yes | `artifact_id`s this artifact directly consumed. Empty array for root artifacts. Used to build the evidence-dependency graph in S8f and X2. |
| `limitations` | string[] | conditional | Required (min 1 item) when `evidence_class` is `robust` or `intrinsic`. Must include the model-independence note and any methodology-specific caveats. |
| `transcript_ref` | string | yes | Relative path to the agent transcript file from repo root, e.g. `transcripts/S4/scf/data-engineer-2026-06-08T12:00:00Z.md`. |
| `created_at` | string (date-time) | yes | ISO-8601 UTC timestamp when `context-manager` wrote this entry. |
| `registry_version` | const `"1.0"` | yes | Schema version guard. Guards against consumers loading entries from a future incompatible schema. |
| `revision_history` | object[] | yes | Ordered list of `{round, timestamp, summary, defect_ref}` records. Empty array on first registration. |
| `description` | string | no | Human-readable description of what this artifact contains. |

### P0 self-attestation exception

P0 is the program-setup stage; the adversary infrastructure is being bootstrapped at that point.
P0 artifacts therefore carry no same-discipline adversary review. This is by gate design, not an
exception. The `adversary` field for P0 artifacts must take the self-attestation form:

```json
"adversary": {
  "self_attested": true,
  "reason": "P0 stage — required_adversary_disciplines is [] per gate definition; adversary infrastructure not yet operational"
}
```

For all stages P1 and beyond, `adversary` must be the full review form with `agent`, `model`,
`family`, and `stance`. A P1+ artifact with `self_attested: true` in the adversary field will fail
schema validation. This is enforced by an `allOf` `if/then` block in `artifact.schema.json`
(JSON Schema draft-07): when `stage_id` is not `P0`, the schema rejects any adversary object that
contains `self_attested`. The constraint is evaluated by `jsonschema.validate()` inside
`stage_gate.py --validate-artifact`.

---

## How context-manager registers an artifact

The atomic registration sequence:

1. **Receive registration request** from the producing agent or coordinator. The request carries:
   the artifact payload, its `artifact_id`, the `certificate_id` claimed to authorize it, and the
   `transcript_ref`.

2. **Verify the certificate.** Load `ledger/certificates/<certificate_id>.json`. Confirm:
   - `verdict == "ACCEPT"`
   - `artifact_id` in the certificate matches the request
   - `git_commit` in the certificate matches the current HEAD

3. **Compute and record the content hash.** SHA-256 the artifact's canonical serialization
   (UTF-8 JSON, keys sorted, no trailing whitespace). Store in `content_hash`.

4. **Validate against schema.** Run the artifact entry against `registry/schema/artifact.schema.json`.
   Any validation failure is a hard stop — return error to coordinator, do not write.

5. **Write the registry entry.** Write `registry/<framework>/<artifact_id>.json` (or
   `registry/_program/<artifact_id>.json`). The file is created atomically; no partial writes.

6. **Confirm to coordinator.** Return the registered `artifact_id` and `content_hash`. Any
   downstream agent requesting this artifact may now consume it.

If any step fails, context-manager writes nothing to the registry and returns a structured error.
There is no partial registration. The ledger entry in `error-coordinator` records the failure.

---

## The transcript link

Every registered artifact carries `transcript_ref`, a relative path to the agent transcript that
produced it. Transcript files live under `transcripts/<stage>/<framework>/` and are named by
agent and timestamp (e.g. `data-engineer-2026-06-08T12:00:00Z.md`).

The transcript is the human-readable log of the reasoning, decisions, and tool calls that produced
the artifact. Combined with `reproduction` (the machine-reproducible run record), the transcript
and registry entry together answer two distinct questions: "what did the agent do and why" and
"can this result be reproduced independently."

Neither the registry entry nor the transcript is sufficient alone. Both are required for full
provenance per hard constraint 8 in `CLAUDE.md`.

---

## Certified-only guarantee

The registry is not a work queue or scratch space. It is an index of artifacts the program treats
as established. This guarantee has two enforcement points:

- `context-manager` will not write a registry entry without a passing certificate. This is not a
  convention — it is the only code path that creates registry entries.
- `multi-agent-coordinator` will not pass a stage gate if a required artifact for the next stage
  is absent from the registry. Downstream agents that attempt to consume an unregistered artifact
  receive an error.

The consequence: an artifact that is rejected, revised, and re-audited does not appear in the
registry until the revision passes. The revision history lives in `ledger/defects/` (via
`error-coordinator`) and in the artifact entry's `depends_on` chain, not in the registry file
itself. When the artifact is finally accepted, it is registered once, clean, with its full
provenance intact.

---

## Gitignore policy

Artifact data files (corpus files, embedding matrices, statistical outputs) are gitignored. They
are large, binary, or both. The registry JSON entries, by contrast, are committed. This means:

- The git history is a complete provenance log of what the program accepted and when.
- Artifact data can be regenerated from `reproduction` fields.
- Reviewers can audit the full acceptance record without checking out large data files.

The `.gitignore` at the repo root excludes `frameworks/<name>/data/` and related output
directories. Registry entries in `registry/` are explicitly tracked.
