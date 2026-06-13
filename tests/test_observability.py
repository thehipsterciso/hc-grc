"""
Tests for the Phoenix/OpenTelemetry bootstrap (ADR-0009).

Offline-safe: these never register a real global tracer provider (that would
mutate process-global OTel state for the rest of the suite). They exercise the
guards, the idempotency cache, and the run_id context manager.
"""

from __future__ import annotations

import src.infrastructure.observability.phoenix_setup as ps


def test_bootstrap_noop_when_disabled(monkeypatch):
    monkeypatch.setenv("HCGRC_DISABLE_TRACING", "1")
    assert ps.bootstrap_observability() is None


def test_instrument_is_idempotent(monkeypatch):
    # With a provider already cached, instrument_langchain must return it without
    # re-registering / re-instrumenting (which would duplicate every span).
    monkeypatch.delenv("HCGRC_DISABLE_TRACING", raising=False)
    sentinel = object()
    monkeypatch.setattr(ps, "_PROVIDER", sentinel)
    assert ps.instrument_langchain() is sentinel
    assert ps.bootstrap_observability() is sentinel


def test_run_trace_context_is_a_safe_noop_without_run_id():
    with ps.run_trace_context(None):
        pass


def test_run_trace_context_stamps_run_id():
    # Should not raise whether or not the OpenInference helper is importable.
    with ps.run_trace_context("run-z"):
        pass
