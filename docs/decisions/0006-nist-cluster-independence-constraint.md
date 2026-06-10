# ADR-0006: NIST Cluster Independence Constraint

**Status:** Accepted
**Date:** 2026-06-09
**Deciders:** Thomas Jones

---

## Context

HC-GRC's P3 (Regulatory Convergence Atlas) module measures cross-framework convergence in the SCF/STRM corpus. A naive analysis would treat NIST SP 800-53, NIST CSF, and NIST SP 800-171 as three independent evidence sources for cross-framework convergence. They are not. All three are authored by the same organization (NIST), share significant vocabulary, and were explicitly designed to be mutually compatible. Treating them as independent observations would inflate the apparent evidence for framework convergence and produce a finding that overstates the degree of independent agreement in the corpus.

## Decision

NIST SP 800-53, NIST CSF, and NIST SP 800-171 are treated as a single evidence cluster ("the NIST cluster") for all cross-framework convergence analyses in P3 and P1. Within-cluster STRM mappings are excluded from analyses that purport to measure independent cross-framework agreement. The constraint is enforced at the data layer — the Data Steward agent applies it at split time — not as a per-analysis choice.

This is documented in:
- `protocol/01_theoretical_framework.md` (TC2 and the NIST cluster construct definition)
- `protocol/04_methods_scaffolding.md` (standing rule, not a per-analysis choice)
- All relevant AGENT.md cards (P1, P3)

## Alternatives Considered

**Treat all frameworks as independent:** Simple. Analytically incorrect. A finding that NIST 800-53 and NIST CSF have high convergence is not evidence of independent cross-framework validation — it is evidence that NIST writes internally consistent documents. Eliminated.

**Apply constraint only to P3:** P1 (STRM NLP Calibration) also measures semantic similarity across frameworks. The same authorship-shared-vocabulary confound applies. The constraint must apply consistently across all modules where framework independence is assumed.

**Weight within-cluster mappings differently (not exclude):** More nuanced. Requires a weighting scheme that is itself an analytical choice requiring pre-specification. The simpler exclusion rule eliminates the analytical choice while preserving the integrity of the cross-framework claim.

## Consequences

**Positive:**
- Cross-framework convergence claims are not inflated by shared authorship
- The constraint is documented and enforced at the data layer — not a judgment call made at analysis time
- Consistent application across P1 and P3 prevents inconsistent treatment of the same confound

**Negative:**
- Reduces the number of cross-framework pairs available for P3 analysis — within-NIST pairs are excluded from the primary convergence analysis
- The NIST cluster boundary is a methodological choice that could be challenged — we treat it as a clear case, but a reviewer might argue for finer-grained treatment

**Reporting:** P3 findings explicitly state the NIST cluster constraint and what fraction of STRM mappings were excluded on that basis. The within-NIST-cluster convergence is reported as a separate descriptive finding (not as independent cross-framework evidence).
