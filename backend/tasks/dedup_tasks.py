"""Celery tasks for job deduplication."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from celery import shared_task

logger = logging.getLogger(__name__)


def _get_sync_session():
    """Create a synchronous SQLAlchemy session for use in Celery tasks.

    Celery workers run synchronously, so we use a standard (non-async) engine
    derived from the configured DATABASE_URL.
    """
    import os

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/joblens",
    )
    # Ensure we use a sync driver
    database_url = database_url.replace("+asyncpg", "+psycopg2")

    engine = create_engine(database_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    return Session()


@shared_task(name="tasks.dedup_tasks.run_batch_dedup")
def run_batch_dedup() -> str:
    """Find jobs that have not been assigned a dedup_cluster_id and run
    the deduplication pipeline on them.

    The pipeline groups jobs by company + normalised title and assigns a
    shared ``dedup_cluster_id`` to each cluster.
    """
    session = _get_sync_session()
    try:
        from app.models.job import Job

        # Fetch jobs without a dedup cluster
        jobs = (
            session.query(Job)
            .filter(Job.dedup_cluster_id.is_(None), Job.is_active.is_(True))
            .order_by(Job.company_id, Job.title)
            .all()
        )

        if not jobs:
            logger.info("No un-clustered jobs found.")
            return "no jobs to dedup"

        # Simple clustering: group by (company_id, normalised title)
        clusters: dict[tuple, list] = {}
        for job in jobs:
            key = (str(job.company_id), job.title.strip().lower())
            clusters.setdefault(key, []).append(job)

        assigned = 0
        for _key, group in clusters.items():
            cluster_id = uuid.uuid4()
            for job in group:
                job.dedup_cluster_id = cluster_id
                assigned += 1

        session.commit()
        logger.info("Assigned dedup_cluster_id to %d jobs across %d clusters.", assigned, len(clusters))
        return f"deduped {assigned} jobs into {len(clusters)} clusters"
    except Exception:
        session.rollback()
        logger.exception("Batch dedup failed.")
        raise
    finally:
        session.close()


@shared_task(name="tasks.dedup_tasks.merge_duplicate_jobs")
def merge_duplicate_jobs(job_id_1: str, job_id_2: str) -> str:
    """Merge two duplicate jobs, keeping the one with the higher quality
    score and combining their sources.

    The lower-quality job is marked inactive.
    """
    session = _get_sync_session()
    try:
        from app.models.job import Job, JobSource

        job1 = session.query(Job).filter(Job.id == uuid.UUID(job_id_1)).first()
        job2 = session.query(Job).filter(Job.id == uuid.UUID(job_id_2)).first()

        if not job1 or not job2:
            logger.warning("One or both jobs not found: %s, %s", job_id_1, job_id_2)
            return "job(s) not found"

        # Keep the job with higher quality_score as the primary
        primary, secondary = (job1, job2) if job1.quality_score >= job2.quality_score else (job2, job1)

        # Re-assign sources from secondary to primary
        secondary_sources = session.query(JobSource).filter(JobSource.job_id == secondary.id).all()
        for source in secondary_sources:
            source.job_id = primary.id

        # Update source count
        primary.source_count = (
            session.query(JobSource).filter(JobSource.job_id == primary.id).count()
        )

        # Ensure they share a dedup_cluster_id
        if not primary.dedup_cluster_id:
            primary.dedup_cluster_id = uuid.uuid4()
        secondary.dedup_cluster_id = primary.dedup_cluster_id

        # Mark secondary as inactive
        secondary.is_active = False
        secondary.updated_at = datetime.now(timezone.utc)

        session.commit()
        logger.info(
            "Merged job %s into %s (primary). Secondary marked inactive.",
            secondary.id,
            primary.id,
        )
        return f"merged {secondary.id} into {primary.id}"
    except Exception:
        session.rollback()
        logger.exception("Merge failed for jobs %s and %s.", job_id_1, job_id_2)
        raise
    finally:
        session.close()
