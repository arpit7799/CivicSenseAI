# =============================================================================
# CivicSense AI — API Dependencies
# =============================================================================
# FastAPI dependency injection for providers and the decision engine.
#
# In Phase 1, all providers are mocks. As real implementations are built,
# the provider instantiation here is the ONLY place that changes —
# the endpoints and decision engine remain untouched.
# =============================================================================

from functools import lru_cache

from app.decision.engine import DecisionEngine

# Person 1 providers (Arpit — replaced in Phases 2–7)
from app.vision.detector import YOLODetector
from app.severity.engine import SeverityEngine
from app.rag.mock_retriever import MockRAGRetriever
from app.llm.mock_generator import MockComplaintGenerator

# Person 2 mocks (Arnav — replaced when Arnav delivers)
from app.location.mock_provider import MockLocationProvider
from app.authority.mock_provider import MockAuthorityProvider
from app.duplicate.mock_detector import MockDuplicateDetector


@lru_cache()
def get_decision_engine() -> DecisionEngine:
    """
    Build and cache the DecisionEngine with all providers.

    This is the single wiring point for dependency injection.
    To swap a mock for a real implementation:
    1. Import the real provider class
    2. Replace the Mock* instantiation below
    3. No other file needs to change

    Example (Phase 2):
        from app.vision.detector import YOLODetector
        vision = YOLODetector(model_path=settings.yolo_model_path)
    """
    # Person 1 providers (mocks for now except vision)
    vision = YOLODetector()
    severity = SeverityEngine()
    rag = MockRAGRetriever()
    complaint = MockComplaintGenerator()

    # Person 2 providers (mocks until Arnav delivers)
    location = MockLocationProvider()
    authority = MockAuthorityProvider()
    duplicate = MockDuplicateDetector()

    return DecisionEngine(
        vision=vision,
        severity=severity,
        location=location,
        authority=authority,
        rag=rag,
        complaint=complaint,
        duplicate=duplicate,
    )
