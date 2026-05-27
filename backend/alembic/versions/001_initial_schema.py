"""Initial schema

Revision ID: 001
Revises: None
Create Date: 2025-05-27 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Enum types ──────────────────────────────────────────────
    job_type_enum = sa.Enum(
        "full_time", "part_time", "contract", "internship",
        name="job_type_enum",
    )
    work_mode_enum = sa.Enum(
        "remote", "hybrid", "onsite",
        name="work_mode_enum",
    )
    apply_mode_enum = sa.Enum(
        "redirect", "direct",
        name="apply_mode_enum",
    )
    source_platform_enum = sa.Enum(
        "career_page", "linkedin", "indeed", "glassdoor", "naukri", "wellfound", "other",
        name="source_platform_enum",
    )
    subscription_tier_enum = sa.Enum(
        "free", "premium",
        name="subscription_tier_enum",
    )
    alert_frequency_enum = sa.Enum(
        "daily", "weekly", "instant",
        name="alert_frequency_enum",
    )
    alert_channel_enum = sa.Enum(
        "email", "push",
        name="alert_channel_enum",
    )
    verification_status_enum = sa.Enum(
        "pending", "verified", "rejected",
        name="verification_status_enum",
    )

    job_type_enum.create(op.get_bind(), checkfirst=True)
    work_mode_enum.create(op.get_bind(), checkfirst=True)
    apply_mode_enum.create(op.get_bind(), checkfirst=True)
    source_platform_enum.create(op.get_bind(), checkfirst=True)
    subscription_tier_enum.create(op.get_bind(), checkfirst=True)
    alert_frequency_enum.create(op.get_bind(), checkfirst=True)
    alert_channel_enum.create(op.get_bind(), checkfirst=True)
    verification_status_enum.create(op.get_bind(), checkfirst=True)

    # ── companies ───────────────────────────────────────────────
    op.create_table(
        "companies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("name_aliases", sa.ARRAY(sa.Text), nullable=True),
        sa.Column("domain", sa.String(255), nullable=True),
        sa.Column("logo_url", sa.String(512), nullable=True),
        sa.Column("industry", sa.String(255), nullable=True),
        sa.Column("size_bucket", sa.String(100), nullable=True),
        sa.Column("career_page_url", sa.String(512), nullable=True),
        sa.Column("careers_ats_platform", sa.String(100), nullable=True),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_hr_direct", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── jobs ────────────────────────────────────────────────────
    op.create_table(
        "jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("title_raw", sa.String(512), nullable=True),
        sa.Column("location_city", sa.String(255), nullable=True),
        sa.Column("location_state", sa.String(255), nullable=True),
        sa.Column("location_country", sa.String(100), nullable=False, server_default="India"),
        sa.Column("location_raw", sa.String(512), nullable=True),
        sa.Column("job_type", job_type_enum, nullable=True),
        sa.Column("work_mode", work_mode_enum, nullable=True),
        sa.Column("experience_min_years", sa.Integer, nullable=True),
        sa.Column("experience_max_years", sa.Integer, nullable=True),
        sa.Column("salary_min", sa.Integer, nullable=True),
        sa.Column("salary_max", sa.Integer, nullable=True),
        sa.Column("salary_currency", sa.String(10), nullable=False, server_default="INR"),
        sa.Column("salary_period", sa.String(50), nullable=True),
        sa.Column("description_summary", sa.Text, nullable=True),
        sa.Column("skills", sa.ARRAY(sa.Text), nullable=True),
        sa.Column("department", sa.String(255), nullable=True),
        sa.Column("seniority_level", sa.String(100), nullable=True),
        sa.Column("posted_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("dedup_cluster_id", UUID(as_uuid=True), nullable=True),
        sa.Column("apply_mode", apply_mode_enum, nullable=True),
        sa.Column("direct_apply_url", sa.String(1024), nullable=True),
        sa.Column("source_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("quality_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── job_sources ─────────────────────────────────────────────
    op.create_table(
        "job_sources",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_platform", source_platform_enum, nullable=False),
        sa.Column("source_url", sa.String(1024), nullable=True),
        sa.Column("source_job_external_id", sa.String(255), nullable=True),
        sa.Column("raw_title", sa.String(512), nullable=True),
        sa.Column("raw_description_hash", sa.String(128), nullable=True),
        sa.Column("raw_location", sa.String(512), nullable=True),
        sa.Column("crawled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── users ───────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("oauth_provider", sa.String(50), nullable=True),
        sa.Column("oauth_id", sa.String(255), nullable=True),
        sa.Column("subscription_tier", subscription_tier_enum, nullable=False, server_default="free"),
        sa.Column("resume_url", sa.String(512), nullable=True),
        sa.Column("skills", sa.ARRAY(sa.Text), nullable=True),
        sa.Column("experience_years", sa.Integer, nullable=True),
        sa.Column("preferred_locations", sa.ARRAY(sa.Text), nullable=True),
        sa.Column("preferred_roles", sa.ARRAY(sa.Text), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── saved_jobs ──────────────────────────────────────────────
    op.create_table(
        "saved_jobs",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("job_id", UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("saved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("notes", sa.Text, nullable=True),
    )

    # ── job_alerts ──────────────────────────────────────────────
    op.create_table(
        "job_alerts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("query", sa.Text, nullable=False),
        sa.Column("filters", JSONB, nullable=True),
        sa.Column("frequency", alert_frequency_enum, nullable=False),
        sa.Column("channel", alert_channel_enum, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── hr_company_registrations ────────────────────────────────
    op.create_table(
        "hr_company_registrations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("admin_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("career_page_url", sa.String(512), nullable=True),
        sa.Column("ats_platform", sa.String(100), nullable=True),
        sa.Column("feed_url", sa.String(512), nullable=True),
        sa.Column("verification_status", verification_status_enum, nullable=False, server_default="pending"),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── Indexes ─────────────────────────────────────────────────
    op.create_index("ix_jobs_company_id", "jobs", ["company_id"])
    op.create_index("ix_jobs_is_active", "jobs", ["is_active"])
    op.create_index("ix_jobs_dedup_cluster_id", "jobs", ["dedup_cluster_id"])
    op.create_index("ix_jobs_location_city", "jobs", ["location_city"])
    op.create_index("ix_job_sources_job_id", "job_sources", ["job_id"])
    op.create_index("ix_job_sources_source_url", "job_sources", ["source_url"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    # ── Drop indexes ────────────────────────────────────────────
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_job_sources_source_url", table_name="job_sources")
    op.drop_index("ix_job_sources_job_id", table_name="job_sources")
    op.drop_index("ix_jobs_location_city", table_name="jobs")
    op.drop_index("ix_jobs_dedup_cluster_id", table_name="jobs")
    op.drop_index("ix_jobs_is_active", table_name="jobs")
    op.drop_index("ix_jobs_company_id", table_name="jobs")

    # ── Drop tables (reverse order due to FK constraints) ──────
    op.drop_table("hr_company_registrations")
    op.drop_table("job_alerts")
    op.drop_table("saved_jobs")
    op.drop_table("users")
    op.drop_table("job_sources")
    op.drop_table("jobs")
    op.drop_table("companies")

    # ── Drop enum types ─────────────────────────────────────────
    sa.Enum(name="verification_status_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="alert_channel_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="alert_frequency_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="subscription_tier_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="source_platform_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="apply_mode_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="work_mode_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="job_type_enum").drop(op.get_bind(), checkfirst=True)
