# =============================================================================
# CivicSense AI — Location Intelligence Endpoints
# =============================================================================
# Endpoint for GPS reverse geocoding and geographic normalization.
# =============================================================================

from fastapi import APIRouter, Depends

from app.contracts.location import LocationResolveRequest, LocationResult
from app.core.interfaces import LocationProvider
from app.api.deps import get_location_provider

router = APIRouter(prefix="/location", tags=["Location Intelligence"])


@router.post("/resolve", response_model=LocationResult)
async def resolve_location(
    request: LocationResolveRequest,
    provider: LocationProvider = Depends(get_location_provider),
) -> LocationResult:
    """
    Resolve GPS coordinates into a structured geographic address hierarchy.
    """
    return await provider.resolve(
        latitude=request.latitude,
        longitude=request.longitude,
    )
