"""
Company listing and detail endpoints.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

# from app.api.deps import get_db

router = APIRouter(prefix="/companies", tags=["Companies"])


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class CompanyListItem(BaseModel):
    id: UUID
    name: str
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None
    active_job_count: int = 0

    class Config:
        from_attributes = True


class CompanyDetail(BaseModel):
    id: UUID
    name: str
    logo_url: Optional[str] = None
    website: Optional[str] = None
    careers_url: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    headquarters: Optional[str] = None
    description: Optional[str] = None
    glassdoor_rating: Optional[float] = None
    active_job_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedCompanies(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[CompanyListItem]


class CompanyJobItem(BaseModel):
    id: UUID
    title: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    work_mode: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "INR"
    posted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedCompanyJobs(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[CompanyJobItem]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=PaginatedCompanies)
async def list_companies(
    q: Optional[str] = Query(None, description="Search company by name"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    # db=Depends(get_db),
):
    """
    List companies with optional search and industry filter.
    """
    # TODO: query companies table with filters
    # companies, total = await crud.company.search(
    #     db, q=q, industry=industry,
    #     offset=(page - 1) * page_size, limit=page_size,
    # )
    return PaginatedCompanies(total=0, page=page, page_size=page_size, results=[])


@router.get("/{company_id}", response_model=CompanyDetail)
async def get_company(
    company_id: UUID,
    # db=Depends(get_db),
):
    """
    Get full company profile.
    """
    # company = await crud.company.get(db, company_id)
    # if not company:
    #     raise HTTPException(status_code=404, detail="Company not found")
    # return company
    raise HTTPException(status_code=404, detail="Company not found")


@router.get("/{company_id}/jobs", response_model=PaginatedCompanyJobs)
async def get_company_jobs(
    company_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    # db=Depends(get_db),
):
    """
    List all active job postings for a given company.
    """
    # company = await crud.company.get(db, company_id)
    # if not company:
    #     raise HTTPException(status_code=404, detail="Company not found")
    # jobs, total = await crud.job.list_by_company(
    #     db, company_id=company_id,
    #     offset=(page - 1) * page_size, limit=page_size,
    # )
    raise HTTPException(status_code=404, detail="Company not found")
