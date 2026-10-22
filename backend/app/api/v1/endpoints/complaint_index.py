"""Internal, authenticated sync endpoint for the complaint read model."""

import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.deps import get_complaint_repository
from app.config import get_settings
from app.contracts.civic_record import (
    ComplaintIndexUpsertRequest,
    ComplaintIndexUpsertResponse,
)
from app.core.complaint_repository import ComplaintRepository


router = APIRouter(prefix="/complaint-index", tags=["Complaint Index"])


@router.post("/upsert", response_model=ComplaintIndexUpsertResponse)
async def upsert_complaint_index(
    request: ComplaintIndexUpsertRequest,
    authorization: str | None = Header(default=None),
    repository: ComplaintRepository = Depends(get_complaint_repository),
) -> ComplaintIndexUpsertResponse:
    settings = get_settings()
    expected_key = settings.complaint_index_api_key
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Complaint index sync is disabled until COMPLAINT_INDEX_API_KEY is configured",
        )
    scheme, _, supplied_key = (authorization or "").partition(" ")
    if scheme.casefold() != "bearer" or not hmac.compare_digest(supplied_key, expected_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid service credential")

    count = await repository.upsert_observations(request.records)
    return ComplaintIndexUpsertResponse(upserted=count)
