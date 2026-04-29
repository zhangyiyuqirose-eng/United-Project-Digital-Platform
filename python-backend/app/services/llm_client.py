"""LLM client abstraction with retry, circuit breaker, and fallback.

Provides a pluggable LLM integration layer for the AI service.
When ANTHROPIC_API_KEY is set, Claude is used as primary with
rule-based fallback on failure.  Otherwise, pure rule-based mode.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

logger = logging.getLogger(__name__)


# ── Data types ───────────────────────────────────────────────────────────

@dataclass
class LlmResponse:
    """Normalised response from any LLM backend."""

    content: str
    model: str
    tokens_used: int = 0
    latency_ms: float = 0.0


class CircuitState(Enum):
    CLOSED = auto()       # normal operation
    OPEN = auto()         # failing — reject immediately
    HALF_OPEN = auto()    # testing recovery


# ── Abstract base ───────────────────────────────────────────────────────

class LlmClient(ABC):
    """Abstract base for LLM clients."""

    @abstractmethod
    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LlmResponse:
        """Send a chat completion request and return a normalised response."""
        ...


# ── Claude (Anthropic) client ───────────────────────────────────────────

class ClaudeClient(LlmClient):
    """LLM client using the Anthropic Claude API.

    Requires ``pip install anthropic`` and a valid API key.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model or os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        self._client = None

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for ClaudeClient")

        try:
            import anthropic

            self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
            logger.info("ClaudeClient initialised with model=%s", self.model)
        except ImportError:
            logger.warning(
                "anthropic package not installed; ClaudeClient will raise on chat()"
            )

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LlmResponse:
        if self._client is None:
            raise RuntimeError(
                "anthropic package not installed. Run: pip install anthropic"
            )

        start = time.monotonic()
        response = await self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        elapsed_ms = (time.monotonic() - start) * 1000

        content = response.content[0].text if response.content else ""
        usage = response.usage
        tokens = (usage.input_tokens + usage.output_tokens) if usage else 0

        logger.debug(
            "Claude chat completed: model=%s tokens=%d latency=%.0fms",
            self.model,
            tokens,
            elapsed_ms,
        )
        return LlmResponse(
            content=content,
            model=self.model,
            tokens_used=tokens,
            latency_ms=round(elapsed_ms, 1),
        )


# ── OpenAI-compatible client (Finna / Minimax / etc.) ────────────────────

class OpenAICompatibleClient(LlmClient):
    """Generic client for any OpenAI-compatible chat completions API.

    Works with Finna, Minimax, DeepSeek, Qwen, Ollama, vLLM, and any other
    provider exposing a ``/v1/chat/completions`` endpoint.

    Requires ``pip install httpx`` (already a FastAPI dependency).
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o",
        timeout: float = 120.0,
    ) -> None:
        import httpx

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(timeout),
        )
        logger.info(
            "OpenAICompatibleClient initialised: url=%s model=%s",
            self.base_url,
            self.model,
        )

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LlmResponse:
        start = time.monotonic()

        # Merge system prompt into user message for models that
        # consume tokens on internal reasoning (Minimax M2.7 etc.)
        if system_prompt:
            combined = f"【系统指令】\n{system_prompt}\n\n【用户问题】\n{user_message}"
        else:
            combined = user_message

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": combined}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        resp = await self._client.post("/v1/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()

        elapsed_ms = (time.monotonic() - start) * 1000
        choice = data["choices"][0] if data.get("choices") else {}
        message = choice.get("message", {})
        content = message.get("content", "") or message.get("reasoning_content", "") or ""
        usage = data.get("usage", {})
        tokens = usage.get("total_tokens", 0)

        logger.debug(
            "OpenAICompatible chat completed: model=%s tokens=%d latency=%.0fms",
            self.model, tokens, elapsed_ms,
        )
        return LlmResponse(
            content=content.strip(),
            model=self.model,
            tokens_used=tokens,
            latency_ms=round(elapsed_ms, 1),
        )

    async def close(self) -> None:
        """Release the underlying HTTP client."""
        await self._client.aclose()


# ── Rule-based fallback client ──────────────────────────────────────────

# System-prompt intent markers used by RuleBasedClient to route requests
_INTENT_MARKERS: dict[str, str] = {
    "document": "generate_document",
    "report": "generate_report",
    "risk": "predict_risks",
    "query": "nlq_query",
    "meeting": "summarize_meeting",
    "approval": "approval_suggest",
    "wbs": "recommend_wbs",
    "timesheet": "forecast_timesheet",
    "knowledge": "search_knowledge",
    "compliance": "compliance_check",
    "insight": "data_insights",
}


class RuleBasedClient(LlmClient):
    """Fallback LLM client that uses keyword matching on the user message.

    This client does NOT perform real LLM inference.  It returns minimal
    structured responses so that the caller (AIService) can detect the
    fallback and use its own richer rule-based logic instead.
    """

    def __init__(self, ai_service: object | None = None) -> None:
        self._ai_service = ai_service

    def set_ai_service(self, ai_service: object) -> None:
        """Late-binding setter — called by AIService.__init__."""
        self._ai_service = ai_service

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LlmResponse:
        # Detect intent from system prompt / user message
        combined = (system_prompt + " " + user_message).lower()
        detected = "unknown"
        for keyword, intent in _INTENT_MARKERS.items():
            if keyword in combined:
                detected = intent
                break

        return LlmResponse(
            content=f"[rule-based] intent={detected}",
            model="rule-based",
            tokens_used=0,
            latency_ms=0.1,
        )


# ── Resilient client with retry + circuit breaker ───────────────────────

class CircuitBreaker:
    """Simple circuit breaker that opens after *threshold* consecutive failures.

    After opening, it stays open for *recovery_seconds* before transitioning
    to HALF_OPEN to test if the underlying service has recovered.
    """

    def __init__(
        self,
        threshold: int = 5,
        recovery_seconds: float = 30.0,
    ) -> None:
        self.threshold = threshold
        self.recovery_seconds = recovery_seconds
        self._failure_count = 0
        self._last_failure_time: float = 0.0
        self._state = CircuitState.CLOSED

    @property
    def state(self) -> CircuitState:
        self._transition()
        return self._state

    def success(self) -> None:
        self._failure_count = 0
        self._state = CircuitState.CLOSED

    def failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.monotonic()
        if self._failure_count >= self.threshold:
            self._state = CircuitState.OPEN
            logger.warning(
                "Circuit breaker OPEN after %d failures", self._failure_count
            )

    def _transition(self) -> None:
        if self._state == CircuitState.OPEN:
            elapsed = time.monotonic() - self._last_failure_time
            if elapsed >= self.recovery_seconds:
                self._state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN")


class ResilientLlmClient(LlmClient):
    """Decorator that adds retry + circuit breaker around *primary*,
    falling back to *fallback* when the primary is unavailable.
    """

    def __init__(
        self,
        primary: LlmClient,
        fallback: LlmClient,
        max_retries: int = 3,
        cb_threshold: int = 5,
        cb_recovery_seconds: float = 30.0,
    ) -> None:
        self._primary = primary
        self._fallback = fallback
        self._max_retries = max_retries
        self._breaker = CircuitBreaker(
            threshold=cb_threshold, recovery_seconds=cb_recovery_seconds
        )

    @property
    def primary(self) -> LlmClient:
        return self._primary

    @property
    def fallback(self) -> LlmClient:
        return self._fallback

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LlmResponse:
        # Try primary if circuit allows
        if self._breaker.state != CircuitState.OPEN:
            for attempt in range(1, self._max_retries + 1):
                try:
                    response = await self._primary.chat(
                        system_prompt=system_prompt,
                        user_message=user_message,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                    self._breaker.success()
                    return response
                except Exception as exc:
                    logger.warning(
                        "LLM primary attempt %d/%d failed: %s",
                        attempt,
                        self._max_retries,
                        exc,
                    )
                    if attempt < self._max_retries:
                        await asyncio.sleep(2 ** (attempt - 1))  # exponential backoff
                    else:
                        self._breaker.failure()

        # Primary failed or circuit is open — try fallback
        logger.info("Falling back to %s", type(self._fallback).__name__)
        try:
            return await self._fallback.chat(
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception as exc:
            logger.error("Fallback also failed: %s", exc)
            raise
