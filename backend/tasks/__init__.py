"""Celery application configuration for JobLens."""

import os

from celery import Celery
from celery.schedules import crontab

app = Celery("joblens")

# ── Broker & backend ────────────────────────────────────────────
app.conf.broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
app.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# ── Serialisation ───────────────────────────────────────────────
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]

# ── Auto-discover tasks in sibling modules ─────────────────────
app.autodiscover_tasks(["tasks"])

# ── Beat schedule ───────────────────────────────────────────────
app.conf.beat_schedule = {
    "crawl-tier1": {
        "task": "tasks.crawl_tasks.run_tier1_crawls",
        "schedule": 4 * 60 * 60,  # every 4 hours
    },
    "crawl-tier2": {
        "task": "tasks.crawl_tasks.run_tier2_crawls",
        "schedule": 12 * 60 * 60,  # every 12 hours
    },
    "crawl-tier3": {
        "task": "tasks.crawl_tasks.run_tier3_crawls",
        "schedule": 24 * 60 * 60,  # every 24 hours
    },
    "verify-freshness": {
        "task": "tasks.freshness_tasks.verify_job_freshness",
        "schedule": 6 * 60 * 60,  # every 6 hours
    },
    "send-daily-alerts": {
        "task": "tasks.alert_tasks.send_daily_alerts",
        # 8:00 AM IST = 2:30 AM UTC
        "schedule": crontab(hour=2, minute=30),
    },
}

app.conf.timezone = "UTC"
