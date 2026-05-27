"""
Spider for the Greenhouse public job-board API.

Usage::

    scrapy crawl greenhouse -a company_slug=razorpay
"""

import json
from datetime import datetime, timezone

import scrapy

from joblens_crawlers.items import RawJobItem


class GreenhouseSpider(scrapy.Spider):
    name = "greenhouse"
    allowed_domains = ["boards-api.greenhouse.io"]

    # Pass via ``-a company_slug=<slug>``
    company_slug: str = ""

    BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"

    def start_requests(self):
        if not self.company_slug:
            self.logger.error("company_slug argument is required")
            return

        url = self.BASE_URL.format(slug=self.company_slug)
        yield scrapy.Request(
            url,
            callback=self.parse,
            meta={"company_slug": self.company_slug},
        )

    def parse(self, response):
        data = json.loads(response.text)
        jobs = data.get("jobs", [])

        self.logger.info(
            "Greenhouse [%s]: found %d jobs", self.company_slug, len(jobs)
        )

        for job in jobs:
            # Build location string from offices list
            offices = job.get("offices", [])
            location_parts = [o.get("name", "") for o in offices if o.get("name")]
            location_raw = ", ".join(location_parts) if location_parts else None

            # Department
            departments = job.get("departments", [])
            department = departments[0].get("name") if departments else None

            yield RawJobItem(
                company_name=self.company_slug.replace("-", " ").title(),
                company_domain=None,
                title=job.get("title", ""),
                location_raw=location_raw,
                job_type=None,
                work_mode=None,
                description=job.get("content", ""),
                description_url=job.get("absolute_url", ""),
                salary_raw=None,
                experience_raw=None,
                skills_raw=None,
                department=department,
                apply_url=job.get("absolute_url", ""),
                source_platform="career_page",
                source_url=response.url,
                source_external_id=str(job.get("id", "")),
                posted_date_raw=job.get("updated_at"),
                crawled_at=datetime.now(timezone.utc).isoformat(),
            )
