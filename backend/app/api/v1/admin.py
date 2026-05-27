"""
Admin endpoints for platform stats and crawler monitoring.
All endpoints require admin privileges.
"""

from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["Admin"])


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class PlatformStats(BaseModel):
    total_jobs: int
    total_companies: int
    total_users: int
    total_sources: int
    jobs_added_today: int
    jobs_added_this_week: int


class CrawlerInstanceStatus(BaseModel):
    crawler_name: str
    status: str  # running | idle | error | disabled
    last_run_at: Optional[datetime] = None
    last_run_duration_seconds: Optional[float] = None
    jobs_crawled_last_run: int = 0
    error_message: Optional[str] = None


class CrawlerStatusResponse(BaseModel):
    crawlers: List[CrawlerInstanceStatus]
    overall_health: str  # healthy | degraded | down


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/stats", response_model=PlatformStats)
async def get_platform_stats(
    admin_user=Depends(get_current_admin_user),
    # db=Depends(get_db),
):
    """
    Return aggregate platform statistics.
    """
    # total_jobs = await crud.job.count(db)
    # total_companies = await crud.company.count(db)
    # total_users = await crud.user.count(db)
    # total_sources = await crud.job_source.count(db)
    # jobs_today = await crud.job.count_since(db, days=1)
    # jobs_week = await crud.job.count_since(db, days=7)
    # return PlatformStats(
    #     total_jobs=total_jobs,
    #     total_companies=total_companies,
    #     total_users=total_users,
    #     total_sources=total_sources,
    #     jobs_added_today=jobs_today,
    #     jobs_added_this_week=jobs_week,
    # )
    return PlatformStats(
        total_jobs=0,
        total_companies=0,
        total_users=0,
        total_sources=0,
        jobs_added_today=0,
        jobs_added_this_week=0,
    )


@router.get("/crawler-status", response_model=CrawlerStatusResponse)
async def get_crawler_status(
    admin_user=Depends(get_current_admin_user),
    # db=Depends(get_db),
):
    """
    Return the health status of all configured crawlers.
    """
    # TODO: query crawler_runs table or health-check service
    # crawlers = await services.crawler_monitor.get_all_statuses(db)
    return CrawlerStatusResponse(
        crawlers=[],
        overall_health="healthy",
    )
