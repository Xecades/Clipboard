"""
Data models for the clipboard application.
"""

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    """Login request with password."""

    password: str = Field(..., max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password is not empty after stripping."""
        if not v.strip():
            raise ValueError("Password cannot be empty")
        return v


class LoginResponse(BaseModel):
    """Login response with JWT token."""

    token: str


class ClipboardData(BaseModel):
    """Clipboard content data."""

    content: str


class UpdateRequest(BaseModel):
    """Request to update clipboard content."""

    content: str = Field(..., max_length=1024 * 1024)  # 1MB limit


class StatusResponse(BaseModel):
    """Response with character and selection statistics."""

    length: int
    selected: int = 0
