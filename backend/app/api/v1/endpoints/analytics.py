# =============================================================================
# CivicSense AI — Civic Analytics Endpoints (Hotspots & Trends)
# =============================================================================
# Endpoints for spatial hotspot clustering and time-series trend analysis.
# =============================================================================

from fastapi import APIRouter, Depends, Query

from app.contracts.analytics import (
    HotspotQueryRequest,
    HotspotResult,
    TrendQueryRequest,
    TrendResult,
)
from app.contracts.news import CivicNewsResponse
from app.core.interfaces import HotspotAnalyzer, TrendAnalyzer
from app.api.deps import get_hotspot_analyzer, get_trend_analyzer
from app.news.service import CivicNewsService, get_civic_news_service

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


@router.get("/civic-news", response_model=CivicNewsResponse)
async def get_civic_news(
    city: str = Query(default="Gurugram", description="Target municipality or region"),
    category: str = Query(
        default="all",
        pattern="^(all|roads|sanitation|environment|municipal)$",
        description="Filter domain: all, roads, sanitation, environment, municipal",
    ),
    limit: int = Query(default=6, ge=1, le=20, description="Max articles to retrieve"),
    news_service: CivicNewsService = Depends(get_civic_news_service),
) -> CivicNewsResponse:
    """
    Fetch tuned, real-time civic, municipal, and infrastructure news for the citizen dashboard.
    """
    return await news_service.get_civic_news(city=city, category=category, page_size=limit)

