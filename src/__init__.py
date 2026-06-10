"""HC-GRC — Autonomous scientific research platform."""

from .state import HCGRCState, GateStatus, initial_state
from .graph import build_graph, run_phase0_synthetic

__all__ = [
    "HCGRCState",
    "GateStatus",
    "initial_state",
    "build_graph",
    "run_phase0_synthetic",
]
