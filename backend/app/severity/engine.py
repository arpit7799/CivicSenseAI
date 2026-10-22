# =============================================================================
# CivicSense AI — Real Severity Engine
# =============================================================================
# Calculates civic severity based on rules and heuristics.
# Owner: Arpit (Person 1)
# =============================================================================

from app.core.interfaces import SeverityProvider
from app.contracts.vision import VisionResult
from app.contracts.severity import SeverityResult
from app.core.logging import get_logger
from app.severity.rules import BASE_SCORES, SECONDARY_MODIFIERS, get_severity_level

logger = get_logger(__name__)


class SeverityEngine(SeverityProvider):
    """
    Real severity assessment engine.
    Calculates score based on issue class, secondary compounding issues,
    and bounding box area heuristics.
    """

    async def assess(self, vision_result: VisionResult) -> SeverityResult:
        logger.info("Starting rule-based severity assessment")
        
        primary = vision_result.primary_issue
        if not primary:
            # Should not happen because DecisionEngine short-circuits, but just in case
            return SeverityResult(
                level="LOW",
                score=0.0,
                factors=["no_primary_issue"],
                confidence=1.0,
                source="rules_engine_v1"
            )

        # 1. Base Score
        base_score = BASE_SCORES.get(primary.issue_class, 0.30)
        final_score = base_score
        factors = [f"base_issue_type:{primary.issue_class}"]
        
        # 2. Secondary Issue Modifiers
        for sec in vision_result.secondary_issues:
            modifier = SECONDARY_MODIFIERS.get(sec.issue_class, 0.05)
            if modifier > 0:
                final_score += modifier
                factors.append(f"compounding_issue:{sec.issue_class}")

        # 3. Bounding Box Area Heuristic
        # Area relative to image size is not a direct danger measure, but a heuristic.
        # We assume coordinates are normalized (0 to 1) or we just use width*height if absolute.
        # Wait, our bounding box coordinates are currently absolute (e.g., from Ultralytics on raw image).
        # We don't easily have the full image dimensions here in the VisionResult contract without adding it.
        # Let's approximate based on a common max dimension, or simply scale the raw area as a small nudge.
        # Actually, Ultralytics returns raw coordinates. Without the image dimensions, we can't do exact relative area.
        # Let's just use the absolute area with a very small heuristic multiplier (e.g. area > 10000 pixels adds +0.05).
        # A better approach: bbox width * height
        bbox = primary.bounding_box
        area = (bbox.x_max - bbox.x_min) * (bbox.y_max - bbox.y_min)
        
        # Just a heuristic nudge
        if area > 50000:
            final_score += 0.10
            factors.append("heuristic_large_apparent_size")
        elif area > 10000:
            final_score += 0.05
            factors.append("heuristic_medium_apparent_size")

        # Clamp between 0.0 and 1.0
        final_score = max(0.0, min(1.0, final_score))
        
        level = get_severity_level(final_score)
        
        # Engine confidence is tied to the YOLO confidence of the primary issue
        engine_confidence = primary.confidence
        
        return SeverityResult(
            level=level,
            score=round(final_score, 2),
            factors=factors,
            confidence=round(engine_confidence, 2),
            source="rules_engine_v1",
        )
