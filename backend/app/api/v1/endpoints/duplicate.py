# =============================================================================
# CivicSense AI — Duplicate Complaint Detection Endpoints
# =============================================================================
# Endpoint for checking potential duplicate complaints.
# =============================================================================

from fastapi import APIRouter, Depends

from app.contracts.duplicate import DuplicateCheckRequest, DuplicateResult
from app.core.interfaces import DuplicateDetector
from app.api.deps import get_duplicate_detector

router = APIRouter(prefix="/duplicate", tags=["Duplicate Detection"])


@router.post("/check", response_model=DuplicateResult)
async def check_duplicate(
    request: DuplicateCheckRequest,
    detector: DuplicateDetector = Depends(get_duplicate_detector),
) -> DuplicateResult:
    """
    Check if a civic complaint is a potential duplicate based on GPS proximity,
    issue category, description, and image similarity.
    """
    return await detector.check(
        issue_type=request.issue_type,
        latitude=request.latitude,
        longitude=request.longitude,
        description=request.description,
        image_url=request.image_url,
    )
