"""AI enrichment service (placeholder).

This module will eventually call an LLM to generate concise summaries and
extract structured metadata from raw job descriptions.  For now it returns
a simple truncation.
"""

from __future__ import annotations

_SUMMARY_MAX_LENGTH = 300


async def generate_job_summary(
    title: str,
    description: str,
    company: str,
) -> str:
    """Return a short plain-text summary of the job posting.

    Parameters
    ----------
    title:
        Normalised job title.
    description:
        Raw or HTML-stripped description text.
    company:
        Company name for context.

    Returns
    -------
    str
        A truncated version of *description* (placeholder implementation).
    """
    if not description:
        return f"{title} at {company}"

    summary = description.strip()
    if len(summary) > _SUMMARY_MAX_LENGTH:
        summary = summary[:_SUMMARY_MAX_LENGTH].rsplit(" ", 1)[0] + "..."
    return summary
