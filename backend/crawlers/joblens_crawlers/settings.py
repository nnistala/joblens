"""
Scrapy settings for the JobLens crawlers project.

These settings control bot behaviour, concurrency, pipelines, and
middleware for all spiders in the joblens_crawlers package.
"""

import os

# ── Project identity ────────────────────────────────────────────────
BOT_NAME = "joblens"
SPIDER_MODULES = ["joblens_crawlers.spiders"]
NEWSPIDER_MODULE = "joblens_crawlers.spiders"

# ── Crawl responsibly ───────────────────────────────────────────────
ROBOTSTXT_OBEY = True

USER_AGENT = os.getenv(
    "CRAWL_USER_AGENT",
    "JobLens/1.0 (+https://joblens.in/about)",
)

# ── Concurrency / throttling ───────────────────────────────────────
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 2
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# ── Item pipelines (lower number = higher priority) ────────────────
ITEM_PIPELINES = {
    "joblens_crawlers.pipelines.normalize.NormalizePipeline": 300,
    "joblens_crawlers.pipelines.dedup.DedupPipeline": 400,
    "joblens_crawlers.pipelines.store.StorePipeline": 500,
}

# ── Downloader middlewares ──────────────────────────────────────────
DOWNLOADER_MIDDLEWARES = {
    # Disable the built-in UA middleware and use our rotator instead
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "joblens_crawlers.middlewares.useragent.RotateUserAgentMiddleware": 400,
}

# ── Feed exports (optional JSON-lines backup) ──────────────────────
FEEDS = {
    "output/%(name)s_%(time)s.jsonl": {
        "format": "jsonlines",
        "encoding": "utf-8",
        "overwrite": False,
    },
}

# ── Logging ─────────────────────────────────────────────────────────
LOG_LEVEL = "INFO"

# ── HTTP cache (disabled — we want fresh data each run) ─────────────
HTTPCACHE_ENABLED = False

# ── Misc ────────────────────────────────────────────────────────────
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
