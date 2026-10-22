import json

import pytest

from app.authority.dataset_provider import VerifiedDatasetAuthorityProvider
from app.contracts.location import Coordinates, LocationResult


def location(city=None, state=None):
    return LocationResult(
        city=city,
        state=state,
        coordinates=Coordinates(latitude=28.4595, longitude=77.0266),
        confidence=0.8,
        source="test",
    )


@pytest.mark.anyio
async def test_routes_gurugram_issue_to_sourced_general_municipal_channel():
    provider = VerifiedDatasetAuthorityProvider()
    result = await provider.route("POTHOLE", location("Gurugram", "Haryana"))

    assert result.authority_name == "Municipal Corporation of Gurugram"
    assert result.department is None
    assert result.contact_phone == "18001801817"
    assert result.source == "verified_dataset"
    assert result.source_reference == "https://www.mcg.gov.in/"
    assert result.verified_at == "2026-10-22"
    assert result.confidence == 0.65


@pytest.mark.anyio
async def test_routes_gurgaon_alias_case_insensitively():
    provider = VerifiedDatasetAuthorityProvider()
    result = await provider.route("garbage_dump", location("Gurgaon", "HARYANA"))
    assert result.authority_name == "Municipal Corporation of Gurugram"


@pytest.mark.anyio
async def test_does_not_route_outside_verified_jurisdiction():
    provider = VerifiedDatasetAuthorityProvider()
    result = await provider.route("pothole", location("Delhi", "Delhi"))

    assert result.authority_name is None
    assert result.contact_phone is None
    assert result.source == "no_match"
    assert result.confidence == 0.0


@pytest.mark.anyio
async def test_does_not_route_unsupported_issue_type():
    provider = VerifiedDatasetAuthorityProvider()
    result = await provider.route("illegal_dumping", location("Gurugram", "Haryana"))
    assert result.authority_name is None


def test_rejects_malformed_authority_dataset(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"records": [{"authority_name": "No provenance"}]}))
    with pytest.raises(ValueError, match="Invalid authority dataset"):
        VerifiedDatasetAuthorityProvider(path)
