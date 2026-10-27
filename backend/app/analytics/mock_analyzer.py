# =============================================================================
# CivicSense AI — Mock Analytics Analyzer (Hotspots & Trends)
# =============================================================================
# Offline / development analytics provider for hotspots and trends.
# Provides baseline spatial clustering and temporal data points for testing.
# =============================================================================

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
    Lightweight fallback/offline hotspot analyzer.
    Returns baseline zero-cluster spatial analysis for decoupled testing.
    Outputs source='mock'.
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
            clusters=[],  # Baseline returns empty clusters
            total_complaints_analyzed=0,
            analysis_region=f"Civic region around ({latitude:.4f}, {longitude:.4f})",
            source="mock",
        )


class MockTrendAnalyzer(TrendAnalyzer):
    """
    Lightweight fallback/offline trend analyzer.
    Returns baseline stable temporal trend analysis for decoupled testing.
    Outputs source='mock'.
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
