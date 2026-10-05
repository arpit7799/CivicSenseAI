# =============================================================================
# CivicSense AI — Mock Vision Detector
# =============================================================================
# ⚠️  MOCK IMPLEMENTATION — NOT PRODUCTION CIVIC INTELLIGENCE
#
# This mock returns placeholder detection results for development/testing.
# Will be replaced with real YOLO-based detection in Phase 2.
#
# Owner: Arpit (Person 1)
# =============================================================================

_MOCK_WARNING = "⚠️ THIS IS A MOCK IMPLEMENTATION — NOT PRODUCTION CIVIC INTELLIGENCE"

from app.core.interfaces import VisionProvider
from app.contracts.vision import (
    VisionResult,
    Detection,
    BoundingBox,
    ImageQuality,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class MockVisionDetector(VisionProvider):
    """
    MOCK: Returns placeholder vision detection results.

    Replace with real YOLO-based CivicIssueDetector in Phase 2.
    All outputs are clearly marked with source='mock'.
    """

    async def detect(self, image_path: str) -> VisionResult:
        logger.info(f"[MOCK] Vision detection on: {image_path}")

        mock_detection = Detection(
            issue_class="pothole",
            confidence=0.92,
            bounding_box=BoundingBox(
                x_min=120.0, y_min=200.0, x_max=380.0, y_max=420.0
            ),
        )

        mock_secondary = Detection(
            issue_class="road_damage",
            confidence=0.67,
            bounding_box=BoundingBox(
                x_min=50.0, y_min=150.0, x_max=500.0, y_max=480.0
            ),
        )

        return VisionResult(
            detections=[mock_detection, mock_secondary],
            primary_issue=mock_detection,
            secondary_issues=[mock_secondary],
            image_quality=ImageQuality(
                is_valid=True,
                resolution_adequate=True,
                blur_score=0.15,
                overall_quality_score=0.85,
                issues=[],
            ),
            processing_time_ms=45.0,
            model_version="mock-v0",
            source="mock",
        )
