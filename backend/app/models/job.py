import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    ARRAY,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.company import Company


# ── Enumerations ────────────────────────────────────────────────
class JobType(str, enum.Enum):
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    internship = "internship"


class WorkMode(str, enum.Enum):
    remote = "remote"
    hybrid = "hybrid"
    onsite = "onsite"


class ApplyMode(str, enum.Enum):
    redirect = "redirect"
    direct = "direct"


class SourcePlatform(str, enum.Enum):
    career_page = "career_page"
    linkedin = "linkedin"
    indeed = "indeed"
    glassdoor = "glassdoor"
    naukri = "naukri"
    wellfound = "wellfound"
    other = "other"


# ── Job model ───────────────────────────────────────────────────
class Job(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "jobs"

    # ── Company FK ──────────────────────────────────────────────
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )

    # ── Title ───────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    title_raw: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # ── Location ────────────────────────────────────────────────
    location_city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location_state: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location_country: Mapped[str] = mapped_column(
        String(100), default="India", nullable=False
    )
    location_raw: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # ── Type / Mode ─────────────────────────────────────────────
    job_type: Mapped[Optional[JobType]] = mapped_column(
        Enum(JobType, name="job_type_enum"), nullable=True
    )
    work_mode: Mapped[Optional[WorkMode]] = mapped_column(
        Enum(WorkMode, name="work_mode_enum"), nullable=True
    )

    # ── Experience ──────────────────────────────────────────────
    experience_min_years: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    experience_max_years: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )

    # ── Salary ──────────────────────────────────────────────────
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str] = mapped_column(
        String(10), default="INR", nullable=False
    )
    salary_period: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # ── Description ─────────────────────────────────────────────
    description_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── Skills / Classification ─────────────────────────────────
    skills: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    seniority_level: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # ── Dates ───────────────────────────────────────────────────
    posted_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    first_seen_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Status / Dedup ──────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    dedup_cluster_id: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)

    # ── Apply ───────────────────────────────────────────────────
    apply_mode: Mapped[Optional[ApplyMode]] = mapped_column(
        Enum(ApplyMode, name="apply_mode_enum"), nullable=True
    )
    direct_apply_url: Mapped[Optional[str]] = mapped_column(
        String(1024), nullable=True
    )

    # ── Aggregation metadata ────────────────────────────────────
    source_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # ── Relationships ───────────────────────────────────────────
    company: Mapped["Company"] = relationship(
        "Company", lazy="selectin", back_populates="jobs"
    )
    sources: Mapped[list["JobSource"]] = relationship(
        "JobSource", back_populates="job", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title!r}>"


# ── JobSource model ─────────────────────────────────────────────
class JobSource(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "job_sources"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    source_platform: Mapped[SourcePlatform] = mapped_column(
        Enum(SourcePlatform, name="source_platform_enum"), nullable=False
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    source_job_external_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    raw_title: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    raw_description_hash: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True
    )
    raw_location: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    crawled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ── Relationships ───────────────────────────────────────────
    job: Mapped["Job"] = relationship("Job", back_populates="sources")

    def __repr__(self) -> str:
        return f"<JobSource id={self.id} platform={self.source_platform.value}>"
