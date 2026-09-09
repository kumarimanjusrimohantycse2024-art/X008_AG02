from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt

from app.core.config import get_settings

PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 310_000
JWT_ALGORITHM = "HS256"
JWT_TYPE = "access"


def hash_password(password: str) -> str:
    settings = get_settings()
    if len(password) < settings.password_min_length:
        raise ValueError(f"Password must be at least {settings.password_min_length} characters.")
    if not password:
        raise ValueError("Password cannot be empty.")
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return "$".join(
        [PASSWORD_SCHEME, str(PASSWORD_ITERATIONS), base64.urlsafe_b64encode(salt).decode("ascii"), base64.urlsafe_b64encode(digest).decode("ascii")]
    )


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, iterations_text, salt_text, digest_text = password_hash.split("$", 3)
        if scheme != PASSWORD_SCHEME:
            return False
        iterations = int(iterations_text)
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_text.encode("ascii"))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _validated_jwt_secret() -> str:
    settings = get_settings()
    if settings.environment.lower() in {"production", "staging"} and len(settings.jwt_secret) < 32:
        raise RuntimeError("JWT_SECRET must be at least 32 characters outside development.")
    return settings.jwt_secret


def create_access_token(user_id: UUID, role: str) -> tuple[str, int]:
    settings = get_settings()
    expires_in = settings.access_token_expire_minutes * 60
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "type": JWT_TYPE,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, _validated_jwt_secret(), algorithm=JWT_ALGORITHM), expires_in


def decode_access_token(token: str) -> dict[str, Any]:
    payload = jwt.decode(token, _validated_jwt_secret(), algorithms=[JWT_ALGORITHM], options={"require": ["sub", "exp", "iat", "type"]})
    if payload.get("type") != JWT_TYPE:
        raise jwt.InvalidTokenError("Invalid token type")
    UUID(str(payload["sub"]))
    return payload
