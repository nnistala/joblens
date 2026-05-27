"""Celery tasks for sending job alert notifications."""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timedelta, timezone

from celery import shared_task

logger = logging.getLogger(__name__)


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


def _match_jobs_for_alert(session, alert, since: datetime) -> list:
    """Return jobs created since ``since`` that match the alert's query
    and filters.  This is a simplified keyword-based matcher; a production
    implementation would query OpenSearch.
    """
    from app.models.job import Job

    query = session.query(Job).filter(
        Job.is_active.is_(True),
        Job.created_at >= since,
    )

    # Basic keyword match on title
    if alert.query:
        keywords = alert.query.strip().split()
        for kw in keywords:
            query = query.filter(Job.title.ilike(f"%{kw}%"))

    # Apply optional filters from JSONB
    if alert.filters:
        if "location_city" in alert.filters:
            query = query.filter(Job.location_city == alert.filters["location_city"])
        if "work_mode" in alert.filters:
            query = query.filter(Job.work_mode == alert.filters["work_mode"])
        if "job_type" in alert.filters:
            query = query.filter(Job.job_type == alert.filters["job_type"])

    return query.all()


def _send_email_notification(user_email: str, alert_name: str, jobs: list) -> None:
    """Send an email notification for matched jobs.

    In production this would call an email service (SES, SendGrid, etc.).
    For now we log the action.
    """
    logger.info(
        "Sending email to %s for alert '%s' with %d matched jobs.",
        user_email,
        alert_name,
        len(jobs),
    )
    # TODO: integrate with email provider


@shared_task(name="tasks.alert_tasks.send_daily_alerts")
def send_daily_alerts() -> str:
    """Find all active daily alerts, match against new jobs from the last
    24 hours, and send email notifications.
    """
    session = _get_sync_session()
    try:
        from app.models.user import AlertFrequency, JobAlert, User

        since = datetime.now(timezone.utc) - timedelta(hours=24)

        alerts = (
            session.query(JobAlert)
            .filter(
                JobAlert.is_active.is_(True),
                JobAlert.frequency == AlertFrequency.daily,
            )
            .all()
        )

        sent_count = 0
        for alert in alerts:
            matched_jobs = _match_jobs_for_alert(session, alert, since)
            if not matched_jobs:
                continue

            user = session.query(User).filter(User.id == alert.user_id).first()
            if not user:
                continue

            _send_email_notification(user.email, alert.name, matched_jobs)
            alert.last_triggered_at = datetime.now(timezone.utc)
            sent_count += 1

        session.commit()
        logger.info("Sent %d daily alert notifications.", sent_count)
        return f"sent {sent_count} daily alerts"
    except Exception:
        session.rollback()
        logger.exception("send_daily_alerts failed.")
        raise
    finally:
        session.close()


@shared_task(name="tasks.alert_tasks.send_weekly_alerts")
def send_weekly_alerts() -> str:
    """Find all active weekly alerts, match against new jobs from the last
    7 days, and send email notifications.
    """
    session = _get_sync_session()
    try:
        from app.models.user import AlertFrequency, JobAlert, User

        since = datetime.now(timezone.utc) - timedelta(days=7)

        alerts = (
            session.query(JobAlert)
            .filter(
                JobAlert.is_active.is_(True),
                JobAlert.frequency == AlertFrequency.weekly,
            )
            .all()
        )

        sent_count = 0
        for alert in alerts:
            matched_jobs = _match_jobs_for_alert(session, alert, since)
            if not matched_jobs:
                continue

            user = session.query(User).filter(User.id == alert.user_id).first()
            if not user:
                continue

            _send_email_notification(user.email, alert.name, matched_jobs)
            alert.last_triggered_at = datetime.now(timezone.utc)
            sent_count += 1

        session.commit()
        logger.info("Sent %d weekly alert notifications.", sent_count)
        return f"sent {sent_count} weekly alerts"
    except Exception:
        session.rollback()
        logger.exception("send_weekly_alerts failed.")
        raise
    finally:
        session.close()


@shared_task(name="tasks.alert_tasks.process_instant_alert")
def process_instant_alert(alert_id: str, job_id: str) -> str:
    """Send an instant alert notification for a specific new job match."""
    session = _get_sync_session()
    try:
        from app.models.job import Job
        from app.models.user import JobAlert, User

        alert = session.query(JobAlert).filter(JobAlert.id == uuid.UUID(alert_id)).first()
        job = session.query(Job).filter(Job.id == uuid.UUID(job_id)).first()

        if not alert or not job:
            logger.warning("Alert or job not found: alert=%s job=%s", alert_id, job_id)
            return "alert or job not found"

        if not alert.is_active:
            return "alert is inactive"

        user = session.query(User).filter(User.id == alert.user_id).first()
        if not user:
            return "user not found"

        _send_email_notification(user.email, alert.name, [job])
        alert.last_triggered_at = datetime.now(timezone.utc)
        session.commit()

        logger.info("Sent instant alert %s for job %s to %s.", alert_id, job_id, user.email)
        return f"instant alert sent to {user.email}"
    except Exception:
        session.rollback()
        logger.exception("process_instant_alert failed for alert=%s job=%s.", alert_id, job_id)
        raise
    finally:
        session.close()
