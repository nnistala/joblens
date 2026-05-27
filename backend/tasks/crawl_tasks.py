"""Celery tasks for triggering Scrapy crawl spiders."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
from celery import shared_task

logger = logging.getLogger(__name__)

# Path to the crawl configuration YAML
CRAWL_CONFIG_PATH = Path(__file__).resolve().parent.parent / "crawlers" / "crawl_config.yaml"


def _load_crawl_config() -> dict[str, Any]:
    """Load and return the crawl configuration from YAML."""
    if not CRAWL_CONFIG_PATH.exists():
        logger.warning("crawl_config.yaml not found at %s", CRAWL_CONFIG_PATH)
        return {}
    with open(CRAWL_CONFIG_PATH) as fh:
        return yaml.safe_load(fh) or {}


def _run_spider(spider_name: str, **kwargs: Any) -> None:
    """Run a single Scrapy spider as a subprocess.

    Using subprocess rather than CrawlerProcess ensures the reactor is not
    shared with the Celery worker (Twisted reactor cannot be restarted).
    """
    cmd = [
        sys.executable,
        "-m",
        "scrapy",
        "crawl",
        spider_name,
    ]
    for key, value in kwargs.items():
        cmd.extend(["-a", f"{key}={value}"])

    logger.info("Starting spider: %s with args %s", spider_name, kwargs)
    result = subprocess.run(
        cmd,
        cwd=str(Path(__file__).resolve().parent.parent / "crawlers"),
        capture_output=True,
        text=True,
        timeout=3600,  # 1-hour timeout per spider
    )
    if result.returncode != 0:
        logger.error(
            "Spider %s failed (rc=%d): %s",
            spider_name,
            result.returncode,
            result.stderr[:2000],
        )
    else:
        logger.info("Spider %s completed successfully.", spider_name)


def _run_tier(tier: str) -> None:
    """Load companies for the given tier and launch their spiders."""
    config = _load_crawl_config()
    companies = config.get(tier, [])
    if not companies:
        logger.info("No companies configured for %s.", tier)
        return
    for entry in companies:
        spider_name = entry.get("spider")
        spider_kwargs = entry.get("kwargs", {})
        if not spider_name:
            logger.warning("Skipping entry without spider name in %s: %s", tier, entry)
            continue
        _run_spider(spider_name, **spider_kwargs)


@shared_task(name="tasks.crawl_tasks.run_tier1_crawls")
def run_tier1_crawls() -> str:
    """Run crawl spiders for all tier-1 companies."""
    _run_tier("tier1")
    return "tier1 crawls completed"


@shared_task(name="tasks.crawl_tasks.run_tier2_crawls")
def run_tier2_crawls() -> str:
    """Run crawl spiders for all tier-2 companies."""
    _run_tier("tier2")
    return "tier2 crawls completed"


@shared_task(name="tasks.crawl_tasks.run_tier3_crawls")
def run_tier3_crawls() -> str:
    """Run crawl spiders for all tier-3 companies."""
    _run_tier("tier3")
    return "tier3 crawls completed"


@shared_task(name="tasks.crawl_tasks.crawl_single_company")
def crawl_single_company(spider_name: str, **kwargs: Any) -> str:
    """Run a single spider with the provided arguments."""
    _run_spider(spider_name, **kwargs)
    return f"spider {spider_name} completed"
