"""
NormalizePipeline — cleans and enriches raw job items before storage.

Responsibilities:
* Normalise company name and job title casing / abbreviations
* Extract structured city + state from free-text location strings
* Parse experience ranges (e.g. "3-5 years" -> min=3, max=5)
* Parse salary information from raw text
* Extract skills mentions from the description body
"""

import re
from typing import Optional

from scrapy import Spider

from joblens_crawlers.items import RawJobItem


# ── Indian location data ────────────────────────────────────────────
_INDIAN_METROS = {
    "bengaluru": ("Bengaluru", "Karnataka"),
    "bangalore": ("Bengaluru", "Karnataka"),
    "mumbai": ("Mumbai", "Maharashtra"),
    "bombay": ("Mumbai", "Maharashtra"),
    "delhi": ("Delhi", "Delhi"),
    "new delhi": ("New Delhi", "Delhi"),
    "noida": ("Noida", "Uttar Pradesh"),
    "gurgaon": ("Gurgaon", "Haryana"),
    "gurugram": ("Gurgaon", "Haryana"),
    "hyderabad": ("Hyderabad", "Telangana"),
    "chennai": ("Chennai", "Tamil Nadu"),
    "madras": ("Chennai", "Tamil Nadu"),
    "pune": ("Pune", "Maharashtra"),
    "kolkata": ("Kolkata", "West Bengal"),
    "calcutta": ("Kolkata", "West Bengal"),
    "ahmedabad": ("Ahmedabad", "Gujarat"),
    "jaipur": ("Jaipur", "Rajasthan"),
    "kochi": ("Kochi", "Kerala"),
    "cochin": ("Kochi", "Kerala"),
    "thiruvananthapuram": ("Thiruvananthapuram", "Kerala"),
    "trivandrum": ("Thiruvananthapuram", "Kerala"),
    "chandigarh": ("Chandigarh", "Chandigarh"),
    "lucknow": ("Lucknow", "Uttar Pradesh"),
    "indore": ("Indore", "Madhya Pradesh"),
    "coimbatore": ("Coimbatore", "Tamil Nadu"),
    "nagpur": ("Nagpur", "Maharashtra"),
    "visakhapatnam": ("Visakhapatnam", "Andhra Pradesh"),
    "vizag": ("Visakhapatnam", "Andhra Pradesh"),
    "bhubaneswar": ("Bhubaneswar", "Odisha"),
    "mysore": ("Mysore", "Karnataka"),
    "mysuru": ("Mysore", "Karnataka"),
    "mangalore": ("Mangalore", "Karnataka"),
    "mangaluru": ("Mangalore", "Karnataka"),
}

# ── Title abbreviation map ──────────────────────────────────────────
_TITLE_ABBREVIATIONS = {
    r"\bSr\.?\b": "Senior",
    r"\bJr\.?\b": "Junior",
    r"\bMgr\.?\b": "Manager",
    r"\bEngg\.?\b": "Engineering",
    r"\bEngr\.?\b": "Engineer",
    r"\bDev\.?\b": "Developer",
    r"\bAdmin\.?\b": "Administrator",
    r"\bAsst\.?\b": "Assistant",
    r"\bExec\.?\b": "Executive",
    r"\bAssoc\.?\b": "Associate",
    r"\bDir\.?\b": "Director",
    r"\bVP\b": "Vice President",
    r"\bSDE\b": "Software Development Engineer",
}

# ── Common tech skills for extraction ───────────────────────────────
_SKILL_PATTERNS = [
    "Python", "Java", "JavaScript", "TypeScript", "Go", "Golang", "Rust",
    "C\\+\\+", "C#", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R",
    "SQL", "NoSQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra",
    "Elasticsearch", "DynamoDB",
    "React", "Angular", "Vue", "Next\\.js", "Node\\.js", "Express",
    "Django", "Flask", "FastAPI", "Spring Boot", "Spring",
    "Docker", "Kubernetes", "K8s", "AWS", "Azure", "GCP",
    "Terraform", "Ansible", "Jenkins", "CI/CD", "CircleCI", "GitHub Actions",
    "Kafka", "RabbitMQ", "Spark", "Hadoop", "Airflow",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "TensorFlow", "PyTorch", "Scikit-learn",
    "REST", "GraphQL", "gRPC", "Microservices",
    "Linux", "Git", "Agile", "Scrum",
    "Figma", "Sketch", "Adobe XD",
    "Tableau", "Power BI", "Looker",
    "Pandas", "NumPy", "SciPy",
    "HTML", "CSS", "SASS", "Tailwind",
    "Selenium", "Cypress", "Jest", "pytest",
]

_SKILL_RE = re.compile(
    r"\b(" + "|".join(_SKILL_PATTERNS) + r")\b",
    re.IGNORECASE,
)

# ── Experience regex ────────────────────────────────────────────────
_EXP_RANGE_RE = re.compile(
    r"(\d{1,2})\s*[-–to]+\s*(\d{1,2})\s*(?:years?|yrs?)",
    re.IGNORECASE,
)
_EXP_SINGLE_RE = re.compile(
    r"(\d{1,2})\+?\s*(?:years?|yrs?)",
    re.IGNORECASE,
)

# ── Salary regex (INR-centric) ──────────────────────────────────────
_SALARY_RANGE_RE = re.compile(
    r"(?:INR|Rs\.?|₹)\s*([\d,.]+)\s*[-–to]+\s*([\d,.]+)\s*"
    r"(?:LPA|lakh|lac|L|per annum|p\.?a\.?|/yr)?",
    re.IGNORECASE,
)
_SALARY_LPA_RE = re.compile(
    r"([\d,.]+)\s*[-–to]+\s*([\d,.]+)\s*(?:LPA|lakh|lac)",
    re.IGNORECASE,
)


class NormalizePipeline:
    """Clean and enrich every RawJobItem that flows through."""

    def process_item(self, item: RawJobItem, spider: Spider) -> RawJobItem:
        # ── Company name ────────────────────────────────────────────
        name = (item.get("company_name") or "").strip()
        if name:
            item["company_name"] = _normalize_company_name(name)

        # ── Title ───────────────────────────────────────────────────
        title = (item.get("title") or "").strip()
        if title:
            item["title"] = _normalize_title(title)

        # ── Location ────────────────────────────────────────────────
        loc = item.get("location_raw") or ""
        parsed = _parse_indian_location(loc)
        # Attach parsed data as extra keys (pipelines downstream
        # can read them; they will be ignored by Scrapy Item).
        item.setdefault("_location_city", parsed[0])
        item.setdefault("_location_state", parsed[1])

        # ── Experience ──────────────────────────────────────────────
        exp_raw = item.get("experience_raw") or ""
        exp_min, exp_max = _parse_experience(exp_raw)
        item.setdefault("_experience_min", exp_min)
        item.setdefault("_experience_max", exp_max)

        # ── Salary ──────────────────────────────────────────────────
        sal_raw = item.get("salary_raw") or ""
        sal_min, sal_max = _parse_salary(sal_raw)
        item.setdefault("_salary_min", sal_min)
        item.setdefault("_salary_max", sal_max)

        # ── Skills extraction ───────────────────────────────────────
        desc = item.get("description") or ""
        title_str = item.get("title") or ""
        skills = _extract_skills(f"{title_str} {desc}")
        item.setdefault("_skills", skills)

        return item


# ════════════════════════════════════════════════════════════════════
#  Helper functions
# ════════════════════════════════════════════════════════════════════

def _normalize_company_name(name: str) -> str:
    """Title-case the company name, handling common suffixes."""
    # Already looks intentionally cased (e.g. "TCS", "CRED")
    if name.isupper() and len(name) <= 6:
        return name
    return name.strip()


def _normalize_title(title: str) -> str:
    """Expand common abbreviations in job titles."""
    for pattern, replacement in _TITLE_ABBREVIATIONS.items():
        title = re.sub(pattern, replacement, title)
    # Collapse extra whitespace
    title = re.sub(r"\s+", " ", title).strip()
    return title


def _parse_indian_location(raw: str) -> tuple[Optional[str], Optional[str]]:
    """Try to extract (city, state) from a free-text location string."""
    if not raw:
        return None, None

    lower = raw.lower().strip()

    # Direct lookup
    for key, (city, state) in _INDIAN_METROS.items():
        if key in lower:
            return city, state

    # Return raw as city if it looks like a single city name
    parts = [p.strip() for p in re.split(r"[,;/|]", raw) if p.strip()]
    if parts:
        candidate = parts[0]
        if candidate.lower() in _INDIAN_METROS:
            city, state = _INDIAN_METROS[candidate.lower()]
            return city, state
        return candidate, None

    return None, None


def _parse_experience(raw: str) -> tuple[Optional[int], Optional[int]]:
    """Extract (min_years, max_years) from text like '3-5 years'."""
    if not raw:
        return None, None

    m = _EXP_RANGE_RE.search(raw)
    if m:
        return int(m.group(1)), int(m.group(2))

    m = _EXP_SINGLE_RE.search(raw)
    if m:
        val = int(m.group(1))
        return val, None

    return None, None


def _parse_salary(raw: str) -> tuple[Optional[int], Optional[int]]:
    """Extract (min, max) salary in INR from text.  Converts LPA to annual."""
    if not raw:
        return None, None

    def _clean_num(s: str) -> int:
        s = s.replace(",", "").strip()
        try:
            return int(float(s))
        except (ValueError, TypeError):
            return 0

    # Try explicit INR/Rs prefix
    m = _SALARY_RANGE_RE.search(raw)
    if m:
        lo, hi = _clean_num(m.group(1)), _clean_num(m.group(2))
        # If values are small, assume LPA
        if lo < 500:
            lo *= 100_000
        if hi < 500:
            hi *= 100_000
        return lo, hi

    # Try LPA pattern without currency prefix
    m = _SALARY_LPA_RE.search(raw)
    if m:
        lo = int(float(m.group(1).replace(",", "")) * 100_000)
        hi = int(float(m.group(2).replace(",", "")) * 100_000)
        return lo, hi

    return None, None


def _extract_skills(text: str) -> list[str]:
    """Return a deduplicated list of recognised skills in *text*."""
    found: dict[str, str] = {}
    for m in _SKILL_RE.finditer(text):
        canonical = m.group(0)
        key = canonical.lower()
        if key not in found:
            found[key] = canonical
    return list(found.values())
