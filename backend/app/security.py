from datetime import datetime, timedelta
from jose import jwt
from .config import settings


def hash_password(password: str) -> str:
    # Simple placeholder hashing for tests; in production use passlib bcrypt
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def _encode_jwt(subject: str, expires_delta: timedelta, extra: dict | None = None) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, extra_claims: dict | None = None) -> str:
    return _encode_jwt(subject, timedelta(minutes=settings.access_token_expires_minutes), extra_claims)


def create_refresh_token(subject: str) -> str:
    return _encode_jwt(subject, timedelta(days=settings.refresh_token_expires_days), {"type": "refresh"})

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, extra_claims: Optional[dict[str, Any]] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expires_minutes)
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expires_days)
    to_encode = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)