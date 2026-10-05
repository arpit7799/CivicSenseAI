# =============================================================================
# CivicSense AI — Mock Location Provider
# =============================================================================
# ⚠️  MOCK IMPLEMENTATION — NOT PRODUCTION CIVIC INTELLIGENCE
#
# This mock returns placeholder location data for development/testing.
# To be replaced by Arnav Yadav (Person 2) with real reverse geocoding.
#
# Owner of interface: Shared
# Owner of real implementation: Arnav Yadav (Person 2)
# =============================================================================

_MOCK_WARNING = "⚠️ THIS IS A MOCK IMPLEMENTATION — NOT PRODUCTION CIVIC INTELLIGENCE"

from app.core.interfaces import LocationProvider
from app.contracts.location import LocationResult, Coordinates
from app.core.logging import get_logger

logger = get_logger(__name__)


class MockLocationProvider(LocationProvider):
    """
    MOCK: Returns placeholder location data.

    Replace with Arnav's real LocationProvider implementation
    (reverse geocoding, geographic normalization, jurisdiction mapping).

    All outputs are clearly marked with source='mock'.
    """

    async def resolve(self, latitude: float, longitude: float) -> LocationResult:
        logger.info(f"[MOCK] Location resolution for ({latitude}, {longitude})")

        return LocationResult(
            address="Mock Address — Replace with real geocoding (Arnav)",
            city="Mock City",
            district="Mock District",
            state="Mock State",
            ward=None,
            zone=None,
            pincode="000000",
            coordinates=Coordinates(latitude=latitude, longitude=longitude),
            confidence=0.0,
            source="mock",
        )
