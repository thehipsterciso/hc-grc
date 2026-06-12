"""
test_data_split.py — compute_data_split() idempotency tests.

Phase 0 deliverable #3: verify that compute_data_split() produces
identical splits on two independent runs given the same seed.

This is the cryptographic guarantee that the exploratory/confirmatory
firewall cannot be accidentally broken by re-running the split.

Tests:
  1. Two independent calls with same seed → identical splits
  2. Different seed → different splits
  3. Leakage assertions pass (no control ID in more than one partition)
  4. Split sizes sum to total control count
  5. Split ratios are approximately 70/15/15
  6. SHA-256 seed derivation is deterministic from same file
  7. GroupKFold-style guarantee: no ID appears in both train and test
"""

from __future__ import annotations

import hashlib
import json

import pytest

from src.nodes.data_split import compute_data_split, derive_seed

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def synthetic_control_ids():
    """1,400 synthetic SCF control IDs — matches SCF corpus scale."""
    return [f"SCF-CTRL-{i:04d}" for i in range(1400)]


@pytest.fixture
def small_control_ids():
    """100 controls for fast tests."""
    return [f"SCF-CTRL-{i:04d}" for i in range(100)]


@pytest.fixture
def manifest_file(tmp_path):
    """Write a deterministic manifest JSON file and return its path."""
    manifest = {
        "version": "1.0.0",
        "corpus": "scf-v2024.3",
        "control_count": 1400,
        "domains": 33,
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest, sort_keys=True))
    return path


# ── Idempotency tests ─────────────────────────────────────────────────────────

class TestIdempotency:
    """Two independent runs with same seed must produce identical splits."""

    def test_same_seed_identical_splits(self, synthetic_control_ids):
        """Core idempotency guarantee."""
        result_a = compute_data_split(synthetic_control_ids, seed=42)
        result_b = compute_data_split(synthetic_control_ids, seed=42)

        assert result_a["train_ids"] == result_b["train_ids"]
        assert result_a["val_ids"] == result_b["val_ids"]
        assert result_a["test_ids"] == result_b["test_ids"]

    def test_same_manifest_identical_splits(self, synthetic_control_ids, manifest_file):
        """Manifest-derived seed produces identical splits."""
        result_a = compute_data_split(synthetic_control_ids, manifest_path=manifest_file)
        result_b = compute_data_split(synthetic_control_ids, manifest_path=manifest_file)

        assert result_a["train_ids"] == result_b["train_ids"]
        assert result_a["val_ids"] == result_b["val_ids"]
        assert result_a["test_ids"] == result_b["test_ids"]
        assert result_a["manifest_hash"] == result_b["manifest_hash"]
        assert result_a["seed"] == result_b["seed"]

    def test_different_seed_different_splits(self, synthetic_control_ids):
        """Different seeds produce different splits."""
        result_a = compute_data_split(synthetic_control_ids, seed=42)
        result_b = compute_data_split(synthetic_control_ids, seed=99)

        # Extremely unlikely to be identical with 1,400 controls
        assert result_a["train_ids"] != result_b["train_ids"]

    def test_manifest_hash_is_sha256(self, synthetic_control_ids, manifest_file):
        """manifest_hash is the hex SHA-256 of the file."""
        result = compute_data_split(synthetic_control_ids, manifest_path=manifest_file)
        expected_hash = hashlib.sha256(manifest_file.read_bytes()).hexdigest()
        assert result["manifest_hash"] == expected_hash


# ── Leakage tests ─────────────────────────────────────────────────────────────

class TestNoLeakage:
    """No control ID appears in more than one partition."""

    def test_no_train_test_overlap(self, synthetic_control_ids):
        result = compute_data_split(synthetic_control_ids, seed=42)
        overlap = set(result["train_ids"]) & set(result["test_ids"])
        assert len(overlap) == 0, f"Leakage: {len(overlap)} IDs in both train and test"

    def test_no_train_val_overlap(self, synthetic_control_ids):
        result = compute_data_split(synthetic_control_ids, seed=42)
        overlap = set(result["train_ids"]) & set(result["val_ids"])
        assert len(overlap) == 0, f"Leakage: {len(overlap)} IDs in both train and val"

    def test_no_val_test_overlap(self, synthetic_control_ids):
        result = compute_data_split(synthetic_control_ids, seed=42)
        overlap = set(result["val_ids"]) & set(result["test_ids"])
        assert len(overlap) == 0, f"Leakage: {len(overlap)} IDs in both val and test"

    def test_all_ids_accounted_for(self, synthetic_control_ids):
        result = compute_data_split(synthetic_control_ids, seed=42)
        all_assigned = set(result["train_ids"]) | set(result["val_ids"]) | set(result["test_ids"])
        assert all_assigned == set(synthetic_control_ids)


# ── Split ratio tests ─────────────────────────────────────────────────────────

class TestSplitRatios:
    """Split ratios approximately match 70/15/15."""

    def test_train_ratio_approximately_70pct(self, synthetic_control_ids):
        result = compute_data_split(synthetic_control_ids, seed=42)
        assert 0.68 <= result["split_ratios"]["train"] <= 0.72

    def test_val_ratio_approximately_15pct(self, synthetic_control_ids):
        result = compute_data_split(synthetic_control_ids, seed=42)
        assert 0.13 <= result["split_ratios"]["val"] <= 0.17

    def test_test_ratio_approximately_15pct(self, synthetic_control_ids):
        result = compute_data_split(synthetic_control_ids, seed=42)
        assert 0.13 <= result["split_ratios"]["test"] <= 0.17

    def test_sizes_sum_to_total(self, synthetic_control_ids):
        result = compute_data_split(synthetic_control_ids, seed=42)
        total = len(result["train_ids"]) + len(result["val_ids"]) + len(result["test_ids"])
        assert total == len(synthetic_control_ids)


# ── Seed derivation tests ─────────────────────────────────────────────────────

class TestSeedDerivation:
    """derive_seed() is deterministic and produces valid integers."""

    def test_derive_seed_deterministic(self, manifest_file):
        hash_a, seed_a = derive_seed(manifest_file)
        hash_b, seed_b = derive_seed(manifest_file)
        assert hash_a == hash_b
        assert seed_a == seed_b

    def test_derive_seed_is_integer(self, manifest_file):
        _, seed = derive_seed(manifest_file)
        assert isinstance(seed, int)
        assert seed >= 0

    def test_different_manifest_different_seed(self, tmp_path):
        manifest_a = tmp_path / "manifest_a.json"
        manifest_b = tmp_path / "manifest_b.json"
        manifest_a.write_text('{"version": "1.0.0"}')
        manifest_b.write_text('{"version": "2.0.0"}')

        _, seed_a = derive_seed(manifest_a)
        _, seed_b = derive_seed(manifest_b)

        assert seed_a != seed_b


# ── Input validation ──────────────────────────────────────────────────────────

class TestInputValidation:
    """compute_data_split() raises on invalid inputs."""

    def test_raises_if_both_manifest_and_seed(self, small_control_ids, manifest_file):
        with pytest.raises(ValueError, match="not both"):
            compute_data_split(small_control_ids, manifest_path=manifest_file, seed=42)

    def test_raises_if_neither_manifest_nor_seed(self, small_control_ids):
        with pytest.raises(ValueError, match="either"):
            compute_data_split(small_control_ids)
