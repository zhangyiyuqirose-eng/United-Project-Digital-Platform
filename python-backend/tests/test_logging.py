"""Tests for app/core/logging.py — structlog configuration and context vars."""

from __future__ import annotations

import logging

import pytest
import structlog
from structlog.contextvars import get_contextvars

from app.core.logging import (
    _patch_logger_for_python_314,
    bind_trace_id,
    bind_user_id,
    clear_request_context,
    get_logger,
    setup_logging,
)


# ── _patch_logger_for_python_314 ──────────────────────────────────────

def test_patch_logger_accepts_kwargs():
    """After patching, Logger._log should accept **kwargs without error."""
    _patch_logger_for_python_314()
    logger = logging.getLogger("test_patch")
    # Should not raise TypeError
    logger.info("test message", extra_field="value")


# ── setup_logging ─────────────────────────────────────────────────────

def test_setup_logging_console_mode():
    """setup_logging(json_logs=False) configures ConsoleRenderer."""
    setup_logging(json_logs=False, log_level="WARNING")
    root = logging.getLogger()
    assert root.level == logging.WARNING


def test_setup_logging_debug_level():
    """setup_logging(log_level=DEBUG) sets root logger to DEBUG."""
    setup_logging(json_logs=False, log_level="DEBUG")
    root = logging.getLogger()
    assert root.level == logging.DEBUG


def test_setup_logging_info_level():
    """setup_logging(log_level=INFO) sets root logger to INFO."""
    setup_logging(json_logs=False, log_level="INFO")
    root = logging.getLogger()
    assert root.level == logging.INFO


def test_setup_logging_has_handlers():
    """After setup_logging, root logger has at least one handler."""
    setup_logging(json_logs=False, log_level="INFO")
    root = logging.getLogger()
    assert len(root.handlers) >= 1


# ── get_logger ────────────────────────────────────────────────────────

def test_get_logger_returns_bound_logger():
    """get_logger returns a structlog BoundLogger or BoundLoggerLazyProxy."""
    logger = get_logger()
    assert hasattr(logger, "info")


def test_get_logger_with_bindings():
    """get_logger can be called with key-value bindings."""
    logger = get_logger("test", module="logging_test")
    assert hasattr(logger, "info")


# ── Context variable bindings ─────────────────────────────────────────

def test_bind_trace_id():
    """bind_trace_id sets trace_id in context vars."""
    clear_request_context()
    bind_trace_id("trace-abc-123")
    ctx = get_contextvars()
    assert ctx.get("trace_id") == "trace-abc-123"
    clear_request_context()


def test_bind_user_id():
    """bind_user_id sets user_id in context vars."""
    clear_request_context()
    bind_user_id("user-001")
    ctx = get_contextvars()
    assert ctx.get("user_id") == "user-001"
    clear_request_context()


def test_clear_request_context():
    """clear_request_context removes all context vars."""
    bind_trace_id("trace-clear")
    bind_user_id("user-clear")
    ctx = get_contextvars()
    assert "trace_id" in ctx
    assert "user_id" in ctx
    clear_request_context()
    ctx_after = get_contextvars()
    assert "trace_id" not in ctx_after
    assert "user_id" not in ctx_after


def test_bind_multiple_vars():
    """Multiple vars can be bound and read together."""
    clear_request_context()
    bind_trace_id("trace-multi")
    bind_user_id("user-multi")
    ctx = get_contextvars()
    assert ctx["trace_id"] == "trace-multi"
    assert ctx["user_id"] == "user-multi"
    clear_request_context()
