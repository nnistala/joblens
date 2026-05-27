import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    ARRAY,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.job import Job


# ── Enumerations ────────────────────────────────────────────────
class SubscriptionTier(str, enum.Enum):
    free = "free"
    premium = "premium"


class AlertFrequency(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"
    instant = "instant"


class AlertChannel(str, enum.Enum):
    email = "email"
    push = "push"


class VerificationStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


# ── User model ──────────────────────────────────────────────────
class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(320), unique=True, index=True, nullable=False
    )
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # ── OAuth fields ────────────────────────────────────────────
    oauth_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    oauth_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # ── Subscription ────────────────────────────────────────────
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier, name="subscription_tier_enum"),
        default=SubscriptionTier.free,
        nullable=False,
    )

    # ── Profile / Preferences ───────────────────────────────────
    resume_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    skills: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), nullable=True)
    experience_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    preferred_locations: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text), nullable=True
    )
    preferred_roles: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text), nullable=True
    )

    # ── Relationships ───────────────────────────────────────────
    saved_jobs: Mapped[list["SavedJob"]] = relationship(
        "SavedJob", back_populates="user", cascade="all, delete-orphan"
    )
    job_alerts: Mapped[list["JobAlert"]] = relationship(
        "JobAlert", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


# ── SavedJob model (association table) ──────────────────────────
class SavedJob(Base):
    __tablename__ = "saved_jobs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
    )
    saved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── Relationships ───────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="saved_jobs")
    job: Mapped["Job"] = relationship("Job", lazy="selectin")

    def __repr__(self) -> str:
        return f"<SavedJob user_id={self.user_id} job_id={self.job_id}>"


# ── JobAlert model ──────────────────────────────────────────────
class JobAlert(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "job_alerts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    filters: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    frequency: Mapped[AlertFrequency] = mapped_column(
        Enum(AlertFrequency, name="alert_frequency_enum"), nullable=False
    )
    channel: Mapped[AlertChannel] = mapped_column(
        Enum(AlertChannel, name="alert_channel_enum"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ───────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="job_alerts")

    def __repr__(self) -> str:
        return f"<JobAlert id={self.id} name={self.name!r}>"


# ── HRCompanyRegistration model ─────────────────────────────────
class HRCompanyRegistration(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "hr_company_registrations"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    admin_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    career_page_url: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True
    )
    ats_platform: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    feed_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status_enum"),
        default=VerificationStatus.pending,
        nullable=False,
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ───────────────────────────────────────────
    company: Mapped["Company"] = relationship("Company", lazy="selectin")
    admin_user: Mapped["User"] = relationship("User", lazy="selectin")

    def __repr__(self) -> str:
        return f"<HRCompanyRegistration id={self.id} status={self.verification_status.value}>"
