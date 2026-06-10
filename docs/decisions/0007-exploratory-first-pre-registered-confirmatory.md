# ADR-0007: Exploratory-First, Pre-registered Confirmatory Protocol

**Status:** Accepted
**Date:** 2026-06-09
**Deciders:** Thomas Jones

---

## Context

The SCF/STRM corpus has never been empirically analyzed at scale. Attempting to write pre-specified hypotheses with effect size thresholds before examining the data produces either trivial hypotheses (ones where the effect is so obvious it needs no test) or poorly-calibrated ones (where the pre-specified effect size has no relationship to what the data can actually show). This is a known failure mode in empirical science — Thomas pushes back on the initial recommendation to lock the full SAP before data acquisition for exactly this reason.

At the same time, a purely exploratory analysis without pre-registration has no protection against p-hacking, HARKing (Hypothesizing After Results are Known), or selective reporting. The combination of "we explored first" and "we then pre-registered what we found" is the most common form of research misconduct in empirical work — the exploratory results are laundered into confirmatory claims.

## Decision

The protocol is explicitly split at the exploratory/confirmatory boundary, enforced structurally:

**Phase 1 (Exploratory):** Characterize the corpus. Generate hypotheses. Run on train + validation splits only. Report descriptive statistics, distributions, and patterns — no p-values, no significance claims.

**Gate 2 (SAP lock):** Write specific hypotheses (H[module].[n]) with named tests and effect sizes, calibrated to what exploratory analysis revealed. Lock the SAP on the pre-registration branch with RFC 3161 timestamp. Release the test split.

**Phase 2 (Confirmatory):** Test only the pre-specified hypotheses. Run on the test split. No new hypotheses from this data. Null results reported with identical rigor.

The exploratory/confirmatory firewall is enforced at Gate 2 — the test split is physically inaccessible before that gate passes.

What is locked at framework pre-registration (before any data is examined): research questions, theoretical framework, methods scaffolding (test families, split strategy, seed management, firewall rules). What is deferred to the SAP: specific hypotheses, effect sizes, named test variants.

## Alternatives Considered

**Full SAP before data acquisition:** Recommended by some pre-registration frameworks. Rejected because it produces hypotheses without empirical grounding in a corpus that has never been characterized. The methods scaffolding approach (locking test families and rules without committing to specific parameters) achieves the anti-p-hacking goal while avoiding the under-powered hypothesis problem.

**Exploratory only, no confirmatory:** Appropriate for a pure characterization study. Rejected because the platform's scientific contribution claims include hypothesis testing. Pure exploratory work cannot make confirmatory claims.

**Registered report format (peer review before data collection):** TOP Level 3, strongest protection. Impractical for a first-of-its-kind corpus characterization where the relevant venue's reviewers have no baseline for what effect sizes are plausible. May be appropriate for follow-on studies.

## Consequences

**Positive:**
- Exploratory findings are calibrated to the actual data before hypotheses are committed
- Confirmatory analysis is protected by structural data access controls, not convention
- The protocol has a citation handle: this is the "split exploratory/confirmatory" design described in TOP guidelines and Kahneman's adversarial collaboration framing

**Negative:**
- Two-phase protocol requires more operational discipline than a single-phase study
- Gate 2 is irreversible — a poorly written SAP at Gate 2 cannot be un-locked without an amendment and ledger entry
- The protocol is nonstandard enough that it requires explanation in every methods section

**Citation handle:** The Transparency and Openness Promotion (TOP) guidelines (https://www.cos.io/initiatives/top-guidelines) describe this split under Study Registration and Analysis Plan practices. The methods scaffolding design is closest to "Level 1 — Disclosed" for Analysis Plan, upgrading to "Level 2 — Shared and Cited" at SAP lock.
