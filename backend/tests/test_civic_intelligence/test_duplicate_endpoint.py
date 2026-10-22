# =============================================================================
# CivicSense AI — Duplicate Endpoint Tests (Phase 8)
# =============================================================================

import pytest
from app.main import app
from app.api.deps import get_duplicate_detector
from app.core.interfaces import DuplicateDetector
from app.contracts.duplicate import DuplicateResult


@pytest.mark.anyio
async def test_check_duplicate_returns_200(client):
    payload = {
        "issue_type": "pothole",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "description": "Deep hole on central avenue",
    }
    response = await client.post("/api/v1/duplicate/check", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "is_potential_duplicate" in data
    assert "similarity_score" in data
    assert "match_factors" in data
    assert data["source"] == "mock"


@pytest.mark.anyio
async def test_check_duplicate_rejects_invalid_latitude(client):
    payload = {
        "issue_type": "pothole",
        "latitude": 99.0,  # Invalid: > 90
        "longitude": 77.2090,
    }
    response = await client.post("/api/v1/duplicate/check", json=payload)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_check_duplicate_supports_di_override(client):
    class CustomDuplicateDetector(DuplicateDetector):
        async def check(
            self,
            issue_type: str,
            latitude: float,
            longitude: float,
            description: str | None = None,
            image_url: str | None = None,
        ) -> DuplicateResult:
            return DuplicateResult(
                is_potential_duplicate=True,
                existing_complaint_id="COMPLAINT-2026-9999",
                similarity_score=0.92,
                match_factors=["gps_proximity", "same_issue_type", "image_similarity"],
                source="test_duplicate_engine",
            )

    app.dependency_overrides[get_duplicate_detector] = lambda: CustomDuplicateDetector()
    try:
        payload = {
            "issue_type": "pothole",
            "latitude": 28.6139,
            "longitude": 77.2090,
        }
        response = await client.post("/api/v1/duplicate/check", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["is_potential_duplicate"] is True
        assert data["existing_complaint_id"] == "COMPLAINT-2026-9999"
        assert data["similarity_score"] == 0.92
        assert data["source"] == "test_duplicate_engine"
    finally:
        app.dependency_overrides.pop(get_duplicate_detector, None)
