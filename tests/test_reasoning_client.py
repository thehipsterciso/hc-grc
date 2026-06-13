"""
Unit tests for the reasoning_client seam (ADR-0016).

Covers the deterministic, offline-safe paths: routing guards, the kill-switch,
JSON recovery, cheap liveness, metered-API scrubbing, and the retry loop. Live
backend calls are covered by the integration smoke paths, not here.
"""

from __future__ import annotations

import pytest

import src.reasoning_client as rc
from src.reasoning_client import (
    ReasoningError,
    Tier,
    _extract_json,
    _first_balanced_json,
    _scrubbed_env,
    complete,
    is_available,
)


def test_t1_is_a_routing_bug(monkeypatch):
    monkeypatch.delenv("HCGRC_DISABLE_REASONING", raising=False)
    with pytest.raises(ReasoningError, match="deterministic ML"):
        complete(Tier.T1, "anything")


def test_kill_switch_fails_fast(monkeypatch):
    monkeypatch.setenv("HCGRC_DISABLE_REASONING", "1")
    with pytest.raises(ReasoningError, match="disabled"):
        complete(Tier.T2, "anything")


@pytest.mark.parametrize("raw,expected", [
    ('{"a": 1}', {"a": 1}),
    ('```json\n{"a": 1}\n```', {"a": 1}),
    ('```\n[1, 2, 3]\n```', [1, 2, 3]),
    ('prefix {"relation": "subset"} trailing prose {junk', {"relation": "subset"}),
    ('[{"x": 1}] and commentary', [{"x": 1}]),
    ('{"nested": {"s": "a } brace in a string"}}', {"nested": {"s": "a } brace in a string"}}),
])
def test_extract_json_recovers(raw, expected):
    assert _extract_json(raw) == expected


def test_extract_json_raises_when_absent():
    with pytest.raises(ReasoningError):
        _extract_json("there is no json here at all")


def test_first_balanced_json_respects_strings():
    # The closing brace inside the string must not terminate the object.
    assert _first_balanced_json('{"a": "}"} tail') == '{"a": "}"}'
    assert _first_balanced_json("plain text") is None


def test_is_available_t1_always_true():
    assert is_available(Tier.T1) is True


def test_is_available_disabled(monkeypatch):
    monkeypatch.setenv("HCGRC_DISABLE_REASONING", "1")
    assert is_available(Tier.T2) is False
    assert is_available(Tier.T3) is False


def test_scrubbed_env_removes_metered_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-should-be-removed")
    monkeypatch.setenv("HCGRC_KEEP", "1")
    env = _scrubbed_env()
    assert "ANTHROPIC_API_KEY" not in env
    assert env.get("HCGRC_KEEP") == "1"


def test_retry_then_success(monkeypatch):
    monkeypatch.delenv("HCGRC_DISABLE_REASONING", raising=False)
    monkeypatch.setattr(rc.time, "sleep", lambda *_: None)
    calls = {"n": 0}

    def flaky(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] < 2:
            raise ReasoningError("transient")
        return "ok"

    monkeypatch.setattr(rc, "_attempt", flaky)
    assert complete(Tier.T2, "x") == "ok"
    assert calls["n"] == 2


def test_retry_exhausted_raises(monkeypatch):
    monkeypatch.delenv("HCGRC_DISABLE_REASONING", raising=False)
    monkeypatch.setattr(rc.time, "sleep", lambda *_: None)
    calls = {"n": 0}

    def always_fail(*args, **kwargs):
        calls["n"] += 1
        raise ReasoningError("down")

    monkeypatch.setattr(rc, "_attempt", always_fail)
    with pytest.raises(ReasoningError, match="down"):
        complete(Tier.T2, "x")
    assert calls["n"] == rc.MAX_RETRIES + 1
