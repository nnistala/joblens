"""
DedupPipeline — drops duplicate items within a single crawl batch.

Computes a SHA-256 fingerprint from (company_name, title, location_raw,
source_platform) and keeps an in-memory set of seen hashes.  If the
same fingerprint appears twice in the same batch the later item is
dropped via ``DropItem``.
"""

import hashlib

from scrapy import Spider
from scrapy.exceptions import DropItem

from joblens_crawlers.items import RawJobItem


def _compute_dedup_hash(item: RawJobItem) -> str:
    """Deterministic SHA-256 hash for deduplication."""
    parts = [
        (item.get("company_name") or "").strip().lower(),
        (item.get("title") or "").strip().lower(),
        (item.get("location_raw") or "").strip().lower(),
        (item.get("source_platform") or "").strip().lower(),
    ]
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class DedupPipeline:
    """In-memory batch deduplication."""

    def open_spider(self, spider: Spider) -> None:
        self._seen: dict[str, RawJobItem] = {}

    def process_item(self, item: RawJobItem, spider: Spider) -> RawJobItem:
        h = _compute_dedup_hash(item)
        item["_dedup_hash"] = h

        if h in self._seen:
            raise DropItem(
                f"Duplicate item (hash={h[:12]}...): "
                f"{item.get('title')} @ {item.get('company_name')}"
            )

        self._seen[h] = item
        return item

    def close_spider(self, spider: Spider) -> None:
        spider.logger.info(
            "DedupPipeline: %d unique items passed through", len(self._seen)
        )
        self._seen.clear()
