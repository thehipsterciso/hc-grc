# Study Charter — Secure Controls Framework (SCF)

## Identity
- **Framework:** Secure Controls Framework, latest release (2026.x)
- **Short ID:** F1
- **Source:** securecontrolsframework.com (ComplianceForge); upstream workbook
- **License:** Creative Commons (per ComplianceForge terms); native control text available
- **Role:** corpus **and** cross-framework crosswalk

## Dual role — read this first
The SCF is studied like any other framework (Q1–Q8), **and** it is the alignment layer for Tier B.
The SCF maps ~1,468 controls across 200+ frameworks, including F2–F5. Its mapping table is what lets
the cross-framework synthesis (X1) align independently-authored frameworks onto a common substrate.

Two consequences the adversary must enforce:
1. **Do not let the SCF's editorial structure leak into cross-framework claims.** The SCF's own
   taxonomy is one framework's opinion; findings about "control space" must be tested against the
   *native* frameworks (F2–F5), not assumed from the SCF.
2. **Crosswalk quality is a measured quantity, not an assumption.** Coverage, many-to-many fan-out,
   and mapping confidence are characterized in S4 and carried into every Tier B claim as a stated
   limitation. A noisy crosswalk weakens cross-framework results and must be reported, not hidden.

## Licensing status (T2)
- [x] CC license permits ingest + embedding of SCF text.
- [ ] Confirm release version and pin it in the registry.

## Scope
Program pipeline S1f–S9 on the SCF corpus, plus production of the crosswalk artifact consumed by
`synthesis/` X1.

## Framework-specific notes
- Control count / granularity: ~1,468 controls, 30+ domains (pin exact at S4).
- Crosswalk is the highest-value artifact for the program; prioritize its S4.
- Watch for: paywalled mapped frameworks appearing as identifiers-only in the crosswalk.

## Status
Stub — not started. On the Tier B critical path (produces the crosswalk).
