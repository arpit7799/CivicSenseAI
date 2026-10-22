# =============================================================================
# CivicSense AI — Civic Analytics Endpoints Tests (Phase 8)
# =============================================================================

import pytest
from app.main import app
from app.api.deps import get_hotspot_analyzer, get_trend_analyzer
from app.core.interfaces import HotspotAnalyzer, TrendAnalyzer
from app.contracts.analytics import (
    HotspotResult,
    HotspotCluster,
    TrendResult,
    TrendDataPoint,
)
from app.contracts.location import Coordinates


# -----------------------------------------------------------------------------
# Hotspots Tests
# -----------------------------------------------------------------------------

@pytest.mark.anyio
async def test_hotspots_returns_200(client):
    payload = {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "radius_km": 5.0,
        "issue_type": "pothole",
    }
    response = await client.post("/api/v1/analytics/hotspots", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "clusters" in data
    assert "total_complaints_analyzed" in data
    assert "analysis_region" in data
    assert data["source"] == "mock"


@pytest.mark.anyio
async def test_hotspots_rejects_invalid_radius(client):
    # Radius must be > 0.0
    payload = {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "radius_km": 0.0,
    }
    response = await client.post("/api/v1/analytics/hotspots", json=payload)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_hotspots_supports_di_override(client):
    class CustomHotspotAnalyzer(HotspotAnalyzer):
        async def analyze(
            self,
            latitude: float,
            longitude: float,
            radius_km: float = 5.0,
            issue_type: str | None = None,
        ) -> HotspotResult:
            return HotspotResult(
                clusters=[
                    HotspotCluster(
                        cluster_id="CLUSTER-001",
                        center=Coordinates(latitude=latitude, longitude=longitude),
                        radius_meters=350.0,
                        complaint_count=12,
                        dominant_issue_type=issue_type or "pothole",
                        severity_distribution={"HIGH": 8, "CRITICAL": 4},
                    )
                ],
                total_complaints_analyzed=12,
                analysis_region="Test Sector 14",
                source="test_dbscan_clustering",
            )

    app.dependency_overrides[get_hotspot_analyzer] = lambda: CustomHotspotAnalyzer()
    try:
        payload = {"latitude": 28.6139, "longitude": 77.2090, "radius_km": 2.5}
        response = await client.post("/api/v1/analytics/hotspots", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["clusters"]) == 1
        assert data["clusters"][0]["cluster_id"] == "CLUSTER-001"
        assert data["source"] == "test_dbscan_clustering"
    finally:
        app.dependency_overrides.pop(get_hotspot_analyzer, None)


# -----------------------------------------------------------------------------
# Trends Tests
# -----------------------------------------------------------------------------

@pytest.mark.anyio
async def test_trends_returns_200(client):
    payload = {
        "issue_type": "water_logging",
        "region": "South Delhi",
        "time_window_days": 30,
    }
    response = await client.post("/api/v1/analytics/trends", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["issue_type"] == "water_logging"
    assert data["trend_direction"] in ("increasing", "decreasing", "stable", "recurring")
    assert "data_points" in data
    assert data["source"] == "mock"


@pytest.mark.anyio
async def test_trends_rejects_empty_region(client):
    payload = {
        "issue_type": "water_logging",
        "region": "",  # Invalid: min_length=1
        "time_window_days": 30,
    }
    response = await client.post("/api/v1/analytics/trends", json=payload)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_trends_supports_di_override(client):
    class CustomTrendAnalyzer(TrendAnalyzer):
        async def analyze(
            self,
            issue_type: str,
            region: str,
            time_window_days: int = 30,
        ) -> TrendResult:
            return TrendResult(
                issue_type=issue_type,
                trend_direction="increasing",
                data_points=[
                    TrendDataPoint(period="Week 1", count=4, dominant_severity="MEDIUM"),
                    TrendDataPoint(period="Week 2", count=11, dominant_severity="HIGH"),
                ],
                time_window_days=time_window_days,
                region=region,
                source="test_trend_analytics",
            )

    app.dependency_overrides[get_trend_analyzer] = lambda: CustomTrendAnalyzer()
    try:
        payload = {
            "issue_type": "garbage_dump",
            "region": "Central Ward",
            "time_window_days": 14,
        }
        response = await client.post("/api/v1/analytics/trends", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["trend_direction"] == "increasing"
        assert len(data["data_points"]) == 2
        assert data["source"] == "test_trend_analytics"
    finally:
        app.dependency_overrides.pop(get_trend_analyzer, None)
