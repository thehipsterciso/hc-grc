"""
Graph/node-level data-split determinism (hardening pass 1, #170 / #27).

compute_data_split() idempotency is covered in test_data_split.py; this pins the
*node-level* synthetic seed and asserts the full partition is byte-for-byte
reproducible across independent runs — the firewall guarantee, not merely
'seed is not None'.
"""

from __future__ import annotations

from src.nodes.data_split import compute_data_split, data_split_node

_IDS = [f"SCF-CTRL-{i:04d}" for i in range(1400)]


def test_phase0_node_seed_is_pinned():
    r = data_split_node({"run_id": "a"}, synthetic_control_ids=_IDS)
    assert r["data_split_seed"] == 42  # pinned, deterministic — not just non-null
    assert r["data_split_verified"] is True


def test_phase0_node_seed_stable_across_runs():
    a = data_split_node({"run_id": "a"}, synthetic_control_ids=_IDS)
    b = data_split_node({"run_id": "b"}, synthetic_control_ids=_IDS)
    assert a["data_split_seed"] == b["data_split_seed"]


def test_partition_is_byte_for_byte_reproducible():
    s1 = compute_data_split(_IDS, seed=42)
    s2 = compute_data_split(_IDS, seed=42)
    assert s1["train_ids"] == s2["train_ids"]
    assert s1["val_ids"] == s2["val_ids"]
    assert s1["test_ids"] == s2["test_ids"]
