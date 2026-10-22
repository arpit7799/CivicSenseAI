# =============================================================================
# CivicSense AI — Health Endpoint Tests
# =============================================================================

import pytest


@pytest.mark.anyio
async def test_health_returns_200(client):
    """Health endpoint should return 200 OK."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_health_response_structure(client):
    """Health response should contain status, service, version, and providers."""
    response = await client.get("/api/v1/health")
    data = response.json()

    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data
    assert "providers" in data


@pytest.mark.anyio
async def test_health_all_providers_are_mock(client):
    """In Phase 1, all providers should report as 'mock'."""
    response = await client.get("/api/v1/health")
    providers = response.json()["providers"]

    for provider_name, provider_type in providers.items():
        assert provider_type == "mock", (
            f"Provider '{provider_name}' should be 'mock' in Phase 1, "
            f"got '{provider_type}'"
        )
