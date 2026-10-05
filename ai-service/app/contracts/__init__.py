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
from app.contracts.location import Coordinates, LocationResult
from app.contracts.authority import AuthorityResult
from app.contracts.complaint import ComplaintPriority, ComplaintResult
from app.contracts.duplicate import DuplicateResult
from app.contracts.analytics import (
    HotspotCluster,
    HotspotResult,
    TrendDataPoint,
    TrendResult,
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
    # Authority
    "AuthorityResult",
    # Complaint
    "ComplaintPriority",
    "ComplaintResult",
    # Duplicate
    "DuplicateResult",
    # Analytics
    "HotspotCluster",
    "HotspotResult",
    "TrendDataPoint",
    "TrendResult",
    # Analysis
    "AnalysisRequest",
    "AnalysisResponse",
    "AnalysisMetadata",
    "IssueInfo",
]
