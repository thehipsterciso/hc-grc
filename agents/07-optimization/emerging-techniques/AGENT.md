---
name: emerging-techniques
description: Applies advanced model optimization techniques — speculative decoding, knowledge distillation, model pruning, model merging, long-context extension — when standard quantization and training optimization are insufficient for target performance or capability requirements.
version: 1.0.0
team: 07-optimization
status: conditional
trigger: Explicit capability gap identified that standard quantization/fine-tuning cannot address; or research requires SCF context lengths exceeding base model limits
author: HC-GRC
tags: [Speculative Decoding, Knowledge Distillation, Model Pruning, Model Merging, Long Context]
skills: [speculative-decoding, knowledge-distillation, model-pruning, model-merging, long-context]
tools: [mcp-mlflow, mcp-dvc, mcp-lab-notebook]
---

# Emerging Techniques Agent

## Purpose

Some capability requirements cannot be met by standard quantization or fine-tuning alone. SCF analysis may require processing full 33-domain control sets in a single context window (long-context extension). Inference throughput requirements may necessitate speculative decoding. A smaller, faster distilled model may be preferable to the full fine-tuned model for specific pipeline stages. This agent handles those cases.

## Trigger Conditions

| Trigger | Technique | Notes |
|---------|-----------|-------|
| Context length exceeds base model maximum | Long-context extension (RoPE scaling, YaRN) | SCF full-domain analysis may require 32K+ tokens |
| Inference latency bottleneck despite quantization | Speculative decoding | Requires draft model of same family |
| Model too large for target deployment after quantization | Knowledge distillation or pruning | Produces smaller student model |
| Domain-specific capabilities need combining | Model merging (TIES, DARE) | Merges specialized adapters |

## Skills Used
- **Speculative Decoding** — Draft + verify pattern for 2–4× throughput improvement with identical outputs.
- **Knowledge Distillation** — Train smaller student model on teacher outputs. Reduces model size while retaining capability.
- **Model Pruning** — Remove low-magnitude weights. Structured pruning preserves hardware efficiency.
- **Model Merging** — Combine fine-tuned adapters via TIES or DARE without additional training.
- **Long Context** — RoPE scaling or YaRN to extend effective context window beyond pretraining maximum.

## Outputs / Artifacts

| Artifact | Destination | Format | Notes |
|----------|-------------|--------|-------|
| Optimized model variant | models/optimized/ (DVC) | safetensors / GGUF | Technique documented in metadata |
| Capability eval report | MLflow | JSON | Task performance vs. baseline, latency comparison |

## Handoffs
**Receives from**: Orchestrator (capability gap assessment), Local Inference Agent (throughput bottleneck)
**Passes to**: Local Inference Agent or Extended Serving Agent

## Evaluation Criteria
- [ ] Target capability met (context length, throughput, or size target)
- [ ] Task accuracy retention ≥ 90% vs. pre-technique baseline on SCF eval set
- [ ] Technique selection logged with justification
- [ ] All model variants versioned in DVC

## Notes
Model merging is the only technique here that does not require additional training data. Useful for combining adapters from different fine-tuning runs that target complementary SCF capabilities.
