"""Celery tasks for verifying job freshness."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone

import httpx
from celery import shared_task

logger = logging.getLogger(__name__)

# Jobs not verified within this many hours are candidates for re-check
VERIFICATION_WINDOW_HOURS = 48

# Jobs not verified within this many days are marked stale/inactive
STALE_THRESHOLD_DAYS = int(os.getenv("STALE_THRESHOLD_DAYS", "7"))


def _get_sync_session():
    """Create a synchronous SQLAlchemy session for Celery tasks."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/joblens",
    )
    database_url = database_url.replace("+asyncpg", "+psycopg2")
    engine = create_engine(database_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    return Session()


def _check_url_alive(url: str) -> bool:
    """Send an HTTP HEAD request to determine if a URL is still live.

    Returns ``False`` if the server responds with 404 or 410 (Gone), or if
    the request fails entirely.
    """
    try:
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            response = client.head(url)
            if response.status_code in (404, 410):
                return False
            return True
    except httpx.HTTPError:
        logger.debug("HTTP error checking URL %s", url)
        return False


@shared_task(name="tasks.freshness_tasks.verify_job_freshness")
def verify_job_freshness() -> str:
    """Find active jobs whose sources have not been verified in the last
    48 hours, check if source URLs are still live, and mark the job
    inactive if *all* sources return 404/410.
    """
    session = _get_sync_session()
    try:
        from app.models.job import Job, JobSource

        threshold = datetime.now(timezone.utc) - timedelta(hours=VERIFICATION_WINDOW_HOURS)

        # Find active jobs with at least one source not recently verified
        jobs = (
            session.query(Job)
            .filter(
                Job.is_active.is_(True),
                (Job.last_verified_at.is_(None)) | (Job.last_verified_at < threshold),
            )
            .all()
        )

        if not jobs:
            logger.info("No jobs require freshness verification.")
            return "no jobs to verify"

        verified_count = 0
        deactivated_count = 0

        for job in jobs:
            sources = (
                session.query(JobSource)
                .filter(JobSource.job_id == job.id, JobSource.is_active.is_(True))
                .all()
            )

            if not sources:
                # No active sources — mark job inactive
                job.is_active = False
                deactivated_count += 1
                continue

            any_alive = False
            for source in sources:
                if source.source_url and _check_url_alive(source.source_url):
                    any_alive = True
                    source.last_verified_at = datetime.now(timezone.utc)
                elif source.source_url:
                    source.is_active = False
                    source.last_verified_at = datetime.now(timezone.utc)

            now = datetime.now(timezone.utc)
            job.last_verified_at = now

            if not any_alive:
                job.is_active = False
                deactivated_count += 1
            else:
                verified_count += 1

        session.commit()
        logger.info(
            "Freshness check complete: %d verified, %d deactivated.",
            verified_count,
            deactivated_count,
        )
        return f"verified {verified_count}, deactivated {deactivated_count}"
    except Exception:
        session.rollback()
        logger.exception("verify_job_freshness failed.")
        raise
    finally:
        session.close()


@shared_task(name="tasks.freshness_tasks.mark_stale_jobs")
def mark_stale_jobs() -> str:
    """Mark jobs as inactive if they have not been verified within the
    configurable stale threshold (default: 7 days).
    """
    session = _get_sync_session()
    try:
        from app.models.job import Job

        threshold = datetime.now(timezone.utc) - timedelta(days=STALE_THRESHOLD_DAYS)

        stale_jobs = (
            session.query(Job)
            .filter(
                Job.is_active.is_(True),
                (Job.last_verified_at.is_(None)) | (Job.last_verified_at < threshold),
            )
            .all()
        )

        count = 0
        for job in stale_jobs:
            job.is_active = False
            count += 1

        session.commit()
        logger.info("Marked %d stale jobs as inactive (threshold=%d days).", count, STALE_THRESHOLD_DAYS)
        return f"marked {count} stale jobs inactive"
    except Exception:
        session.rollback()
        logger.exception("mark_stale_jobs failed.")
        raise
    finally:
        session.close()
