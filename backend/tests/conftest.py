import asyncio
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.deps import get_db
from app.main import app
from app.models.base import Base

TEST_DATABASE_URL = settings.DATABASE_URL.replace("/joblens", "/joblens_test")

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_company_data():
    return {
        "name": "Test Company",
        "domain": "testcompany.com",
        "career_page_url": "https://testcompany.com/careers",
        "industry": "Technology",
        "size_bucket": "1000-5000",
    }


@pytest.fixture
def sample_job_data():
    return {
        "title": "Senior Software Engineer",
        "title_raw": "Sr. Software Eng",
        "location_city": "Bangalore",
        "location_state": "Karnataka",
        "location_country": "India",
        "location_raw": "Bangalore, Karnataka",
        "job_type": "full_time",
        "work_mode": "hybrid",
        "experience_min_years": 3,
        "experience_max_years": 7,
        "salary_min": 1500000,
        "salary_max": 3000000,
        "salary_currency": "INR",
        "description_summary": "Build scalable backend services using Python and microservices architecture.",
        "skills": ["Python", "FastAPI", "PostgreSQL", "AWS"],
        "department": "Engineering",
        "seniority_level": "Senior",
        "apply_mode": "redirect",
    }
