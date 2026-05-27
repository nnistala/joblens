"""
Spider for Indeed India public job search results.

Scrapes only publicly visible, non-login pages and strictly respects
robots.txt.  Uses a redirect-based apply model (links back to Indeed).

Usage::

    scrapy crawl indeed_india -a search_query="python developer" \\
                              -a location="Bangalore"
"""

from datetime import datetime, timezone
from urllib.parse import quote_plus, urljoin

import scrapy

from joblens_crawlers.items import RawJobItem


class IndeedIndiaSpider(scrapy.Spider):
    name = "indeed_india"
    allowed_domains = ["indeed.co.in"]

    # Spider arguments (pass via ``-a``)
    search_query: str = ""
    location: str = "India"

    MAX_PAGES = 5
    RESULTS_PER_PAGE = 10  # Indeed default

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 3,
    }

    def start_requests(self):
        if not self.search_query:
            self.logger.error("search_query argument is required")
            return

        url = (
            f"https://www.indeed.co.in/jobs"
            f"?q={quote_plus(self.search_query)}"
            f"&l={quote_plus(self.location)}"
        )
        yield scrapy.Request(
            url,
            callback=self.parse_results,
            meta={"page": 1},
        )

    def parse_results(self, response):
        current_page = response.meta.get("page", 1)

        # Indeed wraps each job card in various container selectors;
        # try the most common ones.
        job_cards = response.css(
            "div.job_seen_beacon, "
            "div.jobsearch-SerpJobCard, "
            "div.result, "
            "td.resultContent, "
            "div[class*='cardOutline']"
        )

        if not job_cards:
            self.logger.info(
                "Indeed India: no job cards found on page %d — stopping",
                current_page,
            )
            return

        self.logger.info(
            "Indeed India: page %d — found %d cards",
            current_page,
            len(job_cards),
        )

        for card in job_cards:
            # Title + link
            title_el = card.css(
                'h2.jobTitle a, a[class*="title"], '
                'a[data-jk], a.jobtitle'
            )
            title = (
                title_el.css("span::text").get("")
                or title_el.css("::text").get("")
            ).strip()
            href = title_el.attrib.get("href", "")
            job_url = response.urljoin(href) if href else None

            # Company
            company = card.css(
                'span[data-testid="company-name"]::text, '
                "span.companyName::text, "
                "span.company::text"
            ).get("").strip()

            # Location
            location_raw = card.css(
                'div[data-testid="text-location"]::text, '
                "div.companyLocation::text, "
                "span.location::text"
            ).get("").strip()

            # Snippet / summary
            snippet = card.css(
                "div.job-snippet::text, "
                'ul[style] li::text, '
                "div.summary::text"
            ).getall()
            description = " ".join(s.strip() for s in snippet if s.strip())

            # External ID from data attribute
            external_id = (
                title_el.attrib.get("data-jk")
                or card.attrib.get("data-jk")
                or None
            )

            if title and job_url:
                yield RawJobItem(
                    company_name=company,
                    company_domain=None,
                    title=title,
                    location_raw=location_raw or None,
                    job_type=None,
                    work_mode=None,
                    description=description,
                    description_url=job_url,
                    salary_raw=card.css(
                        "div.salary-snippet-container::text, "
                        "span.salaryText::text"
                    ).get("").strip() or None,
                    experience_raw=None,
                    skills_raw=None,
                    department=None,
                    apply_url=job_url,
                    source_platform="indeed",
                    source_url=response.url,
                    source_external_id=external_id,
                    posted_date_raw=card.css(
                        "span.date::text, span[class*='date']::text"
                    ).get("").strip() or None,
                    crawled_at=datetime.now(timezone.utc).isoformat(),
                )

        # ── Pagination ──────────────────────────────────────────────
        if current_page < self.MAX_PAGES:
            next_link = response.css(
                'a[aria-label="Next"]::attr(href), '
                'a[data-testid="pagination-page-next"]::attr(href)'
            ).get()

            if next_link:
                yield scrapy.Request(
                    response.urljoin(next_link),
                    callback=self.parse_results,
                    meta={"page": current_page + 1},
                )
            else:
                # Fallback: construct the next URL manually
                start = current_page * self.RESULTS_PER_PAGE
                next_url = (
                    f"https://www.indeed.co.in/jobs"
                    f"?q={quote_plus(self.search_query)}"
                    f"&l={quote_plus(self.location)}"
                    f"&start={start}"
                )
                yield scrapy.Request(
                    next_url,
                    callback=self.parse_results,
                    meta={"page": current_page + 1},
                )
