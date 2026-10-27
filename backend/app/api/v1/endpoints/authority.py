# =============================================================================
# CivicSense AI — Authority Routing Endpoints
# =============================================================================
# Endpoint for routing civic issues to the responsible public authority.
# =============================================================================

from fastapi import APIRouter, Depends

from app.contracts.authority import AuthorityRouteRequest, AuthorityResult
from app.core.interfaces import AuthorityProvider
from app.api.deps import get_authority_provider

router = APIRouter(prefix="/authority", tags=["Authority Routing"])


@router.post("/route", response_model=AuthorityResult)
async def route_authority(
    request: AuthorityRouteRequest,
    provider: AuthorityProvider = Depends(get_authority_provider),
) -> AuthorityResult:
    """
    Route a civic issue and location to the responsible municipal authority and department.
    """
    return await provider.route(
        issue_type=request.issue_type,
        location=request.location,
    )
