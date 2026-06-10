---
name: post-training-agent
description: Applies reinforcement learning and preference optimization to align fine-tuned models with HC-GRC's scientific rigor requirements and SCF domain quality standards. Triggered when supervised fine-tuning alone is insufficient to achieve desired output quality on structured research tasks.
version: 1.0.0
team: 06-training
status: conditional
trigger: Fine-tuned model passes F1 threshold but fails on structured output quality or scientific rigor alignment over 20+ evaluated runs
author: HC-GRC
tags: [Post-training, RLHF, GRPO, TRL, DPO, SimPO, Alignment, Research Quality]
skills: [trl-fine-tuning, grpo-rl-training, simpo]
tools: [mcp-mlflow, mcp-dvc, mcp-lab-notebook]
---

# Post-training Agent

## Purpose

Supervised fine-tuning adapts a model to domain vocabulary and task format. It does not necessarily align the model with nuanced quality requirements — scientific precision, resistance to hallucination under uncertainty, appropriate hedging when evidence is weak. Post-training uses preference data and reinforcement learning to shape those behavioral properties in fine-tuned models that are domain-capable but still producing outputs that fail on rigor dimensions.

## Trigger Conditions

| Trigger | Threshold | Activated By |
|---------|-----------|-------------|
| Structured output quality below threshold | QA score < 3.5/5 on rigor rubric despite passing F1 | Agent Evolution → Orchestrator |
| Hallucination rate unacceptable | > 5% fabricated control citations in 50-sample eval | QA Agent → Orchestrator |
| Preference alignment needed | Model produces correct but inappropriately confident outputs | Agent Evolution assessment |

## Skills Used
- **TRL** — HuggingFace's Transformer Reinforcement Learning library. Provides DPO (Direct Preference Optimization) and PPO trainers.
- **GRPO RL Training** — Group Relative Policy Optimization for research quality reward modeling.
- **SimPO** — Simple Preference Optimization — reference-model-free alternative when TRL DPO is computationally prohibitive.

## Outputs / Artifacts
| Artifact | Destination | Format | Schema / Notes |
|----------|-------------|--------|----------------|
| Aligned model | models/aligned/ (DVC) | LoRA adapter on fine-tuned base | Versioned |
| Preference dataset | data/03-processed/preference_data/ (DVC) | JSON | Human-labeled or LLM-judged preference pairs — SCF-domain quality judgments |
| RLHF training log | MLflow | JSON | Reward curve, KL divergence, eval metrics |

## Handoffs
**Receives from**: Fine-tuning Agent (supervised base), QA Agent (preference signal from quality evaluations)
**Passes to**: Local Inference Agent (aligned model)
**Human gate**: Preference data curation requires human review — preference labels for scientific rigor cannot be fully automated.

## Evaluation Criteria
- [ ] QA score ≥ 3.5/5 on rigor rubric after alignment
- [ ] Hallucination rate < 2% on held-out eval set
- [ ] KL divergence from fine-tuned base within acceptable range (no mode collapse)
- [ ] Preference dataset versioned in DVC
