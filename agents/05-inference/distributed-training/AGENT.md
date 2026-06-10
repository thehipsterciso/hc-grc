---
name: distributed-training
description: Manages distributed training infrastructure when fine-tuning or post-training runs exceed single-device capacity. Coordinates multi-GPU or multi-node training via Accelerate, PyTorch Lightning, or Ray Train depending on hardware configuration.
version: 1.0.0
team: 05-inference
status: conditional
trigger: Fine-tuning or post-training job requires > single GPU or single machine
author: HC-GRC
tags: [Distributed Training, Accelerate, PyTorch Lightning, Ray Train, Multi-GPU]
skills: [accelerate, pytorch-lightning, ray-train]
tools: [mcp-mlflow, mcp-lab-notebook]
---

# Distributed Training Agent

## Purpose

Most fine-tuning runs in HC-GRC are single-GPU LoRA jobs that the Fine-tuning Agent handles directly. When a job exceeds single-device capacity — larger base model, full fine-tune, or multi-node requirement — this agent orchestrates the distributed setup so the Fine-tuning and Post-training agents can focus on the training logic rather than distributed infrastructure.

## Trigger Conditions

| Trigger | Threshold | Activated By |
|---------|-----------|-------------|
| Fine-tuning job requires > 1 GPU | VRAM requirement estimate exceeds device capacity | Fine-tuning Agent |
| Post-training job requires multi-node | RL training scale exceeds single machine | Post-training Agent |

## Skills Used
- **Accelerate** — HuggingFace's distributed training abstraction. Preferred for LoRA/PEFT fine-tuning jobs across multiple GPUs.
- **PyTorch Lightning** — Trainer abstraction for larger distributed jobs. Used when more granular control over training loop is needed.
- **Ray Train** — Ray-native distributed training. Used when Ray Data pipeline feeds directly into training for seamless data-to-training parallelism.

## Evaluation Criteria
- [ ] Training job completes without OOM on distributed setup
- [ ] Distributed training reproduces single-device baseline results (within 1% metric variance)
- [ ] All runs logged in MLflow with distributed config parameters
