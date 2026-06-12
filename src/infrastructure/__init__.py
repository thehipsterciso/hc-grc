"""
Platform infrastructure for the HC-GRC compute node.

These modules provision and configure the local, data-sovereign infrastructure
services the platform depends on (ADR-0002, ADR-0009, ADR-0014). Everything runs
on-device; no SaaS dependencies.

  tracking/        MLflow experiment tracking (local file store — no daemon)
  observability/   Phoenix LLM tracing + OpenTelemetry instrumentation

Connection parameters are read from configs/platform.yaml via load_platform_config().
"""
