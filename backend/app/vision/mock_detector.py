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

import os
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
    Lightweight fallback/offline vision detection provider.
    Outputs source='mock'.
    """

    async def detect(self, image_path: str) -> VisionResult:
        logger.info(f"[MOCK] Vision detection on: {image_path}")

        # If it is a real uploaded image (base64 or local file), try real fine-tuned YOLO model:
        if (image_path.startswith("data:image") or (os.path.exists(image_path) and not image_path.startswith("http"))):
            try:
                from app.vision.detector import YOLODetector
                real_detector = YOLODetector()
                real_result = await real_detector.detect(image_path)
                if real_result.primary_issue is not None or real_result.classification_status == "no_civic_issue_detected":
                    return real_result
            except Exception as e:
                logger.warning(f"[MOCK] Real YOLO attempt in mock provider: {e}")

        path_lower = image_path.lower()
        if any(w in path_lower for w in ("garbage", "dump", "trash", "litter", "waste")):
            primary_class = "garbage_dump"
            sec_class = "littering_garbage_on_public_places"
        elif any(w in path_lower for w in ("tree", "branch", "leaf", "fallen")):
            primary_class = "fallen_tree"
            sec_class = "fallen_trees"
        elif any(w in path_lower for w in ("light", "pole", "wire", "electric", "cable")):
            primary_class = "broken_streetlight"
            sec_class = "damaged_electric_wires_and_poles"
        elif any(w in path_lower for w in ("sign", "board")):
            primary_class = "broken_road_sign"
            sec_class = "broken_road_sign_issues"
        else:
            primary_class = "pothole"
            sec_class = "road_damage"

        mock_detection = Detection(
            issue_class=primary_class,
            confidence=0.92,
            bounding_box=BoundingBox(
                x_min=120.0, y_min=200.0, x_max=380.0, y_max=420.0
            ),
        )

        mock_secondary = Detection(
            issue_class=sec_class,
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
