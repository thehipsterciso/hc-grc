# Documentation Contribution Guide

> **For code contributions:** see [CONTRIBUTING.md](CONTRIBUTING.md) if it exists, or README.md for project structure.
> **For research protocol contributions:** see [docs/protocol/](docs/protocol/) and the gate structure in [docs/protocol/PREREGISTRATION_LEDGER.md](docs/protocol/PREREGISTRATION_LEDGER.md).

This guide covers documentation contributions — how to write for each audience layer, what the drift check enforces, and how the compliance process works.

---

## The Three Documentation Modes

HC-GRC maintains three parallel documentation layers for the same underlying research. They are not summaries of each other — they are different documents written for different readers with different needs. Conflating them is the most common documentation failure in research projects.

### Executive Mode (P1/P2)

**Audience:** Board members, PE operating partners, C-suite executives. Thomas Jones's Persona 1 and Persona 2 from the brand positioning framework.

**Documents:** OVERVIEW.md, RESEARCH_BRIEF.md, reports/executive-summary/

**What they need:** The business problem, why it matters, and what changes when the findings are in. They will not read past a sentence that requires technical background to parse. They are not unintelligent — they are busy, and their time is the constraint.

**How to write it:**
- Open with the business problem, not the technical solution. The SCF has never been empirically tested — that is the problem. Lead with that.
- State the "so what" explicitly at every section. Not implied. Stated.
- Use analogies that illuminate rather than decorate. Maximum two per document.
- No unexplained acronyms. SCF, STRM, SAP — all require a plain-language bridge on first use.
- Strategic arc: problem → current state gap → what this builds → what it changes.
- Voice: premium executive rigor, honest contrarianism, warm authority. Not sanitized corporate language. Not FUD. See Section 3 of user preferences for the full voice architecture.
- A board member reading for 90 seconds should come away with the core thesis. Test this literally — read for 90 seconds and check.

**What executive mode is NOT:**
- A summary of the README
- A press release
- Bullet points with no connective tissue
- Technical detail that belongs in practitioner or technical mode

### Practitioner Mode (P3)

**Audience:** CDOs, CAIOs, CDAIOs, CISOs. Thomas Jones's Persona 3. People who have done this work, have seen bad GRC research before, and know exactly what to look for.

**Documents:** README.md

**What they need:** Methodological credibility signals first. Pre-registration, gate structure, null result handling. Then enough operational detail to evaluate whether this is research they could cite, commission, or build on.

**How to write it:**
- Lead with methodology. Pre-registration before data analysis is the credibility signal that separates this from industry reports. Say it directly.
- Name tools and frameworks by name. Specificity is respect. "We use LangGraph with PostgresSaver checkpointing for gate enforcement" is better than "we use a modern ML pipeline."
- Describe real complexity without sanitizing it. The STRM reliability limitation is a real constraint — name it and say what it means for interpretation.
- No over-explaining. This audience already knows what a p-value is.
- Address the organizational and career context: this is research a CDO could cite in a board conversation. Make that explicit.

**What practitioner mode is NOT:**
- Dumbed down to executive altitude
- Marketing language
- A developer README (that's technical mode)

### Technical Mode

**Audience:** ML engineers, contributors, anyone building on or extending the platform.

**Documents:** docs/architecture/AGENT_WORKFLOW.md, docs/charter/PROJECT_CHARTER.md, agent cards (agents/**/*.md), code comments

**What they need:** How to run it, how to extend it, where things live, what the interfaces are.

**How to write it:**
- Implementation-first. Architecture, interfaces, dependencies, test coverage.
- Code blocks with language tags. No language tag = won't render correctly.
- Dense but navigable — headers, code blocks, precise naming.
- Contributor-friendly: if adding a new agent, what does the card structure need? (See agents/15-platform-devsecops/repo-documentation/AGENT.md for the canonical card format.)

---

## The Drift Check

Every PR runs `scripts/check_doc_drift.py` via `.github/workflows/docs-sync.yml`. It maps changed files to the documentation layers they affect and enforces documentation currency.

Run it locally before pushing:

```bash
make check-docs
```

**What triggers a Warning (⚠️):** New agent card without README.md update. New config without navigation update. New architecture document not listed in key documents table.

**What triggers a Block (🚫):** Confirmed finding without OVERVIEW.md update (executive-layer misrepresentation). Phase transition without status update. Confirmatory analysis changes without OVERVIEW.md update.

If the drift check fires and you believe the finding is a false positive, document why in the PR template under "If no documentation changes needed."

---

## Adding or Updating Documents

### Adding a new executive-mode document

1. Draft in the correct voice (see Executive Mode above).
2. Run `make check-docs` — if OVERVIEW.md or RESEARCH_BRIEF.md changed, the drift check will flag any other affected documentation.
3. Submit PR. Drift bot posts the report.
4. Before merge: Branding Compliance Agent review, then human sign-off. Log entry in lab notebook with reviewer name and date.

### Adding or updating an agent card

Each agent card lives at `agents/[team]/[agent-name]/AGENT.md`. Required sections:

- YAML frontmatter (name, description, version, team, status, trigger, author, tags, skills, tools)
- Purpose
- Position in Workflow (diagram)
- Inputs table
- Outputs / Artifacts table
- Tools & MCP Servers table (if applicable)
- Skills Used (if applicable)
- Handoffs (**Receives from** / **Passes to** / **Human gate** if applicable)
- Behavioral Constraints
- Failure Modes & Recovery
- Evaluation Criteria

When adding a new agent card, README.md's architecture section needs updating. The drift check will enforce this.

### Updating OVERVIEW.md or RESEARCH_BRIEF.md

These are executive-mode documents. Before any commit:

1. Confirm Gate 4 has passed if the update includes confirmed findings. Gate 4 approval must be logged in the PREREGISTRATION_LEDGER before findings language enters executive-mode documents.
2. Run the Branding Compliance Agent review.
3. Human reviewer signs off — log entry in lab notebook with reviewer name and date.
4. No SCF-derived content in any public document. CC BY-ND 4.0 prohibits redistribution of derivatives. Reference the SCF source; do not reproduce its content.

---

## Branding Compliance Process

Executive-mode content (OVERVIEW.md, RESEARCH_BRIEF.md, reports/executive-summary/) goes through the Branding Compliance Agent before commit. The agent checks:

| Check | What it catches |
|-------|----------------|
| Voice consistency | Sanitized corporate language, missing "so what," over-technical sections |
| Independence positioning | Vendor alignment language without disclosure |
| Commercial disclosure | Any commercial relationship not disclosed immediately |
| Accuracy gate | Claims that conflict with confirmed research findings |
| Privacy gate | Personal history, details beyond public-facing brand |
| Gate 4 compliance | Findings language appearing before Gate 4 approval |

A PASS result + human sign-off is required before the GitHub Management Agent commits executive-mode content.

---

## Protected Paths

The following paths have elevated protection (see [.github/CODEOWNERS](.github/CODEOWNERS)):

| Path | Why protected |
|------|--------------|
| `docs/protocol/` | Pre-registered research protocol — changes are protocol events |
| `docs/protocol/PREREGISTRATION_LEDGER.md` | Append-only integrity record |
| `analysis/02-confirmatory/` | Test-split analysis — changes without Gate 2 are SAP violations |
| `data/` | SCF corpus under CC BY-ND 4.0 |
| `agents/03-analysis/` | PROTECTED P1–P5 agents — Agent Evolution cannot modify autonomously |
| `agents/04-statistical/statistical-analyst/` | PROTECTED statistical agent |
| `agents/01-research/hypothesis-formalizer/` | PROTECTED hypothesis agent |
| `OVERVIEW.md` | Executive-mode — requires Branding Compliance review |
| `RESEARCH_BRIEF.md` | Executive-mode — requires Branding Compliance review |

Changes to protected paths require Thomas Jones review before merge.
