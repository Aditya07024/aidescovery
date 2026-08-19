import pytest


@pytest.mark.asyncio
async def test_health_and_readiness_endpoints(client):
    res_health = await client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_ready = await client.get("/api/v1/ready")
    assert res_ready.status_code == 200
    assert "database" in res_ready.json()


@pytest.mark.asyncio
async def test_list_connectors_endpoint(client):
    res = await client.get("/api/v1/connectors")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 4


@pytest.mark.asyncio
async def test_list_providers_endpoint(client):
    res = await client.get("/api/v1/providers")
    assert res.status_code == 200
    data = res.json()
    assert any(p["name"] == "mock" for p in data)


@pytest.mark.asyncio
async def test_create_and_retrieve_search_job(client):
    payload = {
        "query": "Find therapists in Mathura with at least 5 years of experience.",
        "sources": ["web", "google_maps"],
    }
    create_res = await client.post("/api/v1/search", json=payload)
    assert create_res.status_code == 202
    job_data = create_res.json()
    assert "search_id" in job_data
    search_id = job_data["search_id"]

    # Poll status
    status_res = await client.get(f"/api/v1/search/{search_id}")
    assert status_res.status_code == 200
    assert status_res.json()["search_id"] == search_id
