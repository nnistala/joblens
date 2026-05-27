import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, String, Text, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.job import Job


class Company(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_aliases: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text), nullable=True
    )
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    size_bucket: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    career_page_url: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True
    )
    careers_ats_platform: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_hr_direct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ── Relationships ───────────────────────────────────────────
    jobs: Mapped[list["Job"]] = relationship(
        "Job", back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Company id={self.id} name={self.name!r}>"
