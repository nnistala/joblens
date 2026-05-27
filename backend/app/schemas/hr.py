"""Pydantic v2 schemas for HR Registration request/response payloads."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


class HRRegistrationCreate(BaseModel):
    company_name: str
    career_page_url: HttpUrl
    ats_platform: Optional[str] = None
    feed_url: Optional[HttpUrl] = None


class HRRegistrationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_name: str
    career_page_url: str
    verification_status: Optional[str] = None
    created_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
