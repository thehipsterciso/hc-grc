---
name: fine-tuning-agent
description: Fine-tunes domain-specific language models on SCF corpus using parameter-efficient methods (LoRA/QLoRA) when general-purpose models fail to meet performance thresholds. Primary trigger is Embedding Agent F1 < 0.70 on STRM relationship classification. Produces versioned fine-tuned model artifacts that the Local Inference Agent loads.
version: 1.0.0
team: 06-training
status: conditional
trigger: Embedding Agent semantic model F1 < 0.70 on STRM classification task OR QA Agent score < 3.5/5 on inference quality over 20+ runs
author: HC-GRC
tags: [Fine-tuning, PEFT, LoRA, QLoRA, Axolotl, Domain Adaptation, SCF Corpus]
skills: [peft, axolotl, llama-factory, unsloth]
tools: [mcp-mlflow, mcp-dvc, mcp-lab-notebook]
---

# Fine-tuning Agent

## Purpose

General-purpose sentence-transformer models were not trained on security control text. When cosine similarity between semantically related controls falls below the F1 threshold required for reliable STRM classification, the problem is domain mismatch — not a fundamental limitation of the approach. The Fine-tuning Agent resolves that mismatch by adapting the model to the SCF vocabulary and semantic structure using parameter-efficient fine-tuning, producing a domain-specialized model that the Local Inference Agent deploys for all subsequent inference.

## Trigger Conditions

| Trigger | Threshold | Activated By |
|---------|-----------|-------------|
| Embedding model F1 below threshold | < 0.70 on STRM classification | P1 Agent evaluation → Embedding Agent → Orchestrator |
| QA inference quality below threshold | < 3.5/5 over ≥ 20 runs | Agent Evolution → Orchestrator |
| Domain vocabulary OOV rate high | > 10% OOV on SCF corpus | Tokenization Agent → Orchestrator |

## Inputs

| Input | Source | Format | Schema / Notes |
|-------|--------|--------|----------------|
| Training data | data/splits/train/ | Parquet | SCF control text + STRM labels (train split only) |
| Base model | Local model store | HuggingFace model | DVC-tracked; sovereignty constraint — no HuggingFace Hub download during runs |
| Fine-tuning config | configs/fine_tuning.yaml | YAML | LoRA rank, alpha, target modules, epochs, batch size, learning rate |

## Outputs / Artifacts

| Artifact | Destination | Format | Schema / Notes |
|----------|-------------|--------|----------------|
| Fine-tuned model | models/fine_tuned/ (DVC) | LoRA adapter + base model config | Versioned; loaded by Local Inference Agent |
| Training metrics | MLflow | JSON | Loss curve, eval metrics per checkpoint |
| Fine-tuning report | Lab notebook | Markdown | Trigger reason, base model, config, eval metrics, improvement over baseline |

## Skills Used
- **PEFT** — LoRA and QLoRA adapters. Preferred for memory-efficient fine-tuning on Apple Silicon or single consumer GPU.
- **Axolotl** — Fine-tuning framework with YAML-driven configuration. Used for full fine-tuning pipeline orchestration.
- **LLaMA-Factory** — Alternative fine-tuning framework with web UI for hyperparameter exploration. Used during initial adapter development.
- **Unsloth** — 2× faster LoRA fine-tuning via optimized kernels. Activated when training speed is a bottleneck.

## Handoffs
**Receives from**: Orchestrator (trigger), data/splits/train/ (training data), models/ (base model)
**Passes to**: Local Inference Agent (fine-tuned model), Embedding Agent (re-embedding trigger if model changes)
**Human gate**: Human notified before fine-tuning begins (training data use, model selection). Human reviews eval metrics before fine-tuned model is promoted to production.

## Behavioral Constraints
- Fine-tuning uses train split only — never val or test.
- Base model must be locally available — no downloads during fine-tuning runs.
- Every fine-tuning run versioned in DVC — no model overwrites.
- SCF text used as training data cannot be extracted or published — CC BY-ND constraint.

## Evaluation Criteria
- [ ] Fine-tuned model achieves F1 ≥ 0.70 on STRM classification (val split)
- [ ] Training run fully logged in MLflow
- [ ] Model versioned in DVC before deployment to Local Inference Agent
- [ ] Improvement over baseline documented in lab notebook
