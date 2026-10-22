# =============================================================================
# CivicSense AI — Analyze Endpoint Tests
# =============================================================================

import pytest


@pytest.mark.anyio
async def test_analyze_returns_200_with_valid_request(client, valid_analysis_request):
    """Analyze endpoint should return 200 with a valid request."""
    response = await client.post("/api/v1/analyze", json=valid_analysis_request)
    assert response.status_code == 200


@pytest.mark.anyio
async def test_analyze_returns_200_with_minimal_request(client, minimal_analysis_request):
    """Analyze endpoint should accept a minimal request (no user_description)."""
    response = await client.post("/api/v1/analyze", json=minimal_analysis_request)
    assert response.status_code == 200


@pytest.mark.anyio
async def test_analyze_response_has_required_fields(client, valid_analysis_request):
    """Response should contain all required top-level fields."""
    response = await client.post("/api/v1/analyze", json=valid_analysis_request)
    data = response.json()

    assert "request_id" in data
    assert "status" in data
    assert data["status"] == "completed"
    assert "issue" in data
    assert "severity" in data
    assert "location" in data
    assert "authority" in data
    assert "complaint" in data
    assert "vision_details" in data
    assert "metadata" in data


@pytest.mark.anyio
async def test_analyze_issue_has_type_and_confidence(client, valid_analysis_request):
    """Issue field should have type and confidence."""
    response = await client.post("/api/v1/analyze", json=valid_analysis_request)
    issue = response.json()["issue"]

    assert "type" in issue
    assert "confidence" in issue
    assert isinstance(issue["confidence"], float)
    assert 0.0 <= issue["confidence"] <= 1.0


@pytest.mark.anyio
async def test_analyze_severity_has_level_and_score(client, valid_analysis_request):
    """Severity field should have level and score."""
    response = await client.post("/api/v1/analyze", json=valid_analysis_request)
    severity = response.json()["severity"]

    assert severity["level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert isinstance(severity["score"], float)
    assert 0.0 <= severity["score"] <= 1.0


@pytest.mark.anyio
async def test_analyze_complaint_has_subject_and_body(client, valid_analysis_request):
    """Complaint field should have subject and body."""
    response = await client.post("/api/v1/analyze", json=valid_analysis_request)
    complaint = response.json()["complaint"]

    assert "subject" in complaint
    assert "body" in complaint
    assert "priority" in complaint
    assert len(complaint["subject"]) > 0
    assert len(complaint["body"]) > 0


@pytest.mark.anyio
async def test_analyze_mock_source_fields(client, valid_analysis_request):
    """Provider outputs should have expected sources."""
    response = await client.post("/api/v1/analyze", json=valid_analysis_request)
    data = response.json()

    assert data["severity"]["source"] == "rules_engine_v1"
    assert data["location"]["source"] == "mock"
    assert data["authority"]["source"] == "mock"
    assert data["complaint"]["source"] == "mock"
    assert data["vision_details"]["source"] == "mock"

    # Metadata should report appropriately
    providers = data["metadata"]["providers"]
    for name, source in providers.items():
        if name == "vision":
            assert source == "mock"
        elif name == "severity":
            assert source == "rules_engine_v1"
        else:
            assert source == "mock", (
                f"Provider '{name}' should be 'mock', got '{source}'"
            )


@pytest.mark.anyio
async def test_analyze_rejects_missing_image_url(client):
    """Should reject request missing image_url."""
    response = await client.post("/api/v1/analyze", json={
        "latitude": 28.4595,
        "longitude": 77.0266,
    })
    assert response.status_code == 422


@pytest.mark.anyio
async def test_analyze_rejects_missing_latitude(client):
    """Should reject request missing latitude."""
    response = await client.post("/api/v1/analyze", json={
        "image_url": "https://example.com/test.jpg",
        "longitude": 77.0266,
    })
    assert response.status_code == 422


@pytest.mark.anyio
async def test_analyze_rejects_invalid_latitude(client):
    """Should reject latitude outside valid range."""
    response = await client.post("/api/v1/analyze", json={
        "image_url": "https://example.com/test.jpg",
        "latitude": 100.0,  # Invalid: must be -90 to 90
        "longitude": 77.0266,
    })
    assert response.status_code == 422


@pytest.mark.anyio
async def test_analyze_rejects_invalid_longitude(client):
    """Should reject longitude outside valid range."""
    response = await client.post("/api/v1/analyze", json={
        "image_url": "https://example.com/test.jpg",
        "latitude": 28.4595,
        "longitude": 200.0,  # Invalid: must be -180 to 180
    })
    assert response.status_code == 422


@pytest.mark.anyio
async def test_analyze_rejects_empty_image_url(client):
    """Should reject empty image_url string."""
    response = await client.post("/api/v1/analyze", json={
        "image_url": "",
        "latitude": 28.4595,
        "longitude": 77.0266,
    })
    assert response.status_code == 422
