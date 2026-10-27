# =============================================================================
# CivicSense AI — Duplicate Detection Contracts
# =============================================================================
# Pydantic schemas for duplicate complaint detection results.
# =============================================================================

from pydantic import BaseModel, Field


class DuplicateCheckRequest(BaseModel):
    """Request payload for duplicate complaint checking."""

    issue_type: str = Field(..., min_length=1, description="Civic issue category")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="GPS latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="GPS longitude")
    description: str | None = Field(default=None, description="Optional complaint text description")
    image_url: str | None = Field(default=None, description="Optional image URL")


class DuplicateResult(BaseModel):
    """
    Duplicate complaint detection result.

    Signals include GPS proximity, issue category match, image similarity,
    text similarity, and time difference.
    """

    is_potential_duplicate: bool = Field(
        ..., description="Whether a potential duplicate was found"
    )
    existing_complaint_id: str | None = Field(
        default=None, description="ID of the matching existing complaint, if any"
    )
    similarity_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Overall similarity score 0.0 (no match) to 1.0 (exact match)",
    )
    match_factors: list[str] = Field(
        default_factory=list,
        description="Factors contributing to the match, e.g. ['gps_proximity', 'same_issue_type']",
    )
    source: str = Field(
        default="mock",
        description="Result source: 'mock' | 'duplicate_engine_v1' | etc.",
    )
