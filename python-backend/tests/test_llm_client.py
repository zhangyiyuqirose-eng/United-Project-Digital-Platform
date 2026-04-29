"""Tests for LLM client abstraction (app/services/llm_client.py)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.llm_client import (
    CircuitBreaker,
    CircuitState,
    LlmResponse,
    ResilientLlmClient,
    RuleBasedClient,
)


# ── RuleBasedClient ───────────────────────────────────────────────────

class TestRuleBasedClient:

    @pytest.mark.asyncio
    async def test_returns_response_with_detected_intent(self):
        client = RuleBasedClient()
        resp = await client.chat(
            system_prompt="You are a document generator.",
            user_message="Please generate a report for the project.",
        )
        assert isinstance(resp, LlmResponse)
        assert resp.model == "rule-based"
        assert resp.tokens_used == 0
        assert resp.latency_ms == 0.1
        assert "intent=" in resp.content

    @pytest.mark.asyncio
    async def test_detects_document_intent(self):
        client = RuleBasedClient()
        resp = await client.chat(
            system_prompt="You generate documents.",
            user_message="create a doc",
        )
        assert "intent=generate_document" in resp.content

    @pytest.mark.asyncio
    async def test_detects_report_intent(self):
        client = RuleBasedClient()
        resp = await client.chat(
            system_prompt="Generate reports.",
            user_message="make a report",
        )
        assert "intent=generate_report" in resp.content

    @pytest.mark.asyncio
    async def test_detects_risk_intent(self):
        client = RuleBasedClient()
        resp = await client.chat(
            system_prompt="Predict project risks.",
            user_message="what are the risks",
        )
        assert "intent=predict_risks" in resp.content

    @pytest.mark.asyncio
    async def test_detects_query_intent(self):
        client = RuleBasedClient()
        resp = await client.chat(
            system_prompt="Answer natural language queries.",
            user_message="query: how many projects",
        )
        assert "intent=nlq_query" in resp.content

    @pytest.mark.asyncio
    async def test_unknown_intent_when_no_keyword_matches(self):
        client = RuleBasedClient()
        resp = await client.chat(
            system_prompt="You are a helpful assistant.",
            user_message="Hello, how are you?",
        )
        assert "intent=unknown" in resp.content

    @pytest.mark.asyncio
    async def test_set_ai_service_late_binding(self):
        client = RuleBasedClient()
        mock_service = MagicMock()
        client.set_ai_service(mock_service)
        assert client._ai_service is mock_service


# ── CircuitBreaker ────────────────────────────────────────────────────

class TestCircuitBreaker:

    def test_initial_state_closed(self):
        cb = CircuitBreaker(threshold=3, recovery_seconds=30)
        assert cb.state == CircuitState.CLOSED

    def test_opens_after_threshold_failures(self):
        cb = CircuitBreaker(threshold=3, recovery_seconds=30)
        cb.failure()
        cb.failure()
        assert cb.state == CircuitState.CLOSED
        cb.failure()
        assert cb.state == CircuitState.OPEN

    def test_success_resets_failures(self):
        cb = CircuitBreaker(threshold=3, recovery_seconds=30)
        cb.failure()
        cb.failure()
        cb.success()
        assert cb.state == CircuitState.CLOSED
        cb.failure()
        cb.failure()
        cb.failure()  # This is only 3 since success reset
        assert cb.state == CircuitState.OPEN

    def test_transitions_to_half_open_after_recovery(self):
        cb = CircuitBreaker(threshold=2, recovery_seconds=0.01)
        cb.failure()
        cb.failure()
        assert cb.state == CircuitState.OPEN

        # Wait for recovery
        import time
        time.sleep(0.02)
        assert cb.state == CircuitState.HALF_OPEN

    def test_state_property_triggers_transition(self):
        cb = CircuitBreaker(threshold=2, recovery_seconds=0.01)
        cb.failure()
        cb.failure()
        assert cb.state == CircuitState.OPEN

        import time
        time.sleep(0.02)
        # After recovery time, state transitions to HALF_OPEN
        assert cb.state == CircuitState.HALF_OPEN

    def test_success_in_half_open_returns_to_closed(self):
        cb = CircuitBreaker(threshold=2, recovery_seconds=0.01)
        cb.failure()
        cb.failure()
        assert cb.state == CircuitState.OPEN

        import time
        time.sleep(0.02)
        assert cb.state == CircuitState.HALF_OPEN
        cb.success()
        assert cb.state == CircuitState.CLOSED


# ── ResilientLlmClient ────────────────────────────────────────────────

class TestResilientLlmClient:

    @pytest.mark.asyncio
    async def test_uses_primary_when_available(self):
        primary = AsyncMock()
        primary.chat.return_value = LlmResponse(
            content="Primary response",
            model="claude",
            tokens_used=100,
            latency_ms=500.0,
        )
        fallback = AsyncMock()

        client = ResilientLlmClient(primary=primary, fallback=fallback)
        resp = await client.chat("sys", "msg")

        assert resp.content == "Primary response"
        assert resp.model == "claude"
        primary.chat.assert_called_once()
        fallback.chat.assert_not_called()

    @pytest.mark.asyncio
    async def test_falls_back_when_primary_fails(self):
        primary = AsyncMock()
        primary.chat.side_effect = RuntimeError("Primary down")
        fallback = AsyncMock()
        fallback.chat.return_value = LlmResponse(
            content="Fallback response",
            model="rule-based",
            tokens_used=0,
            latency_ms=0.1,
        )

        client = ResilientLlmClient(
            primary=primary,
            fallback=fallback,
            max_retries=1,
        )
        resp = await client.chat("sys", "msg")

        assert resp.content == "Fallback response"
        assert resp.model == "rule-based"
        primary.chat.assert_called_once()
        fallback.chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_repeated_failures(self):
        """After N failures without retries, circuit opens and falls back immediately."""
        primary = AsyncMock()
        primary.chat.side_effect = RuntimeError("Primary error")
        fallback = AsyncMock()
        fallback.chat.return_value = LlmResponse(
            content="Fallback", model="rule-based",
        )

        client = ResilientLlmClient(
            primary=primary,
            fallback=fallback,
            max_retries=1,           # no retry, single attempt
            cb_threshold=2,          # open after 2 failures
        )

        # First failure: circuit still closed, tries primary, fails, falls back
        resp1 = await client.chat("sys", "msg1")
        assert resp1.model == "rule-based"
        assert client._breaker.state == CircuitState.CLOSED

        # Second failure: circuit opens
        resp2 = await client.chat("sys", "msg2")
        assert resp2.model == "rule-based"
        assert client._breaker.state == CircuitState.OPEN

        # Third call: circuit is OPEN, skips primary, goes directly to fallback
        resp3 = await client.chat("sys", "msg3")
        assert resp3.model == "rule-based"
        # Primary should have been called only twice (circuit open on 3rd)
        assert primary.chat.call_count == 2  # not called on 3rd attempt

    @pytest.mark.asyncio
    async def test_exponential_backoff_on_retry(self):
        """Verify retries are attempted before circuit breaker opens."""
        primary = AsyncMock()
        primary.chat.side_effect = RuntimeError("Service error")
        fallback = AsyncMock()
        fallback.chat.return_value = LlmResponse(content="Fallback", model="rule-based")

        client = ResilientLlmClient(
            primary=primary,
            fallback=fallback,
            max_retries=3,
            cb_threshold=10,  # high threshold, won't open during test
        )

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            resp = await client.chat("sys", "msg")
            assert resp.model == "rule-based"
            # Should have retried 3 times, sleeping between retries
            assert primary.chat.call_count == 3
            assert mock_sleep.call_count == 2  # sleeps between attempts 1-2 and 2-3

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self):
        """After recovery time, circuit goes HALF_OPEN, success returns to CLOSED."""
        primary = AsyncMock()
        primary.chat.side_effect = RuntimeError("Error")
        fallback = AsyncMock()
        fallback.chat.return_value = LlmResponse(content="Fallback", model="rule-based")

        client = ResilientLlmClient(
            primary=primary,
            fallback=fallback,
            max_retries=1,
            cb_threshold=1,           # open after 1 failure
            cb_recovery_seconds=0.01,  # very short recovery
        )

        # One failure opens circuit
        await client.chat("sys", "msg1")
        assert client._breaker.state == CircuitState.OPEN

        import time
        time.sleep(0.02)

        # Circuit is now HALF_OPEN; make primary succeed
        primary.chat.side_effect = None
        primary.chat.return_value = LlmResponse(
            content="Recovered!", model="claude",
        )

        resp = await client.chat("sys", "msg2")
        assert resp.content == "Recovered!"
        assert resp.model == "claude"
        assert client._breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_properties_expose_primary_and_fallback(self):
        primary = MagicMock()
        fallback = MagicMock()
        client = ResilientLlmClient(primary=primary, fallback=fallback)
        assert client.primary is primary
        assert client.fallback is fallback
