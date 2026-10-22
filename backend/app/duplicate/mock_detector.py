# =============================================================================
# CivicSense AI — Mock Duplicate Detector
# =============================================================================
# ⚠️  MOCK IMPLEMENTATION — NOT PRODUCTION CIVIC INTELLIGENCE
#
# This mock returns placeholder duplicate detection results.
# To be replaced by Arnav Yadav (Person 2) with real duplicate detection
# using GPS proximity, issue similarity, image similarity, etc.
#
# Owner of interface: Shared
# Owner of real implementation: Arnav Yadav (Person 2)
# =============================================================================

_MOCK_WARNING = "⚠️ THIS IS A MOCK IMPLEMENTATION — NOT PRODUCTION CIVIC INTELLIGENCE"

from app.core.interfaces import DuplicateDetector
from app.contracts.duplicate import DuplicateResult
from app.core.logging import get_logger

logger = get_logger(__name__)


class MockDuplicateDetector(DuplicateDetector):
    """
    MOCK: Returns placeholder duplicate detection results.

    Replace with Arnav's real DuplicateDetector implementation
    (GPS proximity, issue category, image similarity, text similarity, time).

    All outputs are clearly marked with source='mock'.
    Default: no duplicate found.
    """

    async def check(
        self,
        issue_type: str,
        latitude: float,
        longitude: float,
        description: str | None = None,
        image_url: str | None = None,
    ) -> DuplicateResult:
        logger.info(f"[MOCK] Duplicate check for '{issue_type}' at ({latitude}, {longitude})")

        return DuplicateResult(
            is_potential_duplicate=False,
            existing_complaint_id=None,
            similarity_score=0.0,
            match_factors=[],
            source="mock",
        )
