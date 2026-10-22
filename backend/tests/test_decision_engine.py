# =============================================================================
# CivicSense AI — Decision Engine Tests (Phase 5)
# =============================================================================

import asyncio
import pytest

from app.contracts.analysis import AnalysisRequest
from app.contracts.authority import AuthorityResult
from app.contracts.location import LocationResult, Coordinates
from app.contracts.vision import VisionResult, Detection, BoundingBox, ImageQuality
from app.contracts.severity import SeverityResult
from app.contracts.complaint import ComplaintResult
from app.contracts.duplicate import DuplicateResult
from app.core.interfaces import (
    VisionProvider,
    SeverityProvider,
    LocationProvider,
    AuthorityProvider,
    RAGProvider,
    ComplaintGenerator,
    DuplicateDetector,
)
from app.decision.engine import DecisionEngine


# -----------------------------------------------------------------------------
# Test Fixtures & Helpers
# -----------------------------------------------------------------------------

def make_test_vision_result(issue_class="pothole", confidence=0.95, status="valid_civic_issue") -> VisionResult:
    det = Detection(
        issue_class=issue_class,
        confidence=confidence,
        bounding_box=BoundingBox(x_min=10, y_min=10, x_max=100, y_max=100)
    )
    return VisionResult(
        detections=[det],
        primary_issue=det,
        secondary_issues=[],
        image_quality=ImageQuality(
            is_valid=True,
            resolution_adequate=True,
            blur_score=0.1,
            overall_quality_score=0.9,
            issues=[]
        ),
        classification_status=status,
        processing_time_ms=12.0,
        model_version="test-v1",
        source="test_vision",
    )


class AsyncDelayVision(VisionProvider):
    async def detect(self, image_path: str) -> VisionResult:
        return make_test_vision_result()


class AsyncDelaySeverity(SeverityProvider):
    async def assess(self, vision_result: VisionResult) -> SeverityResult:
        return SeverityResult(
            level="HIGH",
            score=0.75,
            factors=["base_issue_type:pothole"],
            confidence=0.95,
            source="test_severity",
        )


class DelayedLocation(LocationProvider):
    def __init__(self, delay_s: float = 0.05, should_fail: bool = False):
        self.delay_s = delay_s
        self.should_fail = should_fail
        self.called_at = 0.0

    async def resolve(self, latitude: float, longitude: float) -> LocationResult:
        self.called_at = asyncio.get_event_loop().time()
        await asyncio.sleep(self.delay_s)
        if self.should_fail:
            raise RuntimeError("Location resolution service offline")
        return LocationResult(
            address="123 Civic Way",
            city="Metropolis",
            district="Central",
            state="State",
            coordinates=Coordinates(latitude=latitude, longitude=longitude),
            confidence=0.9,
            source="test_location",
        )


class DelayedRAG(RAGProvider):
    def __init__(self, delay_s: float = 0.05, should_fail: bool = False):
        self.delay_s = delay_s
        self.should_fail = should_fail
        self.called_at = 0.0

    async def retrieve(self, query: str, context: dict | None = None) -> dict:
        self.called_at = asyncio.get_event_loop().time()
        await asyncio.sleep(self.delay_s)
        if self.should_fail:
            raise RuntimeError("Qdrant retrieval connection timed out")
        return {
            "documents": ["Doc 1: Road repair guidelines"],
            "scores": [0.85],
            "source": "test_rag",
        }


class DelayedDuplicate(DuplicateDetector):
    def __init__(self, delay_s: float = 0.05, should_fail: bool = False):
        self.delay_s = delay_s
        self.should_fail = should_fail
        self.called_at = 0.0

    async def check(
        self,
        issue_type: str,
        latitude: float,
        longitude: float,
        description: str | None = None,
        image_url: str | None = None,
    ) -> DuplicateResult:
        self.called_at = asyncio.get_event_loop().time()
        await asyncio.sleep(self.delay_s)
        if self.should_fail:
            raise RuntimeError("Duplicate detection database error")
        return DuplicateResult(
            is_potential_duplicate=False,
            similarity_score=0.0,
            match_factors=[],
            source="test_duplicate",
        )


class TrackingAuthority(AuthorityProvider):
    def __init__(self, should_fail: bool = False):
        self.called = False
        self.called_with_location = None
        self.called_at = 0.0
        self.should_fail = should_fail

    async def route(self, issue_type: str, location: LocationResult) -> AuthorityResult:
        self.called = True
        self.called_with_location = location
        self.called_at = asyncio.get_event_loop().time()
        if self.should_fail:
            raise RuntimeError("Authority routing database unreachable")
        return AuthorityResult(
            authority_name="Metropolis Public Works",
            department="Road Maintenance",
            jurisdiction=f"Metropolis - {location.city}",
            confidence=0.9,
            source="test_authority",
        )


class PassThroughComplaint(ComplaintGenerator):
    def __init__(self, should_fail: bool = False):
        self.last_context = None
        self.should_fail = should_fail

    async def generate(self, decision_context: dict) -> ComplaintResult:
        self.last_context = decision_context
        if self.should_fail:
            raise RuntimeError("Ollama LLM connection refused")
        return ComplaintResult(
            subject="Urgent Road Issue",
            body="Fix pothole immediately.",
            priority="HIGH",
            requested_action="Repair road surface",
            generated_at="2026-10-12T00:00:00Z",
            source="test_complaint",
        )


# -----------------------------------------------------------------------------
# Unit & Integration Tests
# -----------------------------------------------------------------------------

@pytest.mark.anyio
async def test_decision_engine_concurrent_execution():
    """Verify that location, RAG, and duplicate check run concurrently."""
    delay = 0.05
    loc = DelayedLocation(delay_s=delay)
    rag = DelayedRAG(delay_s=delay)
    dup = DelayedDuplicate(delay_s=delay)
    auth = TrackingAuthority()
    complaint = PassThroughComplaint()

    engine = DecisionEngine(
        vision=AsyncDelayVision(),
        severity=AsyncDelaySeverity(),
        location=loc,
        authority=auth,
        rag=rag,
        complaint=complaint,
        duplicate=dup,
    )

    req = AnalysisRequest(
        image_url="https://example.com/pothole.jpg",
        latitude=28.4595,
        longitude=77.0266,
        user_description="Big pothole",
    )

    t_start = asyncio.get_event_loop().time()
    response = await engine.analyze(req)
    t_end = asyncio.get_event_loop().time()

    total_time = t_end - t_start

    # Concurrency verification:
    # If sequential, loc + rag + dup would take at least 3 * delay = 0.15s.
    # Concurrent execution should complete close to 1 * delay.
    assert total_time < (delay * 2.5)
    # Timestamps should be very close to each other (launched concurrently)
    assert abs(loc.called_at - rag.called_at) < 0.02
    assert abs(rag.called_at - dup.called_at) < 0.02

    # Status should be completed when all succeed
    assert response.status == "completed"
    assert response.location is not None
    assert response.authority is not None
    assert response.metadata.providers["location"] == "test_location"
    assert response.metadata.providers["rag"] == "test_rag"
    assert response.metadata.providers["duplicate"] == "test_duplicate"
    assert response.metadata.providers["authority"] == "test_authority"


@pytest.mark.anyio
async def test_decision_engine_authority_depends_on_location():
    """Authority routing must execute strictly after location is resolved and receive location."""
    loc = DelayedLocation(delay_s=0.04)
    rag = DelayedRAG(delay_s=0.01)
    dup = DelayedDuplicate(delay_s=0.01)
    auth = TrackingAuthority()

    engine = DecisionEngine(
        vision=AsyncDelayVision(),
        severity=AsyncDelaySeverity(),
        location=loc,
        authority=auth,
        rag=rag,
        complaint=PassThroughComplaint(),
        duplicate=dup,
    )

    req = AnalysisRequest(
        image_url="https://example.com/pothole.jpg",
        latitude=28.4595,
        longitude=77.0266,
    )

    await engine.analyze(req)

    assert auth.called is True
    # Authority was called after location resolution completed
    assert auth.called_at >= (loc.called_at + 0.03)
    assert auth.called_with_location is not None
    assert auth.called_with_location.city == "Metropolis"


@pytest.mark.anyio
async def test_decision_engine_location_failure_skips_authority_honestly():
    """When location resolution fails, authority routing must be skipped honestly without fabricating results."""
    loc = DelayedLocation(should_fail=True)
    rag = DelayedRAG()
    dup = DelayedDuplicate()
    auth = TrackingAuthority()
    complaint = PassThroughComplaint()

    engine = DecisionEngine(
        vision=AsyncDelayVision(),
        severity=AsyncDelaySeverity(),
        location=loc,
        authority=auth,
        rag=rag,
        complaint=complaint,
        duplicate=dup,
    )

    req = AnalysisRequest(
        image_url="https://example.com/pothole.jpg",
        latitude=28.4595,
        longitude=77.0266,
    )

    response = await engine.analyze(req)

    # Status must reflect degradation
    assert response.status == "partial"
    # Location must NOT be fabricated
    assert response.location is None
    # Authority routing must NOT be run
    assert auth.called is False
    assert response.authority is None

    # Providers metadata records explicit honest states
    assert response.metadata.providers["location"] == "failed"
    assert response.metadata.providers["authority"] == "skipped_due_to_unresolved_location"
    # Independent providers succeeded and are preserved
    assert response.metadata.providers["rag"] == "test_rag"
    assert response.metadata.providers["duplicate"] == "test_duplicate"
    assert response.duplicate_check is not None
    assert response.severity is not None


@pytest.mark.anyio
async def test_decision_engine_rag_failure_degrades_gracefully():
    """When RAG fails, complaint is still assembled with other valid data and status is partial."""
    loc = DelayedLocation()
    rag = DelayedRAG(should_fail=True)
    dup = DelayedDuplicate()
    auth = TrackingAuthority()
    complaint = PassThroughComplaint()

    engine = DecisionEngine(
        vision=AsyncDelayVision(),
        severity=AsyncDelaySeverity(),
        location=loc,
        authority=auth,
        rag=rag,
        complaint=complaint,
        duplicate=dup,
    )

    req = AnalysisRequest(
        image_url="https://example.com/pothole.jpg",
        latitude=28.4595,
        longitude=77.0266,
    )

    response = await engine.analyze(req)

    assert response.status == "partial"
    assert response.metadata.providers["rag"] == "failed"
    # Location and authority are preserved
    assert response.location is not None
    assert response.authority is not None
    assert response.metadata.providers["location"] == "test_location"
    assert response.metadata.providers["authority"] == "test_authority"
    # Complaint generator received empty docs rather than failing
    assert complaint.last_context["rag_documents"] == []


@pytest.mark.anyio
async def test_decision_engine_short_circuit_preservation():
    """Short-circuit behavior on non-civic issue must remain intact."""
    class NonCivicVision(VisionProvider):
        async def detect(self, image_path: str) -> VisionResult:
            return make_test_vision_result(issue_class="cat", status="no_civic_issue_detected")

    loc = DelayedLocation()
    engine = DecisionEngine(
        vision=NonCivicVision(),
        severity=AsyncDelaySeverity(),
        location=loc,
        authority=TrackingAuthority(),
        rag=DelayedRAG(),
        complaint=PassThroughComplaint(),
        duplicate=DelayedDuplicate(),
    )

    req = AnalysisRequest(
        image_url="https://example.com/cat.jpg",
        latitude=28.4595,
        longitude=77.0266,
    )

    response = await engine.analyze(req)
    assert response.status == "rejected_no_civic_issue"
    assert response.location is None
    assert response.authority is None
    assert response.severity is None
    assert loc.called_at == 0.0
