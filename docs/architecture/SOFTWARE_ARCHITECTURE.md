# HC-GRC Research Platform — Complete Software Architecture

**Version**: 0.2 (skills-integrated)  
**Date**: 2026-06-09  
**Status**: Architecture design — revised after full skills assessment (SKILLS_ASSESSMENT.md)

**Changelog from v0.1**:
- Added FAISS as Qdrant complement (batch all-pairs P1 computation)
- Added Ray Data to data processing tier (280K STRM parallel processing)
- Added guardrails layer: Constitutional AI + LlamaGuard + NeMo Guardrails + Prompt Guard
- Added LlamaIndex as document indexing layer for literature corpus
- Added llama.cpp + SGLang for local domain-model inference
- ARA trilogy elevated to Phase 1 infrastructure (was afterthought)
- Instructor formalized across all agent output interfaces
- Phoenix embedding drift detection added as operational monitor
- Added Phase 2 conditional stack (fine-tuning, quantization) with decision triggers
- Agent roster expanded: Guardrails Agent added; ARA agents replace custom implementations

This document is the authoritative design specification for the HC-GRC autonomous research platform. Every component, dependency, integration point, agent role, workflow state, and enforcement mechanism is defined here before a line of code is written.

---

## 1. Design Principles

1. **Local-first, data-sovereign.** No research data, embeddings, traces, or results leave the machine. Every infrastructure component self-hosts or runs in-process.
2. **Scientific rigor is enforced by the system, not trusted to the operator.** Pre-registration, SAP compliance, multiple comparison correction, and null result tracking are enforced as graph-topology constraints — you cannot reach a node without passing through the gate that precedes it.
3. **Human controls the science; agents execute the labor.** Five explicit human approval gates. Agents cannot advance past a gate without a human decision. Agents can do everything else.
4. **Typed data contracts between every component.** No unstructured text passing between agents. Pydantic models at every interface boundary.
5. **Everything is versioned, auditable, and replayable.** Code (Git), data (DVC), agent runs (LangGraph checkpoints), experiments (MLflow), traces (Langfuse). Any result can be reproduced by replaying the versioned inputs through the versioned pipeline.
6. **Agents are specialists, not generalists.** Each agent has a narrow role, a defined tool surface, and a defined output schema. A literature agent does not write code. A statistical analyst does not fetch papers.

---

## 2. System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         HUMAN CONTROL LAYER                               │
│              (5 approval gates via LangGraph interrupt + resume)           │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────────────┐
│                     LANGGRAPH ORCHESTRATOR                                │
│     State: PostgreSQL checkpointer  |  Autoresearch two-loop backbone     │
│     Tracing: OpenTelemetry → Langfuse (self-hosted)                       │
└──┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬───────────────┘
   │      │      │      │      │      │      │      │      │
  LIT    DATA   EDA    HYP   STAT    QA   REPORT  ARA    GUARD
 AGENT  STEW  AGENT  FORM  AGENT  AGENT  AGENT  AGENTS  AGENT
   │      │      │      │      │      │      │     │       │
   └──────┴──────┴──────┴──────┴──────┴──────┴─────┘       │
                         │                                   │
           MCP TOOL SERVERS (in-process)                     │
 ┌────────┬────────┬────────┬────────┬────────┬──────────┐   │
LIT-SRCH  DVC   QDRANT   FAISS   MLflow  SAP-CHK  NBOOK    │
   │      │      │        │        │       │        │      │
OpenAlex  DVC   Qdrant  in-proc  MLflow  JSON-Sch  Git     │
LlamaIdx  CLI   local   batch   SQLite  validator append   │
                                                           │
                    GUARDRAILS LAYER ◄─────────────────────┘
          LlamaGuard | NeMo Guardrails | Prompt Guard
          (wraps every agent LLM output before state write)

                    OBSERVABILITY LAYER
          Langfuse (traces) | Phoenix (drift) | MLflow (experiments)
```

---

## 3. Complete Python Dependency Stack

Dependencies are organized by functional tier. Every module is present because it serves a specific role in the architecture. Alternatives are noted where a choice was made.

### 3.1 Data Acquisition and Parsing

```
# HTTP clients
requests==2.32.*             # synchronous HTTP; simple downstream fetches
httpx==0.27.*                # async HTTP; parallel data source downloads
aiohttp==3.10.*              # async HTTP; high-concurrency literature API calls

# Document parsing — primary formats
openpyxl==3.1.*              # SCF Excel parsing (primary data source)
xlrd==2.0.*                  # legacy XLS format support
python-docx==1.1.*           # Word document reading
pymupdf==1.24.*              # PDF extraction; faster and more accurate than PyPDF2
pdfplumber==0.11.*           # PDF table extraction; complements pymupdf
camelot-py[cv]==0.11.*       # PDF table extraction via lattice/stream detection
pytesseract==0.3.*           # OCR for scanned regulatory documents
pillow==10.4.*               # image handling (pytesseract dependency)

# Multi-format document extraction
unstructured[pdf,docx]==0.15.*   # unified extraction pipeline; handles mixed corpus

# Data serialization and validation
pydantic==2.7.*              # typed data models at every interface boundary
pydantic-settings==2.3.*     # settings management
jsonschema==4.23.*           # SAP and hypothesis register schema validation
python-stix2==3.0.*          # ATT&CK STIX format (P4 risk coverage)
lxml==5.2.*                  # XML/HTML parsing
beautifulsoup4==4.12.*       # HTML parsing for web sources
pyyaml==6.0.*                # YAML configuration
tomllib                      # TOML (stdlib in Python 3.11+)

# OSCAL parsing (no mature library exists; use pydantic models against NIST schema)
# Custom: src/data/parsers/oscal.py — pydantic models for NIST OSCAL JSON
```

### 3.2 NLP — Lexical Tier

```
# Classical NLP
scikit-learn==1.5.*          # TF-IDF, cosine similarity, Naive Bayes baseline, pipelines
nltk==3.9.*                  # tokenization, stemming, WordNet, stopwords, BLEU
rank-bm25==0.2.*             # BM25 retrieval; stronger baseline than TF-IDF for short texts
rapidfuzz==3.9.*             # Levenshtein, Jaro-Winkler, token sort/set ratio; ~50x faster than fuzzywuzzy
regex==2024.*                # extended regex; better Unicode support than re module
ftfy==6.2.*                  # fixes text encoding artifacts in regulatory documents
num2words==0.5.*             # normalize numeric tokens ("section 3" → "section three")
contractions==0.1.*          # expand contractions in informal source text

# Evaluation metrics for text similarity
rouge-score==0.1.*           # ROUGE-1/2/L
sacrebleu==2.4.*             # standardized BLEU; tokenization-independent
evaluate==0.4.*              # HuggingFace evaluation harness; wraps both above
```

### 3.3 NLP — Embedding Tier

```
# Core embedding stack
sentence-transformers==3.1.*  # SBERT; primary embedding framework; wraps HuggingFace
transformers==4.44.*          # HuggingFace transformers; domain-adapted model access
tokenizers==0.19.*            # fast tokenization (HuggingFace)
torch==2.4.*                  # PyTorch backend; CPU-only unless GPU available
accelerate==0.34.*            # model device management, mixed precision
bitsandbytes==0.43.*          # quantization for running large models on consumer hardware
einops==0.8.*                 # Einstein notation tensor operations

# Domain-adapted models (download at runtime via HuggingFace Hub):
# jackaduma/SecRoBERTa         — security domain RoBERTa
# CyberPeace-Institute/SecureBERT — cybersecurity BERT
# nlpaueb/legal-bert-base-uncased — legal/regulatory text
# Note: must test all three against general models in P1; domain adaption
# is not guaranteed to outperform general models on security control text

# Classical word embeddings (mid-tier baseline between lexical and contextual)
gensim==4.3.*                 # Word2Vec, Doc2Vec, FastText, GloVe loading

# Similarity search infrastructure
faiss-cpu==1.8.*              # ANN search within analysis scripts; not the primary vector store
qdrant-client==1.11.*         # Qdrant vector store; primary production vector index
```

### 3.4 NLP — Topic Modeling

```
bertopic==0.16.*              # BERTopic: combines SBERT + UMAP + HDBSCAN for topic extraction
                              # primary topic modeling method (modular; can swap backends)
top2vec==1.0.*                # alternative topic model using Doc2Vec embeddings
                              # useful cross-check against BERTopic
# scikit-learn NMF (included above) — baseline topic model
# gensim LDA (included above) — Bayesian topic model
```

### 3.4b Data Processing at Scale

```
ray[data]==2.35.*             # Ray Data: parallel processing for 280K STRM mappings
                              # replaces dask for the heavy ETL stages; actor-based parallelism
                              # use for: parallel embedding generation, batch similarity computation,
                              #   distributed feature extraction across the STRM mapping corpus
                              # Ray Data integrates with DVC pipeline stages via custom run scripts
pyarrow==17.*                 # (above; Ray Data uses Arrow natively)
```

### 3.4c NLP — Similarity Search (Dual-Layer)

```
# Qdrant: production semantic search with metadata filtering
qdrant-client==1.11.*         # (see section 3.5 — primary vector store)

# FAISS: batch all-pairs similarity computation (P1-specific)
faiss-cpu==1.8.*              # NOT a replacement for Qdrant — a complement
                              # Qdrant: query-time filtered semantic search
                              # FAISS: P1 batch pairwise distance matrix over full 280K corpus
                              # building the 280K×candidate cosine similarity matrix for STRM
                              # calibration requires ANN search, not database queries
                              # use faiss.IndexFlatIP for exact search on embedding subsets,
                              #   faiss.IndexIVFPQ for approximate search at full scale
```

### 3.5 Graph Analysis

```
networkx==3.3.*               # graph construction, centrality, community detection, visualization
python-igraph==0.11.*         # performance at scale; 10-100x faster than networkx for large graphs
leidenalg==0.10.*             # Leiden community detection algorithm (better than Louvain)
                              # requires python-igraph
pecanpy==2.0.*                # fast node2vec implementation (10x faster than reference impl)
                              # node2vec graph embeddings for P2 topology
karateclub==1.3.*             # Graph2Vec, Role2Vec, graph-level embedding algorithms
grakel==0.1.*                 # graph kernels for graph-level ML (P2 structural classification)
pyvis==0.3.*                  # interactive network visualization; browser-based output
python-louvain==0.16.*        # Louvain community detection (networkx bridge)
```

### 3.6 Clustering and Dimensionality Reduction

```
hdbscan==0.8.*                # primary clustering method: hierarchical density-based
                              # does not require k; handles variable-density clusters
                              # generates cluster hierarchies for P2 and P5
scikit-learn                  # KMeans, AgglomerativeClustering, DBSCAN, BIRCH, MeanShift
                              # (included above; all clustering via unified API)
umap-learn==0.5.*             # UMAP: primary dimensionality reduction for embedding spaces
                              # used for: visualization, pre-clustering reduction, P5 AI governance
pacmap==0.7.*                 # PaCMAP: alternative to UMAP; preserves global structure better
                              # run both in EDA; select based on downstream clustering quality
scipy==1.13.*                 # hierarchical clustering, dendrogram, distance matrices
kneed==0.8.*                  # elbow/knee detection for choosing k in KMeans
yellowbrick==1.5.*            # ML visualization: clustering evaluation, elbow curves, silhouette
```

### 3.7 Statistical Analysis

```
scipy==1.13.*                 # t-tests, Mann-Whitney, Spearman, Pearson, chi-squared
                              # permutation tests, KS test, bootstrap
statsmodels==0.14.*           # regression, ANOVA, time series, BH/Holm FDR correction
                              # most complete multiple comparison correction implementation
pingouin==0.5.*               # primary test library: built-in effect sizes (Cohen d, η², ω²),
                              # CIs, and power analysis in single call — saves boilerplate
                              # reduces risk of missing effect size in SAP compliance
scikit-posthocs==0.9.*        # post-hoc tests (Dunn, Conover, etc.) with correction
pymc==5.16.*                  # Bayesian analysis where frequentist assumptions don't hold
                              # optional; used when data violates parametric assumptions
arviz==0.19.*                 # Bayesian visualization and diagnostics (pymc companion)
researchpy==0.3.*             # research-oriented statistical summaries; APA-format output
fisher==1.4.*                 # fast exact Fisher test implementation
```

### 3.8 Machine Learning

```
scikit-learn                  # SVM, Random Forest, Logistic Regression, pipelines (above)
xgboost==2.1.*                # gradient boosting; P1 STRM relationship classification
lightgbm==4.5.*               # faster gradient boosting; run in parallel with XGBoost
imbalanced-learn==0.12.*      # SMOTE, class weight adjustment; P1 STRM type imbalance
shap==0.46.*                  # SHAP explainability for all ML models
                              # mandatory in P1: which features drive STRM relationship prediction
lime==0.2.*                   # LIME local explanations; cross-check with SHAP
eli5==0.13.*                  # model weight inspection; text feature importance for NLP models
optuna==3.6.*                 # hyperparameter optimization; tree-structured Parzen estimator
                              # used in model selection; integrates with MLflow
joblib==1.4.*                 # parallel computation; model fitting parallelization
```

### 3.9 Data Processing

```
pandas==2.2.*                 # primary data manipulation; SCF DataFrame operations
polars==1.2.*                 # fast columnar processing for large STRM mapping dataset
                              # use polars for the 280K+ mapping operations; pandas for everything else
pyarrow==17.*                 # columnar storage format; Parquet I/O for processed datasets
numpy==2.0.*                  # numerical computation; embedding operations
dask==2024.*                  # parallel computing for EDA at scale when pandas OOMs
numba==0.60.*                 # JIT compilation for inner loops (pairwise similarity at 280K scale)
deepdiff==7.0.*               # diff two SCF versions; track what changed between releases
```

### 3.10 Visualization

```
matplotlib==3.9.*             # publication-quality static figures; primary output format
seaborn==0.13.*               # statistical visualization; distribution plots, heatmaps
plotly==5.22.*                # interactive visualization for EDA exploration
pyvis==0.3.*                  # network graph visualization (above)
wordcloud==1.9.*              # topic visualization; P5 AI governance domain word clouds
squarify==0.4.*               # treemap: visualize control coverage distribution
adjustText==1.2.*             # auto-adjust text label positions in scatter plots
altair==5.3.*                 # declarative statistical viz; grammar-of-graphics alternative
kaleido==0.2.*                # Plotly static image export for manuscript figures
```

### 3.11 Agent Framework

```
# LangGraph orchestration stack
langgraph==1.0.*              # primary agent orchestration; state machine, HITL, checkpointing
langchain==0.3.*              # base LangChain; document loaders, text splitters, retrievers
langchain-core==0.3.*         # core abstractions; runnable protocol
langchain-anthropic==0.3.*    # Anthropic LLM integration
langchain-community==0.3.*    # community integrations (Semantic Scholar, PubMed, arXiv)
langsmith==0.2.*              # LangSmith SDK; needed for API compatibility even if not using SaaS

# Anthropic SDK (direct API, for non-LangChain nodes)
anthropic==0.35.*             # direct Anthropic API; use for tight coordination loops

# Claude Agent SDK (subprocess-based subagents for isolated heavy tasks)
# Installed separately via: npm install -g @anthropic-ai/claude-code
# Python bridge: subprocess + anthropic SDK for session management

# LangGraph checkpointing backend
psycopg2-binary==2.9.*        # PostgreSQL driver for LangGraph PostgresSaver
asyncpg==0.29.*               # async PostgreSQL driver
aiopg==1.4.*                  # async PostgreSQL (alternative)

# MCP (Model Context Protocol)
mcp==1.5.*                    # MCP Python SDK; in-process tool servers
httpx-sse==0.4.*              # SSE transport for MCP
```

### 3.11b Guardrails Layer

```
# Every agent LLM output passes through guardrails before being written to state.
# Guardrails catch: hallucinated citations, fabricated statistical results,
# out-of-scope claims, prompt injection in document content.

nemo-guardrails==0.10.*       # primary guardrails runtime; Colang policy language
                              # define rails: no_fabricated_p_values, no_hallucinated_doi,
                              #   no_sap_amendment_without_interrupt, citation_format_valid
                              # rails run synchronously inside each agent node before state write

llama-guard3                  # via transformers; input/output safety classifier
                              # secondary filter: catches adversarial content in ingested
                              # regulatory documents (prompt injection defense)
                              # run on all document ingestion in ARA Compiler node

prompt-guard                  # via transformers; injection and jailbreak detection
                              # run on all externally sourced text before it enters agent context
                              # specifically: SCF Excel cells, regulatory document text,
                              #   literature paper abstracts — any text that originated outside
                              #   the research team

# Constitutional AI principles (implemented via system prompt + Instructor validation)
# No separate library needed; encode as Pydantic validators on every output model:
#   - citations must resolve (DOI or arXiv ID verifiable)
#   - statistical claims must have hypothesis_id reference
#   - effect sizes must be within plausible range for the test type
```

### 3.12 Document Extraction and Literature Indexing (Literature Agent)

```
# Literature acquisition APIs
arxiv==2.1.*                  # arXiv API client
semanticscholar==0.8.*        # Semantic Scholar API client
habanero==1.2.*               # CrossRef API client; DOI metadata resolution
pyalex==0.13.*                # OpenAlex API client — PRIMARY literature source
                              # 200M+ works, open access, structured metadata

# PDF extraction
pymupdf==1.24.*               # primary PDF text extraction; fastest and most accurate
papermage==0.15.*             # scientific PDF parsing: figures, tables, section boundaries
                              # superior to unstructured for academic PDFs
refextract==0.2.*             # reference extraction from PDFs
unstructured==0.15.*          # fallback multi-format extraction (HTML, Word, etc.)

# Citation management
bibtexparser==2.0.*           # BibTeX parsing and generation

# LlamaIndex — document indexing layer over literature corpus
llama-index==0.10.*           # LlamaIndex: document indexing, chunk management, RAG over papers
llama-index-readers-papers==0.1.*  # paper-specific readers (arXiv, PDF)
llama-index-vector-stores-qdrant==0.2.*  # LlamaIndex → Qdrant backend
                              # LlamaIndex handles: chunking strategy, node relationships,
                              #   citation-aware retrieval, section-aware querying
                              # LangChain handles: agent tool calling, workflow integration
                              # The two complement: LlamaIndex for indexing/retrieval quality;
                              #   LangChain for agent orchestration
```

### 3.12b Local Inference (Domain Model Serving)

```
# For running domain-adapted security/legal models locally (no GPU required)
llama-cpp-python==0.2.*       # llama.cpp Python bindings; CPU inference of GGUF models
                              # use case: run quantized SecureBERT / legal-bert locally
                              # for embedding generation without GPU dependency
                              # GGUF format: 4-bit quantized models run on MacBook-class hardware
                              # trigger: if SBERT general models score below threshold in P1 EDA
                              #   → download quantized domain model → run via llama.cpp

# SGLang (conditional — only if batched local inference becomes bottleneck)
# sglang==0.2.*               # RadixAttention for efficient batch inference
                              # activate if llama.cpp throughput insufficient for embedding scale
```

### 3.13 Data Versioning and Experiment Tracking

```
# Data versioning
dvc==3.51.*                   # primary data versioning; local filesystem remote
dvc-gdrive                    # optional: Google Drive remote as backup

# Experiment tracking
mlflow==2.15.*                # primary experiment tracker; fully self-hosted
mlflow[extras]                # additional backends and integrations
optuna-integration[mlflow]    # MLflow-Optuna integration for hyperparameter tracking

# Scientific experiment wrapper (custom, built on MLflow):
# src/infrastructure/tracking/scientific_experiment.py
# Enforces: pre-registration before run creation, effect size logging,
# null result entries, DVC data version linkage via tags
```

### 3.14 Observability

```
# OpenTelemetry instrumentation (OTel GenAI semantic conventions, stable 2026)
opentelemetry-api==1.27.*
opentelemetry-sdk==1.27.*
opentelemetry-exporter-otlp-proto-grpc==1.27.*     # export to Langfuse OTLP endpoint
opentelemetry-exporter-otlp-proto-http==1.27.*     # HTTP alternative
opentelemetry-instrumentation-anthropic==0.33.*    # auto-instrument Anthropic API calls
openinference-instrumentation-langchain==0.1.*     # LangChain OTel bridge

# Langfuse (self-hosted; telemetry backend)
langfuse==2.0.*               # Python SDK; trace/span creation, evaluation
# Deployment: docker-compose (Langfuse + Postgres + ClickHouse)

# Arize Phoenix (self-hosted; statistical evaluation + embedding drift)
arize-phoenix==5.0.*          # LLM evals, cluster analysis
arize-phoenix-otel==0.5.*     # OTel bridge
                              # ADDITIONAL USE CASE (from skills assessment):
                              # Embedding drift detection — when SCF releases a new quarterly
                              # version, existing Qdrant embeddings may degrade silently.
                              # Phoenix monitors embedding cluster stability; alerts when
                              # cosine similarity distribution shifts > threshold.
                              # Run Phoenix drift check as a DVC stage after each SCF update.
```

### 3.15 Scientific Enforcement Layer (Custom — No Off-Shelf Option)

```
# JSON schema validation (SAP, hypothesis register)
jsonschema==4.23.*            # (above)
cerberus==1.3.*               # alternative schema validation; more readable rules

# Git operations (pre-registration)
gitpython==3.1.*              # Git repo operations; commit hash retrieval for pre-registration
                              # links hypothesis register commits to SAP analysis specs

# Trusted timestamping (RFC 3161)
python-rfc3161-ng==0.1.*      # RFC 3161 trusted timestamp tokens
# External TSA: FreeTSA (https://freetsa.org) — free, publicly operated

# Scientific data validation
great-expectations==0.18.*    # data quality assertions for raw and processed datasets
                              # validate SCF schema before any analysis runs
pandera==0.20.*               # DataFrame schema validation; typed column assertions

# Diff and audit
deepdiff==7.0.*               # (above) SAP version comparison; detect unauthorized amendments

# Datetime with timezone
pendulum==3.0.*               # timezone-aware timestamp handling; lab notebook entries
```

### 3.16 Configuration Management

```
hydra-core==1.3.*             # hierarchical configuration; compose configs from YAML files
omegaconf==2.3.*              # config composition engine (hydra dependency)
python-dotenv==1.0.*          # .env file loading for secrets/API keys
```

### 3.17 Infrastructure and Utilities

```
# Async
anyio==4.4.*                  # async I/O abstraction layer
asyncio                       # stdlib

# Retry and resilience
tenacity==9.0.*               # retry with exponential backoff; all API calls
circuitbreaker==2.0.*         # circuit breaker pattern for external service calls

# Caching
diskcache==5.6.*              # disk-based cache; embedding cache across sessions
                              # avoids re-embedding 280K controls on every run
cachetools==5.4.*             # in-memory cache with TTL/LRU eviction

# Parallel processing
joblib==1.4.*                 # (above)
concurrent.futures            # stdlib; ThreadPoolExecutor for I/O bound parallelism
multiprocessing               # stdlib; ProcessPoolExecutor for CPU bound parallelism

# Logging
loguru==0.7.*                 # structured logging; replaces stdlib logging
                              # JSON sink for machine-readable log aggregation

# Console output
rich==13.7.*                  # rich terminal output (per CLAUDE.md)
tqdm==4.66.*                  # progress bars for long-running operations
typer==0.12.*                 # CLI interface for research pipeline commands

# String and text utilities
more-itertools==10.3.*        # extended itertools
toolz==0.12.*                 # functional programming utilities
python-slugify==8.0.*         # URL/filename safe slugs for artifact naming

# Hashing and cryptography
hashlib                       # stdlib; SHA256 for data integrity
cryptography==42.*            # cryptographic operations; RFC 3161 timestamp verification

# License compliance
pip-licenses==5.0.*           # audit all installed package licenses
                              # CC BY-ND constraint requires knowing what derivatives we ship
```

### 3.18 Testing

```
pytest==8.2.*                 # test framework
pytest-asyncio==0.23.*        # async test support
pytest-cov==5.0.*             # coverage reporting
pytest-mock==3.14.*           # mocking
pytest-xdist==3.5.*           # parallel test execution
hypothesis==6.108.*           # property-based testing; statistical invariant testing
factory-boy==3.3.*            # test fixture factories for SCF control objects
responses==0.25.*             # mock HTTP responses
time-machine==2.14.*          # time freezing for timestamp-dependent tests
```

### 3.19 Code Quality

```
black==24.*                   # code formatter (per CLAUDE.md)
ruff==0.5.*                   # linter + formatter (per CLAUDE.md)
mypy==1.10.*                  # static type checking
pre-commit==3.7.*             # Git hook management
nbstripout==0.7.*             # strip notebook outputs before git commit
bandit==1.7.*                 # security linting
safety==3.2.*                 # dependency vulnerability scanning
```

### 3.20 Notebook and Reproducibility

```
jupyter==1.0.*                # notebook environment
nbformat==5.10.*              # programmatic notebook manipulation
nbconvert==7.16.*             # notebook → script/HTML/PDF
papermill==2.6.*              # parameterized notebook execution
                              # critical: agents drive EDA via papermill, not direct execution
jupytext==1.16.*              # notebook ↔ Python script sync; enables version control of notebooks
```

---

## 4. Agent Team Architecture

### 4.1 Agent Roster

| Agent | Tier | Primary Responsibility | LLM | Backed By |
|-------|------|----------------------|-----|-----------|
| Orchestrator | Coordinator | State routing, gate enforcement, human interrupt dispatch; two-loop autoresearch backbone | Claude Sonnet (direct API) | Autoresearch skill |
| Literature Agent | Specialist | Systematic search, paper download, extraction, synthesis; LlamaIndex indexing | Claude Sonnet (Agent SDK subagent) | LlamaIndex + OpenAlex + papermage |
| Data Steward Agent | Specialist | Data acquisition, SHA256 verification, DVC registration, MANIFEST | Deterministic + Claude Haiku | DVC + great-expectations |
| EDA Agent | Specialist | Exploratory notebooks via papermill, pattern surfacing, Ray Data parallel processing | Claude Sonnet (Agent SDK subagent) | papermill + Ray Data + FAISS |
| Hypothesis Formalizer | Specialist | EDA observations → typed SAP hypothesis entries via Instructor | Claude Sonnet (direct API) | Instructor + DSPy-optimized prompts |
| Statistical Analyst | Specialist | Pre-registered hypothesis testing, effect sizes, CIs | Claude Sonnet (Agent SDK subagent) | pingouin + statsmodels |
| QA Agent | Specialist | ARA Rigor Reviewer rubric adapted to SAP compliance; 6-dimension epistemic scoring | Claude Sonnet (direct API) | ARA Rigor Reviewer skill |
| ARA Research Manager | Provenance | Post-node provenance recording; decisions, pivots, dead ends → lab notebook | Deterministic + Claude Haiku | ARA Research Manager skill |
| ARA Compiler | Ingestion | SCF + framework sources → structured ARA knowledge artifacts | Claude Sonnet (Agent SDK subagent) | ARA Compiler skill |
| Guardrails Agent | Safety | Wraps every agent output; catches hallucinated citations, fabricated statistics, injection | Deterministic | NeMo Guardrails + LlamaGuard + Prompt Guard |
| Code Reviewer Agent | Specialist | Review confirmatory scripts before merge; SAP header validation | Claude Sonnet (direct API) | — |
| Report Generator | Specialist | Publication-ready manuscript sections, LaTeX formatting, figure captions | Claude Opus (direct API) | ml-paper-writing + academic-plotting skills |

### 4.2 Agent Tool Surfaces (MCP Servers, In-Process)

Each agent has access to only the tools it needs. Tool surface is narrow by design.

```
LITERATURE AGENT tools:
  - literature_search(query, databases, date_range) → List[PaperMetadata]
  - fetch_paper(doi_or_arxiv_id) → PaperContent
  - extract_claims(paper_content) → List[Claim]
  - update_synthesis(claims) → None
  - read_search_strategy() → SearchStrategy
  - write_search_log(entry) → None

DATA STEWARD AGENT tools:
  - download_file(url, destination) → DownloadResult
  - compute_sha256(path) → str
  - register_in_manifest(entry: ManifestEntry) → None
  - dvc_add(path) → DVCPointer
  - dvc_push() → None
  - read_manifest() → List[ManifestEntry]

EDA AGENT tools:
  - run_notebook(template_path, parameters, output_path) → NotebookResult
  - read_dataset(dvc_pointer) → DataFrameRef
  - generate_figure(spec) → FigurePath
  - append_eda_finding(finding: EDAFinding) → None
  - read_codebook() → Codebook

HYPOTHESIS FORMALIZER tools:
  - read_eda_findings() → List[EDAFinding]
  - read_sap() → SAP
  - write_hypothesis(hypothesis: HypothesisEntry) → HypothesisID
  - validate_sap() → SAPValidationResult
  - read_theoretical_framework() → TheoreticalFramework

STATISTICAL ANALYST tools:
  - read_dataset(dvc_pointer, split='test') → DataFrameRef
  - load_hypothesis(hypothesis_id) → HypothesisEntry
  - run_analysis_script(script_path) → AnalysisResult
  - log_result(result: StatisticalResult) → None
  - write_null_result(null_result: NullResult) → None

QA AGENT tools:
  - read_result(result_id) → StatisticalResult
  - validate_effect_size_present(result) → ValidationResult
  - validate_ci_present(result) → ValidationResult
  - validate_correction_applied(results: List, sap_correction_method) → ValidationResult
  - validate_sap_compliance(result, hypothesis_id) → ValidationResult
  - write_qa_report(report: QAReport) → None

CODE REVIEWER AGENT tools:
  - read_script(path) → ScriptContent
  - read_sap_entry(hypothesis_id) → HypothesisEntry
  - check_script_header(script_content) → HeaderValidation
  - post_review_comment(review: CodeReview) → None

LAB NOTEBOOK AGENT tools (deterministic, no LLM):
  - append_entry(entry: NotebookEntry) → None
  - read_last_entry() → NotebookEntry
  - verify_chronological_order(entry) → bool

REPORT GENERATOR tools:
  - read_all_results() → List[StatisticalResult]
  - read_null_results() → List[NullResult]
  - read_theoretical_framework() → TheoreticalFramework
  - read_contribution_statement() → ContributionStatement
  - write_manuscript_section(section: ManuscriptSection) → None
```

### 4.3 Typed State Schema (LangGraph)

```python
from typing import Annotated, Optional
from pydantic import BaseModel
from langgraph.graph.message import add_messages

class ResearchState(BaseModel):
    # Lifecycle
    phase: str                          # current workflow phase
    phase_history: list[str]            # all phases visited
    interrupt_reason: Optional[str]     # what triggered current interrupt
    
    # Protocol documents
    research_questions: Optional[str]   # path to 00_research_questions.md
    theoretical_framework: Optional[str]
    sap_path: Optional[str]
    sap_hash: Optional[str]             # hash at pre-registration time
    sap_locked: bool = False
    
    # Literature
    search_runs: list[SearchRun] = []
    papers_included: int = 0
    synthesis_complete: bool = False
    
    # Data
    manifest_entries: list[ManifestEntry] = []
    dvc_lock_hash: Optional[str]        # dvc.lock hash at analysis time
    data_acquisition_complete: bool = False
    
    # Hypotheses
    hypothesis_register: list[HypothesisEntry] = []
    preregistration_commit: Optional[str]   # git commit hash
    preregistration_timestamp: Optional[str]
    
    # Analysis
    eda_complete: bool = False
    eda_findings: list[EDAFinding] = []
    analyses_run: list[AnalysisResult] = []
    null_results: list[NullResult] = []
    qa_passed: bool = False
    qa_report: Optional[QAReport]
    
    # Human decisions (logged at each gate)
    human_decisions: list[HumanDecision] = []
    
    # Agent messages (LangGraph message reducer)
    messages: Annotated[list, add_messages] = []
```

---

## 5. LangGraph Workflow State Machine

### 5.1 Node Definitions

```
Nodes (in topological order):

PROTOCOL_POPULATION
  Input:  constitutions (SCF_CONSTITUTION.md, RISK_CONSTITUTION.md, FRAMEWORK_RELATIONSHIPS.md)
  Output: populated protocol/00-02 documents
  Agent:  Protocol Agent (Claude Sonnet, direct API)
  Tools:  read_constitution, write_protocol_section

GATE_1_RESEARCH_QUESTIONS [interrupt]
  Type:   Human approval gate
  Payload: populated research questions + theoretical framework
  Decision: approve / request_revision
  If approved: → LITERATURE_SEARCH
  If revision: → PROTOCOL_POPULATION (with feedback)

LITERATURE_SEARCH
  Input:  approved research questions, search strategy template
  Output: papers corpus, synthesis.md populated
  Agent:  Literature Agent (Claude Sonnet, Agent SDK subagent)
  Tools:  literature_search, fetch_paper, extract_claims, update_synthesis

GAP_VALIDATION
  Input:  literature synthesis
  Output: contribution statement, gap statement
  Agent:  Protocol Agent (direct API)
  Tools:  read_synthesis, write_contribution_statement

GATE_2_PROTOCOL_LOCK [interrupt]
  Type:   Human approval gate
  Payload: complete protocol (RQs + framework + contribution + gap)
  Decision: approve / request_revision
  If approved: → DATA_ACQUISITION
  If revision: back to appropriate node

DATA_ACQUISITION
  Input:  approved research protocol, data source list
  Output: all raw datasets acquired, MANIFEST populated, DVC-tracked
  Agent:  Data Steward (deterministic + Haiku)
  Tools:  download_file, compute_sha256, register_in_manifest, dvc_add

CODEBOOK_POPULATION
  Input:  acquired datasets
  Output: data/codebook.md fully populated
  Agent:  Data Steward + Protocol Agent
  Tools:  inspect_dataset, write_codebook_entry

EDA_EXECUTION
  Input:  codebook, DVC-tracked datasets, EDA notebook templates
  Output: EXP_ prefixed figures/tables, EDA findings list
  Agent:  EDA Agent (Claude Sonnet, Agent SDK subagent)
  Tools:  run_notebook (via papermill), read_dataset, append_eda_finding
  Note:   papermill runs parameterized notebooks; outputs logged to MLflow

HYPOTHESIS_FORMALIZATION
  Input:  EDA findings, theoretical framework, literature synthesis
  Output: typed HypothesisEntry objects in hypothesis register
  Agent:  Hypothesis Formalizer (direct API)
  Tools:  read_eda_findings, write_hypothesis, validate_sap

SAP_POPULATION
  Input:  formalized hypotheses
  Output: protocol/03_statistical_analysis_plan.md fully populated
  Agent:  Protocol Agent + Hypothesis Formalizer
  Note:   primary analysis designated here; one only

POWER_ANALYSIS
  Input:  SAP with effect size assumptions
  Output: required N, powered flag for each hypothesis
  Agent:  Statistical Analyst (direct API)
  Tools:  run_power_analysis (pingouin)

PREREGISTRATION
  Input:  locked SAP + hypothesis register + DVC lock hash
  Output: signed commit to protected branch, RFC 3161 timestamp
  Agent:  Deterministic (no LLM; git operations only)
  Tools:  commit_preregistration, request_rfc3161_timestamp

GATE_3_SAP_LOCK [interrupt]
  Type:   Human approval gate — CRITICAL; SAP immutable after this point
  Payload: complete SAP, power analysis results, preregistration commit
  Decision: approve / request_revision
  If approved: → CONFIRMATORY_ANALYSIS
  If revision: SAP amendment logged, amendment commit timestamped, back to SAP_POPULATION

CONFIRMATORY_ANALYSIS
  Input:  locked SAP, DVC test split (set aside at GATE_3)
  Output: StatisticalResult objects for every hypothesis
  Agent:  Statistical Analyst (Agent SDK subagent; isolated filesystem access)
  Enforcement: SAP compliance gate node runs BEFORE any test; fails if hypothesis not registered
  Note:   test set touched ONCE per hypothesis; re-runs logged in lab notebook

QA_VALIDATION
  Input:  all StatisticalResult objects
  Output: QAReport (pass/fail per result, issues list)
  Agent:  QA Agent (direct API)
  Checks:
    - effect size present for every result
    - CI present for every result
    - multiple comparison correction applied per SAP specification
    - null results logged for every non-rejected H0
    - analysis scripts match SAP hypothesis IDs

GATE_4_RESULTS_REVIEW [interrupt]
  Type:   Human approval gate
  Payload: all results + QA report + null results
  Decision: approve / flag_issues
  If approved: → REPORT_GENERATION
  If issues: QA Agent re-runs flagged analyses (with lab notebook entry)

REPORT_GENERATION
  Input:  approved results, null results, theoretical framework, contribution statement
  Output: manuscript sections in manuscripts/
  Agent:  Report Generator (Claude Opus; highest capability for writing)
  Tools:  read_all_results, write_manuscript_section

GATE_5_REPORT_RELEASE [interrupt]
  Type:   Human approval gate — final; researcher reads and approves manuscript
  Payload: complete manuscript
  Decision: approve_release / request_revision

COMPLETE
  Terminal node; log final state to lab notebook
```

### 5.2 Edges

```
PROTOCOL_POPULATION → GATE_1
GATE_1 (approved) → LITERATURE_SEARCH
GATE_1 (revision) → PROTOCOL_POPULATION
LITERATURE_SEARCH → GAP_VALIDATION
GAP_VALIDATION → GATE_2
GATE_2 (approved) → DATA_ACQUISITION
GATE_2 (revision) → PROTOCOL_POPULATION
DATA_ACQUISITION → CODEBOOK_POPULATION
CODEBOOK_POPULATION → EDA_EXECUTION
EDA_EXECUTION → HYPOTHESIS_FORMALIZATION
HYPOTHESIS_FORMALIZATION → SAP_POPULATION
SAP_POPULATION → POWER_ANALYSIS
POWER_ANALYSIS → PREREGISTRATION
PREREGISTRATION → GATE_3
GATE_3 (approved) → CONFIRMATORY_ANALYSIS
GATE_3 (revision) → SAP_POPULATION  [amendment logged in lab notebook]
CONFIRMATORY_ANALYSIS → QA_VALIDATION
QA_VALIDATION (pass) → GATE_4
QA_VALIDATION (fail) → GATE_4  [fails surface in QA report; human decides]
GATE_4 (approved) → REPORT_GENERATION
GATE_4 (flag_issues) → CONFIRMATORY_ANALYSIS  [re-run flagged only]
REPORT_GENERATION → GATE_5
GATE_5 (approved) → COMPLETE
GATE_5 (revision) → REPORT_GENERATION
```

---

## 6. Data Architecture

### 6.1 DVC Pipeline Stages

```
# dvc.yaml

stages:
  acquire_scf:
    cmd: python src/data/acquire/scf.py
    deps: [configs/data_sources.yaml]
    outs: [data/01-raw/scf/]
    frozen: true           # raw data never regenerated; only acquired once

  acquire_nist_oscal:
    cmd: python src/data/acquire/nist_oscal.py
    outs: [data/01-raw/nist_oscal/]
    frozen: true

  acquire_cis:
    cmd: python src/data/acquire/cis_controls.py
    outs: [data/01-raw/cis/]
    frozen: true

  acquire_attck:
    cmd: python src/data/acquire/attck.py
    outs: [data/01-raw/attck/]
    frozen: true

  parse_scf:
    cmd: python src/data/parse/scf_parser.py
    deps: [data/01-raw/scf/, src/data/parse/scf_parser.py]
    outs: [data/03-processed/scf_controls.parquet,
           data/03-processed/strm_mappings.parquet]

  parse_frameworks:
    cmd: python src/data/parse/framework_parser.py
    deps: [data/01-raw/nist_oscal/, data/01-raw/cis/]
    outs: [data/03-processed/frameworks.parquet]

  validate_data:
    cmd: python src/data/validate/schema_check.py
    deps: [data/03-processed/, src/data/validate/]
    outs: [data/03-processed/validation_report.json]

  build_embeddings:
    cmd: python src/analysis/nlp/embed_controls.py
    deps: [data/03-processed/scf_controls.parquet, configs/embedding.yaml]
    outs: [data/03-processed/embeddings/]
    # DVC caches embeddings: re-run only when controls or model config changes

  build_vector_index:
    cmd: python src/infrastructure/vector_store/build_index.py
    deps: [data/03-processed/embeddings/]
    outs: [data/03-processed/qdrant_snapshot/]

  create_splits:
    cmd: python src/data/splits.py
    deps: [data/03-processed/strm_mappings.parquet, configs/splits.yaml]
    outs: [data/splits/train.parquet, data/splits/val.parquet,
           data/splits/test.parquet]
    # test split set aside at GATE_3; not used until GATE_3 approved
```

### 6.2 Qdrant Collection Schema

```
Collection: scf_controls
  Vector: dense_embedding (1024-dim, all-mpnet-base-v2)
  Sparse vector: bm25_sparse (via fastembed sparse model)
  Payload fields (indexed):
    control_id: keyword          # e.g. "GOV-01"
    domain_code: keyword         # e.g. "GOV"
    domain_name: keyword
    scf_version: keyword         # pinned version
    maturity_level: integer      # L0-L5
    risk_categories: list[keyword]  # R-AC, R-AM, etc.
    mcr_dsr: keyword             # "MCR" or "DSR"
    frameworks_mapped: list[keyword]  # which external frameworks map to this control

Collection: strm_mappings
  Vector: mapping_embedding (concatenation of control_a + control_b embeddings)
  Payload:
    mapping_id: keyword
    source_control_id: keyword
    target_framework: keyword
    target_control_id: keyword
    relationship_type: keyword   # ⊂ ∩ = ⊃ ∅
    strength_score: float        # 1-10
    scf_version: keyword

Collection: literature_papers
  Vector: abstract_embedding (768-dim)
  Payload:
    doi: keyword
    title: text
    year: integer
    included: boolean
    relevance_score: float
```

---

## 7. GitHub Architecture

### 7.1 Branch Strategy

```
main                    — production research record; protected; merges require PR
  preregistration       — PROTECTED; SAP + hypothesis register; no force-push; signed commits only
  feature/*             — agent-generated analysis branches; one per analysis module
  eda/*                 — EDA notebooks; merged before preregistration
  amendment/*           — SAP amendments; require PR with human review trail
```

### 7.2 Branch Protection Rules

```
Branch: preregistration
  - Require signed commits
  - No force-push (ever)
  - No deletion
  - Require PR for all changes (creates amendment audit trail)
  - Required status checks: sap-schema-validation, hypothesis-register-validation

Branch: main
  - Require PR from feature/*
  - Required status checks: test-suite, data-integrity, sap-compliance
  - No direct push
```

### 7.3 GitHub Actions Workflows

```yaml
# .github/workflows/sap-validation.yml
# Trigger: push to main, preregistration; PR to main
# Purpose: validate SAP JSON schema; validate hypothesis register schema
# Fails: if sap.json does not validate against sap_schema.json
#        if any confirmatory script lacks a corresponding SAP entry
#        if effect_size or confidence_interval fields absent from any result

# .github/workflows/data-integrity.yml
# Trigger: push to main
# Purpose: verify SHA256 hashes in MANIFEST.md match DVC-tracked files
#          verify dvc.lock is committed and up to date
# Fails: if any hash mismatch; if dvc.lock missing

# .github/workflows/test-suite.yml
# Trigger: all pushes, all PRs
# Purpose: run pytest; fail on any test failure; report coverage
# Threshold: 80% line coverage on src/

# .github/workflows/preregistration.yml
# Trigger: push to preregistration branch
# Purpose: validate SAP completeness before allowing analysis pipeline to run
#          compute and store RFC 3161 timestamp token
#          verify DVC data version hash is embedded in SAP

# .github/workflows/lab-notebook-check.yml
# Trigger: PR to main with analysis results
# Purpose: verify a lab notebook entry exists for each analysis artifact in the PR
# Fails: if results/ contains new files without corresponding lab_notebook.md entries

# .github/workflows/analysis-pipeline.yml
# Trigger: manual dispatch only (human-initiated after GATE_3)
# Purpose: run the LangGraph confirmatory analysis pipeline
#          verify SAP lock before any analysis job executes
#          emit structured logs to Langfuse
```

### 7.4 Pre-commit Hooks

```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks: [black]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks: [ruff, ruff-format]

  - repo: https://github.com/kynan/nbstripout
    rev: 0.7.1
    hooks: [nbstripout]  # strips all notebook outputs before commit

  - repo: local
    hooks:
      - id: no-data-files
        name: Prohibit data files in git
        entry: python scripts/hooks/no_data_files.py
        # rejects: *.parquet, *.csv >100KB, *.pkl, *.npy, *.h5, *.bin

      - id: validate-sap-schema
        name: Validate SAP JSON schema
        entry: python scripts/hooks/validate_sap.py
        files: ^protocol/sap\.json$

      - id: validate-hypothesis-register
        name: Validate hypothesis register schema
        entry: python scripts/hooks/validate_hypothesis_register.py
        files: ^protocol/hypothesis_register\.json$

      - id: exploratory-label-check
        name: Verify exploratory scripts have EXPLORATORY header
        entry: python scripts/hooks/check_exploratory_label.py
        files: ^analysis/01-exploratory/.*\.py$

      - id: confirmatory-sap-header
        name: Verify confirmatory scripts have SAP header
        entry: python scripts/hooks/check_sap_header.py
        files: ^analysis/02-confirmatory/.*\.py$

      - id: no-hardcoded-seeds
        name: No hardcoded random seeds outside configs/seeds.yaml
        entry: python scripts/hooks/check_seeds.py
```

---

## 8. Observability Architecture

### 8.1 Service Topology (All Self-Hosted)

```
┌─────────────────────────────────────────────┐
│              OBSERVABILITY STACK             │
│                                             │
│  ┌─────────────┐    ┌──────────────────┐   │
│  │  Langfuse   │    │  Arize Phoenix   │   │
│  │  (port 3000)│    │  (port 6006)     │   │
│  │             │    │                  │   │
│  │  - LLM      │    │  - Embedding     │   │
│  │    traces   │    │    drift         │   │
│  │  - Agent    │    │  - Cluster       │   │
│  │    spans    │    │    analysis      │   │
│  │  - Human    │    │  - LLM evals     │   │
│  │    annots   │    │                  │   │
│  └──────┬──────┘    └────────┬─────────┘   │
│         │                   │              │
│         └────────┬──────────┘              │
│                  │ OTel OTLP               │
│  ┌───────────────▼─────────────────────┐  │
│  │        Research Pipeline            │  │
│  │  (OTel instrumented; emits spans    │  │
│  │   via opentelemetry-sdk)            │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  ┌─────────────┐    ┌──────────────────┐   │
│  │   MLflow    │    │   Grafana        │   │
│  │  (port 5000)│    │   (port 3001)    │   │
│  │             │    │   (optional)     │   │
│  │  - Exp runs │    │  - Dashboard     │   │
│  │  - Params   │    │    aggregation   │   │
│  │  - Metrics  │    │                  │   │
│  │  - Artifacts│    │                  │   │
│  └─────────────┘    └──────────────────┘   │
└─────────────────────────────────────────────┘
```

### 8.2 Custom OTel Span Attributes for Scientific Tracing

```python
# Attributes added to every span in the research pipeline
# (beyond standard OTel GenAI conventions)

SCIENTIFIC_SPAN_ATTRIBUTES = {
    # Data lineage
    "research.dvc_lock_hash": str,         # dvc.lock SHA256 at run time
    "research.dataset_version": str,       # SCF version string (e.g., "2024.4")
    "research.data_split": str,            # "train" / "val" / "test"
    
    # Hypothesis provenance
    "research.hypothesis_id": str,         # e.g., "H1.3"
    "research.analysis_mode": str,         # "exploratory" / "confirmatory"
    "research.preregistration_commit": str,
    
    # Statistical results (on analysis spans)
    "research.test_name": str,
    "research.p_value": float,
    "research.effect_size": float,
    "research.effect_size_measure": str,   # cohen_d / eta_sq / etc.
    "research.ci_lower": float,
    "research.ci_upper": float,
    "research.n_tests_in_family": int,
    "research.correction_method": str,
    
    # Human decisions (on gate spans)
    "research.gate_id": str,               # "GATE_1" through "GATE_5"
    "research.human_decision": str,        # "approved" / "revision_requested"
    "research.decision_timestamp": str,
}
```

---

## 9. Scientific Enforcement Layer

### 9.1 SAP JSON Schema (not Markdown)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12",
  "type": "object",
  "required": ["version", "locked_at", "primary_analysis", "hypotheses",
               "multiple_comparison_families", "data_splits", "missing_data_protocol"],
  "properties": {
    "version": {"type": "string"},
    "locked_at": {"type": "string", "format": "date-time"},
    "dvc_lock_hash": {"type": "string"},    // data version at lock time
    "preregistration_commit": {"type": "string"},
    "primary_analysis": {
      "type": "object",
      "required": ["hypothesis_id", "outcome_measure", "statistical_test", "decision_rule"],
      "properties": {
        "hypothesis_id": {"type": "string", "pattern": "^H[0-9]+\\.[0-9]+$"},
        "outcome_measure": {"type": "string"},
        "statistical_test": {"type": "string"},
        "decision_rule": {"type": "string"}
      }
    },
    "hypotheses": {
      "type": "array",
      "items": {
        "required": ["id", "h1", "h0", "test", "effect_size_measure",
                     "minimum_meaningful_effect", "alpha", "power",
                     "required_n", "available_n", "powered",
                     "correction_family", "data_split", "script"],
        "properties": {
          "id": {"type": "string", "pattern": "^H[0-9]+\\.[0-9]+$"},
          "h1": {"type": "string"},
          "h0": {"type": "string"},
          "test": {"type": "string"},
          "effect_size_measure": {"type": "string"},
          "minimum_meaningful_effect": {"type": "number"},
          "alpha": {"type": "number", "maximum": 0.05},
          "power": {"type": "number", "minimum": 0.80},
          "required_n": {"type": "integer"},
          "available_n": {"type": "integer"},
          "powered": {"type": "boolean"},
          "correction_family": {"type": "string"},
          "data_split": {"type": "string", "enum": ["train", "val", "test"]},
          "script": {"type": "string"}
        }
      }
    }
  }
}
```

### 9.2 Scientific Experiment MLflow Wrapper

```python
# src/infrastructure/tracking/scientific_experiment.py
# Custom wrapper enforcing scientific rigor at the experiment tracking layer

class ScientificExperiment:
    """
    MLflow wrapper that enforces:
    - pre-registration before run creation (for confirmatory runs)
    - effect size logging on all confirmatory runs
    - CI logging on all confirmatory runs
    - null result entries for all non-rejected H0
    - DVC data version linkage
    """
    def start_confirmatory_run(self, hypothesis_id: str) -> None:
        # validates SAP entry exists for this hypothesis_id
        # validates preregistration commit exists
        # validates data DVC hash matches SAP-registered hash
        # raises SAPViolationError if any check fails

    def log_statistical_result(self, result: StatisticalResult) -> None:
        # enforces: effect_size present
        # enforces: confidence_interval present
        # enforces: p_value present
        # raises ResultIncompleteError if any required field missing

    def close_hypothesis(self, hypothesis_id: str, rejected: bool) -> None:
        # if not rejected: creates null result entry in results/null_results/
        # logs to MLflow with null_result=True tag
```

---

## 10. Infrastructure Topology

### 10.1 Local Services (All on Localhost)

```
PostgreSQL (port 5432)      — LangGraph state checkpointing
MLflow tracking server (port 5000)  — experiment tracking
Langfuse (port 3000)        — agent trace and annotation backend
  └── Postgres (5433)       — Langfuse metadata
  └── ClickHouse (8123)     — Langfuse event storage
Arize Phoenix (port 6006)   — embedding evaluation
Qdrant (port 6333/6334)     — vector store (REST / gRPC)
```

### 10.2 Docker Compose (infrastructure only; research code runs native)

```yaml
# docker-compose.infrastructure.yml
# Starts: postgres, langfuse, clickhouse, phoenix, qdrant, mlflow
# Research pipeline runs natively (not in Docker) for filesystem access
```

### 10.3 Configuration Management

```
configs/
  agents.yaml           — LLM model selection per agent, temperature, max tokens
  data_sources.yaml     — upstream source URLs, expected SHA256s
  embedding.yaml        — model choice, batch size, cache path
  splits.yaml           — train/val/test ratios, stratification key, random seed
  analysis.yaml         — statistical test parameters, alpha, power targets
  seeds.yaml            — ALL random seeds; single source of truth
  infrastructure.yaml   — service ports, connection strings (no secrets)

.env                    — API keys, passwords (never committed)
```

---

## 11. Testing Architecture

```
tests/
  unit/
    test_sap_schema.py          — SAP JSON schema validation
    test_hypothesis_register.py — hypothesis register schema
    test_statistical_result.py  — StatisticalResult pydantic model
    test_scf_parser.py          — SCF Excel/OSCAL parsing
    test_scientific_experiment.py — MLflow wrapper enforcement

  integration/
    test_dvc_pipeline.py        — DVC stage execution
    test_qdrant_search.py       — vector store round-trip
    test_langgraph_gates.py     — interrupt/resume at each gate
    test_agent_tools.py         — MCP tool server responses

  property_based/
    test_data_invariants.py     — hypothesis: all controls have valid domain codes
                                — hypothesis: all STRM scores in [1,10]
                                — hypothesis: no duplicate control IDs

  scientific/
    test_multiple_comparison.py — verify correction applied when N tests > 1
    test_effect_size_present.py — verify every result has effect size
    test_null_result_logged.py  — verify null results have entries
    test_sap_compliance.py      — verify no confirmatory script runs without SAP entry
```

---

## 12. Phase 2 Conditional Stack

These components are not built in Phase 1. Each has a defined trigger — a specific finding from the Phase 1 research that would activate the need.

| Component | Trigger | Stack |
|-----------|---------|-------|
| Domain model fine-tuning | P1 EDA shows general SBERT models below 0.70 F1 on STRM type classification | PEFT + LoRA + sentence-transformers fine-tuning on SCF control pairs |
| Quantized local inference | llama.cpp throughput < 100 embeddings/sec on target hardware | SGLang with GPTQ/AWQ quantized SecureBERT |
| GPU acceleration | Embedding generation > 4 hours for full corpus | bitsandbytes + Flash Attention + accelerate |
| Distributed EDA | Ray Data single-node OOM on 280K × embedding matrix | Ray cluster (2-4 nodes) |
| Agent prompt optimization | QA Agent scoring < 3.5/5 on rigor dimensions after 10 runs | DSPy optimization loop against rigor metric |
| A-Evolve agent improvement | Any agent consistently underperforms over 20+ runs | A-Evolve evolution cycles with git-versioned rollback |
| Knowledge distillation | Fine-tuned domain model too large for local inference | Knowledge distillation to smaller student model |

Each trigger is a measurable condition from Phase 1 analysis. No Phase 2 component is built speculatively.

---

## 13. What Must Be Custom-Built vs. Available Off-Shelf

| Component | Status | Estimated LoC |
|-----------|--------|--------------|
| SAP JSON schema + validator | Build | 200 |
| Hypothesis register schema + validator | Build | 150 |
| ScientificExperiment MLflow wrapper | Build | 600 |
| LangGraph SAP compliance gate node | Build | 150 |
| QA Agent multiple comparison checker | Build | 200 |
| RFC 3161 timestamp Git hook | Build | 100 |
| GitHub Actions scientific enforcement | Build | 250 |
| Lab notebook auto-generation | Build | 150 |
| OTel custom span attributes wrapper | Build | 200 |
| Qdrant hybrid search wrapper | Build | 300 |
| FAISS batch all-pairs P1 wrapper | Build | 200 |
| Ray Data STRM parallel pipeline | Build | 300 |
| Custom OSCAL pydantic parser | Build | 400 |
| DVC pipeline stages | Build | 300 |
| MCP in-process tool servers (12 agents × avg 5 tools) | Build | 1,500 |
| LangGraph state schema | Build | 300 |
| LangGraph node implementations (12 agents) | Build | 2,200 |
| Guardrails layer integration (NeMo + LlamaGuard + PromptGuard) | Build | 200 |
| **TOTAL CUSTOM BUILD** | | **~7,200 LoC** |

All other components are installed dependencies. The 7,200 lines is focused, non-complex Python — schemas, validators, data models, and thin glue code. The expansion from v0.1 (6,500) reflects 3 additional agents, FAISS/Ray wrappers, and the guardrails integration layer.
