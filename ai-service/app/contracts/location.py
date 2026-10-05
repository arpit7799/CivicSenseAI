# =============================================================================
# CivicSense AI — Location Contracts
# =============================================================================
# Pydantic schemas for location intelligence results.
# Owner: Arnav Yadav (Person 2)
# Interface defined by Arpit for cross-team integration.
# =============================================================================

from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    """Geographic coordinates."""

    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude")


class LocationResult(BaseModel):
    """
    Location intelligence result — resolves GPS coordinates into
    structured geographic context.

    Implementation owner: Arnav (Person 2).
    Arpit's code consumes this via the LocationProvider interface.
    """

    address: str = Field(..., description="Resolved street address")
    city: str = Field(..., description="City name")
    district: str = Field(..., description="District name")
    state: str = Field(..., description="State name")
    ward: str | None = Field(default=None, description="Ward/zone if available")
    zone: str | None = Field(default=None, description="Administrative zone if available")
    pincode: str | None = Field(default=None, description="Postal code if available")
    coordinates: Coordinates = Field(..., description="Original GPS coordinates")
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confidence in the resolved location",
    )
    source: str = Field(
        default="mock",
        description="Result source: 'mock' | 'geocoding_api' | 'nominatim' | etc.",
    )
