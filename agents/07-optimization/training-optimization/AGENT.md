---
name: training-optimization
description: Applies hardware-level training efficiency techniques — Flash Attention, gradient checkpointing, mixed precision — to reduce fine-tuning and post-training wall-clock time and memory consumption. Conditional on training job duration or OOM errors during training runs.
version: 1.0.0
team: 07-optimization
status: conditional
trigger: Training OOM on available hardware, or training job projected > 4 hours on target device
author: HC-GRC
tags: [Flash Attention, Mixed Precision, Gradient Checkpointing, Training Efficiency, Optimization]
skills: [flash-attention, bitsandbytes]
tools: [mcp-mlflow, mcp-dvc]
---

# Training Optimization Agent

## Purpose

Fine-tuning and post-training runs on local hardware face real memory and time constraints. This agent applies the appropriate combination of efficiency techniques — Flash Attention 2, bf16/fp16 mixed precision, gradient checkpointing — to make training feasible without requiring distributed infrastructure. It does not change training objectives or hyperparameters; it changes how the same computation is executed.

## Trigger Conditions

| Trigger | Threshold | Activated By |
|---------|-----------|-------------|
| CUDA OOM during training | Any OOM error on training forward/backward pass | Fine-tuning Agent or Post-training Agent |
| Training duration excessive | Estimated wall-clock > 4h on local device | Orchestrator |
| Batch size constraint | Effective batch size too small for stable gradient estimates | Fine-tuning Agent |

## Optimization Stack (applied in order)

1. **Flash Attention 2** — Replaces standard attention with memory-efficient fused kernel. Applied first, largest impact.
2. **Mixed precision (bf16)** — Half-precision compute with fp32 master weights. Requires Ampere+ GPU.
3. **Gradient checkpointing** — Recomputes activations on backward pass instead of storing. Reduces memory at ~30% compute cost.
4. **Gradient accumulation** — Simulates larger batches without proportional memory increase.

## Skills Used
- **Flash Attention** — Memory-efficient attention kernels. Primary optimization for transformer training.
- **bitsandbytes** — 8-bit Adam optimizer. Reduces optimizer state memory by 50%.

## Outputs / Artifacts

| Artifact | Destination | Format | Notes |
|----------|-------------|--------|-------|
| Optimized training config | configs/training/ (DVC) | YAML | Applied techniques documented |
| Training efficiency report | MLflow | JSON | Throughput (tokens/sec), peak memory, wall-clock time |

## Handoffs
**Receives from**: Fine-tuning Agent, Post-training Agent (OOM or timeout signal)
**Passes to**: Fine-tuning Agent, Post-training Agent (updated training config)
**Escalation**: If OOM persists after all optimizations, escalates to Distributed Training Agent.

## Evaluation Criteria
- [ ] Training completes without OOM on target hardware
- [ ] Throughput improvement ≥ 20% over unoptimized baseline
- [ ] Training loss curve equivalent to unoptimized run (no degradation from efficiency techniques)
- [ ] Optimization config versioned alongside model artifacts
