# =============================================================================
# CivicSense AI — Test Configuration
# =============================================================================

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.deps import get_decision_engine


@pytest.fixture
def anyio_backend():
    return "asyncio"


from app.api.deps import get_decision_engine
from app.vision.mock_detector import MockVisionDetector
from app.severity.mock_engine import MockSeverityEngine
from app.rag.mock_retriever import MockRAGRetriever
from app.llm.mock_generator import MockComplaintGenerator
from app.location.mock_provider import MockLocationProvider
from app.authority.mock_provider import MockAuthorityProvider
from app.duplicate.mock_detector import MockDuplicateDetector
from app.decision.engine import DecisionEngine

def mock_get_decision_engine():
    return DecisionEngine(
        vision=MockVisionDetector(),
        severity=MockSeverityEngine(),
        location=MockLocationProvider(),
        authority=MockAuthorityProvider(),
        rag=MockRAGRetriever(),
        complaint=MockComplaintGenerator(),
        duplicate=MockDuplicateDetector(),
    )

@pytest.fixture
async def client():
    """Async test client for the FastAPI application."""
    app.dependency_overrides[get_decision_engine] = mock_get_decision_engine
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def valid_analysis_request() -> dict:
    """Valid analysis request payload for testing."""
    return {
        "image_url": "https://example.com/pothole.jpg",
        "latitude": 28.4595,
        "longitude": 77.0266,
        "user_description": "Large pothole on main road near market",
    }


@pytest.fixture
def minimal_analysis_request() -> dict:
    """Minimal valid analysis request (no optional fields)."""
    return {
        "image_url": "https://example.com/issue.jpg",
        "latitude": 28.4595,
        "longitude": 77.0266,
    }
