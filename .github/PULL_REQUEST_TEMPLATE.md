## Summary

<!-- What does this PR change, and why? One paragraph. -->

## Documentation Drift Checklist

Run `make check-docs` locally before pushing to avoid unnecessary CI cycles.
The drift bot will post a report on this PR. Before requesting review, confirm:

- [ ] I have read the documentation drift report posted by the bot on this PR
- [ ] All ⚠️ Warning items are resolved or I have documented why they are not applicable
- [ ] There are no 🚫 Critical items blocking merge (or this PR resolves them)

### Documentation updated (check all that apply)

- [ ] README.md — architecture or status section updated (search `## Architecture` or `## Status`)
- [ ] OVERVIEW.md — not applicable, or updated with human branding review completed (see below)
- [ ] Agent card(s) — added or modified in `agents/`
- [ ] ADR added to `docs/decisions/` and listed in README.md Key Documents table
- [ ] No documentation changes needed — see legitimate exceptions below

**If no documentation changes needed**, confirm one of these applies:
- Dependency version bump with no API or behavior change
- Test-only change (files entirely under `tests/`) with no new behavior
- Fix to a typo or formatting in an existing document (no content change)
- Internal tooling change with no user-facing impact

If none of these applies, document why documentation is not affected:
<!-- Explain: -->

## Research Integrity

**Applies to:** any PR touching `data/`, `models/`, `analysis/`, `evaluation/`, `docs/protocol/`, or `configs/`.

- [ ] Not applicable — this PR does not touch any of the above paths
- [ ] Gate status unchanged — no phase transition in this PR
- [ ] SAP is current — no confirmatory analysis modified without Gate 2 approval
- [ ] Test split not accessed before Gate 3 approval
- [ ] Pre-registration ledger unchanged — or change is a legitimate ledger update with second-reviewer sign-off

## Branding Compliance (executive-mode content)

**Applies to:** any PR modifying `OVERVIEW.md`, `RESEARCH_BRIEF.md`, or `reports/executive-summary/`.

Executive-mode documents (P1/P2 audience: board, PE, C-suite) require human branding review
before merge. This is currently a human-in-the-loop step — there is no automated compliance
agent. The reviewer must confirm: premium executive voice (no unexplained jargon, "so what"
explicit at each section), no unconfirmed research findings framed as conclusions, no
independence claims that are not substantiated.

- [ ] Not applicable — this PR does not touch executive-mode content
- [ ] Human branding review completed — lab notebook entry made with reviewer name and date
- [ ] No research findings presented as conclusions before Gate 4 approval
- [ ] No SCF data or derived content (paraphrase, summary, or embedding output) included
      in any public-facing document — CC BY-ND 4.0 constraint

## Security

- [ ] No secrets, credentials, `.env` files, or API keys committed
- [ ] No SCF-derived datasets, embeddings, or indices exported off-machine (CC BY-ND 4.0)
- [ ] No SCF-derived prose or paraphrase in any public document (see Branding Compliance above)
- [ ] No SaaS integrations introduced (LangSmith, Pinecone, W&B disqualified — local-first only)
- [ ] Independence claims in executive content (if any) are substantiated — no vendor
      relationships omitted that would qualify the independence assertion
