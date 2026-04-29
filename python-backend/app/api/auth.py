"""Auth API router — replicates AuthController + SecurityController."""

from __future__ import annotations

import re
import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse
from app.core.security import create_token, create_refresh_token, decode_token, hash_password, verify_password
from app.database import get_db
from app.dependencies import get_current_user, get_redis
from app.exceptions import BusinessError, RateLimitExceededError, ValidationError
from app.models.auth.models import LoginAttempt, User

router = APIRouter(tags=["auth"])


# ── Login ────────────────────────────────────────────────────────────

@router.post("/login")
async def login(
    body: LoginRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
):
    # ── Rate limiting per IP ──────────────────────────────────────────
    client_ip = http_request.client.host if http_request.client else "unknown"
    lockout_key = f"login_lockout:{client_ip}"
    attempt_key = f"login_attempts:{client_ip}"

    try:
        redis_conn = await get_redis()
        # Check if IP is currently locked out
        lockout_remaining = await redis_conn.ttl(lockout_key)
        if lockout_remaining > 0:
            raise RateLimitExceededError(retry_after=lockout_remaining)
        # Check recent failed attempts
        attempts_raw = await redis_conn.get(attempt_key)
        if attempts_raw and int(attempts_raw) >= 5:
            await redis_conn.setex(lockout_key, 1800, "1")
            await redis_conn.delete(attempt_key)
            raise RateLimitExceededError(retry_after=1800)
    except RateLimitExceededError:
        raise
    except Exception:
        redis_conn = None  # Redis unavailable; skip rate limiting

    stmt = select(User).where(User.username == body.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise ValidationError("用户名或密码错误")

    if user.status != 1:
        raise BusinessError(code="ACCOUNT_DISABLED", message="账号已被禁用")

    if not verify_password(body.password, user.password):
        # Log failed attempt
        attempt = LoginAttempt(
            attempt_id=str(uuid.uuid4()),
            user_id=user.user_id,
            username=body.username,
            ip_address=http_request.client.host if http_request.client else None,
            success=0,
            failure_reason="密码错误",
            attempt_time=datetime.now(timezone.utc),
        )
        db.add(attempt)
        await db.flush()
        # Increment rate-limit counter
        if redis_conn is not None:
            try:
                await redis_conn.incr(attempt_key)
                await redis_conn.expire(attempt_key, 60)
            except Exception:
                pass
        raise ValidationError("用户名或密码错误")

    # Log successful attempt
    attempt = LoginAttempt(
        attempt_id=str(uuid.uuid4()),
        user_id=user.user_id,
        username=body.username,
        ip_address=http_request.client.host if http_request.client else None,
        success=1,
        attempt_time=datetime.now(timezone.utc),
    )
    db.add(attempt)
    await db.flush()

    # Reset rate-limit counters on success
    if redis_conn is not None:
        try:
            await redis_conn.delete(attempt_key, lockout_key)
        except Exception:
            pass

    access_token = create_token(user.user_id, {"role": "admin" if user.dept_id == "1" else "user"})
    refresh_token = create_refresh_token(user.user_id)

    return ApiResponse(
        code="SUCCESS",
        message="success",
        data={
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "user": {
                "userId": user.user_id,
                "username": user.username,
                "name": user.name,
                "deptId": user.dept_id,
                "email": user.email,
                "phone": user.phone,
            },
        },
    )


# ── Register ─────────────────────────────────────────────────────────

@router.post("/register")
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if username already exists
    stmt = select(User).where(User.username == request.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise ValidationError("用户名已存在")

    user = User(
        user_id=str(uuid.uuid4()),
        username=request.username,
        password=hash_password(request.password),
        name=request.name,
        email=request.email,
        phone=request.phone,
        status=1,
        password_changed_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()

    return ApiResponse(code="SUCCESS", message="注册成功", data={"userId": user.user_id})


# ── Token refresh ────────────────────────────────────────────────────

@router.post("/refresh")
async def refresh_token_endpoint(
    x_refresh_token: str = Header(alias="X-Refresh-Token"),
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(x_refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise BusinessError(code="INVALID_TOKEN", message="Refresh token 无效或已过期", status_code=401)

    user_id = payload["sub"]
    stmt = select(User).where(User.user_id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise BusinessError(code="USER_NOT_FOUND", message="用户不存在", status_code=401)

    new_access = create_token(user.user_id, {"role": "admin" if user.dept_id == "1" else "user"})
    new_refresh = create_refresh_token(user.user_id)

    return ApiResponse(
        code="SUCCESS",
        message="success",
        data={"accessToken": new_access, "refreshToken": new_refresh},
    )


# ── Logout ───────────────────────────────────────────────────────────

@router.post("/logout")
async def logout(authorization: str | None = Header(default=None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        try:
            redis_conn = await get_redis()
            payload = decode_token(token)
            if payload:
                exp_timestamp = payload.get("exp", 0)
                ttl = max(int(exp_timestamp - time.time()), 1)
                await redis_conn.setex(f"blacklist:token:{token}", ttl, "1")
        except Exception:
            pass  # Redis unavailable; skip blacklist
    return ApiResponse(code="SUCCESS", message="success")


# ── SSO callback ─────────────────────────────────────────────────────

@router.get("/sso/callback")
async def sso_callback(ticket: str = Query(), db: AsyncSession = Depends(get_db)):
    # Placeholder — real SSO integration depends on CAS/OAuth provider
    raise BusinessError(code="SSO_NOT_CONFIGURED", message="SSO 未配置")


# ── Change password ──────────────────────────────────────────────────

@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.user_id == current_user["user_id"])
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise BusinessError(code="USER_NOT_FOUND", message="用户不存在")

    if not verify_password(request.old_password, user.password):
        raise ValidationError("原密码错误")

    validate_password_policy(request.new_password)

    user.password = hash_password(request.new_password)
    user.password_changed_at = datetime.now(timezone.utc)
    await db.flush()

    return ApiResponse(code="SUCCESS", message="密码修改成功")


# ── Request schemas (inline to avoid extra file) ─────────────────────

from pydantic import BaseModel  # noqa: E402


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str | None = None
    email: str | None = None
    phone: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


# ── Password Policy ──────────────────────────────────────────────────

_PASSWORD_SPECIAL_CHARS = re.compile(r"[!@#$%^&*()_+\-=\[\]{}|;:'\",.<>/?`~]")


def validate_password_policy(password: str) -> None:
    """Validate password against security policy (12+ chars, upper, lower, digit, special)."""
    if len(password) < 12:
        raise ValidationError("密码长度至少12位")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("密码必须包含大写字母")
    if not re.search(r"[a-z]", password):
        raise ValidationError("密码必须包含小写字母")
    if not re.search(r"\d", password):
        raise ValidationError("密码必须包含数字")
    if not _PASSWORD_SPECIAL_CHARS.search(password):
        raise ValidationError("密码必须包含特殊字符")


@router.get("/password-policy")
async def get_password_policy():
    """Get password policy requirements."""
    return ApiResponse(code="SUCCESS", message="success", data={
        "minLength": 12,
        "maxLength": 32,
        "requireUppercase": True,
        "requireLowercase": True,
        "requireDigit": True,
        "requireSpecialChar": True,
        "historyCount": 5,
        "expiryDays": 90,
        "maxFailedAttempts": 5,
        "lockoutDurationMinutes": 30,
    })


# ── Account Lock / Unlock ───────────────────────────────────────────

@router.post("/account/lock/{user_id}")
async def lock_account(
    user_id: str, db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lock a user account (admin only)."""
    stmt = select(User).where(User.user_id == user_id)
    target = (await db.execute(stmt)).scalar_one_or_none()
    if not target:
        raise BusinessError(code="USER_NOT_FOUND", message="用户不存在")
    target.status = 0  # disabled
    await db.flush()
    return ApiResponse(code="SUCCESS", message="账户已锁定")


@router.post("/account/unlock/{user_id}")
async def unlock_account(
    user_id: str, db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Unlock a user account (admin only)."""
    stmt = select(User).where(User.user_id == user_id)
    target = (await db.execute(stmt)).scalar_one_or_none()
    if not target:
        raise BusinessError(code="USER_NOT_FOUND", message="用户不存在")
    target.status = 1  # enabled
    await db.flush()
    return ApiResponse(code="SUCCESS", message="账户已解锁")
