# Transcript: data-scientist — P1 Pre-registration Rewrite
**Date:** 2026-06-08
**Stage:** P1
**Agent:** data-scientist/claude-sonnet-4-6@hc-macbook-pro.local (Tier-1 producer, P1 lead)
**Task:** Rewrite docs/PREREGISTRATION.md to fix all 16 adversary-identified defects
**Status:** COMPLETED. PENDING ADVERSARY REVIEW (data-scientist-adversary/claude-opus-4-8@hc-macbook-pro.local).

## Files Written
- `docs/PREREGISTRATION.md` (version 2.0-draft)

## All 16 Defects Addressed

| Defect | Severity | Resolution |
|--------|----------|------------|
| D1 — Algorithm names in methods | Critical | Removed all algorithm names; replaced with capability descriptions |
| D2 — Directional Q4 hypothesis | Critical | Rewrote as neutral; both directions equally valid findings |
| D3 — Thresholds before data | Critical | All thresholds → [DEFERRED — set after S3] |
| D4 — Success criteria reward outcomes | High | All rewritten as "method applied correctly, results reported regardless of direction" |
| D5 — No falsifiability per question | High | Added `Falsifiability:` field to every question |
| D6 — SCF circularity not documented | High | Registered as structural limitation L1 with two mitigations |
| D7 — No assumptions ledger | High | Section 5 — 6 entries with assumption, falsifying condition, consequence |
| D8 — CIA triad null underspecified | Medium | Null: uniform CIA representation across categories |
| D9 — No stopping rule | Medium | Section 8 — 5-step procedure, no imputation clause |
| D10 — Evidence class definitions missing | Medium | Section 6 — Robust, Provisional, Framework-specific, Crosswalk-dependent, Intrinsic, Method failure |
| D11 — No pre-analysis exclusion criteria | Medium | Section 7 — 4 criteria: null text, duplicate ID, min token length, placeholder text |
| D12 — Per/cross-framework mixed | Low | Separated: sections 11 (per-framework Q1-Q7) and 12 (cross-framework X-Q1 through X-Q3) |
| D13 — No version/hash placeholder | Low | Header: version 2.0-draft, sha256 [FROZEN AT T1] |
| D14 — Ensemble size undefined | Low | Section 10 — size 3, model selection deferred to T3 |
| D15 — Bootstrap CI unspecified | Low | Section 9 — 10,000 iterations, 95% BCa |
| D16 — NIST independence problem | Critical | Registered as structural limitation L2; intrinsic requires ≥1 non-NIST replication |

## Definition of Done
1. All 16 defects addressed ✓
2. No algorithm names ✓
3. All thresholds [DEFERRED] ✓
4. Q4 hypothesis neutral ✓
5. SCF circularity documented ✓
6. NIST cluster documented ✓
7. Assumptions ledger present ✓
8. Per/cross-framework questions separated ✓
9. sha256 placeholder present ✓
10. Document is a DRAFT — not frozen ✓
