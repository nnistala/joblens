"""
User profile, saved jobs, and job alert endpoints.
All endpoints require authentication.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class UserProfile(BaseModel):
    id: UUID
    email: str
    name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: List[str] = []
    preferred_locations: List[str] = []
    preferred_job_types: List[str] = []
    experience_years: Optional[int] = None
    resume_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = Field(None, max_length=15)
    skills: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_job_types: Optional[List[str]] = None
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    resume_url: Optional[str] = None


class SavedJobItem(BaseModel):
    id: UUID
    job_id: UUID
    job_title: str
    company_name: str
    location: Optional[str] = None
    saved_at: datetime

    class Config:
        from_attributes = True


class SavedJobResponse(BaseModel):
    message: str
    job_id: UUID


class JobAlert(BaseModel):
    id: UUID
    name: str
    query: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    work_mode: Optional[str] = None
    experience_min: Optional[int] = None
    salary_min: Optional[int] = None
    frequency: str = "daily"  # daily | weekly | instant
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateAlertRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    query: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    work_mode: Optional[str] = None
    experience_min: Optional[int] = Field(None, ge=0)
    salary_min: Optional[int] = Field(None, ge=0)
    frequency: str = Field("daily", pattern="^(daily|weekly|instant)$")


class UpdateAlertRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    query: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    work_mode: Optional[str] = None
    experience_min: Optional[int] = Field(None, ge=0)
    salary_min: Optional[int] = Field(None, ge=0)
    frequency: Optional[str] = Field(None, pattern="^(daily|weekly|instant)$")
    is_active: Optional[bool] = None


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user=Depends(get_current_user),
):
    """
    Get the authenticated user's full profile.
    """
    return current_user


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    payload: UpdateProfileRequest,
    current_user=Depends(get_current_user),
    # db=Depends(get_db),
):
    """
    Update the authenticated user's profile fields.
    Only provided (non-null) fields are updated.
    """
    # update_data = payload.model_dump(exclude_unset=True)
    # updated_user = await crud.user.update(db, user=current_user, **update_data)
    # return updated_user
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Profile update not implemented yet",
    )


# ---------------------------------------------------------------------------
# Saved jobs
# ---------------------------------------------------------------------------

@router.get("/saved-jobs", response_model=List[SavedJobItem])
async def list_saved_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
    # db=Depends(get_db),
):
    """
    List jobs saved by the current user, newest first.
    """
    # saved = await crud.saved_job.list_for_user(
    #     db, user_id=current_user.id,
    #     offset=(page - 1) * page_size, limit=page_size,
    # )
    # return saved
    return []


@router.post("/saved-jobs/{job_id}", response_model=SavedJobResponse, status_code=status.HTTP_201_CREATED)
async def save_job(
    job_id: UUID,
    current_user=Depends(get_current_user),
    # db=Depends(get_db),
):
    """
    Save a job to the user's saved-jobs list.
    """
    # job = await crud.job.get(db, job_id)
    # if not job:
    #     raise HTTPException(status_code=404, detail="Job not found")
    # existing = await crud.saved_job.get(db, user_id=current_user.id, job_id=job_id)
    # if existing:
    #     raise HTTPException(status_code=409, detail="Job already saved")
    # await crud.saved_job.create(db, user_id=current_user.id, job_id=job_id)
    # return SavedJobResponse(message="Job saved", job_id=job_id)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Save job not implemented yet",
    )


@router.delete("/saved-jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_job(
    job_id: UUID,
    current_user=Depends(get_current_user),
    # db=Depends(get_db),
):
    """
    Remove a job from the user's saved-jobs list.
    """
    # deleted = await crud.saved_job.delete(db, user_id=current_user.id, job_id=job_id)
    # if not deleted:
    #     raise HTTPException(status_code=404, detail="Saved job not found")
    # return None
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Unsave job not implemented yet",
    )


# ---------------------------------------------------------------------------
# Job alerts
# ---------------------------------------------------------------------------

@router.get("/alerts", response_model=List[JobAlert])
async def list_alerts(
    current_user=Depends(get_current_user),
    # db=Depends(get_db),
):
    """
    List all job alerts for the current user.
    """
    # alerts = await crud.job_alert.list_for_user(db, user_id=current_user.id)
    # return alerts
    return []


@router.post("/alerts", response_model=JobAlert, status_code=status.HTTP_201_CREATED)
async def create_alert(
    payload: CreateAlertRequest,
    current_user=Depends(get_current_user),
    # db=Depends(get_db),
):
    """
    Create a new job alert with specified search criteria and notification frequency.
    """
    # alert = await crud.job_alert.create(
    #     db, user_id=current_user.id, **payload.model_dump()
    # )
    # return alert
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Create alert not implemented yet",
    )


@router.put("/alerts/{alert_id}", response_model=JobAlert)
async def update_alert(
    alert_id: UUID,
    payload: UpdateAlertRequest,
    current_user=Depends(get_current_user),
    # db=Depends(get_db),
):
    """
    Update an existing job alert.
    Only provided (non-null) fields are updated.
    """
    # alert = await crud.job_alert.get(db, alert_id)
    # if not alert or alert.user_id != current_user.id:
    #     raise HTTPException(status_code=404, detail="Alert not found")
    # update_data = payload.model_dump(exclude_unset=True)
    # updated = await crud.job_alert.update(db, alert=alert, **update_data)
    # return updated
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update alert not implemented yet",
    )


@router.delete("/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: UUID,
    current_user=Depends(get_current_user),
    # db=Depends(get_db),
):
    """
    Delete a job alert.
    """
    # alert = await crud.job_alert.get(db, alert_id)
    # if not alert or alert.user_id != current_user.id:
    #     raise HTTPException(status_code=404, detail="Alert not found")
    # await crud.job_alert.delete(db, alert_id)
    # return None
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Delete alert not implemented yet",
    )
