"""Structured logging configuration using structlog.

Replaces standard logging with structured, JSON-capable output.
Injects trace_id, user_id, and duration into every log entry.
"""

from __future__ import annotations

import logging
import logging as _stdlib_logging
import sys
from typing import Any

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars


def _patch_logger_for_python_314() -> None:
    """Patch Logger._log to accept extra kwargs as extra dict fields.

    Python 3.14 removed **kwargs support from Logger._log(). structlog
    passes field key-value pairs as kwargs which now causes a TypeError.
    This patch intercepts _log and merges kwargs into the extra dict.
    """
    original_log = _stdlib_logging.Logger._log

    def patched_log(
        self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1, **kwargs
    ):
        if kwargs:
            extra = {**(extra or {}), **kwargs}
        return original_log(self, level, msg, args, exc_info, extra, stack_info, stacklevel)

    _stdlib_logging.Logger._log = patched_log


def setup_logging(*, json_logs: bool = False, log_level: str = "INFO") -> None:
    """Configure structlog as the application-wide logger.

    Args:
        json_logs: Use JSON output (production) or key-value console output (dev).
        log_level: Logging level string.
    """
    # Patch standard logging for Python 3.14 compatibility
    _patch_logger_for_python_314()

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Console or JSON renderer
    if json_logs:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    # Replace root logger handlers
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(getattr(logging, log_level.upper(), logging.INFO))


def get_logger(*args: str, **kwargs: Any) -> structlog.stdlib.BoundLogger:
    """Get a structlog logger bound to optional key-value pairs."""
    return structlog.get_logger(*args, **kwargs)


def bind_trace_id(trace_id: str) -> None:
    """Bind trace_id to the current context for all subsequent log calls."""
    bind_contextvars(trace_id=trace_id)


def bind_user_id(user_id: str) -> None:
    """Bind user_id to the current context."""
    bind_contextvars(user_id=user_id)


def clear_request_context() -> None:
    """Clear all context vars at the end of a request."""
    clear_contextvars()
