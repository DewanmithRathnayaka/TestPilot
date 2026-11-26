"""
Security and Cryptography Utilities
Provides password hashing (Argon2id via pwdlib) and JWT token generation / decoding.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from pwdlib import PasswordHash
from app.core.config import settings

# Initialize modern Argon2id password hasher (recommended by OWASP and FastAPI)
password_hasher = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    """
    Hashes a plain-text password using the Argon2id cryptographic algorithm with random salt.
    Never stores or logs the original plain-text password.
    """
    return password_hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a stored Argon2id hash.
    Uses constant-time comparison to prevent timing side-channel attacks.
    """
    return password_hasher.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a cryptographically signed JSON Web Token (JWT).
    Payload typically contains:
      - 'sub': Subject identifier (username or user ID)
      - 'exp': Expiration timestamp (UTC)
      - 'iat': Issued-at timestamp (UTC)
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": now
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates the signature and expiration time of a JWT.
    Raises jwt.PyJWTError (e.g. ExpiredSignatureError, InvalidTokenError) if invalid.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
    return payload
