"""
StorePipeline — persists normalised, deduplicated items into
the JobLens PostgreSQL database.

Uses synchronous **psycopg2** because Scrapy pipelines run inside the
Twisted reactor on a thread-pool; async drivers are not needed here.

Environment variable ``DATABASE_URL`` must be a standard PostgreSQL
connection string, e.g.::

    postgresql://user:pass@localhost:5432/joblens
"""

import logging
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Optional

import psycopg2
import psycopg2.extras
from scrapy import Spider
from scrapy.exceptions import DropItem

from joblens_crawlers.items import RawJobItem

logger = logging.getLogger(__name__)

# Regex to convert asyncpg-style URLs to psycopg2
_ASYNCPG_RE = re.compile(r"^postgresql\+asyncpg://")


def _sync_dsn(url: str) -> str:
    """Convert ``postgresql+asyncpg://…`` to plain ``postgresql://…``."""
    return _ASYNCPG_RE.sub("postgresql://", url)


class StorePipeline:
    """Upsert jobs and sources into PostgreSQL."""

    def open_spider(self, spider: Spider) -> None:
        dsn = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/joblens",
        )
        dsn = _sync_dsn(dsn)

        try:
            self._conn = psycopg2.connect(dsn)
            self._conn.autocommit = False
            self._cur = self._conn.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            spider.logger.info("StorePipeline: connected to database")
        except psycopg2.Error as exc:
            spider.logger.error("StorePipeline: DB connection failed — %s", exc)
            raise

    def close_spider(self, spider: Spider) -> None:
        try:
            self._conn.commit()
        except Exception:
            self._conn.rollback()
        finally:
            self._cur.close()
            self._conn.close()
            spider.logger.info("StorePipeline: database connection closed")

    # ────────────────────────────────────────────────────────────────
    def process_item(self, item: RawJobItem, spider: Spider) -> RawJobItem:
        dedup_hash = item.get("_dedup_hash")
        if not dedup_hash:
            raise DropItem("Item has no dedup hash — skipping store")

        try:
            company_id = self._get_or_create_company(item)
            existing_job_id = self._find_existing_job(dedup_hash)

            if existing_job_id:
                # Job already exists — add a new source and bump count
                self._add_job_source(existing_job_id, item)
                self._increment_source_count(existing_job_id)
                spider.logger.debug(
                    "Updated existing job %s with new source", existing_job_id
                )
            else:
                # Brand-new job
                job_id = self._create_job(company_id, item, dedup_hash)
                self._add_job_source(job_id, item)
                spider.logger.debug("Created new job %s", job_id)

            self._conn.commit()

        except psycopg2.Error as exc:
            self._conn.rollback()
            spider.logger.error(
                "StorePipeline DB error for '%s': %s",
                item.get("title"),
                exc,
            )

        return item

    # ════════════════════════════════════════════════════════════════
    #  Private helpers
    # ════════════════════════════════════════════════════════════════

    def _get_or_create_company(self, item: RawJobItem) -> uuid.UUID:
        name = item.get("company_name", "").strip()
        if not name:
            name = "Unknown"

        self._cur.execute(
            "SELECT id FROM companies WHERE LOWER(name) = LOWER(%s) LIMIT 1",
            (name,),
        )
        row = self._cur.fetchone()
        if row:
            return row["id"]

        company_id = uuid.uuid4()
        self._cur.execute(
            """
            INSERT INTO companies (id, name, domain, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                str(company_id),
                name,
                item.get("company_domain"),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc),
            ),
        )
        return company_id

    def _find_existing_job(self, dedup_hash: str) -> Optional[uuid.UUID]:
        self._cur.execute(
            """
            SELECT j.id
            FROM jobs j
            JOIN job_sources js ON js.job_id = j.id
            WHERE js.raw_description_hash = %s
            LIMIT 1
            """,
            (dedup_hash,),
        )
        row = self._cur.fetchone()
        return row["id"] if row else None

    def _create_job(
        self,
        company_id: uuid.UUID,
        item: RawJobItem,
        dedup_hash: str,
    ) -> uuid.UUID:
        job_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        self._cur.execute(
            """
            INSERT INTO jobs (
                id, company_id, title, title_raw,
                location_city, location_state, location_country, location_raw,
                job_type, work_mode,
                experience_min_years, experience_max_years,
                salary_min, salary_max, salary_currency,
                description_summary, skills, department,
                posted_date, first_seen_at, last_verified_at,
                is_active, source_count, quality_score,
                apply_mode, direct_apply_url,
                created_at, updated_at
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s
            )
            """,
            (
                str(job_id),
                str(company_id),
                item.get("title", ""),
                item.get("title", ""),
                item.get("_location_city"),
                item.get("_location_state"),
                "India",
                item.get("location_raw"),
                item.get("job_type"),
                item.get("work_mode"),
                item.get("_experience_min"),
                item.get("_experience_max"),
                item.get("_salary_min"),
                item.get("_salary_max"),
                "INR",
                (item.get("description") or "")[:2000] or None,
                item.get("_skills") or None,
                item.get("department"),
                None,  # posted_date — would need date parsing
                now,
                now,
                True,
                1,
                0.0,
                "redirect",
                item.get("apply_url"),
                now,
                now,
            ),
        )
        return job_id

    def _add_job_source(self, job_id: uuid.UUID, item: RawJobItem) -> None:
        source_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        self._cur.execute(
            """
            INSERT INTO job_sources (
                id, job_id,
                source_platform, source_url, source_job_external_id,
                raw_title, raw_description_hash, raw_location,
                crawled_at, last_verified_at, is_active,
                created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                str(source_id),
                str(job_id),
                item.get("source_platform", "other"),
                item.get("source_url"),
                item.get("source_external_id"),
                item.get("title"),
                item.get("_dedup_hash"),
                item.get("location_raw"),
                item.get("crawled_at"),
                now,
                True,
                now,
                now,
            ),
        )

    def _increment_source_count(self, job_id: uuid.UUID) -> None:
        self._cur.execute(
            """
            UPDATE jobs
            SET source_count = source_count + 1,
                last_verified_at = %s,
                updated_at = %s
            WHERE id = %s
            """,
            (
                datetime.now(timezone.utc),
                datetime.now(timezone.utc),
                str(job_id),
            ),
        )
