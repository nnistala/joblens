"""Pydantic v2 schemas for Job-related request/response payloads."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class JobSearchParams(BaseModel):
    q: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    job_type: Optional[str] = None
    work_mode: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    salary_min: Optional[int] = None
    page: int = 1
    page_size: int = 20


# ---------------------------------------------------------------------------
# Nested helpers (declared before the models that reference them)
# ---------------------------------------------------------------------------

class JobSourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_platform: str
    source_url: str
    crawled_at: Optional[datetime] = None
    is_active: bool


# Forward-ref friendly import – CompanyBrief lives in the company schema file.
from app.schemas.company import CompanyBrief  # noqa: E402


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class JobBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    company_name: str
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    work_mode: Optional[str] = None
    job_type: Optional[str] = None
    experience_min_years: Optional[int] = None
    experience_max_years: Optional[int] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    description_summary: Optional[str] = None
    skills: list[str] = []
    posted_date: Optional[datetime] = None
    source_count: int = 0
    apply_mode: Optional[str] = None
    quality_score: Optional[float] = None


class JobDetail(JobBrief):
    title_raw: Optional[str] = None
    location_raw: Optional[str] = None
    department: Optional[str] = None
    seniority_level: Optional[str] = None
    first_seen_at: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None
    is_active: bool = True
    company: Optional[CompanyBrief] = None
    sources: list[JobSourceOut] = []


class JobSearchResponse(BaseModel):
    jobs: list[JobBrief]
    total: int
    page: int
    page_size: int
    total_pages: int
