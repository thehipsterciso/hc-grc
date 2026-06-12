"""HC-GRC — Autonomous scientific research platform."""

from .graph import build_graph, run_phase0_synthetic
from .state import GateStatus, HCGRCState, initial_state

__all__ = [
    "HCGRCState",
    "GateStatus",
    "initial_state",
    "build_graph",
    "run_phase0_synthetic",
]
