"""Job alert matching and notification service."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def match_alerts_for_job(
    db_session: AsyncSession,
    job: Any,
) -> list[Any]:
    """Find alerts whose query/filters match a newly-ingested *job*.

    Returns a list of ``JobAlert`` ORM instances whose criteria overlap
    with the provided job.
    """
    from app.models.user import JobAlert  # late import

    stmt = select(JobAlert).where(JobAlert.is_active.is_(True))
    result = await db_session.execute(stmt)
    alerts = result.scalars().all()

    matched: list[Any] = []
    for alert in alerts:
        if _alert_matches_job(alert, job):
            matched.append(alert)

    return matched


def _alert_matches_job(alert: Any, job: Any) -> bool:
    """Determine whether a single alert's criteria match *job*.

    This is a simple keyword-based check.  A production implementation would
    parse the alert's OpenSearch DSL filters and evaluate them against the
    job's attributes.
    """
    query_lower = (alert.query or "").lower()
    if not query_lower:
        return False

    # Check title and company name for a naive keyword match
    title = getattr(job, "title", "") or ""
    company = getattr(job, "company_name", "") or ""
    skills = getattr(job, "skills", []) or []

    searchable = f"{title} {company} {' '.join(skills)}".lower()
    return query_lower in searchable


async def send_alert_notification(
    alert: Any,
    jobs: list[Any],
) -> None:
    """Send an alert notification to the user (placeholder).

    In production this would dispatch an email via SES / SendGrid, a push
    notification, or a webhook depending on ``alert.channel``.
    """
    logger.info(
        "PLACEHOLDER: Would send %s notification for alert %s (%d jobs)",
        getattr(alert, "channel", "email"),
        getattr(alert, "id", "?"),
        len(jobs),
    )
