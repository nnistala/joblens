"""CRUD operations for the Job model."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job


async def get_job(db: AsyncSession, job_id: uuid.UUID) -> Job | None:
    """Return a single job by primary key, or ``None``."""
    return await db.get(Job, job_id)


async def get_jobs_by_company(
    db: AsyncSession,
    company_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20,
) -> list[Job]:
    """Return jobs belonging to a given company."""
    stmt = (
        select(Job)
        .where(Job.company_id == company_id, Job.is_active.is_(True))
        .order_by(Job.posted_date.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_job(db: AsyncSession, job_data: dict[str, Any]) -> Job:
    """Insert a new job row and return the ORM instance."""
    job = Job(**job_data)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def update_job(
    db: AsyncSession,
    job_id: uuid.UUID,
    update_data: dict[str, Any],
) -> Job | None:
    """Update an existing job and return the refreshed instance."""
    job = await db.get(Job, job_id)
    if job is None:
        return None
    for key, value in update_data.items():
        setattr(job, key, value)
    await db.commit()
    await db.refresh(job)
    return job


async def deactivate_stale_jobs(db: AsyncSession, hours: int = 48) -> int:
    """Mark jobs not verified within *hours* as inactive.

    Returns the number of rows affected.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    stmt = (
        update(Job)
        .where(Job.is_active.is_(True), Job.last_verified_at < cutoff)
        .values(is_active=False)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount  # type: ignore[return-value]
