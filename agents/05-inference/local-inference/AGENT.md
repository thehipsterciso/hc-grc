---
name: local-inference
description: Runs quantized domain-specific language models locally for SCF-specific classification, relationship type prediction, and semantic analysis tasks where general-purpose API models are insufficient or where data-sovereignty requirements prohibit external API calls. Primary local inference layer for all agents requiring LLM capabilities that must remain on-device.
version: 1.0.0
team: 05-inference
status: primary
trigger: always
author: HC-GRC
tags: [Local Inference, llama.cpp, SGLang, Quantization, Data Sovereignty, Domain Models]
skills: [llama-cpp, sglang]
tools: [mcp-mlflow, mcp-lab-notebook]
---

# Local Inference Agent

## Purpose

Not every LLM call should go to the Anthropic API. Data sovereignty requires that SCF content never leaves the machine. Some tasks — high-volume relationship type classification across 280,000 mappings, domain-specific semantic judgments where general models underperform — are better served by a local quantized model fine-tuned or prompted for the security domain. The Local Inference Agent manages that local model infrastructure: which model is loaded, at what quantization level, with what context window, and with what throughput characteristics. It is the on-device LLM runtime that all other agents can call when they need inference without external data transmission.

## Position in Workflow

Available as a service from project initialization. Called by any agent that needs local LLM inference — primarily P1 (relationship classification), P3 (convergence classification), and the Guardrails Agent (on-device safety checks).

```
Any agent requiring local LLM inference
        ↓
[Local Inference Agent]
  ├── Model selection (llama.cpp quantized GGUF)
  ├── Context management
  └── SGLang structured output serving
        ↓
Typed inference result → calling agent
```

## Inputs

| Input | Source | Format | Schema / Notes |
|-------|--------|--------|----------------|
| Inference request | Any calling agent | Pydantic InferenceRequest | Prompt, expected output schema, max tokens, temperature |
| Model config | configs/infrastructure.yaml | YAML | Model path, quantization level (Q4_K_M default), context window |
| GGUF model file | Local model store | .gguf | Quantized model; DVC-tracked if custom fine-tuned |

## Outputs / Artifacts

| Artifact | Destination | Format | Schema / Notes |
|----------|-------------|--------|----------------|
| Inference result | Calling agent | Pydantic InferenceResult | Typed output matching calling agent's expected schema |
| Inference log | MLflow | JSON | Model name, quantization, prompt hash, latency, token count |

## Tools & MCP Servers

| Tool | Purpose | MCP Server | Notes |
|------|---------|-----------|-------|
| MLflow | Log inference runs for performance monitoring | mcp-mlflow | Latency and throughput tracked for Agent Evolution |
| Lab notebook | Record model version changes | mcp-lab-notebook | Append-only |

## Skills Used

- **llama.cpp** — CPU-first inference runtime for quantized GGUF models. Handles model loading, context window management, and batch inference. Q4_K_M quantization as default balance of quality and speed on Apple Silicon.
- **SGLang** — Structured generation language for constrained outputs. Used when calling agents need inference results in a specific JSON schema — SGLang's grammar-constrained decoding ensures output validity without post-hoc parsing.

## Handoffs

**Receives from**: P1 Agent, P3 Agent, Guardrails Agent, any agent requiring on-device inference
**Passes to**: Calling agent (typed inference result)
**Human gate**: Model version changes (new model loaded, quantization level changed) require lab notebook entry; major changes (new model family) require human notification

## Behavioral Constraints

- All inference is local — no model calls to external APIs.
- SCF text content is never sent to any external endpoint under any circumstances.
- Model files are stored locally and DVC-tracked if custom fine-tuned.
- Inference results are typed — no unstructured text responses to calling agents.

## Failure Modes & Recovery

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Model OOM | llama.cpp memory error | Reduce context window; use lower quantization (Q3_K_M); log |
| Throughput insufficient for P1 volume | > 500ms per inference at 280K scale | Escalate to Extended Serving Agent (vLLM/TensorRT-LLM) — conditional trigger |
| Model output fails schema validation | Pydantic ValidationError | Retry with explicit schema prompt; max 3 retries; return error to caller |

## Evaluation Criteria

- [ ] All inference requests logged with model version and latency
- [ ] Zero external API calls for SCF content
- [ ] Throughput adequate for batch processing requirements (benchmarked at project start)
- [ ] Model version changes documented in lab notebook

## Notes

The local inference agent is the sovereignty enforcement point for LLM inference. Its existence means that even if the Anthropic API becomes unavailable or a data classification policy changes, the platform continues to function. The throughput threshold that triggers Team 05's Extended Serving Agent is defined in configs/infrastructure.yaml and reviewed by the Agent Evolution agent quarterly.
