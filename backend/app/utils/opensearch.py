"""OpenSearch client setup and index management utilities."""

from __future__ import annotations

import logging

from opensearchpy import AsyncOpenSearch

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Index configuration
# ---------------------------------------------------------------------------

JOB_INDEX_NAME = "jobs"

JOB_INDEX_MAPPING: dict = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    },
    "mappings": {
        "properties": {
            # ── Identifiers ───────────────────────────────────────
            "id": {"type": "keyword"},
            "company_id": {"type": "keyword"},
            "dedup_hash": {"type": "keyword"},

            # ── Text fields (full-text searchable) ────────────────
            "title": {
                "type": "text",
                "analyzer": "standard",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "description_summary": {"type": "text", "analyzer": "standard"},
            "company_name": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "location_city": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 128}},
            },
            "location_state": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 128}},
            },

            # ── Keyword / enum fields ─────────────────────────────
            "job_type": {"type": "keyword"},
            "work_mode": {"type": "keyword"},
            "department": {"type": "keyword"},
            "seniority_level": {"type": "keyword"},
            "apply_mode": {"type": "keyword"},
            "skills": {"type": "keyword"},

            # ── Numeric fields ────────────────────────────────────
            "experience_min_years": {"type": "integer"},
            "experience_max_years": {"type": "integer"},
            "salary_min": {"type": "integer"},
            "salary_max": {"type": "integer"},
            "quality_score": {"type": "float"},
            "source_count": {"type": "integer"},

            # ── Date fields ───────────────────────────────────────
            "posted_date": {"type": "date"},
            "first_seen_at": {"type": "date"},
            "last_verified_at": {"type": "date"},

            # ── Boolean fields ────────────────────────────────────
            "is_active": {"type": "boolean"},
        }
    },
}


# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------


async def create_opensearch_client(url: str) -> AsyncOpenSearch:
    """Create and return an ``AsyncOpenSearch`` client.

    Parameters
    ----------
    url:
        Full URL to the OpenSearch cluster (e.g. ``http://localhost:9200``).
    """
    client = AsyncOpenSearch(
        hosts=[url],
        use_ssl=url.startswith("https"),
        verify_certs=False,
        ssl_show_warn=False,
    )
    return client


async def ensure_index_exists(client: AsyncOpenSearch) -> None:
    """Create the *jobs* index with the predefined mapping if it doesn't exist."""
    exists = await client.indices.exists(index=JOB_INDEX_NAME)
    if not exists:
        await client.indices.create(index=JOB_INDEX_NAME, body=JOB_INDEX_MAPPING)
        logger.info("Created OpenSearch index '%s'", JOB_INDEX_NAME)
    else:
        logger.debug("OpenSearch index '%s' already exists", JOB_INDEX_NAME)
