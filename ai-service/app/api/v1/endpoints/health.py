# =============================================================================
# CivicSense AI — Health Endpoint
# =============================================================================

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()


@router.get(
    "/health",
    summary="Health Check",
    description="Returns the health status of the AI service and its loaded providers.",
    response_model=dict,
)
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns service status, version, and which providers are currently loaded.
    In Phase 1, all providers are mocks.
    """
    settings = get_settings()

    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
        "providers": {
            "vision": "mock",
            "severity": "mock",
            "location": "mock",
            "authority": "mock",
            "rag": "mock",
            "complaint_generator": "mock",
            "duplicate_detector": "mock",
            "hotspot_analyzer": "mock",
            "trend_analyzer": "mock",
        },
    }
