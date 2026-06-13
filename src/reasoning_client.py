"""
reasoning_client — the ADR-0016 LLM execution-routing seam.

A single abstraction that isolates LLM auth/transport from agent logic. Agents
declare *what* to reason about and at *what stakes tier*; this seam decides
*where* the call runs, how it authenticates, how it retries, times out, and how
it is traced. No agent imports an LLM client directly — that coupling lives here
and only here (ADR-0016 §"Implementation seam").

Tiers (routing is by stakes, per ADR-0016 / agents/MODEL_TIER_ASSIGNMENTS.md):

    Tier.T1  — Deterministic ML. No LLM. complete() on T1 is a routing bug and
               raises: T1 work is computation, never inference.
    Tier.T2  — Local LLM on the Mac mini, 24/7 (Ollama). Bulk / low-stakes
               reasoning: per-pair classification, triage, drafting, review.
    Tier.T3  — Frontier Claude Max 20x via claude-agent-sdk. The `claude` CLI's
               subscription OAuth (CLAUDE_CODE_OAUTH_TOKEN) is the ONLY auth path
               — NO Anthropic API key. ANTHROPIC_API_KEY is scrubbed from the SDK
               subprocess env so a stray key can never spill to the metered API
               (ADR-0016). Reserved for high-stakes judgments. Bursty / queued.

Reliability (hardening pass 1):
  - Every call has a per-tier timeout (#145, #158) so a hung backend can never
    block a synchronous LangGraph node forever.
  - Transient failures are retried with bounded exponential backoff (#157).
  - Every call is wrapped in an OpenTelemetry span carrying run_id/agent_id/tier
    (OpenInference LLM conventions) so BOTH tiers are visible in Phoenix — T3 is
    not LangChain-instrumented, so without this it would be invisible (#150, #168).
    Spans are cheap no-ops when no tracer provider is registered (offline/tests).
  - complete_json uses Ollama's native JSON mode on T2 and a balanced-brace
    extractor, instead of a greedy regex that mangled multi-value replies (#159).

Data sovereignty (ADR-0002 as amended by ADR-0016): persistent artifacts never
leave the machine; T3 permits transient, non-retained inference over the specific
SCF-derived text needed for a single call.

Public surface:
    complete(tier, prompt, system=..., run_id=..., agent_id=...) -> str
    complete_json(tier, prompt, ...) -> dict | list
    is_available(tier) -> bool
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
from enum import Enum
from functools import lru_cache
from typing import Any

from opentelemetry import trace

# ── Tiers ─────────────────────────────────────────────────────────────────────


class Tier(str, Enum):
    """Execution tier, by stakes. See agents/MODEL_TIER_ASSIGNMENTS.md."""

    T1 = "t1"  # deterministic ML — no LLM
    T2 = "t2"  # local Ollama
    T3 = "t3"  # frontier Claude Max via Agent SDK


class ReasoningError(RuntimeError):
    """Raised when a reasoning call cannot be completed (backend down, timeout, T1 misuse)."""


class PermanentReasoningError(ReasoningError):
    """A non-transient failure (model missing, auth, CLI absent). Never retried."""


class RateLimitError(ReasoningError):
    """A Tier-3 subscription rate window. Retried with long backpressure, never
    spilled to a metered API (ADR-0016)."""


# ── Configuration (env-overridable; local-first defaults) ─────────────────────


def _env(name: str, default: str) -> str:
    val = os.environ.get(name, "").strip()
    return val or default


T2_MODEL = _env("HCGRC_T2_MODEL", "llama3.1:8b")
T2_BASE_URL = _env("HCGRC_OLLAMA_BASE_URL", "http://localhost:11434")
T3_MODEL = os.environ.get("HCGRC_T3_MODEL", "").strip() or None

# Per-tier hard timeouts (seconds). T3 is bursty/queued so it gets more headroom.
T2_TIMEOUT = float(_env("HCGRC_T2_TIMEOUT", "120"))
T3_TIMEOUT = float(_env("HCGRC_T3_TIMEOUT", "300"))

# Tier-2 (Ollama) decoding controls. num_ctx avoids silent truncation at the 2048
# default (#196); seed makes greedy decoding reproducible (#197); num_predict caps
# output so a runaway/JSON-mode generation hits a bound before the hard timeout (#198).
T2_NUM_CTX = int(_env("HCGRC_T2_NUM_CTX", "8192"))
T2_SEED = int(_env("HCGRC_T2_SEED", "0"))
T2_NUM_PREDICT = int(_env("HCGRC_T2_NUM_PREDICT", "2048"))

# Bounded retry with exponential backoff on transient failures. Clamped >= 0 so a
# negative override cannot produce an empty loop that raises None (#208).
MAX_RETRIES = max(0, int(_env("HCGRC_REASONING_RETRIES", "2")))
BACKOFF_BASE = float(_env("HCGRC_REASONING_BACKOFF", "1.5"))
# Tier-3 rate-window backpressure: long, capped waits — queue and resume, never
# fail fast onto a metered path.
RATE_LIMIT_BACKOFF = float(_env("HCGRC_RATELIMIT_BACKOFF", "30"))
RATE_LIMIT_MAX_RETRIES = max(0, int(_env("HCGRC_RATELIMIT_RETRIES", "5")))

# Truncation cap for prompt/response text recorded on spans (local Phoenix only).
_SPAN_TEXT_CAP = 8000

_tracer = trace.get_tracer("hcgrc.reasoning_client")

# Shared executor for enforcing sync-call timeouts. Not shut down: a hung backend
# call leaks one daemon worker rather than blocking the node (a ThreadPoolExecutor
# context-manager exit would join the hung thread, defeating the timeout).
_timeout_pool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="reasoning-timeout")


# ── Timeout helpers ───────────────────────────────────────────────────────────


def _with_timeout(fn, timeout: float, what: str):
    """Run a sync callable with a hard timeout; raise ReasoningError on overrun."""
    future = _timeout_pool.submit(fn)
    try:
        return future.result(timeout=timeout)
    except FuturesTimeout as exc:
        raise ReasoningError(f"{what} timed out after {timeout:.0f}s") from exc


def _run_sync(coro: Any) -> Any:
    """Run a coroutine to completion from sync code, even inside a running loop."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    # Bound the cross-thread wait so a starved/leaked pool can't deadlock a node
    # forever (#227). The inner coroutine already has its own asyncio timeout; this
    # is a backstop slightly beyond it.
    return _timeout_pool.submit(lambda: asyncio.run(coro)).result(timeout=T3_TIMEOUT + 30)


# ── Tier 2: local Ollama ──────────────────────────────────────────────────────


@lru_cache(maxsize=16)
def _ollama(model: str, temperature: float, json_mode: bool) -> Any:
    """Construct (and cache) a ChatOllama client for the local serving stack."""
    try:
        from langchain_ollama import ChatOllama
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise ReasoningError(
            "langchain-ollama is not installed — Tier 2 backend unavailable."
        ) from exc
    kwargs: dict[str, Any] = {
        "model": model,
        "temperature": temperature,
        "base_url": T2_BASE_URL,
        "num_ctx": T2_NUM_CTX,         # avoid silent truncation at the 2048 default (#196)
        "seed": T2_SEED,               # reproducible greedy decoding (#197)
        "client_kwargs": {"timeout": T2_TIMEOUT},  # native HTTP timeout (#195)
    }
    if json_mode:
        # Native structured-output: Ollama constrains decoding to valid JSON,
        # far more reliable than instructing + regex-extracting (#159, #175). Do
        # NOT cap num_predict here — format=json terminates at the end of a valid
        # JSON value, and a num_predict cap would truncate it into INVALID JSON
        # (#231). The hard timeout remains the runaway backstop.
        kwargs["format"] = "json"
    else:
        kwargs["num_predict"] = T2_NUM_PREDICT  # bound free-text output length (#198)
    return ChatOllama(**kwargs)


def _t2_complete(prompt: str, system: str | None, temperature: float, model: str,
                 json_mode: bool) -> str:
    llm = _ollama(model, temperature, json_mode)
    messages: list[tuple[str, str]] = []
    if system:
        messages.append(("system", system))
    messages.append(("human", prompt))

    def _call():
        resp = llm.invoke(messages)
        content = getattr(resp, "content", resp)
        return content if isinstance(content, str) else str(content)

    try:
        text = _with_timeout(_call, T2_TIMEOUT, f"Tier 2 (Ollama @ {T2_BASE_URL})").strip()
        if not text:
            # An empty/whitespace reply is not a valid result — surface it as a
            # retryable error rather than silently returning "" and corrupting a
            # JSON caller or recording an empty high-stakes answer (#233).
            raise ReasoningError(f"Tier 2 (Ollama @ {T2_BASE_URL}) returned an empty reply")
        return text, {"model": model}
    except ReasoningError:
        raise
    except Exception as exc:
        msg = str(exc).lower()
        # A missing model is permanent — retrying just wastes backoff (#194).
        if "not found" in msg or "no such model" in msg or "try pulling" in msg:
            raise PermanentReasoningError(
                f"Tier 2 model {model!r} not available on Ollama: {exc}"
            ) from exc
        raise ReasoningError(f"Tier 2 (Ollama @ {T2_BASE_URL}) call failed: {exc}") from exc


# ── Tier 3: frontier Claude Max via Agent SDK ─────────────────────────────────


def _scrubbed_env() -> dict[str, str]:
    """
    Environment for the Agent SDK subprocess with ANTHROPIC_API_KEY removed.

    ADR-0016: execution runs entirely on the fixed Claude Max subscription via the
    `claude` CLI's OAuth token. A metered Anthropic API key must NEVER be used — if
    one is present in the process env it would silently bill per-token, so we strip
    it before the SDK ever sees it.
    """
    return {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}


async def _t3_async(prompt: str, system: str | None, max_turns: int,
                    model: str | None) -> tuple[str, dict[str, Any]]:
    try:
        from claude_agent_sdk import (
            AssistantMessage,
            ClaudeAgentOptions,
            ResultMessage,
            TextBlock,
            query,
        )
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise PermanentReasoningError(
            "claude-agent-sdk is not installed — Tier 3 backend unavailable."
        ) from exc

    opts = ClaudeAgentOptions(
        max_turns=max_turns,
        system_prompt=system,
        allowed_tools=[],          # pure reasoning — no filesystem/command access
        env=_scrubbed_env(),       # ADR-0016: no metered API key (#146)
    )
    if model:
        opts.model = model

    chunks: list[str] = []
    meta: dict[str, Any] = {"model": model}  # real model id if pinned, else unknown

    async def _drain():
        async for msg in query(prompt=prompt, options=opts):
            if isinstance(msg, AssistantMessage):
                if getattr(msg, "model", None):
                    meta["model"] = msg.model  # the actual model the run used (#204)
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        chunks.append(block.text)
            elif isinstance(msg, ResultMessage):
                if getattr(msg, "usage", None):
                    meta["usage"] = msg.usage  # token usage for the span (#203)
                if getattr(msg, "total_cost_usd", None) is not None:
                    meta["cost_usd"] = msg.total_cost_usd

    await asyncio.wait_for(_drain(), timeout=T3_TIMEOUT)
    return "".join(chunks).strip(), meta


def _t3_complete(prompt: str, system: str | None, max_turns: int,
                 model: str | None) -> tuple[str, dict[str, Any]]:
    try:
        return _run_sync(_t3_async(prompt, system, max_turns, model))
    except ReasoningError:
        raise
    except (asyncio.TimeoutError, FuturesTimeout) as exc:
        raise ReasoningError(f"Tier 3 (Agent SDK) timed out after {T3_TIMEOUT:.0f}s") from exc
    except Exception as exc:
        msg = str(exc).lower()
        # Subscription rate window — queue and resume with long backpressure,
        # never spill to a metered API (ADR-0016, #185).
        if any(k in msg for k in ("rate limit", "rate_limit", "429", "overloaded",
                                  "usage limit", "too many requests")):
            raise RateLimitError(f"Tier 3 rate window: {exc}") from exc
        # CLI absent / auth failure — permanent, not worth retrying (#194).
        if any(k in msg for k in ("not found", "command not found", "no such file",
                                  "auth", "credential", "401", "403", "unauthor")):
            raise PermanentReasoningError(f"Tier 3 (Agent SDK) unavailable: {exc}") from exc
        raise ReasoningError(f"Tier 3 (Agent SDK) call failed: {exc}") from exc


# ── Public API ────────────────────────────────────────────────────────────────


def _attempt(tier: Tier, prompt: str, system: str | None, temperature: float,
             max_turns: int, model: str | None, json_mode: bool) -> tuple[str, dict[str, Any]]:
    if tier is Tier.T2:
        return _t2_complete(prompt, system, temperature, model or T2_MODEL, json_mode)
    return _t3_complete(prompt, system, max_turns, model or T3_MODEL)


def _record_usage(span, usage: Any) -> None:
    """Set OpenInference token-count attributes from a usage dict/object (#203)."""
    if not usage:
        return

    def g(key: str):
        return usage.get(key) if isinstance(usage, dict) else getattr(usage, key, None)

    prompt_toks = g("input_tokens")
    completion_toks = g("output_tokens")
    if prompt_toks is not None:
        span.set_attribute("llm.token_count.prompt", prompt_toks)
    if completion_toks is not None:
        span.set_attribute("llm.token_count.completion", completion_toks)
    if prompt_toks is not None and completion_toks is not None:
        span.set_attribute("llm.token_count.total", prompt_toks + completion_toks)


def complete(
    tier: Tier,
    prompt: str,
    *,
    system: str | None = None,
    temperature: float = 0.0,
    max_turns: int = 1,
    model: str | None = None,
    run_id: str | None = None,
    agent_id: str | None = None,
    _json_mode: bool = False,
) -> str:
    """
    Run a single reasoning call at the given stakes tier and return the text.

    Times out per tier, retries transient failures with backoff, and emits an
    OpenTelemetry span (run_id/agent_id/tier) so the call is visible in Phoenix.

    Raises ReasoningError on T1 misuse or after retries are exhausted. Callers
    that must keep the graph moving (dry-runs) should catch and degrade.
    """
    if tier is Tier.T1:
        raise ReasoningError(
            "Tier.T1 is deterministic ML — it has no LLM. A reasoning_client call "
            "on T1 is a routing bug; the work belongs in computation, not inference."
        )
    if os.environ.get("HCGRC_DISABLE_REASONING", "").strip():
        raise ReasoningError("reasoning disabled via HCGRC_DISABLE_REASONING")

    # Known model id only — never fabricate one (#204). For a T3 run on the
    # subscription default, the real model is read back from the response.
    known_model = model or (T2_MODEL if tier is Tier.T2 else T3_MODEL)
    with _tracer.start_as_current_span("reasoning.complete") as span:
        # For T2, LangChainInstrumentor emits a child ChatOllama span under this
        # one — intentional parent/child nesting (the seam-level call + the
        # provider call), not redundant double-tracing (#214). T3 has no LangChain
        # span, so this is the only record of the frontier call.
        # OpenInference LLM conventions + HC-GRC cross-store correlation.
        span.set_attribute("openinference.span.kind", "LLM")
        span.set_attribute("llm.provider", "ollama" if tier is Tier.T2 else "anthropic")
        if known_model:
            span.set_attribute("llm.model_name", known_model)
        span.set_attribute("hcgrc.tier", tier.value)
        if run_id:
            span.set_attribute("hcgrc.run_id", run_id)
            span.set_attribute("session.id", run_id)
        if agent_id:
            span.set_attribute("hcgrc.agent_id", agent_id)
        if system:
            # Record the system prompt too — without it the trace input is
            # incomplete and the call is not reproducible from the span (#240).
            span.set_attribute("llm.system", system[:_SPAN_TEXT_CAP])
        span.set_attribute("input.value", prompt[:_SPAN_TEXT_CAP])

        last_exc: ReasoningError | None = None
        # Independent retry budgets so a mix of transient and rate-limit errors
        # cannot exhaust each other's allowance prematurely (#228).
        transient_attempts = 0
        rate_attempts = 0
        while True:
            try:
                out, meta = _attempt(tier, prompt, system, temperature, max_turns, model, _json_mode)
                if meta.get("model"):
                    span.set_attribute("llm.model_name", meta["model"])
                _record_usage(span, meta.get("usage"))
                if meta.get("cost_usd") is not None:
                    span.set_attribute("llm.cost_usd", meta["cost_usd"])
                span.set_attribute("output.value", out[:_SPAN_TEXT_CAP])
                span.set_attribute("llm.retries", transient_attempts + rate_attempts)
                return out
            except PermanentReasoningError as exc:
                # Deterministic failure — do not retry (#194).
                last_exc = exc
                break
            except RateLimitError as exc:
                last_exc = exc
                if rate_attempts >= RATE_LIMIT_MAX_RETRIES:
                    break
                span.add_event("rate_limit_backpressure",
                               {"attempt": rate_attempts, "sleep_s": RATE_LIMIT_BACKOFF})
                time.sleep(RATE_LIMIT_BACKOFF * (rate_attempts + 1))
                rate_attempts += 1
            except ReasoningError as exc:
                last_exc = exc
                if transient_attempts >= MAX_RETRIES:
                    break
                span.add_event("retry", {"attempt": transient_attempts, "error": str(exc)[:300]})
                time.sleep(BACKOFF_BASE ** transient_attempts)
                transient_attempts += 1
        # Exhausted retries.
        span.record_exception(last_exc)
        span.set_status(trace.StatusCode.ERROR, str(last_exc))
        raise last_exc


def complete_json(
    tier: Tier,
    prompt: str,
    *,
    system: str | None = None,
    temperature: float = 0.0,
    max_turns: int = 1,
    model: str | None = None,
    run_id: str | None = None,
    agent_id: str | None = None,
) -> Any:
    """
    Like complete(), but parse the model's reply as JSON.

    On T2 this uses Ollama's native JSON mode (constrained decoding). The reply is
    then parsed, falling back to a balanced-brace extractor for models that wrap
    JSON in prose/fences. A parse failure is retried (re-generating the reply) up
    to MAX_RETRIES — the retry budget belongs here, not only in complete() (#230).
    Raises ReasoningError if no valid JSON can be recovered.
    """
    json_system = (system + "\n\n" if system else "") + (
        "Respond with ONLY a single valid JSON value and no other text, "
        "no markdown fences, no commentary."
    )
    last_exc: ReasoningError | None = None
    for attempt in range(MAX_RETRIES + 1):
        raw = complete(
            tier, prompt, system=json_system, temperature=temperature,
            max_turns=max_turns, model=model, run_id=run_id, agent_id=agent_id,
            _json_mode=True,
        )
        try:
            return _extract_json(raw)
        except ReasoningError as exc:
            last_exc = exc  # bad/garbled JSON — regenerate and try again
    raise last_exc


def _extract_json(text: str) -> Any:
    """Recover a JSON value from a model reply that may include fences/prose."""
    candidate = text.strip()
    # Strip a ```json ... ``` fence if present.
    if candidate.startswith("```"):
        inner = candidate[3:]
        if inner[:4].lower() == "json":
            inner = inner[4:]
        candidate = inner.rsplit("```", 1)[0].strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    span = _first_balanced_json(candidate)
    if span is not None:
        try:
            return json.loads(span)
        except json.JSONDecodeError as exc:
            raise ReasoningError(f"Reply was not valid JSON: {text[:200]!r}") from exc
    raise ReasoningError(f"No JSON value found in reply: {text[:200]!r}")


def _first_balanced_json(text: str) -> str | None:
    """
    Return the first balanced {...} or [...] span, respecting string literals.

    A greedy regex (`[\\{\\[].*[\\}\\]]`) grabs from the first brace to the LAST
    brace, which mangles replies containing multiple JSON values or braces in
    trailing prose. This walks the structure honestly (#159).
    """
    start = None
    for i, ch in enumerate(text):
        if ch in "{[":
            start = i
            break
    if start is None:
        return None
    open_ch = text[start]
    close_ch = "}" if open_ch == "{" else "]"
    depth = 0
    in_str = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def is_available(tier: Tier) -> bool:
    """
    Cheap, side-effect-light liveness check for a tier's backend, used by nodes
    that must degrade gracefully rather than fail the run.

    Does NOT spend an LLM turn (the old probe burned a real Tier-3 frontier turn
    on every call, #174, and could hang with no timeout, #173/#30). T1 is always
    available (local computation). Honors HCGRC_DISABLE_REASONING.
    """
    if tier is Tier.T1:
        return True
    if os.environ.get("HCGRC_DISABLE_REASONING", "").strip():
        return False
    if tier is Tier.T2:
        # Hit Ollama's /api/tags — no generation, short timeout — and confirm the
        # configured model is actually pulled, not merely that the server is up (#210).
        import json as _json
        import urllib.request
        try:
            with urllib.request.urlopen(f"{T2_BASE_URL}/api/tags", timeout=3) as r:
                if r.status != 200:
                    return False
                names = [m.get("name", "") for m in _json.loads(r.read()).get("models", [])]
        except Exception:
            return False
        # Exact match only: a prefix match (e.g. configured llama3.1:8b vs a
        # pulled llama3.1:70b) would pass here but complete() would then fail as
        # "model not found" (#232). Ollama tags an untagged pull as ":latest".
        return any(n == T2_MODEL or n == f"{T2_MODEL}:latest" for n in names)
    if tier is Tier.T3:
        # The `claude` CLI must be present and an OAuth token / stored creds
        # available — no frontier turn spent.
        import shutil
        if shutil.which("claude") is None:
            return False
        if os.environ.get("CLAUDE_CODE_OAUTH_TOKEN", "").strip():
            return True
        creds = os.path.expanduser("~/.claude/.credentials.json")
        return os.path.exists(creds)
    return False
