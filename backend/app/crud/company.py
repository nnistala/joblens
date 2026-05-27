"""CRUD operations for the Company model."""

from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company


async def get_company(db: AsyncSession, company_id: uuid.UUID) -> Company | None:
    """Return a company by primary key."""
    return await db.get(Company, company_id)


async def get_company_by_domain(db: AsyncSession, domain: str) -> Company | None:
    """Look up a company by its website domain."""
    stmt = select(Company).where(Company.domain == domain)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def search_companies(
    db: AsyncSession,
    query: str,
    skip: int = 0,
    limit: int = 20,
) -> list[Company]:
    """Search companies by name (case-insensitive ILIKE)."""
    pattern = f"%{query}%"
    stmt = (
        select(Company)
        .where(Company.name.ilike(pattern))
        .order_by(Company.name)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_company(db: AsyncSession, company_data: dict[str, Any]) -> Company:
    """Insert a new company row."""
    company = Company(**company_data)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


async def get_or_create_company(
    db: AsyncSession,
    name: str,
    domain: Optional[str] = None,
) -> Company:
    """Return an existing company (matched by domain or name) or create one.

    Matching priority:
    1. Exact domain match (if *domain* is provided).
    2. Exact name match (case-insensitive).
    3. Create a new record.
    """
    if domain:
        existing = await get_company_by_domain(db, domain)
        if existing is not None:
            return existing

    # Case-insensitive name lookup
    stmt = select(Company).where(Company.name.ilike(name))
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing

    # Create new
    return await create_company(db, {"name": name, "domain": domain})
