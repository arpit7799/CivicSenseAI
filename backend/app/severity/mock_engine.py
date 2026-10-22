# =============================================================================
# CivicSense AI — Mock Severity Engine
# =============================================================================
# ⚠️  MOCK IMPLEMENTATION — NOT PRODUCTION CIVIC INTELLIGENCE
#
# This mock returns placeholder severity results for development/testing.
# Will be replaced with real severity assessment in Phase 4.
#
# Owner: Arpit (Person 1)
# =============================================================================

_MOCK_WARNING = "⚠️ THIS IS A MOCK IMPLEMENTATION — NOT PRODUCTION CIVIC INTELLIGENCE"

from app.core.interfaces import SeverityProvider
from app.contracts.vision import VisionResult
from app.contracts.severity import SeverityResult
from app.core.logging import get_logger

logger = get_logger(__name__)


class MockSeverityEngine(SeverityProvider):
    """
    MOCK: Returns placeholder severity assessment results.

    Replace with real SeverityEngine in Phase 4.
    All outputs are clearly marked with source='mock'.
    """

    async def assess(self, vision_result: VisionResult) -> SeverityResult:
        logger.info("[MOCK] Severity assessment")

        # Simple mock logic: higher confidence detection → higher severity
        primary = vision_result.primary_issue
        if primary and primary.confidence > 0.9:
            level = "HIGH"
            score = 0.86
            factors = ["large_damage_area", "roadway_obstruction"]
        elif primary and primary.confidence > 0.7:
            level = "MEDIUM"
            score = 0.55
            factors = ["visible_damage"]
        else:
            level = "LOW"
            score = 0.25
            factors = ["minor_damage"]

        return SeverityResult(
            level=level,
            score=score,
            factors=factors,
            confidence=0.80,
            source="mock",
        )
