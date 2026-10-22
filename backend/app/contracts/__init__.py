# =============================================================================
# CivicSense AI — Contracts Package
# =============================================================================
# All Pydantic schemas (API contracts) are exported from here.
# =============================================================================

from app.contracts.vision import (
    BoundingBox,
    Detection,
    ImageQuality,
    VisionResult,
)
from app.contracts.severity import SeverityLevel, SeverityResult
from app.contracts.location import Coordinates, LocationResult, LocationResolveRequest
from app.contracts.authority import AuthorityResult, AuthorityRouteRequest
from app.contracts.complaint import ComplaintPriority, ComplaintResult
from app.contracts.duplicate import DuplicateResult, DuplicateCheckRequest
from app.contracts.analytics import (
    HotspotCluster,
    HotspotResult,
    HotspotQueryRequest,
    TrendDataPoint,
    TrendResult,
    TrendQueryRequest,
)
from app.contracts.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisMetadata,
    IssueInfo,
)

__all__ = [
    # Vision
    "BoundingBox",
    "Detection",
    "ImageQuality",
    "VisionResult",
    # Severity
    "SeverityLevel",
    "SeverityResult",
    # Location
    "Coordinates",
    "LocationResult",
    "LocationResolveRequest",
    # Authority
    "AuthorityResult",
    "AuthorityRouteRequest",
    # Complaint
    "ComplaintPriority",
    "ComplaintResult",
    # Duplicate
    "DuplicateResult",
    "DuplicateCheckRequest",
    # Analytics
    "HotspotCluster",
    "HotspotResult",
    "HotspotQueryRequest",
    "TrendDataPoint",
    "TrendResult",
    "TrendQueryRequest",
    # Analysis
    "AnalysisRequest",
    "AnalysisResponse",
    "AnalysisMetadata",
    "IssueInfo",
]
