# =============================================================================
# CivicSense AI — Civic Analytics Endpoints (Hotspots & Trends)
# =============================================================================
# Endpoints for spatial hotspot clustering and time-series trend analysis.
# =============================================================================

from fastapi import APIRouter, Depends

from app.contracts.analytics import (
    HotspotQueryRequest,
    HotspotResult,
    TrendQueryRequest,
    TrendResult,
)
from app.core.interfaces import HotspotAnalyzer, TrendAnalyzer
from app.api.deps import get_hotspot_analyzer, get_trend_analyzer

router = APIRouter(prefix="/analytics", tags=["Civic Analytics"])


@router.post("/hotspots", response_model=HotspotResult)
async def analyze_hotspots(
    request: HotspotQueryRequest,
    analyzer: HotspotAnalyzer = Depends(get_hotspot_analyzer),
) -> HotspotResult:
    """
    Detect geographic complaint clusters (hotspots) using spatial density analysis.
    """
    return await analyzer.analyze(
        latitude=request.latitude,
        longitude=request.longitude,
        radius_km=request.radius_km,
        issue_type=request.issue_type,
    )


@router.post("/trends", response_model=TrendResult)
async def analyze_trends(
    request: TrendQueryRequest,
    analyzer: TrendAnalyzer = Depends(get_trend_analyzer),
) -> TrendResult:
    """
    Analyze civic complaint patterns and time-series trends for a specific issue and region.
    """
    return await analyzer.analyze(
        issue_type=request.issue_type,
        region=request.region,
        time_window_days=request.time_window_days,
    )
