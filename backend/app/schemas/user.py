"""
User Pydantic Schemas
Defines request validation models and response shapes for Authentication & User profiles.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    """Data required from client to register a new account."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9_-]+$",
        description="Alphanumeric username (3-50 characters)"
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Password (min 6 characters)"
    )


class UserResponse(BaseModel):
    """
    Public safe profile data returned to client.
    NEVER includes password or hashed_password.
    """
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Response returned upon successful login."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded internal JWT payload."""
    sub: Optional[str] = None
    exp: Optional[int] = None
