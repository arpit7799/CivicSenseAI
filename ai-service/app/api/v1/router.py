# =============================================================================
# CivicSense AI — API v1 Router
# =============================================================================

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    analyze,
    location,
    authority,
    duplicate,
    analytics,
    complaint_index,
)

router = APIRouter()

router.include_router(health.router, tags=["Health"])
router.include_router(analyze.router, tags=["Analysis"])
router.include_router(location.router, tags=["Location Intelligence"])
router.include_router(authority.router, tags=["Authority Routing"])
router.include_router(duplicate.router, tags=["Duplicate Detection"])
router.include_router(analytics.router, tags=["Civic Analytics"])
router.include_router(complaint_index.router)
