import httpx
import pytest

from app.core.errors import ProviderUnavailableError
from app.location.nominatim_provider import NominatimLocationProvider


@pytest.mark.anyio
async def test_reverse_geocodes_and_normalizes_address_fields():
    observed = {}

    def handler(request: httpx.Request) -> httpx.Response:
        observed["request"] = request
        return httpx.Response(
            200,
            json={
                "display_name": "Sector 29, Gurugram, Haryana, India",
                "address": {
                    "road": "Sector 29",
                    "city": "Gurugram",
                    "state_district": "Gurugram",
                    "state": "Haryana",
                    "postcode": "122001",
                    "suburb": "Sector 29",
                },
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = NominatimLocationProvider(client=client, min_request_interval_seconds=0)
        result = await provider.resolve(28.4595, 77.0266)

    request = observed["request"]
    assert request.url.path == "/reverse"
    assert request.url.params["format"] == "jsonv2"
    assert request.headers["User-Agent"] == provider.settings.geocoder_user_agent
    assert result.address == "Sector 29, Gurugram, Haryana, India"
    assert result.city == "Gurugram"
    assert result.district == "Gurugram"
    assert result.state == "Haryana"
    assert result.ward == "Sector 29"
    assert result.pincode == "122001"
    assert result.source == "nominatim"
    assert result.attribution == "© OpenStreetMap contributors"
    assert result.confidence == 0.85


@pytest.mark.anyio
async def test_unresolved_coordinates_are_returned_without_inventing_address():
    handler = lambda request: httpx.Response(200, json={"error": "Unable to geocode"})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = NominatimLocationProvider(client=client, min_request_interval_seconds=0)
        result = await provider.resolve(0, 0)

    assert result.address is None
    assert result.city is None
    assert result.confidence == 0.0
    assert result.coordinates.latitude == 0


@pytest.mark.anyio
async def test_reuses_cached_lookup_for_same_rounded_coordinates():
    request_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal request_count
        request_count += 1
        return httpx.Response(200, json={"display_name": "Test City", "address": {"city": "Test City"}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = NominatimLocationProvider(client=client, min_request_interval_seconds=0)
        first = await provider.resolve(28.459501, 77.026601)
        second = await provider.resolve(28.459504, 77.026604)

    assert request_count == 1
    assert first.coordinates.latitude == 28.459501
    assert second.coordinates.latitude == 28.459504


@pytest.mark.anyio
async def test_provider_errors_are_reported_as_unavailable():
    handler = lambda request: httpx.Response(503, json={"error": "temporarily unavailable"})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = NominatimLocationProvider(client=client, min_request_interval_seconds=0)
        with pytest.raises(ProviderUnavailableError):
            await provider.resolve(28.4595, 77.0266)
