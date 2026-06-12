"""
Phoenix observability bootstrap for HC-GRC (roadmap Phase 0, deliverable #2).

ADR-0009: Phoenix is the local, self-hosted LLM-tracing stack (LangSmith was
disqualified as SaaS-only). The Phoenix server runs on the compute node and
agent LLM calls export OpenTelemetry traces to it.

Two responsibilities, deliberately separated:

  1. The SERVER is a long-lived process — run it via the `phoenix serve` CLI
     (see launch_server_command()) or the launchd plist in scripts/. It is NOT
     launched from inside the application process, because returning from a
     setup function would tear an embedded server down. Use px.launch_app()
     only for throwaway interactive sessions.

  2. INSTRUMENTATION is wired per-process: instrument_langchain() registers an
     OTel tracer provider pointed at the running server and turns on the
     LangChain instrumentor so every agent LLM/chain call is traced.

run_id propagation (ADR-0015 #79): set run_id as a span attribute on the root
span of each run so traces cross-reference MLflow/PostgresSaver/PROV-DM. With
LangChain, pass it via run metadata, e.g.:
    config={"metadata": {"run_id": state["run_id"]}}
"""

from __future__ import annotations

from ..config import load_platform_config


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
    Register an OTel tracer provider pointed at the running Phoenix server and
    enable LangChain tracing for this process.

    Idempotent within a process. Requires the Phoenix server to be reachable at
    phoenix_endpoint(); traces are buffered/dropped if it is not.

    Returns the tracer provider.
    """
    from openinference.instrumentation.langchain import LangChainInstrumentor
    from phoenix.otel import register

    cfg = _phoenix_cfg()
    tracer_provider = register(
        project_name=project_name or cfg.get("project_name", "hc-grc"),
        endpoint=phoenix_endpoint(),
    )
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider, skip_dep_check=True)
    return tracer_provider


if __name__ == "__main__":  # pragma: no cover - operational entrypoint
    print(f"Phoenix base URL:    {phoenix_base_url()}")
    print(f"OTLP traces endpoint: {phoenix_endpoint()}")
    print(f"Start the server with: {launch_server_command()}")
