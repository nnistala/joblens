"""Pydantic v2 schemas for Company-related request/response payloads."""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CompanyBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    is_verified: bool = False


class CompanyDetail(CompanyBrief):
    size_bucket: Optional[str] = None
    career_page_url: Optional[str] = None
    careers_ats_platform: Optional[str] = None
    is_hr_direct: bool = False
    job_count: int = 0


class CompanyListResponse(BaseModel):
    companies: list[CompanyBrief]
    total: int
