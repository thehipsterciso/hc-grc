"""
Infrastructure config + MLflow URI resolution tests.

Guarded with importorskip so they no-op in the lean CI environment (which does
not install pyyaml/mlflow — Phase 0 CI runs the structural suite only). They run
under the full local venv on the compute node.
"""

from __future__ import annotations

import pytest

pytest.importorskip("yaml")

from src.infrastructure.config import load_platform_config, repo_root  # noqa: E402


def test_platform_config_loads():
    cfg = load_platform_config()
    assert cfg["platform"]["name"] == "hc-grc"
    assert "observability" in cfg


def test_repo_root_points_at_repo():
    assert (repo_root() / "configs" / "platform.yaml").exists()


def test_mlflow_tracking_uri_resolves_sqlite_to_absolute():
    pytest.importorskip("mlflow")
    from src.infrastructure.tracking.mlflow_setup import get_tracking_uri

    uri = get_tracking_uri()
    # Default config uses a relative sqlite path; it must resolve to an absolute
    # sqlite URI rooted at the repo so the store is CWD-independent.
    assert uri.startswith("sqlite:////"), uri
    assert str(repo_root()) in uri


def test_phoenix_endpoint_matches_config():
    from src.infrastructure.observability.phoenix_setup import (
        phoenix_base_url,
        phoenix_endpoint,
    )

    cfg = load_platform_config()["observability"]["phoenix"]
    expected = f"http://{cfg['host']}:{cfg['port']}"
    assert phoenix_base_url() == expected
    assert phoenix_endpoint() == f"{expected}/v1/traces"
