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

# Golden fingerprint of the seed=42 partition of _IDS (1400 synthetic controls).
_GOLDEN_SPLIT_SHA256 = "a46378cbc7fb9ae65247b7e090021737c08eeb52133970bd92ef5b83e485948b"


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


def test_partition_matches_golden_hash():
    # Pin the seed=42 partition to a golden fingerprint so a change in the RNG /
    # numpy / split logic that alters the firewall is caught, not just run-A==run-B
    # within a process (#222). If this changes intentionally, update the golden.
    import hashlib

    s = compute_data_split(_IDS, seed=42)
    fp = hashlib.sha256(
        "|".join(s["train_ids"] + ["::"] + s["val_ids"] + ["::"] + s["test_ids"]).encode()
    ).hexdigest()
    assert fp == _GOLDEN_SPLIT_SHA256, (
        f"seed=42 partition changed (got {fp}). If intentional, update the golden."
    )


def test_duplicate_ids_raise_leakage_assertion():
    # The real firewall risk is the SAME id landing in two splits. Feeding a
    # duplicated id must trip the leakage assertion, not pass silently (#223).
    import pytest
    dup = [f"SCF-CTRL-{i:04d}" for i in range(100)] * 2  # every id appears twice
    with pytest.raises(AssertionError):
        compute_data_split(dup, seed=42)
