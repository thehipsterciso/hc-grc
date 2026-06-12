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


@functools.lru_cache(maxsize=1)
def load_platform_config() -> dict[str, Any]:
    """
    Load and cache configs/platform.yaml.

    Cached for the process lifetime — platform-scope config is stable within a
    run. Call load_platform_config.cache_clear() in tests that mutate the file.
    """
    config_path = repo_root() / "configs" / "platform.yaml"
    if not config_path.exists():
        raise FileNotFoundError(
            f"Platform config not found at {config_path}. "
            "Infrastructure modules require configs/platform.yaml."
        )
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)
