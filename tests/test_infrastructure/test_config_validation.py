"""
platform.yaml schema validation (hardening pass 1, #171).
"""

from __future__ import annotations

import pytest

from src.infrastructure import config


def test_real_config_loads_and_validates():
    cfg = config.load_platform_config()
    assert cfg["observability"]["phoenix"]["port"]
    assert cfg["observability"]["mlflow"]["tracking_uri"]


def test_validate_rejects_non_mapping():
    with pytest.raises(config.ConfigError, match="mapping"):
        config._validate_config(["not", "a", "dict"], "test")


def test_validate_rejects_missing_required_key():
    with pytest.raises(config.ConfigError, match="missing required config key"):
        config._validate_config({"observability": {"phoenix": {}}}, "test")
