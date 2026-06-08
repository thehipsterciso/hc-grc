"""
Set random seeds for full reproducibility from a single integer.

Usage:
    from repro.seeds import set_seeds
    set_seeds(42)

Or as a script:
    python3 -m repro.seeds 42
"""

import os
import random
import sys


def set_seeds(seed: int) -> None:
    """Set Python, NumPy, and PyTorch random seeds from a single integer.

    Also sets PYTHONHASHSEED in the environment. Call this before any stochastic
    operation. The seed is applied to every available backend; missing backends
    (numpy, torch) are silently skipped so the function is safe to call in any
    environment.

    Args:
        seed: Non-negative integer seed value.
    """
    if seed < 0:
        raise ValueError(f"seed must be non-negative, got {seed}")

    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)

    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:
        pass

    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        # Enforce deterministic algorithms where available (torch >= 1.8)
        if hasattr(torch, "use_deterministic_algorithms"):
            torch.use_deterministic_algorithms(True)
    except ImportError:
        pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python3 -m repro.seeds <seed>", file=sys.stderr)
        sys.exit(1)
    set_seeds(int(sys.argv[1]))
    print(f"Seeds set to {sys.argv[1]}.")
