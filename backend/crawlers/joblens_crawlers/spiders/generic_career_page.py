"""
Generic HTML career-page spider.

Crawls a company's career page, follows job-related links up to a
limited depth, and tries to extract job listings using common CSS
patterns found across career sites.

Usage::

    scrapy crawl generic_career -a career_page_url=https://example.com/careers \\
                                 -a company_name="Example Corp"
"""

import re
from datetime import datetime, timezone
from urllib.parse import urljoin

import scrapy

from joblens_crawlers.items import RawJobItem

# Keywords that indicate a link is job-related
_JOB_LINK_KEYWORDS = re.compile(
    r"(job|career|position|opening|apply|vacanc|recruit|hire|opportunit)",
    re.IGNORECASE,
)

# CSS selectors commonly used for job listing containers
_JOB_CONTAINER_SELECTORS = [
    ".job-listing",
    ".job-card",
    ".career-listing",
    ".career-card",
    ".job-item",
    ".position-item",
    ".opening-card",
    "[class*='job']",
    "[class*='position']",
    "[class*='career']",
    "[class*='opening']",
    "article",
]

# CSS selectors for title links inside job containers
_TITLE_LINK_SELECTORS = [
    "h2 a",
    "h3 a",
    "h4 a",
    "a.job-title",
    "a[class*='title']",
    "a",
]

# CSS selectors for location text near a job listing
_LOCATION_SELECTORS = [
    ".location",
    ".job-location",
    "[class*='location']",
    "[class*='city']",
    "span.meta",
]


class GenericCareerPageSpider(scrapy.Spider):
    name = "generic_career"

    # Pass via -a flags
    career_page_url: str = ""
    company_name: str = ""

    MAX_DEPTH = 2

    custom_settings = {
        "DEPTH_LIMIT": 2,
    }

    def start_requests(self):
        if not self.career_page_url:
            self.logger.error("career_page_url argument is required")
            return

        yield scrapy.Request(
            self.career_page_url,
            callback=self.parse_listing_page,
            meta={"depth": 0},
        )

    # ── Listing page ────────────────────────────────────────────────
    def parse_listing_page(self, response):
        current_depth = response.meta.get("depth", 0)

        # Try extracting job cards from the page
        job_links_found = False
        for container_sel in _JOB_CONTAINER_SELECTORS:
            containers = response.css(container_sel)
            if not containers:
                continue

            for container in containers:
                link = None
                title_text = None

                for link_sel in _TITLE_LINK_SELECTORS:
                    link_el = container.css(link_sel)
                    if link_el:
                        href = link_el.attrib.get("href", "")
                        title_text = link_el.css("::text").get("").strip()
                        if href:
                            link = response.urljoin(href)
                            break

                if link and title_text:
                    job_links_found = True
                    # Extract location hint from the container
                    location_raw = None
                    for loc_sel in _LOCATION_SELECTORS:
                        loc_el = container.css(loc_sel)
                        if loc_el:
                            location_raw = loc_el.css("::text").get("").strip()
                            break

                    yield scrapy.Request(
                        link,
                        callback=self.parse_job_detail,
                        meta={
                            "title_hint": title_text,
                            "location_hint": location_raw,
                        },
                    )

        # If no structured job cards found, follow job-related links
        if not job_links_found and current_depth < self.MAX_DEPTH:
            for anchor in response.css("a[href]"):
                href = anchor.attrib.get("href", "")
                text = anchor.css("::text").get("") or ""
                full_url = response.urljoin(href)

                if _JOB_LINK_KEYWORDS.search(href) or _JOB_LINK_KEYWORDS.search(text):
                    yield scrapy.Request(
                        full_url,
                        callback=self.parse_listing_page,
                        meta={"depth": current_depth + 1},
                    )

    # ── Detail page ─────────────────────────────────────────────────
    def parse_job_detail(self, response):
        # Title: prefer h1, fall back to hint
        title = response.css("h1::text").get("").strip()
        if not title:
            title = response.meta.get("title_hint", "")

        # Location from detail page
        location_raw = None
        for loc_sel in _LOCATION_SELECTORS:
            loc_el = response.css(loc_sel)
            if loc_el:
                location_raw = loc_el.css("::text").get("").strip()
                break
        if not location_raw:
            location_raw = response.meta.get("location_hint")

        # Description: try main content areas
        description = ""
        for content_sel in [
            ".job-description",
            ".job-content",
            "[class*='description']",
            "[class*='content']",
            "main",
            "article",
            "#content",
        ]:
            desc_el = response.css(content_sel)
            if desc_el:
                description = desc_el.get()
                break

        if not description:
            description = response.css("body").get("")

        if title:
            yield RawJobItem(
                company_name=self.company_name or "",
                company_domain=None,
                title=title,
                location_raw=location_raw,
                job_type=None,
                work_mode=None,
                description=description,
                description_url=response.url,
                salary_raw=None,
                experience_raw=None,
                skills_raw=None,
                department=None,
                apply_url=response.url,
                source_platform="career_page",
                source_url=response.url,
                source_external_id=None,
                posted_date_raw=None,
                crawled_at=datetime.now(timezone.utc).isoformat(),
            )
