"""
Data models for the clipboard application.
"""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Login request with password."""

    password: str


class LoginResponse(BaseModel):
    """Login response with JWT token."""

    token: str


class ClipboardData(BaseModel):
    """Clipboard content data."""

    content: str


class UpdateRequest(BaseModel):
    """Request to update clipboard content."""

    content: str


class StatusResponse(BaseModel):
    """Response with character and selection statistics."""

    length: int
    selected: int = 0
