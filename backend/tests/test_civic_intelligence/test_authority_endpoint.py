# =============================================================================
# CivicSense AI — Authority Endpoint Tests (Phase 8)
# =============================================================================

import pytest
from app.main import app
from app.api.deps import get_authority_provider
from app.core.interfaces import AuthorityProvider
from app.contracts.authority import AuthorityResult
from app.contracts.location import LocationResult, Coordinates


@pytest.fixture
def sample_location_payload():
    return {
        "address": "123 Civic Road",
        "city": "Metropolis",
        "district": "Central",
        "state": "National Capital",
        "coordinates": {"latitude": 28.6139, "longitude": 77.2090},
        "confidence": 0.95,
        "source": "mock",
    }


@pytest.mark.anyio
async def test_route_authority_returns_200(client, sample_location_payload):
    payload = {
        "issue_type": "pothole",
        "location": sample_location_payload,
    }
    response = await client.post("/api/v1/authority/route", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "authority_name" in data
    assert "department" in data
    assert "jurisdiction" in data
    assert data["source"] == "mock"
    # Anti-hallucination verification: mock must NOT invent official contact details
    assert data["contact_email"] is None
    assert data["contact_phone"] is None
    assert data["verified_at"] is None


@pytest.mark.anyio
async def test_route_authority_rejects_missing_issue_type(client, sample_location_payload):
    payload = {
        "issue_type": "",
        "location": sample_location_payload,
    }
    response = await client.post("/api/v1/authority/route", json=payload)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_route_authority_supports_di_override(client, sample_location_payload):
    class CustomAuthorityProvider(AuthorityProvider):
        async def route(self, issue_type: str, location: LocationResult) -> AuthorityResult:
            return AuthorityResult(
                authority_name="Test Municipal Works",
                department="Roads & Bridges",
                jurisdiction="Test Jurisdiction",
                contact_email="test.verified@municipal.gov",
                contact_phone="1800111222",
                office_address="Civic Center",
                confidence=0.99,
                source="civic_authority_db",
                source_reference="https://municipal.gov/test-record",
                verified_at="2026-10-21T00:00:00Z",
            )

    app.dependency_overrides[get_authority_provider] = lambda: CustomAuthorityProvider()
    try:
        payload = {"issue_type": "pothole", "location": sample_location_payload}
        response = await client.post("/api/v1/authority/route", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["authority_name"] == "Test Municipal Works"
        assert data["contact_email"] == "test.verified@municipal.gov"
        assert data["source"] == "civic_authority_db"
    finally:
        app.dependency_overrides.pop(get_authority_provider, None)
