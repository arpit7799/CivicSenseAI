# =============================================================================
# CivicSense AI — Mock Analytics Analyzer (Hotspots & Trends)
# =============================================================================
# ⚠️  MOCK IMPLEMENTATION — NOT PRODUCTION CIVIC INTELLIGENCE
#
# This mock returns placeholder hotspot and trend results.
# To be replaced by Arnav Yadav (Person 2) with real spatial clustering
# (DBSCAN) and time-series trend analysis.
#
# Owner of interface: Shared
# Owner of real implementation: Arnav Yadav (Person 2)
# =============================================================================

_MOCK_WARNING = "⚠️ THIS IS A MOCK IMPLEMENTATION — NOT PRODUCTION CIVIC INTELLIGENCE"

from app.core.interfaces import HotspotAnalyzer, TrendAnalyzer
from app.contracts.analytics import (
    HotspotResult,
    TrendResult,
    TrendDataPoint,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class MockHotspotAnalyzer(HotspotAnalyzer):
    """
    MOCK: Returns placeholder hotspot detection results.

    Replace with Arnav's real HotspotAnalyzer implementation
    (DBSCAN spatial clustering, complaint density analysis).

    All outputs are clearly marked with source='mock'.
    """

    async def analyze(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        issue_type: str | None = None,
    ) -> HotspotResult:
        logger.info(
            f"[MOCK] Hotspot analysis at ({latitude}, {longitude}), "
            f"radius={radius_km}km"
        )

        return HotspotResult(
            clusters=[],  # Mock returns no clusters
            total_complaints_analyzed=0,
            analysis_region=f"Mock region around ({latitude}, {longitude})",
            source="mock",
        )


class MockTrendAnalyzer(TrendAnalyzer):
    """
    MOCK: Returns placeholder trend analysis results.

    Replace with Arnav's real TrendAnalyzer implementation
    (time-series analysis, recurring issue detection).

    All outputs are clearly marked with source='mock'.
    """

    async def analyze(
        self,
        issue_type: str,
        region: str,
        time_window_days: int = 30,
    ) -> TrendResult:
        logger.info(
            f"[MOCK] Trend analysis for '{issue_type}' in '{region}', "
            f"window={time_window_days}d"
        )

        return TrendResult(
            issue_type=issue_type,
            trend_direction="stable",
            data_points=[],  # Mock returns no data points
            time_window_days=time_window_days,
            region=region,
            source="mock",
        )
