from datetime import datetime, timezone

import pytest

from app.api.deps import get_complaint_repository, get_duplicate_detector
from app.config import get_settings
from app.core.memory_complaint_repository import InMemoryComplaintRepository
from app.duplicate.engine import CivicDuplicateDetector
from app.main import app


def report(identifier="C-1"):
    return {
        "complaint_id": identifier,
        "issue_type": "pothole",
        "reported_at": datetime.now(timezone.utc).isoformat(),
        "latitude": 28.4595,
        "longitude": 77.0266,
        "severity": "HIGH",
        "description": "Large pothole near the market",
        "city": "Gurugram",
    }


@pytest.mark.anyio
async def test_complaint_index_requires_authentication(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "complaint_index_api_key", "a-long-enough-test-key")
    response = await client.post(
        "/api/v1/complaint-index/upsert",
        json={"records": [report()]},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_complaint_index_disabled_without_key(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "complaint_index_api_key", None)
    response = await client.post(
        "/api/v1/complaint-index/upsert",
        headers={"Authorization": "Bearer any-key"},
        json={"records": [report()]},
    )
    assert response.status_code == 503


@pytest.mark.anyio
async def test_index_sync_feeds_duplicate_detection(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "complaint_index_api_key", "a-long-enough-test-key")
    repository = InMemoryComplaintRepository()
    detector = CivicDuplicateDetector(repository)
    app.dependency_overrides[get_complaint_repository] = lambda: repository
    app.dependency_overrides[get_duplicate_detector] = lambda: detector
    try:
        upsert = await client.post(
            "/api/v1/complaint-index/upsert",
            headers={"Authorization": "Bearer a-long-enough-test-key"},
            json={"records": [report("C-1")]},
        )
        assert upsert.status_code == 200, upsert.text
        assert upsert.json() == {"upserted": 1}

        duplicate = await client.post(
            "/api/v1/duplicate/check",
            json={
                "issue_type": "pothole",
                "latitude": 28.4595,
                "longitude": 77.0266,
                "description": "Large pothole near the market",
            },
        )
        assert duplicate.status_code == 200, duplicate.text
        assert duplicate.json()["is_potential_duplicate"] is True
        assert duplicate.json()["existing_complaint_id"] == "C-1"
    finally:
        app.dependency_overrides.pop(get_complaint_repository, None)
        app.dependency_overrides.pop(get_duplicate_detector, None)
