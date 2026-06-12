"""
compute_data_split — deterministic, idempotent SCF corpus partitioning.

Seed derivation: SHA-256 of the raw manifest file → int.from_bytes() → int seed.
Same manifest → identical seed → identical split on every independent run.
This is the idempotency guarantee tested in test_phase0/test_data_split.py.

Split strategy: shuffle-and-slice on UNIQUE SCF control IDs (per SAP §7 / issue #60).
Semantically equivalent to GroupKFold when control_ids contains exactly one entry
per unique control. CALLER CONTRACT: control_ids must be deduplicated before calling —
one ID per control, not one row per STRM mapping. Passing mapping rows (280,000) instead
of control IDs (1,400) would produce leakage because set(train_ids) & set(test_ids) only
catches list-level duplicates, not the case where the same control's mapping rows land
in separate splits. The DataSplitAgent is responsible for deduplication before this call.

No SCF control text appears in both train and test partitions (given the caller contract).
DataSplitAgent asserts len(set(train_ids) ∩ test_ids) == 0 before writing.
This assertion is logged and is a required Gate 1 artifact.

Split ratios: 70% train / 15% validation / 15% test.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np

# ── Seed derivation ───────────────────────────────────────────────────────────


def derive_seed(manifest_path: Path | str) -> tuple[str, int]:
    """
    Derive a deterministic integer seed from the SHA-256 hash of a manifest file.

    Returns:
        (manifest_hash_hex, seed_int)
    """
    path = Path(manifest_path)
    raw = path.read_bytes()
    h = hashlib.sha256(raw)
    manifest_hash = h.hexdigest()
    # 8 bytes (64-bit) → 1-in-2^64 collision probability between different manifests.
    # Using int.from_bytes on the raw digest (not the hex string) for portability.
    seed = int.from_bytes(h.digest()[:8], byteorder="big")
    return manifest_hash, seed


# ── Core split function ───────────────────────────────────────────────────────


def compute_data_split(
    control_ids: list[str],
    manifest_path: Path | str | None = None,
    seed: int | None = None,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    # test_ratio is 1 - train_ratio - val_ratio = 0.15
) -> dict[str, Any]:
    """
    Partition control_ids into train / validation / test splits.

    Exactly one of manifest_path or seed must be provided.
    - manifest_path: derive seed from SHA-256 of the file (production path)
    - seed: use directly (test / synthetic data path)

    Returns:
        {
            "train_ids": [...],
            "val_ids": [...],
            "test_ids": [...],
            "seed": int,
            "manifest_hash": str | None,
            "n_controls": int,
            "split_ratios": {"train": float, "val": float, "test": float},
        }

    Raises:
        AssertionError if any control ID appears in more than one split.
    """
    if manifest_path is not None and seed is not None:
        raise ValueError("Provide manifest_path OR seed, not both.")
    if manifest_path is None and seed is None:
        raise ValueError("Provide either manifest_path or seed.")

    manifest_hash: str | None = None
    if manifest_path is not None:
        manifest_hash, seed = derive_seed(manifest_path)

    rng = np.random.default_rng(seed)
    ids = np.array(control_ids)
    n = len(ids)

    # Shuffle with seeded RNG
    shuffled_indices = rng.permutation(n)
    shuffled_ids = ids[shuffled_indices]

    # Compute split boundaries
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)

    train_ids = shuffled_ids[:train_end].tolist()
    val_ids = shuffled_ids[train_end:val_end].tolist()
    test_ids = shuffled_ids[val_end:].tolist()

    # ── Leakage assertion (required Gate 1 artifact) ─────────────────────────
    train_set = set(train_ids)
    val_set = set(val_ids)
    test_set = set(test_ids)

    assert len(train_set & test_set) == 0, (
        f"LEAKAGE: {len(train_set & test_set)} control IDs appear in both train and test"
    )
    assert len(train_set & val_set) == 0, (
        f"LEAKAGE: {len(train_set & val_set)} control IDs appear in both train and val"
    )
    assert len(val_set & test_set) == 0, (
        f"LEAKAGE: {len(val_set & test_set)} control IDs appear in both val and test"
    )
    assert len(train_ids) + len(val_ids) + len(test_ids) == n, (
        "Split sizes do not sum to total control count"
    )

    actual_train = len(train_ids) / n
    actual_val = len(val_ids) / n
    actual_test = len(test_ids) / n

    return {
        "train_ids": train_ids,
        "val_ids": val_ids,
        "test_ids": test_ids,
        "seed": seed,
        "manifest_hash": manifest_hash,
        "n_controls": n,
        "split_ratios": {
            "train": round(actual_train, 4),
            "val": round(actual_val, 4),
            "test": round(actual_test, 4),
        },
    }


# ── LangGraph node wrapper ────────────────────────────────────────────────────


def data_split_node(state: dict[str, Any], manifest_path: Path | str | None = None,
                    synthetic_control_ids: list[str] | None = None) -> dict[str, Any]:
    """
    LangGraph node: compute and record the data split in state.

    In Phase 0: uses synthetic_control_ids with a fixed seed (no manifest).
    In Phase 1+: uses manifest_path to derive the seed from the real corpus.
    """
    # Phase 0 synthetic mode
    if synthetic_control_ids is not None:
        result = compute_data_split(synthetic_control_ids, seed=state.get("data_split_seed") or 42)
    elif manifest_path is not None:
        result = compute_data_split(list(state.get("control_ids", [])), manifest_path=manifest_path)
    else:
        raise ValueError("Provide manifest_path or synthetic_control_ids.")

    return {
        "data_split_manifest_hash": result["manifest_hash"],
        "data_split_seed": result["seed"],
        "data_split_verified": True,
        "prov_activities": [
            {
                "activity": "data_split",
                "run_id": state.get("run_id"),
                "seed": result["seed"],
                "n_controls": result["n_controls"],
                "split_ratios": result["split_ratios"],
                "leakage_assertion": "passed",
            }
        ],
    }
