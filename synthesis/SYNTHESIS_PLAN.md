# Cross-Framework Synthesis Plan (Tier B)

Tier B turns five independent per-framework characterizations into the program's distinctive
evidence: what survives across independently-authored frameworks. It is also where the discipline
against premature conclusions matters most, so the stance step is isolated, late, and gated.

Begins when ≥ 2 frameworks are certified through S9; re-runs as each additional framework lands.

## X1 — Alignment
Align F1–F5 controls onto a common substrate using the SCF crosswalk (`frameworks/scf/`).
- Measure crosswalk coverage and many-to-many fan-out; record alignment quality.
- Alignment quality is carried into every downstream claim as a stated limitation.
- Owner: `data-engineer` + `data-scientist`; certified by `data-engineer-adversary`.

## X2 — Cross-framework triangulation
For each per-framework result (Q2–Q8), test replication across frameworks and classify:
- **Intrinsic** — holds in ≥ k of 5 within overlapping CIs (k set at T1). Strong evidence of a
  property of control space.
- **Framework-specific** — holds in some, not others.
- **Crosswalk-dependent** — sensitive to alignment quality.
- Independence accounting: F2 (800-53) and F4 (800-171) share lineage and are **not** two
  independent replications; CIS (F5) is genuinely independent. The adversary rejects any
  "intrinsic" label that double-counts F2/F4.
- Owner: `data-scientist` + `knowledge-synthesizer`; certified by `knowledge-synthesizer-adversary`.

## X3 — Insight & gap map
A description (not an argument) of what was found: agreements, divergences, thin/isolated coverage,
taxonomy fractures — each tagged with its X2 evidence class and limitations.

## X4 — Stance synthesis  *(late, derivative, gated — T4)*
Only here does the program theorize. Input is the X3 map and nothing else. Articulate a defensible
stance about control space; every claim must trace to an X2 result of stated evidence class.
- The adversary's job here is to **resist overreach** (premortem + competing-hypotheses stances).
- Cross-discipline backstop: `competitive-analyst` (defensibility vs literature), `product-manager`
  (overclaim).
- A human signs off before this stage is written, acknowledging it is interpretive.

## X5 — Release  *(T5)*
Two congruent tracks — scientific record (every claim cited to an artifact) and a leadership
translation (every claim traced to a scientific section, no overclaim, no fear-selling) — plus a
reproducibility package. One human read before release.

## Anti-confirmation guardrails
- No stance language anywhere upstream of X4. Q1–Q8 and X1–X3 describe; they do not argue.
- "Intrinsic" is earned by cross-framework replication, never asserted.
- Correlated evidence (shared embedding or shared framework lineage) is never called independent.
- If the findings do not support a strong stance, X4 says so. A null or modest result is a valid
  output and ships.
