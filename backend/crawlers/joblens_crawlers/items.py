"""
Scrapy Item definitions for raw job data scraped from various sources.

Every spider yields ``RawJobItem`` instances.  Pipelines then normalise,
de-duplicate, and persist them into the JobLens database.
"""

import scrapy


class RawJobItem(scrapy.Item):
    """A single job listing as scraped from any source."""

    # ── Company info ────────────────────────────────────────────────
    company_name = scrapy.Field()
    company_domain = scrapy.Field()

    # ── Core job fields ─────────────────────────────────────────────
    title = scrapy.Field()
    location_raw = scrapy.Field()
    job_type = scrapy.Field()       # full_time | part_time | contract | internship
    work_mode = scrapy.Field()      # remote | hybrid | onsite
    description = scrapy.Field()    # plain-text / HTML body
    description_url = scrapy.Field()  # link to full JD page

    # ── Compensation / experience ───────────────────────────────────
    salary_raw = scrapy.Field()
    experience_raw = scrapy.Field()

    # ── Classification ──────────────────────────────────────────────
    skills_raw = scrapy.Field()
    department = scrapy.Field()

    # ── Application ─────────────────────────────────────────────────
    apply_url = scrapy.Field()

    # ── Source metadata ─────────────────────────────────────────────
    source_platform = scrapy.Field()     # career_page | indeed | linkedin | …
    source_url = scrapy.Field()          # page URL that was crawled
    source_external_id = scrapy.Field()  # ID on the source platform

    # ── Timestamps ──────────────────────────────────────────────────
    posted_date_raw = scrapy.Field()
    crawled_at = scrapy.Field()
