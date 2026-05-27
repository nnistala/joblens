"""OpenSearch-backed job search service."""

from __future__ import annotations

import math
from typing import Any

from opensearchpy import AsyncOpenSearch

from app.schemas.job import JobSearchParams
from app.utils.opensearch import JOB_INDEX_NAME


class SearchService:
    """Thin wrapper around an ``AsyncOpenSearch`` client for job search."""

    def __init__(self, opensearch_client: AsyncOpenSearch) -> None:
        self.client = opensearch_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def search_jobs(self, params: JobSearchParams) -> dict[str, Any]:
        """Execute a search against the *jobs* index and return results.

        Returns a dict with keys ``hits`` (list of source dicts) and
        ``total`` (int).
        """
        query = self._build_query(params)
        from_ = (params.page - 1) * params.page_size

        body: dict[str, Any] = {
            "query": query,
            "from": from_,
            "size": params.page_size,
            "sort": [
                {"_score": {"order": "desc"}},
                {"posted_date": {"order": "desc", "missing": "_last"}},
            ],
        }

        response = await self.client.search(index=JOB_INDEX_NAME, body=body)

        total = response["hits"]["total"]["value"]
        hits = [hit["_source"] for hit in response["hits"]["hits"]]

        return {
            "hits": hits,
            "total": total,
            "page": params.page,
            "page_size": params.page_size,
            "total_pages": math.ceil(total / params.page_size) if params.page_size else 0,
        }

    async def index_job(self, job_data: dict[str, Any]) -> None:
        """Index (or re-index) a single job document."""
        doc_id = str(job_data.get("id", ""))
        await self.client.index(
            index=JOB_INDEX_NAME,
            id=doc_id,
            body=job_data,
            refresh="wait_for",
        )

    async def delete_job(self, job_id: str) -> None:
        """Delete a job document from the index."""
        await self.client.delete(
            index=JOB_INDEX_NAME,
            id=job_id,
            refresh="wait_for",
            ignore=[404],
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_query(self, params: JobSearchParams) -> dict[str, Any]:
        """Construct an OpenSearch bool query from *params*."""
        must: list[dict[str, Any]] = []
        should: list[dict[str, Any]] = []
        filter_clauses: list[dict[str, Any]] = []

        # Full-text search across title, description, company name
        if params.q:
            should.append(
                {
                    "multi_match": {
                        "query": params.q,
                        "fields": [
                            "title^3",
                            "description_summary^2",
                            "company_name",
                            "skills",
                        ],
                        "type": "best_fields",
                        "fuzziness": "AUTO",
                    }
                }
            )

        # Location filter (text match)
        if params.location:
            filter_clauses.append(
                {
                    "multi_match": {
                        "query": params.location,
                        "fields": ["location_city", "location_state"],
                    }
                }
            )

        # Company filter
        if params.company:
            filter_clauses.append(
                {"match": {"company_name": {"query": params.company}}}
            )

        # Keyword filters
        if params.job_type:
            filter_clauses.append({"term": {"job_type": params.job_type}})

        if params.work_mode:
            filter_clauses.append({"term": {"work_mode": params.work_mode}})

        # Experience range
        if params.experience_min is not None:
            filter_clauses.append(
                {"range": {"experience_max_years": {"gte": params.experience_min}}}
            )
        if params.experience_max is not None:
            filter_clauses.append(
                {"range": {"experience_min_years": {"lte": params.experience_max}}}
            )

        # Salary range
        if params.salary_min is not None:
            filter_clauses.append(
                {"range": {"salary_max": {"gte": params.salary_min}}}
            )

        # Build the bool query
        bool_query: dict[str, Any] = {}
        if must:
            bool_query["must"] = must
        if should:
            bool_query["should"] = should
            bool_query["minimum_should_match"] = 1
        if filter_clauses:
            bool_query["filter"] = filter_clauses

        # Fall back to match_all when nothing is specified
        if not bool_query:
            return {"match_all": {}}

        return {"bool": bool_query}
