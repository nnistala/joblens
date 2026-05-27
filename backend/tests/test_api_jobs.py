import pytest


@pytest.mark.asyncio
async def test_search_jobs_empty(client):
    response = await client.get("/api/v1/jobs/search")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert "total" in data
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_search_jobs_with_query(client):
    response = await client.get("/api/v1/jobs/search", params={"q": "python developer"})
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data


@pytest.mark.asyncio
async def test_get_job_not_found(client):
    response = await client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_trending_jobs(client):
    response = await client.get("/api/v1/jobs/trending")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
