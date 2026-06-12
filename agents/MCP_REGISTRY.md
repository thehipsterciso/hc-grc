# MCP Server Registry

**Version:** 0.1.0
**Status:** Draft — authored 2026-06-12 (closes #120)

The authoritative registry of MCP servers (and the one non-MCP tool) that agent cards
declare in their `tools:` frontmatter. Card `## Tools & MCP Servers` sections reference
the identifiers here. The usage counts are derived from `agents/generated/INFRASTRUCTURE_REQUIREMENTS.md`
(regenerate with `make generate-docs`).

All servers are **local-first per ADR-0002** unless the "Boundary" column says otherwise —
no SCF-derived data leaves the machine.

| Identifier | Backing service | Purpose | Key operations | Boundary | Used by |
|------------|-----------------|---------|----------------|----------|--------:|
| `mcp-lab-notebook` | `lab_notebook.md` (append-only) | The anti-cherry-picking decision/anomaly record every agent writes to | `append_entry`, `read_entries` | Local | 49 |
| `mcp-dvc` | DVC (local remote) | Version data, models, and report artifacts; retrieve content hashes | `add`, `push`, `status`, `get_hash` | Local | 26 |
| `mcp-mlflow` | MLflow (local SQLite, `mlflow.db`) | Experiment/metric/param logging keyed by `run_id` | `log_run`, `log_metric`, `log_param`, `get_run` | Local | 20 |
| `mcp-qdrant` | Qdrant (local Docker, :6333) | Vector store over control/mapping embeddings; collections `hcgrc_controls`, `hcgrc_mappings` | `upsert`, `search`, `get_collection` | Local | 9 |
| `mcp-github` | GitHub (`gh`) | Repo operations: commit, branch, PR, issue, branch protection | `commit`, `create_pr`, `branch`, `issue` | **External** (code/issues only — never SCF data) | 9 |
| `mcp-phoenix` | Arize Phoenix (local, :6001) | LLM observability traces keyed by `run_id` | `export_trace`, `query_traces` | Local | 4 |
| `mcp-sap-validator` | SAP lock service | Confirm the Gate-2 SAP lock and validate a hypothesis against the locked plan | `confirm_lock`, `validate_hypothesis` | Local | 4 |
| `mcp-langgraph` | LangGraph PostgresSaver (local Postgres :5432) | Graph checkpoint/replay; `thread_id == run_id` | `checkpoint`, `resume`, `get_state` | Local | 2 |
| `mcp-literature-search` | External literature indexes | Literature discovery for the Literature Agent | `search`, `fetch` | **External** (queries public indexes; no SCF data transmitted) | 1 |

## Notes

- **`langgraph-checkpointer`** appearing in some card frontmatter is the same capability as `mcp-langgraph`; cards are being normalized to `mcp-langgraph` (orchestrator updated 2026-06-12).
- Validation: `tools[]` entries must match the `mcp-*` pattern (CARDS_SPEC rule 8); `tools/generate_docs.py` warns on any that do not.
- This registry is the source of truth for the `## Tools & MCP Servers` purpose text added to cards under #119.
