"""CRUD operations for User, SavedJob, and JobAlert models."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import JobAlert, SavedJob, User


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Look up a user by email address."""
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: dict[str, Any]) -> User:
    """Insert a new user row."""
    user = User(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_profile(
    db: AsyncSession,
    user_id: uuid.UUID,
    update_data: dict[str, Any],
) -> User | None:
    """Update profile fields for an existing user."""
    user = await db.get(User, user_id)
    if user is None:
        return None
    for key, value in update_data.items():
        if value is not None:
            setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Saved jobs
# ---------------------------------------------------------------------------


async def get_saved_jobs(
    db: AsyncSession,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20,
) -> list[SavedJob]:
    """Return a user's saved jobs, most recent first."""
    stmt = (
        select(SavedJob)
        .where(SavedJob.user_id == user_id)
        .order_by(SavedJob.saved_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def save_job(
    db: AsyncSession,
    user_id: uuid.UUID,
    job_id: uuid.UUID,
) -> SavedJob:
    """Save a job for a user (idempotent-ish: does not check for duplicates)."""
    saved = SavedJob(user_id=user_id, job_id=job_id)
    db.add(saved)
    await db.commit()
    await db.refresh(saved)
    return saved


async def unsave_job(
    db: AsyncSession,
    user_id: uuid.UUID,
    job_id: uuid.UUID,
) -> bool:
    """Remove a saved job. Returns ``True`` if a row was deleted."""
    stmt = delete(SavedJob).where(
        SavedJob.user_id == user_id,
        SavedJob.job_id == job_id,
    )
    result = await db.execute(stmt)
    await db.commit()
    return (result.rowcount or 0) > 0


# ---------------------------------------------------------------------------
# Job alerts
# ---------------------------------------------------------------------------


async def create_alert(
    db: AsyncSession,
    user_id: uuid.UUID,
    alert_data: dict[str, Any],
) -> JobAlert:
    """Create a new job alert for a user."""
    alert = JobAlert(user_id=user_id, **alert_data)
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


async def get_user_alerts(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[JobAlert]:
    """Return all alerts belonging to a user."""
    stmt = (
        select(JobAlert)
        .where(JobAlert.user_id == user_id)
        .order_by(JobAlert.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_alert(
    db: AsyncSession,
    alert_id: uuid.UUID,
    user_id: uuid.UUID,
    update_data: dict[str, Any],
) -> JobAlert | None:
    """Update an alert owned by *user_id*. Returns ``None`` if not found."""
    stmt = select(JobAlert).where(
        JobAlert.id == alert_id,
        JobAlert.user_id == user_id,
    )
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if alert is None:
        return None
    for key, value in update_data.items():
        if value is not None:
            setattr(alert, key, value)
    await db.commit()
    await db.refresh(alert)
    return alert


async def delete_alert(
    db: AsyncSession,
    alert_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """Delete an alert owned by *user_id*. Returns ``True`` if deleted."""
    stmt = delete(JobAlert).where(
        JobAlert.id == alert_id,
        JobAlert.user_id == user_id,
    )
    result = await db.execute(stmt)
    await db.commit()
    return (result.rowcount or 0) > 0
