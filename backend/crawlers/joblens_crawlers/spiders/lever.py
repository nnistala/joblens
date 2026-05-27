"""
Spider for the Lever public postings API.

Usage::

    scrapy crawl lever -a company_slug=dream11
"""

import json
from datetime import datetime, timezone

import scrapy

from joblens_crawlers.items import RawJobItem


class LeverSpider(scrapy.Spider):
    name = "lever"
    allowed_domains = ["api.lever.co"]

    # Pass via ``-a company_slug=<slug>``
    company_slug: str = ""

    BASE_URL = "https://api.lever.co/v0/postings/{slug}"

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
        postings = json.loads(response.text)

        if not isinstance(postings, list):
            self.logger.warning(
                "Lever [%s]: unexpected response format", self.company_slug
            )
            return

        self.logger.info(
            "Lever [%s]: found %d postings", self.company_slug, len(postings)
        )

        for posting in postings:
            categories = posting.get("categories", {})
            location_raw = categories.get("location")
            department = categories.get("department")
            team = categories.get("team")

            # Combine department and team if both exist
            if department and team and team != department:
                department = f"{department} / {team}"

            description_plain = posting.get("descriptionPlain", "")
            additional_plain = posting.get("additionalPlain", "")
            full_description = description_plain
            if additional_plain:
                full_description = f"{description_plain}\n\n{additional_plain}"

            yield RawJobItem(
                company_name=self.company_slug.replace("-", " ").title(),
                company_domain=None,
                title=posting.get("text", ""),
                location_raw=location_raw,
                job_type=categories.get("commitment"),
                work_mode=None,
                description=full_description,
                description_url=posting.get("hostedUrl", ""),
                salary_raw=None,
                experience_raw=None,
                skills_raw=None,
                department=department,
                apply_url=posting.get("hostedUrl", ""),
                source_platform="career_page",
                source_url=response.url,
                source_external_id=posting.get("id", ""),
                posted_date_raw=None,
                crawled_at=datetime.now(timezone.utc).isoformat(),
            )
