# Compute Node Infrastructure

Operational reference for the local, data-sovereign services the platform runs
on the dedicated Apple Silicon compute node (ADR-0014). Everything here runs
on-device; no SaaS dependencies (ADR-0002). Connection parameters live in
[`configs/platform.yaml`](../../configs/platform.yaml) and are read through
`src/infrastructure/config.py`.

## Services at a glance

| Service | Role | Daemon? | How it runs | Endpoint |
|---------|------|---------|-------------|----------|
| PostgreSQL 17 | LangGraph checkpoint store (interrupt/resume across gates) | Yes | Homebrew launchd service | `localhost:5432`, db `hcgrc` |
| MLflow 3 | Experiment tracking (params, metrics, artifacts) | **No** | Serverless local SQLite file | `sqlite:///mlflow.db` |
| Phoenix | LLM trace observability (OpenTelemetry) | Yes | launchd LaunchAgent | `localhost:6006` |
| Qdrant | Vector store for P1–P5 embeddings | Yes | Docker (Colima) via compose | `localhost:6333` (REST), `6334` (gRPC) |

`run_id` is the common key across all three (ADR-0015 #79): PostgresSaver
`thread_id`, MLflow run tag `run_id`, Phoenix span attribute `run_id`. See
[RUNBOOK.md](RUNBOOK.md) for cross-store queries.

---

## PostgreSQL (checkpoint store)

Installed via Homebrew (`postgresql@17`), runs as an always-on launchd service.

```bash
brew services start postgresql@17          # start + enable at login
brew services list | grep postgres         # status
createdb hcgrc                             # one-time: create the platform db
pg_isready -h localhost -p 5432            # health check
```

Connection string comes from `HCGRC_POSTGRES_URL` (default
`postgresql://localhost:5432/hcgrc`). The checkpoint tables are created
automatically on first use by `get_checkpointer()` (`PostgresSaver.setup()`).
`postgresql@17` is keg-only; add `/opt/homebrew/opt/postgresql@17/bin` to PATH
for the `psql`/`createdb` CLIs.

Verify checkpointing end-to-end:
```bash
psql -d hcgrc -c "SELECT count(*) FROM checkpoints;"
```

## MLflow (experiment tracking)

**No server required.** MLflow writes to a local SQLite file (`mlflow.db`,
gitignored). MLflow 3 deprecated the legacy `mlruns/` file store, so we use the
supported SQLite backend — equally data-sovereign, one file, no daemon.

```python
from src.infrastructure.tracking import configure_mlflow
configure_mlflow()   # idempotent: sets tracking URI + experiment "hc-grc"
```

To browse runs in a UI (on demand, not a persistent service):
```bash
mlflow ui --backend-store-uri sqlite:///$PWD/mlflow.db
```

## Phoenix (LLM observability)

Long-lived server, managed as a launchd LaunchAgent so it survives logout and
reboot (ADR-0014 always-on).

```bash
scripts/infra/phoenix-service.sh install     # generate plist + load (RunAtLoad/KeepAlive)
scripts/infra/phoenix-service.sh status      # is it running?
scripts/infra/phoenix-service.sh logs        # tail server log
scripts/infra/phoenix-service.sh restart
scripts/infra/phoenix-service.sh uninstall
```

Trace storage is project-local (`phoenix_storage/`, gitignored) via
`PHOENIX_WORKING_DIR`. Application/agent processes wire tracing at startup:

```python
from src.infrastructure.observability import instrument_langchain
instrument_langchain(project_name="hc-grc")   # exports LangChain spans to localhost:6006
```

UI: <http://localhost:6006>.

## Qdrant (vector store)

Local vector DB for the embedding-driven analysis modules (P1–P5). Runs as a
Docker container on **Colima** (headless Docker runtime for Apple Silicon —
chosen over Docker Desktop: no GUI, no licensing). Storage persists to
`qdrant_storage/` (gitignored); the container is `restart: unless-stopped`.

```bash
brew services start colima              # Docker runtime, always-on at login
docker compose up -d qdrant             # start Qdrant (defined in docker-compose.yml)
docker compose ps                       # status / health
curl -s localhost:6333/readyz           # health check (200 = ready)
docker compose logs -f qdrant           # logs
docker compose down                     # stop
```

Colima needs the Compose plugin: `brew install docker-compose` and symlink it
into `~/.docker/cli-plugins/docker-compose`. Connection params come from
`platform.yaml -> vector_store`. Probe from Python:

```python
from src.infrastructure.vector_store import qdrant_health
qdrant_health()   # {url, reachable, collections_present, collections_missing}
```

Collections (`hcgrc_controls`, `hcgrc_mappings`, `hcgrc_literature`,
`hcgrc_findings`) are created and populated by the Embedding Agent, not here.

---

## Bringing up a fresh compute node

```bash
make install                                  # venv + Python deps
brew install postgresql@17                    # if not present
brew services start postgresql@17
createdb hcgrc
scripts/infra/phoenix-service.sh install      # Phoenix always-on
brew install colima docker docker-compose     # Docker runtime + compose
ln -sf /opt/homebrew/bin/docker-compose ~/.docker/cli-plugins/docker-compose
brew services start colima                    # Docker runtime, always-on
docker compose up -d qdrant                   # vector store
# MLflow needs nothing — first configure_mlflow() creates mlflow.db
```

## Still pending (not yet provisioned)

These remain blocked on this node and gate downstream phases:

- **Local LLM inference** (llama.cpp / Ollama) — on-device inference for the
  analysis agents. Gated on pending-decision #1 (local vs API, model choice) —
  a research-design call, see SWARM_IMPLEMENTATION_ROADMAP.md.
- **DVC local remote** — data versioning for SCF acquisition (Phase 1).
- **FAISS** all-pairs index — built by the Embedding Agent alongside Qdrant.
- **Git deploy trigger** (pull loop / webhook) — auto-deploy from the workstation.
