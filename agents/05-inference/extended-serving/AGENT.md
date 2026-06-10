---
name: extended-serving
description: High-throughput LLM inference serving using TensorRT-LLM or vLLM when llama.cpp throughput is insufficient for batch processing requirements. Activated when Local Inference Agent latency exceeds defined thresholds at production batch volumes.
version: 1.0.0
team: 05-inference
status: conditional
trigger: Local Inference Agent throughput < required batch processing rate (configurable in configs/infrastructure.yaml)
author: HC-GRC
tags: [Inference Serving, TensorRT-LLM, vLLM, High Throughput, Batch Processing]
skills: [tensorrt-llm, vllm]
tools: [mcp-mlflow, mcp-lab-notebook]
---

# Extended Serving Agent

## Purpose

When P1's 280,000-mapping batch classification or P5's cross-domain clustering requires inference at a rate that llama.cpp cannot sustain in reasonable time, this agent takes over inference serving. It provides continuous batching, PagedAttention, and GPU-optimized execution that can sustain 10–100× the throughput of CPU-bound llama.cpp inference.

## Position in Workflow

Activated as a drop-in replacement for Local Inference Agent when throughput threshold is breached. Calling agents do not change their interface — same Pydantic InferenceRequest/InferenceResult schema.

## Inputs

| Input | Source | Format | Schema / Notes |
|-------|--------|--------|----------------|
| Inference requests | Any calling agent | Pydantic InferenceRequest | Same schema as Local Inference Agent |
| Model config | configs/infrastructure.yaml | YAML | Serving engine selection (TensorRT-LLM vs vLLM), GPU config |

## Outputs / Artifacts

| Artifact | Destination | Format | Schema / Notes |
|----------|-------------|--------|----------------|
| Inference results | Calling agent | Pydantic InferenceResult | Same schema as Local Inference Agent |
| Throughput metrics | MLflow | JSON | Tokens/sec, latency percentiles, GPU utilization |

## Skills Used
- **TensorRT-LLM** — NVIDIA-optimized inference. Used when GPU available and maximum throughput required.
- **vLLM** — PagedAttention-based continuous batching. Used when TensorRT-LLM compilation time is prohibitive or model not supported.

## Handoffs
**Receives from**: Orchestrator (activation trigger), any agent previously using Local Inference Agent
**Passes to**: Calling agents (inference results)
**Human gate**: Activation requires human notification — infrastructure change logged in lab notebook

## Behavioral Constraints
- Same data sovereignty constraints as Local Inference Agent — all inference local.
- Model files must be locally available before activation.

## Trigger Conditions

| Trigger | Threshold | Activated By |
|---------|-----------|-------------|
| llama.cpp throughput insufficient | < N inferences/sec at batch volume (N in configs/infrastructure.yaml) | Agent Evolution or Orchestrator |
| P1 batch ETA > 24 hours on CPU | Runtime estimate from Local Inference Agent | Automatic escalation |

## Evaluation Criteria
- [ ] Throughput improvement > 5× over llama.cpp baseline documented
- [ ] Same output quality as Local Inference Agent (schema compliance, accuracy)
- [ ] Activation event logged in lab notebook
