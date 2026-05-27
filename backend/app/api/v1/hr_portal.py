"""
HR Portal endpoints for company registration and career-page onboarding.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, HttpUrl

from app.api.deps import get_current_user

router = APIRouter(prefix="/hr", tags=["HR Portal"])


# ---------------------------------------------------------------------------
# Enums and schemas
# ---------------------------------------------------------------------------

class ATSPlatform(str, Enum):
    greenhouse = "greenhouse"
    lever = "lever"
    workday = "workday"
    taleo = "taleo"
    icims = "icims"
    smartrecruiters = "smartrecruiters"
    freshteam = "freshteam"
    zoho_recruit = "zoho_recruit"
    custom = "custom"
    unknown = "unknown"


class RegistrationStatus(str, Enum):
    pending = "pending"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    crawling = "crawling"
    active = "active"


class RegisterCompanyRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=300)
    career_page_url: str = Field(..., description="URL of the company's careers page")
    ats_platform: ATSPlatform = Field(ATSPlatform.unknown, description="ATS platform used")
    contact_email: Optional[str] = Field(None, description="HR contact email")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes for the review team")


class CompanyRegistration(BaseModel):
    id: UUID
    company_name: str
    career_page_url: str
    ats_platform: ATSPlatform
    contact_email: Optional[str] = None
    notes: Optional[str] = None
    status: RegistrationStatus
    reviewer_notes: Optional[str] = None
    submitted_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/register-company",
    response_model=CompanyRegistration,
    status_code=status.HTTP_201_CREATED,
)
async def register_company(
    payload: RegisterCompanyRequest,
    current_user=Depends(get_current_user),
    # db=Depends(get_db),
):
    """
    Submit a company's career page for onboarding into the JobLens crawler.
    The request goes into a review queue before crawling begins.
    """
    # registration = await crud.hr_registration.create(
    #     db,
    #     submitted_by=current_user.id,
    #     company_name=payload.company_name,
    #     career_page_url=str(payload.career_page_url),
    #     ats_platform=payload.ats_platform,
    #     contact_email=payload.contact_email,
    #     notes=payload.notes,
    # )
    # return registration
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Company registration not implemented yet",
    )


@router.get("/registrations", response_model=List[CompanyRegistration])
async def list_registrations(
    current_user=Depends(get_current_user),
    # db=Depends(get_db),
):
    """
    List all company registration requests submitted by the current user.
    """
    # registrations = await crud.hr_registration.list_for_user(
    #     db, user_id=current_user.id
    # )
    # return registrations
    return []


@router.get("/registrations/{reg_id}", response_model=CompanyRegistration)
async def get_registration(
    reg_id: UUID,
    current_user=Depends(get_current_user),
    # db=Depends(get_db),
):
    """
    Get the status and details of a specific company registration.
    """
    # registration = await crud.hr_registration.get(db, reg_id)
    # if not registration or registration.submitted_by != current_user.id:
    #     raise HTTPException(status_code=404, detail="Registration not found")
    # return registration
    raise HTTPException(status_code=404, detail="Registration not found")
