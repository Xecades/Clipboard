"""
Authentication and authorization utilities.
"""

import os
import secrets
from datetime import UTC, datetime, timedelta

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

# Load environment variables from .env file
load_dotenv()

# Configuration
_SECRET_KEY = os.getenv("SECRET_KEY")
if not _SECRET_KEY:
    raise ValueError(
        "SECRET_KEY environment variable is required. "
        "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )
SECRET_KEY: str = _SECRET_KEY

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

_FIXED_PASSWORD = os.getenv("CLIPBOARD_PASSWORD")
if not _FIXED_PASSWORD:
    raise ValueError(
        "CLIPBOARD_PASSWORD environment variable is required. "
        "Please set a strong password in your .env file."
    )
FIXED_PASSWORD: str = _FIXED_PASSWORD

security = HTTPBearer()


def verify_password(password: str) -> bool:
    """Verify if the provided password matches the fixed password.

    Uses constant-time comparison to prevent timing attacks.
    """
    return secrets.compare_digest(password, FIXED_PASSWORD)


def create_access_token(data: dict) -> str:
    """Create a JWT access token with 7 days expiration."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> bool:
    """Verify if the JWT token is valid."""
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except JWTError:
        return False


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to verify JWT token from Authorization header.
    Raises HTTPException if token is invalid.
    """
    token = credentials.credentials

    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"authenticated": True}
