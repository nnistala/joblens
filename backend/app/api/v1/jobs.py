"""
Job search and detail endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

# from app.api.deps import get_db

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class JobType(str, Enum):
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    internship = "internship"
    freelance = "freelance"


class WorkMode(str, Enum):
    remote = "remote"
    onsite = "onsite"
    hybrid = "hybrid"


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class CompanyBrief(BaseModel):
    id: UUID
    name: str
    logo_url: Optional[str] = None
    industry: Optional[str] = None

    class Config:
        from_attributes = True


class JobSource(BaseModel):
    source_name: str
    source_url: str
    last_seen_at: datetime

    class Config:
        from_attributes = True


class JobListItem(BaseModel):
    id: UUID
    title: str
    company: CompanyBrief
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    work_mode: Optional[WorkMode] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "INR"
    posted_at: Optional[datetime] = None
    source_count: int = 1

    class Config:
        from_attributes = True


class JobDetail(JobListItem):
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    apply_url: Optional[str] = None
    sources: List[JobSource] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedJobs(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[JobListItem]


class TrendingJob(BaseModel):
    id: UUID
    title: str
    company_name: str
    location: Optional[str] = None
    view_count: int = 0


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/trending", response_model=List[TrendingJob])
async def get_trending_jobs(
    limit: int = Query(10, ge=1, le=50, description="Number of trending jobs to return"),
):
    """
    Return trending / most-viewed jobs.
    """
    # TODO: query OpenSearch or analytics table for popular jobs
    return []


@router.get("/search", response_model=PaginatedJobs)
async def search_jobs(
    q: Optional[str] = Query(None, description="Full-text search query"),
    location: Optional[str] = Query(None, description="City or state filter (e.g. Bangalore, Mumbai)"),
    company: Optional[str] = Query(None, description="Company name filter"),
    job_type: Optional[JobType] = Query(None, description="Job type filter"),
    work_mode: Optional[WorkMode] = Query(None, description="Work mode filter"),
    experience_min: Optional[int] = Query(None, ge=0, description="Minimum years of experience"),
    experience_max: Optional[int] = Query(None, ge=0, description="Maximum years of experience"),
    salary_min: Optional[int] = Query(None, ge=0, description="Minimum salary in INR (annual)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    # db=Depends(get_db),
):
    """
    Search jobs using OpenSearch full-text search with filters.
    Supports pagination.
    """
    # TODO: Build OpenSearch query from parameters
    # from app.services.search import search_jobs as os_search
    # hits, total = await os_search(
    #     q=q, location=location, company=company, job_type=job_type,
    #     work_mode=work_mode, experience_min=experience_min,
    #     experience_max=experience_max, salary_min=salary_min,
    #     offset=(page - 1) * page_size, limit=page_size,
    # )
    return PaginatedJobs(total=0, page=page, page_size=page_size, results=[])


@router.get("/{job_id}", response_model=JobDetail)
async def get_job(
    job_id: UUID,
    # db=Depends(get_db),
):
    """
    Get full job details including company info and all source links.
    """
    # TODO: look up job in database
    # job = await crud.job.get_with_company(db, job_id)
    # if not job:
    #     raise HTTPException(status_code=404, detail="Job not found")
    # return job
    raise HTTPException(status_code=404, detail="Job not found")


@router.get("/{job_id}/sources", response_model=List[JobSource])
async def get_job_sources(
    job_id: UUID,
    # db=Depends(get_db),
):
    """
    Return every source (job board / career page) where this job was found.
    """
    # TODO: look up sources for job
    # sources = await crud.job_source.list_for_job(db, job_id)
    # if not sources:
    #     raise HTTPException(status_code=404, detail="Job not found")
    # return sources
    raise HTTPException(status_code=404, detail="Job not found")
