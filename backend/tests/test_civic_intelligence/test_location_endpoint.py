# =============================================================================
# CivicSense AI — Location Endpoint Tests (Phase 8)
# =============================================================================

import pytest
from app.main import app
from app.api.deps import get_location_provider
from app.core.interfaces import LocationProvider
from app.contracts.location import LocationResult, Coordinates


@pytest.mark.anyio
async def test_resolve_location_returns_200(client):
    payload = {"latitude": 28.6139, "longitude": 77.2090}
    response = await client.post("/api/v1/location/resolve", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "address" in data
    assert "city" in data
    assert "coordinates" in data
    assert data["coordinates"]["latitude"] == 28.6139
    assert data["coordinates"]["longitude"] == 77.2090
    assert data["source"] == "mock"  # Explicitly identified as mock data


@pytest.mark.anyio
async def test_resolve_location_rejects_out_of_bounds_coordinates(client):
    # Latitude > 90
    resp_lat = await client.post("/api/v1/location/resolve", json={"latitude": 95.0, "longitude": 77.0})
    assert resp_lat.status_code == 422

    # Longitude < -180
    resp_lon = await client.post("/api/v1/location/resolve", json={"latitude": 28.0, "longitude": -185.0})
    assert resp_lon.status_code == 422


@pytest.mark.anyio
async def test_resolve_location_supports_di_override(client):
    class CustomTestLocationProvider(LocationProvider):
        async def resolve(self, latitude: float, longitude: float) -> LocationResult:
            return LocationResult(
                address="Test Custom Road",
                city="Test City",
                district="Test District",
                state="Test State",
                coordinates=Coordinates(latitude=latitude, longitude=longitude),
                confidence=1.0,
                source="test_custom_provider",
            )

    app.dependency_overrides[get_location_provider] = lambda: CustomTestLocationProvider()
    try:
        response = await client.post(
            "/api/v1/location/resolve",
            json={"latitude": 19.0760, "longitude": 72.8777},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "Test City"
        assert data["source"] == "test_custom_provider"
    finally:
        app.dependency_overrides.pop(get_location_provider, None)
