# =============================================================================
# CivicSense AI — Analyze Endpoint
# =============================================================================
# POST /api/v1/analyze
#
# This is the core AI analysis endpoint as defined in the responsibility
# document §8. It accepts an image URL + GPS coordinates and returns
# a structured analysis result.
# =============================================================================

from fastapi import APIRouter, Depends

from app.contracts.analysis import AnalysisRequest, AnalysisResponse
from app.api.deps import get_decision_engine
from app.decision.engine import DecisionEngine
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/analyze",
    summary="Analyze Civic Issue",
    description=(
        "Analyze a civic issue from a photograph and GPS location. "
        "Returns structured detection, severity, location, authority, "
        "and generated complaint information."
    ),
    response_model=AnalysisResponse,
)
async def analyze_civic_issue(
    request: AnalysisRequest,
    engine: DecisionEngine = Depends(get_decision_engine),
) -> AnalysisResponse:
    """
    Run the full AI analysis pipeline on a civic issue.

    In Phase 1, all providers are mocks. Real implementations
    will be wired in during subsequent phases.
    """
    logger.info(
        f"Analyze request received — image_url={request.image_url}, "
        f"coords=({request.latitude}, {request.longitude})"
    )

    result = await engine.analyze(request)

    return result
