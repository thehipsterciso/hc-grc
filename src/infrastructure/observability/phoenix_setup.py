"""
Phoenix observability bootstrap for HC-GRC (roadmap Phase 0, deliverable #2).

ADR-0009: Phoenix is the local, self-hosted LLM-tracing stack (LangSmith was
disqualified as SaaS-only). The Phoenix server runs on the compute node and
agent LLM calls export OpenTelemetry traces to it.

Two responsibilities, deliberately separated:

  1. The SERVER is a long-lived process — run it via the `phoenix serve` CLI
     (see launch_server_command()) or the launchd plist in scripts/. It is NOT
     launched from inside the application process.

  2. INSTRUMENTATION is wired per-process via bootstrap_observability(), called
     once by each run entrypoint. It registers a global OTel tracer provider
     (BatchSpanProcessor — spans are buffered and exported in the background, so
     a momentary server outage drops spans rather than blocking or failing the
     run) pointed at the running server, and turns on the LangChain instrumentor.
     Because the provider is registered globally, the spans the reasoning_client
     emits for BOTH tiers — including Tier-3 (claude-agent-sdk), which LangChain
     instrumentation does not see — export to Phoenix too.

run_id propagation (ADR-0015 #79): wrap a run in run_trace_context(run_id) so
every span produced during the run carries the run_id as session.id + metadata,
cross-referencing MLflow / PostgresSaver / PROV-DM.
"""

from __future__ import annotations

import os
from contextlib import contextmanager

from ..config import load_platform_config

# Cached registered provider — registration is idempotent within a process
# (repeat bootstrap calls return the same provider instead of double-registering
# the instrumentor, which would duplicate every span).
_PROVIDER = None


def _phoenix_cfg() -> dict:
    return load_platform_config()["observability"]["phoenix"]


def phoenix_base_url() -> str:
    """Return the Phoenix server base URL, e.g. http://localhost:6006."""
    cfg = _phoenix_cfg()
    return f"http://{cfg.get('host', 'localhost')}:{cfg.get('port', 6006)}"


def phoenix_endpoint() -> str:
    """Return the OTLP/HTTP traces endpoint the tracer provider exports to."""
    return f"{phoenix_base_url()}/v1/traces"


def launch_server_command() -> str:
    """Return the shell command that starts the persistent Phoenix server."""
    cfg = _phoenix_cfg()
    return f"phoenix serve --host {cfg.get('host', 'localhost')} --port {cfg.get('port', 6006)}"


def instrument_langchain(project_name: str | None = None):
    """
    Register a global OTel tracer provider pointed at the Phoenix server (using a
    background BatchSpanProcessor) and enable LangChain tracing for this process.

    Idempotent: the first call registers; subsequent calls return the cached
    provider without re-instrumenting (so spans are never duplicated).

    Returns the tracer provider.
    """
    global _PROVIDER
    if _PROVIDER is not None:
        return _PROVIDER

    from openinference.instrumentation.langchain import LangChainInstrumentor
    from phoenix.otel import register

    cfg = _phoenix_cfg()
    provider = register(
        project_name=project_name or cfg.get("project_name", "hc-grc"),
        endpoint=phoenix_endpoint(),
        batch=True,                        # BatchSpanProcessor: buffer + async export
        set_global_tracer_provider=True,   # so reasoning_client spans export too
    )
    LangChainInstrumentor().instrument(tracer_provider=provider, skip_dep_check=True)
    _PROVIDER = provider
    return provider


def bootstrap_observability(run_id: str | None = None):
    """
    Idempotently wire tracing for the current process. Called once by each run
    entrypoint (graph runners). Degrades to a no-op — never raising — when tracing
    is disabled by config, switched off via HCGRC_DISABLE_TRACING, or the
    instrumentation stack cannot be initialized. Returns the provider or None.
    """
    if os.environ.get("HCGRC_DISABLE_TRACING", "").strip():
        return None
    try:
        cfg = _phoenix_cfg()
    except Exception:
        return None
    if not cfg.get("enabled", True):
        return None
    try:
        return instrument_langchain()
    except Exception:
        # Missing deps, server unreachable at registration, etc. — tracing is
        # best-effort observability and must never block the research run.
        return None


@contextmanager
def run_trace_context(run_id: str | None):
    """
    Context manager that stamps run_id onto every span produced within it
    (session.id + metadata.run_id), for cross-store correlation. No-op if the
    OpenInference context helper is unavailable or run_id is None.
    """
    if not run_id:
        yield
        return
    try:
        from openinference.instrumentation import using_attributes
    except Exception:
        yield
        return
    with using_attributes(session_id=run_id, metadata={"run_id": run_id}):
        yield


if __name__ == "__main__":  # pragma: no cover - operational entrypoint
    print(f"Phoenix base URL:    {phoenix_base_url()}")
    print(f"OTLP traces endpoint: {phoenix_endpoint()}")
    print(f"Start the server with: {launch_server_command()}")
