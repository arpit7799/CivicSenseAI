# =============================================================================
# CivicSense AI — Main Analysis Contracts
# =============================================================================
# Pydantic schemas for the primary AI analysis request and response.
# This is the core API contract (POST /ai/analyze) as defined in the
# responsibility document §8.
#
# Shared: Both Person 1 and Person 2 consume/produce parts of this contract.
# =============================================================================

from pydantic import BaseModel, Field

from app.contracts.vision import VisionResult
from app.contracts.severity import SeverityResult
from app.contracts.location import LocationResult
from app.contracts.authority import AuthorityResult
from app.contracts.complaint import ComplaintResult
from app.contracts.duplicate import DuplicateResult


class AnalysisRequest(BaseModel):
    """
    Request payload for civic issue analysis.

    POST /api/v1/analyze
    """

    image_url: str = Field(
        ..., min_length=1,
        description="URL of the civic issue image",
    )
    latitude: float = Field(
        ..., ge=-90.0, le=90.0,
        description="GPS latitude of the issue location",
    )
    longitude: float = Field(
        ..., ge=-180.0, le=180.0,
        description="GPS longitude of the issue location",
    )
    user_description: str | None = Field(
        default=None,
        description="Optional user-provided description of the issue",
    )


class IssueInfo(BaseModel):
    """Summarized issue information for the top-level response."""

    type: str = Field(..., description="Primary issue type detected")
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confidence in the primary issue detection",
    )


class AnalysisMetadata(BaseModel):
    """Metadata about the analysis run."""

    request_id: str = Field(..., description="Unique request identifier")
    processing_time_ms: float = Field(
        ..., ge=0.0, description="Total processing time in milliseconds"
    )
    api_version: str = Field(default="v1", description="API version used")
    providers: dict[str, str] = Field(
        default_factory=dict,
        description="Provider sources used, e.g. {'vision': 'mock', 'location': 'mock'}",
    )


class AnalysisResponse(BaseModel):
    """
    Complete AI analysis response.

    Contains results from all AI pipeline stages:
    - Vision detection (Arpit)
    - Severity assessment (Arpit)
    - Location intelligence (Arnav)
    - Authority routing (Arnav)
    - Complaint generation (Arpit)
    - Duplicate check (Arnav)
    """

    request_id: str = Field(..., description="Unique request identifier")
    status: str = Field(
        default="completed",
        description="Analysis status: 'completed' | 'partial' | 'failed'",
    )
    issue: IssueInfo = Field(..., description="Primary issue summary")
    severity: SeverityResult | None = Field(default=None, description="Severity assessment")
    location: LocationResult | None = Field(default=None, description="Resolved location information")
    authority: AuthorityResult | None = Field(default=None, description="Responsible authority routing")
    complaint: ComplaintResult | None = Field(default=None, description="Generated complaint")
    duplicate_check: DuplicateResult | None = Field(
        default=None, description="Duplicate detection result (may be null)"
    )
    vision_details: VisionResult = Field(
        ..., description="Detailed vision pipeline output"
    )
    metadata: AnalysisMetadata = Field(..., description="Analysis run metadata")
