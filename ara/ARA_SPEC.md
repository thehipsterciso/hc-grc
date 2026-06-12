# ARA Artifact Schema Specification

**Version:** 0.1.0
**Status:** Draft — authored 2026-06-12 to close the missing inter-agent data contract (see KICKOFF_READINESS.md, P1 backlog item 7)
**Owner:** Orchestrator (T-00)

---

## Purpose

ARA (Agent-Native Research Artifact) is the canonical, framework-agnostic data contract that every agent reads from and writes to. Agent cards reference "ARA artifacts" and "the ARA Compiler" throughout (e.g. `data-acquisition`, `p1-strm-nlp`, `report-agent`), but no schema existed. This document defines those schemas so that:

1. The Data Acquisition Agent's ARA Compiler has a target schema to emit.
2. Analysis agents (P1–P5) have a typed contract for the data they consume.
3. The contract is **framework-agnostic** — Tier 2 (`hc-grc-comparative`) ingests Tier 1 ARA artifacts without schema changes (ADR-0010).

All schemas are expressed as Pydantic v2 models. These definitions are the source of truth; the `instructor` skill enforces them at agent boundaries. Persisted artifacts are JSON (records) or Parquet (bulk tables) under `ara/artifacts/`, DVC-tracked, local-only (ADR-0002).

> **Naming convention:** exploratory artifacts are prefixed `EXP_`; confirmatory artifacts are named `H[module].[n]_*`. This prefix is a firewall signal (ADR-0007) and is validated, not decorative.

---

## 1. Core SCF Data Model

The canonical representation of the acquired SCF corpus. Produced by the ARA Compiler from the raw XLSX; consumed by every analysis agent.

### 1.1 `Control`

```python
class Control(BaseModel):
    control_id: str            # SCF canonical ID, e.g. "GOV-01" — primary key
    domain_id: str             # FK → Domain.domain_id (one of 33 SCF domains)
    title: str
    text: str                  # full control statement — the unit of NLP analysis
    methods: list[str] = []    # mapped control mechanisms / assessment objectives, if present
    risk_category_ids: list[str] = []   # FK → RiskCategory (P4 coverage analysis)
    source_framework_refs: list[FrameworkRef] = []  # external framework controls this maps to
    scf_version: str           # SCF release this control was acquired from
    source_sha256: str         # SHA-256 of the raw manifest this control derives from
```

### 1.2 `STRMMapping`

The 280,000+ expert relationship mappings — the objects under test. The strength score and relationship type are **expert labels treated as hypotheses, not ground truth** (ADR-0013).

```python
class STRMRelationship(str, Enum):
    SUBSET = "subset of"
    INTERSECTS = "intersects with"
    EQUAL = "equal"
    SUPERSET = "superset of"
    NO_RELATIONSHIP = "no relationship"

class STRMMapping(BaseModel):
    mapping_id: str            # stable hash of (source, target, relationship) — primary key
    source_control_id: str     # FK → Control.control_id
    target_control_id: str     # FK → Control.control_id
    relationship: STRMRelationship   # expert-assigned set-theoretic relationship
    strength_score: float | None     # expert-assigned strength, if present; null = unscored
    source_framework: str
    target_framework: str
    nist_cluster: bool = False  # True if both endpoints are NIST 800-53/CSF/800-171 (ADR-0006)
    scf_version: str
```

### 1.3 `Domain`, `RiskCategory`, `MaturityLevel`

```python
class Domain(BaseModel):
    domain_id: str             # one of the 33 SCF domains — primary key
    name: str
    description: str

class RiskCategory(BaseModel):
    risk_category_id: str      # one of the 39 SCF risk categories (P4) — primary key
    name: str
    description: str

class MaturityLevel(BaseModel):
    level: int                 # SCF maturity level ordinal
    name: str
    definition: str

class FrameworkRef(BaseModel):
    framework: str             # e.g. "NIST SP 800-53 R5", "CIS v8"
    external_control_id: str
    license: str               # e.g. "CC BY-ND 4.0", "Public Domain" — IP Attribution Agent reads this
```

### 1.4 `CorpusManifest`

Emitted once per acquisition; the provenance anchor for the whole study.

```python
class CorpusManifest(BaseModel):
    scf_version: str
    source_url: str
    github_commit_hash: str
    acquisition_timestamp_utc: str   # ISO-8601
    source_sha256: str               # of the raw XLSX
    control_count: int               # expected ~1,400
    strm_mapping_count: int          # expected ~280,000
    domain_count: int                # expected 33
    risk_category_count: int         # expected 39
    dvc_artifact_hash: str
```

---

## 2. Analysis Artifact Envelope

Every analysis output — exploratory or confirmatory — is wrapped in a common envelope so the Statistical Analyst, QA Agent, Report Agent, and Provenance Agent can consume any module's output uniformly.

```python
class Phase(str, Enum):
    EXPLORATORY = "exploratory"
    CONFIRMATORY = "confirmatory"

class AnalysisArtifact(BaseModel):
    artifact_id: str
    module: Literal["P1", "P2", "P3", "P4", "P5"]
    phase: Phase
    hypothesis_id: str | None        # null in exploratory; "H{n}.{m}" in confirmatory
    path: str                        # repo-relative path to the Parquet/JSON/GraphML payload
    payload_format: Literal["parquet", "json", "graphml", "markdown"]
    run_id: str                      # propagated to all four observability stores (ADR-0015 #79)
    produced_by: str                 # agent name
    timestamp_utc: str               # ISO-8601, written at produce time (ADR-0015 #73)
    nist_cluster_enforced: bool      # P1/P2/P3 must assert True
```

---

## 3. Confirmatory Result Contract

The Statistical Analyst's output. One record per pre-registered hypothesis. Mirrors `ConfirmatoryResult` already defined in `src/agents/statistical_analyst`.

```python
class ConfirmatoryResult(BaseModel):
    hypothesis_id: str               # "H{module}.{n}" — must exist in the locked SAP
    test_name: str                   # must match the SAP-registered test
    statistic: float
    p_value: float
    effect_size: float
    effect_size_metric: str
    ci_lower: float
    ci_upper: float
    n_obs: int
    decision: Literal["reject_null", "fail_to_reject", "inconclusive"]
    correction_applied: str          # multiple-comparisons correction per SAP §6
    corrected_p_value: float | None
    sap_section: str
    is_null_result: bool             # true → reported with equal prominence
    run_id: str
    timestamp_utc: str
```

---

## 4. Findings Record Contract

The Report Agent's output — the machine-readable companion to the canonical findings report. The single interpreted contract all dissemination agents consume.

```python
class FindingsRecord(BaseModel):
    finding_id: str
    module: Literal["P1", "P2", "P3", "P4", "P5"]
    hypothesis_id: str               # traces to a ConfirmatoryResult
    claim: str                       # the interpreted statement, precise (no "frameworks are similar")
    direction: Literal["positive", "null", "unexpected"]
    effect_size: float
    confidence_interval: tuple[float, float]
    qa_score: float                  # ≥ 3.5 required for Gate 4 dissemination
    provenance_ref: str              # PROV-DM activity IRI
    is_null: bool
    practitioner_implication: str | None   # for whitepaper/business derivation
    limitations: list[str] = []
    run_id: str
    timestamp_utc: str
```

---

## 5. Inter-Agent Result Envelope

The generic envelope the Orchestrator uses for any agent handoff (mirrors `AgentResult` referenced in the orchestrator card).

```python
class AgentResult(BaseModel):
    agent_id: str                    # hcgrc:<hash> per CARDS_SPEC §Agent ID
    agent_name: str
    status: Literal["completed", "stub_pending", "failed", "escalated"]
    artifacts: list[str] = []        # paths to produced ARA artifacts
    note: str | None = None
    run_id: str
    timestamp_utc: str
```

---

## 6. Validation & Enforcement

- **At agent boundaries:** the `instructor` skill validates every emitted record against these models. A record missing a required field does not leave the agent.
- **At the firewall:** any `AnalysisArtifact` with `phase == "confirmatory"` and a `hypothesis_id` not present in the locked SAP is rejected (Gate 2 firewall, ADR-0007).
- **At provenance:** every persisted artifact carries `run_id` + `timestamp_utc` written at produce time; downstream consumers sort by timestamp, never list position (ADR-0015 #73).
- **License:** `FrameworkRef.license` is read by the License Compliance and IP Attribution agents; any non-CC-BY-ND source full-text requires operator sign-off (per `data-acquisition` constraints).

## 7. Open Items

- [ ] Confirm SCF strength-score scale and `STRMRelationship` enum values against the real acquired XLSX (currently from charter/card references — verify on first acquisition).
- [ ] Generate Pydantic models in `src/ara/models.py` from this spec and wire `instructor` enforcement (build task).
- [ ] Decide whether `methods` (control mechanisms) warrants its own table vs. the inline list above.
