"""
MLflow tracking setup for HC-GRC (roadmap Phase 0, deliverable #1).

DATA SOVEREIGNTY (ADR-0002): MLflow runs against a LOCAL SQLITE backend — a
single file on the compute node (configs/platform.yaml ->
observability.mlflow.tracking_uri, default "sqlite:///mlflow.db"). No remote
tracking server, no SaaS — nothing leaves the machine.

(MLflow 3 put the legacy filesystem store, e.g. "mlruns/", into maintenance
mode; it refuses writes without MLFLOW_ALLOW_FILE_STORE=true and receives no
new features. SQLite is the supported local backend and is equally
data-sovereign — one file, no daemon.)

The SQLite backend needs NO running daemon: experiment data is written
directly to the .db file. A server is only needed to *view* runs, via
`mlflow ui --backend-store-uri <uri>` (see launch_ui_command()).

run_id propagation (ADR-0015 #79): callers should tag every run with the
platform run_id so it cross-references PostgresSaver/Phoenix/PROV-DM:
    mlflow.set_tag("run_id", state["run_id"])
"""

from __future__ import annotations

import os
from pathlib import Path

import mlflow

from ..config import load_platform_config, repo_root

_REMOTE_SCHEMES = ("http://", "https://", "postgresql:", "file:")
_SQLITE_PREFIX = "sqlite:///"


def get_tracking_uri() -> str:
    """
    Resolve the MLflow tracking URI from platform config.

    A relative SQLite path ("sqlite:///mlflow.db") or a bare relative directory
    ("mlruns") is resolved to an absolute location under the repo root, so the
    store is independent of the working directory. Absolute paths and remote
    schemes (http:, postgresql:, file:) pass through untouched.
    """
    cfg = load_platform_config()["observability"]["mlflow"]
    uri = cfg.get("tracking_uri", f"{_SQLITE_PREFIX}mlflow.db")
    if uri.startswith(_SQLITE_PREFIX):
        path = uri[len(_SQLITE_PREFIX):]
        if not os.path.isabs(path):
            path = str(repo_root() / path)
        return f"{_SQLITE_PREFIX}{path}"
    if uri.startswith(_REMOTE_SCHEMES) or os.path.isabs(uri):
        return uri
    return str(repo_root() / uri)


def configure_mlflow() -> str:
    """
    Point MLflow at the local store and select the platform experiment.

    Idempotent — safe to call at the start of every run. Returns the resolved
    tracking URI for logging/verification.
    """
    cfg = load_platform_config()["observability"]["mlflow"]
    uri = get_tracking_uri()
    # A bare local directory (legacy file store) must exist; sqlite/remote do not.
    if not uri.startswith(_SQLITE_PREFIX) and not uri.startswith(_REMOTE_SCHEMES):
        Path(uri).mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(cfg.get("experiment_name", "hc-grc"))
    return uri


def launch_ui_command() -> str:
    """Return the shell command to view runs in the MLflow UI."""
    return f"mlflow ui --backend-store-uri {get_tracking_uri()}"


if __name__ == "__main__":  # pragma: no cover - operational entrypoint
    resolved = configure_mlflow()
    print(f"MLflow configured. tracking_uri={resolved}")
    print(f"View runs with: {launch_ui_command()}")
