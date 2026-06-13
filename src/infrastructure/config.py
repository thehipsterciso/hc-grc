"""
Platform configuration loader.

Single source of truth for reading configs/platform.yaml. Infrastructure
modules use this so host/port/uri parameters are never hardcoded — they
track the version-controlled config.
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

import yaml


def repo_root() -> Path:
    """Return the repository root (three levels up from this file)."""
    return Path(__file__).resolve().parents[2]


class ConfigError(ValueError):
    """Raised when configs/platform.yaml is malformed or missing required keys."""


# Required structure (dotted paths). Validated at load so a silent typo or a
# dropped section fails loudly at startup rather than as a confusing KeyError deep
# in an infrastructure module (#171).
_REQUIRED_PATHS = (
    "observability.phoenix.port",
    "observability.phoenix.project_name",
    "observability.mlflow.tracking_uri",
    "vector_store.host",       # dereferenced by qdrant_setup (#207)
    "vector_store.http_port",
    "checkpointing.backend",   # drives PostgresSaver selection (#271)
    "checkpointing.database",
)


def _validate_config(cfg: Any, source: str) -> dict[str, Any]:
    if not isinstance(cfg, dict):
        raise ConfigError(f"{source}: top-level YAML must be a mapping, got {type(cfg).__name__}.")
    for path in _REQUIRED_PATHS:
        node: Any = cfg
        for key in path.split("."):
            if not isinstance(node, dict) or key not in node:
                raise ConfigError(f"{source}: missing required config key '{path}'.")
            node = node[key]
    return cfg


@functools.lru_cache(maxsize=1)
def load_platform_config() -> dict[str, Any]:
    """
    Load, validate, and cache configs/platform.yaml.

    Cached for the process lifetime — platform-scope config is stable within a
    run. Call load_platform_config.cache_clear() in tests that mutate the file.
    Raises ConfigError if required sections are missing.
    """
    config_path = repo_root() / "configs" / "platform.yaml"
    if not config_path.exists():
        raise FileNotFoundError(
            f"Platform config not found at {config_path}. "
            "Infrastructure modules require configs/platform.yaml."
        )
    with config_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    return _validate_config(cfg, str(config_path))
