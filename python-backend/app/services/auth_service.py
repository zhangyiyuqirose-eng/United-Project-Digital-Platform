"""Auth domain service — wraps login, token, password, and account management."""

from __future__ import annotations

import re
import time
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.dependencies import get_redis
from app.exceptions import BusinessError, RateLimitExceededError, ValidationError
from app.models.auth.models import LoginAttempt, User

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


class AuthService:
    """Encapsulates all authentication business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Authentication ─────────────────────────────────────────────────

    async def authenticate(self, username: str, password: str) -> User | None:
        """Verify credentials and return the User, or None."""
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    async def login(
        self, username: str, password: str, ip_address: str | None = None
    ) -> dict:
        """Authenticate user and return tokens + user info.

        Raises ValidationError on bad credentials, BusinessError on disabled account.
        """
        # Rate limiting
        client_ip = ip_address or "unknown"
        lockout_key = f"login_lockout:{client_ip}"
        attempt_key = f"login_attempts:{client_ip}"

        redis_conn = None
        try:
            redis_conn = await get_redis()
        except Exception:
            pass

        if redis_conn is not None:
            try:
                lockout_remaining = await redis_conn.ttl(lockout_key)
                if lockout_remaining > 0:
                    raise RateLimitExceededError(retry_after=lockout_remaining)
                attempts_raw = await redis_conn.get(attempt_key)
                if attempts_raw and int(attempts_raw) >= 5:
                    await redis_conn.setex(lockout_key, 1800, "1")
                    await redis_conn.delete(attempt_key)
                    raise RateLimitExceededError(retry_after=1800)
            except RateLimitExceededError:
                raise
            except Exception:
                pass

        user = await self.authenticate(username, password)

        if user is None:
            # Log failed attempt for known user
            stmt = select(User).where(User.username == username)
            existing = (await self.db.execute(stmt)).scalar_one_or_none()
            if existing:
                attempt = LoginAttempt(
                    attempt_id=str(uuid.uuid4()),
                    user_id=existing.user_id,
                    username=username,
                    ip_address=ip_address,
                    success=0,
                    failure_reason="密码错误",
                    attempt_time=datetime.now(timezone.utc),
                )
                self.db.add(attempt)
                await self.db.flush()
            if redis_conn is not None:
                try:
                    await redis_conn.incr(attempt_key)
                    await redis_conn.expire(attempt_key, 60)
                except Exception:
                    pass
            raise ValidationError("用户名或密码错误")

        if user.status != 1:
            raise BusinessError(code="ACCOUNT_DISABLED", message="账号已被禁用")

        # Log success
        attempt = LoginAttempt(
            attempt_id=str(uuid.uuid4()),
            user_id=user.user_id,
            username=username,
            ip_address=ip_address,
            success=1,
            attempt_time=datetime.now(timezone.utc),
        )
        self.db.add(attempt)
        await self.db.flush()

        # Reset rate counters
        if redis_conn is not None:
            try:
                await redis_conn.delete(attempt_key, lockout_key)
            except Exception:
                pass

        access_token = create_token(user.user_id, {"role": "admin" if user.dept_id == "1" else "user"})
        refresh_token = create_refresh_token(user.user_id)

        return {
            "token": {"accessToken": access_token, "refreshToken": refresh_token},
            "userInfo": {
                "userId": user.user_id,
                "username": user.username,
                "name": user.name,
                "deptId": user.dept_id,
                "email": user.email,
                "phone": user.phone,
            },
        }

    # ── Token ──────────────────────────────────────────────────────────

    async def refresh_token(self, refresh_token_str: str) -> dict:
        """Validate refresh token and issue a new pair."""
        payload = decode_token(refresh_token_str)
        if payload is None or payload.get("type") != "refresh":
            raise BusinessError(code="INVALID_TOKEN", message="Refresh token 无效或已过期", status_code=401)

        user_id = payload["sub"]
        stmt = select(User).where(User.user_id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise BusinessError(code="USER_NOT_FOUND", message="用户不存在", status_code=401)

        new_access = create_token(user.user_id, {"role": "admin" if user.dept_id == "1" else "user"})
        new_refresh = create_refresh_token(user.user_id)

        return {"accessToken": new_access, "refreshToken": new_refresh}

    # ── Password ───────────────────────────────────────────────────────

    async def change_password(self, user_id: str, old_pwd: str, new_pwd: str) -> None:
        """Change password for a user after verifying old password."""
        stmt = select(User).where(User.user_id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise BusinessError(code="USER_NOT_FOUND", message="用户不存在")

        if not verify_password(old_pwd, user.password):
            raise ValidationError("原密码错误")

        validate_password_policy(new_pwd)

        user.password = hash_password(new_pwd)
        user.password_changed_at = datetime.now(timezone.utc)
        await self.db.flush()

    def get_password_policy(self) -> dict:
        """Return the current password policy requirements."""
        return {
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
        }

    # ── Account ────────────────────────────────────────────────────────

    async def lock_account(self, user_id: str) -> None:
        """Lock (disable) a user account."""
        stmt = select(User).where(User.user_id == user_id)
        target = (await self.db.execute(stmt)).scalar_one_or_none()
        if not target:
            raise BusinessError(code="USER_NOT_FOUND", message="用户不存在")
        target.status = 0
        await self.db.flush()

    async def unlock_account(self, user_id: str) -> None:
        """Unlock (enable) a user account."""
        stmt = select(User).where(User.user_id == user_id)
        target = (await self.db.execute(stmt)).scalar_one_or_none()
        if not target:
            raise BusinessError(code="USER_NOT_FOUND", message="用户不存在")
        target.status = 1
        await self.db.flush()

    # ── Logout ─────────────────────────────────────────────────────────

    async def logout(self, token: str) -> None:
        """Add token to blacklist."""
        try:
            redis_conn = await get_redis()
            payload = decode_token(token)
            if payload:
                exp_timestamp = payload.get("exp", 0)
                ttl = max(int(exp_timestamp - time.time()), 1)
                await redis_conn.setex(f"blacklist:token:{token}", ttl, "1")
        except Exception:
            pass
