"""Pydantic v2 schemas for User-related request/response payloads."""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


# ---------------------------------------------------------------------------
# Auth requests
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepass",
                "name": "Jane Doe",
            }
        }
    )

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    """Google One-Tap / OAuth ID-token exchange."""
    credential: str


# ---------------------------------------------------------------------------
# Token response
# ---------------------------------------------------------------------------

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str
    subscription_tier: Optional[str] = None
    skills: list[str] = []
    experience_years: Optional[int] = None
    preferred_locations: list[str] = []
    preferred_roles: list[str] = []


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    skills: Optional[list[str]] = None
    experience_years: Optional[int] = None
    preferred_locations: Optional[list[str]] = None
    preferred_roles: Optional[list[str]] = None
