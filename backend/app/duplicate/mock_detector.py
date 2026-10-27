# =============================================================================
# CivicSense AI — Mock Duplicate Detector
# =============================================================================
# Offline / development duplicate detector.
# Provides baseline duplicate evaluation for testing and decoupled environments.
# =============================================================================

from app.core.interfaces import DuplicateDetector
from app.contracts.duplicate import DuplicateResult
from app.core.logging import get_logger

logger = get_logger(__name__)


class MockDuplicateDetector(DuplicateDetector):
    """
    Lightweight fallback/offline duplicate detector.
    Returns baseline zero-match duplicate evaluation.
    Outputs source='mock'.
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
