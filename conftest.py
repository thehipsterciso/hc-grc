"""
Root conftest.py — ensures the repo root is on sys.path for all pytest runs.

Tests import from src.* (e.g., `from src.state import HCGRCState`). This works
when pytest is invoked from the repo root but may fail in CI environments where
the working directory or Python path differs. This file is loaded by pytest before
any test collection and guarantees the import works regardless of invocation context.
"""

import sys
from pathlib import Path

# Add repo root to sys.path so `import src.xxx` works everywhere.
repo_root = Path(__file__).parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
