"""Job deduplication service.

Normalises titles and company names, computes deterministic hashes, and
performs fuzzy matching to detect duplicate postings.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from difflib import SequenceMatcher
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

# The Job model is imported at function level to avoid circular imports when
# the models package is still being assembled.

# ---------------------------------------------------------------------------
# Company name normalisation
# ---------------------------------------------------------------------------

_COMPANY_SUFFIXES = re.compile(
    r"\b("
    r"pvt\.?\s*ltd\.?|private\s+limited|"
    r"ltd\.?|limited|"
    r"inc\.?|incorporated|"
    r"llc\.?|llp\.?|"
    r"corp\.?|corporation|"
    r"co\.?|"
    r"plc\.?"
    r")\b",
    re.IGNORECASE,
)


def normalize_company_name(name: str) -> str:
    """Lowercase, strip common legal suffixes, and collapse whitespace."""
    name = name.lower().strip()
    name = _COMPANY_SUFFIXES.sub("", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


# ---------------------------------------------------------------------------
# Title normalisation
# ---------------------------------------------------------------------------

_TITLE_ABBREVIATIONS: dict[str, str] = {
    "sr.": "senior",
    "sr": "senior",
    "jr.": "junior",
    "jr": "junior",
    "eng": "engineer",
    "engg": "engineer",
    "dev": "developer",
    "mgr": "manager",
    "mgt": "management",
    "mgmt": "management",
    "assoc": "associate",
    "asst": "assistant",
    "vp": "vice president",
    "svp": "senior vice president",
    "dir": "director",
    "dept": "department",
    "exec": "executive",
    "admin": "administrator",
    "ops": "operations",
    "qa": "quality assurance",
    "hr": "human resources",
    "it": "information technology",
}


def normalize_title(title: str) -> str:
    """Expand common abbreviations, lowercase, and collapse whitespace."""
    title = title.lower().strip()
    # Remove non-alphanumeric characters except spaces
    title = re.sub(r"[^\w\s]", " ", title)
    words = title.split()
    expanded = [_TITLE_ABBREVIATIONS.get(w, w) for w in words]
    return " ".join(expanded)


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------


def compute_dedup_hash(company: str, title: str, city: str) -> str:
    """SHA-256 hash of normalised company + title + city."""
    key = "|".join(
        [
            normalize_company_name(company),
            normalize_title(title),
            city.lower().strip(),
        ]
    )
    return hashlib.sha256(key.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Fuzzy matching
# ---------------------------------------------------------------------------

FUZZY_THRESHOLD = 0.85


def fuzzy_title_match(title1: str, title2: str) -> float:
    """Return a similarity ratio between two normalised titles (0.0 .. 1.0)."""
    return SequenceMatcher(
        None,
        normalize_title(title1),
        normalize_title(title2),
    ).ratio()


# ---------------------------------------------------------------------------
# Duplicate detection (DB)
# ---------------------------------------------------------------------------


async def find_duplicate(
    db_session: AsyncSession,
    company_name: str,
    title: str,
    city: str,
) -> Optional[uuid.UUID]:
    """Return the ``id`` of an existing duplicate job, or ``None``.

    Strategy:
    1. Query active jobs in the same city from companies whose name matches
       (case-insensitive contains on the normalised company name).
    2. Among the candidates, check for an exact dedup-hash match on
       ``dedup_cluster_id`` (if the caller previously stored the hash as a
       deterministic UUID).
    3. Fall back to fuzzy title matching (> 0.85 similarity threshold).
    """
    from app.models.company import Company  # late import
    from app.models.job import Job  # late import

    norm_company = normalize_company_name(company_name)
    norm_city = city.lower().strip()

    # Fetch candidate jobs: same city, same (normalised) company
    stmt = (
        select(Job.id, Job.title, Job.dedup_cluster_id)
        .join(Company, Job.company_id == Company.id)
        .where(
            func.lower(Company.name).contains(norm_company),
            func.lower(Job.location_city) == norm_city,
            Job.is_active.is_(True),
        )
    )
    result = await db_session.execute(stmt)
    candidates = result.all()

    if not candidates:
        return None

    # --- exact hash match (deterministic UUID derived from dedup hash) -------
    dedup_hash = compute_dedup_hash(company_name, title, city)
    dedup_uuid = uuid.uuid5(uuid.NAMESPACE_URL, dedup_hash)
    for job_id, _title, cluster_id in candidates:
        if cluster_id is not None and cluster_id == dedup_uuid:
            return job_id

    # --- fuzzy title fallback ------------------------------------------------
    for job_id, existing_title, _cluster_id in candidates:
        if fuzzy_title_match(title, existing_title) >= FUZZY_THRESHOLD:
            return job_id

    return None
