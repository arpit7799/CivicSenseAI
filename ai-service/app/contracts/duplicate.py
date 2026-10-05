# =============================================================================
# CivicSense AI — Duplicate Detection Contracts
# =============================================================================
# Pydantic schemas for duplicate complaint detection results.
# Owner: Arnav Yadav (Person 2)
# Interface defined by Arpit for cross-team integration.
# =============================================================================

from pydantic import BaseModel, Field


class DuplicateResult(BaseModel):
    """
    Duplicate complaint detection result.

    Implementation owner: Arnav (Person 2).
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
