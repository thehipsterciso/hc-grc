# HC-GRC Skills Capability Assessment

**Date**: 2026-06-09
**Assessor**: Claude (Sonnet 4.6)
**Source Library**: AI Research Skills Library (98 skills, 23 categories)
**Target Platform**: HC-GRC — Autonomous Scientific DS/ML Research Platform
**Purpose**: Formal evaluation of each skill's applicability to HC-GRC's five analytical modules and supporting infrastructure

## HC-GRC Context Summary

**Analytical Modules**:
- P1: STRM Calibration — NLP/semantic validation of expert-derived SCF control mappings (exhaustive: every NLP algorithm)
- P2: Control Space Topology — graph analysis, clustering, knowledge graph of control relationships
- P3: Regulatory Convergence Atlas — cross-framework mapping analysis
- P4: Risk Blindspot Engine — risk coverage gap analysis
- P5: AI Governance Cluster Analysis — cross-domain ML clustering, all 33 domains

**Current Stack**: LangGraph 1.0 (10 agents), Claude API / Agent SDK, Qdrant (local-first), DVC, MLflow, Langfuse + OTel, GitHub Actions + pre-commit

**Constraints**: Local-first / data-sovereign (no managed cloud services), SCF text corpus (not multimodal)

---

## [00] Autoresearch

**Path**: `0-autoresearch-skill/autoresearch/`
**What it does**: Provides a two-loop autonomous research orchestration pattern (outer planning loop, inner execution loop) that routes to domain-specific skills. Manages agent continuity, context handoff, and full lifecycle coordination from hypothesis to publication. Acts as the central orchestration layer.

### Features & Capabilities
- Outer loop: hypothesis → experiment design → execution → analysis → write-up
- Inner loop: tool selection → execution → self-critique → retry
- Agent continuity protocol for long-running multi-session research
- Routes to 90+ domain skills based on task type
- Integrated pre-registration and checkpoint discipline
- SAP (Scientific Advancement Protocol) compliance built-in

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: P1/P2/P3/P4/P5/Orchestration
**How it fits**: The autoresearch skill IS the HC-GRC orchestration blueprint. HC-GRC's LangGraph multi-agent system mirrors the two-loop architecture exactly: outer loop = research pipeline (ingest → analyze → validate → report), inner loop = per-module execution with self-critique. The agent continuity protocol maps directly to HC-GRC's SAP enforcement layer.

### Pros
- Provides battle-tested orchestration patterns that HC-GRC's LangGraph design already partially implements
- Agent continuity protocol prevents context loss across long SCF corpus analysis runs
- Built-in pre-registration discipline aligns with HC-GRC's scientific rigor requirements
- Routes to all other skills — functions as index/router for the entire library

### Cons / Risks
- Requires careful adaptation of routing logic to HC-GRC's specific 5-module structure
- Inner loop retry logic needs tuning for SCF domain (not general research)

### Integration Decision
**Use**: YES
**Replaces or augments**: Augments HC-GRC's LangGraph orchestration with proven patterns; does not replace LangGraph itself

---

## [01] LitGPT

**Path**: `01-model-architecture/litgpt/`
**What it does**: Lightning AI's framework for pretraining and fine-tuning LLMs with minimal boilerplate. Supports 20+ model architectures including LLaMA, Mistral, Phi, Gemma. Designed for research-scale training runs.

### Features & Capabilities
- Pretraining from scratch on custom datasets
- Continued pretraining and supervised fine-tuning
- LoRA/QLoRA support via integrations
- Single-file model implementations for hackability
- Supports flash attention and FSDP

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: HC-GRC is not training base language models. The platform uses Claude API as its AI backbone and analyzes an existing corpus (SCF). No pretraining or full fine-tuning of base LLMs is in scope.

### Pros
- N/A

### Cons / Risks
- Overkill: requires GPU infrastructure HC-GRC is not provisioning
- Would introduce pretraining complexity entirely outside HC-GRC's scope

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing in current architecture

---

## [01] Mamba

**Path**: `01-model-architecture/mamba/`
**What it does**: State space model (SSM) architecture for sequence modeling, offering linear-time complexity as an alternative to transformers. Implements selective state space models for efficient long-sequence processing.

### Features & Capabilities
- Linear-time sequence modeling (vs quadratic for transformers)
- Efficient handling of very long sequences (>100K tokens)
- Mamba-1 and Mamba-2 architectures
- Hybrid Mamba-transformer architectures

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: HC-GRC does not train custom architectures. Even for long-context SCF processing, the platform uses Claude API which handles context natively.

### Pros
- N/A

### Cons / Risks
- Training infrastructure HC-GRC doesn't have; Claude API handles long context natively

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing in current architecture

---

## [01] NanoGPT

**Path**: `01-model-architecture/nanogpt/`
**What it does**: Minimal, educational GPT implementation by Andrej Karpathy. ~300 lines for a full GPT-2 training run. Used for understanding transformer internals and rapid prototyping.

### Features & Capabilities
- Minimal GPT-2 implementation for educational purposes
- Fast iteration on transformer architecture experiments
- Single-file training script

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: Educational tool for understanding transformer internals. HC-GRC uses Claude API; not training custom transformers.

### Pros
- N/A

### Cons / Risks
- Educational only; not production-relevant for HC-GRC

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing in current architecture

---

## [01] RWKV

**Path**: `01-model-architecture/rwkv/`
**What it does**: RNN-based language model with transformer-level performance. Combines recurrent networks with attention-like mechanisms for O(1) inference memory. Supports 14B parameter models.

### Features & Capabilities
- Linear-time inference (vs quadratic transformers)
- O(1) memory during inference
- Supports 7B/14B model sizes
- Training and fine-tuning support

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: HC-GRC uses Claude API. Alternative model architectures are not in scope.

### Pros
- N/A

### Cons / Risks
- Out of scope for HC-GRC's architecture

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing in current architecture

---

## [01] TorchTitan

**Path**: `01-model-architecture/torchtitan/`
**What it does**: PyTorch-native large-scale LLM pretraining reference implementation. Supports 3D parallelism (tensor/pipeline/data parallel) for training models at 7B-405B parameter scale.

### Features & Capabilities
- 3D parallelism support for multi-hundred-billion parameter models
- PyTorch-native (no external frameworks)
- Reference implementation for large-scale training

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: HC-GRC is not pretraining LLMs at any scale.

### Pros
- N/A

### Cons / Risks
- Entirely outside HC-GRC scope

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing in current architecture

---

## [02] HuggingFace Tokenizers

**Path**: `02-tokenization/huggingface-tokenizers/`
**What it does**: Rust-backed tokenizer library offering BPE, WordPiece, and Unigram tokenization algorithms. Processes 1GB of text in under 20 seconds. Supports offset tracking, padding, truncation, and custom pre/post-processing.

### Features & Capabilities
- BPE, WordPiece, Unigram, and character/word-level tokenizers
- Rust backend: 1GB text < 20s
- Offset mapping for token-to-character alignment
- Train custom tokenizers on domain corpora
- HuggingFace ecosystem integration
- Special token handling, padding, truncation

### Applicability to HC-GRC
**Verdict**: PARTIAL
**Applicable to modules**: P1
**How it fits**: P1 STRM Calibration requires exhaustive NLP algorithm evaluation on SCF control text. Custom tokenization trained on security/compliance domain vocabulary would improve embedding quality for control mapping validation. Offset mapping is valuable for pinpointing which tokens in a control description contribute to semantic mismatches.

### Pros
- Training a domain-specific BPE tokenizer on SCF corpus could improve downstream embedding quality
- Fast enough for batch processing all 280,000+ mappings
- Offset tracking helps P1 identify exactly which phrases in a control triggered a semantic anomaly

### Cons / Risks
- Custom tokenizer training adds complexity; pretrained models already include reasonable security vocabulary
- Most Sentence Transformer models come with their own tokenizers — custom tokenizers require retraining embeddings

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Augments Sentence Transformers in P1 pipeline
**Condition**: Use if domain-specific tokenization experiments are included in P1's exhaustive NLP algorithm evaluation; skip if using off-the-shelf sentence-transformers models only

---

## [02] SentencePiece

**Path**: `02-tokenization/sentencepiece/`
**What it does**: Google's language-independent subword tokenizer (BPE + Unigram). Used in T5, ALBERT, XLNet, LLaMA. Operates directly on raw text without pre-tokenization, making it suitable for multilingual and specialized domain text.

### Features & Capabilities
- Language-independent tokenization (no pre-tokenization needed)
- BPE and Unigram models
- Used by T5, ALBERT, XLNet, LLaMA families
- Trainable on custom corpora
- Python and C++ APIs

### Applicability to HC-GRC
**Verdict**: PARTIAL
**Applicable to modules**: P1
**How it fits**: Same domain as HuggingFace Tokenizers but used specifically when integrating T5-family models for P1 semantic validation. If HC-GRC evaluates T5-based embeddings (e.g., sentence-t5, flan-t5 for NLI-based mapping validation), SentencePiece handles those model tokenization requirements automatically.

### Pros
- Required when using T5/LLaMA-family models directly
- Language-independent — useful if SCF mappings include non-English regulatory frameworks (P3)

### Cons / Risks
- Redundant if only using transformer-based sentence embeddings through the HuggingFace pipeline
- Most users won't need to interact with SentencePiece directly — it's a dependency, not a tool

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Implicit dependency for P1 NLP model selection
**Condition**: Required automatically if P1 experiments include T5-family or LLaMA-family models for semantic validation

---

## [03] Axolotl

**Path**: `03-fine-tuning/axolotl/`
**What it does**: Configuration-driven fine-tuning framework supporting LoRA, QLoRA, full fine-tuning, FSDP, and DeepSpeed. YAML-based configuration for reproducible training runs.

### Features & Capabilities
- YAML-driven training configuration
- LoRA, QLoRA, full fine-tuning
- Multi-GPU with FSDP/DeepSpeed
- Flash Attention integration
- Dataset preprocessing pipelines

### Applicability to HC-GRC
**Verdict**: PARTIAL
**Applicable to modules**: P1/P5
**How it fits**: If HC-GRC decides to fine-tune a specialized NLP model on SCF domain data (e.g., a security-domain sentence encoder for P1, or a classification head for P5 clustering), Axolotl's YAML-driven approach would make those experiments reproducible and DVC-trackable. Less applicable than PEFT/TRL but more beginner-friendly for configuration.

### Pros
- YAML configuration integrates cleanly with DVC for reproducible experiments
- Lower barrier than raw PEFT/TRL for domain-specific fine-tuning experiments

### Cons / Risks
- Auto-generated skill content (thin documentation) — quality uncertain
- Adds infrastructure dependency for what may be a minor experiment
- Redundant if PEFT is already in use

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Alternative to PEFT for fine-tuning experiments
**Condition**: Use only if fine-tuning experiments are pre-registered in HC-GRC's SAP; prefer PEFT/TRL for more control

---

## [03] LLaMA-Factory

**Path**: `03-fine-tuning/llama-factory/`
**What it does**: WebUI + CLI fine-tuning platform supporting 100+ LLMs with 6 training methods (SFT, DPO, PPO, GRPO, KTO, reward modeling). Includes built-in evaluation and export.

### Features & Capabilities
- WebUI for no-code fine-tuning
- 100+ model support
- 6 training paradigms including GRPO/DPO
- Built-in benchmark evaluation
- LoRA/QLoRA/full fine-tuning

### Applicability to HC-GRC
**Verdict**: PARTIAL
**Applicable to modules**: P1/P5
**How it fits**: Same scope as Axolotl — useful for domain fine-tuning experiments on SCF data. The WebUI makes exploratory fine-tuning accessible without custom training code, which could accelerate P1 NLP algorithm evaluation. However, HC-GRC's scientific enforcement layer requires programmatic, reproducible runs, which the CLI mode supports.

### Pros
- 100+ model support makes P1's exhaustive NLP algorithm evaluation more practical
- CLI mode is scriptable and DVC-compatible

### Cons / Risks
- Auto-generated skill (thin documentation) — rely on upstream docs
- WebUI mode is not reproducible enough for HC-GRC's SAP requirements
- Overlaps with Axolotl/PEFT

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Alternative to Axolotl for fine-tuning experiments
**Condition**: Same as Axolotl — only if domain fine-tuning is in pre-registered experiment plan

---

## [03] PEFT

**Path**: `03-fine-tuning/peft/`
**What it does**: HuggingFace's Parameter-Efficient Fine-Tuning library. Implements 25+ methods including LoRA, QLoRA, DoRA, IA3, Prefix Tuning, Prompt Tuning. Supports multi-adapter composition and hot-swapping.

### Features & Capabilities
- 25+ PEFT methods: LoRA, QLoRA, DoRA, IA3, Prefix Tuning, Prompt Tuning, AdaLoRA
- Multi-adapter serving (hot-swap without model reload)
- bitsandbytes integration for 4-bit/8-bit quantized training
- FSDP compatibility for multi-GPU
- HuggingFace ecosystem native
- Adapter merging and composition

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P5
**How it fits**: The primary fine-tuning tool if HC-GRC creates domain-adapted models. Key use cases: (1) LoRA-fine-tune a sentence encoder on SCF control text for improved P1 semantic similarity, (2) QLoRA-fine-tune a classification model for P5 governance cluster labeling. Multi-adapter hot-swapping could support per-module specialized heads.

### Pros
- Industry-standard PEFT library — well-maintained, well-documented
- QLoRA enables fine-tuning on consumer hardware without large GPU clusters
- Multi-adapter support could power per-module specialized model variants
- Integrates with Axolotl, LLaMA-Factory, and TRL

### Cons / Risks
- Only valuable if fine-tuning experiments are pre-registered in SAP
- Adds model versioning complexity to DVC tracking

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Augments Sentence Transformers with domain-adapted models
**Condition**: Pre-register fine-tuning experiments in SAP before use; use QLoRA variant for local-hardware compatibility

---

## [03] Unsloth

**Path**: `03-fine-tuning/unsloth/`
**What it does**: 2-5x faster fine-tuning with 60% less memory via custom CUDA kernels. Drop-in replacement for HuggingFace training with Llama/Mistral/Gemma family models.

### Features & Capabilities
- 2-5x training speedup via custom CUDA kernels
- 60% memory reduction vs standard LoRA
- Drop-in replacement for HuggingFace Trainer
- Free tier supports models up to 7B

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P5
**How it fits**: If HC-GRC runs local fine-tuning experiments (as per PEFT conditional), Unsloth's memory efficiency makes those experiments viable on local hardware without data-sovereign compromise. The 60% memory reduction is relevant given HC-GRC's local-first constraint.

### Pros
- Makes local fine-tuning on consumer hardware more practical (supports data-sovereign requirement)
- Drop-in for PEFT/HuggingFace Trainer — no code rewrite

### Cons / Risks
- Auto-generated skill (thin documentation)
- Only applies if fine-tuning is pre-registered

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Augments PEFT (speed/memory optimization for local hardware)
**Condition**: Same conditions as PEFT; use if local fine-tuning experiments are approved in SAP

---

## [04] TransformerLens

**Path**: `04-mechanistic-interpretability/transformer-lens/`
**What it does**: De facto standard library for mechanistic interpretability of GPT-style transformers. HookPoints at every activation, activation patching, logit lens, attention visualization. Supports 40+ models.

### Features & Capabilities
- HookPoints for intercepting any intermediate activation
- Activation patching and causal tracing
- Logit lens for tracking information flow
- Attention pattern visualization
- Supports 40+ pretrained models
- Direct integration with SAELens for sparse autoencoders

### Applicability to HC-GRC
**Verdict**: INDIRECT
**Applicable to modules**: P1
**How it fits**: P1's exhaustive NLP algorithm evaluation could include mechanistic analysis of how embedding models process security control text. TransformerLens would let HC-GRC inspect which attention heads activate on control identifiers vs. natural language descriptions, informing which models are best for semantic validation. This is research-quality P1 analysis, not production infrastructure.

### Pros
- Could provide unique insights into why certain NLP models produce anomalous control mappings in P1
- "Exhaustive NLP algorithm evaluation" in P1 could explicitly include mechanistic interpretability as a research method

### Cons / Risks
- Requires models to be loaded locally (not applicable to Claude API)
- Significant research overhead; P1 primary goal is semantic validation, not interpretability research
- Only applicable to open-weight models in HuggingFace format

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Augments P1 NLP research with interpretability analysis
**Condition**: Include only if P1 research plan explicitly pre-registers mechanistic analysis experiments; not for production pipeline

---

## [04] SAELens

**Path**: `04-mechanistic-interpretability/saelens/`
**What it does**: Sparse Autoencoder training and analysis for mechanistic interpretability. Trains SAEs on transformer activations to discover interpretable features. Integrates with TransformerLens.

### Features & Capabilities
- Sparse autoencoder training on transformer activations
- Feature discovery: which concepts activate specific neurons
- Integration with TransformerLens
- Supports Gemma, Llama, GPT-2 family

### Applicability to HC-GRC
**Verdict**: INDIRECT
**Applicable to modules**: P1
**How it fits**: If HC-GRC uses TransformerLens for P1 mechanistic analysis, SAELens would enable feature-level discovery — identifying which model features correspond to security domain concepts (control categories, risk types, compliance terms). This is advanced P1 research that could yield novel findings about how LLMs represent security knowledge.

### Pros
- Could produce publishable findings about security domain representation in LLMs (research novelty for HC-GRC papers)
- Directly complementary to TransformerLens

### Cons / Risks
- Highly specialized; significant time investment for uncertain P1 payoff
- Only applicable to open-weight models, not Claude API

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Research supplement to TransformerLens in P1
**Condition**: Only if mechanistic interpretability is pre-registered as a P1 research sub-experiment; pair with TransformerLens

---

## [04] nnsight

**Path**: `04-mechanistic-interpretability/nnsight/`
**What it does**: Remote execution framework for mechanistic interpretability on large models (70B+) via NDIF (National Deep Inference Fabric). Enables activation patching and causal tracing on models too large for local execution.

### Features & Capabilities
- Remote execution on 70B+ parameter models via NDIF
- Same API as local PyTorch
- Supports multi-model experiments
- Causal tracing and intervention without local GPU requirements

### Applicability to HC-GRC
**Verdict**: INDIRECT
**Applicable to modules**: P1
**How it fits**: If P1's exhaustive NLP evaluation includes mechanistic analysis of large models (70B+), nnsight enables this without local GPU infrastructure. However, NDIF is a remote compute service — HC-GRC's data-sovereign requirement requires careful evaluation of what data is sent to NDIF.

### Pros
- Enables large-model interpretability without local GPU clusters
- NDIF is a research infrastructure (academic, not commercial cloud) — may be acceptable under data-sovereign policy

### Cons / Risks
- Data sovereignty concern: SCF control text would be sent to NDIF servers
- NDIF availability may be limited; dependent on external infrastructure
- Only relevant if large-model mechanistic analysis is in P1 scope

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Remote alternative to local TransformerLens for large models
**Condition**: Requires explicit data-sovereign policy exception; only use if NDIF is deemed acceptable for SCF data

---

## [04] pyvene

**Path**: `04-mechanistic-interpretability/pyvene/`
**What it does**: Stanford NLP's causal intervention framework for LLMs. Supports distributed alignment search (DAS), boundless DAS, and representation surgery. More flexible than TransformerLens for custom causal analysis.

### Features & Capabilities
- Causal interventions on any model component
- Distributed Alignment Search (DAS) for locating representations
- Representation surgery / steering vectors
- Supports HuggingFace models
- Stanford NLP pedigree

### Applicability to HC-GRC
**Verdict**: INDIRECT
**Applicable to modules**: P1
**How it fits**: pyvene's steering vectors and representation surgery could be used in P1 to test whether specific security concepts are linearly represented in embedding models. This would strengthen P1's mechanistic validation of which NLP algorithms are most reliable for SCF control mapping validation.

### Pros
- Steering vectors could serve as a novel P1 validation mechanism (interventional validation)
- Stanford NLP pedigree suggests strong research quality

### Cons / Risks
- High complexity for incremental P1 benefit
- Requires local model access (not Claude API)
- Causal intervention experiments require careful pre-registration

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Alternative/complement to TransformerLens for P1 causal analysis
**Condition**: Pre-register causal intervention experiments in SAP; only if mechanistic interpretability is in P1 scope

---

## [05] Ray Data

**Path**: `05-data-processing/ray-data/`
**What it does**: Distributed ML data processing framework. Handles streaming ingestion, batch transformations, and distributed batch inference at scale. Integrates with PyTorch, HuggingFace, and vLLM.

### Features & Capabilities
- Streaming data pipelines with backpressure
- Distributed batch inference (models + data both distributed)
- Lazy evaluation with automatic memory management
- Map/filter/group operations on large datasets
- Ray cluster integration for multi-node
- Integration with HuggingFace models for distributed embedding generation

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: P1/P2/P3/P4/P5/Data
**How it fits**: HC-GRC ingests and processes 280,000+ expert mappings across the SCF corpus. Ray Data handles: (1) streaming ingestion of SCF spreadsheets/JSON into the pipeline, (2) distributed embedding generation for all 280K mappings in P1, (3) batch inference for P5 clustering features, (4) parallel cross-framework mapping analysis in P3. All without loading the full corpus into memory.

### Pros
- Handles HC-GRC's 280K+ mapping scale without memory issues
- Streaming ingestion prevents full-corpus memory bottlenecks
- Distributed batch embedding generation dramatically accelerates P1 and P5
- Integrates directly with HuggingFace models (Sentence Transformers) and Qdrant
- DVC-compatible: Ray Data pipelines can be tracked as DVC stages

### Cons / Risks
- Ray cluster setup adds infrastructure complexity (though single-node mode works without a cluster)
- Requires careful memory management configuration for local-first deployment

### Integration Decision
**Use**: YES
**Replaces or augments**: Augments DVC data pipelines; handles scale that pandas/numpy cannot

---

## [05] NeMo Curator

**Path**: `05-data-processing/nemo-curator/`
**What it does**: NVIDIA's GPU-accelerated data curation pipeline for LLM pretraining datasets. 16x faster deduplication than CPU-based methods. Includes quality filtering, PII redaction, toxicity filtering, and multilingual support.

### Features & Capabilities
- GPU-accelerated fuzzy deduplication (MinHash LSH)
- 16x faster than CPU dedup on large corpora
- Quality filtering (fastText language ID, perplexity scoring)
- PII detection and redaction
- Synthetic data generation integration
- Dask-based distributed processing

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: Data/P1
**How it fits**: SCF corpus deduplication for P1 and P3 — removing duplicate or near-duplicate control descriptions before embedding ensures cleaner semantic analysis. PII redaction could be relevant if SCF data contains organizational-specific annotations. Quality filtering could identify low-quality or inconsistently formatted control mappings before they enter the analysis pipeline.

### Pros
- Fuzzy deduplication catches near-duplicate control descriptions that exact dedup misses (relevant for P3 cross-framework overlaps)
- PII redaction protects sensitive organizational metadata in SCF annotations
- Dask backend can run on single machines without a full cluster

### Cons / Risks
- GPU requirement: full speed requires NVIDIA GPU; CPU fallback exists but loses the 16x speedup
- Heavy infrastructure for what may be a one-time data cleaning step
- Overkill if SCF corpus deduplication is simple (structured data vs. web crawl scale)

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Augments DVC data pipeline for initial SCF corpus preprocessing
**Condition**: Use if SCF corpus contains significant duplication or requires PII redaction; skip if data is already clean and structured

---

## [06] GRPO RL Training

**Path**: `06-post-training/grpo-rl-training/`
**What it does**: Comprehensive guide for Group Relative Policy Optimization using TRL. Implements reward-based LLM alignment with multi-reward functions, curriculum learning, and production deployment patterns. The "gold standard" skill in this library.

### Features & Capabilities
- GRPO training with custom reward functions
- Multi-reward composition (accuracy + format + domain-specific)
- Curriculum learning for reward difficulty
- TRL GRPOTrainer integration
- Distributed training with DeepSpeed/FSDP
- Production deployment with vLLM
- Detailed troubleshooting for reward hacking, mode collapse

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P5
**How it fits**: If HC-GRC develops a specialized validation model for P1 (verifying NLP algorithm outputs against expert ground truth), GRPO with domain-specific reward functions (e.g., "does the predicted control mapping match expert consensus?") could train a highly calibrated validator. Also applicable if P5 cluster labeling models need alignment.

### Pros
- Custom reward functions can encode HC-GRC's specific validation criteria (e.g., SCF mapping correctness)
- Multi-reward composition allows balancing accuracy, format compliance, and domain specificity
- Most comprehensive skill in the library — reliable documentation

### Cons / Risks
- Requires ground truth labels for reward modeling (HC-GRC has expert mappings, so this exists)
- GRPO training is expensive — needs GPU infrastructure
- Significant engineering investment; most P1 validation can be done with simpler NLP approaches first

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Advanced alternative to standard fine-tuning for P1 validation model
**Condition**: Only after simpler NLP approaches in P1 are exhausted; pre-register as a Phase 2 experiment in SAP

---

## [06] MILES

**Path**: `06-post-training/miles/`
**What it does**: Enterprise-grade RL training framework with FP8/INT4 precision, MoE expert routing, and hybrid parallelism for training 100B+ parameter models.

### Features & Capabilities
- FP8/INT4 mixed precision RL training
- MoE expert routing support
- Hybrid model + data parallelism
- 100B+ parameter scale

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: HC-GRC is not training 100B+ parameter models. Enterprise RL infrastructure at this scale is entirely outside HC-GRC's scope.

### Pros
- N/A

### Cons / Risks
- Massively overscaled for HC-GRC

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing in current architecture

---

## [06] OpenRLHF

**Path**: `06-post-training/openrlhf/`
**What it does**: Large-scale RLHF framework using Ray + vLLM for PPO, GRPO, and RLOO training. Supports models up to 70B. Separates actor/critic/reference/reward models across nodes.

### Features & Capabilities
- Ray + vLLM distributed RLHF
- PPO, GRPO, RLOO algorithms
- 70B model support
- Multi-node actor/critic separation

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: Multi-node RLHF infrastructure for 70B models is outside HC-GRC's scope. Use TRL/GRPO skill instead for any local RL experiments.

### Pros
- N/A

### Cons / Risks
- Requires multi-node Ray cluster; HC-GRC is local-first

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing; TRL is the appropriate tool if RL training is needed

---

## [06] SimPO

**Path**: `06-post-training/simpo/`
**What it does**: Reference-free preference optimization that eliminates the need for a reward model. Uses sequence-length-normalized rewards and a margin term for more stable DPO training.

### Features & Capabilities
- Reference-free DPO (no separate reward model needed)
- Sequence-length-normalized reward
- Simpler than standard DPO
- TRL-compatible implementation

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1
**How it fits**: If HC-GRC creates preference datasets from expert mapping comparisons (e.g., "mapping A is better than mapping B for control X"), SimPO's reference-free approach makes preference training feasible without a separate reward model. Simpler than GRPO for binary preference scenarios.

### Pros
- Simpler than GRPO for binary preference learning
- No separate reward model reduces infrastructure requirements
- Reference-free means less GPU memory than standard DPO

### Cons / Risks
- Thin skill documentation (likely auto-generated)
- Requires preference pair datasets from SCF expert mappings

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Simpler alternative to GRPO for P1 alignment
**Condition**: Only if binary preference datasets are available from SCF expert annotations; less preferred than GRPO for complex reward scenarios

---

## [06] Slime

**Path**: `06-post-training/slime/`
**What it does**: Megatron + SGLang based RL training framework from Zhipu AI (GLM team). Optimized for large-scale GRPO with structured generation during rollout.

### Features & Capabilities
- Megatron + SGLang RL training
- Structured generation during rollout
- Large-scale GRPO

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: Large-scale distributed RL framework; HC-GRC doesn't have the infrastructure or need.

### Pros
- N/A

### Cons / Risks
- Requires Megatron multi-node infrastructure

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing in current architecture

---

## [06] TorchForge

**Path**: `06-post-training/torchforge/`
**What it does**: Meta's PyTorch-native RL training framework for LLMs. Implements PPO, GRPO with native PyTorch without external RL libraries.

### Features & Capabilities
- Pure PyTorch RL (no external RL library dependencies)
- PPO and GRPO support
- Meta's production-quality engineering

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P5
**How it fits**: Same scope as GRPO/TRL skill. If HC-GRC fine-tunes with RL and prefers pure PyTorch over TRL's abstraction layer, TorchForge is an option. Less documentation than TRL skill.

### Pros
- Pure PyTorch: fewer dependencies than TRL
- Meta's engineering quality suggests reliability

### Cons / Risks
- Auto-generated skill content — rely on upstream Meta docs
- Less community support than TRL

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Alternative to TRL for RL fine-tuning if PyTorch-native is preferred
**Condition**: Same as GRPO skill; prefer TRL unless specific PyTorch-native requirement

---

## [06] TRL Fine-Tuning

**Path**: `06-post-training/trl-fine-tuning/`
**What it does**: HuggingFace's TRL library for SFT, DPO, PPO, GRPO, and reward modeling. The most widely-used RLHF/preference optimization library. Integrates with PEFT, accelerate, and vLLM.

### Features & Capabilities
- SFT, DPO, PPO, GRPO, RLOO, KTO trainers
- PEFT/LoRA integration
- vLLM-accelerated generation during PPO/GRPO
- Dataset utilities for preference pairs
- Reward modeling support
- WandB/TensorBoard integration

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P5
**How it fits**: If HC-GRC fine-tunes models on SCF domain data, TRL is the primary tool. Key scenarios: (1) SFT on control-mapping pairs for P1 domain adaptation, (2) DPO using expert preference data for improved mapping quality, (3) GRPO with custom reward for P5 cluster labeling accuracy. TRL integrates with PEFT (QLoRA) for local hardware compatibility.

### Pros
- Industry standard for RLHF/alignment fine-tuning
- PEFT integration makes it viable on local hardware
- Comprehensive: SFT through GRPO in one library
- Best documentation of all post-training skills

### Cons / Risks
- Only valuable if fine-tuning is pre-registered in SAP
- DPO/GRPO requires carefully constructed preference datasets from SCF expert mappings

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Primary fine-tuning tool if post-training experiments are pre-registered
**Condition**: Pre-register fine-tuning experiments; use QLoRA mode for local hardware

---

## [06] verl

**Path**: `06-post-training/verl/`
**What it does**: ByteDance's HybridFlow RL training framework for LLMs up to 671B parameters. Separates model states from computation for flexible parallelism.

### Features & Capabilities
- HybridFlow architecture
- 671B parameter support
- Flexible model-compute separation

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: 671B-scale RL training infrastructure; completely outside HC-GRC's scope.

### Pros
- N/A

### Cons / Risks
- Requires massive compute infrastructure

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing in current architecture

---

## [07] Constitutional AI

**Path**: `07-safety-alignment/constitutional-ai/`
**What it does**: Anthropic's Constitutional AI framework for AI safety via self-critique and revision. Implements RLAIF (RL from AI Feedback) using a constitutional rule set. Powers Claude's alignment. Includes CAI training loop, red-teaming patterns, and self-improvement cycles.

### Features & Capabilities
- Constitutional rule sets (principles-based, not just RLHF)
- Self-critique → revision cycle (SL-CAI)
- RLAIF: AI-generated preference labels replacing human labelers
- Red-teaming integration
- Critique, revision, and preference model training patterns
- Anthropic API integration for Constitutional prompting

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: Orchestration/P1/P5
**How it fits**: HC-GRC's multi-agent system needs principled safety constraints. Constitutional AI patterns directly apply: (1) Self-critique loops for validating agent outputs before committing to experiment logs (P1 validation quality), (2) Constitutional rules encoding HC-GRC's SCF_CONSTITUTION.md principles, (3) RLAIF patterns for generating preference labels from Claude without human annotation in P1 and P5.

### Pros
- Directly mirrors HC-GRC's SCF_CONSTITUTION.md philosophy — rules-based safety over black-box RLHF
- Self-critique patterns plug directly into LangGraph agent nodes as validation steps
- RLAIF reduces need for human labelers for P1 preference dataset creation
- Anthropic's own framework — deep Claude API integration

### Cons / Risks
- Requires careful constitutional rule design for SCF domain (not out-of-box)
- Constitutional prompting adds latency to each agent cycle

### Integration Decision
**Use**: YES
**Replaces or augments**: Augments HC-GRC's SAP enforcement layer; provides self-critique patterns for LangGraph validation nodes

---

## [07] LlamaGuard

**Path**: `07-safety-alignment/llamaguard/`
**What it does**: Meta's 7-8B parameter LLM content moderation model. Classifies inputs and outputs across 6 harm categories (violence, hate, sexual, privacy, IP, safety). Achieves 94-95% accuracy. Available in LlamaGuard 1/2/3 versions.

### Features & Capabilities
- 7-8B parameter moderation (fast, local)
- 6 harm categories with customizable policy
- Input AND output classification
- 94-95% accuracy on benchmarks
- Customizable category definitions
- Local deployment (no API dependency)

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: Orchestration
**How it fits**: HC-GRC's 10-agent LangGraph pipeline processes expert-curated security control text through Claude. LlamaGuard provides local, data-sovereign content moderation: (1) screen LLM outputs before they enter experiment logs, (2) prevent prompt injection attacks from SCF corpus data that might contain adversarial content, (3) validate that agent outputs don't inadvertently expose sensitive policy information. Local deployment aligns with data-sovereign requirement.

### Pros
- Local deployment satisfies data-sovereign constraint
- Input + output moderation covers full HC-GRC pipeline
- Customizable harm categories can be tuned to HC-GRC's security context
- Fast enough for production pipeline integration

### Cons / Risks
- 7-8B model requires local GPU or CPU with significant RAM
- May generate false positives on legitimate security terminology in SCF controls
- Category definitions need tuning for security/compliance domain

### Integration Decision
**Use**: YES
**Replaces or augments**: Augments HC-GRC safety layer; local-first alternative to API-based moderation

---

## [07] NeMo Guardrails

**Path**: `07-safety-alignment/nemo-guardrails/`
**What it does**: NVIDIA's runtime safety framework for LLM applications. Uses Colang 2.0 for declarative safety rules. Covers jailbreak detection, PII protection, hallucination checks, off-topic filtering, and dialog flow control.

### Features & Capabilities
- Colang 2.0: declarative dialog flow and safety rules
- Input, dialog, output, and retrieval guardrails
- Jailbreak and prompt injection detection
- PII detection and masking
- Hallucination detection (fact-checking against knowledge base)
- LangChain and LlamaIndex integration
- Streaming support

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: Orchestration/P1/P3/P4
**How it fits**: NeMo Guardrails is the runtime safety layer HC-GRC's LangGraph pipeline needs. Specific applications: (1) Dialog flow control to keep agents focused on SCF analysis tasks (off-topic filtering), (2) Hallucination detection for P1 and P3 outputs (validate that cited control IDs actually exist in SCF), (3) PII protection for any organizational data in SCF annotations, (4) Colang rules can encode HC-GRC's RISK_CONSTITUTION.md constraints directly.

### Pros
- Colang 2.0 rules can directly encode SCF_CONSTITUTION.md and RISK_CONSTITUTION.md as runtime safety constraints
- Hallucination detection for control ID validation is directly applicable to P1/P3 accuracy
- LangChain integration connects to existing RAG components
- Open-source and local — data-sovereign compatible

### Cons / Risks
- Colang 2.0 has a learning curve
- Runtime overhead on every agent interaction
- Hallucination detection quality depends on knowledge base completeness

### Integration Decision
**Use**: YES
**Replaces or augments**: Primary runtime safety layer for HC-GRC's LangGraph pipeline; augments Constitutional AI patterns

---

## [07] Prompt Guard

**Path**: `07-safety-alignment/prompt-guard/`
**What it does**: Meta's 86M parameter prompt injection and jailbreak detection model. 99% true positive rate on injection detection with <2ms latency. Classifies inputs as BENIGN, INJECTION, or JAILBREAK.

### Features & Capabilities
- 86M parameter (extremely lightweight, runs on CPU)
- 99% TPR on prompt injection
- <2ms latency
- Binary + multi-class classification (BENIGN/INJECTION/JAILBREAK)
- ONNX export for production
- Local deployment

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: Orchestration
**How it fits**: HC-GRC's agents process SCF corpus data (external source) and user queries. Prompt Guard at 86M params with <2ms latency is the ideal lightweight first-pass filter: runs on CPU before every LLM call to screen for injection attacks embedded in SCF data or user inputs. The 99% TPR means high confidence in catching adversarial content without significant false positives.

### Pros
- <2ms latency makes it viable as a pre-filter on every single LLM call
- 86M params runs on CPU without GPU requirement (data-sovereign, local-first)
- 99% TPR provides strong security guarantee for the pipeline
- Complements NeMo Guardrails (Prompt Guard = fast detection, NeMo = comprehensive policy enforcement)

### Cons / Risks
- Model weights require local storage (~340MB)
- False positive rate needs validation on SCF security terminology

### Integration Decision
**Use**: YES
**Replaces or augments**: First-pass injection filter in HC-GRC's LangGraph input processing; complements NeMo Guardrails

---

## [08] Accelerate

**Path**: `08-distributed-training/accelerate/`
**What it does**: HuggingFace's unified distributed training API. 4-line code change to go from single-GPU to multi-GPU/TPU. Supports FSDP, DeepSpeed ZeRO, and DDP. The standard wrapper for scalable HuggingFace training.

### Features & Capabilities
- 4-line distributed training enablement
- FSDP, DeepSpeed, DDP support
- Mixed precision (FP16/BF16)
- Gradient accumulation
- Works with any PyTorch model

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P5
**How it fits**: If HC-GRC runs local fine-tuning experiments (PEFT/TRL), Accelerate is the standard distribution wrapper. Single-machine multi-GPU scenarios would benefit from Accelerate's zero-code-change distribution.

### Pros
- Minimal code change for distribution (4 lines)
- Standard HuggingFace ecosystem integration
- Works with PEFT and TRL transparently

### Cons / Risks
- Only relevant if fine-tuning experiments are approved in SAP
- Single-node multi-GPU scenarios may not apply to HC-GRC hardware

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Distribution wrapper for PEFT/TRL fine-tuning experiments
**Condition**: Same conditions as PEFT; implicit dependency rather than explicit tool selection

---

## [08] DeepSpeed

**Path**: `08-distributed-training/deepspeed/`
**What it does**: Microsoft's distributed training framework with ZeRO memory optimization. ZeRO stages 1-3 shard optimizer states, gradients, and model parameters across GPUs for training models larger than single-GPU memory.

### Features & Capabilities
- ZeRO-1/2/3 memory optimization
- Mixed precision training
- Pipeline parallelism
- Large model training (100B+ with ZeRO-3)

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: HC-GRC is not training large models from scratch. ZeRO optimization is relevant only for multi-GPU training of very large models — outside HC-GRC's scope. Accelerate covers any needed distribution for fine-tuning.

### Pros
- N/A

### Cons / Risks
- Overkill for any fine-tuning HC-GRC might do

### Integration Decision
**Use**: NO
**Replaces or augments**: Accelerate handles any necessary distribution

---

## [08] Megatron-Core

**Path**: `08-distributed-training/megatron-core/`
**What it does**: NVIDIA's tensor + pipeline parallelism framework for training LLMs at the largest scales (47% Model FLOP Utilization on H100). Used for GPT-3/4-scale pretraining.

### Features & Capabilities
- Tensor + pipeline parallelism
- 47% MFU on H100
- Used for GPT-3/4-class pretraining

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: GPT-3/4-scale pretraining infrastructure; entirely outside HC-GRC's scope.

### Pros
- N/A

### Cons / Risks
- Requires NVIDIA H100-class hardware clusters

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing in current architecture

---

## [08] PyTorch FSDP2

**Path**: `08-distributed-training/pytorch-fsdp2/`
**What it does**: PyTorch 2.0's Fully Sharded Data Parallel (FSDP2) using DTensor. Shards model weights, gradients, and optimizer states across GPUs for memory-efficient large model training.

### Features & Capabilities
- DTensor-based weight sharding
- Mixed precision with per-param casting
- Activation checkpointing
- Integration with TorchTitan

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: FSDP2 is for training large models across multiple GPUs. HC-GRC's local fine-tuning (if any) would use QLoRA instead, making FSDP2 unnecessary.

### Pros
- N/A

### Cons / Risks
- Overkill for local fine-tuning; QLoRA is more appropriate

### Integration Decision
**Use**: NO
**Replaces or augments**: QLoRA (PEFT) is more appropriate for HC-GRC's scale

---

## [08] PyTorch Lightning

**Path**: `08-distributed-training/pytorch-lightning/`
**What it does**: High-level PyTorch training framework with automatic hardware abstraction. Trainer class handles distributed training, logging, checkpointing, and mixed precision.

### Features & Capabilities
- High-level Trainer API
- Automatic GPU/TPU/CPU detection
- Built-in logging to WandB/TensorBoard/MLflow
- LightningModule for standardized model organization

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P5
**How it fits**: If HC-GRC trains custom models (classification heads, embedding models for P1/P5), PyTorch Lightning's built-in MLflow integration aligns with HC-GRC's MLflow tracking requirement. The Trainer's automatic checkpointing supports DVC-compatible experiment tracking.

### Pros
- MLflow integration out-of-box aligns with HC-GRC's tracking stack
- Standardized LightningModule pattern makes training code more maintainable
- Automatic checkpointing supports reproducibility requirements

### Cons / Risks
- Only relevant if training custom models, which is conditional on SAP pre-registration
- Overlaps with Accelerate; choosing between them adds decision overhead

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Alternative to Accelerate for custom model training with built-in MLflow integration
**Condition**: Prefer over Accelerate if custom non-HuggingFace models are trained; require SAP pre-registration

---

## [08] Ray Train

**Path**: `08-distributed-training/ray-train/`
**What it does**: Ray's distributed training framework. Handles multi-node training for PyTorch, TensorFlow, and HuggingFace models. Integrates with Ray Data for end-to-end distributed ML pipelines.

### Features & Capabilities
- Multi-node distributed training
- PyTorch, TF, HuggingFace support
- Integration with Ray Data, Ray Tune
- Fault tolerance and auto-recovery
- Hyperparameter sweep integration (Ray Tune)

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P5/Data
**How it fits**: If HC-GRC uses Ray Data (strongly recommended) for data processing, Ray Train provides a natural extension for distributed training experiments. The combined Ray Data + Ray Train pipeline would handle the full P1 workflow: ingest SCF → process with Ray Data → train NLP models with Ray Train → log to MLflow. Fault tolerance is valuable for long P1 training runs.

### Pros
- Natural extension of Ray Data (already recommended for HC-GRC)
- End-to-end distributed ML pipeline: Ray Data → Ray Train → MLflow
- Fault tolerance for long multi-day training runs
- Ray Tune integration for hyperparameter optimization in P1 experiments

### Cons / Risks
- Ray cluster setup complexity (though single-node mode avoids this)
- Overlaps with Accelerate; choose one

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Distributed training extension of Ray Data pipeline
**Condition**: Use if Ray Data is adopted and distributed training experiments are pre-registered; provides Ray ecosystem consistency


---

## [09] Lambda Labs

**Path**: `09-infrastructure/lambda-labs/`
**What it does**: Cloud GPU compute service offering H100/A100/V100 clusters for ML training and inference. Provides on-demand and reserved GPU instances at competitive pricing.

### Features & Capabilities
- H100/A100/V100 cloud GPU instances
- On-demand and reserved instances
- SSH and Jupyter access
- Lambda Cloud API for programmatic provisioning

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: HC-GRC's data-sovereign requirement prohibits sending SCF data to external cloud services. Lambda Labs is managed cloud infrastructure — violates the local-first constraint.

### Pros
- N/A

### Cons / Risks
- HARD BLOCKER: Data-sovereign requirement prohibits cloud GPU usage for SCF data processing

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing; local hardware is required for HC-GRC

---

## [09] Modal

**Path**: `09-infrastructure/modal/`
**What it does**: Serverless cloud compute platform for Python functions. Run ML workloads as serverless containers with automatic GPU provisioning. Supports persistent volumes, scheduled jobs, and webhooks.

### Features & Capabilities
- Serverless ML containers
- Automatic GPU provisioning
- Persistent volumes and scheduled jobs
- Python SDK for cloud deployment

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: Cloud serverless compute; violates data-sovereign requirement.

### Pros
- N/A

### Cons / Risks
- HARD BLOCKER: Serverless cloud execution sends SCF data to Modal's infrastructure

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing; local execution required

---

## [09] SkyPilot

**Path**: `09-infrastructure/skypilot/`
**What it does**: Multi-cloud compute orchestration that runs ML workloads across AWS, GCP, Azure, and Lambda Labs with automatic spot instance management and cost optimization.

### Features & Capabilities
- Multi-cloud job orchestration
- Automatic spot instance failover
- Cost optimization across providers
- YAML-based cluster definition

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: Multi-cloud orchestration; violates data-sovereign requirement. Even if used purely for compute (not storage), SCF data would transit external cloud infrastructure.

### Pros
- N/A

### Cons / Risks
- HARD BLOCKER: Data-sovereign constraint prohibits multi-cloud data transit

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing; local execution required

---

## [10] AWQ

**Path**: `10-optimization/awq/`
**What it does**: Activation-aware Weight Quantization for LLMs. Achieves 4-bit quantization with near-FP16 accuracy by protecting the 1% of weights critical to model quality. Faster than GPTQ with better perplexity.

### Features & Capabilities
- 4-bit weight quantization
- Near-FP16 accuracy preservation
- Faster than GPTQ
- vLLM and text-generation-inference compatible
- AutoAWQ Python library

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: Orchestration
**How it fits**: If HC-GRC deploys local open-weight models (for LlamaGuard, embedding models, or any fine-tuned models), AWQ quantization enables running larger models on local hardware without quality degradation. Particularly relevant if HC-GRC deploys a 7B-13B model locally for P1 validation or P5 classification.

### Pros
- Better accuracy/speed tradeoff than GPTQ for local deployment
- Reduces local model memory requirements (supports data-sovereign constraint)
- vLLM compatible if local model serving is used

### Cons / Risks
- Quantization accuracy loss may affect specialized NLP tasks in P1
- Only relevant if local open-weight model deployment is needed

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Quantization layer for locally deployed models (LlamaGuard, fine-tuned models)
**Condition**: Use when deploying >7B models locally; validate quantization quality on SCF NLP tasks

---

## [10] bitsandbytes

**Path**: `10-optimization/bitsandbytes/`
**What it does**: CUDA-based quantization library for INT8/NF4/FP4 inference and training. Powers QLoRA (NF4 quantization + LoRA). Enables 4-bit model loading for inference and training on consumer GPUs.

### Features & Capabilities
- INT8 matrix multiplication for inference
- NF4/FP4 quantization for training (QLoRA)
- 8-bit Adam optimizer
- Consumer GPU support (RTX 3090/4090)
- Seamless PEFT/TRL integration

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P5
**How it fits**: bitsandbytes is the enabling technology for QLoRA — if HC-GRC runs local fine-tuning experiments on SCF data, bitsandbytes is an implicit dependency. Also enables 8-bit inference for loading larger embedding models locally within memory constraints.

### Pros
- Enables QLoRA on consumer hardware — critical for local-first fine-tuning
- 8-bit Adam reduces optimizer memory by 75% — enables fine-tuning on smaller GPUs
- Implicit PEFT dependency (no explicit integration needed)

### Cons / Risks
- CUDA-only: no CPU fallback for Apple Silicon environments
- Only relevant if fine-tuning experiments are pre-registered

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Implicit dependency for PEFT/QLoRA experiments
**Condition**: Same as PEFT; automatic when using QLoRA mode

---

## [10] Flash Attention

**Path**: `10-optimization/flash-attention/`
**What it does**: IO-aware exact attention algorithm that reduces memory footprint from O(n²) to O(n) and accelerates attention computation 2-4x. Standard in all modern LLM training and inference.

### Features & Capabilities
- 2-4x attention speedup
- O(n) memory vs O(n²) standard attention
- Flash Attention 2/3 variants
- CUDA and Triton kernels
- Supports causal and non-causal attention

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P5
**How it fits**: Flash Attention is an implicit dependency when training or fine-tuning transformer models locally. If HC-GRC runs any local training experiments (PEFT/TRL), Flash Attention reduces memory usage and increases throughput. Not needed if only using Claude API.

### Pros
- Standard dependency for all local transformer training — no configuration needed
- Memory efficiency supports local-first training within hardware constraints

### Cons / Risks
- Only relevant for local model training/inference
- CUDA-only; requires NVIDIA GPU

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Implicit optimization dependency for local model training
**Condition**: Automatically beneficial if any local transformer training is performed

---

## [10] GGUF

**Path**: `10-optimization/gguf/`
**What it does**: GGML's quantized model format for CPU/Apple Silicon inference via llama.cpp. Enables running 7B-70B LLMs on consumer hardware (MacBook, gaming PCs) without GPU. 2-8 bit quantization options.

### Features & Capabilities
- CPU and Apple Silicon optimized inference
- 2-8 bit quantization levels (Q4_K_M most popular)
- Works with llama.cpp ecosystem
- Ollama integration
- Model conversion tools

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: Orchestration/P1
**How it fits**: If HC-GRC needs to run local LLMs (for LlamaGuard inference, local NLP models, or validation models) on Apple Silicon or CPU-only hardware, GGUF is the enabling format. Particularly relevant for data-sovereign deployments where GPU is not available. Pairs with the llama.cpp skill.

### Pros
- CPU/Apple Silicon inference — no GPU requirement for local model deployment
- Supports data-sovereign constraint without GPU dependency
- Ollama integration makes local model management simple

### Cons / Risks
- Quality degrades significantly at lower quantization levels (Q2/Q3)
- Inference speed slower than GPU-based alternatives for batch processing

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Enables local model deployment on CPU/Apple Silicon
**Condition**: Use if local LLM deployment is needed and no GPU is available

---

## [10] GPTQ

**Path**: `10-optimization/gptq/`
**What it does**: Post-training quantization using second-order Hessian information. More accurate than naive quantization at 4-bit. Slower quantization process than AWQ but produces high-quality models.

### Features & Capabilities
- 4-bit quantization with Hessian calibration
- ExLlama/ExLlamaV2 backend for fast inference
- Supports 2/3/4/8 bit quantization
- AutoGPTQ library

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: Orchestration
**How it fits**: Same scope as AWQ — quantization for local model deployment. AWQ is preferred over GPTQ for HC-GRC (faster, similar quality), but GPTQ is relevant as an alternative if specific models don't have AWQ quantizations available.

### Pros
- More model coverage than AWQ (older ecosystem)
- ExLlamaV2 backend provides fast inference

### Cons / Risks
- Slower quantization process than AWQ
- AWQ preferred for new deployments

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Alternative to AWQ for local model quantization
**Condition**: Use only if AWQ quantizations unavailable for a specific model

---

## [10] HQQ

**Path**: `10-optimization/hqq/`
**What it does**: Half-Quadratic Quantization — calibration-free 4-bit quantization. No calibration dataset needed (unlike GPTQ/AWQ). Faster to apply and competitive accuracy. Supports Llama, Mistral, Mixtral families.

### Features & Capabilities
- Calibration-free quantization (no dataset needed)
- 4-bit and 2-bit support
- Fast quantization (minutes vs. hours for GPTQ)
- Competitive quality vs GPTQ/AWQ

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: Orchestration
**How it fits**: Same as AWQ/GPTQ — local model quantization. HQQ's calibration-free approach is advantageous for HC-GRC because no calibration dataset is needed (preserving data sovereignty during model preparation).

### Pros
- No calibration dataset required — supports data-sovereign constraint during model preparation
- Fast quantization enables rapid experimentation with different base models

### Cons / Risks
- Newer than GPTQ/AWQ with less community validation

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Calibration-free alternative to AWQ/GPTQ for local model quantization
**Condition**: Prefer over AWQ/GPTQ when calibration dataset sovereignty is a concern

---

## [10] ML Training Recipes

**Path**: `10-optimization/ml-training-recipes/`
**What it does**: Meta's collection of production ML training best practices. Covers learning rate schedules, regularization, gradient management, mixed precision, and training stability. Reference guide for robust training runs.

### Features & Capabilities
- Learning rate schedule recommendations
- Gradient clipping and accumulation strategies
- Mixed precision training patterns
- Training stability diagnostics
- Checkpointing best practices

### Applicability to HC-GRC
**Verdict**: PARTIAL
**Applicable to modules**: P1/P5
**How it fits**: When HC-GRC runs fine-tuning experiments (P1/P5), this skill provides production-quality training practices that improve experiment reproducibility. Directly supports HC-GRC's scientific rigor requirements — well-calibrated training recipes reduce random training failures that could invalidate pre-registered experiments.

### Pros
- Improves reproducibility of fine-tuning experiments (supports SAP requirements)
- Gradient clipping and stability patterns prevent training failures
- Learning rate schedule guidance critical for domain adaptation fine-tuning

### Cons / Risks
- Reference skill, not a library — value is in reading and applying, not installing
- Only relevant when fine-tuning experiments are pre-registered

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Reference guidance for fine-tuning experiment design
**Condition**: Read before designing any fine-tuning experiment in SAP; not a dependency to install

---

## [11] BigCode Evaluation Harness

**Path**: `11-evaluation/bigcode-evaluation-harness/`
**What it does**: Evaluation framework specifically for code generation models. Covers HumanEval, MBPP, DS-1000, and other programming benchmarks. Supports 40+ code benchmarks.

### Features & Capabilities
- HumanEval, MBPP, DS-1000, MultiPL-E benchmarks
- 40+ code generation benchmarks
- Execution-based evaluation
- Multi-language code evaluation

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: HC-GRC analyzes security controls (natural language), not code. Code generation evaluation benchmarks have no applicability.

### Pros
- N/A

### Cons / Risks
- Entirely different domain (code vs. security control language)

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing in current architecture

---

## [11] lm-evaluation-harness

**Path**: `11-evaluation/lm-evaluation-harness/`
**What it does**: EleutherAI's comprehensive LLM evaluation framework. 60+ benchmarks including MMLU, HellaSwag, TruthfulQA, ARC, WinoGrande. Supports custom task definitions. Standard for academic LLM evaluation.

### Features & Capabilities
- 60+ academic benchmarks
- MMLU, TruthfulQA, ARC, HellaSwag, WinoGrande
- Custom task definition API
- HuggingFace model integration
- Distributed evaluation
- Few-shot prompting support

### Applicability to HC-GRC
**Verdict**: PARTIAL
**Applicable to modules**: P1/P5
**How it fits**: When HC-GRC fine-tunes or selects NLP models for P1/P5, lm-evaluation-harness validates that: (1) domain adaptation didn't cause catastrophic forgetting on general benchmarks, (2) security-domain fine-tuned models maintain reasoning capability. Custom task definitions can encode SCF-specific evaluation tasks (e.g., "given a control description, identify the correct framework mapping").

### Pros
- Custom task API enables HC-GRC-specific evaluation tasks for P1 validation quality
- Standard benchmarks ensure domain fine-tuning doesn't degrade general capability
- Distributed evaluation handles large-scale model assessment efficiently

### Cons / Risks
- Only relevant if HC-GRC is evaluating open-weight models (not Claude API)
- Custom task definition requires effort to encode SCF evaluation criteria

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Model quality validation for fine-tuned NLP models in P1/P5
**Condition**: Use when evaluating fine-tuned models; define custom SCF evaluation tasks in the harness

---

## [11] NeMo Evaluator

**Path**: `11-evaluation/nemo-evaluator/`
**What it does**: NVIDIA's enterprise LLM evaluation platform. 100+ benchmarks, automated pipeline, integration with NeMo training workflows. Supports custom metrics and large-scale evaluation.

### Features & Capabilities
- 100+ benchmarks
- Automated evaluation pipelines
- Custom metric support
- NeMo ecosystem integration

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P5
**How it fits**: Same scope as lm-evaluation-harness but with more benchmarks and NeMo ecosystem integration. If HC-GRC uses NeMo Curator for data processing, NeMo Evaluator provides ecosystem consistency for the evaluation pipeline.

### Pros
- More benchmarks than lm-evaluation-harness
- NeMo ecosystem integration (if NeMo Curator is adopted)

### Cons / Risks
- NVIDIA-centric stack; may require CUDA infrastructure
- Redundant if lm-evaluation-harness is adopted

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Alternative to lm-evaluation-harness; prefer if NeMo ecosystem is already in use
**Condition**: Only if NeMo Curator is also adopted; otherwise lm-evaluation-harness is simpler

---

## [12] llama.cpp

**Path**: `12-inference-serving/llama-cpp/`
**What it does**: CPU and Apple Silicon LLM inference using GGUF format. Runs 7B-70B models on consumer hardware. Server mode provides OpenAI-compatible API. Minimal dependencies, pure C++.

### Features & Capabilities
- CPU, Apple Silicon (Metal), and NVIDIA GPU inference
- OpenAI-compatible REST API server
- GGUF format support (2-8 bit quantization)
- Minimal dependencies
- Streaming output
- Batch inference support

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: Orchestration/P1
**How it fits**: HC-GRC's data-sovereign requirement makes llama.cpp ideal for running local models (LlamaGuard, domain-adapted NLP models) without cloud dependencies. The OpenAI-compatible API means HC-GRC's LangGraph agents can switch between Claude API and local llama.cpp models transparently. Apple Silicon support is critical if HC-GRC runs on MacBook hardware.

### Pros
- OpenAI-compatible API enables transparent Claude API substitution for local-first scenarios
- Apple Silicon Metal acceleration — ideal for MacBook-based development
- No cloud dependency — fully data-sovereign
- LlamaGuard can be deployed via llama.cpp server for local moderation

### Cons / Risks
- Slower throughput than GPU-accelerated vLLM for batch inference
- GGUF quality depends on quantization level chosen

### Integration Decision
**Use**: YES
**Replaces or augments**: Local model serving infrastructure; enables local-first deployment of LlamaGuard and validation models

---

## [12] SGLang

**Path**: `12-inference-serving/sglang/`
**What it does**: Structured Generation Language for fast LLM inference. RadixAttention for KV cache reuse, grammar-constrained generation (JSON/regex), and multi-call program compilation. 3-5x faster than naive vLLM for structured generation workloads.

### Features & Capabilities
- RadixAttention: KV cache reuse across requests with shared prefixes
- Grammar-constrained generation (JSON schema, regex)
- SGLang programs: compile multi-LLM-call workflows
- OpenAI-compatible API
- 3-5x throughput improvement for structured generation

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: P1/P2/P3/P4/P5/Orchestration
**How it fits**: HC-GRC's LangGraph agents need to produce structured outputs (Pydantic models, JSON) for every analytical module. SGLang's grammar-constrained generation ensures type-safe outputs directly from the inference engine. RadixAttention provides massive speedup for batch processing of the SCF corpus where many requests share system prompt prefixes. The compiled program model maps naturally to LangGraph's DAG structure.

### Pros
- Grammar-constrained generation eliminates JSON parsing errors in agent outputs
- RadixAttention is specifically valuable for HC-GRC: batch processing 280K+ mappings with shared system prompts gets 3-5x speedup
- SGLang programs can compile HC-GRC's multi-step agent workflows into efficient execution plans
- OpenAI-compatible: drop-in for Claude API in local inference scenarios

### Cons / Risks
- Primarily optimizes open-weight model serving, not Claude API
- RadixAttention benefits are reduced when using Claude API (vs. local models)
- New framework with smaller community than vLLM

### Integration Decision
**Use**: YES
**Replaces or augments**: Local model inference serving; grammar constraints augment Instructor/Outlines for type-safe outputs

---

## [12] TensorRT-LLM

**Path**: `12-inference-serving/tensorrt-llm/`
**What it does**: NVIDIA's TensorRT-based LLM inference engine. 10-100x throughput improvement over PyTorch on NVIDIA GPUs. Quantization, fusion, and hardware-specific optimizations for production deployment.

### Features & Capabilities
- 10-100x inference speedup on NVIDIA GPUs
- Quantization (FP8, INT8, INT4)
- Continuous batching
- Multi-GPU tensor parallelism

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: Orchestration
**How it fits**: If HC-GRC deploys local models on NVIDIA GPU hardware (LlamaGuard, fine-tuned models), TensorRT-LLM provides maximum throughput. However, the 10-100x speedup is most valuable for high-throughput production serving, which may exceed HC-GRC's batch processing needs.

### Pros
- Maximum throughput if NVIDIA GPU hardware is available
- Quantization pipeline handles model optimization end-to-end

### Cons / Risks
- NVIDIA-only; not applicable on Apple Silicon
- Complex setup compared to vLLM or llama.cpp
- Overkill for HC-GRC's batch processing needs unless serving at production scale

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Alternative to vLLM for NVIDIA GPU deployments requiring maximum throughput
**Condition**: Only if NVIDIA GPU is available and batch throughput requirements exceed vLLM's capabilities

---

## [12] vLLM

**Path**: `12-inference-serving/vllm/`
**What it does**: Fast LLM inference with PagedAttention for efficient KV cache management. Continuous batching for maximum throughput. OpenAI-compatible API. Supports all major model families and multi-modal models.

### Features & Capabilities
- PagedAttention for efficient KV cache
- Continuous batching
- OpenAI-compatible API
- Multi-GPU tensor parallelism
- Streaming, LoRA serving, speculative decoding
- 100+ model family support

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: Orchestration/P1/P5
**How it fits**: If HC-GRC serves local models (LlamaGuard, fine-tuned models, validation models), vLLM provides OpenAI-compatible high-throughput inference. PagedAttention is particularly valuable for concurrent HC-GRC agents making parallel inference requests during batch analysis. Integrates with SGLang for structured generation.

### Pros
- OpenAI-compatible API enables transparent model switching in LangGraph agents
- PagedAttention efficient for concurrent multi-agent requests
- LoRA serving enables serving fine-tuned adapters without full model reloads

### Cons / Risks
- NVIDIA GPU preferred (CPU mode available but slow)
- vLLM adds infrastructure overhead compared to llama.cpp for simple use cases

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Local model serving infrastructure; complements llama.cpp (vLLM for GPU, llama.cpp for CPU/Apple Silicon)
**Condition**: Use on NVIDIA GPU hardware; prefer llama.cpp for CPU/Apple Silicon

---

## [13] MLflow

**Path**: `13-mlops/mlflow/`
**What it does**: Open-source experiment tracking, model registry, and deployment platform. Tracks parameters, metrics, artifacts, and model versions. Supports Python, R, Java. Widely used in production ML pipelines.

### Features & Capabilities
- Experiment tracking (params, metrics, artifacts)
- Model registry with versioning
- MLflow Projects for reproducible runs
- MLflow Models for deployment
- LLM tracing (MLflow 2.9+)
- Auto-logging for sklearn, PyTorch, TF, HuggingFace

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: P1/P2/P3/P4/P5/Orchestration
**How it fits**: MLflow is ALREADY in HC-GRC's tech stack. Every P1-P5 experiment uses MLflow for tracking. Specific applications: (1) P1 algorithm comparison — track NLP algorithm performance metrics across all exhaustive variants, (2) MLflow Model Registry for versioning fine-tuned models, (3) MLflow Projects for reproducible experiment execution (DVC complements for data versioning, MLflow for model + metrics), (4) LLM tracing for agent call logging alongside Langfuse.

### Pros
- Already in stack — zero new infrastructure
- P1 exhaustive NLP algorithm comparison needs MLflow's run comparison views
- Model Registry integrates with DVC for complete reproducibility (data + model versioning)
- LLM tracing in MLflow 2.9+ complements Langfuse for dual observability

### Cons / Risks
- None — already committed to stack

### Integration Decision
**Use**: YES
**Replaces or augments**: Core experiment tracking infrastructure (already in stack)

---

## [13] SwanLab

**Path**: `13-mlops/swanlab/`
**What it does**: Open-source, self-hosted ML experiment tracking platform. Alternative to W&B with Chinese ecosystem support. Real-time monitoring, comparison views, and team collaboration features.

### Features & Capabilities
- Self-hosted deployment option
- Real-time metric streaming
- Experiment comparison
- Team collaboration
- W&B migration support

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P2/P3/P4/P5
**How it fits**: SwanLab's self-hosted deployment aligns with HC-GRC's data-sovereign requirement better than W&B's cloud-first approach. If HC-GRC needs richer experiment visualization than MLflow's UI provides, SwanLab is the self-hosted alternative with W&B-like UX. However, MLflow already covers the core tracking needs.

### Pros
- Self-hosted: data-sovereign compatible
- W&B-like UX without the cloud dependency
- Real-time metric streaming is better than MLflow for interactive monitoring

### Cons / Risks
- Redundant if MLflow meets HC-GRC's visualization needs
- Smaller community than MLflow/W&B

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Enhanced visualization alternative to MLflow UI
**Condition**: Adopt only if MLflow's visualization proves insufficient for P1's exhaustive algorithm comparison (50+ experiments); otherwise MLflow is sufficient

---

## [13] TensorBoard

**Path**: `13-mlops/tensorboard/`
**What it does**: Google's visualization toolkit for ML experiments. Real-time training curves, computation graph visualization, embedding projector, and image/text/audio logging.

### Features & Capabilities
- Training curve visualization
- Computation graph visualization
- Embedding projector (2D/3D UMAP/t-SNE)
- HParams (hyperparameter comparison)
- PyTorch Lightning and HuggingFace native integration

### Applicability to HC-GRC
**Verdict**: PARTIAL
**Applicable to modules**: P1/P2/P5
**How it fits**: TensorBoard's embedding projector is directly valuable for P2 (Control Space Topology) and P5 (AI Governance Cluster Analysis): visualize SCF control embeddings in 2D/3D to validate clustering quality before formal analysis. The embedding projector could serve as an exploratory tool for understanding the control space structure. MLflow has TensorBoard integration, enabling both tools in the same pipeline.

### Pros
- Embedding projector provides interactive 3D visualization of control embeddings (P2/P5 validation)
- MLflow integration means no separate setup if TensorBoard is used alongside MLflow
- Training curve visualization useful for any fine-tuning experiments

### Cons / Risks
- Partially redundant with MLflow for training metrics
- Embedding projector is primarily exploratory; not part of the production pipeline

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Embedding visualization supplement to MLflow
**Condition**: Use the embedding projector for exploratory P2/P5 topology validation; not for production tracking

---

## [13] Weights & Biases

**Path**: `13-mlops/weights-and-biases/`
**What it does**: Real-time ML experiment tracking with advanced visualization. W&B Sweeps for hyperparameter optimization. W&B Artifacts for dataset/model versioning. Industry standard for ML teams.

### Features & Capabilities
- Real-time metric streaming
- W&B Sweeps: automated hyperparameter optimization (Bayesian, grid, random)
- W&B Artifacts: dataset and model versioning
- Team collaboration and report sharing
- LLM evaluation (W&B Weave)

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P5
**How it fits**: W&B Sweeps could automate hyperparameter optimization for P1 NLP algorithm experiments — instead of manually trying all algorithm variants, Sweeps finds optimal configurations. W&B Weave (LLM evaluation) could complement Langfuse for Claude agent evaluation. HOWEVER: W&B's default cloud mode may conflict with data-sovereign requirements; self-hosted W&B server mitigates this.

### Pros
- W&B Sweeps for automated P1 hyperparameter optimization is highly valuable
- Richer visualization than MLflow for algorithm comparison reports
- W&B Weave provides LLM-specific evaluation on top of standard experiment tracking

### Cons / Risks
- Cloud-first: requires self-hosted W&B server to meet data-sovereign requirement
- Redundant with MLflow unless Sweeps or Weave functionality is needed
- Self-hosted W&B requires additional infrastructure setup

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Hyperparameter optimization augment for P1 algorithm experiments
**Condition**: Use W&B Sweeps for P1 hyperparameter optimization if exhaustive NLP algorithm evaluation requires automated search; deploy self-hosted W&B server to satisfy data-sovereign requirement

---

## [14] A-Evolve

**Path**: `14-agents/a-evolve/`
**What it does**: Self-improving agent evolution framework. Agents iteratively improve their own prompts and strategies through meta-learning loops. Inspired by evolutionary algorithms applied to agent optimization.

### Features & Capabilities
- Iterative agent self-improvement
- Prompt mutation and selection
- Meta-learning for agent optimization
- Evolutionary strategy application to agent design

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: Orchestration/P1
**How it fits**: HC-GRC's 10-agent LangGraph system could benefit from evolutionary optimization of agent prompts over time. Specifically for P1: as the exhaustive NLP algorithm evaluation runs, A-Evolve patterns could optimize the validation agent's prompts based on which approach best matches expert ground truth. This is a Phase 2 enhancement after the core pipeline is operational.

### Pros
- Could systematically improve HC-GRC agent prompt quality over time
- P1 validation agent prompt optimization via evolutionary methods aligns with the "exhaustive" requirement

### Cons / Risks
- Experimental framework; immature compared to DSPy for prompt optimization
- Meta-learning loops require careful pre-registration to avoid untracked experiments
- A-Evolve optimization must be logged in MLflow to satisfy SAP requirements

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: DSPy is preferred for systematic prompt optimization; A-Evolve is a research alternative
**Condition**: Consider only in Phase 2 after core pipeline is stable; pre-register evolutionary experiments in SAP; prefer DSPy for systematic prompt optimization

---

## [14] AutoGPT

**Path**: `14-agents/autogpt/`
**What it does**: Autonomous AI agent framework that chains GPT-4 actions to complete complex goals. Uses memory (local + vector), web browsing, file operations, and code execution. One of the original autonomous agent frameworks.

### Features & Capabilities
- Autonomous multi-step task execution
- Long-term memory with vector storage
- Web browsing and file operations
- Plugin system for extensibility
- Self-critique and reflection loops

### Applicability to HC-GRC
**Verdict**: INDIRECT
**Applicable to modules**: Orchestration
**How it fits**: AutoGPT's design patterns (memory management, reflection loops, tool use) inform HC-GRC's LangGraph agent design, but AutoGPT itself is not the right framework — HC-GRC uses LangGraph for deterministic, scientifically rigorous orchestration rather than AutoGPT's looser autonomous execution model.

### Pros
- Self-critique and reflection patterns are directly applicable to HC-GRC agent design
- Long-term memory pattern informs Qdrant integration design

### Cons / Risks
- AutoGPT's looser execution model conflicts with HC-GRC's scientific rigor requirements
- LangGraph already supersedes AutoGPT for structured multi-agent workflows
- Unpredictable agent behavior is incompatible with pre-registered experimental protocols

### Integration Decision
**Use**: NO
**Replaces or augments**: LangGraph is HC-GRC's orchestration; AutoGPT patterns may inform design but the framework itself is not used

---

## [14] CrewAI

**Path**: `14-agents/crewai/`
**What it does**: Role-based multi-agent framework without LangChain dependency. Agents have defined roles, goals, and backstories. Supports sequential, hierarchical, and parallel crew execution modes.

### Features & Capabilities
- Role-based agent definition (role, goal, backstory)
- Sequential, hierarchical, parallel execution modes
- No LangChain dependency
- Task delegation between agents
- Tool integration

### Applicability to HC-GRC
**Verdict**: INDIRECT
**Applicable to modules**: Orchestration
**How it fits**: CrewAI's role-based agent model maps conceptually to HC-GRC's 10 specialized agents (each has a role: P1 validator, P2 graph analyst, etc.). The hierarchical execution mode mirrors HC-GRC's LangGraph supervisor-worker pattern. However, HC-GRC has already committed to LangGraph for orchestration, and CrewAI would be a replacement, not an addition.

### Pros
- Role-based agent definition provides conceptual clarity for documenting HC-GRC's agent responsibilities
- Hierarchical mode mirrors HC-GRC's supervisor-worker LangGraph pattern

### Cons / Risks
- Replacement, not addition — HC-GRC uses LangGraph (already committed)
- CrewAI abstracts over LangGraph; HC-GRC benefits from direct LangGraph control

### Integration Decision
**Use**: NO
**Replaces or augments**: LangGraph already serves as HC-GRC's orchestration; CrewAI is a redundant alternative

---

## [14] LangChain

**Path**: `14-agents/langchain/`
**What it does**: Comprehensive LLM application framework with 500+ integrations. Provides document loaders, text splitters, embedding wrappers, vector store connectors, chain abstractions, and agent toolkits. Foundation for most LLM RAG applications.

### Features & Capabilities
- 500+ document loaders and integrations
- RAG pipeline components (loaders, splitters, embedders, retrievers)
- Chain and agent abstractions
- Memory and conversation management
- LangSmith tracing integration
- LangGraph native integration

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: P1/P2/P3/P4/P5/Orchestration/Data
**How it fits**: LangChain's document loaders ingest SCF data (Excel/CSV/JSON/PDF) into the pipeline. Text splitters chunk control descriptions for Qdrant. The RAG pipeline components (loaders → splitters → embedders → retrievers) are the foundation for P1 control retrieval. LangChain integrates natively with LangGraph — HC-GRC can use LangChain tools within LangGraph nodes without framework conflict.

### Pros
- Native LangGraph integration — HC-GRC's orchestration framework
- Document loaders for all SCF source formats (Excel, CSV, JSON, PDF frameworks)
- RAG pipeline components directly power P1-P3 retrieval workflows
- 500+ integrations future-proof HC-GRC for new data sources

### Cons / Risks
- LangChain has a reputation for abstraction overhead that makes debugging harder
- Some LangChain abstractions can obscure what's actually happening in agent calls

### Integration Decision
**Use**: YES
**Replaces or augments**: Data ingestion and RAG pipeline foundation for all modules

---

## [14] LlamaIndex

**Path**: `14-agents/llamaindex/`
**What it does**: Data framework for LLM applications focused on document ingestion, indexing, and query. 300+ data connectors, advanced retrieval (semantic, keyword, hybrid), and query engines. Specialized for document Q&A and knowledge management.

### Features & Capabilities
- 300+ data connectors
- Advanced retrieval: semantic, keyword, hybrid, recursive
- Knowledge graph index
- Query engines (vector, SQL, knowledge graph)
- Document Q&A workflows
- Qdrant integration

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: P1/P2/P3/P4/P5
**How it fits**: LlamaIndex's knowledge graph index is directly applicable to P2 (Control Space Topology) — building a knowledge graph of SCF control relationships. Advanced hybrid retrieval (semantic + keyword) improves P1 control mapping validation accuracy. P3 (Regulatory Convergence Atlas) benefits from multi-document query engines that span multiple frameworks simultaneously. Native Qdrant integration connects to HC-GRC's existing vector store.

### Pros
- Knowledge graph index is the ideal P2 foundation
- Hybrid retrieval (semantic + keyword) is critical for P1 accuracy on technical control text
- Native Qdrant integration connects seamlessly to HC-GRC's vector store
- P3 multi-document querying enables cross-framework analysis without duplicating data

### Cons / Risks
- Overlaps with LangChain — need to decide which handles which pipeline components
- Both LangChain and LlamaIndex in the same stack adds complexity

### Integration Decision
**Use**: YES
**Replaces or augments**: Augments LangChain; LlamaIndex handles document indexing and advanced retrieval; LangChain handles agent orchestration and chains

---

## [15] Chroma

**Path**: `15-rag/chroma/`
**What it does**: Open-source embedding database. In-memory and persistent modes. Python SDK with simple collection management. Lightweight alternative to Qdrant for small-scale projects.

### Features & Capabilities
- In-memory and persistent storage
- Simple Python SDK
- Metadata filtering
- Cosine, L2, and inner product similarity
- LangChain and LlamaIndex integration

### Applicability to HC-GRC
**Verdict**: INDIRECT
**Applicable to modules**: P1/P2/P3/P4/P5
**How it fits**: HC-GRC already uses Qdrant (which is more performant and feature-rich). Chroma could serve as a lightweight development/testing alternative to Qdrant for local experimentation without Qdrant server setup. However, Qdrant is clearly superior for production use.

### Pros
- In-memory mode useful for unit testing RAG pipeline components without Qdrant
- Simpler setup for rapid prototyping new retrieval experiments

### Cons / Risks
- Qdrant already in stack and clearly superior for production
- Chroma would be a parallel vector store, adding confusion

### Integration Decision
**Use**: NO
**Replaces or augments**: Qdrant already serves this role; Chroma is redundant

---

## [15] FAISS

**Path**: `15-rag/faiss/`
**What it does**: Facebook's billion-scale similarity search library. Exact and approximate nearest neighbor search with GPU support. Specialized indexing structures (IVF, HNSW, PQ) for different scale/accuracy tradeoffs.

### Features & Capabilities
- Billion-scale ANN search
- GPU acceleration for batch similarity search
- Multiple index types: Flat, IVF, HNSW, PQ, ScaNN
- ID mapping for external document stores
- Python and C++ APIs
- LangChain and LlamaIndex integration

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P2/P5
**How it fits**: Qdrant handles HC-GRC's standard RAG retrieval, but FAISS provides something different: batch GPU-accelerated similarity search for P1 exhaustive pairwise comparison. When P1 needs to compute all-pairs similarity across 280K+ control mappings (for clustering validation), FAISS's IVF index provides 10-100x speedup over sequential Qdrant queries. P2 graph construction also requires pairwise similarity that FAISS handles at scale.

### Pros
- All-pairs similarity computation (P1 exhaustive comparison, P2 graph construction) is FAISS's specialty
- GPU acceleration for batch similarity is not Qdrant's primary strength
- IVF index handles 280K+ mappings efficiently

### Cons / Risks
- Requires careful integration alongside Qdrant (two vector stores)
- FAISS is not a vector database — no metadata filtering or persistence management
- GPU version requires CUDA

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Complementary to Qdrant for batch all-pairs similarity computation in P1/P2
**Condition**: Use FAISS for P1 exhaustive pairwise comparison and P2 graph construction; use Qdrant for standard retrieval and metadata-filtered queries

---

## [15] Pinecone

**Path**: `15-rag/pinecone/`
**What it does**: Managed serverless vector database. Fully managed, auto-scaling, high availability. REST and Python SDKs. Production-grade vector search without infrastructure management.

### Features & Capabilities
- Fully managed serverless
- Auto-scaling
- High availability
- Metadata filtering
- Hybrid search (vector + keyword)

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: Managed cloud service — violates HC-GRC's data-sovereign requirement. SCF data cannot be sent to Pinecone's cloud infrastructure.

### Pros
- N/A

### Cons / Risks
- HARD BLOCKER: Managed cloud service violates data-sovereign constraint

### Integration Decision
**Use**: NO
**Replaces or augments**: Qdrant (local-first) serves this role

---

## [15] Qdrant

**Path**: `15-rag/qdrant/`
**What it does**: High-performance vector search engine written in Rust. Supports dense, sparse, and multi-vector search with rich metadata filtering. Local-first with optional cloud. Persistent storage, collections, snapshots.

### Features & Capabilities
- Dense + sparse + multi-vector search
- Rich metadata filtering (AND/OR, range, geo)
- Rust performance (fast, low memory)
- Local-first deployment (Docker or binary)
- Named vectors for multi-embedding documents
- Collection snapshots for backup
- gRPC and REST APIs
- LangChain, LlamaIndex, LlamaGuard integration

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: P1/P2/P3/P4/P5
**How it fits**: Qdrant IS HC-GRC's vector database. All module embeddings stored here: P1 control embeddings for semantic retrieval, P2 control relationship graph via vector queries, P3 cross-framework mappings for convergence analysis, P4 risk coverage embeddings, P5 governance cluster embeddings. Named vectors allow multiple embedding types per control record. Metadata filtering enables per-module queries without separate collections.

### Pros
- Already in stack — core infrastructure
- Local-first satisfies data-sovereign requirement
- Named vectors store multiple embedding representations per control (critical for P1 exhaustive comparison)
- Rich metadata filtering enables per-domain (P5), per-framework (P3), per-risk-type (P4) queries

### Cons / Risks
- None — already committed to stack

### Integration Decision
**Use**: YES
**Replaces or augments**: Core vector storage infrastructure (already in stack)

---

## [15] Sentence Transformers

**Path**: `15-rag/sentence-transformers/`
**What it does**: State-of-the-art sentence and text embedding library. 5,000+ pretrained models on HuggingFace. Supports semantic similarity, clustering, retrieval, and cross-encoder reranking. Multilingual models available.

### Features & Capabilities
- 5,000+ pretrained models
- Bi-encoders for fast retrieval
- Cross-encoders for reranking
- Multilingual models (100+ languages)
- Semantic similarity, clustering, retrieval tasks
- Efficient batch encoding
- MTEB benchmark evaluation

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: P1/P2/P3/P4/P5
**How it fits**: Sentence Transformers generates all embeddings for the SCF corpus. Specific applications: (1) P1 — bi-encoder for fast semantic similarity between expert mappings, cross-encoder for high-accuracy reranking of top-k candidates, (2) P2 — embedding all 1,400 controls for topology analysis, (3) P3 — cross-lingual models for aligning controls from non-English regulatory frameworks, (4) P5 — embedding all 33-domain controls for clustering. Models like `all-mpnet-base-v2`, `multi-qa-mpnet-base-dot-v1` are directly applicable.

### Pros
- Directly generates HC-GRC's Qdrant embeddings
- Cross-encoder reranking improves P1 validation accuracy significantly (bi-encoder retrieves, cross-encoder reranks)
- 5,000+ models enables P1's exhaustive NLP algorithm evaluation across different embedding architectures
- Multilingual models support P3 cross-framework analysis with non-English source frameworks

### Cons / Risks
- Model selection requires empirical evaluation on SCF domain (which models work best for security control text?)
- Large model variety requires systematic evaluation infrastructure (lm-evaluation-harness custom tasks)

### Integration Decision
**Use**: YES
**Replaces or augments**: Core embedding generation for Qdrant; primary NLP tool for P1-P5

---

## [16] DSPy

**Path**: `16-prompt-engineering/dspy/`
**What it does**: Stanford NLP's declarative prompt optimization framework. Define LLM pipelines as programs; DSPy automatically optimizes prompts using few-shot examples or feedback. Signatures define input/output; Optimizers (BootstrapFewShot, MIPRO, COPRO) tune prompts.

### Features & Capabilities
- Declarative program definition (Signatures, Modules, Pipelines)
- Automatic few-shot prompt optimization
- MIPRO, COPRO, BootstrapFewShot optimizers
- Metrics-driven optimization (optimize for any score function)
- Assertions for constrained generation
- Works with any LLM API

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: P1/P2/P3/P4/P5/Orchestration
**How it fits**: DSPy systematically optimizes HC-GRC's LangGraph agent prompts against ground truth. Key applications: (1) P1 validation agent: optimize prompts to maximize agreement with expert SCF mappings, (2) P3 cross-framework mapping: optimize retrieval prompts for maximum mapping accuracy, (3) P4 risk analysis prompts: optimize for coverage completeness, (4) Overall orchestrator: DSPy Assertions enforce output format constraints across all agents. DSPy's metrics-driven approach aligns with HC-GRC's scientific rigor requirements — prompt optimization is measurable and reproducible.

### Pros
- Prompt optimization is measurable and reproducible (logs to MLflow with custom metric integration)
- MIPRO optimizer can discover prompts that outperform hand-crafted ones for SCF domain
- DSPy Assertions provide constrained generation without grammar engines
- Stanford NLP pedigree — scientifically rigorous prompt engineering

### Cons / Risks
- Optimization requires labeled examples (HC-GRC has expert mappings as ground truth)
- DSPy programs require restructuring LangGraph prompts as Signatures — non-trivial refactoring
- Optimizer runs can be expensive (many LLM calls)

### Integration Decision
**Use**: YES
**Replaces or augments**: Replaces ad-hoc prompt engineering in LangGraph agents with systematic optimization; tracks optimization results in MLflow

---

## [16] Guidance

**Path**: `16-prompt-engineering/guidance/`
**What it does**: Microsoft's constrained generation library. Controls LLM output structure using Python-native syntax (f-strings with generation constraints). Supports regex, grammar, and Pydantic-based constraints. Works with local GGUF and API models.

### Features & Capabilities
- Python f-string syntax for constrained generation
- Regex and grammar constraints
- Pydantic model integration
- Works with llama.cpp/GGUF models
- Token healing for prompt/generation boundaries

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P2/P3/P4/P5
**How it fits**: If HC-GRC uses local GGUF models (llama.cpp), Guidance provides Pydantic-constrained generation directly against those models — ensuring JSON output without post-processing. The Python-native syntax makes constraints easy to define inline with HC-GRC agent logic.

### Pros
- Best-in-class for constrained generation on GGUF/llama.cpp models
- Python-native syntax reduces constraint definition complexity
- Token healing avoids off-by-one issues in prompt/completion boundaries

### Cons / Risks
- Instructor is preferred for Claude API; Guidance is better for local GGUF models
- Redundant if Instructor and SGLang grammar constraints cover all use cases

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Constrained generation for local GGUF models; complements Instructor (Claude API) and SGLang (GPU serving)
**Condition**: Use specifically for local llama.cpp model constrained generation; Instructor handles Claude API

---

## [16] Instructor

**Path**: `16-prompt-engineering/instructor/`
**What it does**: Pydantic-based structured output library for LLM APIs. Wraps OpenAI, Anthropic, Gemini, and other APIs to return validated Pydantic models. Auto-retry on validation failures. Supports streaming, partial responses.

### Features & Capabilities
- Pydantic model validation for LLM outputs
- Auto-retry on validation failure (configurable max retries)
- Streaming and partial response support
- Anthropic, OpenAI, Gemini, Cohere support
- Hooks for logging and monitoring
- Partial models for streaming structured generation

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: P1/P2/P3/P4/P5/Orchestration
**How it fits**: Every HC-GRC LangGraph agent needs to produce structured outputs (validated Pydantic models). Instructor wraps the Claude API to enforce type-safe outputs: P1 validation agents return `ControlMappingValidation`, P2 topology agents return `GraphEdgeCollection`, P3 convergence agents return `FrameworkMappingResult`, etc. Auto-retry prevents pipeline failures from transient JSON parse errors.

### Pros
- Direct Anthropic API integration (Claude backbone)
- Auto-retry eliminates JSON parse failures in production pipeline
- Pydantic integration aligns with HC-GRC's type-safe Python stack
- Hooks enable Langfuse/MLflow logging of all structured LLM calls

### Cons / Risks
- Adds one abstraction layer over raw Claude API
- Complex nested Pydantic models may require careful prompt design

### Integration Decision
**Use**: YES
**Replaces or augments**: Wraps Claude API for all LangGraph agent structured outputs; primary type-safety layer

---

## [16] Outlines

**Path**: `16-prompt-engineering/outlines/`
**What it does**: Grammar-based constrained generation library. Uses finite-state machines and context-free grammars to constrain LLM output token-by-token. vLLM and llama.cpp integration. Supports JSON schema, regex, and custom grammars.

### Features & Capabilities
- FSM-based constrained generation
- JSON schema, regex, EBNF grammar constraints
- vLLM integration (token-level constraints)
- llama.cpp integration
- Type-consistent generation (guaranteed valid output)

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P2/P3/P4/P5
**How it fits**: When HC-GRC uses vLLM or llama.cpp for local model serving, Outlines provides token-level grammar constraints — stronger than Instructor's retry-based approach. Particularly valuable for P1's structured validation output where invalid JSON would require expensive model re-calls.

### Pros
- Token-level constraints are more efficient than Instructor's retry mechanism
- Guaranteed valid output even from smaller local models
- vLLM integration aligns with HC-GRC's local model serving

### Cons / Risks
- Instructor is sufficient for Claude API; Outlines is specifically for local models
- Redundant with SGLang's grammar constraints if SGLang is adopted

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Token-level grammar constraints for local vLLM/llama.cpp models; complements Instructor
**Condition**: Use for local model serving; prefer Instructor for Claude API; evaluate if SGLang grammar constraints are adopted first

---

## [17] LangSmith

**Path**: `17-observability/langsmith/`
**What it does**: LangChain's LLM tracing, evaluation, and monitoring platform. Records every LLM call, chain execution, and agent action. Online evaluation with LLM judges. Dataset management for evaluation.

### Features & Capabilities
- Automatic LangChain/LangGraph tracing
- Online evaluation with LLM judges
- Dataset management for regression testing
- A/B testing for prompt variants
- Human feedback collection
- Cloud-hosted (self-hosted option in enterprise plan)

### Applicability to HC-GRC
**Verdict**: PARTIAL
**Applicable to modules**: Orchestration/P1/P2/P3/P4/P5
**How it fits**: LangSmith's automatic LangGraph tracing is highly valuable — every HC-GRC agent call gets traced without additional code. The LLM judge evaluation capability lets HC-GRC assess agent output quality automatically. However, LangSmith's primary deployment is cloud-hosted, which conflicts with data-sovereign requirements. Self-hosted option exists but is enterprise-only.

### Pros
- Native LangGraph integration — traces all 10 HC-GRC agents automatically
- LLM judge evaluation for automated quality assessment (reduces need for human reviewers)
- A/B testing for DSPy-optimized vs. original prompts

### Cons / Risks
- Cloud-hosted by default — data-sovereign concern for SCF data in traces
- Self-hosted option requires enterprise plan (cost)
- Langfuse + OTel already in HC-GRC stack — redundant

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Augments existing Langfuse for LangGraph-specific trace visualization
**Condition**: Use only if self-hosted deployment is available; otherwise Langfuse + OTel is sufficient; do not send SCF data to LangSmith cloud

---

## [17] Phoenix (Arize)

**Path**: `17-observability/phoenix/`
**What it does**: Open-source LLM observability platform by Arize AI. OTel-native tracing, embedding drift detection, retrieval analysis, and LLM evaluation. Self-hosted. Compatible with Langfuse.

### Features & Capabilities
- OTel-native tracing (compatible with existing OTel stacks)
- Embedding drift detection over time
- RAG retrieval quality analysis (precision, recall at k)
- LLM evaluation (hallucination, toxicity, relevance)
- Self-hosted deployment
- Python SDK with LangChain/LlamaIndex integration

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: P1/P2/P3/P4/P5/Observability
**How it fits**: Phoenix's OTel-native design integrates directly with HC-GRC's existing Langfuse + OTel stack. Unique capabilities: (1) Embedding drift detection monitors whether SCF corpus embeddings degrade over time as the SCF corpus updates, (2) RAG retrieval analysis (precision@k) validates P1 control retrieval quality, (3) LLM evaluation flags hallucinated control IDs in agent outputs, (4) Self-hosted deployment satisfies data-sovereign requirement.

### Pros
- OTel-native: slots directly into existing Langfuse + OTel stack without duplication
- Embedding drift detection is unique — critical for monitoring P1/P5 embedding quality over time
- RAG retrieval quality analysis directly validates P1 and P3 retrieval performance
- Self-hosted: data-sovereign compatible
- LangChain/LlamaIndex integration connects to HC-GRC's RAG components

### Cons / Risks
- Some overlap with Langfuse (both do LLM tracing); need to divide responsibilities clearly
- Embedding drift detection requires consistent re-evaluation, adding operational overhead

### Integration Decision
**Use**: YES
**Replaces or augments**: Augments Langfuse + OTel with embedding drift detection and RAG quality metrics; Langfuse handles conversation/agent tracing, Phoenix handles embedding and retrieval analytics

---

## [18] AudioCraft

**Path**: `18-multimodal/audiocraft/`
**What it does**: Meta's audio generation framework for music and audio effects synthesis using transformer models. Generates audio from text prompts.

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: Audio generation has no applicability to HC-GRC's text-based security control analysis.

### Integration Decision
**Use**: NO

---

## [18] BLIP-2

**Path**: `18-multimodal/blip-2/`
**What it does**: Vision-language model for image captioning, visual Q&A, and image-text retrieval. Bridges frozen image encoder and LLMs.

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: HC-GRC processes text security controls. Vision-language models have no applicability.

### Integration Decision
**Use**: NO

---

## [18] CLIP

**Path**: `18-multimodal/clip/`
**What it does**: OpenAI's vision-language model for zero-shot image classification and image-text similarity. Embeds images and text into a shared space.

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: HC-GRC is text-only. CLIP's vision-language capabilities have no applicability to SCF control analysis.

### Integration Decision
**Use**: NO

---

## [18] Cosmos Policy

**Path**: `18-multimodal/cosmos-policy/`
**What it does**: NVIDIA's world model policy framework for physical AI and robotics. Simulates physical environments for policy training.

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: Robotics/physical AI framework; no relevance to security control analysis.

### Integration Decision
**Use**: NO

---

## [18] LLaVA

**Path**: `18-multimodal/llava/`
**What it does**: Large Language and Vision Assistant — multimodal model combining vision encoder with LLM for visual instruction following.

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: Vision-language model; no applicability to text-based SCF analysis.

### Integration Decision
**Use**: NO

---

## [18] OpenPI

**Path**: `18-multimodal/openpi/`
**What it does**: Physical intelligence model for robot manipulation policies. Video-conditioned robot control.

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: Robotics framework; completely outside HC-GRC's domain.

### Integration Decision
**Use**: NO

---

## [18] OpenVLA-OFT

**Path**: `18-multimodal/openvla-oft/`
**What it does**: Open-source Vision-Language-Action model for robot manipulation with optimized fine-tuning.

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: Robotics framework; no applicability to security control analysis.

### Integration Decision
**Use**: NO

---

## [18] Segment Anything (SAM)

**Path**: `18-multimodal/segment-anything/`
**What it does**: Meta's universal image segmentation model. Zero-shot segmentation of any object in any image.

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: Image segmentation; no applicability to text-based SCF analysis.

### Integration Decision
**Use**: NO

---

## [18] Stable Diffusion

**Path**: `18-multimodal/stable-diffusion/`
**What it does**: Open-source text-to-image diffusion model. Generates photorealistic images from text prompts.

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: Image generation; no applicability to security control analysis. Could theoretically generate figures for papers (P20), but matplotlib is more appropriate for data visualizations.

### Integration Decision
**Use**: NO

---

## [18] Whisper

**Path**: `18-multimodal/whisper/`
**What it does**: OpenAI's speech recognition model. Transcribes audio to text in 99 languages with high accuracy. Supports translation.

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: Speech recognition; HC-GRC processes structured text data, not audio.

### Integration Decision
**Use**: NO

---

## [19] Knowledge Distillation

**Path**: `19-emerging-techniques/knowledge-distillation/`
**What it does**: Training smaller student models to mimic larger teacher models. Methods include response distillation (soft labels), feature distillation (intermediate representations), and MiniLLM (generative distillation). Enables deploying smaller, faster models without proportional quality loss.

### Features & Capabilities
- Response distillation (KL divergence on output distributions)
- Feature distillation (intermediate layer matching)
- MiniLLM generative distillation
- 2-10x model size reduction
- Quality retention 90-95% of teacher

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P5
**How it fits**: If HC-GRC fine-tunes a large model (7B+) for P1 validation or P5 classification, knowledge distillation could create a smaller (1-3B) locally deployable model that retains domain performance while reducing inference cost. This supports local-first deployment within hardware constraints.

### Pros
- Enables deploying capable domain models within local hardware constraints
- Distilled models are faster for batch P1 processing of 280K+ mappings
- Supports data-sovereign deployment by making smaller models viable locally

### Cons / Risks
- Requires the full fine-tuned teacher model first (dependency on PEFT experiments)
- Distillation training is an additional experiment requiring SAP pre-registration
- Quality retention on specialized SCF domain tasks needs empirical validation

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Model compression for locally deployed fine-tuned models
**Condition**: Apply after successful fine-tuning experiments; pre-register as Phase 3 optimization in SAP

---

## [19] Long Context

**Path**: `19-emerging-techniques/long-context/`
**What it does**: Techniques for extending LLM context windows beyond training length. Methods include RoPE scaling (YaRN, LongRoPE), position interpolation, and ALiBi. Enables processing documents longer than model's original context limit.

### Features & Capabilities
- YaRN: efficient LLM long context extension
- LongRoPE: position interpolation
- ALiBi: train-short, test-long extrapolation
- 32K-1M+ token context windows

### Applicability to HC-GRC
**Verdict**: PARTIAL
**Applicable to modules**: P1/P3
**How it fits**: SCF corpus documents (full framework specifications) can be very long. Long context techniques enable processing complete regulatory frameworks in a single pass for P3 cross-framework analysis, rather than chunking and losing cross-document coherence. Also relevant for P1 when validating complex multi-control mappings with extensive context.

### Pros
- Whole-document processing improves P3 cross-framework alignment quality
- Reduces retrieval errors from chunking (chunks can lose control context)
- Claude API already supports long context; this skill is relevant for local model experiments

### Cons / Risks
- Claude API already handles long context natively — this skill is mostly for local models
- RoPE scaling quality degrades at extreme lengths (>4x training context)

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Long-context handling for local model experiments
**Condition**: Relevant primarily for local model experiments in P1/P3; Claude API handles long context natively

---

## [19] Model Merging

**Path**: `19-emerging-techniques/model-merging/`
**What it does**: Combining multiple fine-tuned models without retraining. Methods: SLERP (spherical linear interpolation), TIES (task vector consolidation), DARE (random weight elimination), and breadcrumbs merging.

### Features & Capabilities
- SLERP: smooth interpolation between two models
- TIES: multi-task model merging (resolves conflicts)
- DARE: sparse weight merging for less interference
- No additional training required
- Works on models with same architecture

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/P5
**How it fits**: If HC-GRC fine-tunes separate models for different modules (P1 validator, P5 classifier), model merging via TIES could create a single model that handles both tasks — reducing local deployment footprint. Also applicable if combining a general NLP model with a domain-adapted SCF model.

### Pros
- No retraining needed — low-cost specialization path
- TIES handles multi-task merging cleanly (P1 validator + P5 classifier → single model)
- Reduces local model deployment count

### Cons / Risks
- Requires multiple fine-tuned models first (dependency)
- Merged model quality is empirically unpredictable — needs careful validation
- Merging adds another experiment that requires SAP pre-registration

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Model consolidation after successful independent fine-tuning experiments
**Condition**: Apply after Phase 1 fine-tuning experiments; pre-register merging experiments; validate merged model quality on SCF benchmarks

---

## [19] Model Pruning

**Path**: `19-emerging-techniques/model-pruning/`
**What it does**: Removing unnecessary model weights to reduce size and increase inference speed. Methods: Wanda (gradient-free), SparseGPT (second-order), and structured pruning. Achieves 50% sparsity with minimal quality loss.

### Features & Capabilities
- Wanda: gradient-free pruning (fast)
- SparseGPT: second-order pruning (higher quality)
- Structured pruning (entire layers/heads)
- 50% sparsity with <1% perplexity increase
- ONNX and TensorRT export of pruned models

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/Orchestration
**How it fits**: Alternative to quantization for reducing local model inference cost. If HC-GRC deploys fine-tuned models locally, Wanda pruning at 50% sparsity reduces memory footprint while maintaining 99%+ of quality. Particularly useful if quantization (AWQ/GGUF) introduces unacceptable quality degradation on SCF domain tasks.

### Pros
- Alternative to quantization: pruning + quantization together achieve smaller models than either alone
- Wanda is gradient-free — fast to apply without recomputation
- Supports data-sovereign deployment by enabling capable models on constrained hardware

### Cons / Risks
- Quality degradation on specialized NLP tasks needs empirical validation for SCF domain
- Requires fine-tuned models first (dependency on PEFT experiments)

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Model optimization complement to quantization (AWQ/GGUF) for local deployment
**Condition**: Combine with quantization for maximum local model efficiency; pre-register pruning experiments in SAP

---

## [19] MoE Training

**Path**: `19-emerging-techniques/moe-training/`
**What it does**: Mixture of Experts model training. Sparse activation where only a subset of expert layers activate per token. Enables larger model capacity with similar compute cost. Implemented in Mixtral, DeepSeek-MoE.

### Features & Capabilities
- Sparse expert routing
- Expert load balancing
- Top-k expert selection
- Expert parallelism across GPUs

### Applicability to HC-GRC
**Verdict**: NOT APPLICABLE
**Applicable to modules**: None
**How it fits**: HC-GRC is not training MoE architectures. Expert parallelism requires multi-GPU training infrastructure not available.

### Pros
- N/A

### Cons / Risks
- Requires significant GPU infrastructure for MoE training

### Integration Decision
**Use**: NO
**Replaces or augments**: Nothing in current architecture

---

## [19] Speculative Decoding

**Path**: `19-emerging-techniques/speculative-decoding/`
**What it does**: Using a small draft model to generate candidate tokens verified by a larger target model. Achieves 1.5-3.6x inference speedup without quality degradation. Supported in vLLM and TGI.

### Features & Capabilities
- 1.5-3.6x inference speedup
- No quality degradation
- Draft model (small) + target model (large) pipeline
- vLLM integration
- Works with any transformer architecture

### Applicability to HC-GRC
**Verdict**: CONDITIONAL
**Applicable to modules**: P1/Orchestration
**How it fits**: If HC-GRC runs local inference at scale (P1 batch processing 280K+ mappings), speculative decoding with vLLM could provide 2x+ throughput improvement. Particularly valuable for local model serving during P1 exhaustive NLP algorithm evaluation where many inference calls are needed.

### Pros
- Free throughput improvement for local model inference (no quality trade-off)
- Directly reduces P1 batch processing time
- vLLM native support makes this low-effort to enable

### Cons / Risks
- Only applicable to local model serving (not Claude API)
- Requires a suitable draft model matching the target model architecture

### Integration Decision
**Use**: CONDITIONAL
**Replaces or augments**: Throughput optimization for vLLM local model serving
**Condition**: Enable automatically if vLLM is adopted for local model serving; minimal effort for 1.5-3.6x speedup

---

## [20] Academic Plotting

**Path**: `20-ml-paper-writing/academic-plotting/`
**What it does**: Publication-quality figure generation using Python (matplotlib, seaborn, plotly) with AI assistance (Gemini-based). Covers statistical plots, comparison tables, confusion matrices, and LaTeX-compatible figure export.

### Features & Capabilities
- Publication-quality matplotlib/seaborn figures
- Gemini-assisted plot generation from descriptions
- Statistical visualization (confidence intervals, error bars)
- LaTeX-compatible SVG/PDF export
- Color-blind-safe palettes
- NeurIPS/ICML/ICLR style guidelines

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: P1/P2/P3/P4/P5/Reporting
**How it fits**: Every HC-GRC analytical module produces results that require publication-quality visualization. P1 algorithm comparison plots, P2 topology network visualizations, P3 convergence heatmaps, P4 risk coverage gap charts, P5 cluster dendrograms — all require academic-grade figures for HC-GRC papers. The LaTeX-compatible export connects directly to the ML Paper Writing skill.

### Pros
- Every HC-GRC paper needs high-quality figures — this skill provides the workflow
- Conference-specific style guidelines (NeurIPS, ICML, ACL) ensure submission-ready figures
- Gemini-assisted generation accelerates figure iteration

### Cons / Risks
- Gemini-assisted generation requires Gemini API key (cloud call for figure generation, not data)
- Style guide must be selected based on target conference for each paper

### Integration Decision
**Use**: YES
**Replaces or augments**: Augments HC-GRC reporting pipeline with publication-quality visualization

---

## [20] ML Paper Writing

**Path**: `20-ml-paper-writing/ml-paper-writing/`
**What it does**: Comprehensive guide for writing ML conference papers (NeurIPS, ICML, ICLR, ACL, AAAI, COLM). Includes LaTeX templates, section-by-section structure guidance, reviewer-perspective writing, and submission checklist.

### Features & Capabilities
- LaTeX templates for 6 major ML venues
- Section structure guidance (Abstract, Introduction, Related Work, Method, Experiments, Conclusion)
- Reviewer-perspective writing guidance
- Experimental results presentation patterns
- Submission checklists per conference
- Common reviewer objection anticipation

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: Reporting
**How it fits**: HC-GRC's research outputs are academic papers. The ML Paper Writing skill provides the templates and structural guidance for publishing P1-P5 findings at appropriate venues (NeurIPS for methodology, ACL for NLP components, AAAI for AI governance, ICLR for ML systems). The Autoresearch skill routes to this for the final paper writing phase.

### Pros
- Direct application to HC-GRC's research output goals
- Conference-specific templates eliminate formatting work
- Reviewer-perspective guidance increases acceptance rates

### Cons / Risks
- Paper writing is a Phase 4+ activity; core analytical pipeline must be complete first

### Integration Decision
**Use**: YES
**Replaces or augments**: Paper writing workflow for HC-GRC research outputs; connects to Academic Plotting for figures

---

## [20] Presenting Conference Talks

**Path**: `20-ml-paper-writing/presenting-conference-talks/`
**What it does**: Guide for creating and delivering ML conference presentations. Covers Beamer (LaTeX) and PowerPoint slide design, narrative structure for 10/20/30-minute talks, and presentation delivery techniques.

### Features & Capabilities
- Beamer (LaTeX) slide templates
- PowerPoint/Keynote design guidance
- 10/20/30-minute talk structures
- Live demo guidance
- Poster presentation format

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: Reporting
**How it fits**: After HC-GRC papers are accepted, conference presentations are required. The Beamer templates connect to the LaTeX paper workflow. The structured talk formats help distill 5-module technical research into compelling 20-minute presentations.

### Pros
- Beamer integration with LaTeX paper workflow is seamless
- Conference talk structure guidance increases presentation effectiveness

### Cons / Risks
- Phase 4+ activity; relevant only after paper acceptance

### Integration Decision
**Use**: YES
**Replaces or augments**: Presentation workflow for accepted HC-GRC papers

---

## [20] Systems Paper Writing

**Path**: `20-ml-paper-writing/systems-paper-writing/`
**What it does**: Guide for writing systems-focused ML papers (OSDI, SOSP, ASPLOS, MLSys). Covers blueprint methodology, systems evaluation standards, and the "end-to-end" system narrative structure specific to systems venues.

### Features & Capabilities
- Systems venue templates (OSDI, SOSP, ASPLOS, MLSys)
- Blueprint methodology for system design papers
- Systems evaluation standards (throughput, latency, scalability)
- End-to-end system narrative

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: Reporting
**How it fits**: HC-GRC's LangGraph multi-agent infrastructure IS a system — publishable at MLSys, OSDI, or similar venues as a systems contribution. The blueprint methodology helps document HC-GRC's architecture as a reproducible research platform, separate from the domain findings (which go to NeurIPS/ACL).

### Pros
- HC-GRC's infrastructure can be a standalone systems paper contribution
- Blueprint methodology creates reproducible system documentation
- MLSys is an ideal venue for HC-GRC's multi-agent research infrastructure

### Cons / Risks
- Systems paper requires extensive end-to-end performance benchmarking

### Integration Decision
**Use**: YES
**Replaces or augments**: Systems-track paper writing for HC-GRC infrastructure publications

---

## [21] Brainstorming Research Ideas

**Path**: `21-research-ideation/brainstorming-research-ideas/`
**What it does**: Structured research ideation framework using adversarial collaboration, cross-domain analogies, and gap analysis. Includes templates for hypothesis generation, evaluation matrices, and research question formulation.

### Features & Capabilities
- Structured ideation frameworks
- Adversarial collaboration protocol
- Cross-domain analogy generation
- Research gap analysis templates
- Hypothesis generation checklists
- Evaluation matrix for idea ranking

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: Orchestration/P1/P2/P3/P4/P5
**How it fits**: HC-GRC's autonomous research platform needs structured ideation for hypothesis generation across all 5 modules. The adversarial collaboration protocol aligns with HC-GRC's Constitutional AI patterns (self-critique before committing to hypotheses). The Autoresearch skill's outer loop starts with ideation — this skill provides the concrete methods.

### Pros
- Structured ideation prevents P1-P5 from becoming purely algorithmic (algorithmic selection without hypotheses is engineering, not research)
- Adversarial collaboration protocol catches weak hypotheses before expensive experiments
- Aligns with HC-GRC's SAP pre-registration discipline

### Cons / Risks
- Ideation outputs must feed into SAP pre-registration; process must be formalized

### Integration Decision
**Use**: YES
**Replaces or augments**: Research hypothesis generation phase of Autoresearch outer loop

---

## [21] Creative Thinking for Research

**Path**: `21-research-ideation/creative-thinking-for-research/`
**What it does**: Cognitive science-based creative thinking frameworks for research. Covers lateral thinking, SCAMPER, TRIZ, and analogical reasoning applied to ML research ideation.

### Features & Capabilities
- Lateral thinking techniques
- SCAMPER methodology
- TRIZ inventive principles
- Analogical reasoning frameworks
- Divergent-convergent thinking protocols

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: Orchestration
**How it fits**: Complements Brainstorming Research Ideas skill. TRIZ inventive principles are particularly applicable to HC-GRC's novel problem space (applying ML to security control analysis) — TRIZ's contradiction resolution could help identify novel algorithmic approaches for P1-P5 that aren't obvious from the ML literature.

### Pros
- TRIZ contradiction resolution for novel SCF analysis methods
- Lateral thinking techniques help break free from standard NLP approaches in P1

### Cons / Risks
- Cognitive science frameworks require human application; not automatable in the pipeline
- Value depends on research maturity; most applicable in early ideation phases

### Integration Decision
**Use**: YES
**Replaces or augments**: Creative complement to Brainstorming Research Ideas in Autoresearch ideation phase

---

## [22] ARA Compiler

**Path**: `22-agent-native-research-artifact/ara-compiler/`
**What it does**: Compiles Agent-Native Research Artifacts (ARAs) from raw research materials (PDFs, code repositories, logs, datasets). Produces structured research artifacts with standardized metadata, provenance chains, and reproducibility information.

### Features & Capabilities
- Ingestion from PDFs, repos, logs, datasets
- Structured metadata extraction
- Provenance chain construction
- Reproducibility manifest generation
- Cross-reference resolution
- ARA schema validation

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: Orchestration/Data/Reporting
**How it fits**: HC-GRC's research artifacts (SCF analysis results, experiment logs, model outputs) need structured compilation for scientific reproducibility. ARA Compiler creates the ingestion layer: SCF source documents → structured research artifacts → Qdrant storage with full provenance. This directly implements HC-GRC's DVC + MLflow reproducibility requirements in a principled ARA framework.

### Pros
- Directly implements HC-GRC's provenance tracking requirements
- Structured metadata extraction from SCF source documents for DVC tracking
- Provenance chain validates that outputs trace to original SCF data sources
- ARA framework provides the scientific artifact structure that HC-GRC's SAP enforcement requires

### Cons / Risks
- ARA schema must be designed for HC-GRC's specific artifact types (not generic research artifacts)
- Compilation process adds workflow complexity

### Integration Decision
**Use**: YES
**Replaces or augments**: Augments DVC + MLflow with artifact provenance and structured metadata; implements the ingestion phase of HC-GRC's pipeline

---

## [22] ARA Research Manager

**Path**: `22-agent-native-research-artifact/ara-research-manager/`
**What it does**: Post-task provenance recording system for agent-native research. Records every agent action, decision, and output with structured metadata. Maintains research lineage from raw data through final conclusions.

### Features & Capabilities
- Post-task provenance recording
- Agent action logging with structured metadata
- Research lineage tracking
- Decision audit trails
- Integration with DVC and MLflow
- Provenance query interface

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: Orchestration/P1/P2/P3/P4/P5
**How it fits**: Every HC-GRC LangGraph agent action needs provenance recording for scientific reproducibility. ARA Research Manager provides the post-task recording layer: P1 algorithm evaluation decisions, P2 graph construction steps, P3 cross-framework mapping decisions, P4 risk assessment outputs, P5 cluster assignments — all tracked with decision audit trails. This is HC-GRC's SAP compliance record-keeping implemented as a structured framework.

### Pros
- Directly implements HC-GRC's SAP compliance audit requirements
- Decision audit trails enable post-hoc review of agent reasoning
- Integration with DVC and MLflow closes the loop on HC-GRC's existing tracking infrastructure
- Research lineage from raw SCF → final findings enables complete reproducibility

### Cons / Risks
- Recording overhead on every agent action (latency impact)
- Provenance storage grows rapidly for 280K+ mapping analysis runs

### Integration Decision
**Use**: YES
**Replaces or augments**: Augments DVC + MLflow + Langfuse with structured scientific provenance recording; implements SAP audit trail requirements

---

## [22] ARA Rigor Reviewer

**Path**: `22-agent-native-research-artifact/ara-rigor-reviewer/`
**What it does**: Seal Level 2 epistemic review framework. Evaluates research artifacts across 6 dimensions: reproducibility, validity, reliability, transparency, integrity, and impact. Automated quality gate for research outputs.

### Features & Capabilities
- Seal Level 2 epistemic review
- 6-dimension quality assessment (reproducibility, validity, reliability, transparency, integrity, impact)
- Automated quality gate for research outputs
- Structured review reports
- Integration with research manager provenance chain
- Constitutional AI-style self-critique loops

### Applicability to HC-GRC
**Verdict**: DIRECT
**Applicable to modules**: Orchestration/P1/P2/P3/P4/P5/Reporting
**How it fits**: ARA Rigor Reviewer IS HC-GRC's scientific enforcement layer. Every P1-P5 module output goes through Seal Level 2 review before being committed to the research record. The 6-dimension quality assessment maps directly to HC-GRC's RISK_CONSTITUTION.md requirements: reproducibility ↔ DVC, validity ↔ statistical tests, reliability ↔ cross-validation, transparency ↔ Langfuse traces, integrity ↔ pre-registration, impact ↔ significance tests.

### Pros
- Directly implements HC-GRC's scientific rigor enforcement layer
- Automated quality gate prevents low-quality results from entering the research record
- 6-dimension review maps to HC-GRC's existing quality requirements
- Constitutional AI self-critique integration aligns with HC-GRC's safety patterns
- Structured review reports are audit-ready for SAP compliance

### Cons / Risks
- Rigor review adds latency to every module output
- Review criteria must be calibrated to HC-GRC's specific quality thresholds
- Over-strict review gates could block valid results (requires careful threshold tuning)

### Integration Decision
**Use**: YES
**Replaces or augments**: Implements HC-GRC's scientific enforcement layer; quality gate for all P1-P5 module outputs before research record commitment


---

## Summary: Architecture Integration Map

### Skills Adoption Summary

| Category | Total Skills | YES | CONDITIONAL | NO |
|----------|-------------|-----|-------------|-----|
| 00 Autoresearch | 1 | 1 | 0 | 0 |
| 01 Model Architecture | 5 | 0 | 0 | 5 |
| 02 Tokenization | 2 | 0 | 2 | 0 |
| 03 Fine-Tuning | 4 | 0 | 4 | 0 |
| 04 Mechanistic Interpretability | 4 | 0 | 4 | 0 |
| 05 Data Processing | 2 | 1 | 1 | 0 |
| 06 Post-Training | 8 | 0 | 4 | 4 |
| 07 Safety Alignment | 4 | 4 | 0 | 0 |
| 08 Distributed Training | 6 | 0 | 4 | 2 |
| 09 Infrastructure | 3 | 0 | 0 | 3 |
| 10 Optimization | 7 | 0 | 5 | 2 (DeepSpeed, MoE-subset) |
| 11 Evaluation | 3 | 0 | 2 | 1 |
| 12 Inference Serving | 4 | 2 | 2 | 0 |
| 13 MLOps | 4 | 1 | 3 | 0 |
| 14 Agents | 5 | 2 | 1 | 2 |
| 15 RAG | 5 | 2 | 1 | 2 |
| 16 Prompt Engineering | 4 | 2 | 2 | 0 |
| 17 Observability | 2 | 1 | 1 | 0 |
| 18 Multimodal | 10 | 0 | 0 | 10 |
| 19 Emerging Techniques | 6 | 0 | 5 | 1 |
| 20 ML Paper Writing | 4 | 4 | 0 | 0 |
| 21 Research Ideation | 2 | 2 | 0 | 0 |
| 22 ARA | 3 | 3 | 0 | 0 |
| **TOTAL** | **98** | **25** | **41** | **32** |

### LangGraph Node → Skills Integration Map

| LangGraph Node | Skills Used | Verdict | Notes |
|----------------|-------------|---------|-------|
| **Orchestrator / Supervisor** | Autoresearch, Constitutional AI, NeMo Guardrails, Prompt Guard, LlamaGuard, ARA Research Manager, ARA Rigor Reviewer, DSPy | YES | Central coordination + safety enforcement + provenance + quality gates |
| **Data Ingestion Agent** | LangChain (document loaders), LlamaIndex (data connectors), Ray Data, NeMo Curator (CONDITIONAL), ARA Compiler, DVC | YES | SCF corpus ingestion → chunking → versioning → artifact compilation |
| **Embedding Agent** | Sentence Transformers, Qdrant, FAISS (CONDITIONAL), HuggingFace Tokenizers (CONDITIONAL), bitsandbytes (CONDITIONAL) | YES | Embedding generation → vector storage → multi-index management |
| **P1: STRM Calibration Agent** | Sentence Transformers, Qdrant, Instructor, DSPy, LlamaIndex (hybrid retrieval), MLflow, FAISS (batch similarity), lm-evaluation-harness (CONDITIONAL), Ray Data | YES | NLP semantic validation of expert mappings; exhaustive algorithm comparison |
| **P2: Topology Agent** | LlamaIndex (knowledge graph), Sentence Transformers, Qdrant, FAISS (graph construction), TensorBoard (embedding projector, CONDITIONAL), MLflow, ARA Research Manager | YES | Graph construction + clustering + topology analysis of control space |
| **P3: Convergence Atlas Agent** | LangChain, LlamaIndex (multi-doc queries), Sentence Transformers (multilingual), Qdrant, Instructor, MLflow | YES | Cross-framework mapping analysis; multilingual regulatory alignment |
| **P4: Risk Blindspot Agent** | LangChain, Qdrant, Instructor, DSPy, MLflow, ARA Research Manager | YES | Gap detection in risk coverage; structured output validation |
| **P5: Governance Cluster Agent** | Sentence Transformers, Qdrant, Ray Data, FAISS (CONDITIONAL), MLflow, TRL (CONDITIONAL), PEFT (CONDITIONAL), lm-evaluation-harness (CONDITIONAL) | YES | Cross-domain clustering of all 33 domains; ML clustering pipeline |
| **Fine-Tuning Agent** (CONDITIONAL) | PEFT, TRL, Unsloth, bitsandbytes, Accelerate/Ray Train, Axolotl/LLaMA-Factory, MLflow, lm-evaluation-harness, ML Training Recipes | CONDITIONAL | Domain adaptation for P1/P5 models; only if pre-registered in SAP |
| **Local Model Server** | llama.cpp, vLLM (CONDITIONAL), SGLang, GGUF, AWQ/GPTQ/HQQ, Outlines (CONDITIONAL), Guidance (CONDITIONAL) | YES/CONDITIONAL | Local-first model serving for LlamaGuard + domain models; data-sovereign |
| **Safety Filter (pre-LLM)** | Prompt Guard, LlamaGuard, NeMo Guardrails, Constitutional AI | YES | Input screening + output moderation + policy enforcement |
| **Observability Layer** | MLflow, Langfuse+OTel (existing), Phoenix (Arize), LangSmith (CONDITIONAL), TensorBoard (CONDITIONAL), SwanLab (CONDITIONAL) | YES | Experiment tracking + LLM tracing + embedding drift + retrieval quality |
| **Prompt Optimization** | DSPy, Instructor, Outlines (CONDITIONAL), Guidance (CONDITIONAL), A-Evolve (CONDITIONAL) | YES | Systematic prompt optimization across all agents using expert mappings as ground truth |
| **Scientific Enforcement** | ARA Compiler, ARA Research Manager, ARA Rigor Reviewer, Constitutional AI, MLflow, DVC | YES | SAP compliance + provenance + Seal Level 2 quality gates |
| **Research Reporting** | ML Paper Writing, Academic Plotting, Systems Paper Writing, Presenting Conference Talks | YES | Publication pipeline from findings → figures → papers → talks |
| **Research Ideation** | Brainstorming Research Ideas, Creative Thinking for Research, Autoresearch | YES | Hypothesis generation + structured ideation + SAP pre-registration |

### Priority Integration Sequence

**Phase 1 — Core Pipeline (implement first)**:
1. Ray Data — SCF corpus processing at scale
2. Sentence Transformers — embeddings for all modules
3. LangChain + LlamaIndex — ingestion and retrieval
4. Instructor — structured outputs from Claude API
5. Prompt Guard + LlamaGuard + NeMo Guardrails — safety layer
6. DSPy — systematic prompt optimization
7. Phoenix (Arize) — embedding drift + RAG quality monitoring
8. ARA Compiler + Research Manager — provenance and artifact tracking
9. ARA Rigor Reviewer — scientific quality gates

**Phase 2 — Enhancement (after core is operational)**:
10. FAISS — batch all-pairs similarity for P1/P2 scale
11. SGLang — structured generation for local models
12. llama.cpp — local model deployment (LlamaGuard, validation models)
13. Constitutional AI patterns — self-critique in LangGraph agents
14. SwanLab or W&B Sweeps — enhanced experiment visualization (if needed)
15. lm-evaluation-harness — custom SCF evaluation tasks

**Phase 3 — Research Experiments (pre-register in SAP)**:
16. PEFT + TRL + bitsandbytes — fine-tuning on SCF domain data
17. GRPO / DSPy optimization — reward-based alignment experiments
18. Knowledge Distillation + Model Pruning — model compression for deployment
19. Mechanistic Interpretability (TransformerLens, SAELens) — P1 interpretability research
20. Model Merging — consolidation of fine-tuned models

**Phase 4 — Publication**:
21. ML Paper Writing + Academic Plotting + Systems Paper Writing + Conference Talks

### Hard Exclusions (Data Sovereignty)

The following skills are permanently excluded from HC-GRC due to the data-sovereign requirement (SCF data cannot leave local infrastructure):

- Lambda Labs, Modal, SkyPilot (cloud GPU compute)
- Pinecone (managed cloud vector database)
- Weights & Biases cloud mode (use self-hosted or SwanLab instead)
- LangSmith cloud mode (use self-hosted or Langfuse instead)
- nnsight / NDIF (remote inference on external servers — requires policy exception)

### Not Applicable (Wrong Domain)

All 10 multimodal skills (AudioCraft, BLIP-2, CLIP, Cosmos Policy, LLaVA, OpenPI, OpenVLA-OFT, SAM, Stable Diffusion, Whisper) are excluded — HC-GRC processes structured text security controls, not images, audio, or video.

All 5 model architecture training skills (LitGPT, Mamba, NanoGPT, RWKV, TorchTitan) are excluded — HC-GRC uses Claude API and does not pretrain base LLMs.

Large-scale distributed training and RL infrastructure (DeepSpeed, Megatron-Core, PyTorch FSDP2, MILES, OpenRLHF, Slime, verl) are excluded — overkill for HC-GRC's local-first fine-tuning scale.

---

*Assessment complete. 98 skills evaluated. 25 YES, 41 CONDITIONAL, 32 NO.*
*Generated: 2026-06-09*
