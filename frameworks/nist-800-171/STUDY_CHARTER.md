# Study Charter — NIST SP 800-171 Rev 3

## Identity
- **Framework:** NIST SP 800-171 Revision 3 (protecting CUI)
- **Short ID:** F4
- **Source:** NIST OSCAL content (github.com/usnistgov/oscal-content)
- **License:** public domain; native control text available (OSCAL)
- **Role:** native corpus

## Licensing status (T2)
- [x] Public domain — no rights barrier; pin the OSCAL release.

## Scope
Program pipeline S1f–S9 on 800-171 Rev 3, using its requirement families as the imposed taxonomy
for Q4/Q5. 800-171 is a scoped derivative of 800-53 (CUI subset) — a useful structural relationship
to surface, but findings are computed natively, not inherited from F2.

## Framework-specific notes
- Control count / granularity: ~110+ requirements across 17 families (pin at S4).
- Derives from 800-53 — Tier B should examine whether its structure mirrors or diverges from F2;
  shared lineage is a confound the `data-scientist-adversary` must flag (F2 and F4 are NOT fully
  independent and must not be counted as two independent replications without that caveat).

## Status
Stub — not started.
