# =============================================================================
# CivicSense AI — Severity Contracts
# =============================================================================
# Pydantic schemas for severity assessment results.
# Owner: Arpit (Person 1)
# =============================================================================

from typing import Literal

from pydantic import BaseModel, Field


# Allowed severity levels per the responsibility document
SeverityLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class SeverityResult(BaseModel):
    """Severity assessment result for a detected civic issue."""

    level: SeverityLevel = Field(..., description="Severity level classification")
    score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Numeric severity score 0.0 (negligible) to 1.0 (critical)",
    )
    factors: list[str] = Field(
        default_factory=list,
        description="Contributing factors, e.g. ['large_damage_area', 'roadway_obstruction']",
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confidence in the severity assessment",
    )
    source: str = Field(
        default="mock",
        description="Result source: 'mock' | 'severity_model_v1' | etc.",
    )
