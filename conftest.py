"""
Root conftest.py — ensures the repo root is on sys.path for all pytest runs.

Tests import from src.* (e.g., `from src.state import HCGRCState`). This works
when pytest is invoked from the repo root but may fail in CI environments where
the working directory or Python path differs. This file is loaded by pytest before
any test collection and guarantees the import works regardless of invocation context.
"""

import os
import sys
from pathlib import Path

# Add repo root to sys.path so `import src.xxx` works everywhere.
repo_root = Path(__file__).parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Default the suite to the no-LLM path: graph/node tests must be deterministic and
# offline (no Ollama / no frontier calls). Tests that exercise the real
# reasoning_client backends opt back in explicitly (monkeypatch.delenv).
os.environ.setdefault("HCGRC_DISABLE_REASONING", "1")
