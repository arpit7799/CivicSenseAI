# =============================================================================
# CivicSense AI — Provider Interfaces (Abstract Base Classes)
# =============================================================================
# These interfaces define the contract between the core AI decision engine
# and the individual intelligence modules.
#
# ARCHITECTURE RULE:
# - The decision engine depends on these interfaces, NEVER on concrete
#   implementations.
# - Person 1 (Arpit) implements: VisionProvider, SeverityProvider,
#   RAGProvider, ComplaintGenerator
# - Person 2 (Arnav) implements: LocationProvider, AuthorityProvider,
#   DuplicateDetector, HotspotAnalyzer, TrendAnalyzer
# - During development, mock implementations are used for any provider
#   not yet implemented.
# =============================================================================

from abc import ABC, abstractmethod

from app.contracts.vision import VisionResult
from app.contracts.severity import SeverityResult
from app.contracts.location import LocationResult
from app.contracts.authority import AuthorityResult
from app.contracts.complaint import ComplaintResult
from app.contracts.duplicate import DuplicateResult
from app.contracts.analytics import HotspotResult, TrendResult


# =============================================================================
# Person 1 (Arpit) Interfaces
# =============================================================================

class VisionProvider(ABC):
    """
    Interface for computer vision / civic issue detection.

    Owner: Arpit (Person 1)
    Consumes: image file path or URL
    Produces: VisionResult with detections, quality, and confidence
    """

    @abstractmethod
    async def detect(self, image_path: str) -> VisionResult:
        """Run vision detection pipeline on an image."""
        ...


class SeverityProvider(ABC):
    """
    Interface for severity assessment.

    Owner: Arpit (Person 1)
    Consumes: VisionResult
    Produces: SeverityResult with level, score, and factors
    """

    @abstractmethod
    async def assess(self, vision_result: VisionResult) -> SeverityResult:
        """Assess severity based on vision detection results."""
        ...


class RAGProvider(ABC):
    """
    Interface for RAG (Retrieval-Augmented Generation) context retrieval.

    Owner: Arpit (Person 1)
    Consumes: query string + context metadata
    Produces: RAGResult with retrieved documents and context
    """

    @abstractmethod
    async def retrieve(self, query: str, context: dict | None = None) -> dict:
        """
        Retrieve relevant civic knowledge for the given query.

        Returns a dict with at minimum:
        - 'documents': list of retrieved text chunks
        - 'scores': list of relevance scores
        - 'source': 'mock' | 'qdrant' | etc.
        """
        ...


class ComplaintGenerator(ABC):
    """
    Interface for AI complaint generation.

    Owner: Arpit (Person 1)
    Consumes: structured decision context (vision + severity + location +
              authority + RAG context)
    Produces: ComplaintResult with subject, body, and priority
    """

    @abstractmethod
    async def generate(self, decision_context: dict) -> ComplaintResult:
        """Generate a structured complaint from the decision context."""
        ...


# =============================================================================
# Person 2 (Arnav) Interfaces
# =============================================================================

class LocationProvider(ABC):
    """
    Interface for location intelligence / reverse geocoding.

    Owner: Arnav Yadav (Person 2)
    Consumes: GPS coordinates (latitude, longitude)
    Produces: LocationResult with address, city, district, state, etc.
    """

    @abstractmethod
    async def resolve(self, latitude: float, longitude: float) -> LocationResult:
        """Resolve GPS coordinates into structured location information."""
        ...


class AuthorityProvider(ABC):
    """
    Interface for civic authority routing.

    Owner: Arnav Yadav (Person 2)
    Consumes: issue type + LocationResult
    Produces: AuthorityResult with authority, department, and contact info

    CRITICAL: Authority contact data MUST come from verified datasets.
    The LLM must NOT be the source of truth for official contacts.
    """

    @abstractmethod
    async def route(
        self, issue_type: str, location: LocationResult
    ) -> AuthorityResult:
        """Route a civic issue to the responsible authority."""
        ...


class DuplicateDetector(ABC):
    """
    Interface for duplicate complaint detection.

    Owner: Arnav Yadav (Person 2)
    Consumes: complaint data (location, issue type, description, image)
    Produces: DuplicateResult with similarity score and match factors
    """

    @abstractmethod
    async def check(
        self,
        issue_type: str,
        latitude: float,
        longitude: float,
        description: str | None = None,
        image_url: str | None = None,
    ) -> DuplicateResult:
        """Check for potential duplicate complaints."""
        ...


class HotspotAnalyzer(ABC):
    """
    Interface for civic hotspot detection.

    Owner: Arnav Yadav (Person 2)
    Consumes: geographic region + optional filters
    Produces: HotspotResult with spatial clusters
    """

    @abstractmethod
    async def analyze(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        issue_type: str | None = None,
    ) -> HotspotResult:
        """Analyze a geographic region for complaint hotspots."""
        ...


class TrendAnalyzer(ABC):
    """
    Interface for civic trend analysis.

    Owner: Arnav Yadav (Person 2)
    Consumes: issue type + region + time window
    Produces: TrendResult with trend direction and time-series data
    """

    @abstractmethod
    async def analyze(
        self,
        issue_type: str,
        region: str,
        time_window_days: int = 30,
    ) -> TrendResult:
        """Analyze civic complaint trends for a given issue and region."""
        ...
