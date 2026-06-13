"""
reasoning_client — the ADR-0016 LLM execution-routing seam.

A single abstraction that isolates LLM auth/transport from agent logic. Agents
declare *what* to reason about and at *what stakes tier*; this seam decides
*where* the call runs and how it authenticates. No agent imports an LLM client
directly — that coupling lives here and only here (ADR-0016 §"Implementation
seam").

Tiers (routing is by stakes, per ADR-0016 / agents/MODEL_TIER_ASSIGNMENTS.md):

    Tier.T1  — Deterministic ML. No LLM. complete() on T1 is a routing bug and
               raises: T1 work is computation (embeddings, graph algorithms,
               clustering, statistics), never inference.
    Tier.T2  — Local LLM on the Mac mini, 24/7 (Ollama). Bulk / low-stakes
               reasoning: per-pair classification, triage, drafting, review.
    Tier.T3  — Frontier Claude Max 20x via claude-agent-sdk. The `claude` CLI's
               subscription OAuth (CLAUDE_CODE_OAUTH_TOKEN) is the only auth path
               — NO Anthropic API key is provisioned. Reserved for high-stakes
               judgments where a wrong answer corrupts the science or a public
               output. Bursty / queued against the fixed subscription envelope.

Data sovereignty (ADR-0002 as amended by ADR-0016): persistent artifacts —
embeddings, traces, datasets, results — never leave the machine. T3 permits
*transient, non-retained* inference over the specific SCF-derived text needed
for a single call; no derived dataset is transmitted or stored off-device.

The public surface is deliberately tiny:

    complete(tier, prompt, system=...) -> str
    complete_json(tier, prompt, system=...) -> dict | list
    is_available(tier) -> bool

so an agent's call site reads `complete(Tier.T2, prompt, system=...)` and the
agent has no idea whether that hit Ollama or a frontier model.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
import os
import re
from enum import Enum
from functools import lru_cache
from typing import Any

# ── Tiers ─────────────────────────────────────────────────────────────────────


class Tier(str, Enum):
    """Execution tier, by stakes. See agents/MODEL_TIER_ASSIGNMENTS.md."""

    T1 = "t1"  # deterministic ML — no LLM
    T2 = "t2"  # local Ollama
    T3 = "t3"  # frontier Claude Max via Agent SDK


class ReasoningError(RuntimeError):
    """Raised when a reasoning call cannot be completed (backend down, T1 misuse)."""


# ── Configuration (env-overridable; local-first defaults) ─────────────────────


def _env(name: str, default: str) -> str:
    val = os.environ.get(name, "").strip()
    return val or default


# Tier 2 — local Ollama serving stack (operated by the local-inference agent).
T2_MODEL = _env("HCGRC_T2_MODEL", "llama3.1:8b")
T2_BASE_URL = _env("HCGRC_OLLAMA_BASE_URL", "http://localhost:11434")

# Tier 3 — frontier model id (Agent SDK / `claude` CLI default if unset).
T3_MODEL = os.environ.get("HCGRC_T3_MODEL", "").strip() or None


# ── Async → sync bridge ───────────────────────────────────────────────────────


def _run_sync(coro: Any) -> Any:
    """
    Run a coroutine to completion from sync code.

    LangGraph nodes are synchronous, but the Agent SDK is async. If no event
    loop is running we use asyncio.run(); if one is (e.g. an async caller),
    we offload to a worker thread with its own loop so we never deadlock.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(lambda: asyncio.run(coro)).result()


# ── Tier 2: local Ollama ──────────────────────────────────────────────────────


@lru_cache(maxsize=8)
def _ollama(model: str, temperature: float) -> Any:
    """Construct (and cache) a ChatOllama client for the local serving stack."""
    try:
        from langchain_ollama import ChatOllama
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise ReasoningError(
            "langchain-ollama is not installed — Tier 2 backend unavailable. "
            "Install per requirements.txt (ADR-0016)."
        ) from exc
    return ChatOllama(model=model, temperature=temperature, base_url=T2_BASE_URL)


def _t2_complete(prompt: str, system: str | None, temperature: float, model: str) -> str:
    llm = _ollama(model, temperature)
    messages: list[tuple[str, str]] = []
    if system:
        messages.append(("system", system))
    messages.append(("human", prompt))
    try:
        resp = llm.invoke(messages)
    except Exception as exc:  # connection refused, model missing, etc.
        raise ReasoningError(f"Tier 2 (Ollama @ {T2_BASE_URL}) call failed: {exc}") from exc
    content = getattr(resp, "content", resp)
    return content.strip() if isinstance(content, str) else str(content).strip()


# ── Tier 3: frontier Claude Max via Agent SDK ─────────────────────────────────


async def _t3_async(prompt: str, system: str | None, max_turns: int, model: str | None) -> str:
    try:
        from claude_agent_sdk import (
            AssistantMessage,
            ClaudeAgentOptions,
            TextBlock,
            query,
        )
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise ReasoningError(
            "claude-agent-sdk is not installed — Tier 3 backend unavailable. "
            "Install per requirements.txt (ADR-0016)."
        ) from exc

    # Pure reasoning: no tool access. The frontier model answers from the prompt
    # alone — it must not touch the filesystem or run commands for a T3 judgment.
    opts = ClaudeAgentOptions(
        max_turns=max_turns,
        system_prompt=system,
        allowed_tools=[],
    )
    if model:
        opts.model = model

    chunks: list[str] = []
    async for msg in query(prompt=prompt, options=opts):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    chunks.append(block.text)
    return "".join(chunks).strip()


def _t3_complete(prompt: str, system: str | None, max_turns: int, model: str | None) -> str:
    try:
        return _run_sync(_t3_async(prompt, system, max_turns, model))
    except ReasoningError:
        raise
    except Exception as exc:  # CLI not found, auth, rate window, etc.
        raise ReasoningError(f"Tier 3 (Agent SDK) call failed: {exc}") from exc


# ── Public API ────────────────────────────────────────────────────────────────


def complete(
    tier: Tier,
    prompt: str,
    *,
    system: str | None = None,
    temperature: float = 0.0,
    max_turns: int = 1,
    model: str | None = None,
) -> str:
    """
    Run a single reasoning call at the given stakes tier and return the text.

    Args:
        tier: Tier.T2 (local) or Tier.T3 (frontier). Tier.T1 raises — T1 is
              deterministic ML with no inference, so a T1 reasoning call is a
              routing error to be surfaced, not silently degraded.
        prompt: the user/task content.
        system: optional system prompt establishing the agent's role/constraints.
        temperature: sampling temperature (Tier 2). Default 0.0 for reproducibility.
        max_turns: Tier 3 agent turns (default 1 — single judgment).
        model: override the tier's default model id.

    Raises:
        ReasoningError: on T1 misuse or backend failure. Callers that must keep
                        the graph moving (e.g. dry-runs) should catch and degrade.
    """
    if tier is Tier.T1:
        raise ReasoningError(
            "Tier.T1 is deterministic ML — it has no LLM. A reasoning_client call "
            "on T1 is a routing bug; the work belongs in computation, not inference."
        )
    # Test/offline kill-switch: when set, every reasoning call fails fast so nodes
    # exercise their graceful-degradation path without any network/model dependency.
    if os.environ.get("HCGRC_DISABLE_REASONING", "").strip():
        raise ReasoningError("reasoning disabled via HCGRC_DISABLE_REASONING")
    if tier is Tier.T2:
        return _t2_complete(prompt, system, temperature, model or T2_MODEL)
    if tier is Tier.T3:
        return _t3_complete(prompt, system, max_turns, model or T3_MODEL)
    raise ReasoningError(f"Unknown tier: {tier!r}")


def complete_json(
    tier: Tier,
    prompt: str,
    *,
    system: str | None = None,
    temperature: float = 0.0,
    max_turns: int = 1,
    model: str | None = None,
) -> Any:
    """
    Like complete(), but parse the model's reply as JSON.

    Appends a strict-JSON instruction, then tolerantly extracts the first JSON
    object/array from the reply (models sometimes wrap JSON in prose or fences).

    Raises ReasoningError if no valid JSON can be recovered.
    """
    json_system = (system + "\n\n" if system else "") + (
        "Respond with ONLY a single valid JSON value and no other text, "
        "no markdown fences, no commentary."
    )
    raw = complete(
        tier, prompt, system=json_system, temperature=temperature,
        max_turns=max_turns, model=model,
    )
    return _extract_json(raw)


def _extract_json(text: str) -> Any:
    """Recover a JSON value from a model reply that may include fences/prose."""
    # Strip ```json ... ``` fences if present.
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    candidate = fenced.group(1).strip() if fenced else text.strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    # Fall back to the first balanced object/array span.
    match = re.search(r"[\{\[].*[\}\]]", candidate, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ReasoningError(
                f"Tier reply was not valid JSON: {text[:200]!r}"
            ) from exc
    raise ReasoningError(f"No JSON value found in reply: {text[:200]!r}")


def is_available(tier: Tier) -> bool:
    """
    Cheap liveness check for a tier's backend. Used by nodes that must degrade
    gracefully (dry-runs, offline CI) rather than fail the run.

    Tier.T1 is always 'available' (it is local computation, no backend).
    """
    if tier is Tier.T1:
        return True
    try:
        reply = complete(tier, "Reply with the single word: OK", system="Answer in one word.")
        return "ok" in reply.lower()
    except ReasoningError:
        return False
