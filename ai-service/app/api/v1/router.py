# =============================================================================
# CivicSense AI — API v1 Router
# =============================================================================

from fastapi import APIRouter

from app.api.v1.endpoints import health, analyze

router = APIRouter()

router.include_router(health.router, tags=["Health"])
router.include_router(analyze.router, tags=["Analysis"])
