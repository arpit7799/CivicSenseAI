# =============================================================================
# CivicSense AI — API Dependencies
# =============================================================================
# FastAPI dependency injection for providers and the decision engine.
#
# Providers are selected from configuration here so local mock mode stays
# lightweight and production adapters can be enabled independently.
# =============================================================================

from functools import lru_cache

from app.config import get_settings
from app.decision.engine import DecisionEngine

# Person 2 provider interfaces
from app.core.interfaces import (
    LocationProvider,
    AuthorityProvider,
    DuplicateDetector,
    HotspotAnalyzer,
    TrendAnalyzer,
)
from app.core.complaint_repository import ComplaintRepository


@lru_cache()
def get_location_provider() -> LocationProvider:
    """Return configured LocationProvider (Arnav)."""
    if get_settings().location_provider == "nominatim":
        from app.location.nominatim_provider import NominatimLocationProvider

        return NominatimLocationProvider()

    from app.location.mock_provider import MockLocationProvider

    return MockLocationProvider()


@lru_cache()
def get_authority_provider() -> AuthorityProvider:
    """Return configured AuthorityProvider (Arnav)."""
    if get_settings().authority_provider == "verified_dataset":
        from app.authority.dataset_provider import VerifiedDatasetAuthorityProvider

        return VerifiedDatasetAuthorityProvider()

    from app.authority.mock_provider import MockAuthorityProvider

    return MockAuthorityProvider()


@lru_cache()
def get_duplicate_detector() -> DuplicateDetector:
    """Return configured DuplicateDetector (Arnav)."""
    if get_settings().duplicate_provider == "engine":
        from app.duplicate.engine import CivicDuplicateDetector

        return CivicDuplicateDetector(get_complaint_repository())

    from app.duplicate.mock_detector import MockDuplicateDetector

    return MockDuplicateDetector()


@lru_cache()
def get_hotspot_analyzer() -> HotspotAnalyzer:
    """Return configured HotspotAnalyzer (Arnav)."""
    if get_settings().analytics_provider == "engine":
        from app.analytics.engine import CivicHotspotAnalyzer

        return CivicHotspotAnalyzer(get_complaint_repository())

    from app.analytics.mock_analyzer import MockHotspotAnalyzer

    return MockHotspotAnalyzer()


@lru_cache()
def get_trend_analyzer() -> TrendAnalyzer:
    """Return configured TrendAnalyzer (Arnav)."""
    if get_settings().analytics_provider == "engine":
        from app.analytics.engine import CivicTrendAnalyzer

        return CivicTrendAnalyzer(get_complaint_repository())

    from app.analytics.mock_analyzer import MockTrendAnalyzer

    return MockTrendAnalyzer()


@lru_cache()
def get_complaint_repository() -> ComplaintRepository:
    """Return the configured complaint read-model adapter."""
    if get_settings().complaint_repository == "postgres":
        from app.core.postgres_complaint_repository import PostgresComplaintRepository

        return PostgresComplaintRepository()

    from app.core.memory_complaint_repository import InMemoryComplaintRepository

    return InMemoryComplaintRepository()


@lru_cache()
def get_decision_engine() -> DecisionEngine:
    """
    Build and cache the DecisionEngine with all providers.

    This is the single wiring point for dependency injection.
    To swap a mock for a real implementation:
    1. Import the real provider class
    2. Replace the Mock* instantiation in the respective getter above
    3. No other file needs to change
    """
    settings = get_settings()

    if settings.provider_mode == "production":
        # Keep optional model dependencies out of API startup and mock-mode installs.
        from app.vision.detector import YOLODetector
        from app.severity.engine import SeverityEngine
        from app.rag.retriever import QdrantRAGRetriever
        from app.llm.generator import OllamaComplaintGenerator

        vision = YOLODetector()
        severity = SeverityEngine()
        rag = QdrantRAGRetriever()
        complaint = OllamaComplaintGenerator()
    else:
        from app.vision.mock_detector import MockVisionDetector
        from app.severity.mock_engine import MockSeverityEngine
        from app.rag.mock_retriever import MockRAGRetriever
        from app.llm.mock_generator import MockComplaintGenerator

        vision = MockVisionDetector()
        severity = MockSeverityEngine()
        rag = MockRAGRetriever()
        complaint = MockComplaintGenerator()

    # Person 2 providers (Arnav)
    location = get_location_provider()
    authority = get_authority_provider()
    duplicate = get_duplicate_detector()

    return DecisionEngine(
        vision=vision,
        severity=severity,
        location=location,
        authority=authority,
        rag=rag,
        complaint=complaint,
        duplicate=duplicate,
    )
