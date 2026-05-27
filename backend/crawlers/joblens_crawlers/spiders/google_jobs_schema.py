"""
Spider that extracts Google-for-Jobs structured data (JSON-LD and
microdata) from company career pages.

Looks for ``<script type="application/ld+json">`` blocks with
``@type: "JobPosting"`` as well as HTML microdata using
``itemtype="https://schema.org/JobPosting"``.

Usage::

    scrapy crawl google_schema -a start_url=https://example.com/careers
"""

import json
from datetime import datetime, timezone

import scrapy

from joblens_crawlers.items import RawJobItem


class GoogleJobsSchemaSpider(scrapy.Spider):
    name = "google_schema"

    # Pass via ``-a start_url=<url>``
    start_url: str = ""

    def start_requests(self):
        if not self.start_url:
            self.logger.error("start_url argument is required")
            return

        yield scrapy.Request(self.start_url, callback=self.parse)

    def parse(self, response):
        # ── Strategy 1: JSON-LD ─────────────────────────────────────
        for script in response.css('script[type="application/ld+json"]::text'):
            try:
                data = json.loads(script.get())
            except (json.JSONDecodeError, TypeError):
                continue

            yield from self._extract_from_jsonld(data, response)

        # ── Strategy 2: Microdata ───────────────────────────────────
        for item in response.css(
            '[itemtype="https://schema.org/JobPosting"], '
            '[itemtype="http://schema.org/JobPosting"]'
        ):
            yield from self._extract_from_microdata(item, response)

    # ────────────────────────────────────────────────────────────────
    #  JSON-LD helpers
    # ────────────────────────────────────────────────────────────────
    def _extract_from_jsonld(self, data, response):
        """Recursively find JobPosting objects in JSON-LD data."""
        if isinstance(data, list):
            for item in data:
                yield from self._extract_from_jsonld(item, response)
            return

        if not isinstance(data, dict):
            return

        # Handle @graph wrapper
        if "@graph" in data:
            yield from self._extract_from_jsonld(data["@graph"], response)
            return

        if data.get("@type") == "JobPosting":
            yield self._jsonld_to_item(data, response)

    def _jsonld_to_item(self, data, response):
        """Convert a single JSON-LD JobPosting dict to a RawJobItem."""
        # Hiring organisation
        org = data.get("hiringOrganization") or {}
        company_name = org.get("name", "") if isinstance(org, dict) else ""

        # Location
        location_raw = self._extract_jsonld_location(data.get("jobLocation"))

        # Salary
        salary_raw = self._extract_jsonld_salary(data.get("baseSalary"))

        return RawJobItem(
            company_name=company_name,
            company_domain=None,
            title=data.get("title", ""),
            location_raw=location_raw,
            job_type=data.get("employmentType"),
            work_mode=None,
            description=data.get("description", ""),
            description_url=data.get("url") or response.url,
            salary_raw=salary_raw,
            experience_raw=None,
            skills_raw=None,
            department=None,
            apply_url=data.get("url") or response.url,
            source_platform="career_page",
            source_url=response.url,
            source_external_id=data.get("identifier", {}).get("value")
            if isinstance(data.get("identifier"), dict)
            else None,
            posted_date_raw=data.get("datePosted"),
            crawled_at=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def _extract_jsonld_location(loc):
        """Flatten jobLocation into a comma-separated string."""
        if loc is None:
            return None
        if isinstance(loc, str):
            return loc
        if isinstance(loc, list):
            parts = []
            for item in loc:
                if isinstance(item, dict):
                    addr = item.get("address", item)
                    if isinstance(addr, dict):
                        parts.append(
                            ", ".join(
                                filter(
                                    None,
                                    [
                                        addr.get("addressLocality"),
                                        addr.get("addressRegion"),
                                        addr.get("addressCountry"),
                                    ],
                                )
                            )
                        )
                    elif isinstance(addr, str):
                        parts.append(addr)
            return "; ".join(parts) if parts else None
        if isinstance(loc, dict):
            addr = loc.get("address", loc)
            if isinstance(addr, dict):
                return ", ".join(
                    filter(
                        None,
                        [
                            addr.get("addressLocality"),
                            addr.get("addressRegion"),
                            addr.get("addressCountry"),
                        ],
                    )
                )
            if isinstance(addr, str):
                return addr
        return None

    @staticmethod
    def _extract_jsonld_salary(salary):
        """Flatten baseSalary into a human-readable string."""
        if salary is None:
            return None
        if isinstance(salary, str):
            return salary
        if isinstance(salary, dict):
            currency = salary.get("currency", "")
            value = salary.get("value", {})
            if isinstance(value, dict):
                min_val = value.get("minValue", "")
                max_val = value.get("maxValue", "")
                unit = value.get("unitText", "")
                return f"{currency} {min_val}-{max_val} {unit}".strip()
            return f"{currency} {value}".strip()
        return None

    # ────────────────────────────────────────────────────────────────
    #  Microdata helpers
    # ────────────────────────────────────────────────────────────────
    def _extract_from_microdata(self, selector, response):
        """Extract job data from HTML microdata markup."""

        def _prop(name):
            """Get itemprop text content."""
            el = selector.css(f'[itemprop="{name}"]')
            return (
                el.css("::text").get("").strip()
                or el.attrib.get("content", "").strip()
            )

        title = _prop("title") or _prop("name")
        if not title:
            return

        # Hiring org
        org_el = selector.css('[itemprop="hiringOrganization"]')
        company_name = ""
        if org_el:
            company_name = (
                org_el.css('[itemprop="name"]::text').get("")
                or org_el.css('[itemprop="name"]').attrib.get("content", "")
            ).strip()

        # Location
        loc_el = selector.css('[itemprop="jobLocation"]')
        location_raw = ""
        if loc_el:
            location_raw = (
                loc_el.css('[itemprop="addressLocality"]::text').get("")
                or loc_el.css("::text").get("")
            ).strip()

        yield RawJobItem(
            company_name=company_name,
            company_domain=None,
            title=title,
            location_raw=location_raw or None,
            job_type=_prop("employmentType") or None,
            work_mode=None,
            description=_prop("description") or None,
            description_url=response.url,
            salary_raw=_prop("baseSalary") or None,
            experience_raw=None,
            skills_raw=None,
            department=None,
            apply_url=response.url,
            source_platform="career_page",
            source_url=response.url,
            source_external_id=None,
            posted_date_raw=_prop("datePosted") or None,
            crawled_at=datetime.now(timezone.utc).isoformat(),
        )
