# =============================================================================
# CivicSense AI — Analytics Contracts (Hotspots & Trends)
# =============================================================================
# Pydantic schemas for civic hotspot detection and trend analysis.
# Owner: Arnav Yadav (Person 2)
# Interface defined by Arpit for cross-team integration.
# =============================================================================

from pydantic import BaseModel, Field

from app.contracts.location import Coordinates


class HotspotQueryRequest(BaseModel):
    """Request payload for civic hotspot clustering."""

    latitude: float = Field(..., ge=-90.0, le=90.0, description="Center latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Center longitude")
    radius_km: float = Field(default=5.0, gt=0.0, le=100.0, description="Search radius in kilometers")
    issue_type: str | None = Field(default=None, description="Optional issue type filter")


class HotspotCluster(BaseModel):
    """A single geographic hotspot cluster."""

    cluster_id: str = Field(..., description="Unique cluster identifier")
    center: Coordinates = Field(..., description="Cluster centroid coordinates")
    radius_meters: float = Field(..., ge=0.0, description="Approximate cluster radius")
    complaint_count: int = Field(..., ge=0, description="Number of complaints in cluster")
    dominant_issue_type: str = Field(..., description="Most common issue type in cluster")
    severity_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Count per severity level, e.g. {'HIGH': 5, 'MEDIUM': 3}",
    )


class HotspotResult(BaseModel):
    """Civic hotspot detection result."""

    clusters: list[HotspotCluster] = Field(
        default_factory=list, description="Detected hotspot clusters"
    )
    total_complaints_analyzed: int = Field(
        ..., ge=0, description="Total complaints in the analysis window"
    )
    analysis_region: str = Field(..., description="Geographic region analyzed")
    source: str = Field(
        default="mock",
        description="Result source: 'mock' | 'dbscan_v1' | etc.",
    )


class TrendQueryRequest(BaseModel):
    """Request payload for civic trend analysis."""

    issue_type: str = Field(..., min_length=1, description="Civic issue category to analyze")
    region: str = Field(..., min_length=1, description="Geographic region name")
    time_window_days: int = Field(default=30, ge=1, le=365, description="Time window in days")


class TrendDataPoint(BaseModel):
    """A single data point in a civic trend."""

    period: str = Field(..., description="Time period label, e.g. '2024-W03' or '2024-01-15'")
    count: int = Field(..., ge=0, description="Complaint count for this period")
    dominant_severity: str | None = Field(default=None, description="Most common severity, if reports exist")


class TrendResult(BaseModel):
    """Civic trend analysis result."""

    issue_type: str = Field(..., description="Issue type analyzed")
    trend_direction: str = Field(
        ..., description="Trend direction: 'increasing' | 'decreasing' | 'stable' | 'recurring'"
    )
    data_points: list[TrendDataPoint] = Field(
        default_factory=list, description="Time-series data points"
    )
    time_window_days: int = Field(..., ge=1, description="Analysis time window in days")
    region: str = Field(..., description="Geographic region analyzed")
    source: str = Field(
        default="mock",
        description="Result source: 'mock' | 'trend_engine_v1' | etc.",
    )
