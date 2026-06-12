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

---

## Bringing up a fresh compute node

```bash
make install                                  # venv + Python deps
brew install postgresql@17                    # if not present
brew services start postgresql@17
createdb hcgrc
scripts/infra/phoenix-service.sh install      # Phoenix always-on
# MLflow needs nothing — first configure_mlflow() creates mlflow.db
```

## Still pending (not yet provisioned)

These remain blocked on this node and gate downstream phases:

- **Qdrant** (Docker) + **FAISS** indices — vector stores for P1–P5
- **Local LLM inference** (llama.cpp / Ollama) — on-device inference for the analysis agents
- **DVC local remote** — data versioning for SCF acquisition (Phase 1)
- **Docker Compose stack** + **git deploy trigger** — orchestration and auto-deploy
