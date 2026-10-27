# =============================================================================
# CivicSense AI — Mock Location Provider
# =============================================================================
# Lightweight offline location provider for development and testing.
# Returns structured geographic context matching municipal schemas.
# =============================================================================

from app.core.interfaces import LocationProvider
from app.contracts.location import LocationResult, Coordinates
from app.core.logging import get_logger

logger = get_logger(__name__)


class MockLocationProvider(LocationProvider):
    """
    Lightweight fallback/offline location provider.
    Resolves GPS coordinates into structured municipal geographic context.
    Outputs source='mock'.
    """

    async def resolve(self, latitude: float, longitude: float) -> LocationResult:
        logger.info(f"[MOCK] Location resolution for ({latitude}, {longitude})")

        # Provide realistic Gurugram municipal context for testing
        is_ncr = 28.0 <= latitude <= 29.0 and 76.5 <= longitude <= 77.8
        address = (
            "Sector 34, Arterial Road, Gurugram, Haryana"
            if is_ncr
            else f"Municipal Ward Road, Vicinity ({latitude:.4f}, {longitude:.4f})"
        )

        return LocationResult(
            address=address,
            city="Gurugram",
            district="Gurugram",
            state="Haryana",
            ward="Ward 34",
            zone="Zone 3",
            pincode="122001",
            coordinates=Coordinates(latitude=latitude, longitude=longitude),
            confidence=0.85,
            source="mock",
        )

