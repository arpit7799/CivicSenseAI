# =============================================================================
# CivicSense AI — Health Endpoint
# =============================================================================

from fastapi import APIRouter

from app.config import get_settings
from app.api.deps import (
    get_location_provider,
    get_authority_provider,
    get_duplicate_detector,
    get_hotspot_analyzer,
    get_trend_analyzer,
)

router = APIRouter()


def _provider_status(provider: object) -> str:
    """Report mock providers honestly while allowing later implementations."""
    return "mock" if type(provider).__name__.startswith("Mock") else "configured"


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
    Reports whether each provider is a mock or a configured implementation.
    """
    settings = get_settings()
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
        "providers": {
            "vision": "mock" if settings.provider_mode == "mock" else "configured",
            "severity": "mock" if settings.provider_mode == "mock" else "configured",
            "location": _provider_status(get_location_provider()),
            "authority": _provider_status(get_authority_provider()),
            "rag": "mock" if settings.provider_mode == "mock" else "configured",
            "complaint_generator": "mock" if settings.provider_mode == "mock" else "configured",
            "duplicate_detector": _provider_status(get_duplicate_detector()),
            "hotspot_analyzer": _provider_status(get_hotspot_analyzer()),
            "trend_analyzer": _provider_status(get_trend_analyzer()),
        },
    }
