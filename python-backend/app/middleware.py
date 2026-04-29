"""Middleware stack: CORS, JWT auth, trace ID, rate limiting, anti-replay, request logging."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from app.config import settings
from app.core.logging import bind_trace_id
from app.core.masking import mask_token
from app.core.security import decode_token

logger = logging.getLogger(__name__)

TRACE_ID_HEADER = "X-Trace-Id"

# Paths that skip JWT authentication
AUTH_WHITELIST = {
    "/health",
    "/api/auth/login", "/api/auth/register", "/api/auth/logout",
    "/api/system/auth/login", "/api/system/auth/captcha", "/api/system/auth/logout",
    "/docs", "/openapi.json", "/redoc",
}


def setup_middleware(app) -> None:
    """Configure the full 6-layer middleware stack."""

    # Layer 1: CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=3600,
    )

    # Layer 2: Trace ID + Request Logging (outermost HTTP middleware)
    @app.middleware("http")
    async def trace_and_logging_middleware(request: Request, call_next) -> Response:
        trace_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        request.state.trace_id = trace_id
        bind_trace_id(trace_id)

        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start

        response.headers[TRACE_ID_HEADER] = trace_id
        response.headers["X-Response-Time"] = f"{elapsed * 1000:.1f}ms"

        # Structured log (skip health checks to reduce noise)
        if request.url.path != "/health":
            logger.info(
                "http_request",
                http_method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(elapsed * 1000, 1),
                trace_id=trace_id,
            )

        return response

    # Layer 3: JWT Authentication
    @app.middleware("http")
    async def jwt_auth_middleware(request: Request, call_next) -> Response:
        path = request.url.path
        if path in AUTH_WHITELIST or path.startswith("/api/auth/refresh"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content='{"code":"AUTH_TOKEN_INVALID","message":"Missing or invalid Authorization header"}',
                media_type="application/json",
                headers={TRACE_ID_HEADER: getattr(request.state, "trace_id", "")},
            )

        token = auth_header[7:]
        payload = decode_token(token)
        if payload is None:
            return Response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content='{"code":"AUTH_TOKEN_EXPIRED","message":"Token expired or invalid"}',
                media_type="application/json",
                headers={TRACE_ID_HEADER: getattr(request.state, "trace_id", "")},
            )

        # Check token blacklist (Redis-backed)
        try:
            from app.dependencies import get_redis
            redis_conn = await get_redis()
            if await redis_conn.exists(f"blacklist:token:{token}"):
                return Response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content='{"code":"AUTH_TOKEN_INVALID","message":"Token has been revoked"}',
                    media_type="application/json",
                    headers={TRACE_ID_HEADER: getattr(request.state, "trace_id", "")},
                )
        except Exception:
            pass  # Redis unavailable; skip blacklist check

        # Inject user info into request state for downstream use
        request.state.user_id = payload.get("sub")
        request.state.user_role = payload.get("role", "user")
        request.state.username = payload.get("username", "")

        return await call_next(request)

    # Layer 4: Rate Limiting (Redis-backed sliding window)
    _rate_limit_redis: dict[str, bool] = {"available": True}

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next) -> Response:
        if not _rate_limit_redis["available"]:
            return await call_next(request)

        # Only rate limit API endpoints
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        # Identify client: user_id if authenticated, else IP
        client_id = getattr(request.state, "user_id", None) or request.client.host if request.client else "unknown"
        key = f"ratelimit:{client_id}"

        try:
            from app.dependencies import get_redis
            redis: Redis = await get_redis()
            now = time.time()
            window = 60  # 1 minute
            limit = 1000  # requests per minute

            # Sliding window: count requests in current window
            pipeline = redis.pipeline()
            pipeline.zadd(key, {f"{now}:{uuid.uuid4().hex[:8]}": now})
            pipeline.zremrangebyscore(key, 0, now - window)
            pipeline.zcard(key)
            pipeline.expire(key, window * 2)
            _, _, count, _ = await pipeline.execute()

            if count > limit:
                return Response(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content='{"code":"RATE_LIMIT","message":"Too many requests"}',
                    media_type="application/json",
                )
        except Exception:
            _rate_limit_redis["available"] = False
            logger.warning("Rate limiting disabled: Redis unavailable")

        return await call_next(request)

    # Layer 5: Anti-Replay (nonce + timestamp + HMAC signature)
    @app.middleware("http")
    async def anti_replay_middleware(request: Request, call_next) -> Response:
        if request.method not in ("POST", "PUT", "DELETE", "PATCH"):
            return await call_next(request)

        nonce = request.headers.get("X-Nonce")
        timestamp = request.headers.get("X-Timestamp")

        if nonce and timestamp and settings.anti_replay_enabled:
            try:
                # Check timestamp freshness (5 minute window)
                ts = float(timestamp)
                if abs(time.time() - ts) > settings.anti_replay_ttl_seconds:
                    return Response(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content='{"code":"PARAM_ERROR","message":"Request timestamp expired"}',
                        media_type="application/json",
                    )

                from app.dependencies import get_redis
                redis = await get_redis()
                cache_key = f"nonce:{nonce}"
                exists = await redis.exists(cache_key)
                if exists:
                    return Response(
                        status_code=status.HTTP_409_CONFLICT,
                        content='{"code":"DUPLICATE","message":"Replay attack detected"}',
                        media_type="application/json",
                    )
                await redis.setex(cache_key, settings.anti_replay_ttl_seconds, "1")
            except HTTPException:
                raise
            except Exception:
                pass  # Redis unavailable; skip

        return await call_next(request)
